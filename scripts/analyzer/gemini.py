"""LLM 호출 (Gemini → Gemma 4) + JSON 파싱.

폴백 체인 (v2.6.1):
1. Gemini 2.5 Flash (cloud, 무료 20 RPD/model) — quota 80% 도달 시 자동 스킵
2. Gemini 2.5 Flash Lite (cloud, 무료 1000 RPD/model) — 한도 50배 큰 폴백
3. Gemma 4 26B (local Ollama, 무제한, 약 15-30초)

검증 retry 와 body_too_short 보강은 Gemma 로만. cloud quota 보존.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests

from .prompt import (
    build_prompt, CATEGORIES, GRADES, TARGETS, AI_TOOLS, DIFFICULTIES,
    BANNED_HEADINGS, ALLOWED_HEADINGS,
)

logger = logging.getLogger(__name__)

MODEL_PRIMARY = "gemini-2.5-flash"
# 2.0-flash 는 free tier limit:0 으로 사실상 차단됨 → 2.5-flash-lite 로 교체 (1000 RPD)
MODEL_FALLBACK = "gemini-2.5-flash-lite"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma4:26b")
GEMMA_TIMEOUT = int(os.getenv("GEMMA_TIMEOUT", "120"))

# Cloud quota 카운터 — 모델별 일일 free tier 한도 (소진 전 미리 스킵)
QUOTA_FILE = Path(__file__).resolve().parents[2] / "logs" / "gemini_quota.json"
QUOTA_DAILY_LIMITS = {
    "gemini-2.5-flash": int(os.getenv("GEMINI_FLASH_RPD", "20")),
    "gemini-2.5-flash-lite": int(os.getenv("GEMINI_FLASH_LITE_RPD", "1000")),
}
QUOTA_SOFT_THRESHOLD = float(os.getenv("GEMINI_QUOTA_SOFT", "0.80"))


def _quota_today_key() -> str:
    return _dt.date.today().isoformat()


def _quota_load() -> dict:
    try:
        if QUOTA_FILE.exists():
            return json.loads(QUOTA_FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        pass
    return {}


def _quota_save(data: dict) -> None:
    try:
        QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
        QUOTA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        logger.warning("quota 저장 실패: %s", e)


def _quota_increment(model: str, *, hit_429: bool = False) -> None:
    """모델별 일일 카운트 +1. 429 응답이면 그 날 한도 도달로 마킹."""
    data = _quota_load()
    today = _quota_today_key()
    day = data.setdefault(today, {})
    entry = day.setdefault(model, {"count": 0, "exhausted": False})
    entry["count"] = entry.get("count", 0) + 1
    if hit_429:
        entry["exhausted"] = True
    # 7일 이전 기록 정리
    cutoff = (_dt.date.today() - _dt.timedelta(days=7)).isoformat()
    for k in list(data.keys()):
        if k < cutoff:
            data.pop(k, None)
    _quota_save(data)


def _quota_should_skip(model: str) -> bool:
    """이 모델을 오늘 더 호출하면 안 되는지 — 429 도달했거나 80% 임계 초과."""
    data = _quota_load()
    entry = (data.get(_quota_today_key()) or {}).get(model) or {}
    if entry.get("exhausted"):
        return True
    limit = QUOTA_DAILY_LIMITS.get(model, 0)
    if limit <= 0:
        return False
    return entry.get("count", 0) >= max(1, int(limit * QUOTA_SOFT_THRESHOLD))


def call_gemma_json(
    prompt: str,
    *,
    num_predict: int = int(os.getenv("GEMMA_NUM_PREDICT", "8192")),
    temperature: float = 0.3,
) -> Optional[str]:
    """Gemma 4 26B 로컬 호출. JSON 응답 강제.

    think=False: Gemma 4·Qwen3 계열은 사고(thinking) 토큰이 켜진 상태면
    출력 예산을 잠식해 JSON 이 잘리거나 필수 필드가 누락된다 (실 발생:
    skill_title_ko 누락 → 잡 실패). 로컬 LLM 폴백은 사고 없이 바로 JSON.
    num_ctx: Ollama 기본 컨텍스트는 4096 토큰이라 20K자+ 스크랩이 잘려
    스키마 지시가 유실된다. 16384 로 올려 전체 프롬프트가 모델에 들어가게.
    num_predict/temperature: body_too_short 보강 재요청 시 더 긴 출력 허용.
    """
    body = {
        "model": os.getenv("GEMMA_MODEL", GEMMA_MODEL),
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
            "num_ctx": int(os.getenv("GEMMA_NUM_CTX", "16384")),
            "num_predict": num_predict,
        },
    }
    timeout = int(os.getenv("GEMMA_TIMEOUT", str(GEMMA_TIMEOUT)))
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=body, timeout=timeout)
        # think 파라미터 미지원 Ollama 버전 → think 빼고 1회 재시도
        if r.status_code == 400 and "think" in r.text.lower():
            body.pop("think", None)
            r = requests.post(f"{OLLAMA_URL}/api/generate", json=body, timeout=timeout)
        r.raise_for_status()
        return r.json().get("response", "")
    except Exception as e:  # noqa: BLE001
        logger.warning("Gemma 4 호출 실패: %s", e)
        return None


@dataclass
class AnalysisResult:
    """v2.4: body_md 가 본문 단일 소스. legacy 필드는 호환용(기존 22건/합병 로직)."""
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
    # v2.4 — 자유 본문 (LLM 이 출처 결대로 작성)
    tldr: str = ""
    body_md: str = ""
    # v2.6 — 페이지 맨 위 callout (💡 blue_bg) 별도 필드
    callout: str = ""
    # legacy 섹션 — 기존 22건 변환/합병 호환용. 신규 v2.4 출력은 body_md 만 사용.
    how_it_works: str = ""
    steps: str = ""
    examples: str = ""
    doogeun: str = ""
    caveats: str = ""
    body_content: str = ""  # deprecated
    raw: dict = field(default_factory=dict)
    ok: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "skill_title_ko": self.skill_title_ko,
            "tldr": self.tldr,
            "body_md": self.body_md,
            "category": self.category,
            "grade": self.grade,
            "grade_reason": self.grade_reason,
            "difficulty": self.difficulty,
            "ai_tools": self.ai_tools,
            # legacy
            "targets": self.targets,
            "summary": self.summary,
            "when_to_use": self.when_to_use,
            "memo": self.memo,
            "tags": self.tags,
            "body_content": self.body_content,
            "ok": self.ok,
            "error": self.error,
        }


def _unescape_literal_newlines(s: str) -> str:
    """LLM 이 개행을 역슬래시+n 두 글자로 뱉은 경우를 실제 개행으로 되돌린다.

    JSON 파서는 진짜 이스케이프(\\n)만 풀어주므로, 모델이 한 번 더 이스케이프해서
    (\\\\n) 넣으면 본문이 통째로 한 줄이 된다. 그러면 마크다운 구조가 전부 무너지고
    Notion 등록 시 heading 하나에 rich_text 119개가 몰려 페이지 등록 전체가 실패한다
    (실사고 2026-08-10 webswing-desktop-pet — 로컬엔 설치됐는데 Notion 에만 누락).

    진짜 개행이 이미 충분하면 손대지 않는다 — 코드블록 안의 정상 '\\n' 문자열 보호.
    """
    if not s or "\\n" not in s:
        return s
    real = s.count("\n")
    literal = s.count("\\n")
    if literal < 3 or real >= literal:
        return s
    logger.warning("body_md 에 리터럴 개행 %d개 감지 → 실제 개행으로 복원", literal)
    return s.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")


def _compose_body(d: dict) -> str:
    """v2.3 minimal fallback — LLM 이 body_md 비워서 반환했을 때만 호출된다.

    옛 _compose_body 는 v2.1 8섹션 + "## 🏢 두근 환경 적용" 헤딩을 박아넣어서
    v2.3 prompt 와 충돌하고 banned_heading 검증도 우회했다 (코드가 박은 거라).
    지금은 그냥 callout + when_to_use 만 있는 stub 을 만들어서, body_too_short
    검증에 무조건 걸리고 Gemma 보강 재요청으로 풍부한 본문을 받게 한다.
    """
    parts: list[str] = []
    if d.get("callout") or d.get("tldr"):
        parts.append(d.get("callout") or d.get("tldr"))
    if d.get("when_to_use"):
        parts.append(f"## 이게 뭔가요?\n\n{d['when_to_use']}")
    return "\n\n".join(parts).strip()


_REPAIR_STRING_FIELDS = (
    "skill_name", "skill_title_ko", "callout", "category", "grade",
    "grade_reason", "summary", "when_to_use", "memo", "tldr",
    "how_it_works", "steps", "examples", "doogeun", "caveats", "body_md",
)
_REPAIR_ARRAY_FIELDS = ("ai_tools", "tags", "targets", "sources")


def _repair_partial_json(raw: str) -> dict:
    """Gemma/Gemini 가 partial JSON 을 뱉었을 때 필드 단위로 복구.

    응답이 잘려서 최상위 json.loads 는 실패하지만 앞부분에 완성된 필드는 남아있는
    케이스가 잦다 (Gemma 4 partial output). 개별 필드 정규식으로 회수해서 필수
    5필드 (skill_name/skill_title_ko/callout/category/grade) 가 채워지면 부분
    성공으로 진행. 이후 _validate 의 소프트 디폴트가 나머지 커버.
    """
    result: dict = {}
    for f in _REPAIR_STRING_FIELDS:
        # 값 안에 escaped quote 허용, 다중 라인 지원
        m = re.search(
            rf'"{f}"\s*:\s*"((?:[^"\\]|\\.)*)"',
            raw, re.DOTALL,
        )
        if m:
            try:
                # JSON escape (\n, \" 등) 해제
                result[f] = json.loads('"' + m.group(1) + '"')
            except Exception:  # noqa: BLE001
                result[f] = m.group(1)
    for f in _REPAIR_ARRAY_FIELDS:
        m = re.search(rf'"{f}"\s*:\s*\[([^\]]*)\]', raw, re.DOTALL)
        if m:
            try:
                result[f] = json.loads("[" + m.group(1) + "]")
            except Exception:  # noqa: BLE001
                # 콤마 스플릿 폴백
                items = [
                    x.strip().strip('"').strip("'")
                    for x in m.group(1).split(",")
                    if x.strip()
                ]
                result[f] = items
    # 최소 요건: skill_name 또는 skill_title_ko 하나는 있어야
    if not (result.get("skill_name") or result.get("skill_title_ko")):
        raise ValueError("복구 불가 — 이름 필드 회수 실패")
    return result


def _extract_json(text: str) -> dict:
    """Gemini 응답에서 JSON 블록 추출. 코드펜스 제거 + partial 자동 복구."""
    s = text.strip()
    # 코드펜스 제거
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    # 첫 { 부터 마지막 } 까지
    start = s.find("{")
    end = s.rfind("}")
    if start < 0:
        # 정상 JSON 블록 시작조차 없음 → 원문 그대로 복구 시도
        try:
            return _repair_partial_json(s)
        except Exception:  # noqa: BLE001
            raise ValueError(f"JSON 블록 없음: {s[:200]}")
    # 온전한 종결 없어도 일단 시도
    payload = s[start : end + 1] if end > start else s[start:]
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        # partial → 필드 단위 복구
        return _repair_partial_json(payload)


def _validate(d: dict) -> dict:
    """필수 필드/enum 검증 + 정규화. TEMPLATE.md v1 기준.

    로컬 LLM(Gemma) 폴백이 필드 일부를 빠뜨려도 잡 전체가 실패하지 않도록
    graceful degrade — 이름 두 필드는 상호 보완하고, 나머지는 소프트 디폴트.
    이름이 둘 다 없을 때만 하드 실패.
    """
    # 8섹션 필드 — v2.2: 빈 값 그대로 두어서 md_generator 가 자동 생략
    section_fields = ["tldr", "how_it_works", "steps", "examples", "doogeun", "caveats", "when_to_use"]

    # 소프트 디폴트 — 누락/빈 값이면 채움 (잡 실패 대신 보존)
    _soft = {
        "category": "기타", "grade": "C", "grade_reason": "",
        "summary": "", "when_to_use": "", "memo": "",
    }
    for k, dv in _soft.items():
        if not d.get(k):
            d[k] = dv
    if not d.get("targets"):
        d["targets"] = []

    # 이름 두 필드 상호 보완 — 슬러그/한글명 중 하나라도 있으면 OK
    name = (d.get("skill_name") or "").strip()
    title = (d.get("skill_title_ko") or "").strip()
    if not name and not title:
        raise ValueError("필수 필드 누락: skill_name / skill_title_ko 둘 다 없음")
    if not title:
        title = name.replace("-", " ").replace("_", " ").strip().title()
    if not name:
        name = title
    d["skill_name"], d["skill_title_ko"] = name, title
    # Gemini가 가끔 list로 반환 — 문자열로 정규화
    for k in section_fields:
        v = d.get(k)
        if v is None:
            d[k] = ""
        elif isinstance(v, list):
            parts = []
            for x in v:
                s = str(x).strip()
                if not s: continue
                if not s.startswith(("- ", "* ", "1.", "2.", "3.")):
                    s = f"- {s}"
                parts.append(s)
            d[k] = "\n".join(parts)
        elif not isinstance(v, str):
            d[k] = str(v)
    # v2.4: body_md 가 본문 단일 소스 — LLM 이 자유 형식으로 작성
    if not d.get("body_md"):
        d["body_md"] = ""
    d["body_md"] = _unescape_literal_newlines(d["body_md"])
    # body_content (legacy) 동기화 — merger/legacy 소비처 호환
    if not d.get("body_content"):
        d["body_content"] = d["body_md"] or _compose_body(d)

    if d["category"] not in CATEGORIES:
        logger.warning("unknown category %s → 기타", d["category"])
        d["category"] = "기타"
    if d["grade"] not in GRADES:
        # 이름/카테고리와 일관되게 graceful degrade — enum 밖 값(B+, 중 등)이면 C
        logger.warning("등급 값 이상 %s → C", d["grade"])
        d["grade"] = "C"

    # targets 정규화
    d["targets"] = [t for t in d.get("targets", []) if t in TARGETS] or ["공통"]
    d.setdefault("tags", [])

    # ai_tools enum 강제 — LLM 이 "LLM (Claude Max, Gemini 등)" 같은 자유형 만들 때 정규화
    raw_tools = d.get("ai_tools") or []
    if not isinstance(raw_tools, list):
        raw_tools = []
    norm_tools: list[str] = []
    for t in raw_tools:
        s = str(t).strip().lower()
        # 한 입력 토큰에 여러 canonical 이름이 포함될 수 있음 (예: "LLM (Claude Max, Gemini 등)") — 다 추출
        for canon in AI_TOOLS:
            if canon.lower() in s and canon not in norm_tools:
                norm_tools.append(canon)
    d["ai_tools"] = norm_tools[:5]

    # difficulty enum 강제 — "초보OK" 같은 자유형 매핑
    df = (d.get("difficulty") or "").strip()
    if df not in DIFFICULTIES:
        if any(k in df for k in ("초보", "초급", "쉬움", "쉽", "Easy", "easy")):
            df = "초급"
        elif any(k in df for k in ("고급", "전문", "어려", "Hard", "hard", "Advanced")):
            df = "고급"
        else:
            df = "중급"
    d["difficulty"] = df

    # 슬러그 검증 — kebab-case 강제
    slug = re.sub(r"[^a-z0-9-]", "-", d["skill_name"].lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        slug = "untitled-skill"
    d["skill_name"] = slug

    return d


def validate_output(data: dict, scraped_text: str = "") -> list[dict]:
    """v2.6 검증 3종 — 검증 실패 사유 리스트 반환 (빈 리스트면 통과).

    각 issue: {"kind": ..., "severity": "retry"|"warn", "hint": ...}
    - retry: callout 누락 / 금지 대제목 사용 → LLM 재호출 권장
    - warn: 본문 너무 짧음 / 코드블록 절반 이상 소실 → partial_ok 마킹
    """
    issues: list[dict] = []
    body = (data.get("body_md") or "") + " " + (data.get("body_content") or "")
    callout = (data.get("callout") or "").strip()

    # 체크 1: callout 존재
    if not callout:
        issues.append({"kind": "callout_missing", "severity": "retry",
                       "hint": "callout 필드를 1~2문장으로 채워라"})

    # 체크 2: 금지 대제목
    for h in BANNED_HEADINGS:
        if f"## {h}" in body or f"##  {h}" in body:
            issues.append({"kind": "banned_heading", "severity": "retry",
                           "hint": f"금지 대제목 사용: '{h}' — 허용 7종으로 교체"})
            break

    # 체크 3: 본문 최소 길이 — 1000자 미만이면 핵심 섹션이 누락된 케이스가 많음
    # len=0(빈 body_md)도 포함 — merger 가 body_content 만 채울 때도 보강 트리거되어야 함
    body_md = (data.get("body_md") or "").strip()
    body_any = body_md or (data.get("body_content") or "").strip()
    if len(body_any) < 1000:
        issues.append({"kind": "body_too_short", "severity": "warn",
                       "hint": f"본문 {len(body_any)}자 — 섹션 누락 의심, Gemma 보강 필요"})

    # 체크 4: 코드블록 절반 이상 소실
    if scraped_text:
        orig = scraped_text.count("```") // 2
        out = body_md.count("```") // 2
        if orig >= 2 and out < max(1, orig // 2):
            issues.append({"kind": "code_blocks_lost", "severity": "warn",
                           "hint": f"코드블록 {orig}개 → {out}개로 소실"})
    return issues


def _retry_prompt(original_prompt: str, raw: str, issues: list[dict]) -> str:
    """검증 실패 사유 → LLM 재요청 프롬프트."""
    fixes = "\n".join(f"- {i['hint']}" for i in issues if i["severity"] == "retry")
    return (
        original_prompt
        + "\n\n[직전 응답 검증 실패 — 아래 사유를 모두 고쳐 JSON 만 다시 작성]\n"
        + fixes
        + "\n\n[직전 응답]\n" + raw[:4000]
    )


def _is_429(err: Exception) -> bool:
    s = f"{err}".lower()
    return "429" in s or "quota" in s or "resource_exhausted" in s


# SDK 0.8 이 thinking 계열 모델에 자동으로 thinking_config 를 주입하는 경우가 있는데
# gemini-2.5-flash-lite 같은 thinking 미지원 모델은 그걸 reject 함.
# 한 번 거부당한 모델은 프로세스 동안 다시 호출하지 않도록 메모리 캐시.
_UNSUPPORTED_MODELS: set[str] = set()


def _is_thinking_config_reject(err: Exception) -> bool:
    s = f"{err}".lower()
    return "thinking_config" in s or "thinking config" in s


def _gemini_gen_config() -> dict:
    """Gemini generation_config — JSON mime + 충분한 출력 토큰.

    실 발생 버그 (2026-06-03): max_output_tokens 미지정 시 default 가 작아 응답이
    중간에 잘려 _extract_json 파싱 실패 → AI 분석 실패. 16384 로 명시.
    thinking 비활성화는 legacy google-generativeai SDK 가 thinking_config 키를
    reject 해서 제거됨 — 대신 gemini-2.5-flash-lite (thinking 미사용) 가 폴백 모델.
    quota 풀린 gemini-2.5-flash 가 사고 토큰을 잠식하더라도 16k 출력이면 본문 충분.
    """
    return {
        "response_mime_type": "application/json",
        "max_output_tokens": int(os.getenv("GEMINI_MAX_OUTPUT", "16384")),
    }


def analyze(scrape_dict: dict) -> AnalysisResult:
    """ScrapeResult.to_dict() → AnalysisResult.

    v2.6.1:
    - Cloud quota 게이트 — 80% 도달한 모델은 호출 자체를 스킵 (logs/gemini_quota.json)
    - 검증 retry 는 무조건 Gemma — URL 당 Cloud 호출 최대 2회로 절반 절감
    - body_too_short 발생 시 Gemma 에 num_predict 8192·temperature 0.4 로 1회 보강 재요청
    """
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

    # 1-2단계: Gemini cloud — quota 80% 도달 모델은 호출 자체를 스킵
    for model_name in (MODEL_PRIMARY, MODEL_FALLBACK):
        if _quota_should_skip(model_name):
            logger.info("Gemini %s quota 임계(>=%.0f%%) — 호출 스킵",
                        model_name, QUOTA_SOFT_THRESHOLD * 100)
            continue
        if model_name in _UNSUPPORTED_MODELS:
            logger.info("Gemini %s — 이번 세션에서 SDK 비호환으로 비활성화 상태", model_name)
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
            logger.warning("Gemini %s 실패: %s", model_name, e)
            last_err = e
            if _is_429(e):
                _quota_increment(model_name, hit_429=True)
            elif _is_thinking_config_reject(e):
                _UNSUPPORTED_MODELS.add(model_name)
                logger.warning(
                    "%s thinking_config 미지원 — 세션 내 비활성 (다음 호출부터 스킵)",
                    model_name,
                )

    # 3단계: Gemma 4 로컬 폴백 (Gemini 둘 다 실패 또는 빈 응답 또는 quota 도달)
    if not raw_text:
        logger.info("Gemini 사용 불가 → Gemma 4 로컬 시도")
        raw_text = call_gemma_json(prompt) or ""

    if not raw_text:
        return AnalysisResult(
            skill_name="", skill_title_ko="", category="기타", grade="C",
            grade_reason="", targets=[], summary="", when_to_use="", memo="",
            ai_tools=[], tags=[], difficulty="", body_content="",
            ok=False, error=f"모든 LLM 호출 실패 (Gemini + Gemma): {last_err}",
        )

    # JSON 파싱 실패 시 Gemma 폴백 1회 — Gemini 응답이 max_output 한도로 잘렸을 때 회복
    try:
        data = _extract_json(raw_text)
    except Exception as parse_err:  # noqa: BLE001
        logger.warning("Gemini 응답 JSON 파싱 실패 (길이=%d) → Gemma 폴백 1회: %s",
                       len(raw_text), parse_err)
        gemma_text = call_gemma_json(prompt) or ""
        if not gemma_text:
            return AnalysisResult(
                skill_name="", skill_title_ko="", category="기타", grade="C",
                grade_reason="", targets=[], summary="", when_to_use="", memo="",
                ai_tools=[], tags=[], difficulty="", body_content="",
                ok=False, error=f"JSON 파싱 실패 + Gemma 폴백 실패: {parse_err}",
            )
        raw_text = gemma_text
        data = _extract_json(raw_text)

    try:
        data = _validate(data)

        # v2.6 검증 3종 + 1회 retry (Cloud quota 보존 위해 Gemma 만 사용)
        scraped_text = scrape_dict.get("text") or ""
        issues = validate_output(data, scraped_text)
        retry_needed = [i for i in issues if i["severity"] == "retry"]
        if retry_needed:
            logger.info("검증 실패 %d건 → Gemma 재요청: %s",
                        len(retry_needed), [i["kind"] for i in retry_needed])
            retry_prompt = _retry_prompt(prompt, raw_text, issues)
            retry_text = call_gemma_json(retry_prompt) or ""
            if retry_text:
                try:
                    data2 = _validate(_extract_json(retry_text))
                    issues2 = validate_output(data2, scraped_text)
                    retry_left2 = [i for i in issues2 if i["severity"] == "retry"]
                    if len(retry_left2) < len(retry_needed):
                        data = data2
                        issues = issues2
                        logger.info("재요청 개선 채택")
                except Exception as e:  # noqa: BLE001
                    logger.warning("재요청 응답 파싱 실패 — 원본 유지: %s", e)

        # v2.6.1 — body_too_short 발생 시 Gemma 에 보강 재요청 1회
        warns = [i for i in issues if i["severity"] == "warn"]
        if any(w["kind"] == "body_too_short" for w in warns):
            cur_body = (data.get("body_md") or "").strip()
            logger.info("body_too_short(%d자) → Gemma 보강 재요청", len(cur_body))
            boost_prompt = (
                prompt
                + "\n\n[직전 응답 본문이 너무 짧음 — 원본 결을 살려 더 풍부하게 작성. "
                "최소 1200자 이상. 코드/명령어/링크 보존. JSON 만 출력]\n"
                + "\n[직전 본문]\n" + cur_body[:3000]
            )
            boost_text = call_gemma_json(
                boost_prompt, num_predict=8192, temperature=0.4
            ) or ""
            if boost_text:
                try:
                    data3 = _validate(_extract_json(boost_text))
                    new_body = (data3.get("body_md") or "").strip()
                    if len(new_body) > max(len(cur_body) + 200, 800):
                        # 더 풍부해진 경우만 채택. 메타 필드는 원본 유지(이름/카테고리 안정)
                        data["body_md"] = new_body
                        data["body_content"] = new_body or data.get("body_content", "")
                        issues = [w for w in issues if w["kind"] != "body_too_short"]
                        warns = [w for w in warns if w["kind"] != "body_too_short"]
                        logger.info("보강 채택: %d자 → %d자", len(cur_body), len(new_body))
                except Exception as e:  # noqa: BLE001
                    logger.warning("보강 응답 파싱 실패 — 원본 유지: %s", e)

        # 경고는 raw 에 박아 collect 가 partial_ok 처리 가능하게
        if warns:
            data["_validation_warnings"] = warns
            logger.warning("검증 경고: %s", [w["kind"] for w in warns])

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
            tldr=data.get("tldr", "") or data.get("callout", ""),
            body_md=data.get("body_md", ""),
            callout=data.get("callout", "") or data.get("tldr", ""),
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
