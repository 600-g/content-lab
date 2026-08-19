---
name: hyperframes-url-to-video
description: HyperFrames + Claude Code로 웹사이트 URL 한 줄만 던지면 광고 영상까지 자동 제작하는 HTML→MP4 변환 프레임워크. 인스타 릴스·틱톡·제품 소개·브랜드 광고 다양한 포맷을 슬래시 명령 한 줄로, Suno AI로 BGM 자동 추가까지
origin: content-lab
sources:
  - https://resonant-frog-df5.notion.site/HyperFrames-Claude-3503a1a3234380b685bddfa2931f3665
---

# URL → 광고영상+BGM 자동 제작 (HyperFrames)

## 이게 뭔가요?

HTML → MP4 자동 변환 프레임워크. Claude에게 웹사이트 URL 던지면 디자인 분석부터 영상 완성까지 자동.

| 종류 | 길이 | 포맷 |
|---|---|---|
| 인스타 릴스/스토리 | 10~15초 | 1080 × 1920 세로 |
| 틱톡 광고 | 10~15초 | 1080 × 1920 세로 |
| 제품 소개 영상 | 30~60초 | 1920 × 1080 가로 |
| 브랜드 광고 | 15~30초 | 원하는 포맷 |

## 따라하기

### STEP 1. HyperFrames 셋업

Claude에게 한 줄:
```
HyperFrames 깃헙 레포 [URL] 를 내 프로젝트에 설치하고 셋업해줘.
Claude Code 슬래시 명령으로 /website-to-hyperframes 가 동작하도록.
```

### STEP 2. Claude Code에서 한 줄 명령

```
/website-to-hyperframes https://원하는사이트.com 15초짜리 인스타 광고 만들어줘
```

Claude가 프리뷰 URL 반환 → 브라우저에서 확인.

### STEP 3. 상세 프롬프트 (제품 정보 포함)

```
/hyperframes 사용해서 영상 만들어줘.

제품 : claudeasy
설명 : 개발을 몰라도 자동화를 만들어주는 웹앱.
핵심 기능 : 200개 넘는 하네스 임베드, 오케스트레이션이 알아서 대답,
          깃헙 트렌드 실시간 모니터링.
타겟 : 비전공자 / 클로드 초보.
길이 : 15초.
프로젝트 path: [본인 프로젝트 경로]
```

### STEP 4. MP4 저장
Claude가 만들어준 웹페이지에서 Export → 다운로드.

### STEP 5. Suno AI BGM (선택)
사이트: https://suno.com (무료 하루 5곡)

**BGM 프롬프트 예:**
```
cinematic ambient, minimal piano, no vocals, soft, premium feel, 30 seconds
upbeat electronic, corporate, motivational, no lyrics, clean
J-pop rock, anime opening, energetic, female vocal, refreshing, 1 minute
```

**활용 팁**: 1막(도입)·2막(전개)·3막(CTA)별로 다른 BGM으로 분위기 전환.

## 주의사항

- 저작권 — 본인 웹사이트만 사용 (타사 URL로 광고 제작 X)
- HyperFrames 셋업은 Claude Code 권한 필요
- Suno 무료 5곡/일 한도 — 대량은 Suno Pro $10/월
- AI 생성 영상의 톤 검수 필수 — 첫 5개는 사람 검수
- 1080×1920 세로 영상 실제 앱 미리보기 필수
- Suno 한국어 발음 어색 — 영어 가사 또는 Instrumental 권장
- Suno 무료는 상업 사용 제한 — 광고용은 Pro 라이선스 확인

## 출처
- [HyperFrames × Claude 가이드](https://resonant-frog-df5.notion.site/HyperFrames-Claude-3503a1a3234380b685bddfa2931f3665)
- [Suno AI](https://suno.com)
