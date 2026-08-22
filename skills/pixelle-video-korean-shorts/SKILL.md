---
name: pixelle-video-korean-shorts
description: 중국 오픈소스 AI 영상 자동 생성 툴 Pixelle-Video의 한국어 패치 + Gemini 이미지 패치 통합 설치 가이드. GPU 없이 클라우드 API만으로 한국 숏폼 바이럴 스크립트 스타일 세로 영상을 자동 생성 (TTS 자동 한국어)
origin: content-lab
sources:
  - https://resonant-frog-df5.notion.site/Pixelle-Video-Gemini-3573a1a32343817196bec934ee86fb5f
---

# AI 세로영상 자동생성 (Pixelle + Gemini)

## 이게 뭔가요?

**Pixelle-Video (AIDC-AI 오픈소스) 한국어 세팅 + 한국 숏폼 바이럴 스크립트 + 한국어 TTS + Gemini 이미지 패치** 통합 가이드.

### 3가지 핵심
- ✅ **한국어 UI + 숏폼 바이럴 스크립트 스타일** (500+ 항목 한글 번역)
- ✅ **한국어 TTS 자동 설정** (`ko-KR-SunHiNeural`)
- ✅ **GPU 없이 클라우드 API만으로** 이미지·영상 생성

### 이미지·영상 방식 비교

| 방식 | 이미지 | 영상 | 비고 |
|---|---|---|---|
| RunningHub (기본) | ✅ | ✅ | 유료 크레딧 (월 $9) |
| Gemini API (패치) | ✅ | ❌ | 무료 티어, 영상은 RunningHub |
| ComfyUI 로컬 | ✅ | ✅ | GPU 필수 |

**추천 조합**: 이미지는 Gemini (무료), 영상은 Veo 3 또는 RunningHub.

## 따라하기 (Claude Code 방식)

### STEP 1. API 키 준비

| 키 | 용도 | 발급 |
|---|---|---|
| LLM (1개 필수) | 스크립트 생성 | Claude/ChatGPT/DeepSeek/Ollama |
| RunningHub | 이미지 + 영상 | runninghub.ai |
| Gemini | 이미지만 (RunningHub 대체) | aistudio.google.com |

RunningHub와 Gemini 중 **하나만 있어도 OK**. 영상 만들려면 RunningHub 필요.

### STEP 2. 설치 + 한국어 패치 (Claude에게)

```
아래 순서대로 실행해줘.

1. Pixelle-Video 설치
git clone https://github.com/AIDC-AI/Pixelle-Video.git [내_작업폴더]/Pixelle-Video
cd [내_작업폴더]/Pixelle-Video
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

2. 한국어 패치
git clone https://github.com/junsungkim-lab/pixelle-video-korean-patch.git [내_작업폴더]/pixelle-video-korean-patch
cd [내_작업폴더]/pixelle-video-korean-patch/korean_patch
chmod +x install.sh
./install.sh [내_작업폴더]/Pixelle-Video
```

### STEP 3. config.yaml (RunningHub 방식)

```yaml
llm:
  api_key: "여기에_API키"
  base_url: "https://api.anthropic.com/v1/"
  model: "claude-sonnet-4-6"
  # 또는 ChatGPT: base_url: "https://api.openai.com/v1", model: "gpt-4o"
  # 또는 Ollama: base_url: "http://localhost:11434/v1", model: "llama3.2"

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

### STEP 3-B. config.yaml (Gemini 방식 — 이미지만)

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

### STEP 4. Gemini 이미지 패치 (Gemini 방식 시)

```
cd [내_작업폴더]/pixelle-video-korean-patch/gemini_patch
chmod +x install.sh
./install.sh [내_작업폴더]/Pixelle-Video
```

### STEP 5. 실행

```
cd [내_작업폴더]/Pixelle-Video
source .venv/bin/activate
streamlit run web/app.py
```

브라우저 `http://localhost:8501` → 우측 상단 🌐 → 한국어.

## 최종 체크리스트

- [ ] Pixelle-Video 클론 + Python 환경 완료
- [ ] `config.yaml` LLM API 키 입력
- [ ] `config.yaml` RunningHub 또는 Gemini 키
- [ ] TTS voice `ko-KR-SunHiNeural`
- [ ] 한국어 패치 설치
- [ ] (Gemini 사용 시) Gemini 패치도 설치
- [ ] streamlit 실행 후 한국어 UI

## 주의사항

- Gemini 무료 티어는 일일 호출 제한 — 대량은 RunningHub 권장
- TTS `ko-KR-SunHiNeural` 외 한국어 음성은 별도 설정
- RunningHub 영상 1편 ≈ $0.10-0.30 — 대량 시 누적
- 생성 영상 저작권 — 유사 IP 라이선스 이슈 주의
- GPU 없으면 영상 로컬 생성 제한적 (M1/M2 8GB RAM 부족)
- streamlit 기본 localhost 전용 — 외부 노출 시 인증 추가

## 출처
- [Pixelle-Video 한국어 가이드](https://resonant-frog-df5.notion.site/Pixelle-Video-Gemini-3573a1a32343817196bec934ee86fb5f)
- [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video)
- [junsungkim-lab/pixelle-video-korean-patch](https://github.com/junsungkim-lab/pixelle-video-korean-patch)
