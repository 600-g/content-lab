# Notion 마이그레이션 자산 (2026-05~08, 기본 off)

CLAUDE.md 에서 분리(2026-09-25). `config.json notion.register_on_collect` 가 기본 false 라 평소엔 안 쓴다. 켤 때만 참조.

## 명령어

```bash
# Notion 인티그레이션 권한 확인
source .env && curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer ${NOTION_API_KEY}" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" -d '{"page_size":10}' \
  | python3 -c "import json,sys;print(len(json.load(sys.stdin).get('results',[])),'건 접근 가능')"

# DB 전수 큐레이션 batch
python -m scripts.curate_db analyze              # 변경 X, 분석만
python -m scripts.curate_db fix-emoji            # 제목 첫 이모지 → 아이콘 이동
python -m scripts.curate_db fix-meta             # Gemini로 카테고리/등급 재평가
python -m scripts.curate_db polish-body --limit 1 --dry  # 본문 1건 미리보기
python -m scripts.curate_db all                  # 전체 순차

# v2.3 보편 정보 템플릿 전환 워크플로 (DB 정리 — 항상 백업부터)
python -m scripts.backup_all                                    # 1) 백업 (logs/backup_v27_{date}/)
python -m scripts.audit_loss                                    # 2) 손실 점검 (백업 vs 현재 노션)
python -m scripts.audit_pages                                   # 3) 가독성/일관성 종합 점검
python -m scripts.rebuild_template --engine gemma               #    dry-run (LLM 재작성 미리보기)
python -m scripts.rebuild_template --engine gemma --apply       #    적용 (캐시 자동 사용, 100단위 chunk)
python -m scripts.rebuild_template --engine gemma --apply --use-cache  # 캐시만 사용 (LLM 재호출 X)
python -m scripts.rebuild_template --engine gemma --apply --only 옵시디언 --min-score 0.65  # 단일 + 임계값 조정
python -m scripts.recategorize --apply                          # 카테고리 재분류 + 아이콘 동기화
python -m scripts.rename_headings --apply                       # H2 헤더 한글 친화 통일
python -m scripts.demote_h2_to_h3 --apply                       # 비표준 H2 → H3 강등
python -m scripts.strip_meta_quotes --apply                     # TL;DR/메타 quote 박스 제거
python -m scripts.restore_from_backup --apply "키워드"           # 백업에서 원본 raw_blocks 복원 (LLM 변환 실패 시)
```

### Notion DB v2 스키마 (TEMPLATE.md 가 단일 진실)

**중요**: 4곳에서 같은 enum을 써야 함. 변경 시 모두 동시 업데이트:
- `scripts/analyzer/prompt.py` (`CATEGORIES`, `TAGS`, `AI_TOOLS`, `TARGETS`)
- `scripts/notion_client/register.py` (`CATEGORY_TO_DB`, `DB_TAGS`, `DIFFICULTY_TO_DB`, `CATEGORY_ICON`)
- `TEMPLATE.md` (사람용 문서)
- Notion DB select/multi_select 옵션 (실제 DB)

속성 9개만: `스킬명 / 등급 / 난이도 / 카테고리 / AI 도구 / 태그 / 적용 대상 / 출처 URL / 상태`. v1에서 제거된 5개(수집일/핵심요약/적용메모/출처유형/관련스킬)는 본문 메타 callout에 흡수.

### 카테고리(7) vs 태그(15) 분리 원칙

- **카테고리** = "어떤 작업 영역인가?" (select, 1개) — `프롬프트 / 자동화 / 콘텐츠 / 디자인 / 개발 / 업무 / 기타`
- **태그** = "어떤 기술/방법을 쓰는가?" (multi_select) — `MCP / API / RAG / Function Calling / Vision / Multimodal / 프롬프트체이닝 / CoT / Tool Use / Webhook / Streaming / CLI / GitHub Actions / 자체호스팅 / 오픈소스`

둘이 겹치지 않게 설계. Gemini 프롬프트에서 enum 강제 + register.py에서 enum 미일치 값은 자동 제거.

### 표준 본문 구조 (v2.3 보편 정보, 2026-05-18)

**v2.1 (8섹션 + TL;DR/메타 quote 박스) → v2.3 (callout + 보편 정보 + 한글 친화) 전환 완료**.

`scripts/rebuild_template.py:REBUILD_PROMPT` 가 단일 진실. 모든 페이지가 따르는 형태:

```
💡 [callout] 이 스킬은 [무엇]을 [어떻게] 하는 [도구/방법]입니다. [한 줄 가치 제안].
            (Notion callout 블록, 파란 배경 + 💡 아이콘, bold 강조)

## 🔑 어떻게 작동하나요?   ← 메커니즘/원리 (긴 경우 ### H3 분할)
## 🛠 따라 하기 (단계별)   ← numbered list (**굵은 짧은 라벨**: 설명)
## 💡 실제 예시            ← 표/코드/대화 (코드는 [[CODE_BLOCK_N]] placeholder 로 보호)
## ⚡ 이렇게 쓰면 효과적이다 ← 추천 시점 / 시너지 도구 / 수익화 가능성 / 적용 난이도 (보편 권장)
## ⚠️ 주의할 점            ← 한도/유료/실패 케이스
## 📎 출처
(필요시) ## 📌 원본 코드/명령어 (자동 보존) ← placeholder 누락된 코드 자동 rescue
```

**v2.1 → v2.3 핵심 변경**:
- `> **TL;DR** —` quote 박스 제거 → **💡 callout** 으로 시각 임팩트
- `> **메타** ...` quote 박스 제거 → DB properties 와 중복이라 폐지 (등급/카테고리/난이도/도구/대상은 우상단 properties 가 단일 진실)
- 영문 부제 (When to use / How it works / Steps / Examples / Caveats / Sources) 모두 제거 → 한글 친화 헤더만
- `## 🏢 두근 환경 적용` → `## ⚡ 이렇게 쓰면 효과적이다` (두근 프로젝트 강제 매핑 폐기 — 보편 정보로)
- bold (`**`) 적극 활용 — 핵심 명사·도구명·숫자
- 긴 섹션은 `###` H3 소제목 분할 권장

**보편 정보 원칙**: 두근컴퍼니/두근펫/매매봇/검은별/클로드코드/AI900/첼시인스타 같은 개인 프로젝트 매핑 강제 X. 다른 사용자·AI 가 RAG 로 읽고 자체 판단할 수 있게. `feedback_skill_pages_universal.md` 메모리 참조.

### 코드 보호 placeholder 패턴 (`scripts/rebuild_template.py`)

LLM 재작성 시 코드블록/인라인 코드/단축키 손실 방지:

1. **추출 단계** (`protect_code`): `\`\`\`...\`\`\`` 와 `` `...` `` 를 본문에서 추출 → `[[CODE_BLOCK_N]]` / `[[INLINE_N]]` 토큰으로 치환
2. **LLM 호출**: placeholder 포함된 텍스트 전달 (프롬프트에 "이 토큰은 절대 수정/번역/삭제 금지" 명시)
3. **복원 단계** (`restore_code` + `_PLACEHOLDER_RE` fuzzy): LLM 출력에서 placeholder 자리에 원본 코드 그대로 삽입. LLM 이 토큰명 변형 (`[[CON_7]]`, `[[CB_N]]`) 해도 fuzzy 매칭으로 복원
4. **누락 자동 rescue**: 매칭 실패한 placeholder 의 원본 코드 → 페이지 끝 `## 📌 원본 코드/명령어 (자동 보존)` 섹션에 자동 추가 — 데이터 손실 0

이 패턴 덕분에 LLM paraphrase 강도와 무관하게 코드/명령어/단축키는 100% 보존.

### LLM 보존율 검증 (`scripts/rebuild_template.py:preservation_score`)

- 원본 markdown 에서 한글 3자+ / 영문 5자+ 핵심 키워드 추출 (빈도 top 40)
- LLM 출력에 몇 % 보존됐는지 측정
- **임계값 기본 0.70** (`--min-score` 로 조정). 미달 시 자동 skip → 페이지 안 건드림
- 임계값 미달 페이지 → `restore_from_backup.py` 로 원본 그대로 복원 (정보 보존 우선)
- `STOPWORDS` 에 두근 개인 프로젝트명 포함 — 보편 정보 변환 시 의도적으로 빠지는 키워드는 누락 카운트 X

### SKILL.md ↔ Notion 본문 분리

`md_generator.render_skill_md()` 는 YAML 프론트매터 + H1 + 8섹션 (SKILL.md 표준).
**Notion 본문에 넣을 때는 `register.py:_strip_for_notion()` 이 프론트매터 + 최상위 H1 자동 제거**. 이걸 안 하면 YAML이 Notion 페이지 본문에 paragraph로 박혀버림 (실제 발생했던 버그).


## 함정 (Notion write 경로 전용)

1. **Gemini 2.5 Flash** (cloud, 무료 20/day per project — company-hq 와 키 공유)

2. **Gemini 2.5 Flash Lite** (cloud, 실측 20/day)

3. **Gemma 4 26B 또는 e4b** (Ollama localhost:11434, 무제한, cold start 20-30s)

5. **이모지 이중 표시** — 페이지 아이콘 + 제목 시작 이모지 둘 다 있으면 카드/링크에서 `🔍 ⚡ 제목` 처럼 두 번. `register.py:_clean_title()` 이 제목 첫 이모지 자동 제거 + `CATEGORY_ICON` 으로 아이콘 자동 설정.

10. **Notion API write 시 `null` 필드 제거 필수** — 페이지 fetch (read) 응답에는 `paragraph.icon: null` 같은 필드가 들어있는데 API write 가 이걸 reject (`should be an object or undefined`). `restore_from_backup.py:_strip_nulls()` 가 재귀적으로 None 제거 후 PATCH. raw_blocks 백업 그대로 보내면 안 됨.

11. **Notion code block language enum 매핑** — `code.language` 는 Notion 이 정한 enum 안에서만 허용. LLM 이 임의 언어 (예: `text`, `tsv`, `console`) 출력하면 reject. `rebuild_template.py:NOTION_CODE_LANGS` + `_LANG_ALIASES` + `_normalize_code_lang()` 가 안전하게 매핑 (모르면 `plain text`).

12. **Notion 인티그레이션 권한은 페이지별** — 마스터 DB 에 Connection 추가했어도 같은 워크스페이스 다른 페이지에는 자동 상속 안 됨. 외부 page id 가 `2e91...` 같이 다른 prefix 면 별도 권한 추가 필요. 또는 Playwright 로 public share view scrape.

13. **Notion page id prefix 충돌** — 같은 DB row 페이지들은 첫 8자 같음 (`35f14362-...`). 백업 파일명에 `pid[:8]` 만 쓰면 모든 파일이 같은 prefix → glob 매칭이 첫 1개만 반환 → **다른 페이지 본문이 잘못된 페이지에 박힘** (실 발생 버그). `backup_all.py` 와 `rebuild_template.py` 는 항상 **전체 32자** 사용.

14. **delete 후 append 패턴의 위험** — `rebuild_template.py:replace_h2_with_h3` 와 페이지 children 교체 시: `delete_all_children()` 다음 `append_blocks()`. 만약 append 가 validation 으로 실패하면 **페이지가 통째로 비어버림**. → `restore_from_backup.py` 즉시 실행으로 복원. append 실패 사유는 보통 (10), (11) 케이스.

15. **LLM 보편 정보 변환 한계** — 본문이 짧거나 광고성/특수 표현 위주 페이지는 보존율 0.40 미만으로 떨어짐 (실 사례: "클로드 MCP 메타 광고 자동화" 36%). 무리하게 변환하면 정보 손실 큼. 임계값 미달 페이지는 자동 skip → `restore_from_backup.py` 로 원본 보존 처리.

16. **노션 DB row 는 사이드바에 펼쳐 보임** — 노션 UI 가 "허브 페이지 → DB → row 페이지" 트리를 사이드바에 자동 expand. 사용자가 "외부 페이지 여러 개 생긴" 줄 오해할 수 있음. 실제 구조는 `허브 1 + DB 1 + DB.rows = 페이지 수`. `/v1/search` 결과로 검증 가능.

