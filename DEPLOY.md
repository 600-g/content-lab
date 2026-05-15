# aiskillbox 배포 가이드 — aiskillbox.600g.net

> **중요**: 현재 cloudflared는 **Token 방식 (Remotely-managed)** 으로 동작 중.
> 모든 ingress 설정은 Cloudflare 대시보드에서 관리되며, **sudo / config.yml 수정 불필요**.
>
> 진단 결과:
> - Tunnel UUID: `06005a94-2c00-4baa-9b26-600360259fd2`
> - 실행 위치: `/Library/LaunchDaemons/com.cloudflare.cloudflared.plist` (root, token 모드)
> - 기존 라우트: `api.600g.net` → `localhost:8000` (Cloudflare 대시보드에 정의됨)

---

## 1. .env 세팅 (완료된 상태)

✅ `.env` 이미 작성됨. 검증:
```bash
cd ~/Developer/my-company/content-lab
grep -c "API_KEY=" .env
# 2 (GEMINI + NOTION)
```

---

## 2. Notion DB 연결 (Notion 앱에서)

DB 페이지 우측 상단 `⋯` → Connections → `aiskillbox 연동 api` 추가.

검증:
```bash
cd ~/Developer/my-company/content-lab && source .env
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer ${NOTION_API_KEY}" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"value":"database","property":"object"}}' \
  | python3 -m json.tool | head -30
# results 배열에 두근 스킬 DB 보이면 OK
```

---

## 3. LaunchAgent 로드 (Flask 서버 상시 가동)

```bash
launchctl load -w ~/Library/LaunchAgents/com.doogeun.aiskillbox.plist

# 첫 부팅: venv + 의존성 자동 설치 (5분 정도, playwright chromium 500MB)
tail -f ~/Developer/my-company/content-lab/logs/launchd_stdout.log
# "aiskillbox listening on http://0.0.0.0:5050" 보이면 OK
```

검증:
```bash
curl -s http://localhost:5050/healthz | python3 -m json.tool
# {"ok": true, "gemini_configured": true, "notion_configured": true, ...}
```

브라우저:
```bash
open http://localhost:5050
```

---

## 4. Cloudflare 대시보드에서 도메인 연결 (3분, sudo 없음)

### 4-1. Zero Trust 대시보드 접속
https://one.dash.cloudflare.com → 600g.net 계정 선택

### 4-2. 기존 터널 찾기
- 왼쪽 메뉴 **Networks → Tunnels**
- 터널 목록에서 UUID `06005a94-2c00-4baa-9b26-600360259fd2` 와 일치하는 터널 찾기 (보통 1개만 있음)
- 터널 클릭 → **Configure** 또는 카드 안의 **... 메뉴 → Configure**

### 4-3. Public Hostname 추가
- **"Public Hostname"** 탭 클릭
- **"Add a public hostname"** 버튼
- 입력:
  | 필드 | 값 |
  |------|-----|
  | Subdomain | `aiskillbox` |
  | Domain | `600g.net` |
  | Path | (비워둠) |
  | Type | `HTTP` |
  | URL | `localhost:5050` |
- **Save hostname**

### 4-4. DNS 자동 추가 확인
저장하면 Cloudflare가 **DNS CNAME 자동 생성**.

DNS 탭에서 확인:
- `aiskillbox` → `06005a94-2c00-4baa-9b26-600360259fd2.cfargotunnel.com` (Proxied)

---

## 5. 외부 검증

```bash
# DNS 전파 5초 정도 후
curl -s https://aiskillbox.600g.net/healthz | python3 -m json.tool

open https://aiskillbox.600g.net
```

iPhone Safari로도 https://aiskillbox.600g.net 접속 → 공유 → **홈 화면에 추가** → PWA로 동작.

---

## 6. iOS 단축어 (선택 — URL 공유 → 자동 수집)

1. 단축어 앱 → 새 단축어
2. **"공유 시트에서 받기"** 추가 → URL 받기
3. **"URL 내용 가져오기"** 추가:
   - 방법: POST
   - URL: `https://aiskillbox.600g.net/api/collect`
   - 본문: JSON
   - 키: `url`, 값: `[입력된 URL]`
4. **"알림 표시"** 추가 (응답 표시)
5. 저장 → 이름 "aiskillbox 수집"

이후 Safari/유튜브 앱에서 공유 → "aiskillbox 수집" 누르면 자동 수집.

---

## 7. 트러블슈팅

### `502 Bad Gateway` (외부)
- 로컬 5050 안 뜸. `curl http://localhost:5050/healthz` → 안 뜨면 LaunchAgent 확인:
  ```bash
  launchctl list | grep aiskillbox
  tail -50 ~/Developer/my-company/content-lab/logs/launchd_stderr.log
  ```

### `404` 외부에서만
- Cloudflare 대시보드에 Public Hostname 추가 안 됨, 또는 typo
- DNS 전파 대기 (보통 즉시, 최대 1분)

### Notion 401 — `unauthorized`
- DB 페이지 Connections에 인티그레이션 안 붙임
- https://www.notion.so/my-integrations 에서 `aiskillbox 연동 api` 확인 → DB 페이지에서 추가

### Playwright chromium 설치 실패
```bash
cd ~/Developer/my-company/content-lab
source venv/bin/activate
playwright install chromium
```

### LaunchAgent 첫 부팅 venv 설치 실패
`scripts/aiskillbox_start.sh` 가 자동 처리하지만 실패하면 수동:
```bash
cd ~/Developer/my-company/content-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
launchctl kickstart -k gui/$(id -u)/com.doogeun.aiskillbox
```

---

## 8. 비용

- Cloudflare Tunnel: 무료
- DNS: 600g.net 기존 활용
- LaunchAgent: 시스템 기본
- **월 0원**
