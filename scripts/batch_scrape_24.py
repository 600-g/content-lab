"""24건 URL → router.scrape() raw 텍스트 일괄 추출 → aiskillbox_briefs/raw/ 저장.

각 페이지 timeout 120초. stuck 시 다음으로. 결과 _scrape_results.json 에 요약.
"""
from __future__ import annotations

import json
import re
import signal
import time
from pathlib import Path
from contextlib import contextmanager

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from scripts.scraper.router import scrape


@contextmanager
def time_limit(seconds: int):
    """SIGALRM 기반 timeout (macOS/Linux). Playwright 가 시그널 무시할 수도 있음 — 보조 보호."""
    def _handler(signum, frame):
        raise TimeoutError(f"{seconds}s timeout")
    old = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def slugify(s: str) -> str:
    s = re.sub(r"[^\w가-힣\-_]", "_", s)[:60]
    return s.strip("_") or "item"


def main():
    base = Path(__file__).resolve().parent.parent
    todo = json.loads((base / "aiskillbox_briefs" / "_todo_25.json").read_text())
    # 1번(이미 완료) 제외 → 24건
    targets = todo[1:]

    out_dir = base / "aiskillbox_briefs" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, t in enumerate(targets, 2):  # 인덱스 2부터 (todo 의 0-base → user-facing 2)
        url = t["url"]
        title = t["title"]
        slug = slugify(title.split()[0])
        out = out_dir / f"{i:02d}_{slug}.md"

        start = time.time()
        info = {"i": i, "title": title, "url": url, "slug": slug, "file": str(out.relative_to(base))}
        try:
            with time_limit(120):
                r = scrape(url)
            elapsed = int(time.time() - start)
            text = (r.text or "").strip()
            content = (
                f"# {r.title or title}\n\n"
                f"- URL: {url}\n"
                f"- source_type: {r.source_type}\n"
                f"- length: {len(text)} chars\n"
                f"- scraped_at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"- elapsed: {elapsed}s\n"
                f"- ok: {r.ok}\n"
                f"- error: {r.error or ''}\n\n"
                f"---\n\n{text}\n"
            )
            out.write_text(content, encoding="utf-8")
            info.update({"ok": bool(text), "length": len(text), "source_type": r.source_type,
                         "scrape_error": r.error, "elapsed": elapsed})
            mark = "✓" if text else "⚠️"
            print(f"  {i:>2}. {mark} {len(text):>6}자 {elapsed:>3}s  {title[:42]}")
        except TimeoutError:
            elapsed = int(time.time() - start)
            info.update({"ok": False, "length": 0, "elapsed": elapsed, "error": f"timeout {elapsed}s"})
            print(f"  {i:>2}. ⏱️ timeout {elapsed}s        {title[:42]}")
        except Exception as e:  # noqa: BLE001
            elapsed = int(time.time() - start)
            info.update({"ok": False, "length": 0, "elapsed": elapsed, "error": str(e)[:200]})
            print(f"  {i:>2}. ❌ {str(e)[:50]}  {title[:42]}")
        results.append(info)

    (out_dir.parent / "_scrape_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    ok_n = sum(1 for r in results if r.get("ok"))
    print(f"\n총 {len(results)}건 / 성공 {ok_n} / 실패 {len(results) - ok_n}")


if __name__ == "__main__":
    main()
