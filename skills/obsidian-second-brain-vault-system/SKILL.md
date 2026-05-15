---
name: obsidian-second-brain-vault-system
description: 이 스킬은 [옵시디언을 이용해] [개인 및 팀의 지식을 체계적으로 관리하고 재활용]한다. 이는 AI 학습과 활용의 기반이 되는 지식 자산화를 돕는다. Use when: ['- 방대한 정보와 AI 학습 자료를 효율적으로 정리하고 재활용하고 싶을 때', '- 프로젝트 문서, 회의록, 개인 아이디어를 통합적이고 체계적으로 관리하고 싶을 때', "- '두 번 이상 사용한' 지식을 매뉴얼/플레이북으로 승격하여 팀과 공유하고 싶을 때"]
origin: content-lab
metadata:
  template_version: "v1"
  category: "업무"
  grade: "S"
  difficulty: "중급"
  targets: ["공통", "클로드코드", "두근펫"]
  ai_tools: ["Claude Code", "도구무관"]
  tags: ["MCP", "CLI", "Tool Use", "자체호스팅"]
  source_urls:
    - "https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149"
  source_type: "notion"
  collected_at: "2026-05-15"
  last_updated_at: "2026-05-15"
  merge_count: 1
---

# 📦 옵시디언 기반 세컨드 브레인 볼트 시스템

> **TL;DR** — 이 스킬은 [옵시디언을 이용해] [개인 및 팀의 지식을 체계적으로 관리하고 재활용]한다. 이는 AI 학습과 활용의 기반이 되는 지식 자산화를 돕는다.

> **메타** 등급 S · 카테고리 업무 · 난이도 중급
> **도구** Claude Code, 도구무관
> **적용 대상** 공통, 클로드코드, 두근펫

---

## 🎯 When to use (언제 쓰는가)

['- 방대한 정보와 AI 학습 자료를 효율적으로 정리하고 재활용하고 싶을 때', '- 프로젝트 문서, 회의록, 개인 아이디어를 통합적이고 체계적으로 관리하고 싶을 때', "- '두 번 이상 사용한' 지식을 매뉴얼/플레이북으로 승격하여 팀과 공유하고 싶을 때"]

## 🔑 How it works (작동 원리)

Work, Shared-Knowledge, Personal 세 가지 핵심 폴더 구조를 기반으로 정보를 분류하고 관리합니다. DM, 릴스 등 다양한 소스에서 얻은 정보를 00-Inbox 또는 31-Journal로 캡처한 뒤, 주간 정리를 통해 관련 프로젝트(10-Work) 또는 공유 지식(20-Shared-Knowledge)으로 옮깁니다. 반복 사용되는 지식은 Guide/Playbook으로 '승격'하여 재사용성을 높입니다. 제목 접두사(예: `G-`, `PB-`, `R-`, `J-`, `L-`), 메타데이터, 링크/태그 활용 꿀팁을 적용하여 효율성을 극대화합니다.

## 🛠 Steps (적용 단계)

['1) **기본 볼트 구조 생성**: Obsidian Vault 내에 `00-Inbox`, `10-Work`, `20-Shared-Knowledge`, `30-Personal`, `Attachments`, `Templates` 폴더를 생성합니다.', '2) **영역별 하위 폴더 설계**: 각 메인 폴더(Work, Shared-Knowledge, Personal) 내에 프로젝트(`11-Projects`), 미팅(`12-Meetings`), 가이드(`21-Guides`), 저널(`31-Journal`), 학습(`32-Learning`) 등 목적에 맞는 하위 폴더를 만듭니다.', '3) **정보 캡처 및 저장**: 모든 외부 정보(릴스, DM 링크 등)는 `00-Inbox` 또는 `31-Journal`에 우선 저장합니다. PC에 AI 즐겨찾기 폴더를 만들어 중요 자료를 백업합니다.', '4) **주간 운영 루틴 실행**: 매주 `00-Inbox`를 검토하여 실행이 필요한 내용은 `10-Work/11-Projects`로, 재사용 가능한 지식은 `20-Shared-Knowledge`로 옮깁니다.', '5) **지식 승격 규칙 적용**: 동일한 내용이 두 번 이상 사용되었다고 판단되면, `Personal`이나 `Work` 영역의 내용을 `20-Shared-Knowledge`의 `Guide`나 `Playbook`으로 승격시킵니다.', '6) **꿀팁 적용**: 파일명에 접두사(예: `G-`, `PB-`, `R-`)를 사용하여 타입을 구분하고, 공유 전제 지식에는 작성자/날짜/적용 범위 등의 메타데이터를 상단에 고정합니다. 개인적인 메모는 `#private` 태그를 활용합니다.']

## 💡 Examples (예시)

```
# Obsidian Vault Structure Example:
Vault/
├── 00-Inbox/
├── 10-Work/
│ ├── 11-Projects/
│ │ ├── P-AINOW-Youtube/
│ │ └── P-Client-Clinic-A/
│ ├── 12-Meetings/
│ │ └── M-2026-05-05-Client-Clinic-A/
│ └── 13-Assets/ # 재사용 가능한 자료 (스크립트, 템플릿 등)
├── 20-Shared-Knowledge/
│ ├── 21-Guides/ # HOW: 실행 방법
│ │ └── G-Instagram-Reels-Playbook.md
│ ├── 22-Playbooks/ # 전략/시나리오
│ │ └── PB-Launch-Sequence.md
│ └── 23-Research/ # 리서치/요약
│     └── R-AI-Agents-2026Q1.md
├── 30-Personal/
│ ├── 31-Journal/
│ │ └── J-2026-05-05.md
│ └── 32-Learning/
│     └── L-Book-Building-A-Second-Brain.md
└── Attachments/
```

## 🏢 두근 환경 적용

['- (필수 1) 원본의 Obsidian 시스템은 Notion DB와 함께 활용하여 핵심 프로젝트/지식 관리는 Notion, 세부 작업/개인 기록 및 빠른 메모는 Obsidian으로 분담하여 효율성을 높일 수 있습니다.', '- (필수 2) 클로드코드: 개발 중인 AI 스킬, 프롬프트, MCP 개발 노트를 20-Shared-Knowledge/21-Guides 또는 10-Work/11-Projects에 체계적으로 기록하고 관리하여 AI 에이전트 개발 효율성을 높일 수 있습니다.', '- (필수 2) 두근펫: 프로젝트 기획, 개발 미팅, 에셋 관리 문서를 10-Work 영역에 저장하고, 팀 내 SOP나 튜토리얼은 20-Shared-Knowledge에 보관하여 협업 지식을 축적할 수 있습니다.', '- (필수 2) 공통: 모든 팀원이 학습한 AI 지식이나 새로운 도구 사용법을 20-Shared-Knowledge에 공유하고, 개인 학습 노트는 30-Personal에 기록하여 지식 자산화를 촉진할 수 있습니다.']

## ⚠️ Caveats (주의사항)

['- 초기 설정에 시간이 소요될 수 있으며, 일관된 규칙 유지를 위한 꾸준한 노력이 필요합니다.', '- Obsidian은 마크다운 기반이므로, 복잡한 테이블이나 특정 서식 요구 시 Notion 등 다른 도구와의 연동을 고려해야 합니다.', '- 팀 단위로 확장 시, 공유 지식의 업데이트 및 동기화 방안을 별도로 수립해야 합니다 (예: Obsidian Sync 유료, Git, 외부 클라우드 연동).']

## 📎 Sources (출처)

- [https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149](https://waiting-drug-536.notion.site/x-2-352d86104de280d38258fefa2c024cbf?pvs=149)

---

## 메타 정보

- 최초 수집: 2026-05-15
- 마지막 갱신: 2026-05-15
- 합병 횟수: 1회
- 템플릿: v1 (TEMPLATE.md)
- 자동 생성: 두근컴퍼니 콘텐츠랩 v4.0
