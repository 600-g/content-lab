"""LLM 호출 (Gemini → Gemma 4) + JSON 파싱.

폴백 체인:
1. Gemini 2.5 Flash (cloud, 무료 20/day)
2. Gemini 2.0 Flash (cloud, 폴백)
3. Gemma 4 26B (local Ollama, 무제한, 약 15-30초)
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import requests

from .prompt import build_prompt, CATEGORIES, GRADES, TARGETS

logger = logging.getLogger(__name__)

MODEL_PRIMARY = "gemini-2.5-flash"
MODEL_FALLBACK = "gemini-2.0-flash"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma4:26b")
GEMMA_TIMEOUT = int(os.getenv("GEMMA_TIMEOUT", "120"))


def call_gemma_json(prompt: str) -> Optional[str]:
    """Gemma 4 26B 로컬 호출. JSON 응답 강제."""
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": GEMMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=GEMMA_TIMEOUT,
        )
        r.raise_for_status()
        return r.json().get("response", "")
    except Exception as e:  # noqa: BLE001
        logger.warning("Gemma 4 호출 실패: %s", e)
        return None


@dataclass
class AnalysisResult:
    skill_name: str  # kebab-case 슬러그
    skill_title_ko: str
    category: str
    grade: str
    grade_reason: str
    targets: list[str]
    summary: str
    when_to_use: str
    memo: str
    ai_tools: list[str]
    tags: list[str]
    difficulty: str
    # 표준 8섹션 (TEMPLATE.md v1)
    tldr: str = ""
    how_it_works: str = ""
    steps: str = ""
    examples: str = ""
    doogeun: str = ""
    caveats: str = ""
    body_content: str = ""  # 레거시 호환용 (deprecated)
    raw: dict = field(default_factory=dict)
    ok: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "skill_title_ko": self.skill_title_ko,
            "category": self.category,
            "grade": self.grade,
            "grade_reason": self.grade_reason,
            "targets": self.targets,
            "summary": self.summary,
            "when_to_use": self.when_to_use,
            "memo": self.memo,
            "ai_tools": self.ai_tools,
            "tags": self.tags,
            "difficulty": self.difficulty,
            "body_content": self.body_content,
            "ok": self.ok,
            "error": self.error,
        }


def _compose_body(d: dict) -> str:
    """8섹션 필드 → 표준 마크다운 본문."""
    return f"""> **TL;DR** — {d.get('tldr','(해당 없음)')}

> **메타** 등급 {d.get('grade','?')} · 카테고리 {d.get('category','?')} · 난이도 {d.get('difficulty','중급')}
> **도구** {', '.join(d.get('ai_tools',[])) or '도구무관'}
> **적용 대상** {', '.join(d.get('targets',[])) or '공통'}

---

## 🎯 When to use (언제 쓰는가)

{d.get('when_to_use','(해당 없음)')}

## 🔑 How it works (작동 원리)

{d.get('how_it_works','(해당 없음)')}

## 🛠 Steps (적용 단계)

{d.get('steps','(해당 없음)')}

## 💡 Examples (예시)

{d.get('examples','(해당 없음)')}

## 🏢 두근 환경 적용

{d.get('doogeun','(해당 없음)')}

## ⚠️ Caveats (주의사항)

{d.get('caveats','(해당 없음)')}

## 📎 Sources (출처)

{d.get('sources', '(출처 정보 없음)')}
"""


def _extract_json(text: str) -> dict:
    """Gemini 응답에서 JSON 블록 추출. 코드펜스 제거."""
    s = text.strip()
    # 코드펜스 제거
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    # 첫 { 부터 마지막 } 까지
    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end < 0:
        raise ValueError(f"JSON 블록 없음: {s[:200]}")
    return json.loads(s[start : end + 1])


def _validate(d: dict) -> dict:
    """필수 필드/enum 검증 + 정규화. TEMPLATE.md v1 기준."""
    required = [
        "skill_name", "skill_title_ko", "category", "grade", "grade_reason",
        "targets", "summary", "when_to_use", "memo",
    ]
    # 8섹션 필드 (없으면 "(해당 없음)" 로 기본값)
    section_fields = ["tldr", "how_it_works", "steps", "examples", "doogeun", "caveats"]
    for k in required:
        if k not in d:
            raise ValueError(f"필수 필드 누락: {k}")
    for k in section_fields:
        if not d.get(k):
            d[k] = "(해당 없음)"
    # 레거시 body_content 호환 — 없으면 8섹션 합성
    if not d.get("body_content"):
        d["body_content"] = _compose_body(d)

    if d["category"] not in CATEGORIES:
        logger.warning("unknown category %s → 기타", d["category"])
        d["category"] = "기타"
    if d["grade"] not in GRADES:
        raise ValueError(f"등급 값 이상: {d['grade']}")

    # targets 정규화
    d["targets"] = [t for t in d.get("targets", []) if t in TARGETS] or ["공통"]
    d.setdefault("ai_tools", [])
    d.setdefault("tags", [])
    d.setdefault("difficulty", "중급")

    # 슬러그 검증 — kebab-case 강제
    slug = re.sub(r"[^a-z0-9-]", "-", d["skill_name"].lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        slug = "untitled-skill"
    d["skill_name"] = slug

    return d


def analyze(scrape_dict: dict) -> AnalysisResult:
    """ScrapeResult.to_dict() → AnalysisResult."""
    try:
        import google.generativeai as genai
    except ImportError:
        return AnalysisResult(
            skill_name="", skill_title_ko="", category="기타", grade="C",
            grade_reason="", targets=[], summary="", when_to_use="", memo="",
            ai_tools=[], tags=[], difficulty="", body_content="",
            ok=False, error="google-generativeai 미설치",
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return AnalysisResult(
            skill_name="", skill_title_ko="", category="기타", grade="C",
            grade_reason="", targets=[], summary="", when_to_use="", memo="",
            ai_tools=[], tags=[], difficulty="", body_content="",
            ok=False, error="GEMINI_API_KEY 미설정 (.env 확인)",
        )

    genai.configure(api_key=api_key)
    prompt = build_prompt(scrape_dict)

    last_err: Exception | None = None
    raw_text: str = ""

    # 1-2단계: Gemini cloud (cloud 빠름, 한도 있음)
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
            logger.warning("Gemini %s 실패: %s", model_name, e)
            last_err = e

    # 3단계: Gemma 4 26B 로컬 폴백 (Gemini 둘 다 실패 또는 빈 응답)
    if not raw_text:
        logger.info("Gemini 폴백 실패 → Gemma 4 26B 로컬 시도")
        raw_text = call_gemma_json(prompt) or ""

    if not raw_text:
        return AnalysisResult(
            skill_name="", skill_title_ko="", category="기타", grade="C",
            grade_reason="", targets=[], summary="", when_to_use="", memo="",
            ai_tools=[], tags=[], difficulty="", body_content="",
            ok=False, error=f"모든 LLM 호출 실패 (Gemini + Gemma): {last_err}",
        )

    try:
        data = _extract_json(raw_text)
        data = _validate(data)
        return AnalysisResult(
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
            tldr=data.get("tldr", ""),
            how_it_works=data.get("how_it_works", ""),
            steps=data.get("steps", ""),
            examples=data.get("examples", ""),
            doogeun=data.get("doogeun", ""),
            caveats=data.get("caveats", ""),
            body_content=data["body_content"],
            raw=data,
        )
    except Exception as e:  # noqa: BLE001
        return AnalysisResult(
            skill_name="", skill_title_ko="", category="기타", grade="C",
            grade_reason="", targets=[], summary="", when_to_use="", memo="",
            ai_tools=[], tags=[], difficulty="", body_content="",
            ok=False, error=f"JSON 파싱 실패: {e}",
        )
