---
name: jarvis-clap-trigger
description: 파이썬 없이 **간단한 복사/붙여넣기**로 스피커에서 **자비스가 응답**하는 스킬입니다.
origin: content-lab
grade: S
difficulty: 초급
category: 자동화
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://adu-jarvis-guide.vercel.app/?fbclid=PAVERFWATXAllwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpzvg3ztkoA4eASv4RN4H1XQis14j-6JGAjvFNE4SzGmf8uIf6jjq0qW1dRnp_aem_y2bJqHM9NysmUs8qrd_Whw
---

# 박수로 자비스 호출하기

💡 파이썬 없이 **간단한 복사/붙여넣기**로 스피커에서 **자비스가 응답**하는 스킬입니다.

## 이게 뭔가요?

이 스킬은 **Fish Audio S2.1 무료 API**를 활용하여, 마이크가 상시 청취하다가 **박수 두 번(0.12~0.9초 간격)**을 감지하면 지정된 텍스트를 스피커로 재생하는 자동화 기능입니다.

개발자가 아니어도 파이썬 코드를 복사하여 `jarvis.py` 파일로 저장하고, 환경 변수에 API 키만 설정하면 바로 사용할 수 있습니다. 텍스트 투 스피치(TTS) 엔진과 목소리 권한을 얻는 API 키만 있으면, 마치 아이언맨의 자비스처럼 음성 비서를 구현할 수 있습니다.

주요 AI 도구로는 Fish Audio의 TTS API와, 스크립트 실행을 위해 Claude Code CLI를 활용할 수 있습니다.

💰 **유료 필요**: Fish Audio API 키 발급이 필요합니다. (무료 티어 제공)
✅ **무료 대안**: Fish Audio의 무료 API를 사용하면 비용 없이 구현 가능합니다.

## 따라하기

**준비물**: Python 3 설치, Fish Audio API 키 발급

1.  **Python 및 라이브러리 설치**: 터미널에서 다음 명령어를 실행합니다.
    ```bash
    python3 --version
    pip install sounddevice numpy requests
    ```

2.  **`jarvis.py` 파일 생성**: 아래 코드를 복사하여 `jarvis.py`라는 이름으로 저장합니다.
    ```python
    #!/usr/bin/env python3
    """박수 두 번 → 자비스 응답 (Fish Audio S2.1 무료 API). 마이크를 상시 청취하다가 박수 2회(0.12~0.9초 간격)를 감지하면 Fish Audio TTS로 응답을 생성해 스피커로 재생한다. export FISH_AUDIO_API_KEY="발급한키" python3 jarvis.py """
    import argparse
    import os
    import queue
    import subprocess
    import sys
    import time
    from pathlib import Path
    import numpy as np
    import requests
    import sounddevice as sd

    API_URL = "https://api.fish.audio/v1/tts"
    MODEL = "s2.1-pro-free" # ← 모델 이름 한 줄. 이게 전부입니다
    OUT_DIR = Path(__file__).parent / "out" # 자비스가 읽을 대사 — 자유롭게 수정하세요
    GREETING = "네 부르셨나요."
    SCHEDULE_LINES = [
        "오늘 일정은 세 건입니다.",
        "오전 릴스 촬영. 조명은 어제보다 왼쪽이 나았습니다.",
        "오후 두 시 협업 미팅. 늦으시면 제가 대신 사과드리겠습니다.",
    ]
    # 기본 보이스 = 한국어 성우 차분 톤 (릴에서 들리는 그 목소리)
    JARVIS_VOICE_ID = "3623d139404b4756b1499559bda0e59b"
    SAMPLE_RATE = 16000
    BLOCK_DUR = 0.03 # 30ms 블록 단위로 소리 크기 계산
    CLAP_GAP = (0.12, 0.9) # 박수 2회 사이 허용 간격(초)
    REFRACTORY = 2.0 # 응답 후 재무장 대기(초)

    def load_env() -> None:
        """같은 폴더 .env 파일에서 키 로드 (FISH_AUDIO_API_KEY / FISH_VOICE_ID)."""
        env = Path(__file__).parent / ".env"
        if not env.exists():
            return
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))

    def rms(block: np.ndarray) -> float:
        return float(np.sqrt(np.mean(np.square(block))))

    def tts(text: str, api_key: str, voice: str | None) -> Path:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "model": MODEL,
        }
        body = {"text": text, "format": "mp3"}
        if voice:
            body["reference_id"] = voice
        r = requests.post(API_URL, headers=headers, json=body, timeout=60)
        r.raise_for_status()
        OUT_DIR.mkdir(exist_ok=True)
        path = OUT_DIR / f"jarvis_{int(time.time())}.mp3"
        path.write_bytes(r.content)
        return path

    def speak(text: str, api_key: str, voice: str | None) -> None:
        print(f" 🗣 {text}")
        path = tts(text, api_key, voice)
        if sys.platform == "darwin":
            subprocess.run(["afplay", str(path)], check=False)
        else:
            # windows
            os.startfile(path) # 기본 플레이어로 재생

    def main() -> None:
        load_env()
        ap = argparse.ArgumentParser(description="clap-clap → Jarvis")
        ap.add_argument("--threshold", type=float, default=0.12, help="박수 감지 문턱 (기본 0.12)")
        ap.add_argument("--device", type=int, default=None, help="입력 장치 index (--list-devices로 확인)")
        ap.add_argument("--list-devices", action="store_true")
        ap.add_argument("--voice", default=os.environ.get("FISH_VOICE_ID", JARVIS_VOICE_ID), help="보이스 ID (--voice '' 로 기본 보이스)")
        ap.add_argument("--mood", default=None, help="이모션 태그 — 예: whispering / angry")
        ap.add_argument("--text", default=None, help="일정 대신 이 문장만 읽기")
        ap.add_argument("--test-tts", action="store_true", help="박수 없이 TTS 1회 재생 (API 키 점검용)")
        args = ap.parse_args()

        if args.list_devices:
            print(sd.query_devices())
            return

        api_key = os.environ.get("FISH_AUDIO_API_KEY")
        if not api_key:
            sys.exit("FISH_AUDIO_API_KEY 환경변수가 필요합니다 (fish.audio → API Keys)")

        def build_line() -> str:
            text = args.text if args.text else GREETING + " " + " ".join(SCHEDULE_LINES)
            if args.mood:
                text = f"[{args.mood}] {text}"
            return text

        if args.test_tts:
            speak(build_line(), api_key, args.voice)
            return

        q: queue.Queue[np.ndarray] = queue.Queue()

        def cb(indata, frames, t, status):
            q.put(indata.copy())

        block = int(SAMPLE_RATE * BLOCK_DUR)
        last_clap = 0.0
        armed_until = 0.0
        print(f"👂 청취 중 — 박수 두 번 치세요 (threshold={args.threshold}, Ctrl+C 종료)")

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=block, device=args.device, callback=cb):
            while True:
                data = q.get().flatten()
                now = time.monotonic()

                if now < armed_until:
                    continue

                if rms(data) >= args.threshold:
                    gap = now - last_clap
                    if CLAP_GAP[0] <= gap <= CLAP_GAP[1]:
                        print("👏👏 감지 — 자비스 호출")
                        # 자비스 목소리가 박수로 오인되지 않게 재생 동안 감지 중단
                        speak(build_line(), api_key, args.voice)
                        last_clap = 0.0
                        armed_until = time.monotonic() + REFRACTORY
                        while not q.empty():
                            q.get_nowait()
                        print("👂 다시 청취 중")
                    else:
                        last_clap = now
                        # 같은 박수의 잔향이 2타로 읽히지 않게 짧은 데드타임
                        armed_until = now + CLAP_GAP[0]

    if __name__ == "__main__":
        main()
    ```

3.  **API 키 환경 변수 설정**: 발급받은 Fish Audio API 키를 환경 변수로 설정합니다.
    *   **macOS / Linux**: 터미널에 다음을 입력하세요. `export FISH_AUDIO_API_KEY="여기에_발급한_키"`
    *   **Windows**: 명령 프롬프트에서 `set FISH_AUDIO_API_KEY=여기에_발급한_키` 또는 PowerShell에서 `$env:FISH_AUDIO_API_KEY='여기에_발급한_키'` 를 사용합니다.

4.  **TTS 기능 테스트**: 박수 감지 없이 음성만 테스트하여 API 키와 음성 출력을 점검합니다.
    ```bash
    python3 jarvis.py --test-tts
    ```

5.  **박수 트리거 실행**: 이제 `jarvis.py`를 실행하면 마이크가 청취를 시작합니다.
    ```bash
    python3 jarvis.py
    ```

    마이크에 두 번 박수를 치면 설정된 문장이 스피커를 통해 나옵니다.

**박수 감지 조절**: 박수가 잘 감지되지 않거나, 소음에 오작동할 경우 `--threshold` 옵션으로 문턱 값을 조절할 수 있습니다. (예: `python3 jarvis.py --threshold 0.09` 또는 `python3 jarvis.py --threshold 0.3`)

**다른 장치 사용**: 마이크가 여러 개일 경우, `--list-devices` 옵션으로 장치 번호를 확인한 후 `--device` 옵션으로 지정합니다. (예: `python3 jarvis.py --device 1`)

## 활용 예시

*   **기본 응답**: 집에서 스마트폰이나 컴퓨터 앞에서 박수를 두 번 치면 "네 부르셨나요." 라고 응답합니다.
*   **일정 알림**: 스크립트 내 `SCHEDULE_LINES` 부분을 수정하여 오늘의 일정을 자비스가 대신 읽어주도록 설정할 수 있습니다.
    ```bash
    python3 jarvis.py --test-tts # 수정된 일정 문장 확인
    ```
*   **특정 문장만 읽기**: `--text` 옵션으로 특정 문장을 읽게 할 수 있습니다. (테스트 또는 알림용)
    ```bash
    python3 jarvis.py --test-tts --text "오늘 미팅은 세 건입니다."
    ```
*   **감정 표현**: `--mood` 옵션으로 다양한 감정 태그를 붙여 목소리 톤을 조절할 수 있습니다. (예: `whispering`, `angry`)
    ```bash
    python3 jarvis.py --test-tts --mood whispering --text "오늘 미팅은 세 건입니다."
    python3 jarvis.py --test-tts --mood angry --text "오늘 미팅은 세 건입니다."
    ```

## 💡 아이디어

*   **음성 명령 통합**: 박수 트리거에 특정 음성 명령을 조합하여, 음성 인식 후 Claude Code 같은 AI 모델에게 작업을 위임하는 방식으로 확장할 수 있습니다. (예: 박수 2번 후 "오늘 날씨 알려줘" 라고 말하면 날씨 정보를 음성으로 응답)
*   **개인화된 목소리**: Fish Audio의 목소리 클론 기능을 활용하여 자신의 목소리로 자비스를 구현할 수 있습니다. (10초 녹음 필요)
    ```bash
    # 환경 변수 설정 예시
    export FISH_AUDIO_API_KEY=발급한_키
    export FISH_VOICE_ID=복사한_보이스ID
    # 또는 실행 시 직접 지정
    python3 jarvis.py --voice 복사한_보이스ID
    ```

## 주의사항

*   **ModuleNotFound 에러**: `pip` 대신 `pip3`를 사용하여 라이브러리를 설치했는지 확인하세요 (`pip3 install sounddevice numpy requests`).
*   **API 키 에러 (401)**: `export` 명령어에서 API 키 앞뒤 공백이나 따옴표를 확인하고, 등호(`=`) 양옆에 공백이 없는지 점검하세요.
*   **소리 출력 문제**: 시스템의 기본 출력 장치가 올바르게 설정되었는지, 음소거 상태는 아닌지 확인하세요.
*   **박수 인식 문제**: macOS 사용 시, 시스템 설정 > 개인정보 보호 > 마이크에서 터미널 앱을 허용해야 할 수 있습니다. 계속 문제가 발생하면 `--threshold` 값을 조절해보세요.
*   **오작동 (혼자 두 번 반응)**: 박수의 잔향이 길거나 주변 소음이 박수로 오인되는 경우, `--threshold` 값을 높게 설정하거나 `CLAP_GAP` 간격을 조절해야 할 수 있습니다.

## 출처

[자비스 박수 트리거 — 풀코드 가이드](https://adu-jarvis-guide.vercel.app/?fbclid=PAVERFWATXAllwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpzvg3ztkoA4eASv4RN4H1XQis14j-6JGAjvFNE4SzGmf8uIf6jjq0qW1dRnp_aem_y2bJqHM9NysmUs8qrd_Whw)

## 출처

- [https://adu-jarvis-guide.vercel.app/?fbclid=PAVERFWATXAllwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpzvg3ztkoA4eASv4RN4H1XQis14j-6JGAjvFNE4SzGmf8uIf6jjq0qW1dRnp_aem_y2bJqHM9NysmUs8qrd_Whw](https://adu-jarvis-guide.vercel.app/?fbclid=PAVERFWATXAllwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpzvg3ztkoA4eASv4RN4H1XQis14j-6JGAjvFNE4SzGmf8uIf6jjq0qW1dRnp_aem_y2bJqHM9NysmUs8qrd_Whw)
