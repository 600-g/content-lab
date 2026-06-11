---
name: card-news-automation-agent
description: 구조화된 자료(시트, PDF)를 입력으로 받아 카드뉴스 제작 과정을 자동화하는 에이전트를 구축할 때 사용합니다. 콘텐츠 제작 효율을 극대화할 수 있습니다. Use when: - 대량의 콘텐츠(카드뉴스, 보고서 등)를 주기적으로 제작해야 할 때 - 콘텐츠의 기획-제작-배포 과정에 반복적인 수작업이 많을 때 - 구조화된 데이터(표, 목록)를 시각적인 콘텐츠로 변환해야 할 때
origin: content-lab
grade: A
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code", "Gemini"]
sources:
  - https://drive.google.com/drive/mobile/folders/1VK_GmuLkmECb77XMI2pYPp5gdQx00XTN?usp=sharing&fbclid=PAVERFWAR61fZleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafICs6AuzCfHSH46zXzOKHwRfXTp3Wk4pbuI1sqdj-Kgm-mP780K1DUHdZeUg_aem_qoXaqOzMj4wyzOF87sjptg
---
# 카드뉴스 자동화 에이전트 구축

구조화된 자료(시트, PDF)를 입력으로 받아 카드뉴스 제작 과정을 자동화하는 에이전트를 구축할 때 사용합니다. 콘텐츠 제작 효율을 극대화할 수 있습니다. Use when: - 대량의 콘텐츠(카드뉴스, 보고서 등)를 주기적으로 제작해야 할 때 - 콘텐츠의 기획-제작-배포 과정에 반복적인 수작업이 많을 때 - 구조화된 데이터(표, 목록)를 시각적인 콘텐츠로 변환해야 할 때

구조화된 자료(시트, PDF)를 입력으로 받아 카드뉴스 제작 과정을 자동화하는 에이전트를 구축할 때 사용합니다. 콘텐츠 제작 효율을 극대화할 수 있습니다. Use when: - 대량의 콘텐츠(카드뉴스, 보고서 등)를 주기적으로 제작해야 할 때 - 콘텐츠의 기획-제작-배포 과정에 반복적인 수작업이 많을 때 - 구조화된 데이터(표, 목록)를 시각적인 콘텐츠로 변환해야 할 때

구조화된 자료(시트, PDF)를 입력으로 받아 카드뉴스 제작 과정을 자동화하는 에이전트를 구축할 때 사용합니다. 콘텐츠 제작 효율을 극대화할 수 있습니다.

## 언제 쓰나

- 대량의 콘텐츠(카드뉴스, 보고서 등)를 주기적으로 제작해야 할 때
- 콘텐츠의 기획-제작-배포 과정에 반복적인 수작업이 많을 때
- 구조화된 데이터(표, 목록)를 시각적인 콘텐츠로 변환해야 할 때

## 원리

이 스킬은 클로드 코드(Claude Code) 환경에서 에이전트(Agent)를 구축하여, 입력된 구조화된 데이터(예: 엑셀 시트)를 분석하고, 이를 카드뉴스 형식의 콘텐츠로 자동 변환하는 워크플로우를 만듭니다. 핵심은 데이터 입력 → 내용 추출/가공 → 시각적 레이아웃 구성의 자동화입니다.

## 단계

1) **데이터 준비:** 카드뉴스에 들어갈 원본 데이터를 엑셀 시트나 구조화된 PDF 형태로 정리합니다. 2) **에이전트 설계:** 클로드 코드 환경에서 에이전트의 역할을 정의하고, 데이터 입력 및 콘텐츠 생성 로직을 설계합니다. 3) **자동화 구현:** 데이터가 입력되면, 에이전트가 자동으로 내용을 추출하고, 카드뉴스에 적합한 텍스트와 레이아웃을 구성하도록 코드를 작성하고 테스트합니다.

## 예시

입력: [클로드 코드 마스터 시트 자료.xlsx] (주제별 핵심 키워드 및 내용)
출력: [카드뉴스 자동화 에이전트 실행 결과] (시각적 레이아웃이 적용된 카드뉴스 PDF 또는 이미지 시퀀스)

## 두근컴퍼니 적용

두근컴퍼니 환경에 적용 시, 클로드 코드를 핵심 개발 환경으로 사용합니다. 특히, 데이터 처리 및 자동화 로직 구현에 Claude Code (CLI)를 활용하여 에이전트를 구축합니다. 기존의 자동화 도구(Zapier/Make)가 필요했던 과정을 Claude Code + GitHub Actions 조합으로 대체하여 구현할 수 있습니다.

## ️ 주의

- 원본 데이터의 구조화 수준이 낮으면 에이전트가 정확한 내용을 추출하기 어렵습니다.
- 에이전트가 생성하는 시각적 결과물(이미지/PDF)의 최종 디자인 검토는 사람이 반드시 거쳐야 합니다.

## 출처

- [https://drive.google.com/drive/mobile/folders/1VK_GmuLkmECb77XMI2pYPp5gdQx00XTN?usp=sharing&fbclid=PAVERFWAR61fZleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafICs6AuzCfHSH46zXzOKHwRfXTp3Wk4pbuI1sqdj-Kgm-mP780K1DUHdZeUg_aem_qoXaqOzMj4wyzOF87sjptg](https://drive.google.com/drive/mobile/folders/1VK_GmuLkmECb77XMI2pYPp5gdQx00XTN?usp=sharing&fbclid=PAVERFWAR61fZleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafICs6AuzCfHSH46zXzOKHwRfXTp3Wk4pbuI1sqdj-Kgm-mP780K1DUHdZeUg_aem_qoXaqOzMj4wyzOF87sjptg)

---
