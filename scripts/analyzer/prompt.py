"""Gemini 분석 프롬프트.

SKILL_AGENT.md 의 원본 v3 + 콘텐츠랩 v3.0 의 분석 매트릭스를 통합.
JSON 응답 → AnalysisResult 로 파싱.
"""

# TEMPLATE v2 (2026-05-15) — 카테고리 7개 + 태그 15개 기술/방법 키워드로 재정의

CATEGORIES = [
    "프롬프트", "자동화", "콘텐츠", "디자인", "개발", "업무", "기타",
]

GRADES = ["S", "A", "B", "C"]

TARGETS = [
    "두근펫", "매매봇", "검은별", "클로드코드", "AI900", "첼시인스타", "이모티콘", "공통",
]

# Notion DB AI 도구 옵션 (변경 없음)
AI_TOOLS = [
    "Claude", "GPT", "Gemini", "Midjourney", "Leonardo AI", "CapCut", "Canva",
    "Cursor", "Codex", "ComfyUI", "Stable Diffusion", "Ollama", "Claude Code", "도구무관",
]

# v2 태그 — 기술/방법 키워드 (카테고리와 안 겹침)
TAGS = [
    "MCP", "API", "RAG", "Function Calling", "Vision", "Multimodal",
    "프롬프트체이닝", "CoT", "Tool Use", "Webhook", "Streaming",
    "CLI", "GitHub Actions", "자체호스팅", "오픈소스",
]
DIFFICULTIES = ["초급", "중급", "고급"]

ANALYSIS_PROMPT_TEMPLATE = """너는 두근컴퍼니의 AI 스킬 분석기다.

아래 [원본]에서 재사용 가능한 **AI 스킬**을 추출해서 JSON으로만 응답해.
광고/홍보/잡담은 제거. 핵심 스킬만 추출. 여러 개면 가장 가치 있는 1개를 고른다.

[원본 정보]
- URL: {url}
- 출처유형: {source_type}
- 제목: {title}

[원본 텍스트]
{text}

[등급 기준]
- S: 지금 바로 두근컴퍼니에서 쓸 수 있다. 무료 도구로 실행 가능.
- A: 가까운 미래에 활용 가능. 약간의 준비 필요.
- B: 직접 관련 없지만 미래에 쓸 수 있음.
- C: 품질 낮거나 활용 불가. body_content 비워서 반환 (DB 등록 안 함).

[두근컴퍼니 환경 — 적용 판단 시 참고]
- 메인 제품: company-hq (AI 에이전트 사무실 시각화 플랫폼)
- 유료 보유: Claude Max
- 무료 활용: Gemini API, Gemma 4 26B 로컬(Ollama), Bing Image Creator, Leonardo, CapCut, Canva
- 장비: Mac Mini M4 (Apple Silicon, 24GB)
- 코딩: 사용자는 초보 (Python 기초)
- 강점: CX 운영 11년, 기획력, AI 빠른 습득

[두근이 안 쓰는 외부 도구 → 두근 환경 대체 매핑 (외부 도구 등장 시 반드시 doogeun 섹션에 대체안 명시)]
- Cursor → Claude Code (CLI) + VSCode + Continue 확장
- GitHub Copilot → Claude Code 또는 Codex CLI
- ChatGPT Plus → Gemini 무료 (대용량) + Claude Max (코딩) 조합
- Midjourney → Bing Image Creator (DALL-E 3) / Leonardo AI 무료
- Replit / Vercel → Mac Mini M4 자체 호스팅 + Cloudflare Tunnel
- Notion AI → Notion MCP + Claude Code 조합
- Runway / Pika → Pixelle (오픈소스) + Gemini 이미지 + Mac Mini
- Zapier / Make → Claude Code + GitHub Actions
- Perplexity → Gemini + Claude (web search MCP)
- v0.dev → Claude Artifacts (Claude Max 포함)
- ElevenLabs → 로컬 TTS (ko-KR-SunHiNeural) + CapCut 무료
- DeepL → Gemini / Claude 번역
- Linear / Jira → Notion DB + Cursor 룰
- Figma AI → Claude Design (Claude Max 포함)

[적용대상 판단 기준]
- 클로드코드: CLAUDE.md, 프롬프트, MCP, CLI, 스킬
- 두근컴퍼니: 멀티 에이전트, 오피스 씬, Phaser
- 두근펫: Electron 데스크톱 앱
- 매매봇: 코인봇 v10.1 / 주식봇, 트레이딩, API
- 검은별: 게임 기획, RPG
- AI900: Azure AI, 자격증
- 첼시인스타: 인스타 콘텐츠, 릴스
- 이모티콘: 캐릭터 디자인
- 공통: 범용 스킬

[허용된 옵션만 사용 — 다른 값 쓰면 자동 제거. TEMPLATE v2]
- category 7종 ("작업 영역", 1개 선택): 프롬프트 / 자동화 / 콘텐츠 / 디자인 / 개발 / 업무 / 기타
- targets 8종: 두근펫 / 매매봇 / 검은별 / 클로드코드 / AI900 / 첼시인스타 / 이모티콘 / 공통
- ai_tools 14종 (없으면 빈 배열): Claude / GPT / Gemini / Midjourney / Leonardo AI / CapCut / Canva / Cursor / Codex / ComfyUI / Stable Diffusion / Ollama / Claude Code / 도구무관
- tags 15종 ("기술/방법" 키워드, 카테고리와 안 겹침): MCP / API / RAG / Function Calling / Vision / Multimodal / 프롬프트체이닝 / CoT / Tool Use / Webhook / Streaming / CLI / GitHub Actions / 자체호스팅 / 오픈소스
- difficulty: 초급 / 중급 / 고급

[카테고리 vs 태그 구분 규칙]
- "어떤 작업/영역인가?" → category (1개만)
- "어떤 기술/방법을 쓰는가?" → tags (해당하는 것만, 없으면 빈 배열)

[응답 형식 — JSON만, 마크다운 코드블록 없이. TEMPLATE v2.2 사람 가독성 우선]
{{
  "skill_name": "kebab-case 영문 슬러그 (예: youtube-hook-pattern)",
  "skill_title_ko": "한국어 짧은 제목, 이모지 없음 (예: 유튜브 훅 3초 패턴)",
  "category": "위 7종 중 택1 (정확히 일치)",
  "grade": "S/A/B/C 중 택1",
  "grade_reason": "등급 판정 사유 1줄",
  "targets": ["위 8종 중 1-3개"],
  "summary": "2-3줄 핵심요약",
  "tldr": "한 줄 요약 (2문장 이내, 무엇을/언제 쓰는지). 페이지 첫 callout에 표시되니 가장 임팩트 있게",
  "when_to_use": "언제 쓰나 — bullet 2-3개. '- ~할 때' 형식. 정보 없으면 빈 문자열",
  "how_it_works": "원리 — 작동 메커니즘 짧은 문단 1-2개. 핵심 명령어/공식은 ```코드블록```. 정보 없으면 빈 문자열",
  "steps": "단계 — 1) 2) 3) 번호 (또는 표). 두근(초보)도 따라할 수 있게. 정보 없으면 빈 문자열",
  "examples": "예시 — 실제 입력→출력. 표/코드 권장. 정보 없으면 빈 문자열",
  "doogeun": "두근컴퍼니 적용 — (필수 1) 원본이 두근 안 쓰는 외부 도구 사용 시 위 대체 매핑으로 변환 명시 (예: 'Cursor 대신 → Claude Code + Continue') (필수 2) 두근펫/매매봇/검은별/콘텐츠 등 프로젝트별 매핑. bullet",
  "caveats": "주의 — 한도/유료/실패 케이스. bullet. 정보 없으면 빈 문자열",
  "memo": "위 doogeun을 한 줄로 요약 (백업용)",
  "ai_tools": ["위 14종 중 해당하는 것만 (없으면 [])"],
  "tags": ["위 15종 중 해당하는 것만 5개 이내 (없으면 [])"],
  "difficulty": "초급/중급/고급 중 택1"
}}

[가독성 규칙 v2.2]
- 정보 없는 섹션은 빈 문자열 "" 로 두면 자동 생략됨 (사람 가독성 위함)
- "(해당 없음)" 같은 placeholder 문구 쓰지 말 것
- 헤더는 한국어만 (영문 추가 금지). 시스템이 자동 처리.

응답은 반드시 위 JSON 구조만 따른다. 다른 텍스트 절대 포함 금지.
"""


def build_prompt(scrape_dict: dict) -> str:
    """ScrapeResult.to_dict() → 분석 프롬프트."""
    return ANALYSIS_PROMPT_TEMPLATE.format(
        url=scrape_dict["url"],
        source_type=scrape_dict["source_type"],
        title=scrape_dict.get("title", "") or "(제목 없음)",
        text=(scrape_dict.get("text") or "")[:150000],
    )
