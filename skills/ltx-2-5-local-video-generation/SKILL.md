---
name: ltx-2-5-local-video-generation
description: 이 스킬은 구독료 없이 **내 컴퓨터 GPU**에서 LTX 2.5 모델을 돌려 영상을 무제한으로 뽑는 방법입니다. 가중치 다운로드부터 첫 영상 생성 명령어, 메모리 부족 대처법까지 그대로 따라 하면 됩니다.
origin: content-lab
grade: S
difficulty: 고급
category: 콘텐츠
ai_tools: ["ComfyUI"]
sources:
  - https://wandering-mile-86e.notion.site/LTX-2-5-3d898dec8eed813c878ecc13cc7fd3fe?pvs=149
---

# LTX 2.5 로컬 영상 생성

💡 이 스킬은 구독료 없이 **내 컴퓨터 GPU**에서 LTX 2.5 모델을 돌려 영상을 무제한으로 뽑는 방법입니다. 가중치 다운로드부터 첫 영상 생성 명령어, 메모리 부족 대처법까지 그대로 따라 하면 됩니다.

## 이게 뭔가요?

구독형 영상 생성 서비스는 회사 서버에서 영상을 뽑을 때마다 크레딧이 줄어듭니다. **LTX 2.5**는 Lightricks가 공개한 영상 생성 모델로, 가중치 파일을 내 컴퓨터에 내려받아 직접 GPU로 돌리면 몇 편을 뽑든 전기값 말고는 추가 비용이 없습니다.

라이선스는 Apache나 MIT가 아니라 Lightricks가 직접 쓴 **LTX-2.x Community License**입니다. 연 매출 1,000만 달러 미만이면 유튜브·릴스·광고 등 상업적 용도로 완전 무료입니다. 매출 1,000만 달러 이상이면 별도 유료 계약이 필요합니다. 개인이나 소규모 팀은 그냥 무료라고 보면 됩니다.

전체 구조는 부품 여러 개로 나뉩니다: 텍스트를 뜻으로 바꾸는 **Gemma 4 12B 텍스트 인코더**(LTX 전용판, 26.3GB) → 영상의 속을 만드는 **22B 트랜스포머(DiT)** → 이를 실제 그림으로 펴는 **비디오 VAE** → 소리를 더하는 **오디오 VAE**. 2.5 버전에서는 컷이 여러 개 이어져도 인물·배경·조명·목소리가 그대로 유지되는 **멀티샷** 기능이 새로 생겼고, 화질이 개선된 새 비디오 디코더, 긴 요청을 끝까지 붙드는 Gemma 4 인코더, 자동 프롬프트 보정, 프레임 수 자동 예측 기능이 추가됐습니다.

💰 유료 필요: 없음 (전기값·GPU만 소요) — 단, 받아야 할 파일이 약 66GiB이므로 디스크 100GB 이상, VRAM 여유가 필요합니다. VRAM이 부족하면 앱이 자동으로 API 모드(=남의 서버)로 넘어가므로 주의하세요.

## 따라하기

### 1. 내 컴퓨터가 되는지 확인

어느 길로 갈지가 사양을 정합니다.

| 길 | 무엇 | 필요한 VRAM | 디스크 |
|---|---|---|---|
| A. LTX Desktop | 공식 데스크톱 앱, 제일 쉬움 | NVIDIA 16GB 이상 | 160GB 이상 |
| B. ComfyUI | 노드로 연결 | 32GB 이상 전제 | 100GB 이상 |
| C. 파이썬 직접 | 명령줄, 옵션 제일 많음 | 표 없음(하드웨어마다 다름) | 66GiB + 여유 |

맥(Apple Silicon)은 LTX Desktop으로 됩니다. 여유 RAM 15GB 이상이면 로컬 생성이 가능합니다. 파이썬 길의 공통 요구 사항은 Python 3.12 이상, CUDA 12.7 이상, PyTorch 2.7 권장입니다.

### 2. 가중치 받기 (허깅페이스 게이트 통과)

LTX 2.5는 허깅페이스에서 게이트(gated) 상태라 그냥 링크만 눌러선 안 받아집니다.

1. `huggingface.co/Lightricks/LTX-2.5` 로 들어가 로그인 후 "Agree and Access"를 누릅니다.
2. 설정에서 Read 토큰을 만듭니다. 세분화(fine-grained) 토큰을 쓸 거면 **"read gated repos" 권한을 반드시 켜세요**. 이걸 안 켜서 401·403 오류가 나는 경우가 가장 흔합니다.
3. 터미널에서 토큰을 등록합니다.

```
hf auth login
```

### 3. 저장소 내려받기

```
git clone https://github.com/Lightricks/LTX-2.git
cd LTX-2
uv sync --extra natten
```

`natten`은 새 비디오 디코더를 제일 빠르게 돌리는 부품입니다. 리눅스+CUDA 전용이라 윈도우·맥에서는 자동으로 건너뛰고 다른 방식으로 대신 돌아가므로 같은 명령을 그대로 쓰면 됩니다.

### 4. 모델 부품 받기 (약 66GiB)

```
hf auth login
hf download Lightricks/LTX-2.5 \
diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors \
text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors \
vae/ltx-2.5-video-vae-bf16.safetensors \
vae/ltx-2.5-audio-vae-bf16.safetensors \
model_patches/ltx-2.5-duration-head-bf16.safetensors \
latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors \
--local-dir models/ltx-2.5
```

### 5. 첫 영상 뽑기

```
uv run python -m ltx_pipelines.distilled \
--transformer-path models/ltx-2.5/diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors \
--text-encoder-path models/ltx-2.5/text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors \
--video-vae-path models/ltx-2.5/vae/ltx-2.5-video-vae-bf16.safetensors \
--audio-vae-path models/ltx-2.5/vae/ltx-2.5-audio-vae-bf16.safetensors \
--duration-head-path models/ltx-2.5/model_patches/ltx-2.5-duration-head-bf16.safetensors \
--prompt "무대 위 기타리스트가 솔로를 연주하고, 카메라가 그 주위를 천천히 돈다" \
--num-frames 121 \
--seed 42 \
--output-path first.mp4
```

기본값은 1024×1536, 24fps입니다. `--num-frames 121`이면 24fps 기준 약 5초 분량이며, 이 옵션을 빼면 길이 예측 부품이 프롬프트를 보고 알아서 정합니다. 4K로 뽑을 때는 `--width 3840 --height 2176` 입니다(2160이 아니라 2176 — 자주 틀립니다).

### 6. 메모리가 모자랄 때

```
# bf16 체크포인트를 돌리면서 즉석에서 FP8로 낮춘다
--quantization fp8-cast --offload cpu
# 그래도 모자라면 (느려집니다)
--offload disk
```

Hopper 이상 GPU에서 fp8 체크포인트를 쓸 때는 `--quantization fp8-scaled-mm`이 더 빠릅니다. ComfyUI 쪽은 `python -m main --reserve-vram 5` 로 여유를 확보합니다.

### 7. 화질을 더 높이고 싶을 때 (DFR)

`distilled`는 8스텝짜리 제일 빠른 길입니다. 결과물 품질이 중요하면 DFR(Diffusion Fidelity Rendering)로 돌립니다. 더 오래 걸리고 VRAM을 더 씁니다.

```
uv run python -m ltx_pipelines.dfr_pipeline \
... (5번과 같은 경로들) ...
--num-frames 121 \
--output-path hq.mp4
```

⚠️ DFR도 distilled 트랜스포머를 씁니다. 전체(dev) 트랜스포머를 넣지 마세요.

### 8. 프롬프트 작성 순서 (멀티샷)

LTX 2.5의 간판 기능은 여러 컷이 이어지는 영상을 한 번에 만드는 것입니다. 이 순서로 쓰면 잘 먹힙니다.

1. 누가·무엇을 하는가 — "설상복을 입은 탐험가가 얼음 위에 앉아 상자를 연다"
2. 카메라가 어떻게 움직이나 — "카메라가 천천히 다가간다"
3. 조명·분위기 — "머리 위로 오로라가 흐른다"
4. 컷 전환 — "컷 전환 — 장갑 낀 손의 클로즈업"
5. 다음 컷의 1·2·3 — "같은 인물이 빛나는 결정을 들어 올린다"

복사해서 쓰는 프롬프트 뼈대(한 컷):

```
[인물/사물] 이 [행동] 하고,
카메라가 [움직임],
[조명/분위기] 이 [어떻게] 들어온다.
```

프롬프트 뼈대(여러 컷):

```
[와이드] 넓은 [장소] 에서 [인물] 이 [행동] 한다. [조명].
컷 전환 — [미디엄] 같은 인물의 [부분] 이 보인다. 카메라가 [움직임].
컷 전환 — [클로즈업] [핵심 사물] 이 [상태] 가 된다.
```

## 활용 예시

- 위 5번 명령의 `--prompt` 부분만 바꿔서 실행하면 → 원하는 장면의 5초 mp4가 `first.mp4`로 저장됩니다.
- 유튜브 인트로처럼 여러 장면이 이어지는 영상이 필요하면 → 8번의 멀티컷 뼈대에 맞춰 프롬프트를 쓰고 `--num-frames`를 늘려 실행하면 컷이 바뀌어도 인물·배경·조명이 이어지는 결과가 나옵니다.
- 노트북 VRAM이 부족한 경우 → 6번의 `--quantization fp8-cast --offload cpu` 옵션을 붙여 같은 명령을 실행하면 속도는 느려지지만 생성이 완료됩니다.
- 내가 만든 영상 스타일을 따라 하고 싶으면 → `LTX-2/packages/ltx-trainer` 로 `dev` 트랜스포머를 LoRA 학습시킨 뒤 `--lora-paths my_style.safetensors --lora-scale 1.0`(0.8~1.2 권장)을 첫 영상 명령에 추가합니다.

## 주의사항

- 401/403 오류 → 허깅페이스 약관 동의를 안 했거나 토큰에 "read gated repos" 권한이 없는 경우입니다. 2번을 다시 확인하세요.
- 구글 순정 Gemma 4를 넣으면 작동하지 않습니다. 반드시 LTX 전용 재학습판(`gemma4-12b-ltx-v1`)을 써야 합니다.
- LTX-2 / LTX-2.3용 파일과 섞지 마세요. 2.5는 부품이 파일별로 나뉘어 있고 Gemma 4를 쓰지만, 2.3 이하는 한 파일에 다 들어 있고 Gemma 3를 씁니다.
- LTX Desktop은 기본값이 텍스트 인코딩만 LTX 서버로 보냅니다. 한 톨도 밖으로 안 보내려면 설정에서 Local Text Encoder를 따로 받아 켜야 합니다.
- 데스크톱 앱에서 Pro를 고르면 로컬이 아니라 API 전용으로 서버에서 처리됩니다. 로컬로 도는 것은 LTX 2.5 Fast입니다.
- 4K가 안 나오면 높이 값을 확인하세요. 2160이 아니라 `--height 2176` 입니다.
- LoRA 학습 시 설정에 쓴 rank·차원과 적용할 때 설정이 다르면 오류 없이 조용히 잘못된 결과가 나오니 두 설정을 반드시 맞추세요.
- LoRA 학습은 리눅스+CUDA 13 이상, 표준 설정 기준 VRAM 80GB 이상 권장입니다. VRAM이 32GB(RTX 5090)라면 `t2v_lora_low_vram.yaml`(INT8 양자화·8비트 옵티마이저·LoRA rank 16)을 씁니다. 참조 영상·이미지는 20~30장 이상, 학습량은 500~2,000스텝이 기준입니다.

## 출처

- [https://wandering-mile-86e.notion.site/LTX-2-5-3d898dec8eed813c878ecc13cc7fd3fe?pvs=149](https://wandering-mile-86e.notion.site/LTX-2-5-3d898dec8eed813c878ecc13cc7fd3fe?pvs=149)
