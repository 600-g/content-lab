"""스킬 통합 (v5.3) — 이미 등록된 두 스킬을 하나로 합친다.

사용자 원칙 (2026-09-16): 같은 주제를 다른 출처로 또 받는 일이 잦으니, 정확히 유사하고 카테고리가
겹치면 합쳐서 간소화한다. 수집 시점에는 collect.py 의 의미 dedup 이 자동으로 하고, 이 도구는
이미 쌓인 중복(예: 같은 PDF 에서 나온 3건)을 사람이 지정해 합칠 때 쓴다.

    venv/bin/python -m scripts.library.consolidate <keeper> <absorbed> [<absorbed2> ...]
    venv/bin/python -m scripts.library.consolidate --dry-run <keeper> <absorbed>
    venv/bin/python -m scripts.library.consolidate --content 합성본.md <keeper> <a> <b> ...   # 묶음 전체를 새로 쓴 문서로 교체

- keeper 의 슬러그·경로가 유지되고 absorbed 의 본문·출처가 합병기(Claude → Gemini → Gemma)로 흡수된다
- absorbed 는 logs/backup_consolidate_<date>/ 에 백업한 뒤 mirror(skills/)·글로벌(~/.claude/skills) 에서 삭제
- 합병 LLM 이 실패하면 아무것도 지우지 않는다
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import logging
import re
import shutil
import sys
from pathlib import Path
from typing import Callable, Optional

from scripts.analyzer.gemini import AnalysisResult
from scripts.analyzer.merger import merge_with_existing, _parse_existing_skill_md
from scripts.skill_builder import render_skill_md
from scripts.skill_builder.installer import LOCAL_MIRROR_DIR, _global_skills_dir, normalize_url

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


def _fm_get(fm: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
    return m.group(1).strip() if m else ""


def result_from_skill(path: Path) -> AnalysisResult:
    """SKILL.md → AnalysisResult (합병기의 '신규' 입력으로 쓰기 위해). 제목·콜아웃·출처 섹션은 본문에서 뺀다."""
    path = Path(path)
    meta = _parse_existing_skill_md(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    m = _FM_RE.match(text)
    fm = m.group(1) if m else ""
    body = meta.get("body") or ""
    title = ""
    callout = ""
    kept: list[str] = []
    for ln in body.splitlines():
        s = ln.strip()
        if not title and s.startswith("# "):
            title = s[2:].replace(" (합병됨)", "").strip()
            continue
        if not callout and s.startswith("💡 "):
            callout = s[2:].strip()
            continue
        kept.append(ln)
    body_md = "\n".join(kept).strip()
    body_md = re.split(r"\n## 출처\s*\n", body_md, maxsplit=1)[0].strip()
    tools = re.findall(r'"([^"]+)"', _fm_get(fm, "ai_tools"))
    r = AnalysisResult(
        skill_name=meta.get("name") or path.parent.name, skill_title_ko=title or path.parent.name,
        category=meta.get("category") or "기타", grade=meta.get("grade") or "B", grade_reason="",
        targets=[], summary="", when_to_use="", memo="", ai_tools=tools, tags=[],
        difficulty=_fm_get(fm, "difficulty") or "중급", callout=callout or _fm_get(fm, "description"),
        body_md=body_md, body_content=body_md, raw={"body_md": body_md},
    )
    r.raw["_source_urls"] = list(meta.get("source_urls") or [])
    return r


def merge_pair(
    keeper: str,
    absorbed: str,
    *,
    mirror_dir: Path | str = LOCAL_MIRROR_DIR,
    global_dir: Path | str | None = None,
    backup_dir: Path | str | None = None,
    merge: Callable[..., AnalysisResult] = merge_with_existing,
) -> dict:
    mirror_dir = Path(mirror_dir)
    gdir = Path(global_dir) if global_dir is not None else _global_skills_dir()
    kp = mirror_dir / keeper / "SKILL.md"
    ap = mirror_dir / absorbed / "SKILL.md"
    if not kp.exists():
        return {"ok": False, "reason": f"keeper 없음: {keeper}"}
    if not ap.exists():
        return {"ok": False, "reason": f"absorbed 없음: {absorbed}"}
    if keeper == absorbed:
        return {"ok": False, "reason": "같은 슬러그"}

    new = result_from_skill(ap)
    srcs: list[str] = list(new.raw.get("_source_urls") or [])
    primary = srcs[0] if srcs else f"skill://{absorbed}"
    merged = merge(kp, new, primary, "web")
    if not (merged.raw or {}).get("_is_merged"):
        return {"ok": False, "reason": "합병 LLM 실패 — 아무것도 바꾸지 않음", "keeper": keeper, "absorbed": absorbed}

    # 출처 합집합 (absorbed 의 출처를 전부 보존)
    urls = list(merged.raw.get("_merged_source_urls") or [])
    seen = {normalize_url(u) for u in urls}
    for u in srcs:
        if normalize_url(u) not in seen:
            urls.append(u)
            seen.add(normalize_url(u))
    merged.raw["_merged_source_urls"] = urls
    merged.skill_name = keeper
    md = render_skill_md(merged, primary, "web")

    # 백업 (keeper 합병 전 상태 + absorbed) → 삭제 → 쓰기
    if backup_dir:
        b = Path(backup_dir)
        for slug in (absorbed, keeper):
            src = mirror_dir / slug
            if src.exists():
                shutil.copytree(src, b / slug, dirs_exist_ok=True)
            g = gdir / slug
            if g.exists():
                shutil.copytree(g, b / f"global__{slug}", dirs_exist_ok=True)
    kp.write_text(md, encoding="utf-8")
    gp = gdir / keeper / "SKILL.md"
    if gp.exists():  # 전역 사본이 있을 때만 갱신 — 없는 스킬을 전역에 새로 깔지 않는다 (installer 전역 설치 정책)
        gp.write_text(md, encoding="utf-8")
    shutil.rmtree(mirror_dir / absorbed, ignore_errors=True)
    shutil.rmtree(gdir / absorbed, ignore_errors=True)

    try:  # 임베딩: absorbed 는 무효화, keeper 는 새 본문으로
        from scripts.analyzer import embedder
        from scripts.analyzer.dedup_finder import _component_text
        from scripts import config_store
        embedder.invalidate([absorbed, keeper])
        comp = config_store.get("dedup.components", ["callout", "ai_tools", "category"])
        t = _component_text(merged, comp)
        if t:
            embedder.get_or_embed(keeper, t)
    except Exception as e:  # noqa: BLE001
        logger.warning("임베딩 갱신 실패 (합병 자체는 완료): %s", e)

    logger.info("통합 완료: %s ← %s (provider=%s, %d자, 출처 %d)", keeper, absorbed,
                getattr(merged, "provider", ""), len(merged.body_md or ""), len(urls))
    return {"ok": True, "keeper": keeper, "absorbed": absorbed, "provider": getattr(merged, "provider", ""),
            "body_chars": len(merged.body_md or ""), "sources": len(urls)}


_ALLOWED_H2 = ("이게 뭔가요?", "따라하기", "활용 예시", "💡 아이디어", "주의사항", "출처")


def check_synthesized(md: str, keeper: str, required_sources: list[str]) -> list[str]:
    """합성 문서 검사 — 문제 목록(빈 리스트면 통과). 출처 누락·슬러그 불일치·합병 흔적·금지 대제목을 막는다."""
    problems: list[str] = []
    m = _FM_RE.match(md)
    if not m:
        return ["frontmatter 없음"]
    fm, body = m.group(1), m.group(2)
    if _fm_get(fm, "name") != keeper:
        problems.append(f"name 이 keeper({keeper}) 가 아님: {_fm_get(fm, 'name')!r}")
    for key in ("description", "grade", "category"):
        if not _fm_get(fm, key):
            problems.append(f"frontmatter {key} 비어 있음")
    have = {normalize_url(u) for u in re.findall(r"^\s+-\s+(\S+)\s*$", fm, re.M)}
    missing = [u for u in required_sources if normalize_url(u) not in have]
    if missing:
        problems.append(f"출처 누락 {len(missing)}건: {missing[:3]}")
    prose = re.sub(r"```.*?```", "", body, flags=re.S)  # 코드블록 안의 '## ' 는 프롬프트 원문이다
    if "합병됨" in prose or "🔀" in prose:
        problems.append("합병 표시가 남아 있음")
    bad = [h for h in re.findall(r"^## (.+?)\s*$", prose, re.M) if h not in _ALLOWED_H2]
    if bad:
        problems.append(f"허용 밖 대제목: {bad[:3]}")
    if not re.search(r"^# \S", prose, re.M):
        problems.append("제목(# ) 없음")
    return problems


def apply_synthesized(
    keeper: str,
    absorbed: list[str],
    content: str,
    *,
    mirror_dir: Path | str = LOCAL_MIRROR_DIR,
    global_dir: Path | str | None = None,
    backup_dir: Path | str | None = None,
) -> dict:
    """미리 합성해 둔 문서(사람·Claude 가 묶음 전체를 읽고 새로 쓴 것)로 keeper 를 교체하고 absorbed 를 흡수한다.

    merge_pair 는 LLM 이 둘씩 합치지만, 여러 문서를 하나로 재설계할 때는 묶음 전체를 한 번에 본 합성본이 낫다
    (2026-10-05 사용자 지시: 이어붙이지 말고 하나의 문서로 고도화). 검사에 걸리면 아무것도 바꾸지 않는다.
    전역(~/.claude/skills) 은 keeper 나 absorbed 중 하나라도 전역에 있었으면 keeper 를 전역에 둔다.
    """
    mirror_dir = Path(mirror_dir)
    gdir = Path(global_dir) if global_dir is not None else _global_skills_dir()
    members = [keeper, *absorbed]
    if len(set(members)) != len(members):
        return {"ok": False, "reason": "슬러그 중복"}
    for slug in members:
        if not (mirror_dir / slug / "SKILL.md").exists():
            return {"ok": False, "reason": f"없음: {slug}"}
    required: list[str] = []
    for slug in members:
        required += list(_parse_existing_skill_md(mirror_dir / slug / "SKILL.md").get("source_urls") or [])
    problems = check_synthesized(content, keeper, required)
    if problems:
        return {"ok": False, "reason": "; ".join(problems), "keeper": keeper}

    any_global = any((gdir / slug / "SKILL.md").exists() for slug in members)
    if backup_dir:
        b = Path(backup_dir)
        for slug in members:
            shutil.copytree(mirror_dir / slug, b / slug, dirs_exist_ok=True)
            if (gdir / slug).exists():
                shutil.copytree(gdir / slug, b / f"global__{slug}", dirs_exist_ok=True)
    (mirror_dir / keeper / "SKILL.md").write_text(content, encoding="utf-8")
    if any_global:
        (gdir / keeper).mkdir(parents=True, exist_ok=True)
        (gdir / keeper / "SKILL.md").write_text(content, encoding="utf-8")
    for slug in absorbed:
        shutil.rmtree(mirror_dir / slug, ignore_errors=True)
        shutil.rmtree(gdir / slug, ignore_errors=True)

    try:  # 임베딩: absorbed 는 무효화, keeper 는 새 본문으로
        from scripts.analyzer import embedder
        from scripts.analyzer.dedup_finder import _component_text
        from scripts import config_store
        embedder.invalidate(members)
        comp = config_store.get("dedup.components", ["callout", "ai_tools", "category"])
        t = _component_text(result_from_skill(mirror_dir / keeper / "SKILL.md"), comp)
        if t:
            embedder.get_or_embed(keeper, t)
    except Exception as e:  # noqa: BLE001
        logger.warning("임베딩 갱신 실패 (통합 자체는 완료): %s", e)

    logger.info("합성본 적용: %s ← %s (%d자, 출처 %d, 전역=%s)", keeper, ",".join(absorbed), len(content), len(required), any_global)
    return {"ok": True, "keeper": keeper, "absorbed": absorbed, "chars": len(content), "global": any_global}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="등록된 스킬 통합 — keeper 에 absorbed 를 흡수")
    ap.add_argument("keeper")
    ap.add_argument("absorbed", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--content", help="미리 합성한 SKILL.md 경로 — LLM 합병 대신 이 문서로 keeper 를 교체하고 absorbed 를 모두 흡수")
    ap.add_argument("--backup-dir", default=str(PROJECT_ROOT / "logs" / f"backup_consolidate_{_dt.date.today():%Y%m%d}"))
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    if args.content:
        text = Path(args.content).read_text(encoding="utf-8")
        if args.dry_run:
            req: list[str] = []
            for slug in [args.keeper, *args.absorbed]:
                p = LOCAL_MIRROR_DIR / slug / "SKILL.md"
                req += list(_parse_existing_skill_md(p).get("source_urls") or []) if p.exists() else [f"(없음: {slug})"]
            probs = check_synthesized(text, args.keeper, req)
            print(f"[dry-run] {args.keeper} ← {args.absorbed}: " + ("통과" if not probs else "; ".join(probs)))
            return 1 if probs else 0
        out = apply_synthesized(args.keeper, list(args.absorbed), text, backup_dir=args.backup_dir)
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    rc = 0
    for a in args.absorbed:
        if args.dry_run:
            kp, apth = LOCAL_MIRROR_DIR / args.keeper / "SKILL.md", LOCAL_MIRROR_DIR / a / "SKILL.md"
            print(f"[dry-run] {args.keeper} ← {a}: keeper={kp.exists()} absorbed={apth.exists()}")
            continue
        out = merge_pair(args.keeper, a, backup_dir=args.backup_dir)
        print(json.dumps(out, ensure_ascii=False))
        if not out.get("ok"):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
