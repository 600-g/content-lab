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
)
from .prompt import CATEGORIES, GRADES, TARGETS

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

    prompt = f"""너는 두근컴퍼니의 AI 스킬 큐레이터다.

같은 주제로 기존 스킬과 신규 분석이 들어왔다. 두 개를 **합병**해서 더 풍부한 단일 스킬로 만들어라.

[기존 스킬 — {existing.get('collected_at','?')} 수집]
- 슬러그: {existing.get('name','?')}
- 카테고리: {existing.get('category','?')}
- 등급: {existing.get('grade','?')}
- 본문:
{existing.get('body','')[:8000]}

[신규 분석 — 오늘 추가]
- 슬러그(제안): {new_result.skill_name}
- 카테고리(제안): {new_result.category}
- 등급(제안): {new_result.grade}
- 요약: {new_result.summary}
- 적용메모: {new_result.memo}
- 본문:
{new_result.body_content[:8000]}

[합병 규칙]
1. 중복 문장 제거. 누락된 통찰은 통합.
2. 등급/카테고리는 더 정확한 것 선택 (사유 명시).
3. 슬러그는 기존 유지 (변경 금지).
4. 본문은 "## 핵심 패턴 / 적용 단계 / 예시 / 주의사항" 구조 유지.
5. "## 출처" 섹션은 두 출처 모두 명시 (기존 + 신규).
6. 두근컴퍼니 환경에 맞는 적용 메모 보강.

[응답 — JSON only, 코드블록 없이]
{{
  "skill_name": "{existing.get('name', new_result.skill_name)}",
  "skill_title_ko": "한국어 짧은 제목",
  "category": "8종 중 택1",
  "grade": "S/A/B/C",
  "grade_reason": "재평가 사유",
  "targets": ["적용대상"],
  "summary": "통합된 2-3줄 요약",
  "when_to_use": "통합된 트리거 조건",
  "memo": "통합된 적용 메모",
  "ai_tools": ["통합된 도구"],
  "tags": ["통합된 태그 5개 이내"],
  "difficulty": "초급/중급/고급",
  "body_content": "통합된 본문 (## 핵심 패턴 / 적용 단계 / 예시 / 주의사항 / 출처)"
}}
"""

    last_err: Exception | None = None
    raw_text: str = ""

    # 1-2단계: Gemini cloud
    for model_name in (MODEL_PRIMARY, MODEL_FALLBACK):
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"},
            )
            resp = model.generate_content(prompt)
            raw_text = resp.text or ""
            if raw_text:
                break
        except Exception as e:  # noqa: BLE001
            logger.warning("Gemini merge %s 실패: %s", model_name, e)
            last_err = e

    # 3단계: Gemma 4 로컬 폴백
    if not raw_text:
        logger.info("Gemini merge 폴백 → Gemma 4 26B")
        raw_text = call_gemma_json(prompt) or ""

    if raw_text:
        try:
            data = _extract_json(raw_text)
            # 기존 슬러그 강제
            data["skill_name"] = existing.get("name", new_result.skill_name)
            data = _validate(data)

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
