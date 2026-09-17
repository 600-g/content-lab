---
name: obsidian-second-brain-vault-structure
description: 이 스킬은 **옵시디언(Obsidian)** 볼트를 Work / Shared-Knowledge / Personal 세 영역으로 나누고, **캡처 → 주간 정리 → 승격** 루틴으로 운영해 정보를 "제2의 뇌"로 축적하는 볼트 구조 설계 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 업무
ai_tools: ["도구무관"]
sources:
  - https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149
---

# 옵시디언 볼트 3단 구조화하기

💡 이 스킬은 **옵시디언(Obsidian)** 볼트를 Work / Shared-Knowledge / Personal 세 영역으로 나누고, **캡처 → 주간 정리 → 승격** 루틴으로 운영해 정보를 "제2의 뇌"로 축적하는 볼트 구조 설계 스킬입니다.

## 이게 뭔가요?
이 스킬은 **옵시디언(Obsidian)**을 활용해 릴스·DM·카톡 등으로 쏟아지는 정보를 놓치지 않고 흡수하고, 이를 **작업용 / 지식공유용 / 개인용** 세 영역으로 나눠 정리하는 볼트(Vault) 구조 설계법입니다. 메모 앱을 그냥 쓰는 게 아니라, 캡처 → 주간 정리 → 승격이라는 운영 루틴을 통해 "한 번 보고 잊는 정보"를 "다시 찾아 쓰는 지식"으로 전환하는 것이 핵심입니다.

정보를 접하는 즉시 기록하고 바로 사용해보는 습관이 전제입니다. 릴스 영상은 저장/공유로 남기고, DM 링크는 카톡으로 옮기고, PC에서 AI 즐겨찾기 폴더에 모아둔 뒤 절대 미루지 않고 바로 써보는 것이 흡수 속도를 높이는 방법으로 소개됩니다.

💰 유료 필요 없음 — 옵시디언은 개인 사용 기준 무료입니다.
✅ 무료 대안: 옵시디언 자체가 무료 도구이므로 별도 대안이 필요 없습니다.

## 따라하기

### 1. 정보를 놓치지 않고 캡처하기
1. 릴스 영상을 **저장 또는 공유**로 기록해둔다.
2. DM으로 받은 링크는 **카톡**으로 옮겨 놓는다.
3. PC로 접속해서 **AI 즐겨찾기 폴더**를 만들어 저장해둔다.
4. 바로 사용해본다. 절대 미루지 않는다. (⭐ 제일 중요)

### 2. 볼트 최상위 구조 만들기
옵시디언 볼트 안에 아래 폴더 구조를 그대로 만든다.

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

각 영역의 목적은 다음과 같다.

| 영역 | 핵심 목적 | 노트 예시 |
|---|---|---|
| Work(작업용) | 수익/프로젝트 실행 | 미팅, 작업 티켓, 결과물 |
| Shared-Knowledge | 팀/커뮤니티를 위한 매뉴얼 | SOP, 튜토리얼, 리서치 정리 |
| Personal(개인용) | 사적 기록과 실험 | 일기, 브레인덤프, 개인 공부 노트 |

### 3. 작업용(10-Work) 폴더 세팅하기
실제 돈이 오가는 프로젝트를 중심으로 최소 구조만 두고, 나머지는 링크·태그로 엮는다.

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

꿀팁:
- **프로젝트 = 허브 노트**: 각 `P-프로젝트` 노트 상단에 목표, 마감, 주요 링크(미팅, 코드, 파일)를 걸어두면 "컨트롤 타워" 역할을 한다.
- **미팅은 모두 12-Meetings로 통합**: 날짜+주제 형식으로 통일하고, 관련 프로젝트로만 링크한다.
- **Assets는 "재사용 가능"만**: 체크리스트, 공용 스크립트, 피치덱 템플릿처럼 다시 쓸 것만 모은다.

### 4. 지식공유용(20-Shared-Knowledge) 폴더 세팅하기
"사람이 바뀌어도 남는 지식"을 정리하는 공간이라, 구조보다 일관된 노트 타입이 더 중요하다.

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

꿀팁:
- **제목 접두사로 타입 구분**: `G-`, `PB-`, `R-`처럼 파일명만 보고도 성격이 보이게 한다.
- **공유 전제 메타데이터**: 상단에 작성자, 최신 업데이트 날짜, 적용 범위 등을 property로 고정한다.
- **개인 생각은 Personal로 링크만**: 실험적 아이디어나 날것의 메모는 Personal에 두고, 검증된 내용만 Guide/Playbook으로 승격한다.

### 5. 개인용(30-Personal) 폴더 세팅하기
자유도가 높지만, 최소 가드레일을 두면 나중에 "공유 가능 지식"으로 옮기기 쉽다.

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

꿀팁:
- **하루 1노트 저널**: 일일 로그에 아이디어, 착안점, 시행착오를 모두 쌓고, 나중에 Shared-Knowledge로 승격할 것만 골라낸다.
- **Learning 노트는 '내 언어로'**: 원문 인용은 최소화하고 본인 사례·적용 아이디어 위주로 적으면 바로 Playbook으로 옮기기 좋다.
- **Private 태그로 선 긋기**: 아주 개인적인 내용은 `#private` 태그로 표시해 공유 범위를 한 번에 필터링한다.

### 6. 세 영역을 이어주는 운영 루틴 돌리기
1. **캡처**: 모든 정보는 우선 `00-Inbox` 또는 `31-Journal`로 들어간다.
2. **주간 정리**: 인박스를 보면서, 실행이 필요한 것은 `10-Work/11-Projects`로, 재사용 가능한 지식은 `20-Shared-Knowledge`로 옮긴다.
3. **승격 규칙**: "두 번 이상 썼다" 싶으면 Personal/Work에 있던 내용을 Guide/Playbook으로 승격한다.

## 활용 예시
- 릴스에서 본 N8N 에러 처리 팁을 캡처 → `00-Inbox`에 저장 → 실제로 두 번 이상 적용해봄 → `20-Shared-Knowledge/21-Guides/G-N8N-Error-Handling.md`로 승격
- 클라이언트 미팅 내용을 `12-Meetings/M-2026-05-05-Client-Clinic-A.md`로 기록 → 상위 `P-Client-Clinic-A` 허브 노트에 링크 → 프로젝트 진행 상황을 한 곳에서 파악
- 매일 저녁 `31-Journal`에 하루 배운 것 기록 → 주간 정리 시 반복해서 언급된 아이디어만 골라 `32-Learning`이나 Guide로 승격

## 주의사항
- 구조를 먼저 완벽하게 만들려고 하면 시작이 늦어진다. `00-Inbox`에 일단 캡처하고, 주간 정리 때 분류하는 흐름이 더 중요하다.
- Personal의 날것 메모를 검증 없이 바로 Shared-Knowledge로 옮기면 신뢰도가 떨어진다. 반드시 "두 번 이상 썼다" 기준을 거친 뒤 승격한다.

## 출처

- [https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149](https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149)
