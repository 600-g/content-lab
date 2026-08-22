"""채팅 도구 화이트리스트 + 디스패치.

- 모든 도구는 명시적으로 등록. Anthropic tool_use schema 로 변환해서 모델에 전달.
- mutating 도구는 safety 게이트 (PIN 세션 토큰) 통과 후에만 dispatch 가능.
- 도구 내부는 작은 함수 단위. 새 도구 추가는 register_tool() 한 줄.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from scripts import config_store
from scripts.chat import safety

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GLOBAL_SKILLS_DIR = Path(
    os.path.expanduser(os.getenv("SKILL_INSTALL_DIR", "~/.claude/skills"))
)
MIRROR_SKILLS_DIR = PROJECT_ROOT / "skills"


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict
    handler: Callable[..., Any]
    mutating: bool = False


REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    REGISTRY[spec.name] = spec


def anthropic_tools() -> list[dict]:
    """Anthropic Messages API 의 tools 배열 형식으로 변환."""
    return [
        {
            "name": s.name,
            "description": s.description,
            "input_schema": s.input_schema,
        }
        for s in REGISTRY.values()
    ]


def dispatch(name: str, args: dict, *, session_token: str | None) -> dict:
    """도구 실행. mutating 이면 세션 검증. 결과는 항상 dict (직렬화 가능)."""
    spec = REGISTRY.get(name)
    if not spec:
        return {"ok": False, "error": f"알 수 없는 도구: {name}"}
    if spec.mutating and not safety.check_session(session_token):
        return {"ok": False, "error": "세션 만료/미인증 — PIN 다시 입력해주세요", "need_pin": True}
    try:
        result = spec.handler(**args)
        if not isinstance(result, dict):
            result = {"ok": True, "result": result}
        result.setdefault("ok", True)
        return result
    except TypeError as e:
        return {"ok": False, "error": f"인자 오류: {e}"}
    except Exception as e:  # noqa: BLE001
        logger.exception("tool %s 실패", name)
        return {"ok": False, "error": str(e)}


# ── 안전 (조회) 도구 ────────────────────────────────────────────

def _t_read_config() -> dict:
    return {"ok": True, "config": config_store.all_config()}


def _t_recent_jobs(limit: int = 10) -> dict:
    jobs_file = PROJECT_ROOT / "logs" / "jobs.json"
    if not jobs_file.exists():
        return {"ok": True, "jobs": []}
    try:
        data = json.loads(jobs_file.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"jobs.json 읽기 실패: {e}"}
    items = list(data.values()) if isinstance(data, dict) else list(data)
    items.sort(key=lambda x: x.get("started_at", 0), reverse=True)
    out = []
    for j in items[:max(1, int(limit))]:
        out.append({
            "id": j.get("id"),
            "url": j.get("url"),
            "status": j.get("status"),
            "stage": j.get("stage"),
            "elapsed": (j.get("result") or {}).get("elapsed"),
            "message_ko": (j.get("result") or {}).get("message_ko"),
            "error_ko": (j.get("result") or {}).get("error_ko"),
        })
    return {"ok": True, "jobs": out}


_SECRET_RE = None


def _redact_secrets(text: str) -> str:
    """로그 속 API 키/토큰 마스킹 — 공개 채팅으로 로그가 노출되는 경로 방어."""
    global _SECRET_RE  # noqa: PLW0603
    import re
    if _SECRET_RE is None:
        _SECRET_RE = re.compile(
            r"(AIza[0-9A-Za-z_\-]{20,}|sk-[A-Za-z0-9_\-]{16,}|key=[0-9A-Za-z_\-]{16,}"
            r"|secret_[0-9A-Za-z]{16,}|ntn_[0-9A-Za-z]{16,})"
        )
    return _SECRET_RE.sub("[REDACTED]", text)


def _t_tail_log(lines: int = 50) -> dict:
    log_file = PROJECT_ROOT / "logs" / "launchd_stderr.log"
    if not log_file.exists():
        return {"ok": True, "lines": []}
    try:
        n = max(1, min(int(lines), 500))
        # 큰 파일도 안전하게 끝부분만.
        result = subprocess.run(
            ["tail", "-n", str(n), str(log_file)],
            capture_output=True, text=True, timeout=5,
        )
        out_lines = [_redact_secrets(ln) for ln in result.stdout.splitlines()]
        return {"ok": True, "lines": out_lines}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def _t_read_skill_md(slug: str) -> dict:
    target = GLOBAL_SKILLS_DIR / slug / "SKILL.md"
    if not target.exists():
        return {"ok": False, "error": f"스킬 없음: {slug}"}
    return {"ok": True, "slug": slug, "path": str(target), "content": target.read_text(encoding="utf-8")}


def _t_dedup_report() -> dict:
    report = PROJECT_ROOT / "inbox" / "dedup_candidates.md"
    if not report.exists():
        return {
            "ok": True,
            "exists": False,
            "hint": "리포트가 없습니다. scan_existing_dedup 도구로 먼저 생성하세요.",
        }
    return {
        "ok": True,
        "exists": True,
        "path": str(report),
        "content": report.read_text(encoding="utf-8"),
    }


def _t_list_skills(limit: int = 200) -> dict:
    if not GLOBAL_SKILLS_DIR.exists():
        return {"ok": True, "skills": []}
    slugs = sorted([p.name for p in GLOBAL_SKILLS_DIR.glob("*/SKILL.md")])
    return {"ok": True, "total": len(slugs), "slugs": slugs[:max(1, int(limit))]}


def _t_search_library(query: str, k: int = 5, category: str = "") -> dict:
    """스킬 라이브러리 하이브리드 검색 (키워드 + 의미). 결과는 메타 + 스니펫만 — 본문은 read_skill_md."""
    from scripts.library.search import search as _lib_search
    res = _lib_search(str(query), k=k, category=category or None)
    if not res.get("ok"):
        return res
    slim = [
        {
            "slug": r["slug"], "title": r["title"], "description": r["description"][:200],
            "category": r["category"], "grade": r["grade"], "snippet": r["snippet"],
            "page_url": r["page_url"],       # 사람에게 안내할 게시글 링크
            "detail_url": r["detail_url"],   # 본문 전문 (read_skill_md 로도 가능)
        }
        for r in res["results"]
    ]
    return {
        "ok": True, "query": res["query"], "semantic_used": res["semantic_used"],
        "total_indexed": res["total_indexed"], "results": slim,
    }


# ── mutating (적용) 도구 ──────────────────────────────────────────

OP_COMMANDS = {
    "restart_aiskillbox": [
        "launchctl", "kickstart", "-k",
        f"gui/{os.getuid()}/com.doogeun.aiskillbox",
    ],
    "reinstall_skills": [],  # 특수: 핸들러 내부 처리
    "gemini_quota_status": [],  # 특수: 핸들러 내부 처리
}


def _t_run_op_command(cmd: str) -> dict:
    if cmd not in OP_COMMANDS:
        return {"ok": False, "error": f"허용 안 된 명령: {cmd}"}
    if cmd == "restart_aiskillbox":
        try:
            r = subprocess.run(OP_COMMANDS[cmd], capture_output=True, text=True, timeout=15)
            return {"ok": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr, "code": r.returncode}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}
    if cmd == "gemini_quota_status":
        qf = PROJECT_ROOT / "logs" / "gemini_quota.json"
        if qf.exists():
            try:
                return {"ok": True, "quota": json.loads(qf.read_text(encoding="utf-8"))}
            except Exception as e:  # noqa: BLE001
                return {"ok": False, "error": f"quota 파싱 실패: {e}"}
        return {"ok": True, "quota": None, "hint": "gemini_quota.json 없음 — 아직 호출 기록 없음"}
    if cmd == "reinstall_skills":
        # 글로벌 skills 와 mirror 디렉토리만 보고하는 안전 동작. 진짜 재설치는 별 도구.
        n = len(list(GLOBAL_SKILLS_DIR.glob("*/SKILL.md")))
        m = len(list(MIRROR_SKILLS_DIR.glob("*/SKILL.md")))
        return {"ok": True, "global_count": n, "mirror_count": m,
                "hint": "이 도구는 현황만 보고합니다. 실제 재설치는 collect 파이프라인이 수행."}
    return {"ok": False, "error": "알 수 없는 명령"}


def _t_write_config(patches: dict) -> dict:
    if not isinstance(patches, dict):
        return {"ok": False, "error": "patches 는 객체여야 합니다"}
    allowed = ("dedup", "ig_block", "chat", "notion", "library")
    res = config_store.patch(patches, allowed_prefixes=allowed)
    res["ok"] = True
    return res


def _t_edit_skill_md(slug: str, new_content: str) -> dict:
    if "/" in slug or ".." in slug:
        return {"ok": False, "error": "잘못된 슬러그"}
    if not new_content or len(new_content) > 200_000:
        return {"ok": False, "error": "본문이 비어있거나 너무 깁니다"}
    target = GLOBAL_SKILLS_DIR / slug / "SKILL.md"
    if not target.exists():
        return {"ok": False, "error": f"스킬 없음: {slug}"}
    backup_dir = PROJECT_ROOT / "logs" / "chat_skill_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"{slug}__{ts}.md"
    backup_path.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
    target.write_text(new_content, encoding="utf-8")
    # mirror 도 동시 갱신.
    mirror_target = MIRROR_SKILLS_DIR / slug / "SKILL.md"
    mirror_target.parent.mkdir(parents=True, exist_ok=True)
    mirror_target.write_text(new_content, encoding="utf-8")
    return {
        "ok": True,
        "global": str(target),
        "mirror": str(mirror_target),
        "backup": str(backup_path),
    }


def _t_merge_skills(slug_a: str, slug_b: str) -> dict:
    """slug_b 의 본문을 slug_a 에 합쳐넣고 slug_b 는 archive 로 이동.

    안전 정책: 진짜 LLM 합병은 시간/토큰 소모가 크므로 여기서는 mechanical merge —
    slug_a 의 ## 📎 출처 섹션에 slug_b 의 출처 URL append, slug_b 폴더는 archive 폴더로 이동.
    """
    if slug_a == slug_b:
        return {"ok": False, "error": "같은 슬러그 합병 불가"}
    a_path = GLOBAL_SKILLS_DIR / slug_a / "SKILL.md"
    b_path = GLOBAL_SKILLS_DIR / slug_b / "SKILL.md"
    if not a_path.exists() or not b_path.exists():
        return {"ok": False, "error": "한쪽 또는 양쪽 스킬을 찾을 수 없습니다"}

    a_text = a_path.read_text(encoding="utf-8")
    b_text = b_path.read_text(encoding="utf-8")

    # b 의 출처 URL 들을 a 의 출처 섹션에 append (간단 정규식 처리).
    import re as _re
    b_urls = _re.findall(r"https?://\S+", b_text)
    if b_urls:
        marker = "## 📎 출처"
        if marker in a_text:
            a_text = a_text.replace(
                marker,
                marker + "\n\n<!-- merged from " + slug_b + " -->\n"
                + "\n".join(f"- {u}" for u in b_urls) + "\n",
                1,
            )
        else:
            a_text += "\n\n## 📎 출처\n\n<!-- merged from " + slug_b + " -->\n" + \
                "\n".join(f"- {u}" for u in b_urls) + "\n"

    backup_dir = PROJECT_ROOT / "logs" / "chat_skill_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    (backup_dir / f"{slug_a}__pre-merge-{ts}.md").write_text(a_path.read_text(encoding="utf-8"), encoding="utf-8")
    (backup_dir / f"{slug_b}__archived-{ts}.md").write_text(b_text, encoding="utf-8")
    a_path.write_text(a_text, encoding="utf-8")

    # mirror 도 동기화.
    mirror_a = MIRROR_SKILLS_DIR / slug_a / "SKILL.md"
    mirror_a.parent.mkdir(parents=True, exist_ok=True)
    mirror_a.write_text(a_text, encoding="utf-8")

    # b 는 archive 로 이동 (글로벌 + mirror).
    archive_dir = GLOBAL_SKILLS_DIR / "_archived"
    archive_dir.mkdir(parents=True, exist_ok=True)
    target_archive = archive_dir / f"{slug_b}__{ts}"
    (GLOBAL_SKILLS_DIR / slug_b).rename(target_archive)
    mirror_b_dir = MIRROR_SKILLS_DIR / slug_b
    if mirror_b_dir.exists():
        mirror_archive = MIRROR_SKILLS_DIR / "_archived"
        mirror_archive.mkdir(parents=True, exist_ok=True)
        mirror_b_dir.rename(mirror_archive / f"{slug_b}__{ts}")

    # 임베딩 캐시에서도 slug_b 제거 + slug_a 재계산은 다음 collect 호출 때 자동.
    try:
        from scripts.analyzer import embedder
        embedder.invalidate([slug_b])
    except Exception:  # noqa: BLE001
        pass

    return {
        "ok": True,
        "merged_into": slug_a,
        "archived": str(target_archive),
        "added_urls": b_urls,
    }


def _t_rebuild_embeddings(slugs: list[str] | None = None) -> dict:
    from scripts.analyzer import embedder
    n = embedder.invalidate(slugs if slugs else None)
    return {"ok": True, "invalidated": n,
            "hint": "다음 collect 호출 또는 scan_existing_dedup 실행 시 재계산됩니다."}


def _t_escalate_fix(instruction: str, failed_url: str = "", job_id: str = "") -> dict:
    """코드 수정을 로컬 Claude Code(Max 플랜)에 위임 — 백그라운드 fix 잡."""
    from scripts.chat import fixer
    return fixer.start_fix(
        instruction,
        failed_url=failed_url or None,
        source_job_id=job_id or None,
    )


def _t_fix_status(limit: int = 5) -> dict:
    from scripts.chat import fixer
    return fixer.fix_status(limit=limit)


def _t_scan_existing_dedup(threshold: float = 0.75) -> dict:
    """일괄 스캔 트리거. 실제 작업은 subprocess 로 (블로킹 회피 위해 백그라운드)."""
    cmd = [
        str(PROJECT_ROOT / "venv" / "bin" / "python3"),
        "-m", "scripts.oneshot.scan_existing_dedup",
        "--threshold", str(threshold),
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {
            "ok": True,
            "pid": proc.pid,
            "hint": "백그라운드 실행 중. 끝나면 inbox/dedup_candidates.md 확인 (dedup_report 도구).",
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


# ── 등록 ─────────────────────────────────────────────────────────

def _register_all() -> None:
    register(ToolSpec(
        name="read_config",
        description="현재 aiskillbox 운영 설정(config.json) 전체를 조회합니다.",
        input_schema={"type": "object", "properties": {}, "required": []},
        handler=_t_read_config,
    ))
    register(ToolSpec(
        name="recent_jobs",
        description="최근 잡 요약(상태/오류/메시지)을 limit 개 반환합니다.",
        input_schema={
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 50}},
            "required": [],
        },
        handler=_t_recent_jobs,
    ))
    register(ToolSpec(
        name="tail_log",
        description="aiskillbox 의 launchd_stderr.log 끝부분을 lines 개 반환합니다.",
        input_schema={
            "type": "object",
            "properties": {"lines": {"type": "integer", "minimum": 1, "maximum": 500}},
            "required": [],
        },
        handler=_t_tail_log,
    ))
    register(ToolSpec(
        name="read_skill_md",
        description="글로벌 스킬 디렉토리에서 SKILL.md 를 읽어 반환합니다.",
        input_schema={
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
        handler=_t_read_skill_md,
    ))
    register(ToolSpec(
        name="list_skills",
        description="등록된 글로벌 스킬 슬러그 목록을 반환합니다.",
        input_schema={
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 500}},
            "required": [],
        },
        handler=_t_list_skills,
    ))
    register(ToolSpec(
        name="dedup_report",
        description="inbox/dedup_candidates.md 일괄 스캔 리포트를 반환합니다.",
        input_schema={"type": "object", "properties": {}, "required": []},
        handler=_t_dedup_report,
    ))
    register(ToolSpec(
        name="search_library",
        description=(
            "스킬 라이브러리(SKILL.md 79+건)를 자연어로 검색합니다 — 키워드 + 의미 하이브리드. "
            "'OO 관련 스킬 있어?' 류 질문에 먼저 호출. 결과는 slug/제목/설명/등급/스니펫/카탈로그 링크. "
            "본문 전문은 read_skill_md(slug) 로."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "자연어 질의 (2자 이상)"},
                "k": {"type": "integer", "minimum": 1, "maximum": 20},
                "category": {
                    "type": "string",
                    "enum": ["", "프롬프트", "자동화", "콘텐츠", "디자인", "개발", "업무", "기타"],
                },
            },
            "required": ["query"],
        },
        handler=_t_search_library,
    ))

    # ── mutating ──
    register(ToolSpec(
        name="run_op_command",
        description=(
            "운영 명령을 실행합니다. 허용 명령: "
            "restart_aiskillbox(서비스 재기동), "
            "reinstall_skills(스킬 디렉토리 현황 보고), "
            "gemini_quota_status(쿼터 현황)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "cmd": {
                    "type": "string",
                    "enum": list(OP_COMMANDS.keys()),
                },
            },
            "required": ["cmd"],
        },
        handler=_t_run_op_command,
        mutating=True,
    ))
    register(ToolSpec(
        name="write_config",
        description=(
            "config.json 의 dedup.* / ig_block.* / chat.* / notion.* / library.* 키만 패치 가능 "
            "(notion.register_on_collect 로 수집 시 Notion 등록 on/off). "
            "patches 는 점 표기 키와 값의 객체. 예: {\"dedup.threshold\": 0.85}."
        ),
        input_schema={
            "type": "object",
            "properties": {"patches": {"type": "object"}},
            "required": ["patches"],
        },
        handler=_t_write_config,
        mutating=True,
    ))
    register(ToolSpec(
        name="edit_skill_md",
        description=(
            "SKILL.md 본문을 통째 교체합니다. 변경 전 자동 백업. "
            "이 도구는 코드(.py) 가 아닌 SKILL.md 만 다룹니다."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "new_content": {"type": "string"},
            },
            "required": ["slug", "new_content"],
        },
        handler=_t_edit_skill_md,
        mutating=True,
    ))
    register(ToolSpec(
        name="merge_skills",
        description=(
            "slug_b 를 slug_a 로 합치고 slug_b 는 _archived 폴더로 이동합니다. "
            "출처 URL 만 mechanical 하게 추가. 본문 재작성이 필요하면 edit_skill_md 추가 호출."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "slug_a": {"type": "string"},
                "slug_b": {"type": "string"},
            },
            "required": ["slug_a", "slug_b"],
        },
        handler=_t_merge_skills,
        mutating=True,
    ))
    register(ToolSpec(
        name="rebuild_embeddings",
        description=(
            "embeddings.json 캐시를 무효화합니다. slugs 비우면 전체 캐시 비움. "
            "다음 collect 호출 또는 scan_existing_dedup 실행 시 재계산."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "slugs": {"type": "array", "items": {"type": "string"}},
            },
            "required": [],
        },
        handler=_t_rebuild_embeddings,
        mutating=True,
    ))
    register(ToolSpec(
        name="escalate_fix",
        description=(
            "코드 수정을 로컬 Claude Code(Max 플랜)에 위임합니다. 스크래퍼/파이프라인 버그 등 "
            "코드 본체 수정이 필요할 때 사용. instruction 에 증상 + 의심 원인 + 검증 방법을 "
            "한국어로 요약해 담으세요. 실패한 수집 잡이 있으면 job_id 를, 문제의 URL 이 있으면 "
            "failed_url 을 함께 전달 (수정 후 자동 재스크랩 검증에 사용). "
            "백그라운드 실행 (최대 15분), 동시 1건. 검증 실패 시 자동 원복, 성공 시 서비스 자동 재기동 + "
            "Web Push 알림."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "instruction": {"type": "string", "description": "수정 지시 (증상+원인+검증법 요약)"},
                "failed_url": {"type": "string", "description": "재스크랩 검증에 쓸 문제 URL (선택)"},
                "job_id": {"type": "string", "description": "실패한 수집 잡 id (선택 — 에러 컨텍스트 자동 첨부)"},
            },
            "required": ["instruction"],
        },
        handler=_t_escalate_fix,
        mutating=True,
    ))
    register(ToolSpec(
        name="fix_status",
        description="escalate_fix 로 시작한 자동수정 잡의 최근 상태를 반환합니다.",
        input_schema={
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 20}},
            "required": [],
        },
        handler=_t_fix_status,
    ))
    register(ToolSpec(
        name="scan_existing_dedup",
        description=(
            "기존 모든 스킬을 일괄 임베딩 → 중복 후보 리포트를 생성합니다. "
            "백그라운드 실행이고, 완료 후 inbox/dedup_candidates.md 에 저장."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "threshold": {"type": "number", "minimum": 0.5, "maximum": 0.99},
            },
            "required": [],
        },
        handler=_t_scan_existing_dedup,
        mutating=True,
    ))


_register_all()
