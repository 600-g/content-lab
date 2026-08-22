---
name: codex-pet-status-system
description: OpenAI Codex 데스크톱 앱 내장 플로팅 AI 동반자(Pet) UI를 활용해 Codex의 현재 상태(Running/Waiting/Review)를 한눈에 파악하고, hatch-pet 스킬로 커스텀 캐릭터를 제작해 멀티태스킹 인지 부담을 해결하는 워크플로우 가이드
origin: content-lab
sources:
  - https://resonant-frog-df5.notion.site/Codex-Pet-AI-35c3a1a3234381fb9b8bd2ca7adb8d29
---

# Codex Pet — AI 펫 제작 & 상태 시스템

## 이게 뭔가요?

OpenAI Codex Desktop 앱 내장 플로팅 AI 동반자 UI. 작은 동물의 행동 상태로 **Codex가 지금 무엇을 하고 있는지 직관적으로 표시**.

### 3가지 핵심 상태
- 🏃 **Running** — 작업 진행 중 → 다른 업무 전환 OK
- ⏳ **Waiting** — 사용자 입력 대기 → 빠르게 확인 필요
- ✅ **Review** — 작업 완료, 리뷰 요청 → 결과물 확인 타이밍

## 따라하기

### Step 1. Codex Desktop 앱 설치 (CLI 아님)
```bash
npm i -g @openai/codex
codex app
# 또는 macOS:
brew install --cask codex
```

### Step 2. Pet 활성화
```
1. 최신 Codex 업데이트
2. 입력창에 /pet 입력 → 펫 토글
3. 또는 Settings → Appearance → Pets
```

### Step 3. hatch-pet으로 커스텀 펫 만들기
```
$skill-installer hatch-pet
# Cmd+K → "Force Reload Skills"
$hatch-pet create a new pet inspired by my recent projects
```

예시:
- `$hatch-pet 내 최근 Rust 코드 스타일 기반 펫` → Crab 캐릭터
- `$hatch-pet 실험실 가운을 입은 카피바라`
- `$hatch-pet 픽셀 스타일 검은 고양이, 노란 눈`

### Step 4. 스프라이트 규격 (hatch-pet 자동 처리)
- 전체 크기: 1536 × 1872
- 셀 크기: 192 × 208
- 8 × 9 grid, WebP, 투명 배경
- 상태: idle, running-right/left, waving, jumping, failed, waiting, running, review

### Step 5. 설치 경로
```
~/.codex/pets/[펫이름]/spritesheet.webp
~/.codex/pets/[펫이름]/pet.json
```
설정값: `custom:[펫이름]` → 앱 재실행 후 `/pet`

## 주의사항

- Codex CLI 버전은 미지원 — Desktop 앱만
- ChatGPT 유료 구독 필수 (Plus $20+)
- 커스텀 펫 제작 시 외부 IP(디즈니·포켓몬) 표절 금지
- `hatch-pet`은 [openai/skills](https://github.com/openai/skills) 공식 스킬 (커뮤니티 스킬은 보안 검토)

## 출처
- [Codex Pet 가이드](https://resonant-frog-df5.notion.site/Codex-Pet-AI-35c3a1a3234381fb9b8bd2ca7adb8d29)
- [openai/skills GitHub](https://github.com/openai/skills)
