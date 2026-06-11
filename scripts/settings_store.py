"""설정 저장소 — .env 안전 읽기/쓰기.

aiskillbox 설정 창(PIN 보호)이 API 키를 편집할 때 쓴다.
주석·빈 줄·키 순서를 보존하고, 기존 키는 제자리 갱신, 새 키는 끝에 추가.
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# 설정 창에서 편집 가능한 키 — 순서대로 UI 렌더
# kind: "secret"(마스킹), "id"(부분 노출), "text"(그대로)
SETTINGS_SCHEMA: list[dict] = [
    {"key": "GEMINI_API_KEY", "label": "Gemini API 키", "kind": "secret",
     "hint": "aistudio.google.com/apikey — 무료 발급"},
    {"key": "NOTION_API_KEY", "label": "Notion API 키", "kind": "secret",
     "hint": "notion.so/my-integrations — DB 페이지에 Connection 추가 필수"},
    {"key": "NOTION_DB_ID", "label": "Notion 스킬 DB ID", "kind": "id",
     "hint": "🧠 AI 스킬 마스터 DB"},
    {"key": "NOTION_HUB_PAGE_ID", "label": "Notion 허브 페이지 ID", "kind": "id",
     "hint": "📒 AI 스킬 수집소"},
    {"key": "GEMMA_MODEL", "label": "Gemma 폴백 모델", "kind": "text",
     "hint": "예: gemma4:26b · gemma4:e4b"},
    {"key": "GEMMA_TIMEOUT", "label": "Gemma 타임아웃(초)", "kind": "text",
     "hint": "로컬 LLM 콜드스타트 대비 — 기본 120"},
    {"key": "ADMIN_PIN", "label": "설정 창 PIN", "kind": "secret",
     "hint": "이 창에 들어올 때 쓰는 비밀번호"},
]
_EDITABLE_KEYS = {s["key"] for s in SETTINGS_SCHEMA}
_KIND = {s["key"]: s["kind"] for s in SETTINGS_SCHEMA}


def read_env() -> dict[str, str]:
    """현재 .env 파싱 (KEY=VALUE 만)."""
    out: dict[str, str] = {}
    if not ENV_FILE.exists():
        return out
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def mask(value: str, kind: str) -> str:
    """UI 표시용 마스킹 — 원본 값은 절대 그대로 반환하지 않는다."""
    if not value:
        return ""
    if kind == "secret":
        if len(value) <= 4:
            return "•" * len(value)
        return value[:3] + "•" * 6 + value[-2:]
    if kind == "id":
        return value[:8] + "…" if len(value) > 10 else value
    return value  # text 는 그대로 (모델명/숫자 — 비밀 아님)


def settings_view() -> list[dict]:
    """설정 창에 줄 메타 + 마스킹 값 (PIN 검증 통과 후 호출)."""
    env = read_env()
    rows: list[dict] = []
    for s in SETTINGS_SCHEMA:
        raw = env.get(s["key"], "")
        rows.append({
            "key": s["key"],
            "label": s["label"],
            "kind": s["kind"],
            "hint": s["hint"],
            "is_set": bool(raw),
            "preview": mask(raw, s["kind"]),
        })
    return rows


def update_env(updates: dict[str, str]) -> list[str]:
    """편집 허용 키만 .env 에 반영. 기존 키 제자리 갱신, 신규 키 끝에 추가.

    빈 문자열 값은 '변경 안 함'으로 간주(마스킹된 칸을 안 건드린 경우).
    적용된 키 목록을 반환.
    """
    clean: dict[str, str] = {}
    for k, v in (updates or {}).items():
        if k not in _EDITABLE_KEYS:
            continue
        v = (v or "").strip()
        if v == "":
            continue  # 빈 칸은 건드리지 않음
        if "\n" in v or "\r" in v:
            continue  # 안전: 개행 주입 차단
        clean[k] = v
    if not clean:
        return []

    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    seen: set[str] = set()
    new_lines: list[str] = []
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.partition("=")[0].strip()
            if k in clean:
                new_lines.append(f"{k}={clean[k]}")
                seen.add(k)
                continue
        new_lines.append(line)

    extra = [k for k in clean if k not in seen]
    if extra:
        new_lines.append("")
        new_lines.append("# 설정 창에서 추가됨")
        new_lines.extend(f"{k}={clean[k]}" for k in extra)

    # 원자적 쓰기 — 같은 디렉터리 임시파일에 쓴 뒤 os.replace.
    # write_text 직접 호출은 truncate→write 사이 크래시 시 .env 가 통째로 날아간다.
    tmp = ENV_FILE.with_name(".env.tmp")
    tmp.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, ENV_FILE)
    return sorted(clean.keys())
