# 미디어 이해 단계 — 릴스·피드·자막 없는 유튜브의 "내용" 읽기 (v5.1 설계)

날짜: 2026-09-12 · 상태: 구현 중

## 문제

수집 파이프라인은 텍스트만 본다. 그래서 (2026-05 ~ 09-12 로그 전수 기준):

| 출처 | 지금 | 결과 |
|---|---|---|
| 인스타 릴스 5건 | yt-dlp 가 "login required" 로 매번 실패 → Playwright 가 **캡션만** 확보 | 캡션(계정 홍보문)으로 스킬 생성. 실사례 DdGu4P0MjXk: 영상은 "AI Office 8가지 대시보드" 인데 스킬은 "AI 정보 큐레이션 마인드셋" |
| 인스타 피드 `/p/` 4건 | `_ig_guard` 가 시도 없이 사전 차단 | 캐러셀 슬라이드에 든 본문을 통째로 버림 |
| 유튜브 | 자동자막 있으면 정상(20만 자/8초). 자막 없으면 설명문만 | 설명문만으로 스킬 생성 |
| 등급 파싱 1건 | 프롬프트가 `S-즉시적용` 표기를 가르치는데 파서는 `S` 만 인정 | S 콘텐츠가 C 로 강등돼 미등록 (08-28 fieldby) |

## 실측으로 확인된 사실 (2026-09-12)

- `instagram.com/<p|reel>/<shortcode>/embed/captioned/` 는 **로그인·쿠키·yt-dlp 없이** 200 을 주고,
  HTML 의 `"contextJSON":"…"` (JSON 문자열을 한 번 더 JSON 인코딩) 안 `gql_data.shortcode_media` 에
  캡션(`edge_media_to_caption`) · `owner.username` · `is_video` · `video_url` · `video_duration` ·
  `display_url` · 캐러셀 자식(`edge_sidecar_to_children.edges[].node`) · `accessibility_caption` 이 있다.
- 릴스 mp4(5.9MB) 는 그 `video_url` 로 바로 받아진다. Gemini Files API 업로드 → `gemini-2.5-flash-lite`
  가 8초·8k 토큰으로 음성 + 화면 자막을 정리했다. 캐러셀 5장은 inline 이미지로 7초·1.9k 토큰.
- 유튜브 URL 은 다운로드 없이 `file_data.file_uri` 로 직접 넣으면 된다 (87초 영상 11초·2.6만 토큰).
- `gemini-2.5-flash` 는 company-hq 와 같은 키라 하루 20회가 매일 첫 호출에 소진돼 있다.
  미디어 이해는 별도 쿼터인 `flash-lite` 를 1순위로 쓴다 — 단 **flash-lite 도 프로젝트당 하루 20회**다 (2026-09-13 429 실측). 분석+미디어가 한 키를 쓰면 하루 10건 안팎이 한계라 별도 프로젝트 키가 필요하다.

## 설계

### 1. `scripts/scraper/instagram_embed.py` (신규)
- `scrape(url, *, fetch=None) -> ScrapeResult`. embed 페이지 → `contextJSON` 파싱 → 캡션·작성자·길이를
  `text` 로, 미디어 목록을 `meta["media"]` 로. 실패는 `ok=False` (예외 불출) → router 가 기존 경로로 폴백.
- `meta["media"]` 항목: `{"kind": "video"|"image", "url": str, "key": "ig:<shortcode>:<idx>", "alt": str}`.
  `key` 는 캐시 키 — URL 은 서명·만료가 붙어 매번 달라지므로 쓰지 않는다.
- router: instagram 이면 embed 를 **먼저** 시도. 캡션이나 미디어가 하나라도 잡히면 채택. 실패 시에만
  기존 `_ig_guard`(피드 차단) → yt-dlp → Playwright 순서 유지.

### 2. `scripts/analyzer/media_understand.py` (신규) — 스크랩과 분석 사이의 새 단계
- `enrich(scrape_res, *, fetch=None, upload=None, generate=None, cache_path=None) -> dict`.
  `meta["media"]` 를 읽어 결과 텍스트를 `scrape_res.text` 끝에 섹션으로 덧붙인다:
  `[영상 내용 — AI 전사]` (video/youtube) · `[슬라이드 텍스트 — AI 판독]` (image, 최대 10장 한 번에).
- 영상: 다운로드(60MB 상한) → Files API resumable 업로드 → ACTIVE 대기 → generateContent.
  유튜브: 다운로드 없이 URL 을 `file_data` 로 (30분 상한).
- 모델: `flash-lite` → `flash` 순. `gemini._quota_should_skip/_quota_increment` 공유, `x-goog-api-key` 헤더,
  `thinkingBudget: 0`.
- 캐시 `logs/media_cache.json` (key → text). 재수집·합병 시 미디어 호출 0회.
- 어떤 항목이 실패해도 예외를 밖으로 내지 않는다 (gotcha 39 패턴). 결과는 `summary["stages"]["media"]`.

### 3. `scripts/scraper/youtube.py`
- 자막이 비면 `meta["media"] = [{"kind": "youtube", "url": url, "key": "yt:<id>"}]` (duration ≤ 1800s).

### 4. `scripts/analyzer/gemini.py:_validate`
- 등급이 enum 밖이어도 첫 글자가 S/A/B/C 면 그 글자로 정규화. (`S-즉시적용` → `S`, `B+` → `B`)

### 5. `scripts/collect.py`
- 스크랩 성공 직후, 본문 길이 게이트 **앞에서** `media_understand.enrich()` 호출. 붙여넣기 경로는 제외.
  미디어 텍스트가 더해지면 500자 게이트는 자연히 넘는다.

## 검증
- unittest (네트워크 0): embed 파서 · router 분기 · youtube media 플래그 · enrich(주입 fetch/upload/generate, 캐시, 실패 격리) · 등급 정규화.
- 실 URL: 이번 로그의 릴스 5건·피드 3건 재수집 → 스킬 본문에 영상/슬라이드 내용이 들어가는지 확인.

## 위험
- embed 엔드포인트는 Meta 의 임베드용 비공개 계약이라 바뀔 수 있다. 깨지면 `ok=False` 로 기존 경로에
  자동 폴백되고, 예비 경로는 이 맥의 크롬 쿠키를 쓰는 `yt-dlp --cookies-from-browser chrome` 이다.
