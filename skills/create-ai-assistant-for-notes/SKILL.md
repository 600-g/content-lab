---
name: create-ai-assistant-for-notes
description: 릴스·DM·링크로 들어오는 AI 정보를 **저장 습관 → 옵시디언(Obsidian) 볼트 구조 → 카파시 LLM Wiki** 순으로 쌓고, **Claude Code** 가 볼트를 읽어 ingest·query·lint 로 답해주는 '제2의 뇌' 메모 비서를 만드는 스킬입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://adu-llm-wiki.vercel.app/?fbclid=PAVERFWASrLkRleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafopEyq9qrMijCCDp96qb158X29Agwno0-jPsFSwe4cSeEzyVOwtKtfzy-DHw_aem_s3d4e4EQ4Xs6x0b10NDE6A
  - https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149
  - https://waiting-drug-536.notion.site/387d86104de2806f8657d947faa7156b?pvs=149
  - https://waiting-drug-536.notion.site/LLM-WIKI-39ed86104de28049b9d4ffaf2979a20b?pvs=149
---

# 내 메모를 이해하는 AI 비서

💡 정보를 **바로 캡처**하고, **옵시디언 볼트**에 구조대로 쌓고, **Claude Code** 가 그 볼트를 **LLM Wiki** 로 정리해 질문에 답하게 만드는 '제2의 뇌' 구축 가이드입니다.

## 이게 뭔가요?

AI 와 GPT 는 5년 전만 해도 생활과 거리가 멀었지만 이제는 없어서는 안 될 기술이 되었습니다. 인터넷 활용 능력이 그랬던 것처럼, 앞으로는 AI 를 잘 다루는 능력이 뒤처지지 않기 위한 핵심 역량이 됩니다. 문제는 정보가 릴스·DM·카톡·뉴스레터로 쏟아져 들어와 **한 번 보고 잊힌다**는 점입니다.

이 스킬은 그 정보를 "다시 찾아 쓰는 지식", 나아가 "AI 가 읽고 답해주는 지식"으로 바꾸는 전 과정을 한 흐름으로 다룹니다.

| 단계 | 하는 일 | 결과 |
|---|---|---|
| ① 저장 습관 | 릴스·DM·링크를 놓치지 않고 모으고 **바로 써본다** | 흩어진 정보가 한곳으로 모임 |
| ② 볼트 구조 | 옵시디언 볼트를 Work / Shared-Knowledge / Personal 로 나누고 캡처 → 주간 정리 → 승격 루틴을 돌린다 | 사람이 다시 찾아 쓰는 지식 |
| ③ LLM Wiki | OpenAI 창립 멤버 **안드레 카파시**가 공개한 'LLM Wiki' 패턴(`raw/` · `wiki/` · `index.md` · `log.md` · `CLAUDE.md`)을 적용한다 | AI 가 정리한 읽기용 위키 |
| ④ AI 비서 | Claude Code 가 볼트 폴더를 직접 열어 ingest·query·lint 를 수행한다 | 내 메모 전체를 이해하고 답하는 '살아있는 지식 시스템' |

**작동 방식**

- **Obsidian**: 내 모든 메모와 자료가 저장되는 저장소입니다.
- **Claude Code**: Obsidian 폴더를 직접 열어 읽고 요약·분류·연결해 '읽기 좋은 위키' 형태로 정리하는 AI 사서입니다.

예전 메모 앱이 단순히 저장만 담당했다면, 이 방식은 AI 가 내 메모 전체를 읽고 이해해 질문에 답합니다. Claude Code 와 Obsidian 만 있으면 ③~④ 단계는 약 **30분** 안에 구축할 수 있습니다.

**💰 비용**: ①~② 단계는 무료입니다(옵시디언은 개인 사용 기준 무료). ③~④ 단계의 Claude Code 는 **Claude Pro 또는 Max 구독**이 필요합니다. Obsidian, Node.js, Web Clipper 는 무료입니다.

### 어떤 구조를 언제 쓰나

| 상황 | 추천 구조 | 이유 |
|---|---|---|
| AI 없이 내가 직접 정리하고 다시 찾아 쓰고 싶다 | 3영역 볼트 (따라하기 2~3) | 폴더·접두사·태그로 사람이 찾기 쉬움, 완전 무료 |
| AI 가 내 자료를 읽고 요약·답변해 주길 원한다 | 카파시 LLM Wiki (따라하기 4~5) | `raw/` 원본 + `wiki/` AI 정리본 분리, Claude Code 규칙 파일로 일관 운영 |
| 둘 다 원한다 | 3영역 볼트로 캡처·승격을 운영하고, AI 에게 맡길 원본은 `raw/` 에 넣어 ingest | 사람용 정리와 AI 용 원본 보관을 한 볼트에서 같이 굴림 |

처음이라면 **① 저장 습관부터** 시작하고, 볼트가 어느 정도 쌓이면 ③~④ 를 붙이는 순서가 가장 부담이 적습니다.

## 따라하기

### 1. 정보를 놓치지 않고 캡처하기 (저장 습관)

AI 관련 유용한 정보를 놓치지 않고 흡수하기 위한 4단계입니다. 정보를 접하는 즉시 기록하고 바로 써보는 습관이 이후 모든 단계의 전제입니다.

1. **릴스 영상 저장 또는 공유하기로 기록**: 인스타그램 릴스나 다른 영상 플랫폼에서 유용한 AI 정보를 발견하면 바로 저장하거나 공유 기능(예: DM 보내기)으로 기록해 둡니다.
2. **DM 으로 받은 링크를 카카오톡으로 옮기기**: 다른 사람에게 DM 으로 받은 AI 관련 링크는 개인 확인·관리를 위해 카카오톡 등 자신에게 편한 메신저로 옮겨 둡니다.
3. **PC 로 접속해 'AI 즐겨찾기' 폴더를 만들어 저장**: 모바일에서 기록해 둔 정보를 PC 로 옮겨 'AI 즐겨찾기' 같은 별도 폴더에 모읍니다. PC 에서 더 쉽고 빠르게 찾을 수 있습니다. (볼트를 만든 뒤에는 이 자리를 `00-Inbox` 또는 `raw/` 가 대신합니다.)
4. **바로 사용해보기 (⭐ 제일 중요 — 절대 미루지 마세요)**: 저장한 정보는 미루지 말고 즉시 실행해 봅니다. 학습한 내용을 바로 적용해야 실질적인 능력이 늘어납니다.

### 2. 옵시디언 설치와 볼트 만들기

1. obsidian.md 에서 Obsidian 을 다운로드해 설치합니다.
2. 'Create new vault' 를 눌러 새 Vault(자료 저장 폴더)를 만들고 이름을 정합니다 (예: MyBrain).
3. Vault 폴더의 위치를 기억해 둡니다. Claude Code 를 붙일 때 이 경로를 씁니다.

### 3. 사람이 쓰는 3영역 볼트 구조 만들기

#### 3-1. 최상위 구조

옵시디언 볼트 안에 아래 폴더 구조를 그대로 만듭니다.

```
Vault/
├── 00-Inbox/              # 모든 캡처 공용 인박스
├── 10-Work/                # 작업용 (실무, 클라이언트)
│   ├── 11-Projects/
│   ├── 12-Meetings/
│   ├── 13-Assets/
│   └── 19-Archive/
├── 20-Shared-Knowledge/    # 지식/정보 공유용
│   ├── 21-Guides/
│   ├── 22-Playbooks/
│   ├── 23-Research/
│   └── 29-Archive/
├── 30-Personal/            # 개인용 (일기, 아이디어)
│   ├── 31-Journal/
│   ├── 32-Learning/
│   └── 39-Archive/
├── Attachments/
└── Templates/
```

각 영역의 목적은 다음과 같습니다.

| 영역 | 핵심 목적 | 노트 예시 |
|---|---|---|
| Work(작업용) | 수익/프로젝트 실행 | 미팅, 작업 티켓, 결과물 |
| Shared-Knowledge | 팀/커뮤니티를 위한 매뉴얼 | SOP, 튜토리얼, 리서치 정리 |
| Personal(개인용) | 사적 기록과 실험 | 일기, 브레인덤프, 개인 공부 노트 |

#### 3-2. 작업용 (10-Work)

실제 돈이 오가는 프로젝트를 중심으로 최소 구조만 두고, 나머지는 링크·태그로 엮습니다.

```
10-Work/
├── 11-Projects/
│   ├── P-AINOW-Youtube/
│   ├── P-Client-Clinic-A/
│   └── P-AutoTrading-Bot/
├── 12-Meetings/
│   ├── M-2026-05-05-Client-Clinic-A/
│   └── M-2026-05-06-Team-Standup/
├── 13-Assets/
│   ├── Scripts/
│   ├── Templates-Decks/
│   └── Checklists/
└── 19-Archive/
    └── 2025/
```

- **프로젝트 = 허브 노트**: 각 `P-프로젝트` 노트 상단에 목표, 마감, 주요 링크(미팅, 코드, 파일)를 걸어 두면 "컨트롤 타워" 역할을 합니다.
- **미팅은 모두 12-Meetings 로 통합**: 날짜+주제 형식으로 통일하고, 관련 프로젝트로만 링크합니다.
- **Assets 는 "재사용 가능"만**: 체크리스트, 공용 스크립트, 피치덱 템플릿처럼 다시 쓸 것만 모읍니다.

#### 3-3. 지식공유용 (20-Shared-Knowledge)

"사람이 바뀌어도 남는 지식"을 정리하는 공간이라, 구조보다 일관된 노트 타입이 더 중요합니다.

```
20-Shared-Knowledge/
├── 21-Guides/       # HOW: 실행 방법
│   ├── G-Instagram-Reels-Playbook.md
│   ├── G-N8N-Error-Handling.md
│   └── G-Client-Onboarding.md
├── 22-Playbooks/     # 전략/시나리오
│   ├── PB-Launch-Sequence.md
│   └── PB-Content-Calendar-System.md
├── 23-Research/      # 리서치/요약
│   ├── R-AI-Agents-2026Q1.md
│   └── R-Obsidian-Workflows.md
└── 29-Archive/
```

- **제목 접두사로 타입 구분**: `G-`, `PB-`, `R-` 처럼 파일명만 보고도 성격이 보이게 합니다.
- **공유 전제 메타데이터**: 상단에 작성자, 최신 업데이트 날짜, 적용 범위 등을 property 로 고정합니다.
- **개인 생각은 Personal 로 링크만**: 실험적 아이디어나 날것의 메모는 Personal 에 두고, 검증된 내용만 Guide/Playbook 으로 승격합니다.

#### 3-4. 개인용 (30-Personal)

자유도가 높지만 최소 가드레일을 두면 나중에 "공유 가능 지식"으로 옮기기 쉽습니다.

```
30-Personal/
├── 31-Journal/
│   ├── J-2026-05-05.md
│   └── J-2026-05-06.md
├── 32-Learning/
│   ├── L-Book-Building-A-Second-Brain.md
│   ├── L-Course-Advanced-N8N.md
│   └── L-YouTube-Channel-Analysis.md
└── 39-Archive/
```

- **하루 1노트 저널**: 일일 로그에 아이디어, 착안점, 시행착오를 모두 쌓고, 나중에 Shared-Knowledge 로 승격할 것만 골라냅니다.
- **Learning 노트는 '내 언어로'**: 원문 인용은 최소화하고 본인 사례·적용 아이디어 위주로 적으면 바로 Playbook 으로 옮기기 좋습니다.
- **Private 태그로 선 긋기**: 아주 개인적인 내용은 `#private` 태그로 표시해 공유 범위를 한 번에 필터링합니다.

#### 3-5. 세 영역을 이어주는 운영 루틴

1. **캡처**: 모든 정보는 우선 `00-Inbox` 또는 `31-Journal` 로 들어갑니다.
2. **주간 정리**: 인박스를 보면서 실행이 필요한 것은 `10-Work/11-Projects` 로, 재사용 가능한 지식은 `20-Shared-Knowledge` 로 옮깁니다.
3. **승격 규칙**: "두 번 이상 썼다" 싶으면 Personal/Work 에 있던 내용을 Guide/Playbook 으로 승격합니다.

### 4. AI 가 읽는 LLM Wiki 구조 잡기 (카파시 정석)

AI 에게 정리와 답변을 맡길 때는 원본과 AI 정리본을 분리한 아래 구조를 씁니다. 3영역 볼트와 함께 쓴다면 같은 볼트 최상위에 두면 됩니다.

- `raw/`: 기사, 논문, 메모 등 원본 자료를 그대로 저장하는 폴더.
- `raw/articles/`: 웹 클리핑 자료 저장 폴더 (선택 사항).
- `wiki/`: AI 가 정리한 읽기용 페이지가 저장되는 폴더.
- `index.md`: 위키 전체 목차.
- `log.md`: 작업 이력 기록.
- `CLAUDE.md`: AI 운영 규칙 파일.

이 폴더와 파일은 손으로 만들어도 되지만, 5단계의 설계도 프롬프트를 쓰면 Claude Code 가 한 번에 만들어 줍니다.

### 5. Claude Code 를 볼트에 붙이기

#### 5-1. Claude Code 설치

1. **Node.js 설치**: nodejs.org 에서 LTS 버전을 다운로드해 설치합니다.
   - 터미널(Mac) 또는 PowerShell(Windows)에서 `node -v` 를 입력해 설치를 확인합니다.
2. **Claude Code 설치**: 터미널 또는 PowerShell 에서 다음 명령어를 실행합니다.
   ```
   npm install -g @anthropic-ai/claude-code
   ```
3. **로그인**: 터미널에서 `claude` 를 실행하고 안내에 따라 Claude 계정으로 로그인합니다.

#### 5-2. Vault 를 Claude Code 로 열기

1. 터미널에서 내 Vault 폴더로 이동합니다.
   ```
   # 예시 (실제 경로로 변경)
   cd "~/Documents/MyBrain"
   ```
2. 해당 폴더에서 `claude` 를 실행합니다.

#### 5-3. 카파시 설계도 적용 (지름길)

1. 아래 주소에서 카파시의 LLM Wiki 설계도를 복사합니다:
   [https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
2. Claude Code(`claude` 실행 후)에 복사한 내용을 붙여넣고 다음과 같이 요청합니다:
   ```
   이 설계도를 그대로 내 세컨드 브레인으로 구현해줘. - CLAUDE.md 규칙 파일을 만들고 - index.md와 log.md를 만들고 - raw, wiki 폴더 구조를 잡아줘 - 첫 ingest 예시를 한 번 보여줘 앞으로 모든 작업은 이 규칙을 따른다. 한국어로 해줘.
   ```
3. AI 의 제안을 허용하고 폴더와 파일이 생성됐는지 확인합니다.

### 6. 자료 넣고 굴리기 (ingest · query · lint)

#### 자료 넣는 방법

1. **직접 넣기**: 마크다운(.md) 형식으로 저장된 메모나 문서를 `raw/` 폴더에 넣습니다. 1단계에서 모아 둔 링크·메모, 3영역 볼트의 `00-Inbox` 에서 AI 에게 맡길 것도 여기로 옮기면 됩니다.
2. **웹에서 줍기**: Obsidian Web Clipper 를 설치해 웹 기사를 `raw/articles/` 에 저장합니다.

#### 핵심 동작 ① ingest

자료를 넣은 뒤 Claude Code 가 실행 중인 상태에서 다음 명령어를 입력합니다.

```
› ingest
```

AI 가 자동으로 요약, 엔티티 추출, 개념 분류/연결, 목차(`index.md`) 및 이력(`log.md`) 갱신을 수행합니다.

#### 핵심 동작 ② query

정리된 위키(`wiki/` 폴더)에 평소 말투로 질문합니다. AI 는 흩어진 정보를 모아 새로운 정리본을 만들어 줍니다.

- 예: "예전에 적었던 AI 관련 아이디어 전부 찾아서 정리해줘."

#### 핵심 동작 ③ lint

AI 에게 위키 점검을 요청해 오래된 주장, 모순, 끊긴 링크 등을 찾아 고칩니다.

```
› 위키를 점검(lint)해줘. 오래된 주장, 서로 모순되는 내용, 끊긴 링크, 외톨이 페이지, 약한 연결을 찾아서 알려줘.
```

#### 운영 두 가지 원칙

1. **위키가 자산, 채팅은 창구**: 가치 있는 결과는 반드시 위키 페이지로 저장합니다.
2. **꾸준히, 작게 처리**: 매일 정해진 시간에 ingest 를 수행해 시스템 과부하를 막습니다. 3영역 볼트의 주간 정리와 같은 리듬으로 묶어 두면 빠뜨리지 않습니다.

### 7. 시작 체크리스트

- [ ] 릴스·DM·링크를 한 곳(메신저 → PC 'AI 즐겨찾기' 또는 `00-Inbox`)에 모으고 있다
- [ ] 저장한 것 중 하나는 오늘 바로 써봤다
- [ ] 옵시디언 볼트를 만들고 경로를 알고 있다
- [ ] (사람용) `00-Inbox` / `10-Work` / `20-Shared-Knowledge` / `30-Personal` 구조와 주간 정리 요일을 정했다
- [ ] (AI 용) `node -v` 확인 → Claude Code 설치·로그인 완료
- [ ] 볼트 폴더에서 `claude` 실행 후 카파시 설계도로 `CLAUDE.md` · `index.md` · `log.md` · `raw/` · `wiki/` 생성 확인
- [ ] 첫 자료를 `raw/` 에 넣고 `› ingest` → `wiki/` 페이지 생성 확인
- [ ] 백업(클라우드 동기화 또는 주기 복사) 설정

## 활용 예시

- **직장인**: 회의록·업무 메모를 `raw/` 에 모아 "이번 주 내 할 일", "지난 분기 결정사항" 등을 질문해 주간 보고 초안 작성에 활용합니다. 미팅 원본은 `12-Meetings/M-2026-05-05-Client-Clinic-A.md` 처럼 기록하고 상위 `P-Client-Clinic-A` 허브 노트에 링크해 프로젝트 진행 상황을 한곳에서 파악합니다.
- **크리에이터**: 아이디어·레퍼런스를 `raw/` 에 저장하고 "이번 달 콘텐츠 소재 후보", "예전 인기 글 패턴" 등을 질문해 기획에 활용합니다.
- **공부하는 사람**: 강의 노트·책 요약을 `raw/` 에 넣고 "이 개념 관련 내 메모 전부", "시험 범위 핵심만" 등을 질문해 학습 자료를 정리합니다. 매일 저녁 `31-Journal` 에 하루 배운 것을 기록하고, 주간 정리 때 반복해서 언급된 아이디어만 골라 `32-Learning` 이나 Guide 로 승격합니다.
- **팁 → 가이드 승격**: 릴스에서 본 N8N 에러 처리 팁을 캡처 → `00-Inbox` 에 저장 → 실제로 두 번 이상 적용해 봄 → `20-Shared-Knowledge/21-Guides/G-N8N-Error-Handling.md` 로 승격합니다.
- **새 AI 툴 바로 써보기**: 릴스에서 새 AI 이미지 생성 툴 소개 영상을 보면 저장한 뒤, PC 의 'AI 툴' 폴더(또는 인박스)에 둔 링크를 열어 그날 직접 사용해 봅니다.
- **동료가 공유한 GPT 프롬프트**: DM 으로 받은 업무 자동화 프롬프트 링크를 개인 카톡으로 옮겨 두었다가, 퇴근 후 PC 에서 열어 프롬프트를 복사해 실제 업무에 적용합니다.
- **AI 뉴스레터 요약**: 구독 중인 AI 뉴스레터에서 흥미로운 기사 링크를 저장해 두었다가 주말에 PC 로 모아 보고, 관심 있는 내용은 `raw/articles/` 에 넣어 ingest 한 뒤 실행 계획을 세웁니다.

## 💡 아이디어

- **개인화된 AI 학습 루틴**: 매일 짧은 시간을 정해 저장된 AI 정보를 하나씩 실행해 보고, 결과를 저널에 남긴 뒤 ingest 하면 학습 기록이 그대로 위키가 됩니다. 이를 바탕으로 개인 맞춤형 AI 학습 로드맵을 만들 수 있습니다.
- **스터디 그룹·커뮤니티 운영**: 각자 수집하고 실행해 본 AI 정보를 공유하고 토론하면 집단지성의 힘을 쓸 수 있습니다. 검증된 내용은 `20-Shared-Knowledge` 의 Guide/Playbook 형태로 모아 공유 자료로 삼습니다.
- **후기 콘텐츠 제작**: 써 본 AI 도구들의 후기를 위키에 쌓고, query 로 묶어 콘텐츠 초안을 만들어 수익화를 시도해 볼 수 있습니다.

## 주의사항

- **민감 정보 금지**: 비밀번호, 주민등록번호 등 민감한 정보는 Vault 에 저장하지 않습니다. AI 가 볼트 전체를 읽는다는 점을 전제로 합니다. 아주 개인적인 노트는 `#private` 태그로 구분해 둡니다.
- **원본(raw) 보존**: AI 가 `raw/` 폴더의 원본 파일을 임의로 수정하지 않도록 합니다. ingest 때 AI 가 `raw/` 를 바꾸려 하면 거부합니다.
- **백업 필수**: Vault 폴더를 클라우드에 동기화하거나 주기적으로 복사해 백업합니다.
- **처음엔 사본으로**: 중요한 자료는 복사본으로 먼저 연습한 뒤 적용합니다.
- **구조보다 캡처 먼저**: 구조를 먼저 완벽하게 만들려고 하면 시작이 늦어집니다. `00-Inbox` 에 일단 캡처하고 주간 정리 때 분류하는 흐름이 더 중요합니다.
- **승격은 검증 후**: Personal 의 날것 메모를 검증 없이 바로 Shared-Knowledge 로 옮기면 신뢰도가 떨어집니다. 반드시 "두 번 이상 썼다" 기준을 거친 뒤 승격합니다.
- **저장만 하고 끝내지 않기**: 저장은 시작일 뿐입니다. 바로 써보지 않은 정보는 볼트에 쌓여도 실력이 되지 않습니다.
- **비용**: Claude Code 를 쓰는 ③~④ 단계는 Claude Pro 또는 Max 구독이 필요합니다.

## 출처

- [https://adu-llm-wiki.vercel.app/?fbclid=PAVERFWASrLkRleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafopEyq9qrMijCCDp96qb158X29Agwno0-jPsFSwe4cSeEzyVOwtKtfzy-DHw_aem_s3d4e4EQ4Xs6x0b10NDE6A](https://adu-llm-wiki.vercel.app/?fbclid=PAVERFWASrLkRleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafopEyq9qrMijCCDp96qb158X29Agwno0-jPsFSwe4cSeEzyVOwtKtfzy-DHw_aem_s3d4e4EQ4Xs6x0b10NDE6A)
- [https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149](https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149)
- [https://waiting-drug-536.notion.site/387d86104de2806f8657d947faa7156b?pvs=149](https://waiting-drug-536.notion.site/387d86104de2806f8657d947faa7156b?pvs=149)
- [https://waiting-drug-536.notion.site/LLM-WIKI-39ed86104de28049b9d4ffaf2979a20b?pvs=149](https://waiting-drug-536.notion.site/LLM-WIKI-39ed86104de28049b9d4ffaf2979a20b?pvs=149)
