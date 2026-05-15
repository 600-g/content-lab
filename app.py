"""aiskillbox — Flask 웹 UI for 콘텐츠랩 v4.0.

도메인: https://aiskillbox.600g.net (Cloudflare Tunnel 경유)
로컬: http://localhost:5050
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from collections import deque
from pathlib import Path

from flask import Flask, jsonify, make_response, render_template, request

# .env 자동 로드
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from scripts.collect import collect

PROJECT_ROOT = Path(__file__).resolve().parent
RECENT_FILE = PROJECT_ROOT / "logs" / "recent.json"
JOBS_FILE = PROJECT_ROOT / "logs" / "jobs.json"
PORT = int(os.getenv("AISKILLBOX_PORT", "5050"))

app = Flask(__name__)
log = logging.getLogger("aiskillbox")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()
RECENT_MAX = 50
JOBS_MAX_PERSIST = 200  # 디스크에 보존할 최대 잡 수


def _save_jobs() -> None:
    """JOBS dict → 디스크. JOBS_LOCK 안에서 호출 권장."""
    try:
        JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
        # 최신 200건만 보존 (started_at 기준)
        items = list(JOBS.values())
        items.sort(key=lambda x: x.get("started_at", 0), reverse=True)
        keep = items[:JOBS_MAX_PERSIST]
        data = {j["id"]: j for j in keep}
        JOBS_FILE.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        log.warning("JOBS 저장 실패: %s", e)


def _load_jobs() -> None:
    """서버 시작 시 JOBS 복원. 진행 중이던 잡은 interrupted로 마킹."""
    if not JOBS_FILE.exists():
        return
    try:
        data = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
        for jid, j in data.items():
            if j.get("status") in ("queued", "running"):
                j["status"] = "interrupted"
                j["stage"] = "서버 재시작으로 중단"
                j["error"] = "서버 재시작으로 중단됨. 다시 시도해주세요."
                if not j.get("done_at"):
                    j["done_at"] = time.time()
            JOBS[jid] = j
        log.info("JOBS 복원: %d건 (interrupted=%d)",
                 len(JOBS),
                 sum(1 for j in JOBS.values() if j.get("status") == "interrupted"))
    except Exception as e:  # noqa: BLE001
        log.warning("JOBS 로드 실패: %s", e)


def _load_recent() -> list[dict]:
    if not RECENT_FILE.exists():
        return []
    try:
        return json.loads(RECENT_FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []


def _save_recent(item: dict) -> None:
    RECENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    items = _load_recent()
    items.insert(0, item)
    items = items[:RECENT_MAX]
    RECENT_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _gc_old_jobs() -> None:
    """1시간 넘은 완료 잡 제거."""
    now = time.time()
    with JOBS_LOCK:
        stale = [
            jid for jid, j in JOBS.items()
            if j.get("done_at") and now - j["done_at"] > 3600
        ]
        for jid in stale:
            JOBS.pop(jid, None)


def _run_job(job_id: str, url: str, no_notion: bool, skip_duplicate: bool) -> None:
    with JOBS_LOCK:
        JOBS[job_id]["status"] = "running"
        JOBS[job_id]["stage"] = "scraping"
        _save_jobs()
    try:
        summary = collect(url, register_notion=not no_notion, skip_duplicate=skip_duplicate)
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "completed" if summary.get("ok") else "failed"
            JOBS[job_id]["result"] = summary
            JOBS[job_id]["done_at"] = time.time()
            _save_jobs()
        if summary.get("ok") and not summary.get("skipped"):
            skill = summary.get("skill", {})
            web = summary.get("notion_web_url", "")
            app_url = web.replace("https://", "notion://") if web else ""
            _save_recent({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "url": url,
                "skill_name": skill.get("name", ""),
                "skill_title": skill.get("title", ""),
                "grade": skill.get("grade", ""),
                "category": skill.get("category", ""),
                "merged": skill.get("merged", False),
                "source_count": skill.get("source_count", 1),
                "notion_page": summary.get("stages", {}).get("notion", ""),
                "notion_app_url": app_url,
                "notion_web_url": web,
            })
    except Exception as e:  # noqa: BLE001
        log.exception("job failed: %s", e)
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = str(e)
            JOBS[job_id]["done_at"] = time.time()
            _save_jobs()
    _gc_old_jobs()


def _notion_urls() -> dict:
    """통합 Notion 페이지 URL — 앱 + 웹 둘 다 노출.

    클라이언트에서 UA 보고 분기:
    - 모바일(iOS/Android) → notion:// 스킴으로 앱 즉시 호출 + 0.8s 후 https 폴백
    - 데스크톱 → https로 안전하게 (OS의 기본 핸들러가 알아서 앱 라우팅)
    """
    db_id = os.getenv("NOTION_DB_ID", "").replace("-", "")
    hub_id = os.getenv("NOTION_HUB_PAGE_ID", "").replace("-", "")
    out = {"db_app": "", "db_web": "", "hub_app": "", "hub_web": ""}
    if db_id:
        out["db_app"] = f"notion://www.notion.so/{db_id}"
        out["db_web"] = f"https://www.notion.so/{db_id}"
    if hub_id:
        out["hub_app"] = f"notion://www.notion.so/{hub_id}"
        out["hub_web"] = f"https://www.notion.so/{hub_id}"
    return out


@app.get("/")
def index():
    # 정적 파일 캐시 무효화: 매 응답에 build_id 주입
    import hashlib
    static_dir = Path(__file__).parent / "static"
    h = hashlib.md5()
    for f in ("app.js", "style.css"):
        p = static_dir / f
        if p.exists():
            h.update(str(int(p.stat().st_mtime)).encode())
    build_id = h.hexdigest()[:8]
    resp = make_response(render_template("index.html", notion=_notion_urls(), build_id=build_id))
    resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    return resp


@app.post("/api/collect")
def api_collect():
    data = request.get_json(silent=True) or request.form.to_dict()
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"ok": False, "error": "url 필수"}), 400
    if not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"ok": False, "error": "유효한 http(s) URL 필요"}), 400

    # 정책: 중복 시 항상 합병, Notion은 항상 등록. 옵션 없음.
    no_notion = False
    skip_duplicate = False

    job_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[job_id] = {
            "id": job_id,
            "url": url,
            "status": "queued",
            "stage": "queued",
            "started_at": time.time(),
        }
        _save_jobs()
    threading.Thread(
        target=_run_job,
        args=(job_id, url, no_notion, skip_duplicate),
        daemon=True,
    ).start()
    return jsonify({"ok": True, "job_id": job_id})


@app.get("/api/status/<job_id>")
def api_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "job 없음"}), 404
    return jsonify({"ok": True, "job": job})


@app.get("/api/jobs/active")
def api_jobs_active():
    """현재 진행 중 + 최근 1시간 내 완료된 잡 리스트. 새로고침/멀티기기 추적용."""
    now = time.time()
    items: list[dict] = []
    with JOBS_LOCK:
        for j in JOBS.values():
            done_at = j.get("done_at")
            # 진행 중이거나, 완료된 지 1시간 이내 (GC 전)
            if done_at is None or (now - done_at) < 3600:
                items.append({
                    "id": j["id"],
                    "url": j["url"],
                    "status": j["status"],
                    "stage": j.get("stage", ""),
                    "started_at": j.get("started_at", 0),
                    "done_at": done_at,
                    "elapsed": int(now - j.get("started_at", now)),
                })
    items.sort(key=lambda x: -x["started_at"])
    return jsonify({"ok": True, "items": items, "active_count": sum(1 for i in items if i["status"] in ("queued", "running"))})


@app.get("/api/recent")
def api_recent():
    return jsonify({"ok": True, "items": _load_recent()})


@app.get("/api/stats")
def api_stats():
    items = _load_recent()
    by_grade: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for it in items:
        by_grade[it.get("grade", "?")] = by_grade.get(it.get("grade", "?"), 0) + 1
        by_category[it.get("category", "?")] = by_category.get(it.get("category", "?"), 0) + 1
    return jsonify({
        "ok": True,
        "total": len(items),
        "by_grade": by_grade,
        "by_category": by_category,
    })


@app.get("/healthz")
def healthz():
    notion_ok = bool(os.getenv("NOTION_API_KEY"))
    gemini_ok = bool(os.getenv("GEMINI_API_KEY"))
    return jsonify({
        "ok": True,
        "service": "aiskillbox",
        "version": "4.0",
        "gemini_configured": gemini_ok,
        "notion_configured": notion_ok,
        "recent_count": len(_load_recent()),
        "active_jobs": sum(1 for j in JOBS.values() if j.get("status") == "running"),
        "notion": _notion_urls(),
    })


_load_jobs()  # 시작 시 JOBS 복원

if __name__ == "__main__":
    log.info("aiskillbox listening on http://0.0.0.0:%d", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=False)
