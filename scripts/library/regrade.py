"""활용도 등급 재판정 (v5.3) — 라이브러리 전체(또는 일부)를 Claude 로 다시 등급 매긴다.

왜: 5월~9월 산출물의 68/119 가 S 였다 — 등급이 정보를 못 줬다. 사용자 원칙 (2026-09-16):
등급 = 활용도 (S 즉시 실행 / A 절차형 / B 개념·방법론 / C 정보·소개). 소장 가치가 아니므로 C 도 남긴다.
같은 rubric 이 analyzer/prompt.py 의 신규 수집 판정에도 들어간다 — 두 곳이 어긋나면 안 된다.

동작: 스킬 N개(기본 6)를 한 프롬프트에 묶어 `claude -p --json-schema` 로 판정 → 프론트매터 패치.
- grade 는 항상 새 판정으로 교체
- category / difficulty / ai_tools 는 비었거나 enum 밖일 때만 채움 (`--recategorize` 면 category 도 교체)
- mirror(skills/) 와 글로벌(~/.claude/skills, origin: content-lab 인 것만) 둘 다 패치
- 결과는 logs/regrade_<date>.jsonl 에 남긴다. 기본은 dry-run.

    venv/bin/python -m scripts.library.regrade                 # 판정만 출력
    venv/bin/python -m scripts.library.regrade --apply         # 적용
    venv/bin/python -m scripts.library.regrade --apply --recategorize --only a,b
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from scripts.analyzer import claude_cli
from scripts.analyzer.gemini import _extract_json
from scripts.analyzer.prompt import GRADES, CATEGORIES, DIFFICULTIES, AI_TOOLS
from scripts.skill_builder.installer import LOCAL_MIRROR_DIR, _global_skills_dir

logger = logging.getLogger(__name__)

BATCH_SIZE = 6
BODY_CAP = 2500
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RUBRIC = (
    "등급은 활용도다 — 소장 가치가 아니다. 어떤 등급이든 스킬은 라이브러리에 남는다.\n"
    "- S 즉시 실행: 복붙 가능한 프롬프트·명령·코드·설정이 들어 있고, 그대로 따라 하면 결과가 나온다. 재현 절차 완결\n"
    "- A 절차형: 단계별 방법은 있으나 사용자가 채워야 할 부분(도구 가입·파라미터·자료)이 있다. 프롬프트 원문이 일부만\n"
    "- B 개념·방법론: 원리·사고법·체크리스트·비교. 실행하려면 스스로 설계해야 한다\n"
    "- C 정보·소개: 도구 소개, 기능 목록, 뉴스, 홍보, 후기. 따라 할 절차가 없다. 참고·소장용\n"
    "판정 원칙: 길이가 아니라 '따라 하면 되는가'. 길어도 절차가 없으면 C, 짧아도 복붙 프롬프트 하나가 완결이면 S."
)

JUDGE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "grade": {"type": "string", "enum": list(GRADES)},
                    "grade_reason": {"type": "string"},
                    "category": {"type": "string", "enum": list(CATEGORIES)},
                    "difficulty": {"type": "string", "enum": list(DIFFICULTIES)},
                    "ai_tools": {"type": "array", "items": {"type": "string", "enum": list(AI_TOOLS)}},
                },
                "required": ["slug", "grade", "grade_reason", "category", "difficulty", "ai_tools"],
            },
        }
    },
    "required": ["items"],
}

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


@dataclass
class SkillDoc:
    slug: str
    path: Path
    title: str = ""
    description: str = ""
    grade: str = ""
    category: str = ""
    difficulty: str = ""
    ai_tools: list[str] = field(default_factory=list)
    body: str = ""


def _fm_get(fm: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
    return m.group(1).strip() if m else ""


def _parse_tools(value: str) -> list[str]:
    quoted = re.findall(r'"([^"]+)"', value)
    if quoted:
        return quoted
    inner = value.strip().strip("[]")
    return [x.strip() for x in inner.split(",") if x.strip()]


def load_skill(path: Path) -> SkillDoc:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    m = _FM_RE.match(text)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)
    t = re.search(r"^# (.+)$", body, re.M)
    title = (t.group(1).strip() if t else "").replace(" (합병됨)", "")
    return SkillDoc(
        slug=Path(path).parent.name, path=Path(path), title=title,
        description=_fm_get(fm, "description"), grade=_fm_get(fm, "grade").upper(),
        category=_fm_get(fm, "category"), difficulty=_fm_get(fm, "difficulty"),
        ai_tools=_parse_tools(_fm_get(fm, "ai_tools")), body=body.strip(),
    )


def load_all(mirror_dir: Path | str = LOCAL_MIRROR_DIR) -> list[SkillDoc]:
    return [load_skill(p) for p in sorted(Path(mirror_dir).glob("*/SKILL.md"))]


def build_batches(docs: list[SkillDoc], size: int = BATCH_SIZE) -> list[list[SkillDoc]]:
    size = max(1, int(size))
    return [docs[i:i + size] for i in range(0, len(docs), size)]


def build_prompt(batch: list[SkillDoc]) -> str:
    blocks = []
    for d in batch:
        cur = f"{d.grade or '-'} / {d.category or '-'} / {d.difficulty or '-'}"
        blocks.append(
            f"### {d.slug}\n제목: {d.title}\n설명: {d.description}\n현재 등급/카테고리/난이도: {cur}\n"
            f"본문(앞 {BODY_CAP}자):\n{d.body[:BODY_CAP]}\n"
        )
    return (
        "너는 AI 스킬 라이브러리 큐레이터다. 아래 스킬들의 등급·카테고리·난이도·AI 도구를 판정하라.\n\n"
        f"[등급 기준]\n{RUBRIC}\n\n"
        f"[허용 값] category: {' / '.join(CATEGORIES)} | difficulty: {' / '.join(DIFFICULTIES)} | "
        f"ai_tools (0~5개, 이름 그대로): {' / '.join(AI_TOOLS)}\n\n"
        "[스킬 목록]\n" + "\n".join(blocks) +
        "\n[응답] items 배열에 스킬마다 하나씩, slug 는 위 그대로. grade_reason 은 판정 근거 1줄 (한국어)."
    )


def _norm_grade(g) -> str:
    s = str(g or "").strip().upper()
    return s[0] if s and s[0] in GRADES else ""


def parse_judgement(text: str, expected_slugs: set[str]) -> dict[str, dict]:
    try:
        data = _extract_json(text or "")
    except Exception:  # noqa: BLE001
        return {}
    out: dict[str, dict] = {}
    for it in (data.get("items") or []) if isinstance(data, dict) else []:
        if not isinstance(it, dict):
            continue
        slug = str(it.get("slug") or "").strip()
        grade = _norm_grade(it.get("grade"))
        if slug not in expected_slugs or not grade:
            continue
        cat = str(it.get("category") or "").strip()
        diff = str(it.get("difficulty") or "").strip()
        tools = [t for t in (it.get("ai_tools") or []) if isinstance(t, str) and t in AI_TOOLS]
        out[slug] = {
            "grade": grade,
            "grade_reason": str(it.get("grade_reason") or "").strip(),
            "category": cat if cat in CATEGORIES else "",
            "difficulty": diff if diff in DIFFICULTIES else "",
            "ai_tools": tools,
        }
    return out


def _set_line(lines: list[str], key: str, value: str) -> None:
    for i, ln in enumerate(lines):
        if ln.startswith(f"{key}:"):
            lines[i] = f"{key}: {value}"
            return
    # 없으면 sources: 앞에 (없으면 끝에) 삽입
    for i, ln in enumerate(lines):
        if ln.startswith("sources:"):
            lines.insert(i, f"{key}: {value}")
            return
    lines.append(f"{key}: {value}")


def apply_meta(text: str, fields: dict, *, recategorize: bool = False) -> str:
    """프론트매터만 패치. grade 는 항상, 나머지는 비었거나 enum 밖일 때만 (recategorize 면 category 도)."""
    m = _FM_RE.match(text)
    if not m:
        return text
    lines = m.group(1).split("\n")
    fm = m.group(1)
    grade = _norm_grade(fields.get("grade"))
    if grade:
        _set_line(lines, "grade", grade)
    cur_cat = _fm_get(fm, "category")
    if fields.get("category") and (recategorize or cur_cat not in CATEGORIES):
        _set_line(lines, "category", fields["category"])
    cur_diff = _fm_get(fm, "difficulty")
    if fields.get("difficulty") and cur_diff not in DIFFICULTIES:
        _set_line(lines, "difficulty", fields["difficulty"])
    cur_tools = _parse_tools(_fm_get(fm, "ai_tools"))
    if fields.get("ai_tools") and not cur_tools:
        _set_line(lines, "ai_tools", "[" + ", ".join(f'"{t}"' for t in fields["ai_tools"]) + "]")
    return "---\n" + "\n".join(lines) + "\n---\n" + m.group(2)


def _patch_file(path: Path, fields: dict, *, recategorize: bool) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    new = apply_meta(text, fields, recategorize=recategorize)
    if new != text:
        path.write_text(new, encoding="utf-8")


def regrade(
    docs: list[SkillDoc],
    *,
    call: Callable[..., Optional[str]] = claude_cli.call_claude_json,
    apply: bool = False,
    recategorize: bool = False,
    global_dir: Path | str | None = None,
    report_path: Path | str | None = None,
    batch_size: int = BATCH_SIZE,
    sleep_seconds: float = 0.0,
) -> list[dict]:
    gdir = Path(global_dir) if global_dir is not None else _global_skills_dir()
    rows: list[dict] = []
    batches = build_batches(docs, size=batch_size)
    for n, batch in enumerate(batches, 1):
        raw = call(build_prompt(batch), schema=JUDGE_SCHEMA)
        judged = parse_judgement(raw, {d.slug for d in batch}) if raw else {}
        if not judged:
            logger.warning("배치 %d/%d 판정 없음 (Claude 비활성·한도·파싱 실패) — 건너뜀", n, len(batches))
        for d in batch:
            f = judged.get(d.slug)
            row = {
                "slug": d.slug, "old_grade": d.grade or None, "new_grade": f["grade"] if f else None,
                "reason": f["grade_reason"] if f else None, "old_category": d.category or None,
                "category": f["category"] if f else None, "difficulty": f["difficulty"] if f else None,
                "applied": False, "ts": _dt.datetime.now().isoformat(timespec="seconds"),
            }
            if f and apply:
                _patch_file(d.path, f, recategorize=recategorize)
                gp = gdir / d.slug / "SKILL.md"
                if gp.exists() and "origin: content-lab" in gp.read_text(encoding="utf-8", errors="replace")[:800]:
                    _patch_file(gp, f, recategorize=recategorize)
                row["applied"] = True
            rows.append(row)
        if sleep_seconds and n < len(batches):
            time.sleep(sleep_seconds)
    if report_path:
        p = Path(report_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="스킬 라이브러리 활용도 등급 재판정 (Claude)")
    ap.add_argument("--apply", action="store_true", help="프론트매터에 적용 (기본 dry-run)")
    ap.add_argument("--recategorize", action="store_true", help="유효한 category 도 새 판정으로 교체")
    ap.add_argument("--only", default="", help="쉼표로 구분한 슬러그만")
    ap.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    ap.add_argument("--sleep", type=float, default=20.0, help="배치 사이 대기(초) — 119 가드 임계 아래 유지")
    ap.add_argument("--report", default=str(PROJECT_ROOT / "logs" / f"regrade_{_dt.date.today():%Y%m%d}.jsonl"))
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    docs = load_all()
    if args.only:
        keep = {s.strip() for s in args.only.split(",") if s.strip()}
        docs = [d for d in docs if d.slug in keep]
    rows = regrade(docs, apply=args.apply, recategorize=args.recategorize, batch_size=args.batch_size,
                   sleep_seconds=args.sleep, report_path=args.report)
    changed = [r for r in rows if r["new_grade"] and r["new_grade"] != r["old_grade"]]
    missed = [r["slug"] for r in rows if not r["new_grade"]]
    for r in rows:
        mark = "→" if r["new_grade"] != r["old_grade"] else "="
        print(f"{r['slug']:48s} {r['old_grade'] or '-'} {mark} {r['new_grade'] or '?'}  {(r['reason'] or '')[:70]}")
    print(f"\n총 {len(rows)}건 · 변경 {len(changed)}건 · 판정 없음 {len(missed)}건 · {'적용됨' if args.apply else 'dry-run'}")
    if missed:
        print("판정 없음:", ", ".join(missed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
