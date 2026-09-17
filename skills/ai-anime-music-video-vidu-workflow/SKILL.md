---
name: ai-anime-music-video-vidu-workflow
description: 이 스킬은 **Vidu(GPT Image 2)**, **Suno**, **CapCut**을 조합해 캐릭터 일관성을 유지한 AI 애니메이션 뮤직비디오를 처음부터 끝까지 제작하는 6단계 워크플로우입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 콘텐츠
ai_tools: ["GPT", "CapCut"]
sources:
  - https://vaulted-decade-3b2.notion.site/AI-361f563cd706808ba6d7e626f0f159a4?pvs=149
---

# AI 애니 뮤비 제작하기

💡 이 스킬은 **Vidu(GPT Image 2)**, **Suno**, **CapCut**을 조합해 캐릭터 일관성을 유지한 AI 애니메이션 뮤직비디오를 처음부터 끝까지 제작하는 6단계 워크플로우입니다.

## 이게 뭔가요?
이 스킬은 **Vidu** (GPT Image 2 모델 탑재) 와 **Suno**, **CapCut** 을 조합해 캐릭터 일관성을 유지하는 AI 애니메이션 뮤직비디오를 제작하는 전체 워크플로우입니다. 캐릭터 이미지를 만들고, 레퍼런스로 등록한 뒤, 같은 캐릭터로 여러 씬 이미지를 생성하고, 이를 영상으로 변환한 다음 음악과 편집을 더해 완성된 뮤비를 만드는 6단계 파이프라인입니다.

핵심은 Vidu 의 **Create References** 기능입니다. 한 번 등록한 캐릭터를 @태그로 소환하면 어떤 장면을 만들어도 동일한 얼굴·의상·헤어가 유지됩니다. 이미지 생성부터 영상, 음악, 편집까지 하나의 흐름 안에서 처리하는 것이 이 워크플로우의 특징입니다.

💰 유료 필요: Vidu (이미지/영상 생성 크레딧), Suno (음악 생성)
✅ 무료 대안: 두 서비스 모두 가입 시 무료 크레딧을 제공하므로 소규모 테스트는 무료 크레딧만으로 가능. 캐릭터 이미지 생성만 놓고 보면 Leonardo AI, Bing Image Creator 로도 대체할 수 있음.

## 따라하기

### 전체 워크플로우 요약
| 단계 | 작업 | 툴 |
|---|---|---|
| 1 | 캐릭터 이미지 생성 | Vidu (GPT Image 2) |
| 2 | 캐릭터 레퍼런스 등록 | Vidu (Create References) |
| 3 | 씬 이미지 생성 | Vidu (GPT Image 2) |
| 4 | 영상 생성 | Vidu Q3 (I2V / R2V) |
| 5 | 음악 생성 | Suno |
| 6 | 최종 편집 | CapCut |

1. **캐릭터 이미지 만들기 (Vidu 이미지 탭)**
   - Vidu 접속 → 이미지 탭 클릭
   - 모델: GPT Image 2 선택
   - 해상도: 1080p / 비율: 1:1 로 설정 후 생성
   - 프롬프트 예시 (하루 — 빛의 마법소녀)

```
A magical girl named Haru, full body front view, standing pose. Long white hair with soft purple gradient at the tips, large sparkling eyes with purple and pink irises, white and gold magical girl uniform with sailor-style collar, pink ribbon on chest, glowing star wand in right hand. Soft light aura surrounding her. Clean white background. Japanese anime style, detailed illustration, high quality, 1080p.
```

   - 프롬프트 예시 (레이 — 어둠의 마법소녀)

```
A magical girl named Rei, full body front view, standing pose. Long black hair with deep red gradient at the tips, sharp and intense eyes with red and black irises, black and silver dark magical girl uniform with gothic details, black feather ornament on shoulder, dark energy orb in left hand. Dark purple aura surrounding her. Clean white background. Japanese anime style, detailed illustration, high quality, 1080p.
```

   - 팁: 정면, 측면, 후면 3가지 각도로 뽑아두면 레퍼런스 등록 시 일관성이 훨씬 좋아진다.

2. **캐릭터 레퍼런스 등록 (Create References)**
   - Vidu → 자료 탭 → 나의 참고 자료 클릭
   - 십자 버튼을 눌러 캐릭터 이미지 업로드
   - 캐릭터 이름 설정 (예: 마법하루, 마법레이)
   - 확인을 누르면 등록 완료
   - 팁: 레퍼런스를 등록하면 어떤 장면을 만들어도 같은 캐릭터가 나온다. 교복 버전, 마법소녀 버전을 따로 등록해두면 더 편하다.

3. **씬 이미지 생성 (GPT Image 2)**
   - Vidu 이미지 탭 → 참고 자료-이미지 변환 선택
   - 등록한 캐릭터 레퍼런스를 @태그로 소환
   - 원하는 장면 설명 프롬프트 입력
   - 프롬프트 예시 (등교 장면)

```
@마법하루 @마법레이 두 여고생이 벚꽃 흩날리는 일본 주택가 골목길을 나란히 걸어가고 있다. 교복 차림, 따뜻한 아침 햇살, 서로 바라보며 미소 짓는 장면. 일본 애니메이션 스타일, 고퀄리티, 16:9.
```

4. **영상 생성 (Vidu Q3)**
   - 생성한 씬 이미지를 시작 프레임으로 활용
   - 사진으로 영상 생성 (I2V) 탭 선택
   - 모델: Vidu Q3 / 시간: 최대 16초 / 해상도: 1080p / 시네마틱 모드
   - 원하는 동작과 분위기 프롬프트 입력 후 생성
   - 프롬프트 마지막에 반드시 아래 문구를 추가한다 (안 그러면 자동으로 배경음악이 붙는다)

```
NO MUSIC. NO BACKGROUND MUSIC.
```

   - 크레딧 소요량: 이미지 생성 약 6 크레딧, 16초 영상 생성 약 90 크레딧. 처음 가입 시 무료 크레딧 제공.

5. **음악 생성 (Suno)**
   - Suno 접속 → 가사 + 장르 입력
   - 장르 프롬프트 예시

```
J-pop rock, anime opening, pop-punk influence, energetic, upbeat, funk rhythm guitar, driving bass, fast acoustic drums, catchy synth, clear female vocal, nostalgic melody, refreshing, short 1 minute song
```

6. **최종 편집 (CapCut)**
   - 생성된 영상 클립들을 CapCut에 불러오기
   - BGM 타이밍에 맞춰 클립 배치
   - 자막, 효과 추가 후 완성
   - 팁: 1막(일상)은 잔잔한 피아노, 3막(전투)은 강렬한 오케스트라로 분위기 전환을 주면 뮤비 느낌이 살아난다.

## 활용 예시
- 마법소녀 캐릭터 2명(하루, 레이)의 등교 장면을 만들고 싶다면 → 위 캐릭터 프롬프트로 정면/측면/후면 이미지를 뽑아 레퍼런스로 등록 → @마법하루 @마법레이 태그로 벚꽃길 씬 프롬프트 입력 → I2V로 16초 영상 변환 → NO MUSIC 문구 필수 추가.
- 오프닝/엔딩 뮤비 전체를 제작한다면 → 6단계를 반복해 일상 파트(1막)와 전투 파트(3막) 씬을 각각 생성한 뒤, CapCut에서 Suno로 만든 BGM에 맞춰 컷 편집.
- 두근 환경 적용: Vidu·Suno는 무료 크레딧으로 소규모 테스트가 가능하고, 부족하면 유료 크레딧을 충전한다. 편집 단계(CapCut)는 무료로 그대로 사용 가능.

## 주의사항
- I2V 영상 생성 프롬프트에 `NO MUSIC. NO BACKGROUND MUSIC.` 을 빼먹으면 자동으로 배경음악이 삽입되어 편집 단계에서 다시 제거해야 하는 번거로움이 생긴다.
- 크레딧 소모가 크다 (16초 영상 1개당 약 90 크레딧) — 무료 크레딧 소진 여부를 먼저 확인할 것.
- 캐릭터 레퍼런스를 정면 각도만 등록하면 다른 각도 씬에서 캐릭터 일관성이 깨질 수 있으니 3방향 이미지를 미리 준비할 것.

## 출처

- [https://vaulted-decade-3b2.notion.site/AI-361f563cd706808ba6d7e626f0f159a4?pvs=149](https://vaulted-decade-3b2.notion.site/AI-361f563cd706808ba6d7e626f0f159a4?pvs=149)
