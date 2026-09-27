---
name: free-icon-sites-replace-emoji-prompt
description: 이 스킬은 AI 가 만든 화면의 **이모지 아이콘**을 **Lucide·Phosphor 같은 무료 오픈소스 아이콘 세트**로 통일해 화면이 싸 보이는 '밤티'를 벗어나게 하는 스킬입니다.
origin: content-lab
grade: S
difficulty: 초급
category: 디자인
ai_tools: ["Claude", "Claude Code", "GPT", "Gemini"]
sources:
  - https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw
---

# 이모지를 무료 아이콘 세트로 교체

💡 이 스킬은 AI 가 만든 화면의 **이모지 아이콘**을 **Lucide·Phosphor 같은 무료 오픈소스 아이콘 세트**로 통일해 화면이 싸 보이는 '밤티'를 벗어나게 하는 스킬입니다.

## 이게 뭔가요?

클로드에게 화면(랜딩 페이지, 카드 UI 등)을 맡기면, 아이콘을 따로 정해 주지 않은 경우 ☕·🚀·✨ 같은 **이모지**로 아이콘 자리를 채우는 일이 많습니다. 이모지는 OS·브라우저마다 모양이 다르고 색감도 제각각이라 화면 전체가 싸 보이는 원인이 됩니다.

해결법은 간단합니다. 쓸 **아이콘 세트를 이름으로 딱 하나 지정**해 주면, 화면 전체의 선 굵기와 모양이 한 가지로 맞춰집니다. 이 자료는 무료로 쓸 수 있는 오픈소스 아이콘 사이트 다섯 곳(Lucide, Heroicons, Phosphor, Tabler Icons, Iconify)과, 이모지를 실제 아이콘 세트로 바꾸게 하는 프롬프트를 함께 담고 있습니다.

Claude, Claude Code 등 화면 코드를 만들어 주는 AI 어디서나 쓸 수 있습니다. 다섯 사이트 모두 무료 오픈소스라 별도 비용이 없습니다.

- ✅ 무료 대안: Claude Max 가 없어도 Gemini·ChatGPT 무료 플랜에 같은 프롬프트를 넣어 쓸 수 있습니다.

## 따라하기

### STEP 1 · 3분 — 만들 화면에 맞는 아이콘 세트를 고른다

| 사이트 | 이럴 때 | 특징 |
|---|---|---|
| Lucide | 무난하고 깔끔한 기본 세트가 필요할 때 | 아이콘 1,856개(검색창 표시 기준). 색·크기·선 굵기를 바꿀 수 있음. ISC 라이선스 |
| Heroicons | 테일윈드 CSS로 만든 화면일 때 | Tailwind CSS 제작팀이 만든 316개. Outline·Solid·Mini·Micro 네 가지 스타일. MIT 라이선스 |
| Phosphor | 굵기를 화면 분위기에 맞추고 싶을 때 | 9,072개. Thin·Light·Regular·Bold·Fill·Duotone 여섯 굵기. MIT 라이선스 |
| Tabler Icons | 개수가 많고 상업용으로 쓸 세트가 필요할 때 | 6,220개. 무료 오픈소스 플랜에 MIT License·Personal & Commercial License 표기 |
| Iconify | 여러 세트를 한 번에 찾아보고 싶을 때 | 222개 아이콘 세트, 30만 개가 넘는 오픈소스 아이콘을 한곳에서 검색. 라이선스는 세트마다 다름 |

1. 위 표에서 만들 화면에 맞는 세트를 **하나만** 고릅니다. 잘 모르겠다면 Lucide 가 무난합니다.

### STEP 2 · 3분 — 세트 이름과 아이콘 이름을 확인한다

2. 선택한 사이트에서 필요한 아이콘을 검색합니다. `coffee`, `truck`, `shield-check` 처럼 영문 이름이 나옵니다.
3. 이 이름을 두세 개만 적어 둡니다. 이름을 알려 주면 클로드가 같은 세트에서 정확히 골라 씁니다.
4. Iconify 에서 찾은 아이콘은 **세트 이름과 라이선스를 함께** 확인합니다.

### STEP 3 · 5분 — 프롬프트로 이모지를 아이콘 세트로 바꾼다

5. 이미 만든 화면이 있다면 아래 프롬프트를 그대로 입력합니다. 아이콘 이름은 STEP 2 에서 적어 둔 것으로 바꿉니다.

```
방금 만든 화면에서 이모지로 된 아이콘을 전부 Lucide 아이콘으로 바꿔줘.
- 기능 카드: coffee, truck, leaf, star
- 버튼 안 화살표: arrow-right
아이콘은 한 세트만 쓰고, 크기와 선 굵기(stroke width)는 화면 전체에서 똑같이 맞춰줘. 본문과 버튼 글자에는 이모지를 넣지 마.
```

6. 처음부터 새 화면을 만들 때는 아래 프롬프트를 씁니다. `[우리 서비스 한 줄 설명]` 자리에 서비스 설명을 넣습니다.

```
[우리 서비스 한 줄 설명]의 랜딩 페이지를 만들어줘. 아이콘은 Phosphor의 Regular 굵기만 쓰고, 이모지는 화면 어디에도 쓰지 마. 아이콘마다 어떤 이름을 썼는지 마지막에 목록으로 알려줘.
```

7. 성공하면 화면의 이모지가 사라지고, 같은 굵기의 선 아이콘으로 통일됩니다. 두 번째 프롬프트는 마지막에 사용한 아이콘 이름 목록도 함께 받을 수 있어 검수하기 편합니다.

## 활용 예시

- **기존 화면 정리**: 클로드가 만든 카페 소개 페이지에 ☕🚚🌿⭐ 이모지가 카드마다 박혀 있다 → 위 첫 번째 프롬프트를 입력 → `coffee`, `truck`, `leaf`, `star` Lucide 아이콘으로 바뀌고 버튼의 화살표도 `arrow-right` 로 통일됩니다.
- **처음부터 새로 만들기**: 서비스 한 줄 설명과 함께 두 번째 프롬프트를 입력 → Phosphor Regular 굵기 아이콘만 쓴 랜딩 페이지가 나오고, 마지막에 아이콘별 사용 이름 목록이 붙습니다.
- **테일윈드 화면**: 테일윈드 CSS 로 만든 화면이라면 프롬프트의 세트 이름만 `Heroicons` 로 바꾸고 스타일(Outline 등)을 함께 지정합니다.

## 💡 아이디어

- 프로젝트마다 사용할 아이콘 세트와 굵기를 CLAUDE.md 에 한 줄로 적어 두면, 매번 프롬프트에 쓰지 않아도 같은 스타일이 유지됩니다.
- 랜딩 페이지·블로그 썸네일·상세페이지 목업 등 외주·판매용 결과물의 완성도를 올리는 마무리 단계로 넣을 수 있습니다.

## 주의사항

- 아이콘만 바꿔도 인상이 크게 달라지지만, **색·글꼴·여백**은 따로 다듬어야 합니다.
- 한 화면에 여러 세트를 섞으면 선 굵기가 달라져 다시 어수선해 보입니다. **세트는 하나만** 고르세요.
- 라이선스와 아이콘 개수는 2026년 9월 25일 각 공식 페이지를 직접 열어 본 내용 기준입니다. 이후 달라질 수 있습니다.
- Iconify 의 개별 세트는 라이선스가 서로 다르니 쓰기 전에 세트 페이지에서 확인하세요.
- 공식 참고 자료: Lucide(아이콘 검색), Heroicons(Tailwind CSS 제작팀 아이콘), Phosphor(여섯 굵기 아이콘), Tabler Icons(MIT 라이선스 아이콘), Iconify(아이콘 세트 통합 검색) 각 공식 사이트.

## 출처

- [https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw](https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw)
