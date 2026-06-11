"""기존 SKILL.md + 신규 분석 결과 → Gemini로 합병해 더 풍부한 단일 스킬 생성.

스펙: 단순 덮어쓰기 X. 자산화 = 누적 정제.
- 출처 URL은 누적 (리스트)
- 본문 풍부화 (중복 문장은 제거, 누락된 통찰 보강)
- 등급/카테고리 재평가
- collected_at 은 최초 등록일 유지, last_updated_at 갱신
"""
from __future__ import annotations

import datetime
import logging
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from .gemini import (
    AnalysisResult, _extract_json, _validate,
    MODEL_PRIMARY, MODEL_FALLBACK, call_gemma_json,
    _quota_should_skip, _quota_increment, _is_429, _gemini_gen_config,
)
from .prompt import CATEGORIES, GRADES, TARGETS

MIN_MERGED_BODY = 1000  # 합병 결과 본문 최소 길이 — 미달 시 Gemma 보강 1회

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _parse_existing_skill_md(path: Path) -> dict:
    """기존 SKILL.md 파일에서 본문 + 메타 추출."""
    text = path.read_text(encoding="utf-8")
    # 프론트매터 추출
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    fm_text = m.group(1) if m else ""
    body = m.group(2).strip() if m else text

    meta: dict = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if line.startswith("name:"):
            meta["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("description:"):
            meta["description"] = line.split(":", 1)[1].strip()
        elif line.startswith("- ") and "source_url" in fm_text:
            pass
    # source_urls 다중 추출 (YAML 리스트 또는 단일)
    urls_m = re.search(r"source_urls?:\s*(.+?)(?=\n\w|\n---|$)", fm_text, re.DOTALL)
    urls: list[str] = []
    if urls_m:
        raw = urls_m.group(1)
        # 리스트 형식 추출
        for ln in raw.splitlines():
            s = ln.strip().lstrip("-").strip().strip('"').strip("'")
            if s.startswith("http"):
                urls.append(s)
        if not urls:
            s = raw.strip().strip('"').strip("'")
            if s.startswith("http"):
                urls.append(s)
    meta["source_urls"] = urls

    cat_m = re.search(r'category:\s*"?([^"\n]+)"?', fm_text)
    if cat_m:
        meta["category"] = cat_m.group(1).strip()
    grade_m = re.search(r'grade:\s*"?([SABC])"?', fm_text)
    if grade_m:
        meta["grade"] = grade_m.group(1)
    collected_m = re.search(r'collected_at:\s*"?(\d{4}-\d{2}-\d{2})"?', fm_text)
    if collected_m:
        meta["collected_at"] = collected_m.group(1)

    meta["body"] = body
    return meta


def merge_with_existing(
    existing_path: Path,
    new_result: AnalysisResult,
    new_source_url: str,
    new_source_type: str,
) -> AnalysisResult:
    """기존 SKILL.md + 신규 분석을 Gemini로 합병.

    실패 시 신규 결과 그대로 반환 (덮어쓰기 효과).
    """
    try:
        import google.generativeai as genai
    except ImportError:
        logger.warning("google-generativeai 미설치 → 신규 결과만 사용")
        return new_result

    existing = _parse_existing_skill_md(existing_path)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY 없음 → 신규 결과만 사용")
        return new_result

    genai.configure(api_key=api_key)

    # 출처 URL 누적
    existing_urls = existing.get("source_urls") or []
    if new_source_url not in existing_urls:
        merged_urls = existing_urls + [new_source_url]
    else:
        merged_urls = existing_urls

    # v2.3 합병 prompt — body_md 단일 필드, 새 헤딩 강제, 1500자 이상.
    # existing/new 본문은 Gemma 컨텍스트 절약 위해 4000자로 cap (기존 8000 자는 24k+ 토큰).
    new_body_full = (new_result.raw.get("body_md") or new_result.body_content or "")
    prompt = f"""너는 두근컴퍼니의 AI 스킬 큐레이터다.

같은 주제로 기존 스킬과 신규 분석이 들어왔다. **두 출처의 모든 핵심 정보를 보존**하면서 더 풍부한 단일 스킬로 합병하라.

[기존 스킬 — {existing.get('collected_at','?')} 수집]
- 슬러그: {existing.get('name','?')}
- 카테고리: {existing.get('category','?')}
- 등급: {existing.get('grade','?')}
- 본문:
{existing.get('body','')[:4000]}

[신규 분석 — 오늘 추가]
- 슬러그(제안): {new_result.skill_name}
- 카테고리(제안): {new_result.category}
- 등급(제안): {new_result.grade}
- callout: {new_result.callout or new_result.tldr}
- 본문:
{new_body_full[:4000]}

[🚨 최우선 규칙]
1. **코드/프롬프트/명령어 절대 요약 금지** — 둘 중 하나에 있던 것은 합병 본문에도 반드시 보존
2. **본문 body_md 최소 1500자** — 추상 요약 가득한 짧은 결과는 실패로 간주
3. **빈 출처 없음** — 두 출처를 다 흡수했을 때 자연스러운 분량이 나와야 함

[합병 규칙]
1. 중복 문장 제거, 누락된 통찰 통합.
2. 등급/카테고리는 더 정확한 것 택.
3. 슬러그는 **기존 그대로** 유지.
4. body_md 구조 — 새 v2.3 헤딩만 사용:
   ## 이게 뭔가요?  /  ## 따라하기  /  ## 활용 예시  /  ## 💡 아이디어 (선택)  /  ## 주의사항 (선택)
5. 옛 헤딩 금지: "두근컴퍼니 적용", "두근 환경", "핵심 패턴", "적용 단계", "How it works", "Steps".
6. callout 별도 필드 (1~2문장, body_md 안에 또 박지 말 것).
7. 출처는 body_md 안에 박지 말 것 (md_generator 가 자동 추가).

[응답 — JSON only, 코드블록 펜스 없이]
{{
  "skill_name": "{existing.get('name', new_result.skill_name)}",
  "skill_title_ko": "8-15자 동사형 한국어 제목 (이모지 X)",
  "callout": "이 스킬이 뭔지 1~2문장. 핵심 키워드 **굵게**",
  "category": "프롬프트/자동화/콘텐츠/디자인/개발/업무/기타 중 1",
  "grade": "S/A/B/C",
  "grade_reason": "재평가 사유 1줄",
  "targets": ["적용대상"],
  "summary": "통합된 2-3줄 요약",
  "when_to_use": "통합된 트리거 조건",
  "memo": "통합된 적용 메모",
  "ai_tools": ["통합된 도구 14종 중 일치"],
  "tags": ["통합된 태그 5개 이내"],
  "difficulty": "초급/중급/고급",
  "body_md": "## 이게 뭔가요?\\n... (1500자 이상, 코드/프롬프트 전문 보존, 위 v2.3 헤딩만)"
}}
"""

    last_err: Exception | None = None
    raw_text: str = ""

    # 1-2단계: Gemini cloud — quota 임계 도달 모델은 스킵, 429 시 카운터 마킹
    for model_name in (MODEL_PRIMARY, MODEL_FALLBACK):
        if _quota_should_skip(model_name):
            logger.info("Gemini merge %s quota 임계 — 스킵", model_name)
            continue
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config=_gemini_gen_config(),
            )
            resp = model.generate_content(prompt)
            raw_text = resp.text or ""
            _quota_increment(model_name)
            if raw_text:
                break
        except Exception as e:  # noqa: BLE001
            logger.warning("Gemini merge %s 실패: %s", model_name, e)
            last_err = e
            if _is_429(e):
                _quota_increment(model_name, hit_429=True)

    # 3단계: Gemma 4 로컬 폴백
    if not raw_text:
        logger.info("Gemini merge 사용 불가 → Gemma 4 로컬")
        raw_text = call_gemma_json(prompt) or ""

    if raw_text:
        try:
            data = _extract_json(raw_text)
            # 기존 슬러그 강제
            data["skill_name"] = existing.get("name", new_result.skill_name)
            data = _validate(data)

            # 합병 본문이 너무 짧으면 Gemma 보강 재요청 1회 — body_md 우선, fallback 으로 body_content
            # len=0(빈 응답)도 포함 — opt-in 트리거가 못 잡으면 본문이 완전히 비어버림
            cur_body = (data.get("body_md") or data.get("body_content") or "").strip()
            if len(cur_body) < MIN_MERGED_BODY:
                logger.info("합병 본문 %d자 — Gemma 보강 재요청", len(cur_body))
                boost_prompt = (
                    prompt
                    + "\n\n[직전 합병 본문이 너무 짧음 — 두 출처의 누락된 통찰을 모두 살려 "
                    f"최소 {MIN_MERGED_BODY + 500}자 이상 풍부하게 다시 작성. "
                    "코드/명령어/링크는 보존. JSON 만 출력]\n"
                    + "\n[직전 본문]\n" + cur_body[:3000]
                )
                boost_text = call_gemma_json(
                    boost_prompt, num_predict=8192, temperature=0.4
                ) or ""
                if boost_text:
                    try:
                        data3 = _extract_json(boost_text)
                        data3["skill_name"] = data["skill_name"]
                        data3 = _validate(data3)
                        new_body = (data3.get("body_md") or data3.get("body_content") or "").strip()
                        if len(new_body) > max(len(cur_body) + 200, 800):
                            # 본문만 교체. 메타(카테고리/등급/슬러그)는 1차 합병 유지
                            data["body_md"] = new_body
                            data["body_content"] = new_body
                            logger.info("합병 보강 채택: %d자 → %d자", len(cur_body), len(new_body))
                    except Exception as e:  # noqa: BLE001
                        logger.warning("합병 보강 응답 파싱 실패 — 원본 유지: %s", e)

            merged = AnalysisResult(
                skill_name=data["skill_name"],
                skill_title_ko=data["skill_title_ko"],
                category=data["category"],
                grade=data["grade"],
                grade_reason=data["grade_reason"],
                targets=data["targets"],
                summary=data["summary"],
                when_to_use=data["when_to_use"],
                memo=data["memo"],
                ai_tools=data.get("ai_tools", []),
                tags=data.get("tags", []),
                difficulty=data.get("difficulty", "중급"),
                body_md=data.get("body_md", ""),
                body_content=data["body_content"],
                raw=data,
            )
            # merged 결과에 누적된 source_urls 정보를 raw로 전달
            merged.raw["_merged_source_urls"] = merged_urls
            merged.raw["_merged_collected_at"] = existing.get("collected_at") or datetime.date.today().isoformat()
            merged.raw["_is_merged"] = True
            logger.info("스킬 합병 완료: %s (출처 %d→%d)", merged.skill_name, len(existing_urls), len(merged_urls))
            return merged
        except Exception as e:  # noqa: BLE001
            logger.warning("합병 JSON 파싱 실패: %s", e)
            last_err = e

    logger.warning("합병 실패 (모든 LLM 시도 끝), 신규 결과 사용: %s", last_err)
    return new_result
