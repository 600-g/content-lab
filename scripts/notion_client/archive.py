"""원본 아카이브 — URL → 스크랩(글화) → 통일 양식 → 신규 DB 등록.

aiskillbox 25건 재처리 시 메인 DB 본문 교체와 동시에 원본 raw 콘텐츠를 별도 DB 에 보관.
- 영상(YouTube/Instagram Reel): yt-dlp 자막 추출 (scraper/social.py 가 처리)
- PDF/이미지: 가능한 추출 (현재는 텍스트만 보장, OCR 은 추후)
- 일반 웹: trafilatura/BeautifulSoup
"""
from __future__ import annotations

import os
import time
import datetime
import requests

from .register import _markdown_to_blocks, _headers, NOTION_API
from ..scraper.router import scrape as scrape_url


def _src_type(url: str) -> str:
    """노션 select 옵션과 매칭되는 출처 유형."""
    u = url.lower()
    if "github.com" in u:
        return "github"
    if "youtu.be" in u or "youtube.com" in u:
        return "youtube"
    if "instagram.com" in u:
        return "instagram"
    if "notion.site" in u or "notion.so" in u:
        return "notion"
    if "drive.google" in u:
        return "drive"
    if u.endswith(".pdf") or "/pdf/" in u:
        return "pdf"
    if any(u.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return "image"
    return "web"


def _kind_label(url: str, src_type: str) -> str:
    """글화 방식 라벨 — 노션 select 옵션과 매칭."""
    u = url.lower()
    if "/reel/" in u or "/shorts/" in u or "youtu.be" in u or "youtube.com" in u:
        return "자막 추출"
    if src_type == "instagram" and "/p/" in u:
        return "자막 추출"  # 인스타 포스트도 yt-dlp 가 영상 자막 시도
    if src_type in ("pdf", "drive"):
        return "PDF 텍스트 추출"
    if src_type == "image":
        return "OCR/이미지 캡션"
    return "웹 파싱"


def archive_source(url: str, linked_skill_slug: str = "", title_hint: str = "") -> dict:
    """원본 스크랩 + 글화 → 새 DB 페이지 생성.

    반환: {ok, page_id, char_count, kind, src_type, error?}
    """
    db_id = os.getenv("NOTION_ARCHIVE_DB_ID", "")
    if not db_id:
        return {"ok": False, "error": "NOTION_ARCHIVE_DB_ID 미설정 (.env 확인)"}

    src_type = _src_type(url)
    kind = _kind_label(url, src_type)

    # 스크랩 — router.scrape 가 자동으로 source 별 스크래퍼 선택
    try:
        result = scrape_url(url)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"스크랩 실패: {e}", "src_type": src_type}

    raw = (result.text or "").strip()
    if not raw:
        return {"ok": False, "error": "스크랩 결과 빈 텍스트",
                "src_type": src_type, "scrape_error": result.error}

    title = (result.title or title_hint or url[:80]).strip()
    today = datetime.date.today().isoformat()

    # 통일 양식 본문
    char_count = len(raw)
    # 노션 텍스트 안전 한도 — 페이지당 ~90KB
    body_text = raw[:90000]
    truncated = " (...일부 절단)" if len(raw) > 90000 else ""

    body_md = f"""## 메타

- **원본 제목**: {title}
- **출처 URL**: [{url}]({url})
- **출처 유형**: `{src_type}`
- **수집일**: {today}
- **글자수**: {char_count:,}자{truncated}
- **글화 방식**: {kind}
- **연결 스킬**: {linked_skill_slug or "(미연결)"}

## 원본 콘텐츠

{body_text}
"""

    blocks = _markdown_to_blocks(body_md)

    page_body = {
        "parent": {"database_id": db_id},
        "icon": {"type": "emoji", "emoji": "📦"},
        "properties": {
            "원본 제목": {"title": [{"text": {"content": title[:200]}}]},
            "출처 URL": {"url": url},
            "출처 유형": {"select": {"name": src_type}},
            "수집일": {"date": {"start": today}},
            "글자수": {"number": char_count},
            "글화 방식": {"select": {"name": kind}},
            "연결 스킬": {"rich_text": [{"text": {"content": linked_skill_slug}}]},
        },
        "children": blocks[:100],
    }

    r = requests.post(f"{NOTION_API}/pages", headers=_headers(), json=page_body, timeout=30)
    if r.status_code not in (200, 201):
        return {"ok": False, "error": f"노션 등록 실패 {r.status_code}: {r.text[:200]}",
                "src_type": src_type, "kind": kind}

    page_id = r.json()["id"]

    # 100블록 초과 시 추가 append
    if len(blocks) > 100:
        for i in range(100, len(blocks), 90):
            chunk = blocks[i:i + 90]
            try:
                requests.patch(f"{NOTION_API}/blocks/{page_id}/children",
                               headers=_headers(), json={"children": chunk}, timeout=20)
                time.sleep(0.3)
            except Exception:  # noqa: BLE001
                pass

    return {
        "ok": True,
        "page_id": page_id,
        "title": title,
        "char_count": char_count,
        "blocks": len(blocks),
        "kind": kind,
        "src_type": src_type,
    }


if __name__ == "__main__":
    import sys, json
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
    if len(sys.argv) < 2:
        print("사용: python -m scripts.notion_client.archive <url> [linked_skill_slug] [title_hint]")
        sys.exit(1)
    url = sys.argv[1]
    slug = sys.argv[2] if len(sys.argv) > 2 else ""
    hint = sys.argv[3] if len(sys.argv) > 3 else ""
    print(json.dumps(archive_source(url, slug, hint), ensure_ascii=False, indent=2))
