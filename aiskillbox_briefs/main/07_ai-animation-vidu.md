💡 이 스킬은 **Vidu Q3 + Suno + CapCut** 6단계 워크플로우로, 캐릭터 일관성을 유지하며 **AI 마법소녀 애니메이션 뮤직비디오**까지 직접 만드는 완전 가이드입니다.

## 이게 뭔가요?

**캐릭터 이미지 생성부터 영상·음악 제작·최종 편집까지 6단계 AI 애니메이션 파이프라인**. 핵심은 Vidu 의 **참고 자료(References) 기능**으로 캐릭터 일관성을 유지하면서 여러 씬을 연결하는 것.

전체 워크플로우:

| 단계 | 작업 | 툴 |
|---|---|---|
| 1 | 캐릭터 이미지 생성 | Vidu (GPT Image 2) |
| 2 | 캐릭터 레퍼런스 등록 | Vidu (Create References) |
| 3 | 씬 이미지 생성 | Vidu (GPT Image 2) |
| 4 | 영상 생성 | Vidu Q3 (I2V / R2V) |
| 5 | 음악 생성 | Suno |
| 6 | 최종 편집 | CapCut |

💰 유료 필요: Vidu 크레딧 (16초 영상 약 90 크레딧) · Suno 구독 (음악 생성)
✅ 무료 대안: 가입 시 무료 크레딧 제공 · Suno 무료 티어로 1분 곡 가능

## 따라하기

### STEP 1. 캐릭터 이미지 만들기 (Vidu 이미지 탭)

Vidu 접속 → 이미지 탭 → 모델: **GPT Image 2** / 해상도: 1080p / 비율: 1:1 → 생성

**프롬프트 예시 (하루 — 빛의 마법소녀)**

```
A magical girl named Haru, full body front view, standing pose. Long white hair with soft purple gradient at the tips, large sparkling eyes with purple and pink irises, white and gold magical girl uniform with sailor-style collar, pink ribbon on chest, glowing star wand in right hand. Soft light aura surrounding her. Clean white background. Japanese anime style, detailed illustration, high quality, 1080p.
```

**프롬프트 예시 (레이 — 어둠의 마법소녀)**

```
A magical girl named Rei, full body front view, standing pose. Long black hair with deep red gradient at the tips, sharp and intense eyes with red and black irises, black and silver dark magical girl uniform with gothic details, black feather ornament on shoulder, dark energy orb in left hand. Dark purple aura surrounding her. Clean white background. Japanese anime style, detailed illustration, high quality, 1080p.
```

💡 **팁**: 정면·측면·후면 3가지 각도로 뽑아두면 레퍼런스 등록할 때 일관성이 훨씬 좋아집니다.

### STEP 2. 캐릭터 레퍼런스 등록 (Create References)

1. Vidu → **자료 탭** → 나의 참고 자료 클릭
2. 십자 버튼 → 캐릭터 이미지 업로드
3. 캐릭터 이름 설정 (예: 마법하루, 마법레이) → 확인

💡 **팁**: 레퍼런스 등록 후엔 어떤 장면을 만들어도 같은 캐릭터가 나옵니다. 교복 버전·마법소녀 버전 따로 등록해두면 더 편함.

### STEP 3. 씬 이미지 생성 (GPT Image 2)

1. Vidu 이미지 탭 → **참고 자료-이미지 변환** 선택
2. 등록한 캐릭터 레퍼런스를 **@태그**로 소환
3. 원하는 장면 설명 프롬프트 입력

**프롬프트 예시 (등교 장면)**

```
@마법하루 @마법레이 두 여고생이 벚꽃 흩날리는 일본 주택가 골목길을 나란히 걸어가고 있다. 교복 차림, 따뜻한 아침 햇살, 서로 바라보며 미소 짓는 장면. 일본 애니메이션 스타일, 고퀄리티, 16:9.
```

### STEP 4. 영상 생성 (Vidu Q3)

1. 생성한 씬 이미지를 **시작 프레임**으로
2. **사진으로 영상 생성 (I2V)** 탭 선택
3. 모델: **Vidu Q3** / 시간: 최대 16초 / 해상도: 1080p / **시네마틱 모드**
4. 원하는 동작·분위기 프롬프트 입력 후 생성

💡 **중요**: 프롬프트 마지막에 반드시 `NO MUSIC. NO BACKGROUND MUSIC.` 추가. 안 그러면 자동으로 배경음악이 붙음.

**크레딧 소요량**: 이미지 생성 약 6 크레딧 / 16초 영상 약 90 크레딧 (가입 시 무료 크레딧 제공)

### STEP 5. 음악 생성 (Suno)

Suno 접속 → 가사 + 장르 입력

**장르 프롬프트 예시**

```
J-pop rock, anime opening, pop-punk influence, energetic, upbeat, funk rhythm guitar, driving bass, fast acoustic drums, catchy synth, clear female vocal, nostalgic melody, refreshing, short 1 minute song
```

### STEP 6. 최종 편집 (CapCut)

1. 생성된 영상 클립들 CapCut 으로 불러오기
2. **BGM 타이밍**에 맞춰 클립 배치
3. 자막·효과 추가 후 완성

💡 **팁**: 1막(일상)은 잔잔한 피아노, 3막(전투)은 강렬한 오케스트라로 분위기 전환을 주면 뮤비 느낌이 살아남.

## 활용 예시

- **1인 콘텐츠 크리에이터 — 오리지널 애니 단편** — 본인 캐릭터(IP) 만들어 1-3분 단편으로 인스타·유튜브 시리즈화. 충성 팬덤 구축
- **e-book·동화 작가의 비주얼 강화** — 책 캐릭터를 Vidu 로 일관되게 시각화 → 인스타 짧은 영상으로 책 홍보
- **교육 콘텐츠 (역사·과학)** — 가상 캐릭터 2명이 대화하며 개념 설명하는 짧은 클립 시리즈
- **광고·캠페인** — 브랜드 캐릭터를 만들어 매번 새 씬으로 광고 — 모델 고용 비용·촬영 시간 절감
- **개인 추억 영상화** — 가족 사진을 캐릭터로 변환 → 결혼식·생일 축하 애니메이션 클립

## 💡 아이디어

- **AI 캐릭터 IP 사업** — 본인만의 캐릭터 2-3명 등록 → 매주 새 에피소드 제작 → 굿즈·NFT·라이선싱 수익화
- **소상공인 마스코트 영상 제작 대행** — 카페·헬스장 등의 마스코트를 Vidu 캐릭터로 등록 → 매달 이벤트 영상 1편 제공 ($50-100/월)
- **유튜브 채널 운영 자동화** — 1주일에 1편씩 동일 캐릭터 시리즈로 알고리즘 푸시 받기 좋음

## 주의사항

- **크레딧 비용 빠르게 누적** — 16초 클립 = 90 크레딧. 1분 영상 ≈ 4-5클립 = 400-450 크레딧. 월 정기 구독 검토 권장
- **Vidu Q3 무음 옵션 필수** — `NO MUSIC` 안 넣으면 자동 BGM 이 붙어 Suno 음악 덮어쓰기 어색
- **캐릭터 일관성은 레퍼런스 품질에 좌우** — 3각도 등록 권장, 흐릿한 이미지는 후속 씬에서 변형 발생
- **저작권 — 캐릭터 디자인 표절 주의** — 기존 IP(세일러문·러브라이브 등) 직접 차용은 라이선스 이슈 가능

## 출처

- [AI 애니메이션 만들기 튜토리얼 (Notion)](https://vaulted-decade-3b2.notion.site/AI-361f563cd706808ba6d7e626f0f159a4)
- 관련: AI 영상 만들기 수업 / 미드저니 AI 그림책 클래스
