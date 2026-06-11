"""원본 백업 vs 현재 노션 페이지 — 데이터 손실 점검.

체크 항목:
- 코드블록 개수 (```...```)
- 백틱 인라인 코드 (`...`)
- 단축키 패턴 (Cmd+X, Ctrl+X)
- 명령어 (npm/git/cd/$ ...)
- URL/링크
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ["NOTION_DB_ID"]
BACKUP_DIR = Path(__file__).resolve().parents[1] / "logs" / "backup_v27_2026-05-15"


def block_text(b: dict) -> str:
    """rich_text 를 텍스트로. annotations.code=True 면 backtick 으로 감싸기 (audit 정확도)."""
    t = b.get("type", "?")
    rt = b.get(t, {}).get("rich_text", [])
    parts = []
    for r in rt:
        text = r.get("plain_text", "")
        ann = r.get("annotations", {})
        if ann.get("code"):
            text = f"`{text}`"
        parts.append(text)
    return "".join(parts)


def fetch_current_text(pid: str) -> str:
    parts = []
    cursor = None
    while True:
        path = f"{API}/blocks/{pid}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        d = requests.get(path, headers=H, timeout=30).json()
        for b in d.get("results", []):
            t = b.get("type", "?")
            text = block_text(b)
            if t == "code":
                lang = b.get("code", {}).get("language", "")
                parts.append(f"```{lang}\n{text}\n```")
            else:
                parts.append(text)
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return "\n".join(parts)


PATTERNS = {
    "code_blocks": re.compile(r"```[\s\S]*?```"),
    "inline_code": re.compile(r"`[^`\n]{2,}`"),
    "shortcuts": re.compile(r"\b(Cmd|Ctrl|Alt|Shift|Option|⌘|⌃|⌥|⇧)\s*[\+\-]\s*[A-Za-z0-9]+", re.I),
    "commands": re.compile(r"(?:^|\s)\$\s+\S+|(?:^|\s)(npm|git|cd|brew|pip|python|node|curl|docker|gh|cargo)\s+\S+", re.M),
    "urls": re.compile(r"https?://\S+"),
}


def count_patterns(text: str) -> dict[str, int]:
    return {k: len(p.findall(text)) for k, p in PATTERNS.items()}


def main() -> int:
    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={"page_size": 50}).json()
    pages = r.get("results", [])
    print(f"📡 {len(pages)}건 점검\n")
    print(f"{'페이지':<46} | 코드블록 | 인라인 | 단축키 | 명령어 | URL")
    print("─" * 100)

    losses = []
    for p in pages:
        pid = p["id"]
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        backup_file = next(BACKUP_DIR.glob(f"{pid.replace('-','')}__*.md"), None)
        if not backup_file:
            print(f"{title[:45]:<46} | 백업 없음")
            continue
        orig = backup_file.read_text(encoding="utf-8")
        curr = fetch_current_text(pid)
        o = count_patterns(orig)
        c = count_patterns(curr)
        diff = {k: c[k] - o[k] for k in o}
        warn = ""
        if c["code_blocks"] < o["code_blocks"] or c["inline_code"] < o["inline_code"] - 2 \
           or c["shortcuts"] < o["shortcuts"] or c["commands"] < o["commands"] - 1:
            warn = " ⚠️ 손실"
            losses.append((title, o, c))
        print(f"{title[:45]:<46} | {o['code_blocks']:>3}/{c['code_blocks']:<3} | {o['inline_code']:>3}/{c['inline_code']:<3} | {o['shortcuts']:>3}/{c['shortcuts']:<3} | {o['commands']:>3}/{c['commands']:<3} | {o['urls']:>3}/{c['urls']:<3}{warn}")

    print(f"\n원본/현재 — 손실 의심 페이지: {len(losses)}건")
    for title, o, c in losses:
        print(f"\n⚠️ {title}")
        for k in ("code_blocks", "inline_code", "shortcuts", "commands"):
            if c[k] < o[k]:
                print(f"   {k}: {o[k]} → {c[k]} ({o[k] - c[k]}건 손실)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
