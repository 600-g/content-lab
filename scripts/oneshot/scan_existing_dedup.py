"""기존 ~/.claude/skills/ 의 모든 SKILL.md 를 일괄 임베딩 → 중복 후보 리포트.

사용:
    python -m scripts.oneshot.scan_existing_dedup
    python -m scripts.oneshot.scan_existing_dedup --threshold 0.75 --out inbox/dedup_candidates.md

출력: 마크다운 리포트 (점수 내림차순, threshold 이상 페어만).
자동 합병 X. 사용자가 검토 후 채팅으로 "리포트 N번 합병해줘" 실행.
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

from scripts.analyzer import embedder

logger = logging.getLogger(__name__)

GLOBAL_SKILLS_DIR = Path(
    os.path.expanduser(os.getenv("SKILL_INSTALL_DIR", "~/.claude/skills"))
)


def _parse_frontmatter(md_text: str) -> dict:
    """간단한 YAML 프론트매터 파서 — name/description/category/ai_tools 만 추출."""
    if not md_text.startswith("---"):
        return {}
    end = md_text.find("---", 3)
    if end == -1:
        return {}
    block = md_text[3:end]
    out: dict[str, object] = {}
    list_key: str | None = None
    list_acc: list[str] = []
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if list_key and line.lstrip().startswith("- "):
            list_acc.append(line.lstrip()[2:].strip(' "\''))
            continue
        if list_key and not line.lstrip().startswith("- "):
            out[list_key] = list_acc
            list_key = None
            list_acc = []
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1).strip(), m.group(2).strip()
        if val == "" or val == "|":
            list_key = key
            list_acc = []
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [x.strip().strip(' "\'') for x in inner.split(",") if x.strip()]
            out[key] = items
            continue
        out[key] = val.strip().strip(' "\'')
    if list_key:
        out[list_key] = list_acc
    return out


def _extract_callout(md_text: str) -> str:
    """본문에서 💡 callout 한 단락 추출. 실패 시 빈 문자열."""
    m = re.search(r"^💡\s*(.+?)(?:\n\n|\Z)", md_text, re.S | re.M)
    if m:
        return m.group(1).strip()
    return ""


def load_skills(skills_dir: Path) -> list[dict]:
    """skills_dir/*/SKILL.md 전부 파싱."""
    items: list[dict] = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            logger.warning("read fail %s: %s", skill_md, e)
            continue
        fm = _parse_frontmatter(text)
        slug = skill_md.parent.name
        callout = _extract_callout(text)
        description = fm.get("description") or ""
        # callout 이 비어있으면 description 으로 폴백 (대부분의 ECC 스킬은 description 사용).
        content = callout or str(description)
        ai_tools = fm.get("ai_tools") or []
        if isinstance(ai_tools, str):
            ai_tools = [ai_tools]
        category = fm.get("category") or ""
        items.append({
            "slug": slug,
            "name": fm.get("name") or slug,
            "callout": content,
            "ai_tools": ai_tools,
            "category": category,
        })
    return items


def build_text(item: dict) -> str:
    parts = [item.get("callout") or ""]
    ai_tools = item.get("ai_tools") or []
    if ai_tools:
        parts.append(" ".join(str(x) for x in ai_tools))
    if item.get("category"):
        parts.append(str(item["category"]))
    return "\n".join(p.strip() for p in parts if p.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="일괄 임베딩 + 중복 후보 리포트")
    parser.add_argument("--threshold", type=float, default=0.75)
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[2] / "inbox" / "dedup_candidates.md"),
    )
    parser.add_argument("--skills-dir", default=str(GLOBAL_SKILLS_DIR))
    parser.add_argument("--sleep", type=float, default=0.3,
                        help="임베딩 API 호출 사이 sleep 초 (rate limit 회피)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    skills_dir = Path(os.path.expanduser(args.skills_dir))
    if not skills_dir.exists():
        print(f"❌ 스킬 디렉토리 없음: {skills_dir}", file=sys.stderr)
        return 1

    skills = load_skills(skills_dir)
    print(f"📂 {len(skills)}개 스킬 발견 (dir={skills_dir})")

    # 임베딩 — 캐시 활용.
    vecs: dict[str, list[float]] = {}
    embedded = 0
    cached_hit = 0
    for s in skills:
        text = build_text(s)
        if not text:
            continue
        before = embedder.all_cached().get(s["slug"], {}).get("vec")
        vec = embedder.get_or_embed(s["slug"], text)
        if vec is None:
            continue
        if before and before == vec:
            cached_hit += 1
        else:
            embedded += 1
            time.sleep(args.sleep)
        vecs[s["slug"]] = vec
    print(f"🔢 임베딩: 신규/갱신 {embedded}, 캐시 히트 {cached_hit}")

    # 페어 코사인 — N*(N-1)/2.
    pairs: list[tuple[str, str, float]] = []
    slugs = list(vecs.keys())
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            score = embedder.cosine(vecs[a], vecs[b])
            if score >= args.threshold:
                pairs.append((a, b, score))
    pairs.sort(key=lambda x: x[2], reverse=True)
    print(f"🔍 임계값 {args.threshold} 이상 페어: {len(pairs)}건")

    # 리포트.
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    by_slug = {s["slug"]: s for s in skills}
    lines = [
        f"# 스킬 중복 후보 리포트 (threshold ≥ {args.threshold})",
        "",
        f"- 대상: `{skills_dir}` ({len(skills)} 스킬)",
        f"- 후보 페어: {len(pairs)}건",
        "",
        "| 순위 | 유사도 | A | B | A 카테고리 | B 카테고리 |",
        "|------|--------|---|---|-----------|-----------|",
    ]
    for i, (a, b, score) in enumerate(pairs, start=1):
        cat_a = by_slug.get(a, {}).get("category", "")
        cat_b = by_slug.get(b, {}).get("category", "")
        lines.append(f"| {i} | {score:.3f} | {a} | {b} | {cat_a} | {cat_b} |")
    lines.extend([
        "",
        "## 합병 방법",
        "",
        "1. 위 표에서 합칠 페어 결정",
        "2. 채팅 사이드패널 열고 `리포트 N번 합병해줘` (N = 순위 번호)",
        "3. 또는 직접: `python -m scripts.collect --merge <slug_a> <slug_b>` (TBD)",
        "",
        f"생성: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    ])
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📝 리포트 저장: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
