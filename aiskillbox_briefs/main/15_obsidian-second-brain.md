💡 이 스킬은 **옵시디언(Obsidian) 으로 제 2의 뇌**를 만드는 폴더 구조 + 운영 루틴으로, **작업용·지식 공유용·개인용 3영역**을 분리해 정보를 10배 빠르게 흡수·재활용하는 PKM 시스템입니다.

## 이게 뭔가요?

**Obsidian (마크다운 기반 로컬 노트 앱) 으로 PKM(Personal Knowledge Management) 시스템 구축 가이드**. 핵심 컨셉은 정보를 **단순 저장이 아니라 즉시 활용 가능한 자산**으로 변환:

**10배 더 빠르게 흡수하는 4단계 루틴**:
1. **릴스 영상·콘텐츠**를 저장 또는 공유로 기록
2. DM 으로 받은 링크를 **카톡으로 옮겨** 두기
3. PC 로 접속해 **AI 즐겨찾기 폴더** 만들어 저장
4. **바로 사용** — 절대 미루지 말 것 (가장 중요)

**시스템의 본질 — 3영역 분리**:

| 영역 | 핵심 목적 | 노트 예시 |
|---|---|---|
| **Work(작업용)** | 수익·프로젝트 실행 | 미팅·작업 티켓·결과물 |
| **Shared-Knowledge(지식 공유용)** | 팀·커뮤니티용 매뉴얼 | SOP·튜토리얼·리서치 정리 |
| **Personal(개인용)** | 사적 기록과 실험 | 일기·브레인덤프·개인 공부 노트 |

💰 유료 필요: 없음 (Obsidian 개인용 무료, Sync 만 유료)
✅ 무료 대안: Obsidian 자체 무료 / iCloud·Google Drive 폴더 동기화로 Sync 대체

## 따라하기

### 추천 Vault 전체 구조

```
Vault/
├── 00-Inbox/                # 모든 캡처 공용 인박스
├── 10-Work/                 # 작업용 (실무, 클라이언트)
│   ├── 11-Projects/
│   ├── 12-Meetings/
│   ├── 13-Assets/
│   └── 19-Archive/
├── 20-Shared-Knowledge/     # 지식/정보 공유용
│   ├── 21-Guides/
│   ├── 22-Playbooks/
│   ├── 23-Research/
│   └── 29-Archive/
├── 30-Personal/             # 개인용 (일기, 아이디어)
│   ├── 31-Journal/
│   ├── 32-Learning/
│   └── 39-Archive/
├── Attachments/
└── Templates/
```

### 1) 작업용 폴더 (10-Work) 도식 & 팁

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

**꿀팁 3가지**:
- **프로젝트 = 허브 노트** — 각 `P-프로젝트` 노트 상단에 **목표·마감·주요 링크**(미팅·코드·파일) 걸어두면 **컨트롤 타워** 역할
- **미팅은 모두 12-Meetings 로 통합** — `날짜+주제` 형식 통일 후 관련 프로젝트로만 링크
- **Assets 는 "재사용 가능" 만** — 체크리스트·공용 스크립트·피치덱 템플릿처럼 **다시 쓸 것만** 모음

### 2) 지식/정보 공유용 폴더 (20-Shared-Knowledge) 도식 & 팁

```
20-Shared-Knowledge/
├── 21-Guides/         # HOW: 실행 방법
│   ├── G-Instagram-Reels-Playbook.md
│   ├── G-N8N-Error-Handling.md
│   └── G-Client-Onboarding.md
├── 22-Playbooks/      # 전략/시나리오
│   ├── PB-Launch-Sequence.md
│   └── PB-Content-Calendar-System.md
├── 23-Research/       # 리서치/요약
│   ├── R-AI-Agents-2026Q1.md
│   └── R-Obsidian-Workflows.md
└── 29-Archive/
```

**꿀팁 3가지**:
- **제목 접두사로 타입 구분** — `G-` (Guide), `PB-` (Playbook), `R-` (Research). 파일명만 봐도 성격이 보임
- **공유 전제 메타데이터** — 상단에 **작성자·최신 업데이트·적용 범위** 등을 property 로 고정
- **개인 생각은 Personal 로 링크만** — 실험적 아이디어·날것 메모는 Personal 에 두고 **검증된 내용만** Guide/Playbook 으로 승격

### 3) 개인용 폴더 (30-Personal) 도식 & 팁

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

**꿀팁 3가지**:
- **하루 1노트 저널** — 일일 로그에 아이디어·착안점·시행착오 모두 쌓고, 나중에 Shared-Knowledge 로 승격할 것만 골라냄
- **Learning 노트는 '내 언어로'** — 원문 인용 최소화, 본인 사례·적용 아이디어 위주로 적으면 바로 Playbook 으로 옮기기 좋음
- **`#private` 태그로 선 긋기** — 아주 개인적인 내용은 `#private` 태그로 표시해 공유 범위 한 번에 필터링

### 4) 세 영역을 이어주는 운영 루틴

세 구역이 따로 놀지 않게 간단한 흐름:

| 단계 | 작업 |
|---|---|
| **캡처** | 모든 정보는 우선 `00-Inbox` 또는 `31-Journal` 로 들어감 |
| **주간 정리** | 인박스를 보면서, **실행 필요한 것 → 11-Projects**, **재사용 가능 지식 → 20-Shared-Knowledge** 로 이동 |
| **승격 규칙** | "두 번 이상 썼다" 싶으면 Personal/Work 에 있던 내용을 **Guide/Playbook 으로 승격** |

### Claude Code 연동 패턴 (옵션)

Vault 폴더를 Claude Code 작업 디렉토리로 지정하면:
- **CLAUDE.md** 를 Vault 루트에 두어 AI 가 본인 지식 베이스 전체 인지
- Claude Code 가 **마크다운 노트 자동 생성·갱신**
- `/skills/` 도 Vault 안에 두면 본인 작업 지식이 모두 AI 스킬로 자산화

## 활용 예시

- **1인 사업자·프리랜서 — 클라이언트 일원화** — Work 폴더에 클라이언트별 P-프로젝트 노트. 미팅·산출물·인보이스 모두 한 곳. 클라이언트 추가될 때마다 폴더 복제만
- **콘텐츠 크리에이터 — 영상 기획 → 발행 파이프라인** — Inbox 에 아이디어 캡처 → 11-Projects/P-YouTube-Channel 로 승격 → 12-Meetings 에 촬영 일정 → 21-Guides/G-Editing-Workflow 에 매번 쓰는 편집 체크리스트
- **개발자 — 코드·문서·미팅 통합** — 11-Projects 안 코드 저장 + 21-Guides 에 본인이 쓰는 라이브러리 정리 + 32-Learning 에 새로 배운 패턴. 6개월 후 시니어 개발자 본인이 후배에게 던질 자산 완성
- **연구자·대학원생 — 논문 + 실험 + 일기 분리** — Work 에 실험 데이터·논문 초안 / Shared 에 본인 분야 서베이 정리 / Personal 에 메타인지·아이디어. 학위논문 작성 시 Shared 만 모아 챕터화
- **회사 팀 — Slack·미팅 록 통합 매뉴얼화** — Slack DM·미팅 내용을 Inbox 에 일단 받고, **두 번 나오면** Guides 로 승격. 신입 온보딩 시 21-Guides 만 던져주면 됨
- **부모 — 자녀 학습·취미·생활 기록** — Personal 의 일기·Learning 에 자녀 발달 기록. 연 1회 회고로 자녀 성장 자산화

## 💡 아이디어

- **Obsidian Vault 템플릿 배포** — 직군별(개발자·마케터·연구자·1인사업자) Vault 구조 템플릿 → 무료 + Pro 버전 ($10)
- **PKM 코칭 1:1** — 본인 직군에 맞게 폴더 구조·운영 루틴 설계 컨설팅 → 1회 $100-300. 월 5-10명 처리 가능
- **Vault 자동 정리 봇** — Claude Code 가 매주 일요일 Vault 자동 정리: Inbox 비우기, 두 번 등장한 키워드를 Guide 로 승격 제안. 오픈소스 + Pro 호스팅 $5/월
- **Obsidian + Notion 양방향 싱크 도구** — Obsidian (로컬·빠름) + Notion (공유 쉬움) 양립 운영 도구 → $10/월
- **PKM 신간 출간** — 본인 6개월 운영 일지를 책으로 정리. PKM 한국어 자료 부족해서 시장 비어 있음

## 주의사항

- **3영역 동시에 만들지 말 것** — 우선 Work 만 시작 → 1개월 운영 → Shared, Personal 추가. 한 번에 다 만들면 빈 폴더가 의욕 꺾음
- **승격 규칙을 지키지 못하면 폴더 의미 X** — "두 번 등장" 규칙 안 지키면 Personal 이 폭주. **주 1회 30분 정리 시간** 캘린더에 고정 필수
- **링크 너무 깊게 만들지 말 것** — Obsidian 그래프 뷰가 예쁘다고 모든 노트 서로 링크하면 검색·이동 비효율. **한 노트당 평균 3-5 링크** 권장
- **Sync 유료 결제 전 무료 동기화 시도** — iCloud/Google Drive 로도 충분히 동기화 가능. Sync ($4/월) 는 충돌 자동 해결 등 편의 기능
- **모바일 편집은 보조용** — 모바일 Obsidian 은 빠른 캡처용. 정리·승격은 PC 에서. 모바일에서 깊게 편집하다가 데이터 손실 사례 있음

## 출처

- [클로드코드x옵시디언으로 제 2의 뇌 만들기 (Notion)](https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf)
