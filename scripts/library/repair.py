"""라이브러리 파일 수선 (v5.3.1) — 렌더 결함으로 남은 흔적을 기존 SKILL.md 에서 정리한다.

    venv/bin/python -m scripts.library.repair sources            # '## 출처' 이중 섹션 → 마지막(렌더러) 것만 (dry-run)
    venv/bin/python -m scripts.library.repair sources --apply    # mirror + 글로벌(origin: content-lab) 둘 다 패치
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.skill_builder.installer import LOCAL_MIRROR_DIR, _global_skills_dir

_HEAD_RE = re.compile(r"(?m)^##\s*출처\s*$")


def dedupe_source_sections(text: str) -> str:
    """`## 출처` 가 둘 이상이면 첫 번째 앞 본문 + 마지막 섹션만 남긴다. 하나 이하면 그대로 (멱등)."""
    heads = list(_HEAD_RE.finditer(text or ""))
    if len(heads) < 2:
        return text or ""
    before = text[:heads[0].start()].rstrip()
    last = text[heads[-1].start():]
    return before + "\n\n" + last


def repair_sources(*, apply: bool, mirror_dir: Path = LOCAL_MIRROR_DIR, global_dir: Path | None = None) -> list[str]:
    gdir = Path(global_dir) if global_dir is not None else _global_skills_dir()
    fixed: list[str] = []
    for p in sorted(Path(mirror_dir).glob("*/SKILL.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        new = dedupe_source_sections(text)
        if new == text:
            continue
        fixed.append(p.parent.name)
        if apply:
            p.write_text(new, encoding="utf-8")
            g = gdir / p.parent.name / "SKILL.md"
            if g.exists():
                gt = g.read_text(encoding="utf-8", errors="replace")
                if "origin: content-lab" in gt[:800]:
                    g.write_text(dedupe_source_sections(gt), encoding="utf-8")
    return fixed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="스킬 파일 수선")
    ap.add_argument("what", choices=["sources"])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    fixed = repair_sources(apply=args.apply)
    print(f"{'수정' if args.apply else '대상'} {len(fixed)}건: {', '.join(fixed[:12])}{' …' if len(fixed) > 12 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
