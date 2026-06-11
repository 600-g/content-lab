💡 이 스킬은 **Claude Code 환경에서 카드뉴스 자동화 에이전트를 구축**하는 워크플로우로, 엑셀/PDF 같은 구조화 데이터를 입력하면 **콘텐츠 추출 → 카드뉴스 텍스트 + 시각적 레이아웃까지 자동 구성**하는 무료 자동화 시스템입니다.

## 이게 뭔가요?

**대량 콘텐츠(카드뉴스·보고서)를 주기적으로 제작할 때 반복적인 수작업을 줄이기 위한 자동화 에이전트**. 구조화된 데이터(엑셀 시트·표·목록 등)를 입력하면 에이전트가 내용을 추출·가공하고 카드뉴스에 적합한 텍스트·레이아웃을 자동 구성.

**Claude Code 환경에서 구축**하는 이유:
- Zapier·Make 같은 외부 자동화 도구 **없이도 같은 워크플로우 구현 가능**
- **Claude Code + GitHub Actions 조합** = 정기 실행 + 트리거 자동화
- 모든 단계가 **코드로 제어** → 본인 입맛에 맞게 디테일 조정 가능

**원본 자료 구성**:

| 자료 | 내용 |
|---|---|
| (필독) 시트 자료 활용 방법 (PNG) | 137KB — 가이드 이미지 |
| 마스터_썸네일 (PDF) | 209KB — 디자인 reference |
| 클로드 코드로 카드뉴스 자동화 에이전트 만들기_마스터 시트 자료 (XLSX) | 19KB — 실 데이터 템플릿 |
| 클로드코드 카드뉴스 자동화 에이전트 (v0.3 PDF) | 1,000KB — 풀 가이드 |

💰 유료 필요: Claude Max (Claude Code 포함)
✅ 무료 대안: Claude 무료 + GitHub Actions 무료 티어 / 또는 Gemini CLI + GitHub Actions

## 따라하기

### STEP 1. 데이터 준비

카드뉴스에 들어갈 원본 데이터를 **엑셀 시트나 구조화된 PDF** 형태로 정리:

| 컬럼 | 예시 |
|---|---|
| 슬라이드 번호 | 1, 2, 3, ... |
| 카테고리 | AI 뉴스 / 제품 추천 / 트렌드 |
| 헤드라인 | "ChatGPT 무료 한도 늘었다" |
| 본문 (3-5줄) | "Pro 1.5배, Plus 2배 ..." |
| 이미지 키워드 | "AI 로봇 / 차트" |
| CTA | "더 알아보기" |

**구조화 수준이 높을수록 결과물 품질도 올라감**. 컬럼 정의 명확하면 에이전트가 정확하게 추출.

### STEP 2. 에이전트 설계

Claude Code 환경에서 에이전트 역할 정의. `CLAUDE.md` 또는 프로젝트 루트에:

```markdown
# 카드뉴스 자동화 에이전트

## 역할
- 입력: 엑셀 시트 / PDF (구조화된 콘텐츠 데이터)
- 출력: 인스타 캐러셀 콘텐츠 (10장 PDF 또는 이미지 시퀀스)

## 처리 단계
1. 시트 파일 읽기 (openpyxl / pandas)
2. 각 행을 슬라이드 1장으로 매핑
3. 헤드라인·본문·CTA 추출
4. HTML 템플릿에 데이터 삽입
5. HTML → PNG/PDF 변환 (Playwright / wkhtmltopdf)
6. 인스타 1080×1080 정사각형 출력

## 규칙
- 헤드라인: 20자 이내, 본문: 3-5줄
- 컬러: 본인 브랜드 톤 (#FF6B9D 핑크)
- 폰트: Pretendard 또는 Noto Sans KR
```

### STEP 3. 자동화 구현

데이터 입력 시 자동 실행되도록 코드 작성:

```python
# card_news_agent.py
import pandas as pd
from playwright.sync_api import sync_playwright

def generate_card_news(xlsx_path, output_dir):
    df = pd.read_excel(xlsx_path)
    for idx, row in df.iterrows():
        html = render_template(row['헤드라인'], row['본문'], row['CTA'])
        save_as_png(html, f"{output_dir}/slide_{idx+1}.png")
    
    # PDF 묶기
    merge_pngs_to_pdf(output_dir, f"{output_dir}/final.pdf")

# GitHub Actions 트리거
# .github/workflows/card-news.yml — Sheets 변경 시 자동 실행
```

### STEP 4. GitHub Actions 연동 (선택)

`.github/workflows/card-news.yml`:

```yaml
name: Card News Generator

on:
  schedule:
    - cron: '0 9 * * *'   # 매일 오전 9시
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install pandas openpyxl playwright
      - run: playwright install chromium
      - run: python card_news_agent.py
      - uses: actions/upload-artifact@v4
        with:
          name: card-news
          path: output/*.png
```

### STEP 5. 디자인 결과물 검토

AI 가 생성한 시각적 결과물의 **최종 디자인 검토는 사람이 반드시**. AI 가 만든 레이아웃은 폰트·색상 조합 일관성 부족할 수 있으므로 **Canva 후처리** 권장.

## 활용 예시

- **인스타 운영자 — 주 3회 캐러셀** — 엑셀에 주제·키워드만 정리 → 카드뉴스 자동 생성. 매일 다른 카테고리 자동 양산
- **콘텐츠 마케팅 에이전시** — 클라이언트별 10-20개 카드뉴스 / 주 → 1명이 클라이언트 10+ 곳 처리 가능
- **블로거·뉴스레터 운영자** — 매주 수집된 AI 뉴스 → 카드뉴스 자동 변환 → 인스타·뉴스레터·블로그 동시 배포
- **교육 콘텐츠 — 강의 슬라이드 자동화** — 강의 노트 엑셀 → 카드뉴스 자동 생성 → 학생 배포용 자료 0초에 완성
- **e커머스 — 상품 카드 양산** — 신상 등록 시마다 카드뉴스 (상품명·특징·가격·CTA) 자동 생성 → 인스타·블로그 동시 게시
- **소셜미디어 에이전시 1인 사업** — 카드뉴스 자동화 + GitHub Actions 정기 실행 → 클라이언트당 월 콘텐츠 100+ 개 제공 패키지 $300-500
- **개인 브랜딩** — 본인 매주 학습 정리를 카드뉴스화 → 인스타 시리즈 운영. 6개월간 콘텐츠 자산 누적
- **B2B SaaS 마케팅** — 제품 업데이트·고객 사례를 매주 카드뉴스로 → LinkedIn·트위터·블로그 자동 배포

## 💡 아이디어

- **소상공인 콘텐츠 대행 자동화** — 카드뉴스 에이전트 + 제품 후기 프롬프트 조합 → 고객사별 SNS 콘텐츠 반자동 대량 생산 → 월 $200-500/매장
- **뉴스레터 자동화 SaaS** — 매주 사용자 관심사 키워드 수집 → 카드뉴스 자동 변환 → 이메일 발송 → 월 $5-10 구독
- **본인 브랜드 카드뉴스 빌더 노코드** — 비개발자도 사용할 수 있는 GUI → 엑셀 + 디자인 템플릿 선택 → 카드뉴스 자동 생성 → 월 $10-20
- **HTML→PNG 변환 마이크로 SaaS** — 본인의 카드뉴스 자동화에서 만든 HTML→PNG 모듈을 SaaS 로 분리 → 다른 개발자 API 사용 → 호출당 $0.01
- **사내 보고서 자동화** — 회사 데이터 시트 + 보고서 템플릿 → 매주 임원 보고서 자동 생성 → B2B 컨설팅 ($3,000-5,000/회)
- **AI 강의 콘텐츠 — 4시간 강의 패키지** ($100-200/회)
- **카드뉴스 디자인 마켓플레이스** — 카테고리별(뉴스·교육·제품·뷰티) 디자인 템플릿 100+ 종 → $10-30/팩

## 주의사항

- **원본 데이터 구조화 수준이 8할** — 엑셀 컬럼이 모호하면 에이전트가 정확한 내용 추출 어려움. **컬럼 정의 명확하게** + 데이터 검증 단계 추가
- **AI 디자인 일관성 부족** — AI 가 생성하는 레이아웃은 폰트·색상 조합이 일관되지 X. **Canva 후처리 권장** 또는 **HTML 템플릿 고정**해서 변형 X
- **사람 최종 검수 필수** — 광고성 표현·민감 정보·오타 등은 사람이 반드시 확인. 자동 발행 X
- **이미지 권한** — AI 가 추천한 이미지 키워드로 무료 이미지 사이트(Unsplash·Pexels) 사용. **저작권 확인 필수**
- **GitHub Actions 한도** — 무료 티어 월 2,000분. 카드뉴스 자동화 빈도 높으면 한도 초과. 자체 호스팅 서버 검토
- **AI 비용 누적** — 매일 카드뉴스 10개 자동 생성 = Claude API 토큰 빠르게 소비. 월 비용 모니터링 필수
- **HTML→PNG 변환 도구** — Playwright 가 가장 안정. wkhtmltopdf 는 한글 폰트 문제 자주 발생

## 출처

- [클로드 코드로 카드뉴스 자동화 에이전트 만들기 (Google Drive)](https://drive.google.com/drive/mobile/folders/1VK_GmuLkmECb77XMI2pYPp5gdQx00XTN)
- 자료 구성: (필독) 시트 활용 가이드 PNG / 마스터 썸네일 PDF / 마스터 시트 자료 XLSX / 풀 가이드 PDF v0.3
