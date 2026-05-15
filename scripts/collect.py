"""콘텐츠랩 v4.0 메인 진입점.

URL → 스크랩 → Gemini 분석 → (중복 합병) → SKILL.md → 글로벌+mirror 설치 → Notion 등록

모든 단계 실패는 **한글 사유 + 우회 안내** 형태로 결과 JSON에 포함.
한 단계가 실패해도 다른 단계는 계속 시도 (부분 성공 허용).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")
except ImportError:
    pass

from scripts.scraper import scrape, detect_source
from scripts.analyzer import analyze
from scripts.analyzer.merger import merge_with_existing
from scripts.skill_builder import render_skill_md, install_skill, mirror_skill
from scripts.skill_builder.installer import find_existing_by_url, find_global_by_slug, find_mirror_by_slug
from scripts.notion_client import register_skill, check_duplicate, curate_after_register


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _humanize_scrape_error(scrape_res) -> tuple[str, str]:
    """스크랩 실패 사유를 한글로 변환 + 우회 가이드."""
    err = scrape_res.error or ""
    src = scrape_res.source_type
    if "yt-dlp" in err:
        if "Sign in" in err or "login" in err.lower():
            return ("로그인 필요한 콘텐츠 — 비공개 또는 연령 제한.",
                    "공개 영상으로 다시 시도하거나 캡션/설명을 직접 텍스트로 입력")
        return ("yt-dlp 실패 — 일부 SNS는 봇 차단 강화 중.",
                "Cloudflare MCP(firecrawl)로 우회 시도 또는 다른 URL 사용")
    if "playwright" in err.lower() or "chromium" in err.lower():
        return ("브라우저 엔진 미설치 또는 실행 실패.",
                "터미널에서 `cd ~/Developer/my-company/content-lab && ./venv/bin/playwright install chromium`")
    if "empty body" in err or "빈" in err:
        return (f"{src.upper()} 페이지에서 본문을 추출하지 못했습니다.",
                "로그인 벽 또는 JS heavy 페이지일 가능성. 다른 URL 또는 모바일 버전 시도")
    if "404" in err or "private" in err.lower():
        return ("페이지가 없거나 비공개입니다.", "URL 재확인 또는 공개 페이지로 변경")
    if "timeout" in err.lower() or "TimeoutExpired" in err:
        return ("페이지 로딩 시간 초과 (45초).", "느린 사이트 또는 네트워크 이슈. 1-2분 후 재시도")
    return (f"스크랩 실패 ({src}) — {err[:200]}",
            "URL 확인 후 재시도. 지속 시 다른 출처 또는 텍스트 직접 입력")


def _humanize_analyze_error(analysis) -> tuple[str, str]:
    err = (analysis.error or "").lower()
    if "gemini_api_key" in err or "미설정" in err:
        return ("Gemini API 키가 .env에 없습니다.",
                "https://aistudio.google.com/apikey 에서 발급 → .env GEMINI_API_KEY")
    if "quota" in err or "429" in err or "limit" in err:
        return ("Gemini 무료 한도 (일 1500회) 초과.", "자정 (PST) 리셋. 또는 다른 API 키")
    if "404" in err or "not found" in err:
        return ("Gemini 모델을 찾을 수 없습니다.", "google-generativeai 업그레이드 (pip install -U)")
    if "permission" in err or "403" in err:
        return ("Gemini API 키 권한 없음.", "API 키 재발급 또는 결제 정보 확인")
    return (f"AI 분석 실패 — {analysis.error[:200] if analysis.error else 'unknown'}",
            "1분 후 재시도. 지속 시 .env 확인")


def collect(url: str, *, register_notion: bool = True, skip_duplicate: bool = False) -> dict:
    """전체 파이프라인. 실패 시 한글 사유 + 부분 성공 반환."""
    log = logging.getLogger("collect")
    summary: dict = {
        "url": url,
        "stages": {},
        "ok": False,
        "partial_ok": False,  # 일부 단계만 성공
    }

    # ── 1. 스크랩 ──────────────────────────────────────────────────
    source_type = detect_source(url)
    log.info("[1/5] 스크랩 시작 type=%s", source_type)
    summary["stages"]["scrape"] = {"stage": "스크래핑", "ok": None}
    try:
        scrape_res = scrape(url)
    except Exception as e:  # noqa: BLE001
        log.exception("스크랩 예외")
        summary["stages"]["scrape"] = {
            "stage": "스크래핑", "ok": False,
            "error_ko": f"스크래핑 단계에서 예기치 못한 오류: {e}",
            "hint": "logs/launchd_stderr.log 확인",
        }
        summary["error_ko"] = summary["stages"]["scrape"]["error_ko"]
        summary["hint"] = summary["stages"]["scrape"]["hint"]
        return summary

    summary["stages"]["scrape"] = {
        "stage": "스크래핑",
        "ok": scrape_res.ok and bool(scrape_res.text.strip()),
        "source_type": scrape_res.source_type,
        "title": scrape_res.title,
        "text_length": len(scrape_res.text or ""),
    }
    if not summary["stages"]["scrape"]["ok"]:
        msg_ko, hint = _humanize_scrape_error(scrape_res)
        summary["stages"]["scrape"]["error_ko"] = msg_ko
        summary["stages"]["scrape"]["hint"] = hint
        summary["error_ko"] = msg_ko
        summary["hint"] = hint
        return summary

    # ── 2. 분석 ────────────────────────────────────────────────────
    log.info("[2/5] Gemini 분석 시작")
    summary["stages"]["analyze"] = {"stage": "AI 분석", "ok": None}
    analysis = analyze(scrape_res.to_dict())
    summary["stages"]["analyze"]["ok"] = analysis.ok
    summary["stages"]["analyze"]["skill_name"] = analysis.skill_name
    summary["stages"]["analyze"]["grade"] = analysis.grade
    summary["stages"]["analyze"]["category"] = analysis.category

    if not analysis.ok:
        msg_ko, hint = _humanize_analyze_error(analysis)
        summary["stages"]["analyze"]["error_ko"] = msg_ko
        summary["stages"]["analyze"]["hint"] = hint
        summary["error_ko"] = msg_ko
        summary["hint"] = hint
        return summary

    if analysis.grade == "C":
        summary["stages"]["analyze"]["note"] = f"등급 C — 활용 불가 ({analysis.grade_reason})"
        summary["ok"] = True  # 분석 자체는 성공
        summary["message_ko"] = "스킬로 등록할 가치 없는 콘텐츠로 판정 (등급 C). DB에 안 올라감."
        return summary

    # ── 3. 중복 감지 → 합병 ────────────────────────────────────────
    existing = find_global_by_slug(analysis.skill_name) or find_mirror_by_slug(analysis.skill_name)
    if not existing:
        existing = find_existing_by_url(url)
    if existing:
        if skip_duplicate:
            summary["stages"]["merge"] = {
                "stage": "중복 처리", "ok": True,
                "action": "스킵 (사용자 옵션)",
                "existing": str(existing),
            }
            summary["ok"] = True
            summary["skipped"] = True
            summary["message_ko"] = "이미 등록된 스킬 — 스킵 옵션으로 합병 안 함"
            return summary
        try:
            analysis = merge_with_existing(existing, analysis, url, scrape_res.source_type)
            summary["stages"]["merge"] = {
                "stage": "중복 합병", "ok": True,
                "existing": str(existing),
                "source_count": len(analysis.raw.get("_merged_source_urls", [])),
            }
        except Exception as e:  # noqa: BLE001
            log.warning("합병 실패, 신규로 진행: %s", e)
            summary["stages"]["merge"] = {
                "stage": "중복 합병", "ok": False,
                "error_ko": f"합병 실패 — 신규 스킬로 저장: {e}",
                "hint": "기존 SKILL.md 형식이 손상되었을 수 있음",
            }
    else:
        summary["stages"]["merge"] = {"stage": "중복 처리", "ok": True, "action": "신규"}

    # ── 4. SKILL.md 생성 + 설치 ───────────────────────────────────
    try:
        skill_md = render_skill_md(analysis, url, scrape_res.source_type)
        global_path, was_new = install_skill(analysis, skill_md)
        mirror_path = mirror_skill(analysis, skill_md)
        summary["stages"]["install"] = {
            "stage": "스킬 파일 저장", "ok": True,
            "global": str(global_path),
            "mirror": str(mirror_path),
            "new": was_new,
        }
    except Exception as e:  # noqa: BLE001
        log.exception("SKILL.md 저장 실패")
        summary["stages"]["install"] = {
            "stage": "스킬 파일 저장", "ok": False,
            "error_ko": f"파일 저장 실패: {e}",
            "hint": "디스크 권한 또는 경로 문제. ~/.claude/skills/ 확인",
        }
        summary["error_ko"] = summary["stages"]["install"]["error_ko"]
        summary["hint"] = summary["stages"]["install"]["hint"]
        return summary

    # ── 5. Notion 등록 (실패해도 부분 성공으로 진행) ─────────────────
    if register_notion:
        existing_page = check_duplicate(url)
        notion_res = register_skill(
            analysis, url, scrape_res.source_type, skill_md,
            existing_page_id=existing_page,
        )
        if notion_res.get("ok"):
            summary["stages"]["notion"] = {
                "stage": "Notion 등록", "ok": True,
                "page_id": notion_res["page_id"],
                "action": notion_res.get("action", ""),
            }
            page_id = notion_res["page_id"]
            clean = page_id.replace("-", "")
            summary["notion_web_url"] = f"https://www.notion.so/{clean}"

            # 자동 큐레이션: 관련 스킬 relation 연결
            try:
                curated = curate_after_register(page_id, analysis)
                if curated.get("related_linked"):
                    summary["stages"]["curate"] = {
                        "stage": "관련 스킬 연결", "ok": True,
                        "linked": curated["related_linked"],
                    }
            except Exception as e:  # noqa: BLE001
                log.warning("자동 큐레이션 실패: %s", e)
        else:
            summary["stages"]["notion"] = {
                "stage": "Notion 등록", "ok": False,
                "error_ko": notion_res.get("error_ko", "알 수 없는 오류"),
                "code": notion_res.get("code", ""),
                "hint": notion_res.get("hint", ""),
            }
    else:
        summary["stages"]["notion"] = {"stage": "Notion 등록", "ok": True, "action": "건너뜀 (옵션)"}

    # ── 최종 판정 ───────────────────────────────────────────────────
    notion_ok = summary["stages"]["notion"]["ok"]
    if notion_ok:
        summary["ok"] = True
        summary["message_ko"] = (
            f"✅ 완료 — {analysis.skill_name} ({analysis.grade}/{analysis.category})"
            + (" 🔀 합병됨" if analysis.raw.get("_is_merged") else "")
        )
    else:
        # 부분 성공 — SKILL.md는 저장됐지만 Notion만 실패
        summary["ok"] = True  # 사용자가 결과 확인하려면 ok:True 줘야 UI가 정상 표시
        summary["partial_ok"] = True
        summary["message_ko"] = (
            f"⚠️ 부분 성공 — 로컬 스킬은 저장됨 ({analysis.skill_name}). "
            f"Notion만 실패: {summary['stages']['notion'].get('error_ko','')}"
        )
        summary["error_ko"] = summary["stages"]["notion"].get("error_ko", "")
        summary["hint"] = summary["stages"]["notion"].get("hint", "")

    summary["skill"] = {
        "name": analysis.skill_name,
        "title": analysis.skill_title_ko,
        "grade": analysis.grade,
        "category": analysis.category,
        "merged": bool(analysis.raw.get("_is_merged")),
        "source_count": len(analysis.raw.get("_merged_source_urls") or [url]),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="콘텐츠랩 v4.0 — URL → 스킬 자산화 (자동 합병)")
    parser.add_argument("url")
    parser.add_argument("--no-notion", action="store_true")
    parser.add_argument("--skip-duplicate", action="store_true")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    args = parser.parse_args()

    setup_logging(args.log_level)
    result = collect(args.url, register_notion=not args.no_notion, skip_duplicate=args.skip_duplicate)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
