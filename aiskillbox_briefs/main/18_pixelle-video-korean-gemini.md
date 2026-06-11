💡 이 스킬은 **중국 오픈소스 AI 영상 자동 생성 툴 Pixelle-Video 의 한국어 패치 + Gemini 이미지 패치** 적용 가이드로, GPU 없이 클라우드 API 만으로 **한국 숏폼 바이럴 스크립트 스타일 영상**을 자동 생성하는 셋업입니다.

## 이게 뭔가요?

**Pixelle-Video (AIDC-AI 의 오픈소스 영상 자동 생성 툴) 한국어 세팅 + 한국 숏폼 바이럴 스크립트 + 한국어 TTS 자동 설정 + Gemini 이미지 생성 패치** 통합 가이드.

**3가지 핵심**:
- ✅ **한국어 UI + 한국 숏폼 바이럴 스크립트 스타일** 적용 (500+ UI 항목 한글 번역)
- ✅ **한국어 TTS 자동 설정** (`ko-KR-SunHiNeural`)
- ✅ **GPU 없이 클라우드 API 만으로** 이미지·영상 생성 가능

### 이미지·영상 생성 방식 비교

| 방식 | 이미지 | 영상 | 비고 |
|---|---|---|---|
| **RunningHub** (원본 기본) | ✅ | ✅ | 유료 크레딧 필요 (월 $9 수준) |
| **Gemini API** (한국 패치 추가) | ✅ | ❌ | **무료 티어** 있음, 영상은 RunningHub 필요 |
| **ComfyUI 로컬** | ✅ | ✅ | **GPU 필요** |

💡 추천 조합: 이미지는 **Gemini (무료)**, 영상은 **Veo 3** 또는 **RunningHub**.

💰 유료 필요: RunningHub 월 ≈$9 (영상 생성 시) / 또는 LLM API 종량제
✅ 무료 대안: Gemini API 무료 티어 + Ollama 로컬 LLM 조합 (이미지만)

## 따라하기

### A 방법 — Claude Code 에 시키기 (추천)

**STEP 1. 사전 API 키 준비**

| 키 | 용도 | 발급 주소 | 형태 |
|---|---|---|---|
| **LLM** (스크립트 생성) — 1개 필수 | 아래 중 1개만 | Claude / ChatGPT / DeepSeek / Ollama | `sk-ant-...` / `sk-...` |
| **RunningHub** | 이미지 + 영상 — 원본 방식 | runninghub.ai | `rh-...` |
| **Gemini** | 이미지만 — RunningHub 대체 | aistudio.google.com | `AIzaSy...` |

RunningHub 와 Gemini 중 **하나만 있어도 OK**. 영상 만들려면 RunningHub 필요.

**STEP 2. 프롬프트 1 — 설치 + 한국어 패치 (복붙)**

```
아래 순서대로 실행해줘.
1. Pixelle-Video 설치
git clone https://github.com/AIDC-AI/Pixelle-Video.git [내_작업폴더]/Pixelle-Video
cd [내_작업폴더]/Pixelle-Video
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
2. 한국어 패치 설치
git clone https://github.com/junsungkim-lab/pixelle-video-korean-patch.git [내_작업폴더]/pixelle-video-korean-patch
cd [내_작업폴더]/pixelle-video-korean-patch/korean_patch
chmod +x install.sh
./install.sh [내_작업폴더]/Pixelle-Video
설치 완료 후 결과 알려줘.
```

📌 `[내_작업폴더]` 예시: `~/Documents` → `~/Documents/Pixelle-Video` 에 설치됩니다.

**STEP 3. 프롬프트 2 — config.yaml 설정 (RunningHub 방식 — 기본)**

이미지 + 영상 모두 생성하려면:

```yaml
llm:
  api_key: "여기에_API키"   # Ollama 는 아무 값이나
  base_url: "https://api.anthropic.com/v1/"   # Claude
  # base_url: "https://api.openai.com/v1"   # ChatGPT
  # base_url: "https://api.deepseek.com"   # DeepSeek
  # base_url: "http://localhost:11434/v1"   # Ollama (무료, 로컬)
  model: "claude-sonnet-4-6"
  # model: "gpt-4o"
  # model: "deepseek-chat"
  # model: "llama3.2"   # Ollama

comfyui:
  runninghub_api_key: "여기에_RunningHub_API키"
  runninghub_concurrent_limit: 1

tts:
  default_workflow: selfhost/tts_edge.json
  inference_mode: local
  local:
    voice: "ko-KR-SunHiNeural"
    speed: 1.0

image:
  default_workflow: runninghub/image_flux.json
video:
  default_workflow: runninghub/video_wan2.1_fusionx.json
template:
  default_template: "1080x1920/image_default.html"
```

**STEP 4. 프롬프트 2-B — config.yaml 설정 (Gemini 방식)**

RunningHub 없이 이미지만 생성 시. 영상은 별도로 **Veo 3** 활용 가능:

```yaml
llm:
  api_key: "여기에_API키"
  base_url: "https://api.anthropic.com/v1/"
  model: "claude-sonnet-4-6"

comfyui:
tts:
  default_workflow: selfhost/tts_edge.json
  inference_mode: local
  local:
    voice: "ko-KR-SunHiNeural"
    speed: 1.0

image:
  default_workflow: selfhost/image_flux.json
video:
  default_workflow: selfhost/video_wan2.1_fusionx.json

gemini:
  api_key: "여기에_Gemini_API키"
  model: "imagen-4.0-fast-generate-001"

template:
  default_template: "1080x1920/image_default.html"
```

**STEP 5. 프롬프트 3 — Gemini 이미지 패치 설치** (2-B 사용 시 필수)

```
아래를 실행해줘.
cd [내_작업폴더]/pixelle-video-korean-patch/gemini_patch
chmod +x install.sh
./install.sh [내_작업폴더]/Pixelle-Video
설치 완료 후 결과 알려줘.
```

**STEP 6. 프롬프트 4 — 실행**

```
[내_작업폴더]/Pixelle-Video 에서 아래를 실행해줘.
source .venv/bin/activate
streamlit run web/app.py
```

브라우저 `http://localhost:8501` 접속 → 우측 상단 **🌐 → 한국어** 선택.

### B 방법 — 직접 터미널 명령어

위 모든 명령어를 본인이 직접 실행하는 방식. 자세한 단계는 위 A 방법과 동일.

### ✅ 최종 체크리스트

- [ ] Pixelle-Video 클론 + Python 환경 설치 완료
- [ ] `config.yaml` LLM API 키 입력 (Claude / ChatGPT / DeepSeek / Ollama 중 하나)
- [ ] `config.yaml` RunningHub API 키 입력 (또는 Gemini 섹션 추가)
- [ ] `config.yaml` TTS voice `ko-KR-SunHiNeural` 설정
- [ ] 한국어 패치 설치 (`korean_patch/install.sh`)
- [ ] (Gemini 사용 시) Gemini 패치도 설치 (`gemini_patch/install.sh`)
- [ ] `streamlit run web/app.py` 실행
- [ ] UI 우측 상단 🌐 → 한국어 선택

## 활용 예시

- **유튜브 쇼츠 / 인스타 릴스 1인 운영자** — 매주 7개 숏폼 자동 생성. 본인은 기획·CTA 만 검토 → 영상 제작 시간 90% 단축
- **이커머스 셀러 — 상품 영상 양산** — 매번 신상 등록 시 1분 영상 자동 생성 → 스마트스토어·쿠팡 모두 활용. 영상 외주 비용 0
- **소상공인 — 매주 1회 매장 홍보 영상** — 카페·헬스장·미용실 매장 매주 1회 SNS 영상 자동 생성 → 인스타·틱톡 동시 업로드
- **언어 교육 콘텐츠** — 영어·일본어·중국어 학습 영상을 한국어 자막·TTS 로 자동 생성 → 어학 채널 운영
- **부동산·자동차 매물 영상** — 매물 사진+정보 → 1분 영상 자동 생성 → 인스타·당근·번개장터 동시 활용
- **AI 강의 콘텐츠** — 위 가이드 자체를 강의로 4시간 패키지 → ($100-200/회)

## 💡 아이디어

- **Pixelle-Video SaaS 호스팅** — 사용자가 직접 설치할 필요 없는 클라우드 호스팅 버전 → 월 $20-30 구독
- **한국 숏폼 톤 프롬프트 라이브러리** — 카테고리별(뷰티·패션·푸드·여행) 최적화된 프롬프트 30개 → 패키지 $30-50
- **자동 업로드 봇 결합** — Pixelle-Video → 인스타·틱톡·유튜브 동시 업로드 자동화 → 월 $50 (SaaS)
- **다국어 TTS 확장 패치** — 한국어 외에 일본어·중국어·태국어 TTS 추가 패치 → 글로벌 1인 크리에이터 타겟

## 주의사항

- **Gemini 무료 티어 한도** — 일일 호출 제한 있음. 대량 생성 시 한도 초과 가능. 본격 양산은 RunningHub 권장
- **TTS 음성 다양성 제한** — `ko-KR-SunHiNeural` 외 한국어 TTS 음성은 별도 설정 필요. Edge TTS 다른 한국어 voice 검색 권장
- **RunningHub 결제 주의** — 사용량 기반 차감. 영상 1편 ≈ $0.10-0.30. 대량 생성 시 빠르게 누적
- **저작권** — 생성한 영상에 사용된 캐릭터·배경·음악이 다른 IP 와 유사하면 라이선스 이슈 가능
- **GPU 없으면 영상 생성 제한적** — 로컬 ComfyUI 는 GPU 필수. M1/M2 Mac 일부 모델 가능하지만 8GB RAM 부족하면 어려움
- **streamlit 보안** — 외부 IP 노출 시 인증 추가 필요. 기본은 `localhost` 전용

## 출처

- [Pixelle-Video 한국어 사용 가이드 (Notion)](https://resonant-frog-df5.notion.site/Pixelle-Video-Gemini-3573a1a32343817196bec934ee86fb5f)
- 원본 GitHub: [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video)
- 한국어 패치: [junsungkim-lab/pixelle-video-korean-patch](https://github.com/junsungkim-lab/pixelle-video-korean-patch)
