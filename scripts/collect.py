"""콘텐츠랩 v4.0 메인 진입점.

URL → 스크랩 → Gemini 분석 → (중복 합병) → SKILL.md → 글로벌+mirror 설치 → Notion 등록

모든 단계 실패는 **한글 사유 + 우회 안내** 형태로 결과 JSON에 포함.
한 단계가 실패해도 다른 단계는 계속 시도 (부분 성공 허용).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")
except ImportError:
    pass

from scripts.scraper import scrape, detect_source
# 분석에 들어갈 최소 본문 길이 — 스크래퍼 폴백 트리거와 같은 기준을 쓴다 (SCRAPER_MIN_TEXT_LEN 로 조정).
from scripts.scraper.router import MIN_TEXT_LEN
from scripts.analyzer import analyze
from scripts.analyzer.merger import merge_with_existing
from scripts.skill_builder import render_skill_md, install_skill, mirror_skill
from scripts.skill_builder.installer import find_existing_by_url, find_global_by_slug, find_mirror_by_slug
from scripts.notion_client import register_skill, check_duplicate, curate_after_register


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _humanize_scrape_error(scrape_res) -> tuple[str, str]:
    """스크랩 실패 사유를 한글로 변환 + 우회 가이드."""
    err = scrape_res.error or ""
    src = scrape_res.source_type
    if "yt-dlp" in err:
        if "Sign in" in err or "login" in err.lower():
            return ("로그인 필요한 콘텐츠 — 비공개 또는 연령 제한.",
                    "공개 영상으로 다시 시도하거나 캡션/설명을 직접 텍스트로 입력")
        return ("yt-dlp 실패 — 일부 SNS는 봇 차단 강화 중.",
                "Cloudflare MCP(firecrawl)로 우회 시도 또는 다른 URL 사용")
    if "playwright" in err.lower() or "chromium" in err.lower():
        return ("브라우저 엔진 미설치 또는 실행 실패.",
                "터미널에서 `cd ~/Developer/my-company/content-lab && ./venv/bin/playwright install chromium`")
    if "empty body" in err or "빈" in err:
        return (f"{src.upper()} 페이지에서 본문을 추출하지 못했습니다.",
                "로그인 벽 또는 JS heavy 페이지일 가능성. 다른 URL 또는 모바일 버전 시도")
    if "404" in err or "private" in err.lower():
        return ("페이지가 없거나 비공개입니다.", "URL 재확인 또는 공개 페이지로 변경")
    if "timeout" in err.lower() or "TimeoutExpired" in err:
        return ("페이지 로딩 시간 초과 (45초).", "느린 사이트 또는 네트워크 이슈. 1-2분 후 재시도")
    return (f"스크랩 실패 ({src}) — {err[:200]}",
            "URL 확인 후 재시도. 지속 시 다른 출처 또는 텍스트 직접 입력")


def _short_text_hint(scrape_res) -> str:
    """본문 부족의 출처별 우회 안내 — 사용자가 다음에 뭘 하면 되는지까지."""
    url = (scrape_res.url or "").lower()
    src = scrape_res.source_type
    if "chatgpt.com" in url or "chat.openai.com" in url:
        return ("ChatGPT 공유·GPT 링크는 로그인 벽이라 본문 수집이 구조적으로 불가능합니다. "
                "대화 내용을 복사해 노션 등에 붙여넣고 그 공개 URL로 등록해 주세요.")
    if src == "notion":
        return ("노션이라면 [Share] → [Publish to web] 이 켜져 있는지 확인 후 재시도해 주세요. "
                "공개 상태인데 반복되면 잠시 후 다시 시도하면 대개 풀립니다.")
    if src in ("instagram", "tiktok", "twitter"):
        return "SNS는 로그인 벽이 강합니다. 캡션을 직접 텍스트로 옮겨 등록해 주세요."
    return "다른 URL(모바일 버전·원문 링크)로 시도하거나, 본문을 직접 텍스트로 옮겨 등록해 주세요."


def _humanize_analyze_error(analysis) -> tuple[str, str]:
    err = (analysis.error or "").lower()
    if "gemini_api_key" in err or "미설정" in err:
        return ("Gemini API 키가 .env에 없습니다.",
                "https://aistudio.google.com/apikey 에서 발급 → .env GEMINI_API_KEY")
    if "quota" in err or "429" in err or "limit" in err:
        return ("Gemini 무료 한도 (일 1500회) 초과.", "자정 (PST) 리셋. 또는 다른 API 키")
    if "404" in err or "not found" in err:
        return ("Gemini 모델을 찾을 수 없습니다.", "google-generativeai 업그레이드 (pip install -U)")
    if "permission" in err or "403" in err:
        return ("Gemini API 키 권한 없음.", "API 키 재발급 또는 결제 정보 확인")
    return (f"AI 분석 실패 — {analysis.error[:200] if analysis.error else 'unknown'}",
            "1분 후 재시도. 지속 시 .env 확인")


# LLM 이 스킬명 생성에 실패했을 때 흘러나오는 무의미 슬러그. 서로 무관한 콘텐츠가 같은 이름을
# 받아 한 스킬로 합쳐지는 사고의 근원이라 합병 후보에서 영구 제외한다.
GENERIC_SLUGS = {
    "untitled-skill", "untitled", "unnamed-skill", "unnamed",
    "unknown-skill", "unknown", "new-skill", "skill", "ai-skill", "no-title",
}


def _confirm_semantic_merge(analysis, slug: str, cand_path: Path, log) -> bool:
    """의미 dedup 후보를 LLM 으로 최종 확인 (v4.4.5).

    전수 페어 계측 결과 임베딩 점수만으로는 '실질 동일 스킬'(0.94~0.96)과
    '같은 주제·다른 스킬'(0.91~0.94)이 안 갈림 → 임계값 통과 후 로컬 Gemma 로
    같은 스킬인지 yes/no 확정. 실패/불확실 시 보수적으로 신규 등록 (오합병 방지).
    """
    try:
        from scripts.analyzer.gemini import call_gemma_json, _extract_json
        text = cand_path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        cand_desc = m.group(1).strip() if m else ""
        m = re.search(r"^# (.+)$", text, re.MULTILINE)
        cand_title = m.group(1).strip() if m else slug
        new_desc = (getattr(analysis, "callout", "") or getattr(analysis, "summary", "") or "")
        prompt = (
            "두 AI 스킬 문서가 '같은 스킬'인지 판정하라.\n"
            "같은 스킬 = 한쪽만 남기고 다른 쪽을 지워도 정보 손실이 거의 없는 관계.\n"
            f"[기존] {cand_title} — {cand_desc[:400]}\n"
            f"[신규] {analysis.skill_title_ko} — {new_desc[:400]}\n"
            "판정 기준:\n"
            "- 제목과 표현이 달라도 다루는 대상(도구·기능)과 목표가 같으면 same=true. "
            "같은 자료를 다르게 요약한 경우가 흔하므로 문구 차이는 근거가 못 된다.\n"
            "- 다루는 도구가 다르거나, 목표·결과물이 다르거나, 한쪽에만 있는 핵심 절차가 있으면 same=false.\n"
            "- '포괄적 vs 특정 기능' 같은 서술 범위 차이만으로 판단하지 말고 핵심 대상이 같은지를 봐라.\n"
            'JSON only: {"same": true, "reason": "1줄"}'
        )
        raw = call_gemma_json(prompt) or ""
        data = _extract_json(raw)
        same = bool(data.get("same"))
        log.info("의미 dedup LLM 확인: %s → same=%s (%s)", slug, same, str(data.get("reason", ""))[:80])
        return same
    except Exception as e:  # noqa: BLE001
        log.warning("의미 dedup LLM 확인 실패 (%s) — 보수적으로 신규 처리", e)
        return False


def collect(url: str, *, register_notion: bool = True, skip_duplicate: bool = False) -> dict:
    """전체 파이프라인. 실패 시 한글 사유 + 부분 성공 반환."""
    log = logging.getLogger("collect")
    summary: dict = {
        "url": url,
        "stages": {},
        "ok": False,
        "partial_ok": False,  # 일부 단계만 성공
    }

    # ── 1. 스크랩 ──────────────────────────────────────────────────
    source_type = detect_source(url)
    log.info("[1/5] 스크랩 시작 type=%s", source_type)
    summary["stages"]["scrape"] = {"stage": "스크래핑", "ok": None}
    try:
        scrape_res = scrape(url)
    except Exception as e:  # noqa: BLE001
        log.exception("스크랩 예외")
        summary["stages"]["scrape"] = {
            "stage": "스크래핑", "ok": False,
            "error_ko": f"스크래핑 단계에서 예기치 못한 오류: {e}",
            "hint": "logs/launchd_stderr.log 확인",
        }
        summary["error_ko"] = summary["stages"]["scrape"]["error_ko"]
        summary["hint"] = summary["stages"]["scrape"]["hint"]
        return summary

    # 의도적 사전 차단 (IG 로그인 벽 등) — 실패가 아닌 'skipped' 로 깔끔 종료.
    if getattr(scrape_res, "skip_reason", None):
        summary["stages"]["scrape"] = {
            "stage": "스크래핑",
            "ok": True,
            "source_type": scrape_res.source_type,
            "skipped": True,
            "skip_reason": scrape_res.skip_reason,
        }
        summary["ok"] = True
        summary["skipped"] = True
        summary["skip_kind"] = "blocked"  # UI 배지 구분 — '이미 등록됨' 아님
        summary["message_ko"] = scrape_res.skip_message_ko or "사전 차단된 URL 입니다."
        return summary

    text_len = len(scrape_res.text or "")
    summary["stages"]["scrape"] = {
        "stage": "스크래핑",
        "ok": scrape_res.ok and bool(scrape_res.text.strip()),
        "source_type": scrape_res.source_type,
        "title": scrape_res.title,
        "text_length": text_len,
    }
    if not summary["stages"]["scrape"]["ok"]:
        msg_ko, hint = _humanize_scrape_error(scrape_res)
        summary["stages"]["scrape"]["error_ko"] = msg_ko
        summary["stages"]["scrape"]["hint"] = hint
        summary["error_ko"] = msg_ko
        summary["hint"] = hint
        return summary

    # 본문이 너무 짧으면 LLM 을 부르지 않고 여기서 끝낸다.
    # 예전에는 그대로 분석에 넘겨서 Gemini 가 빈약한 입력으로 등급 C 를 내렸고, 사용자에겐
    # "가치 없는 콘텐츠" 로 표시됐다 — 실제 사유는 로그인 벽/렌더 실패인데 콘텐츠 탓으로 오인됨
    # (실사고 2026-08-13: ChatGPT 공유 링크 106자 → 등급 C). 사유를 정확히 알려주고 쿼터도 아낀다.
    if text_len < MIN_TEXT_LEN:
        summary["stages"]["scrape"]["ok"] = False
        msg_ko = (
            f"본문을 {text_len}자밖에 가져오지 못했습니다 (분석에 최소 {MIN_TEXT_LEN}자 필요). "
            "로그인이 필요한 페이지이거나 JS 렌더링이 끝나기 전 화면만 잡혔을 가능성이 큽니다."
        )
        hint = _short_text_hint(scrape_res)
        summary["stages"]["scrape"]["error_ko"] = msg_ko
        summary["stages"]["scrape"]["hint"] = hint
        summary["error_ko"] = msg_ko
        summary["hint"] = hint
        log.warning("본문 부족 %d자 (<%d) → 분석 생략", text_len, MIN_TEXT_LEN)
        return summary

    # ── 2. 분석 ────────────────────────────────────────────────────
    log.info("[2/5] Gemini 분석 시작")
    summary["stages"]["analyze"] = {"stage": "AI 분석", "ok": None}
    analysis = analyze(scrape_res.to_dict())
    summary["stages"]["analyze"]["ok"] = analysis.ok
    summary["stages"]["analyze"]["skill_name"] = analysis.skill_name
    summary["stages"]["analyze"]["grade"] = analysis.grade
    summary["stages"]["analyze"]["category"] = analysis.category

    if not analysis.ok:
        msg_ko, hint = _humanize_analyze_error(analysis)
        summary["stages"]["analyze"]["error_ko"] = msg_ko
        summary["stages"]["analyze"]["hint"] = hint
        summary["error_ko"] = msg_ko
        summary["hint"] = hint
        return summary

    if analysis.grade == "C":
        # 여기 도달했다는 건 본문은 충분히 확보됐다는 뜻 (위 MIN_TEXT_LEN 게이트 통과).
        # 즉 진짜로 '내용은 읽었는데 스킬 가치가 없다' 는 판정이므로 그렇게 안내한다.
        reason = (analysis.grade_reason or "").strip()
        summary["stages"]["analyze"]["note"] = f"등급 C — 활용 불가 ({reason})"
        summary["ok"] = True  # 분석 자체는 성공
        summary["message_ko"] = (
            f"본문 {text_len}자를 읽었지만 스킬로 등록할 가치가 없다고 판정했습니다 (등급 C). DB에 안 올라감."
            + (f" 사유: {reason}" if reason else "")
        )
        return summary

    # ── 3. 중복 감지 → 합병 ────────────────────────────────────────
    def _lab_origin(p) -> bool:
        """SKILL.md 가 content-lab 산출물인지 (frontmatter origin). 수동 설치 스킬 보호용."""
        try:
            return "origin: content-lab" in p.read_text(encoding="utf-8", errors="replace")[:800]
        except Exception:  # noqa: BLE001
            return False

    def _sources_contain(p, target_url: str) -> bool:
        """기존 SKILL.md 의 sources: 에 이 URL 이 이미 있는지 (정규화 비교)."""
        try:
            from scripts.skill_builder.installer import _frontmatter_sources, normalize_url
            srcs = _frontmatter_sources(p.read_text(encoding="utf-8", errors="replace"))
            return normalize_url(target_url) in {normalize_url(u) for u in srcs}
        except Exception:  # noqa: BLE001
            return False

    def _next_free_slug(base: str) -> str:
        n = 2
        while find_global_by_slug(f"{base}-{n}") or find_mirror_by_slug(f"{base}-{n}"):
            n += 1
        return f"{base}-{n}"

    existing = find_global_by_slug(analysis.skill_name)
    if existing and not _lab_origin(existing):
        # 글로벌 ~/.claude/skills/ 의 수동 설치 스킬과 슬러그 충돌 — 합병하면 그 스킬이
        # 파괴되고 Notion 에 엉뚱한 페이지가 생김. 접미사 붙여 신규 슬러그로 회피.
        base = analysis.skill_name
        analysis.skill_name = _next_free_slug(base)
        log.warning("슬러그 충돌: %s 는 content-lab 소유 아님 → %s 로 신규 등록", base, analysis.skill_name)
        existing = None
    if not existing:
        existing = find_mirror_by_slug(analysis.skill_name)

    # 슬러그가 같다는 이유만으로 합병하면 안 된다. LLM 이 서로 다른 콘텐츠에 같은 이름을 붙이는
    # 일이 실제로 있었고 (실사고: 'untitled-skill' 하나에 주식 시장 분석 + Claude 프롬프트 60선이
    # 통째로 합쳐짐), 이 경로는 임계값·임베딩·LLM 게이트를 전부 우회했다.
    # 같은 URL 재수집이면 내용 확인이 불필요하니 그대로 통과시키고, 그 외에는 의미 게이트를 태운다.
    if existing and not _sources_contain(existing, url):
        base = analysis.skill_name
        if base in GENERIC_SLUGS:
            # LLM 이 이름 짓기에 실패했을 때 나오는 무의미 슬러그 — 서로 무관한 콘텐츠가
            # 여기로 전부 빨려 들어간다. 절대 합병 후보로 쓰지 않는다.
            analysis.skill_name = _next_free_slug(base)
            log.warning("범용 슬러그(%s) 합병 차단 → %s 로 신규 등록", base, analysis.skill_name)
            existing = None
        elif not _confirm_semantic_merge(analysis, base, existing, log):
            analysis.skill_name = _next_free_slug(base)
            log.warning("슬러그는 같으나 내용 불일치(%s) → %s 로 신규 등록", base, analysis.skill_name)
            existing = None

    if not existing:
        existing = find_existing_by_url(url)
    # 위 두 단계가 모두 미스면 — 의미 임베딩 dedup 시도. 후보가 있으면 그 슬러그의
    # 기존 SKILL.md 경로를 existing 으로 채택.
    semantic_hit: str | None = None
    if not existing:
        try:
            from scripts.analyzer.dedup_finder import find_semantic_candidates
            candidates = find_semantic_candidates(analysis, exclude_slug=analysis.skill_name)
            # 범용 슬러그 스킬은 내용이 뒤섞여 있어 임베딩이 아무 주제에나 가깝게 나온다 —
            # 후보에서 배제하지 않으면 dedup 이 여기로 계속 빨려 들어간다.
            candidates = [c for c in candidates if c.slug not in GENERIC_SLUGS]
            if candidates:
                top = candidates[0]
                gp = find_global_by_slug(top.slug)
                if gp and not _lab_origin(gp):
                    gp = None  # 남의 스킬로는 합병 금지 — mirror 쪽만 후보
                cand_path = gp or find_mirror_by_slug(top.slug)
                if cand_path and _confirm_semantic_merge(analysis, top.slug, cand_path, log):
                    existing = cand_path
                    semantic_hit = top.slug
                    log.info("의미 dedup 매칭: %s (score=%.3f)", top.slug, top.score)
        except Exception as e:  # noqa: BLE001
            log.warning("의미 dedup 스킵 (%s) — 신규로 진행", e)
    if existing:
        if skip_duplicate:
            summary["stages"]["merge"] = {
                "stage": "중복 처리", "ok": True,
                "action": "스킵 (사용자 옵션)",
                "existing": str(existing),
            }
            summary["ok"] = True
            summary["skipped"] = True
            summary["skip_kind"] = "duplicate"
            summary["message_ko"] = "이미 등록된 스킬 — 스킵 옵션으로 합병 안 함"
            return summary
        try:
            analysis = merge_with_existing(existing, analysis, url, scrape_res.source_type)
            summary["stages"]["merge"] = {
                "stage": "중복 합병", "ok": True,
                "existing": str(existing),
                "source_count": len(analysis.raw.get("_merged_source_urls", [])),
                "match_kind": "semantic" if semantic_hit else "exact",
                "semantic_hit": semantic_hit,
            }
        except Exception as e:  # noqa: BLE001
            log.warning("합병 실패, 신규로 진행: %s", e)
            summary["stages"]["merge"] = {
                "stage": "중복 합병", "ok": False,
                "error_ko": f"합병 실패 — 신규 스킬로 저장: {e}",
                "hint": "기존 SKILL.md 형식이 손상되었을 수 있음",
            }
    else:
        summary["stages"]["merge"] = {"stage": "중복 처리", "ok": True, "action": "신규"}

    # ── 4. SKILL.md 생성 + 설치 ───────────────────────────────────
    try:
        skill_md = render_skill_md(analysis, url, scrape_res.source_type)
        global_path, was_new = install_skill(analysis, skill_md)
        mirror_path = mirror_skill(analysis, skill_md)
        summary["stages"]["install"] = {
            "stage": "스킬 파일 저장", "ok": True,
            "global": str(global_path),
            "mirror": str(mirror_path),
            "new": was_new,
        }
        # 임베딩 캐시 갱신 — 다음 번 신규 스킬 dedup 후보가 되게.
        try:
            from scripts.analyzer.dedup_finder import _component_text
            from scripts.analyzer import embedder as _embedder
            from scripts import config_store as _cfg
            # dedup_finder 의 쿼리 벡터와 반드시 같은 컴포넌트 기준 — 하드코딩 금지
            # (기준이 어긋나면 코사인 점수가 비대칭이 돼 dedup 판정 신뢰도 붕괴).
            components = _cfg.get("dedup.components", ["callout", "ai_tools", "category"])
            text_for_embed = _component_text(analysis, components)
            if text_for_embed:
                _embedder.get_or_embed(analysis.skill_name, text_for_embed)
        except Exception as e:  # noqa: BLE001
            log.warning("임베딩 캐시 갱신 실패: %s", e)
    except Exception as e:  # noqa: BLE001
        log.exception("SKILL.md 저장 실패")
        summary["stages"]["install"] = {
            "stage": "스킬 파일 저장", "ok": False,
            "error_ko": f"파일 저장 실패: {e}",
            "hint": "디스크 권한 또는 경로 문제. ~/.claude/skills/ 확인",
        }
        summary["error_ko"] = summary["stages"]["install"]["error_ko"]
        summary["hint"] = summary["stages"]["install"]["hint"]
        return summary

    # ── 5. Notion 등록 (실패해도 부분 성공으로 진행) ─────────────────
    if register_notion:
        # 새 URL 만으로 조회하면 합병(특히 의미 dedup) 시 기존 페이지를 못 찾아
        # 같은 스킬의 Notion 페이지가 합병마다 하나씩 늘어남 (실사고: 6개 스킬 × 2~6페이지).
        # 누적된 모든 출처 URL 로 조회 + 합병 케이스는 제목 완전 일치 2차 안전망.
        dup_urls = list(analysis.raw.get("_merged_source_urls") or []) + [url]
        existing_page = None
        for u in dup_urls:
            existing_page = check_duplicate(u)
            if existing_page:
                break
        if not existing_page and analysis.raw.get("_is_merged"):
            try:
                from scripts.notion_client.register import find_by_title
                existing_page = find_by_title(analysis.skill_title_ko)
            except Exception as e:  # noqa: BLE001
                log.warning("제목 기반 중복 체크 스킵: %s", e)
        notion_res = register_skill(
            analysis, url, scrape_res.source_type, skill_md,
            existing_page_id=existing_page,
        )
        if notion_res.get("ok"):
            summary["stages"]["notion"] = {
                "stage": "Notion 등록", "ok": True,
                "page_id": notion_res["page_id"],
                "action": notion_res.get("action", ""),
            }
            page_id = notion_res["page_id"]
            clean = page_id.replace("-", "")
            summary["notion_web_url"] = f"https://www.notion.so/{clean}"

            # 자동 큐레이션: 관련 스킬 relation 연결
            try:
                curated = curate_after_register(page_id, analysis)
                if curated.get("related_linked"):
                    summary["stages"]["curate"] = {
                        "stage": "관련 스킬 연결", "ok": True,
                        "linked": curated["related_linked"],
                    }
            except Exception as e:  # noqa: BLE001
                log.warning("자동 큐레이션 실패: %s", e)
        else:
            summary["stages"]["notion"] = {
                "stage": "Notion 등록", "ok": False,
                "error_ko": notion_res.get("error_ko", "알 수 없는 오류"),
                "code": notion_res.get("code", ""),
                "hint": notion_res.get("hint", ""),
            }
    else:
        summary["stages"]["notion"] = {"stage": "Notion 등록", "ok": True, "action": "건너뜀 (옵션)"}

    # ── 최종 판정 ───────────────────────────────────────────────────
    notion_ok = summary["stages"]["notion"]["ok"]
    if notion_ok:
        summary["ok"] = True
        summary["message_ko"] = (
            f"✅ 완료 — {analysis.skill_name} ({analysis.grade}/{analysis.category})"
            + (" 🔀 합병됨" if analysis.raw.get("_is_merged") else "")
        )
    else:
        # 부분 성공 — SKILL.md는 저장됐지만 Notion만 실패
        summary["ok"] = True  # 사용자가 결과 확인하려면 ok:True 줘야 UI가 정상 표시
        summary["partial_ok"] = True
        summary["message_ko"] = (
            f"⚠️ 부분 성공 — 로컬 스킬은 저장됨 ({analysis.skill_name}). "
            f"Notion만 실패: {summary['stages']['notion'].get('error_ko','')}"
        )
        summary["error_ko"] = summary["stages"]["notion"].get("error_ko", "")
        summary["hint"] = summary["stages"]["notion"].get("hint", "")

    summary["skill"] = {
        "name": analysis.skill_name,
        "title": analysis.skill_title_ko,
        "grade": analysis.grade,
        "category": analysis.category,
        "merged": bool(analysis.raw.get("_is_merged")),
        "source_count": len(analysis.raw.get("_merged_source_urls") or [url]),
    }
    # v4.5 스킬 라이브러리 — 카탈로그 딥링크 (mirror 에 저장된 순간부터 /api/library, /catalog 에서 검색 가능)
    summary["catalog_url"] = f"/catalog#{analysis.skill_name}"

    # Hub 상단 카테고리별 목록 자동 동기화 (best-effort, 실패해도 잡은 성공 처리)
    if register_notion and notion_ok:
        try:
            from scripts import sync_hub
            hub_res = sync_hub.sync(limit_per_column=20, dry_run=False)
            summary["stages"]["hub_sync"] = {
                "stage": "Hub 카테고리 갱신", "ok": bool(hub_res.get("ok")),
                "total_rows": hub_res.get("total_rows"),
            }
        except Exception as e:  # noqa: BLE001
            log.warning("Hub 동기화 실패 (등록 자체는 성공): %s", e)
            summary["stages"]["hub_sync"] = {"stage": "Hub 카테고리 갱신", "ok": False, "error": str(e)}

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="콘텐츠랩 v4.0 — URL → 스킬 자산화 (자동 합병)")
    parser.add_argument("url")
    notion_grp = parser.add_mutually_exclusive_group()
    notion_grp.add_argument("--notion", action="store_true", help="Notion 등록 강제 (config 무관)")
    notion_grp.add_argument("--no-notion", action="store_true", help="Notion 등록 생략 (config 무관)")
    parser.add_argument("--skip-duplicate", action="store_true")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    args = parser.parse_args()

    setup_logging(args.log_level)
    # v4.5: 기본값은 config.json notion.register_on_collect (기본 False — SKILL.md 가 유일한 원본)
    if args.notion:
        register_notion = True
    elif args.no_notion:
        register_notion = False
    else:
        try:
            from scripts import config_store
            register_notion = bool(config_store.get("notion.register_on_collect", False))
        except Exception:  # noqa: BLE001
            register_notion = False
    result = collect(args.url, register_notion=register_notion, skip_duplicate=args.skip_duplicate)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
