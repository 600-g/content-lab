💡 이 스킬은 **Anthropic 공식 Claude API quickstart 리포지토리**로, 6가지 프로덕션 레디 템플릿(고객지원 · 금융분석 · 컴퓨터 사용 · 브라우저 자동화 · 자율 코딩)을 즉시 클론해 활용할 수 있는 공식 베이스 코드 모음입니다.

## 이게 뭔가요?

**Anthropic 이 직접 관리하는 공식 GitHub 리포지토리**(stars 16.8k · forks 2.9k)로, Claude API 를 활용한 6가지 프로덕션 레디 애플리케이션 템플릿을 제공합니다. 각 quickstart 는 독립된 디렉터리로 분리되어 있어 필요한 것만 선택해 클론·커스터마이징할 수 있습니다.

언어 구성: **Python 62.7%** · TypeScript 20.6% · Jupyter Notebook 5.7% · JavaScript 5.0% · HTML 3.3% · Shell 1.2%.

💰 유료 필요: Claude API 키 (월 $5 무료 크레딧 → `console.anthropic.com` 가입)
✅ 무료 대안: Claude Max 구독 보유자는 API 크레딧으로 충당 가능

## 따라하기

1. **리포지토리 클론**

   ```bash
   git clone https://github.com/anthropics/anthropic-quickstarts
   cd anthropic-quickstarts
   ```

2. **6가지 quickstart 중 하나 선택** — 폴더로 이동

   - `/customer-support-agent` — **지식 기반 챗봇** (자연어 이해·생성)
   - `/financial-data-analyst` — **재무 데이터 분석 + 대화형 시각화**
   - `/computer-use-demo` — Claude 가 **데스크톱 제어** (`computer_use_20251124` 도구 버전, 줌 기능)
   - `/computer-use-best-practices` — **macOS 네이티브** 컴퓨터 사용 에이전트 참조 구현. 명시적 도구 정의 / 이미지 크기 조정 / 프롬프트 캐싱 / 서버 측 컴팩션 / 배치 도구 호출 / 샌드박스 쉘 / 궤적 기록 포함
   - `/browser-use-demo` — **Playwright 기반 브라우저 자동화** (DOM 검사·콘텐츠 추출·폼 작성)
   - `/autonomous-coding` — Claude Agent SDK 기반 **자율 코딩**. 2-에이전트 패턴(initializer + coding agent) · Git 으로 진행 상황 유지 · 점진적 기능 작업

3. **종속성 설치 + API 키 설정**

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   # Python quickstart
   pip install -r requirements.txt
   # TypeScript quickstart
   npm install
   ```

4. **각 quickstart 의 README 따라 실행** — 디렉터리마다 별도 setup 지침 포함

## 활용 예시

- **스타트업 MVP 1주 구축** — `/customer-support-agent` 클론 + 자사 FAQ 를 knowledge base 로 임포트 → 1주 만에 SaaS 챗봇 출시. **PMF 검증 비용 90% 절감**
- **사내 반복 업무 자동화** — `/browser-use-demo` 로 매일 아침 경쟁사 가격·재고 자동 수집 → 슬랙 알림. 운영팀 인당 **하루 2시간 절감**
- **1인 개발자 야간 자동 코딩** — `/autonomous-coding` 으로 잠든 사이 기능 추가 → 아침에 PR 리뷰만. 사이드 프로젝트 진척 **3배 가속**
- **금융·재무 분석 도구 신속 프로토타이핑** — `/financial-data-analyst` 베이스에 사내 데이터셋 연결 → 임원 보고용 대화형 대시보드를 며칠 만에 구축
- **AI 에이전트 학습 교재** — 6개 quickstart 가 각각 모범 패턴(프롬프트 캐싱 · 도구 정의 · 컴팩션 · 배치 호출)을 보여주므로, 학생·연구원·신입 개발자의 **실전 학습 자료**로 활용

## 💡 아이디어

- **6종 quickstart 를 결합한 멀티 에이전트 SaaS** — 예: `/browser-use-demo` 로 정보 수집 + `/autonomous-coding` 으로 보고서 자동 생성 → B2B 리서치 자동화 서비스 (월 구독 $50–200 가능)
- **소상공인 화이트라벨 챗봇** — `/customer-support-agent` 를 디자인만 입혀 카페·뷰티숍·온라인몰에 월 $30 패키지 판매
- **노코드 사용자용 GUI 래퍼** — quickstart 위에 간단한 웹 UI 만 얹어 코딩 모르는 사용자도 클릭으로 에이전트 실행

## 주의사항

- **Computer Use 시리즈는 반드시 VM 또는 컨테이너**에서 실행 (Claude 가 실제 시스템 제어 → 호스트 손상 위험)
- 각 quickstart 마다 별도 종속성 + API 사용량 → 동시 실행 시 **비용 누적**
- `computer_use_20251124` 같은 도구 버전 명시 — 최신 Claude 모델에 맞춰 주기적 업데이트 확인 필요

## 출처

- [anthropics/anthropic-quickstarts (GitHub)](https://github.com/anthropics/anthropic-quickstarts)
- [Claude API 문서](https://docs.claude.com)
- [Claude API 기초 과정](https://github.com/anthropics/courses/tree/master/anthropic_api_fundamentals)
