---
name: self-updating-app-release-pipeline
description: 소스를 main 에 올리면 **GitHub Actions** 가 버전 판정·빌드·산출물 검증·**GitHub Release** 까지 하고, 사이트 카드는 최신 릴리스를 따라가며, 설치된 앱은 **인앱 업데이터**로 스스로 교체하는 배포 파이프라인. 워크플로 템플릿·600g.net 허브 연동 실례·실사고 함정 포함.
origin: content-lab
grade: S
difficulty: 고급
category: 개발
ai_tools: ["Claude", "Claude Code", "도구무관"]
sources:
  - https://github.com/600-g/shutdown-timer
  - https://600g.net
originals:
  - self-updating-app-release-pipeline | 스스로 업데이트하는 앱 배포 파이프라인 | https://github.com/600-g/shutdown-timer
  - 600g-app-github-release-hub-onboarding | 600g 앱 배포 표준 — GitHub 릴리스 → 600g.net → 자동 업데이트 | https://github.com/600-g/shutdown-timer https://600g.net
---

# 자동 업데이트 앱 배포 파이프라인

💡 **버전 상수 한 줄**을 올리고 push 하면 **빌드 → 검증 → 릴리스 → 사이트 카드 갱신 → 인앱 자동 업데이트**까지 사람 손이 0인 구조입니다. 자기 자신을 교체하는 코드는 실수가 되돌려지지 않으니 **실사고 함정**부터 읽으세요.

## 이게 뭔가요?

"코드 고쳤는데 사용자한테 어떻게 전달하지?" 를 한 번만 만들어 두고 끝내는 구조입니다.

소스를 저장소에 올리면 **빌드 → 산출물 검증 → 릴리스 → 사이트 카드 갱신**까지 자동으로 가고, 이미 앱을 쓰고 있는 사람에게는 **앱이 스스로 새 버전을 알려주고 받아서 교체**합니다. 사람이 파일을 어딘가에 업로드하는 단계가 0입니다.

데스크톱 앱(exe)을 기준으로 쓰였지만 구조는 모바일·CLI·웹앱에도 그대로 옮겨집니다. 윈도우·맥·안드로이드·CLI 무엇이든 같은 순서로 붙이면 되고, 뒤쪽에 실제 적용 예(600g.net 허브 + C# WinForms 앱 `600-g/shutdown-timer`)의 구체값을 그대로 실었습니다.

```
소스 수정 → main push
   ↓ (GitHub Actions)
버전 읽기 → 태그 중복 확인 → 빌드 → 산출물 검증 → Release 생성(변경내역 첨부)
   ↓
사이트가 "최신 릴리스" 를 가리키고 있어 카드가 자동 갱신
   ↓
기존 사용자: 앱이 주기적으로 확인 → 알림 → 사용자가 누르면 교체 → 재실행
```

**핵심 원칙 둘**

1. **버전 번호의 진실은 소스 안 상수 한 곳**입니다. 태그도, 릴리스 제목도, 사이트 표기도 전부 거기서 파생됩니다. 손으로 맞추는 곳이 생기면 반드시 어긋납니다.
2. **파일은 GitHub Release 한 곳에만** 있습니다. 사이트는 가리키기만 하고, 앱도 같은 곳을 봅니다.

### 무엇을 어디까지 붙이나

| 대상 | 붙일 단계 | 인앱 교체 |
|---|---|---|
| 데스크톱 설치형(exe·맥 앱) | 1~10 전부 | 외부 스크립트로 교체 (7단계) |
| CLI | 1~10 전부 | 같은 구조, 실행 중 자기 교체 제약도 동일 |
| 모바일(안드로이드·iOS) | 1~6, 8 | 스토어 심사가 껴서 자동 교체 불가 — 버전 확인과 "스토어 열기"(또는 "새 버전 받기" 링크)까지만 |
| 웹앱 | 1~3, 6 | 교체 불필요 — 빌드 ID 를 심어 두고 새 빌드를 감지하면 새로고침 권유 |
| 문구만 자주 고치는 앱 | — | 문구를 실행파일 밖 파일로 빼면 재배포 없이 고칠 수 있다. 파일 → 원격 → 내장 기본값 3단 폴백 |

## 따라하기

### 1. 버전을 소스에 하나만 둔다

```csharp
private const string VERSION = "1.0.0";   // 이 한 줄이 유일한 진실
```

스택별 위치: C# `const string VERSION = "1.0.0";` / Node `package.json` 의 `version` / Python `__version__` / 안드로이드 `versionName`.

CI 가 이 값을 읽어 태그(`v1.0.0`)를 만듭니다. `major.minor.patch`(semver)를 쓰고 버그·안정화는 patch(1.0.**1**), 기능 추가는 minor(1.**1**.0), 대변경은 major 를 올립니다.

⚠️ **비교할 때 끝자리만 보면 안 됩니다.** `1.1.0` 의 끝은 `0` 이라 `1.0.9` 보다 작아집니다. 반드시 자리별로 비교하세요(1.1.0 > 1.0.9).

```
1.2.3  →  1*1000000 + 2*1000 + 3
```

### 2. 변경 내역을 한 곳에 쓰고 두 곳에 흘린다

`CHANGELOG.md` 를 아래 형태로 둡니다.

```markdown
# 변경 내역
<!-- RELEASES -->
## 1.0.1
- 사용자 말로 한 줄씩
## 1.0.0
- 첫 공개 버전이에요
```

`## 1.0.1` 절을 쓰면 CI 가 그 절만 뽑아 릴리스 본문으로 쓰고, 앱은 릴리스 API 의 `body` 를 읽어 **업데이트 창에 그대로** 보여줍니다. 한 번 쓰면 두 곳에 나갑니다.

**검증 단계에서 CHANGELOG 에 해당 버전 절이 없으면 릴리스를 막으세요.** 설명 없는 배포를 원천 차단합니다. 소스 수정과 VERSION·CHANGELOG 절은 **같은 커밋**에 넣습니다.

### 3. CI 가 버전을 읽고, 중복이면 막는다

```yaml
on:
  push:
    branches: [main, dev]      # dev 는 릴리스 없이 빌드만
    paths: ['src/**', 'build.sh', '.github/workflows/**']
```

판정 단계에서:
- 소스에서 버전을 읽어 태그 이름을 만든다
- 그 태그가 이미 있으면 **릴리스하지 않는다**
- 그런데 **소스가 바뀌었는데** 태그가 그대로면 → **실패(빨간 X)로 막는다**

마지막 줄이 핵심입니다. 번호 올리기를 깜빡하는 일이 구조적으로 안 생깁니다.

```bash
if git diff --quiet "$BEFORE" "$GITHUB_SHA" -- src/main.ext; then
  echo "소스 변경 없음 — 빌드만"
else
  echo "::error::소스가 바뀌었는데 $TAG 는 이미 릴리스됨. 버전을 올리세요."
  exit 1
fi
```

워크플로에는 `permissions: contents: write`(Release 생성 권한)와 `concurrency`(동시 릴리스 방지)를 함께 둡니다. 전체 템플릿은 아래 "실제 적용 예" 절에 있습니다.

### 4. 릴리스 전 산출물 검증 — 마지막 관문

빌드 직후, 릴리스 **전에** 산출물을 뜯어봅니다. 하나라도 걸리면 배포하지 않습니다.

- 패키지에 필요한 파일이 다 있는가
- 실행파일이 올바른 형식이고 비정상적으로 작지 않은가
- **소스의 버전과 산출물 안에 박힌 버전이 일치하는가**
- **CHANGELOG 에 이 버전 절이 있는가**
- **업데이트 기능이 산출물에 살아 있는가**

마지막 항목이 특히 중요합니다. 업데이트 코드가 빠진 빌드가 한 번 나가면 **그걸 받은 사람은 영원히 갱신을 못 받습니다.** 되돌릴 수 없는 사고라 자동 검사로 막아야 합니다.

```python
need(("v" + ver).encode("utf-16-le") in exe, "산출물 버전 불일치")
need(b"api.github.com/repos/OWNER/REPO/releases/latest" in exe, "업데이트 기능 유실")
```

### 5. 로컬에서 빌드할 수 없을 때 — dev 브랜치

맥에서 윈도우 앱을 만드는 것처럼 **개발 기기에서 컴파일이 불가능한** 조합이 흔합니다. 이때 `dev` 브랜치를 릴리스 없는 빌드 전용으로 씁니다.

```
dev push → 빌드 + 검증만 (릴리스 X)  ← 문법·참조 오류를 여기서 다 잡는다
초록불 → main 병합 → 릴리스
```

큰 변경은 **호출자 없는 상태로 먼저 올려** 컴파일만 통과시키고, 그다음 연결하세요. 한 번에 다 넣으면 오류가 어디서 났는지 찾는 데 시간이 다 갑니다.

### 6. 사이트는 "최신" 을 가리키게만 둔다

사이트에 파일을 올리지 마세요. 고정 주소 하나를 걸어 두면 릴리스가 바뀔 때 알아서 따라옵니다.

```
https://github.com/OWNER/REPO/releases/latest/download/App.zip
```

카드에 버전·용량을 표시하려면 릴리스 API 를 주기적으로 읽어 캐시하면 됩니다(10분 정도).

**에셋 파일 이름은 ASCII 로 고정**하세요. 바꾸는 순간 사이트 링크와 모든 설치본의 업데이트가 끊깁니다(워크플로·빌드 스크립트 양쪽에 박혀 있음). GitHub 은 한글 에셋명을 뭉갭니다. 익명 다운로드가 되려면 **저장소는 Public** 이어야 합니다.

### 7. 인앱 업데이터 — 여기가 제일 위험하다

흐름은 단순합니다. 하지만 **자기 자신을 교체하는 코드**라 실수가 되돌려지지 않습니다.

```
주기적으로 최신 버전 확인 → 새 버전이면 표시 → 사용자가 누르면
임시 스크립트 생성 → 앱 종료 → 스크립트가 교체 → 새 앱 실행
```

실행 중인 프로그램은 자기 파일을 덮어쓸 수 없어서 **교체는 외부 스크립트가 대신**합니다. 교체 스크립트는 다음 순서를 지킵니다(이유는 주의사항의 함정 ①~⑥).

```
원본 백업 → 새 파일 복사 → 복사 결과 확인 → 파일 존재·크기 확인
  → 정상이면 백업 삭제 / 어긋나면 백업으로 원복
  → 원복까지 실패하면 백업을 남기고 복구 방법을 파일로 안내
```

- 압축 해제 직후 OS 의 **차단 표시를 지운다** (앱이 켜질 때 한 번 더 지우면 이중 방어)
- 업데이트로 인한 종료는 "저장 안 했는데 끄시겠습니까?" 확인 창을 **건너뛰는 플래그**를 준다
- 종료가 취소되면 **취소 신호 파일**을 남기고, 스크립트는 대기 루프에서 그걸 보면 조용히 물러난다
- 대기가 **시간 초과되면 교체를 포기**한다 (강행하면 앱을 잃는다)
- 성공 판정은 **타이밍이 아니라 파일 무결성(존재·크기·해시)** 으로 한다
- 스크립트 본문은 **ASCII 만**, 경로는 **환경변수로** 넘긴다

### 8. 사용자에게 보이는 부분

기술이 잘 돌아도 안내가 어색하면 완성도가 깎입니다. 정착된 방침입니다.

- **작업을 막지 마세요.** 시작하자마자 팝업을 띄우는 대신 **어딘가에 표시(배지)만** 남기고, 알림은 하루 한 번으로 제한합니다. 받을지 말지는 사용자가 정합니다.
- **안내창을 OS 기본 대화상자로 두지 마세요.** 앱이 고유한 디자인을 쓴다면 거기만 확 튑니다. 앱 디자인으로 만든 시트를 재사용하세요.
- **무엇이 바뀌는지 보여주세요.** 변경 내역을 목록으로 띄우면 "왜 받아야 하지" 가 해결됩니다.
- **말투**: 사실은 짧게, 설명은 친근하게. "버그를 고쳤어요" 보다 "불편함을 해소했어요". "새 버전 없어요" 보다 "최신 버전".
- **겁주는 문구는 빼세요.** 보안 경고 안내 같은 건 앱이 알아서 처리하게 만들고 노출하지 않습니다.

### 9. 저장소에 AI 작업 규칙 남기기

저장소 루트 `CLAUDE.md` 에 최소 이 셋을 적어 두면 어느 세션·기기에서 고쳐도 배포가 안 깨집니다.

- 소스를 고치면 **VERSION + CHANGELOG 절**을 같은 커밋에
- **에셋 이름 변경 금지**, 사이트(허브)에 파일 직접 업로드 금지
- 로컬 클론은 `git pull` 먼저, `--force` 금지

### 10. 실제 적용 예: 600g.net 허브

위 구조를 600g 의 모든 앱에 공통으로 붙이는 표준입니다. 첫 적용 사례는 자동 종료 타이머(`600-g/shutdown-timer` → 600g.net "종료타이머&알림" 카드)이고, 기준 구현은 그 저장소의 `build.yml` · `build.sh` · `CLAUDE.md` · `PhoneShell.cs` 끝 `Updater` 클래스, 허브 쪽은 company-hq `docs/platform-notes.md` "앱 배포" 절 · `server/routers/apps.py` 입니다.

```
[개발] VERSION 올림 + CHANGELOG 한 절 → main push
   ↓ GitHub Actions
[빌드] 버전 읽기 → 태그 중복 판정 → 빌드 → 산출물 검증 → Release(v x.y.z) + 에셋(고정 이름)
   ↓ 10분 이내
[허브] api.600g.net 이 최신 릴리스 조회 → 600g.net 카드 버전·용량 자동 갱신
       [받기] = /api/apps/{id}/download → 카운트 후 GitHub 로 302 (트래픽은 GitHub 가 부담)
   ↓
[사용자] 설치된 앱이 GitHub API 로 최신 태그 확인 → 배지 → 사용자가 누르면 교체
```

#### 10-0. 정할 것 3개 (프로젝트마다)

| 항목 | 규칙 | 예 |
|---|---|---|
| 저장소 | `600-g/<영문-이름>`, **Public** (익명 다운로드 필수) | `600-g/shutdown-timer` |
| 에셋 이름 | **ASCII 고정 파일명**, 절대 안 바꿈 (GitHub 은 한글 에셋명을 뭉갬) | `AutoShutdownTimer.zip` |
| 허브 id | 영문 소문자 슬러그 = 공유 링크 `600g.net/a/{id}` | `autotimer` |

#### 10-1. 저장소 만들기

1. github.com/new → Owner `600-g` → 이름 → **Public** → README·gitignore·license 끄기 → Create
2. Settings → Actions → General → Workflow permissions → **Read and write** → 그 섹션의 **Save**. 빠지면 Release 생성이 권한 오류로 실패합니다. 같은 페이지에 Save 가 여러 개라 **엉뚱한 섹션을 저장하기 쉬우니** 저장 후 새로고침해 재확인하세요.

#### 10-2. 워크플로 `.github/workflows/build.yml` (공통 뼈대)

빌드 스텝만 스택별로 바꾸고 나머지는 그대로 씁니다. 완성본 참고: `600-g/shutdown-timer/.github/workflows/build.yml`.

```yaml
name: build-and-release
on:
  push:
    branches: [main, dev]          # dev = 빌드·검증만, 릴리스 없음
    paths: ['src/**', 'build.sh', '.github/workflows/**', 'CHANGELOG.md']
    tags: ['v*']
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: build-and-release
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest         # 스택에 따라 windows-latest / macos-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: 버전 읽기
        id: ver
        run: |
          VER=$(sed -nE 's/.*VERSION = "([0-9]+\.[0-9]+\.[0-9]+)".*/\1/p' src/Main.cs | head -1)   # ← 스택별로 수정
          [ -z "$VER" ] && { echo "::error::VERSION 을 못 찾음"; exit 1; }
          TAG="v$VER"
          if git ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null 2>&1; then EX=true; else EX=false; fi
          echo "tag=$TAG" >> $GITHUB_OUTPUT; echo "exists=$EX" >> $GITHUB_OUTPUT

      - name: 릴리스 판정 (번호 안 올리고 소스 바꾸면 실패)
        id: gate
        env: { BEFORE: "${{ github.event.before }}", EX: "${{ steps.ver.outputs.exists }}", TAG: "${{ steps.ver.outputs.tag }}" }
        run: |
          DO=false
          [[ "$GITHUB_REF" == refs/tags/* ]] && DO=true
          [[ "$GITHUB_REF" == refs/heads/main && "$EX" == false ]] && DO=true
          echo "release=$DO" >> $GITHUB_OUTPUT
          if [[ "$DO" == false && "$GITHUB_REF" == refs/heads/main && -n "$BEFORE" && "$BEFORE" != 0000000000000000000000000000000000000000 ]] \
             && ! git diff --quiet "$BEFORE" "$GITHUB_SHA" -- src/; then
            echo "::error::소스가 바뀌었는데 $TAG 는 이미 릴리스됨 — VERSION 올리고 CHANGELOG 추가"; exit 1
          fi

      - name: 빌드                    # ← 스택별 (아래 표)
        run: ./build.sh

      - name: 산출물 검증              # 걸리면 릴리스 안 함
        run: |
          test -f MyApp.zip
          VER="${{ steps.ver.outputs.tag }}"; VER="${VER#v}"
          grep -qE "^##\s*$VER\s*$" CHANGELOG.md || { echo "::error::CHANGELOG 에 ## $VER 없음"; exit 1; }
          # 인앱 업데이트가 있는 앱이면: 산출물 안에 업데이트 URL 문자열이 남아 있는지도 검사

      - name: 변경 내역 뽑기
        if: steps.gate.outputs.release == 'true'
        run: |
          VER="${{ steps.ver.outputs.tag }}"; VER="${VER#v}"
          awk -v v="$VER" '$0 ~ "^##[ \t]*"v"[ \t]*$" {f=1; next} /^##[ \t]/ {f=0} f' CHANGELOG.md > RELEASE_NOTES.md

      - uses: softprops/action-gh-release@v2
        if: steps.gate.outputs.release == 'true'
        with:
          tag_name: ${{ steps.ver.outputs.tag }}
          target_commitish: ${{ github.sha }}
          files: MyApp.zip             # ← 0단계의 고정 에셋 이름
          body_path: RELEASE_NOTES.md
```

자동 종료 타이머의 릴리스 스텝은 에셋 이름만 바뀐 같은 형태입니다(태그를 CI 가 만들 때).

```yaml
- uses: softprops/action-gh-release@v2
  with:
    tag_name: ${{ steps.ver.outputs.tag }}
    target_commitish: ${{ github.sha }}   # 태그가 이 빌드 커밋을 가리키게
    files: AutoShutdownTimer.zip           # 에셋 이름 고정 (사이트·앱이 이 이름으로 찾음)
    body_path: RELEASE_NOTES.md            # CHANGELOG 해당 절
```

**스택별 빌드 스텝**

| 스택 | runs-on | 빌드 |
|---|---|---|
| C# WinForms 단일 exe | ubuntu-latest | `apt-get install -y mono-devel` → `mcs -sdk:4.5 -target:winexe ...` (→ `windows-tray-app-autorun-patterns` 3부) |
| Python → exe | windows-latest | `pip install pyinstaller` → `pyinstaller --onefile` (크로스 빌드 불가) |
| Electron | windows-latest / macos-latest | `npm ci && npx electron-builder --publish never` |
| 안드로이드 APK | ubuntu-latest | `./gradlew assembleRelease` (서명 키는 Secrets) |
| CLI(Go·Rust 등) | ubuntu-latest | 타깃별 크로스 컴파일 후 zip |

zip 안에는 실행파일 + 필요 시 설치 보조(`보안패치.bat` 등) + 사용설명서를 넣습니다. zip 이름·내부 exe 이름 모두 ASCII 입니다.

#### 10-3. 첫 릴리스 만들기

main 에 올리면 끝입니다(태그는 Actions 가 만듦). 올리는 방법은 아무거나: GitHub 웹 Upload files · `git push` · claude.ai Code. Actions 탭 초록불 → Releases 에 `v1.0.0` + 에셋을 확인합니다.

#### 10-4. 600g.net 허브에 연결 (최초 1회)

허브 백엔드(company-hq, 맥)의 **링크 API** 로 등록합니다. 관리 UI 에는 연동 입력칸이 아직 없어 API 전용입니다. 맥 터미널에서:

```bash
cd ~/Developer/my-company/company-hq/server
PW=$(grep '^SHOWCASE_ADMIN_PASSWORD=' .env | cut -d= -f2-)
curl -s -X POST http://localhost:8000/api/apps/link \
  -H "X-Admin-Password: $PW" -H "Content-Type: application/json" \
  -d '{"id":"myapp","source_repo":"600-g/my-app","source_asset":"MyApp.zip",
       "name":"마이앱","description":"한 줄 설명","platform":"windows",
       "icon":"lucide:rocket","color":"#0ea5e9","visible":true,"order":2}'
curl -s https://api.600g.net/api/apps | python3 -m json.tool     # 카드 확인
```

- 등록 시 **최신 릴리스와 에셋이 실제로 있어야** 성공합니다(없으면 400) → 반드시 10-3 다음에.
- `platform`: windows · mac · linux · android · ios · other
- `icon`: `lucide:<이름>` / `https://…` / 인라인 `<svg>`
- 이후 버전·용량·날짜는 허브가 **10분 캐시**로 자동 갱신합니다. 이름·설명 등은 관리 UI(600g.net 푸터 `© 600g` 5번 탭)나 `PUT /api/apps` 로 수정합니다.
- `source_repo`/`source_asset` 는 PUT 으로 못 바꾸고 link 로만 재설정합니다.
- 공유 링크: `https://600g.net/a/{id}` (OG 미리보기 자동)

#### 10-5. 인앱 업데이터 계약

설치형 앱이 지켜야 할 계약입니다.

```text
확인:   GET https://api.github.com/repos/600-g/<repo>/releases/latest
        → tag_name("v1.0.1") 을 앱 VERSION 과 자리별 비교, body = 변경 내역(업데이트 창에 표시)
받기:   https://github.com/600-g/<repo>/releases/latest/download/<에셋>
주기:   시작 수 초 뒤 1회 + 6시간마다 (비인증 API 는 IP 당 시간 60회 제한)
표시:   작업을 막는 팝업 금지 — 배지 + 하루 1회 알림, 사용자가 눌러야 교체
```

교체·롤백·차단 해제는 7단계와 주의사항의 함정 목록을 그대로 따릅니다.

#### 10-6. 윈도우 .NET 앱 구체값 (자동 종료 타이머 실측)

C# WinForms 단일 exe 에 위 구조를 옮기며 확인한 값입니다.

- `.NET 4.5` 기본 TLS 는 1.0 → GitHub API 연결 불가. `ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072;` (TLS 1.2) 를 지우지 말 것.
- 업데이트 확인 타이머는 **생성자**에 둡니다(`Shown` 아님). `--tray` 로 트레이에 숨어 시작하면 `Shown` 이 영영 안 와서 트레이 상주 사용자가 업데이트를 못 받습니다. 첫 확인 6초 뒤, 이후 6시간마다.
- 표시 방침: 설정 화면 버전 줄에 배지(`ShowUpdateBadge`) + 트레이 귀띔 하루 1회(레지스트리 `updNotice`=yyyyMMdd). 확인 창은 사용자가 그 줄을 눌렀을 때만.
- 배치 실행 형태(환경변수를 전달하려면 `UseShellExecute=false` 필수):

```csharp
psi = new ProcessStartInfo(Environment.GetEnvironmentVariable("ComSpec") ?? "cmd.exe",
                           "/d /c \"\"" + bat + "\"\"");
psi.UseShellExecute = false;   // true 로 바꾸면 EnvironmentVariables 가 예외
```

- 차단 표시(MOTW) 해제 두 겹 — 교체 배치 안:

```text
Get-ChildItem -LiteralPath $env:TMPD -Recurse -File | Unblock-File
del "%TMPD%\AutoShutdownTimer.exe:Zone.Identifier" 2>nul
```

- 경로 전달 환경변수: `AST_EXE` / `AST_DIR` / `AST_PID`, 취소 신호 파일 `AST_CANCEL`, 대기 60초 초과 시 `goto :fail`, 백업은 `%EXE%.bak`, 크기 검증 기준 500KB.

#### 10-7. 확인 명령

```bash
gh release list --repo 600-g/shutdown-timer --limit 3
curl -s https://api.600g.net/api/apps | python3 -m json.tool
```

### 11. 체크리스트

배포 파이프라인을 새로 만들 때 이것만 확인하면 됩니다.

- [ ] 저장소가 Public 이고 Workflow permissions 가 Read and write 로 저장됐는가 (새로고침 확인)
- [ ] 버전 상수가 소스 한 곳에만 있고 태그·릴리스·사이트가 거기서 파생되는가
- [ ] 버전을 안 올리면 CI 가 막는가
- [ ] 변경 내역이 없으면 CI 가 막는가
- [ ] 릴리스 전 산출물 검증이 있는가 (특히 업데이트 기능 유실 검사)
- [ ] 로컬 빌드가 안 되면 릴리스 없는 검증 브랜치가 있는가
- [ ] 에셋 이름이 ASCII 고정이고, 사이트가 "최신" 을 가리키는가 (파일을 직접 올리지 않는가)
- [ ] 교체 실패 시 원래 상태로 돌아오는가
- [ ] 타이밍으로 성공을 판정하는 곳이 없는가
- [ ] 안내가 사용자 작업을 막지 않는가
- [ ] 저장소 `CLAUDE.md` 에 VERSION+CHANGELOG 동시 커밋 · 에셋 이름 고정 · `--force` 금지 규칙이 있는가
- [ ] (허브 연동 시) 첫 릴리스 후 link 등록 → `api/apps` 에서 카드 확인

## 활용 예시

- **윈도우 유틸**(자동 종료 타이머): C# → mono 빌드 → `AutoShutdownTimer.zip` → 허브 `autotimer`. main 에 소스를 올리면 Actions 가 태그·빌드·Release 를 만들고 카드가 따라갑니다.
- **맥 앱**: macos-latest 에서 빌드 → `MyApp-mac.zip` → `platform:"mac"` 으로 별도 id 등록(윈도우판과 카드 분리).
- **안드로이드 APK**: gradle 빌드 → `MyApp.apk` → `platform:"android"`. 앱 안 업데이트는 "새 버전 받기" 링크까지만.
- **웹앱**: 교체 불필요 — 허브 앱 카드 대신 쇼케이스 카드. 빌드 ID 로 새 버전 감지 시 새로고침 권유.

## 💡 아이디어

- 새 프로젝트를 만들 때 Claude 에게 한 줄이면 됩니다: "600g 앱 배포 표준 스킬대로 이 프로젝트에 저장소·워크플로·CHANGELOG·허브 연결까지 붙여줘. 에셋 이름은 ○○.zip, 허브 id 는 ○○"
- 여러 앱이 쌓이면 워크플로를 `600-g/.github` 재사용 워크플로(`workflow_call`)로 빼서 각 저장소는 빌드 스텝만 두기.

## 주의사항

### 실제 배포 사고에서 얻은 함정

#### ① 교체 스크립트는 "지금 설치된" 버전이 만든다 ★★★

**가장 중요합니다.** 새로 받은 파일은 교체 작업에 참여하지 않습니다. 스크립트를 고쳐도 **그 버전이 설치된 다음 업데이트부터** 적용됩니다.

→ **결함 있는 교체 스크립트를 한 번 배포하면 그 버전 사용자는 수동 재설치 외에 탈출구가 없습니다.** 업데이터를 건드릴 때 유독 조심해야 하는 이유입니다. 다른 버그는 다음 버전에서 고치면 되지만 이건 아닙니다.

#### ② 타이밍으로 성공을 판정하지 마라 ★★★

"새 앱이 5초 안에 떴는지 확인하고 안 떴으면 되돌리기" 를 넣었다가 **앱을 못 켜게 만들었습니다.**

백신이 새 파일을 검사하느라 늦게 뜨는 건 흔한 정상 상황입니다. 그걸 실패로 오판하고 되돌리려다 막 시작한 파일을 덮어쓰지 못해, 결국 아무것도 안 띄우는 경로로 빠졌습니다.

→ **되돌릴 수 없는 동작에 시간 기반 판정을 붙이지 마세요.** 파일 무결성(존재·크기·해시)으로 충분합니다.

#### ③ 실행 검증이 불가능한 플랫폼은 감사로 대체되지 않는다 ★★★

코드 감사를 두 번 돌려 결함 20건을 잡고도 **실사용 첫 시도에서 터졌습니다.** 심지어 감사가 권한 방어 로직이 새로운 고장을 만들었습니다(함정 ②).

그리고 감사가 "이건 100% 실패한다" 고 확신했던 항목이 **실제로는 잘 동작했습니다.** 그 말을 그대로 믿고 사용자에게 "수동 설치가 필요하다" 고 잘못 안내했습니다.

→ 실행할 수 없는 플랫폼의 동작은 **검토 결과를 확정으로 전달하지 마세요.** "코드상으로는 이렇게 보인다" 와 "실제로 그렇다" 는 다릅니다. 첫 실사용 확인 전까지는 가설입니다.

#### ④ 내려받은 파일의 차단 표시를 풀어라 ★★

인터넷에서 받은 파일에는 OS 가 차단 표시를 붙입니다. 압축을 풀면 그게 실행파일로 옮겨가 **실행이 막히거나 경고가 뜹니다.** 최초 설치 때 안내 스크립트가 하는 일인데 업데이트 경로에서 빠뜨리기 쉽습니다.

→ 압축 해제 직후 차단 표시를 지우세요. 앱 안에서도 켜질 때 한 번 더 지우면 이중 방어가 됩니다. (윈도우 구체 명령은 10-6)

#### ⑤ 종료가 취소될 수 있다 ★★

"저장 안 했는데 끄시겠습니까?" 같은 확인 창이 종료를 붙잡으면, 교체 스크립트는 기다리다 지쳐 **살아 있는 파일을 덮어쓰려다** 실패합니다.

→ 두 가지를 같이 하세요.
- 업데이트로 인한 종료일 때는 그 확인 창을 건너뛰는 플래그
- 종료가 취소되면 스크립트에 알리는 **취소 신호 파일**. 스크립트는 대기 루프에서 그걸 확인하고 조용히 물러납니다

그리고 **대기가 시간 초과되면 교체를 포기**하게 하세요. 강행하면 앱을 잃습니다.

#### ⑥ 교체는 백업 → 검증 → 실패 시 원복 ★★

제자리 덮어쓰기만 하면 복사가 중간에 끊겼을 때 되돌릴 수단이 없습니다(순서는 7단계). **복사 결과를 확인하지 않으면 실패가 성공으로 처리됩니다.** 사용자는 같은 실패를 무한 반복하면서 왜 버전이 안 바뀌는지 모릅니다.

#### ⑦ 스크립트는 ASCII 로, 경로는 환경변수로 ★

스크립트 본문에 경로를 글자로 박으면 **비영어 사용자명이나 다른 언어 환경에서 깨집니다.** 본문은 ASCII 만 쓰고 경로는 환경변수로 넘기세요. 환경변수는 인코딩 영향을 안 받습니다.

배치 파일을 실행할 때는 명령 해석기를 거치는 쪽이 안전합니다. 직접 실행이 되는 환경도 있지만 의존하지 마세요. (이 부분은 환경마다 다르니 **단정하지 말고 실측**하세요.)

#### ⑧ 에셋 이름·저장소 공개 여부는 바꾸는 순간 전부 끊긴다 ★★

에셋 이름은 ASCII·고정입니다. 바꾸면 사이트 [받기]와 모든 설치본의 업데이트가 끊깁니다. 저장소가 Public 이 아니면 익명 다운로드·앱 업데이트가 안 됩니다.

#### ⑨ 이미 받아간 릴리스는 지우고 다시 내지 마라 ★★

릴리스를 지우고 같은 번호로 다시 내는 것은 **배포 전 단계에서만** 하세요. 이미 받아간 사람이 있으면 그 사람의 버전이 서버보다 높아져(버전 역전) 갱신이 영영 안 뜹니다.

#### ⑩ 로컬 클론이 제일 위험하다 ★★

claude.ai 등이 GitHub 을 직접 고친 뒤 뒤처진 로컬 사본을 밀면 남의 수정을 덮습니다. 로컬 작업은 `git pull` 먼저, 충돌해도 `--force` 금지입니다(태그·커밋 어긋남은 되돌리기 어렵다).

#### ⑪ 사이트가 자체 서버를 거치면 그 서버가 단일 장애점이다 ★

사이트 카드가 자체 서버(예: 맥의 `api.600g.net` — company-hq + cloudflared)를 거치면 **그 서버가 꺼질 때 카드가 안 뜨고 다운로드도 멈춥니다.** GitHub 직행 주소(`…/releases/latest/download/<에셋>`)는 항상 살아 있으니 비상 링크로 보관하세요. 허브 카드 반영은 최대 10분 지연(캐시)이며, 급하면 기다리거나 link 를 다시 호출(force 조회)합니다.

#### ⑫ 윈도우 전용 함정 ★

- 저장소 안 윈도우 `.bat`(릴리스.bat·보안패치.bat)은 **CP949 + CRLF** 로 저장합니다. UTF-8 이면 한글이 깨집니다.
- `.NET 4.5` 앱은 TLS 1.2 설정을 지우면 GitHub API 에 연결하지 못합니다.
- 업데이트 확인을 `Shown` 에 두면 트레이로 시작한 사용자는 업데이트를 못 받습니다.

### 그 밖에

- **업데이터를 건드린 변경은 한 번 더 검증하세요.** 다른 버그와 달리 되돌릴 수 없습니다.
- **첫 실사용 확인 전까지는 "된다" 고 말하지 마세요.** 감사 통과는 가설 검증이지 실증이 아닙니다.
- 코드 서명이 없으면 최초 실행 경고는 완전히 없앨 수 없습니다. 인증서는 유료이고, 초기 단계라면 안내 스크립트로 우회하는 편이 현실적입니다.
- 관리자 비번(`SHOWCASE_ADMIN_PASSWORD`)은 `company-hq/server/.env` 에만 둡니다. 스킬·문서·커밋에 적지 마세요.
- 비인증 GitHub API 는 IP 당 시간 60회 제한이 있으니 확인 주기를 너무 짧게 잡지 마세요(시작 후 1회 + 6시간마다).

## 출처

- [https://github.com/600-g/shutdown-timer](https://github.com/600-g/shutdown-timer)
- [https://600g.net](https://600g.net)

### 합쳐진 원본 문서

이 문서는 아래 2개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| 스스로 업데이트하는 앱 배포 파이프라인 | `self-updating-app-release-pipeline` | [github.com](https://github.com/600-g/shutdown-timer) |
| 600g 앱 배포 표준 — GitHub 릴리스 → 600g.net → 자동 업데이트 | `600g-app-github-release-hub-onboarding` | [github.com](https://github.com/600-g/shutdown-timer) · [600g.net](https://600g.net) |
