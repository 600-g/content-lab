---
name: claude-code-memory-md-200-lines
description: Claude Code의 MEMORY.md 자동 메모리 시스템 200줄 법칙 활용법 — 매 세션마다 AI가 스스로 학습한 사용자 패턴·선호도·반복 명령어를 첫 200줄까지만 자동 로드하는 셰프의 개인 노트 관리 원칙과 토픽 파일 분리 전략
origin: content-lab
sources:
  - https://waiting-drug-536.notion.site/4-317d86104de280078bbbe9e3bc98ff18
---

# Claude Code MEMORY.md 200줄 법칙

## 이게 뭔가요?

`MEMORY.md` = Claude Code의 자동 메모리 시스템 핵심. 셰프가 주방에서 개인적으로 적어두는 자동 메모리 파일.

### 4가지 핵심 속성

**1. 저장 위치**
- 경로: `~/.claude/projects/<프로젝트해시>/memory/`
- 팀원과 공유하는 `CLAUDE.md`와 달리 **사용자 개인 전용** (Git 공유 불가)

**2. 자동 기록**
- AI가 작업하며 발견한 유용한 패턴을 스스로 파악 → 백그라운드 자동 저장
- 자연스러운 지시: "우리는 npm 대신 pnpm 쓴다고 기억해" → AI가 요약 기록

**3. 200줄의 법칙 (가장 중요)**
> 매 세션 시작 시 Claude는 `MEMORY.md`의 **첫 200줄까지만** 자동으로 읽어 들임.

작업대(컨텍스트 윈도우) 공간 낭비 방지가 목적. 200줄 초과 시 토픽 파일로 분리.

**4. CLAUDE.md vs MEMORY.md**

| 구분 | CLAUDE.md (운영 매뉴얼) | MEMORY.md (개인 노트) |
|---|---|---|
| 작성 주체 | 사용자 직접 | Claude가 자동 |
| 로드 시점 | 매 세션 **전체** 로드 | 매 세션 **첫 200줄만** |
| 주요 용도 | 아키텍처·컨벤션·핵심 규칙 | 학습된 패턴·명령어·선호도 |
| 팀 공유 | Git 체크인 가능 | Git 체크인 불가 |

## 따라하기

### STEP 1. 위치 확인
```bash
ls ~/.claude/projects/
cat ~/.claude/projects/<프로젝트해시>/memory/MEMORY.md
```

### STEP 2. 자연스럽게 학습시키기
```
"우리는 npm 대신 pnpm 쓴다고 기억해"
"이 프로젝트는 항상 TypeScript strict 모드야"
"테스트는 vitest 로 돌리고 jest 는 안 써"
"PR 브랜치는 feature/<title> 형식으로"
/memory  # 명시적 기록
```

### STEP 3. 200줄 초과 시 토픽 파일 분리

| 토픽 | 파일명 | 내용 |
|---|---|---|
| 디버깅 | `debugging.md` | 자주 만나는 에러 + 해결법 |
| 테스트 | `testing.md` | 전략, mock 패턴 |
| 빌드/CI | `deployment.md` | 배포 명령, CI 설정 |
| DB | `database.md` | 마이그레이션, 쿼리 패턴 |
| API 통합 | `apis.md` | 외부 API 호출 패턴 |

분리 후 `MEMORY.md`는 **인덱스 + 가장 자주 쓰는 패턴**만.

### STEP 4. 월 1회 점검
```bash
wc -l ~/.claude/projects/<프로젝트해시>/memory/MEMORY.md
# 200줄 가까우면:
# 1) 오래된 항목 제거
# 2) 토픽 파일로 분리
# 3) 비슷한 항목 통합
```

### STEP 5. 효과적인 메모리 5가지 패턴
1. **"왜"를 함께 기록** — "X를 쓴다" 보다 "X를 쓴다 (이유: Y 때문)"
2. **부정형 명시** — "Z는 절대 쓰지 마라" 금지 사항도
3. **반복 명령어 단축형** — "테스트는 `pnpm test --filter=core`로"
4. **사용자 선호 톤** — "에러 메시지는 한글로", "코드 주석 최소화"
5. **프로젝트 변천사** — "이전엔 X 썼다가 Y로 마이그레이션 완료"

## 주의사항

- 200줄 법칙 절대 무시 X — 150줄 도달 시 정리 권장
- MEMORY.md는 Git 체크인 X (자동 gitignore) — 비밀번호·내부 정보 가능성
- 자동 기록 100% 정확 X — 월 1회 직접 점검
- Claude Code 전용 — Codex/Cursor/Copilot 미적용
- 민감 정보 자동 저장 주의 — 정기 검토 필수
- `.claude` 폴더 백업 권장 (시스템 재설치 시 손실)

## 출처
- [클로드코드 기초 총정리 시리즈 4편](https://waiting-drug-536.notion.site/4-317d86104de280078bbbe9e3bc98ff18)
