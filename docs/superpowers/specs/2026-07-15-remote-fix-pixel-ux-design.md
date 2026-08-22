# aiskillbox 원격 진단·수정 + 픽셀 UX 설계 (2026-07-15)

## 목표

1. 스크랩/파이프라인 실패를 **외부(폰)에서 즉시 인지** — Web Push + healthz 확장
2. 자연어 채팅으로 **코드 수정까지 위임** — Claude Code(`claude -p`, Max 플랜) 에스컬레이션
3. UI 전면 리스타일 — **픽셀+디지털 분위기, 본문은 Pretendard** (가독성 우선)

## 1. 실패 알림 (외부 체크)

- `app.py` 워커: 잡이 `error` 로 끝나면 `scripts/push.py:send_push()` 로 실패 알림
  (제목: `❌ 스킬화 실패`, 본문: URL + 한글 사유, 클릭 → `/?diag=<job_id>` 채팅 자동 진단)
- `static/sw.js` notificationclick 이 data.url 로 열기 (기존 구현 확인 후 필요 시 보강)
- `/healthz` 에 `last_failure: {job_id, url, error_ko, at}` 추가 — 112 모니터 등 외부 체커용

## 2. Claude Code 에스컬레이션 (자연어 수정)

- `scripts/chat/fix_runner.py` (독립 CLI, 서버 프로세스와 분리):
  1. 시작 전 코드 스냅샷 (app.py, scripts/, templates/, static/ → logs/fix_snapshots/<ts>/)
  2. `claude --dangerously-skip-permissions --model sonnet -p <가드레일 프롬프트>` (cwd=content-lab, 타임아웃 15분)
  3. 검증: `py_compile` 전체 + (실패 URL 있으면) scrape-only 재시도
  4. 실패 시 스냅샷 대비 변경 파일만 원복 (신규 생성 파일 삭제 포함)
  5. 성공 시 `launchctl kickstart -k` 재기동, 완료/실패 Web Push
  6. 상태를 `logs/fix_jobs.json` 에 기록 (single-flight 락: 동시 1개)
- `scripts/chat/tools.py`: `escalate_fix(instruction)` (mutating, PIN) + `fix_status()` (조회) 등록
- `engine.py` 시스템 프롬프트: "코드 본체 금지" → "직접 수정 금지, escalate_fix 로 위임" 으로 변경
- `routes.py`: `/api/fix/status` (UI 배너용)
- 분리 실행 이유: fix 성공 시 서버 재기동이 fix 프로세스 자신을 죽이면 안 됨 → `Popen(start_new_session=True)`

## 3. 픽셀+디지털 UX (본문 Pretendard)

- 본문/입력/채팅 텍스트: **Pretendard** (jsdelivr CDN) — 가독성 유지
- 픽셀 분위기 요소만: 로고·상태 뱃지·숫자 라벨에 픽셀 폰트(Galmuri11), 각진 모서리(2~6px),
  하드 오프셋 섀도(4px 4px 0), 네온 시안/마젠타/라임 포인트, 도트그리드 배경 + 은은한 스캔라인,
  잡 상태 픽셀 뱃지(▶ RUNNING / ✔ DONE / ✖ FAIL), 입력창 블링킹 커서, 채팅 = 터미널 창 스타일
- 기능 변경 없음 — 기존 class 구조 유지, style.css 중심 리스타일 + index.html 소폭

## 검증

- `python -m py_compile app.py scripts/**/*.py`
- `launchctl kickstart` 후 `curl /healthz`
- UI: 로컬 렌더 확인 (build_id 캐시 무효화로 강제 새로고침 불필요)

## 리스크

- 공개 도메인에서 코드 수정 트리거 → PIN 세션 필수 (기존 safety 게이트 재사용)
- git 미커밋 변경 존재 → 롤백은 전역 reset 금지, fix 가 건드린 파일만 원복
- launchd PATH 에 /opt/homebrew/bin 포함 확인됨 → claude CLI 실행 가능
