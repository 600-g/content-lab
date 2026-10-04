---
name: tencent-cloudflare-oss-ai-tools-3
description: 이 스킬은 텐센트와 클라우드플레어가 같은 주에 공개한 브라우저 자동화·보안 감사·지식베이스용 **오픈소스 AI 도구 3종**을 GitHub에서 무료로 받아 설치하는 스킬입니다.
origin: content-lab
grade: C
difficulty: 초급
category: 개발
ai_tools: ["도구무관"]
sources:
  - https://yeongseon.kr/archive/3d8d86104de2801eb0c7fc59e09a6344.html?fbclid=PAVERFWAUlrntleHRuA2FlbQIxMABwZG9mAmZkaWQWUPMGrgd2AmXWvAKPDrWRqt2sU1003nNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp2bqxqhYJw5zRrbt5RoIvH0b3ff_pK_a8_FKxBaHgBg0Rq8T-g5s0q7tKqIb_aem_1DQmyJyVTQ9sw_LU83Zg3Q
---

# 오픈소스 AI 도구 3종 설치하기

💡 이 스킬은 텐센트와 클라우드플레어가 같은 주에 공개한 브라우저 자동화·보안 감사·지식베이스용 **오픈소스 AI 도구 3종**을 GitHub에서 무료로 받아 설치하는 스킬입니다.

## 이게 뭔가요?
2026년 9월 셋째 주, 텐센트(Tencent)와 클라우드플레어(Cloudflare)가 같은 주에 각각 오픈소스 AI 도구를 GitHub에 공개했다. 두 회사 모두 사내에서 실제로 쓰던 도구를 외부에 무료로 풀었다는 점이 특징이다. 공개된 도구는 총 3개로, 브라우저 자동화용 **Browser Skill**, 보안 점검용 **security-audit-skill**, 지식베이스·RAG용 **WeKnora** 다.

세 도구 모두 특정 AI 모델에 종속되지 않는 범용 오픈소스이며, 별도 구독료 없이 GitHub 저장소를 클론해 로컬이나 서버에 설치해 쓰는 방식이다. ✅ 무료 대안: 전부 오픈소스라 별도 유료 결제 없이 바로 사용 가능하다.

원문 작성자는 세 도구의 설치·활용법을 정리한 별도 가이드북(Google Docs, v1, 2026-09-20)도 함께 공개했으며, 이 가이드북에 실제 설치 스크린샷과 활용 절차가 담겨 있다.

## 따라하기
1. **Browser Skill** (텐센트) 설치
   - GitHub: `github.com/Tencent/BrowserSkill`
   - 브라우저 조작을 스킬 단위로 정의해 에이전트가 웹사이트를 클릭·입력·스크롤하도록 만드는 오픈소스다. 저장소를 클론한 뒤 README 안내에 따라 의존성을 설치하고, 원하는 브라우저 동작을 스킬로 등록해 실행한다.

2. **security-audit-skill** (클라우드플레어) 설치
   - GitHub: `github.com/cloudflare/security-audit-skill`
   - 코드베이스나 인프라 설정을 스캔해 보안 취약점을 점검하는 스킬이다. 저장소를 로컬에 클론한 뒤, 점검 대상 리포지토리 경로를 지정해 감사 스킬을 실행하면 취약점 리포트가 나온다.

3. **WeKnora** (텐센트) 설치
   - GitHub: `github.com/Tencent/WeKnora`
   - 문서·데이터를 인덱싱해 검색·질의응답(RAG)에 활용할 수 있는 지식베이스 엔진이다. 저장소를 클론하고 설정 파일에 문서 소스를 연결한 뒤 서버를 띄우면 자체 지식베이스 검색 API로 쓸 수 있다.

4. **설치·활용 가이드북 확인**
   - 위 3개 도구의 설치부터 실전 활용까지 정리한 가이드북이 별도로 공개되어 있다. 원문에 첨부된 "무료 AI 오픈소스 3종 설치·활용 가이드북 (v1, 2026-09-20)" Google Docs 링크에서 스크린샷과 함께 자세한 절차를 확인할 수 있다.

## 활용 예시
- 반복적인 웹 리서치 업무를 자동화하고 싶다면 → **Browser Skill**을 설치해 특정 사이트에서 데이터를 수집하는 스킬을 등록 → 매번 수동으로 클릭하던 작업을 스킬 실행 한 번으로 대체
- 사내 코드나 서버 설정에 보안 취약점이 있는지 점검하고 싶다면 → **security-audit-skill**로 리포지토리를 스캔 → 취약점 목록과 우선순위가 정리된 리포트를 받는다
- 회사 문서·매뉴얼을 모아 챗봇처럼 질의응답하고 싶다면 → **WeKnora**에 문서를 색인 → "우리 회사 환불 정책이 뭐야?" 같은 질문에 문서 기반으로 답변받기

## 주의사항
- 원문에는 각 도구의 상세 사용법이 나와 있지 않으며, 실제 설치·실행 절차는 각 GitHub 저장소의 README를 직접 확인해야 한다.
- 가이드북은 원문 작성자가 만든 외부 Google Docs 문서이므로, 접근 권한이나 버전(v1, 2026-09-20)이 이후 바뀔 수 있다.
- 세 도구 모두 오픈소스이지만 서버 배포·API 키 발급 등 인프라 설정이 필요할 수 있어 코딩 경험이 없으면 설치 난이도가 있을 수 있다.

## 출처

- [https://yeongseon.kr/archive/3d8d86104de2801eb0c7fc59e09a6344.html?fbclid=PAVERFWAUlrntleHRuA2FlbQIxMABwZG9mAmZkaWQWUPMGrgd2AmXWvAKPDrWRqt2sU1003nNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp2bqxqhYJw5zRrbt5RoIvH0b3ff_pK_a8_FKxBaHgBg0Rq8T-g5s0q7tKqIb_aem_1DQmyJyVTQ9sw_LU83Zg3Q](https://yeongseon.kr/archive/3d8d86104de2801eb0c7fc59e09a6344.html?fbclid=PAVERFWAUlrntleHRuA2FlbQIxMABwZG9mAmZkaWQWUPMGrgd2AmXWvAKPDrWRqt2sU1003nNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp2bqxqhYJw5zRrbt5RoIvH0b3ff_pK_a8_FKxBaHgBg0Rq8T-g5s0q7tKqIb_aem_1DQmyJyVTQ9sw_LU83Zg3Q)
