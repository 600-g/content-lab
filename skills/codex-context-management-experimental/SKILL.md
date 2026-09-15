---
name: codex-context-management-experimental
description: Codex의 **실험적 컨텍스트 관리 기능**을 활성화하여, 세션 중 **메모리 압축 및 수동 개입 없이** AI가 이전 대화 내용을 효과적으로 관리하도록 합니다.
origin: content-lab
grade: S
difficulty: 중급
category: 자동화
ai_tools: ["Codex"]
sources:
  - https://app.notion.com/p/3d173c7b15ad81239d3fe9e54f0c8e05?pvs=39
---

# Codex 실험 기능으로 컨텍스트 관리 자동화

💡 Codex의 **실험적 컨텍스트 관리 기능**을 활성화하여, 세션 중 **메모리 압축 및 수동 개입 없이** AI가 이전 대화 내용을 효과적으로 관리하도록 합니다.

## 이게 뭔가요?
Codex의 새로운 실험 기능인 `features.context_management.experimental_mode = true` 설정을 통해, AI가 대화 중에 메모리를 수동으로 압축하거나 보존할 내용을 직접 지정할 필요 없이 컨텍스트를 자동으로 관리하게 됩니다. 기존에는 대화가 길어지면 AI가 스스로 요약하여 압축했지만, 이 기능은 "history notes"와 "new_context" 툴, "token-budget context"를 활성화하여 이전 컨텍스트 윈도우의 정보를 검색하고 유지하는 데 도움을 줍니다. 이는 AI 작업 시 압축으로 인한 정보 손실 문제를 해결하는 데 초점을 맞추고 있습니다.

이 기능은 **Codex CLI 0.153.0** 버전부터 도입되었으며, 현재는 실험 기능으로 "몇 주 안에 기본값이 될 예정"이라고 합니다. 이 기능은 **ChatGPT Plus, Pro, Pro Lite 로그인**에서만 작동하며, Business, Enterprise, API 키 세션에서는 사용할 수 없습니다.


### 🔧 설정은 한 줄입니다

Codex 설정 파일(`config.toml`)에 다음 설정을 추가하고 새 태스크를 시작하면 기능이 활성화됩니다. 기본값은 꺼짐(disabled by default)입니다.

```toml
features.context_management.experimental_mode = true
```

| 항목 | 내용 |
|---|---|
| 파일 | `codex config.toml` |
| 기본값 | 꺼짐 (disabled by default) |
| 적용 시점 | 설정 후 새 태스크부터 |
| 추가된 버전 | Codex CLI 0.153.0 (2026-09-03) |
| 상태 | 실험 기능. "몇 주 안에 기본값이 될 예정" |

실험 기능이라는 점을 염두에 두어야 합니다.

### 📦 켜면 뭐가 달라지나

기존 방식은 대화가 길어지면 요약본으로 압축되었으나, 이 설정을 켜면 다음과 같은 세 가지가 활성화됩니다:

| 이름 | 하는 일 |
|---|---|
| history notes | 요약으로 뭉개는 대신 노트로 남겨, 쌓인 디테일이 한 덩어리로 압축되지 않도록 함 |
| new_context 툴 | 모델이 컨텍스트를 새로 여는 동작을 직접 다룸 |
| token-budget context | 컨텍스트를 토큰 예산으로 관리 |

특히 이전 컨텍스트 윈도우가 검색된다는 점이 체감될 것으로 예상됩니다. 노트에 담기지 않은 내용이라도 이전 메시지와 툴 실행 결과에서 요구사항이나 테스트 결과를 찾아올 수 있게 됩니다.

### 🔍 내 계정에서 켜지나

이 기능은 계정 요금제보다는 **로그인 방식**에 따라 작동합니다.

| 로그인 방식 | 사용 가능 여부 |
|---|---|
| ChatGPT Plus 로그인 | ⭕ |
| ChatGPT Pro 로그인 | ⭕ |
| ChatGPT Pro Lite 로그인 | ⭕ |
| Business · Enterprise | ❌ 런칭 시점 불가 |
| API 키 세션 | ❌ |
| 커스텀 프로바이더 | ❌ |
| 임시 structured 스레드 | ❌ |

API 키 등으로 Codex를 사용하는 경우, 이 설정을 넣어도 작동하지 않습니다.

### 🧩 아스트라랑 무슨 관계인가

GPT-6 Astra와 같은 날 발표되었지만, 이 컨텍스트 관리 설정은 Codex CLI 0.153.0에, Astra 관련 업데이트는 0.153.1, 0.153.2에 분리되어 있습니다. 오픈AI의 설명은 주로 Astra를 주어로 하고 있으나, 노트를 유지하고 이전 대화를 찾아오는 것은 모델의 역할이며, 해당 설정은 이를 켜는 스위치 역할을 합니다. Astra가 아닌 다른 모델에서 이 설정을 켰을 때의 동작은 문서에 명시되어 있지 않습니다.

### 📁 클로드 자산 안 버리고 옮기려면

기존 Claude Code의 지침과 스킬을 Codex로 옮기지 않고 그대로 읽어오려면, `config.toml` 파일에 다음 설정을 추가합니다:

```toml
project_doc_fallback_filenames = ["CLAUDE.md", "COPILOT.md"]
```

이렇게 하면 Codex가 기존 `CLAUDE.md` 파일을 그대로 읽어옵니다. 만약 이전 설정을 옮기려면 다음과 같이 대응됩니다:

| 클로드 코드 | 코덱스 |
|---|---|
| CLAUDE.md | AGENTS.md |
| .claude/settings.json | .codex/config.toml |
| 스킬 ( <이름>/SKILL.md 폴더) | 형식 동일 — 그대로 씁니다 |
| 서브에이전트 | 코덱스 서브에이전트 |
| 프로젝트 메모리 | 코덱스 Memories |
| MCP 서버 설정 · 훅 | 함께 넘어갑니다 |

`/import` 명령어를 통해 Claude Code의 설정, 프로젝트 파일, 최근 채팅 등을 가져올 수 있습니다 (최근 30일, 최대 50개). 가져오기 후에는 스킬·에이전트의 도구 제한과 권한, 커스텀 인증 MCP 서버 설정, 훅 동작 변경 가능성 등을 직접 확인해야 합니다.

### 🖥️ 컴퓨터 유즈는 또 다른 얘기입니다

Astra 발표에서 화제가 된 컴퓨터 유즈 기능은 이 컨텍스트 설정과 별개이며, 이전 모델 Sol에서도 지원되었습니다. Astra는 정확도와 속도를 개선했습니다. 이 기능은 **ChatGPT Work** 또는 **Codex**에서, **ChatGPT 데스크톱 앱**을 통해 macOS와 Windows에서 사용할 수 있습니다. Plugins에서 컴퓨터 유즈 플러그인을 설치하고 권한 설정을 해야 합니다. 터미널 앱 자동화, 보안 승인 대행 등은 불가능하며, Windows에서는 활성 데스크톱에서만 작동합니다. 한국에서의 사용 가능 여부는 명확하지 않습니다.

### 📌 정리

*   **설정**: `config.toml`에 `features.context_management.experimental_mode = true` 한 줄 추가, 새 태스크부터 적용.
*   **사용 가능 계정**: Plus, Pro, Pro Lite 로그인만 가능. Business, Enterprise, API 키는 불가.
*   **기능**: 요약 압축 대신 노트로 남기고, 앞선 컨텍스트 검색.
*   **Astra**: 컨텍스트 설정과는 별개의 업데이트 항목.
*   **Claude 이전**: `project_doc_fallback_filenames` 설정으로 기존 지침 그대로 읽기 가능.
*   **컴퓨터 유즈**: 별도 기능이며 Work/Codex 조건이 붙음.
*   **Claude Code**: 기존 컨텍스트 관리법은 그대로 유효함.

이 문서는 공식 문서를 바탕으로 작성되었으며, 실제 사용 경험에 대한 내용은 추후 업데이트될 수 있습니다.

## 출처

[Notion | Where teams and agents work together](https://app.notion.com/p/3d173c7b15ad81239d3fe9e54f0c8e05?pvs=39)

## 출처

- [https://app.notion.com/p/3d173c7b15ad81239d3fe9e54f0c8e05?pvs=39](https://app.notion.com/p/3d173c7b15ad81239d3fe9e54f0c8e05?pvs=39)
