---
name: 3-day-app-launch-pipeline
description: 3일 만에 앱을 출시하는 AI 6단계 파이프라인 — Claude in Chrome(시장조사) → Claude Cowork(데이터 정리) → Gemini Pro(아이디어 회의) → Claude Artifacts(구현) → Claude Design(디자인) → Replit×Expo(배포) 각 단계의 결과물이 다음 단계 입력으로 연결되는 실전 출시 가이드
origin: content-lab
sources:
  - https://ink-jay-f32.notion.site/3-Ai-350f2e12ad5c81e0b0d8f283a89d7504
---

# 3일 앱 출시 파이프라인 (AI 6단계)

## 이게 뭔가요?

각 단계의 결과물이 다음 단계의 입력으로 연결되는 파이프라인 구조. 6단계 각각에 최적의 AI 도구 조합.

| 단계 | 도구 | 핵심 역할 |
|---|---|---|
| 🔭 시장조사 | Claude in Chrome | 웹페이지 실시간 분석·요약·추출 |
| 🗂️ 데이터 정리 | Claude Cowork | 로컬 파일 자동 분류·정제 |
| 💡 아이디어 회의 | Gemini Pro | 100만 토큰으로 대용량 브레인스토밍 |
| ⚙️ 구현 | Claude Artifacts | 코드·UI·문서 인터랙티브 프로토타이핑 |
| 🎨 디자인 | Claude Design | UI/UX 목업·디자인 시스템·아이콘 |
| 🚀 배포 | Replit × Expo | 백엔드 클라우드 + 멀티플랫폼 앱 |

## 따라하기

### 🔭 1단계. Claude in Chrome — 시장조사
1. Chrome 웹스토어에서 Claude for Chrome 설치
2. 경쟁사 웹사이트·앱스토어 리뷰 페이지 열고 사이드패널 Claude
3. "이 페이지에서 사용자 불만 키워드 추출해줘"
4. 여러 페이지 순회 → 누적 데이터 비교·분석
5. 인사이트를 마크다운 보고서로 정리

### 🗂️ 2단계. Claude Cowork — 데이터 정리
1. Cowork 데스크탑 앱 설치 + 원자료 폴더 지정
2. 폴더를 작업 컨텍스트로 연결
3. "중복 제거하고 카테고리별로 분류해줘"
4. 정리 결과물 검토·수정
5. 다음 단계 입력 자료로 저장

### 💡 3단계. Gemini Pro — 아이디어 회의
1. Google AI Studio 접속 + 시장조사 데이터 업로드
2. "이 데이터로 해결할 수 있는 사용자 문제 10가지"
3. 팀과 함께 투표·점수 부여
4. 선정 아이디어에 "장단점과 MVP 기능 정의"
5. 최종 명세서 → 구현 단계 전달

### ⚙️ 4단계. Claude Artifacts — 구현
1. Claude.ai 새 대화 + 명세서 붙여넣기
2. "React 컴포넌트 만들어줘" / "랜딩 페이지 HTML"
3. 아티팩트 패널 실시간 확인 → 반복 수정
4. 완성 코드 복사 → 프로젝트 파일 통합
5. 여러 아티팩트 조합 → 전체 앱 구조

### 🎨 5단계. Claude Design — 디자인
1. 브랜드 키워드 + 디자인 요구사항 설명
2. "온보딩 화면 3개 목업" / "색상 팔레트+타이포"
3. 아티팩트에서 미리보기·수정
4. CSS 변수·컴포넌트 스타일 추출
5. Figma MCP 연동 (선택)

### 🚀 6단계. Replit × Expo — 배포
1. Replit 새 프로젝트 + 백엔드 코드 붙여넣어 실행
2. Deploy 버튼으로 공개 URL 배포
3. `npx create-expo-app` + Replit API URL 환경변수
4. `npx expo start` → Expo Go로 실제 디바이스 테스트
5. `eas build` + `eas submit` → App Store / Google Play

## 주의사항

- 3일은 이상치, 실제 1-2주 권장 (앱스토어 심사 포함)
- Claude Cowork 보안 — 별도 격리 폴더 권장
- Replit 무료는 sleep 모드 빈번 — Pro $25/월
- Expo eas build 무료 월 30빌드 한도
- Apple Developer $99/년 필수 (App Store)
- Google Play 일회성 $25
- AI 결과물은 80% 초안 — 본인 최종 검토 + 보안·성능 점검

## 출처
- [3일 앱 출시 파이프라인](https://ink-jay-f32.notion.site/3-Ai-350f2e12ad5c81e0b0d8f283a89d7504)
