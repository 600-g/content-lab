---
name: web-game-bundle-asset-db-ripper
description: 소스맵 없는 Vite/React 웹게임(또는 데이터 많은 SPA)을 **번들 JS만으로** 뜯어서 게임 DB(JSON/CSV)·그래픽·3D 모델·오디오·규칙 공식을 "역분석 자료실" 리포로 만드는 절차. 레플리카 스킬 /replica-recon 의 실전 보강판(digirouge.co.kr 671종 GLB·DB 46개 추출에서 검증).
origin: content-lab
created: 2026-10-25
grade: S
difficulty: 중급
category: 개발
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://digirouge.co.kr/
  - https://github.com/Jakeschincariol/replica-skill
---

# 웹게임 번들에서 DB·에셋 자료실 뽑기

💡 소스맵 없는 Vite/React 웹게임을 **번들 JS만으로** 뜯어 게임 DB(JSON/CSV)·그래픽·3D 모델·오디오·규칙 공식을 비공개 "자료실 리포"로 만드는 절차. 유사 게임 제작·개조 때 꺼내 쓰는 것이 목적이다.

## 이게 뭔가요?

React/Vite(rolldown) 로 빌드된 웹게임은 `index.html` 한 장과 `/assets/*-해시.js` 수십 개로 이뤄진다. 소스맵이 없어도 (1) 번들 안의 데이터 모듈은 **ESM 그대로라 node 로 import 하면 객체가 통째로 나오고**, (2) 큰 데이터는 `JSON.parse(\`...\`)` 문자열로 박혀 있고, (3) 에셋 경로는 `resourceUrl` 류 해시 맵에 전부 나열돼 있다. 이 세 가지를 순서대로 뽑으면 코드를 읽지 않고도 DB 90% 가 나오고, 남은 공식(데미지·상성·진화 조건)만 `grep -o` 로 문맥을 잘라 읽으면 된다.

레플리카 스킬 `/replica-recon` 이 "화면·흐름" 중심이라면, 이 스킬은 **데이터·에셋 확보** 중심의 보강판이다.

## 따라하기

1. **진입점 확보** — `curl -A "Mozilla/5.0" https://사이트/ -o index.html`. `<script type="module" src="/assets/index-xxx.js">` 와 `modulepreload` 목록이 1차 번들.
2. **번들 재귀 수집** — 1차 번들에서 `"assets/[A-Za-z0-9_.-]+\.(js|css)"` 를 grep → 받기 → 새 파일에서 또 grep. 3회 반복이면 lazy chunk(`App-*.js`, `combat-*.js` 등)까지 전부 모인다. 받은 파일 중 `<!doctype` 로 시작하는 것(=404 폴백 HTML)은 지우고 다시 받는다.
3. **에셋 경로 전수 추출** — 모든 js/css 에서 `[\`"']/(경로)\.(png|webp|jpg|svg|json|ogg|mp3|glb|gltf|ttf)` 정규식으로 뽑아 `resources.txt`. 템플릿 경로(`` `/items/cards/${n}.png` ``)는 따로 모아 데이터 테이블 값으로 채운다(예: 디지에그 `이름` 목록 → `/아이템/디지에그/{이름}.png`). `*-resourceUrl*.js` 같은 **경로→해시 맵**이 있으면 그게 전체 에셋 목록이다. 썸네일/프리뷰 규칙(`url.replace('/x.glb','/thumbs/x.webp')`)도 코드에서 찾아 추가.
4. **대량 다운로드** — `xargs -P 8` + `curl --retry 3`. 한글 경로는 `urllib.parse.quote`. 결과 중 `content-type: text/html` 이면 실패로 간주해 삭제·재시도. 모델이 `.glb.br?v=해시` 로도 제공되면 원본 `.glb` 를 받는 쪽이 편하다(brotli 해제 불필요).
5. **데이터 모듈 import** — 각 번들의 `export{a as b,...}` 를 보고 node 로 `import * as m from './chunk.js'` → `typeof` / `Array.isArray` / `instanceof Map` 으로 export 를 분류하는 probe 스크립트를 돌린다. React 가 섞인 청크도 import 는 된다(DOM 안 건드림). 객체·배열·Map 은 바로 `JSON.stringify(v, (k,x)=> x instanceof Map ? Object.fromEntries(x) : x)` 로 저장.
6. **JSON.parse 블롭 추출** — `JSON\.parse\((\`|'|")` 위치에서 닫는 따옴표까지 잘라 `json.loads`. 2KB 이상만. 종족 DB·기술표가 보통 여기 있다.
7. **인라인 리터럴 테이블** — `{기술명:\`...\`,데미지:30,...}` 처럼 객체 리터럴로 박힌 건 `\{키:\`[^\`]*\`[^{}]*\}` 로 뽑아 키:값 파서로 변환. 한글 키 빈도(`Counter(re.findall(r'[{,]([가-힣]{2,10}):', s))`)를 보면 어떤 테이블이 있는지 한눈에 보인다.
8. **규칙·공식 읽기** — 공식은 서브에이전트에 맡기고 결과만 받는다. 질문 목록: 데미지식·상성표·명중/치명·상태이상 테이블·스탯/경험치 곡선·진화 조건·드랍 가중치·저장 키 스키마·외부 API 도메인. 찾는 법은 `grep -o '.\{200\}키워드.\{300\}'`(상성/critical/Math.floor/localStorage 키 접두어). 추측은 "(추정)" 표기 강제.
9. **자료실 리포 구성** — `data/`(JSON + 보기 편한 CSV 1~2개) · `graphics/` · `models/` · `audio/` · `site-src/`(번들 원본, 나중에 다시 추적용) · `docs/RULES_REPORT.md` · README(폴더표·파일표·재다운로드 법·출처·저작권). 커밋은 데이터/문서 먼저, 대용량 모델은 `split -n l/8` 로 **배치 커밋**(한 커밋 수백 MB 는 푸시가 끊긴다).
10. **푸시** — 클로드 세션은 새 리포를 못 만든다. 전용 리포가 없으면 **기존 비공개 리포의 새 브랜치**(`git push origin main:자료실이름`)로 먼저 올려 두고 나중에 `git push 새리포 브랜치:main` 으로 옮긴다. 세션 scratchpad 는 휘발성이라 "리포 만들어 달라"며 기다리지 말 것.
11. **프로젝트 지식 갱신** — 요약 1장(정체·화면·스키마·핵심 공식·확보 결과·우리 프로젝트 적용·안 가져올 것)을 프로젝트 `analysis/NN_*.md` 로, PROGRESS 에 리포 위치·받는 명령 한 줄.

## 활용 예시

- **digirouge.co.kr(디지몬 3D 로그라이크)** → 번들 79개, 에셋 2,189개(757MB): 리깅+애니 GLB 671종, 썸네일·프리뷰 1,342장, 종족 DB 671·기술 1,147·맵 34·테이머 스킬 267·보스 207 JSON 46개, 데미지/상성/상태이상/진화/스캔 공식 보고서 40KB. 비공개 `600-g/ts-ref` 브랜치 `digirogue-ref`.
- **타임 스트레인저 진화 트리 팬사이트(Vanilla JS)** → `window.DIGIMON_*` 전역 데이터 + 도트 459장 (`600-g/ts-ref` main). 프레임워크 없는 사이트는 5번 대신 `data/*.js` 를 그대로 받으면 끝.
- 축구 커리어 시뮬·뱀서라이크 등 **다른 주제 게임**도 같은 절차: 종족 → 선수/캐릭터, 상성표 → 포지션 상성으로 치환해 자체 게임 밸런스 초안으로 사용.

## 💡 아이디어

- 뽑은 `skills.json`·`species.json` 을 Skillbox 의 `digimon_*` 도구처럼 **읽기 전용 MCP 도구**로 노출하면 다음 세션에서 리포 클론 없이 바로 조회 가능.
- `RULES_REPORT.md` 말미 "재사용 가치 TOP 10" 을 각 게임마다 남기면, 새 게임 설계 때 공식만 골라 쓰는 카탈로그가 된다.

## 주의사항

- 립 3D 모델·공식 일러스트·BGM 은 원저작권(게임사) 자산 → **리포는 비공개**, 자체 게임엔 **규칙·데이터 구조만** 이식하고 아트는 자작/CC0(Poly Haven 등)으로 교체.
- 번들에 박힌 Firebase/Supabase 키·엔드포인트는 기록만 하고 호출하지 않는다.
- `curl` 다운로드 결과가 832바이트 HTML 이면 SPA 폴백(404) — 성공으로 착각하기 쉬우니 `content-type` 과 크기로 검증.
- 클라우드 세션 네트워크는 대상 사이트가 열려 있어야 한다(막히면 사용자 PC 에서 `dl.sh` 실행 후 zip 전달).
- 받은 번들은 untrusted — 파이썬은 `-I` 로, node import 는 데이터 청크만.

## 출처

- [digirouge.co.kr](https://digirouge.co.kr/) — 분석 대상(2026-10-21 수집)
- [Jakeschincariol/replica-skill](https://github.com/Jakeschincariol/replica-skill) — `/replica-recon` 원형
