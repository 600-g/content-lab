"""스킬 라이브러리 (도서관) — SKILL.md 원본 기반 검색/카탈로그/MCP.

- index.py      : skills/*/SKILL.md 스캔 → frozen 레코드 인덱스 (mtime 변경 감지)
- search.py     : 키워드(BM25) + 의미(코사인) + RRF 하이브리드 검색
- catalog.py    : 사람용 단일 HTML 카탈로그 생성 (킷 템플릿 이식)
- routes.py     : Flask /api/library/* + /catalog
- mcp_server.py : stdio MCP 서버 (표준 라이브러리만 — 외부 도구/기기용)

설계: docs/superpowers/specs/2026-08-20-skill-library-design.md
"""
