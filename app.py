"""aiskillbox — Flask 웹 UI for 콘텐츠랩 v4.3.

도메인: https://aiskillbox.600g.net (Cloudflare Tunnel 경유)
로컬: http://localhost:5050

v4.3 변경:
- 순차 잡 큐 — 단일 워커 스레드가 큐를 하나씩 처리. 제출은 즉시 반환되어
  링크 입력칸이 바로 비고, 다음 작업을 계속 넣을 수 있다.
- Web Push — 잡 완료 시 서비스워커로 푸시 발송 (앱이 백그라운드여도 알림).
- 설정 API — PIN 보호. API 키를 웹 UI 에서 편집.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import queue
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, make_response, render_template, request

# .env 자동 로드
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    load_dotenv = None  # type: ignore

from scripts import push as push_mod
from scripts import settings_store
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
JOB_QUEUE: "queue.Queue[str]" = queue.Queue()  # 순차 처리 — 단일 워커가 소비
_worker_thread: "threading.Thread | None" = None  # 워커 — 시작 시 할당, healthz 가 생존 확인
RECENT_MAX = 50
JOBS_MAX_PERSIST = 200  # 디스크에 보존할 최대 잡 수

# PIN 무차별 대입 방어 — 메모리 카운터 (_PIN_LOCK 로 스레드 보호)
_PIN_GUARD = {"fails": 0, "locked_until": 0.0}
_PIN_LOCK = threading.Lock()
_PIN_MAX_FAILS = 5
_PIN_LOCK_SECONDS = 300


# ── 잡 영속화 ────────────────────────────────────────────
def _save_jobs() -> None:
    """JOBS dict → 디스크. 반드시 JOBS_LOCK 안에서 호출 (JOBS 순회 — 락 없으면 RuntimeError)."""
    try:
        JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
        items = list(JOBS.values())
        items.sort(key=lambda x: x.get("started_at", 0), reverse=True)
        keep = items[:JOBS_MAX_PERSIST]
        data = {j["id"]: j for j in keep}
        JOBS_FILE.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        log.warning("JOBS 저장 실패: %s", e)


def _load_jobs() -> None:
    """서버 시작 시 JOBS 복원.

    - running 잡: 백그라운드 스레드가 사라졌으므로 interrupted 마킹.
    - queued 잡: 큐에 다시 들어갈 수 있으므로 그대로 둔다 (_requeue_pending 가 재투입).
    """
    if not JOBS_FILE.exists():
        return
    try:
        data = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
        for jid, j in data.items():
            if j.get("status") == "running":
                j["status"] = "interrupted"
                j["stage"] = "서버 재시작으로 중단"
                j["error"] = "서버 재시작으로 중단됨. 다시 시도해주세요."
                if not j.get("done_at"):
                    j["done_at"] = time.time()
            JOBS[jid] = j
        log.info("JOBS 복원: %d건", len(JOBS))
    except Exception as e:  # noqa: BLE001
        log.warning("JOBS 로드 실패: %s", e)


def _requeue_pending() -> None:
    """재시작 전 queued 상태였던 잡을 큐에 다시 투입 (FIFO 보존)."""
    with JOBS_LOCK:
        pending = sorted(
            (j for j in JOBS.values() if j.get("status") == "queued"),
            key=lambda x: x.get("started_at", 0),
        )
    for j in pending:
        JOB_QUEUE.put(j["id"])
    if pending:
        log.info("재시작 — queued 잡 %d건 재투입", len(pending))


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


# ── Web Push 발송 ────────────────────────────────────────
def _push_for_job(job: dict) -> None:
    """잡 완료 → 구독된 기기에 Web Push. 실패해도 잡엔 영향 없음."""
    try:
        r = job.get("result") or {}
        skill = r.get("skill") or {}
        name = skill.get("title") or skill.get("name") or job.get("url", "")
        if job.get("status") == "failed":
            title = "aiskillbox · ❌ 실패"
            body = r.get("error_ko") or job.get("error") or "오류가 발생했어요"
            # 알림 탭 → 채팅 자동 진단 딥링크 (chat.js 가 ?diag= 처리)
            url = f"/?diag={job.get('id', '')}"
        elif r.get("partial_ok"):
            title = "aiskillbox · ⚠️ 부분 성공"
            body = name
            url = r.get("notion_web_url") or "/"
        elif r.get("skipped"):
            title = "aiskillbox · ⏭ 이미 등록됨"
            body = name
            url = r.get("notion_web_url") or "/"
        elif skill.get("merged"):
            title = "aiskillbox · 🔀 합병 완료"
            body = name
            url = r.get("notion_web_url") or "/"
        else:
            title = "aiskillbox · ✅ 스킬화 완료"
            grade = skill.get("grade", "")
            body = f"[{grade}] {name}" if grade else name
            url = r.get("notion_web_url") or "/"
        sent = push_mod.send_push(title, body, url=url, tag="aiskillbox-job")
        if sent:
            log.info("Web Push 발송: %d기기", sent)
    except Exception as e:  # noqa: BLE001
        log.warning("Web Push 발송 실패: %s", e)


# ── 잡 실행 ──────────────────────────────────────────────
def _run_job(job_id: str) -> None:
    """큐 워커가 호출 — 잡 1건 처리. url 은 JOBS 에서 읽는다."""
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return
        url = job["url"]
        job["status"] = "running"
        job["stage"] = "scraping"
        _save_jobs()
    try:
        # v4.5: SKILL.md 가 유일한 원본 — Notion 등록은 config 옵션 (기본 off).
        summary = collect(url, register_notion=_notion_enabled(), skip_duplicate=False)
        with JOBS_LOCK:
            j = JOBS.get(job_id)
            if j is not None:
                j["status"] = "completed" if summary.get("ok") else "failed"
                j["result"] = summary
                j["done_at"] = time.time()
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
                "catalog_url": f"/catalog#{skill.get('name', '')}" if skill.get("name") else "",
            })
    except Exception as e:  # noqa: BLE001
        log.exception("job failed: %s", e)
        with JOBS_LOCK:
            j = JOBS.get(job_id)
            if j is not None:
                j["status"] = "failed"
                j["error"] = str(e)
                j["done_at"] = time.time()
            _save_jobs()
    with JOBS_LOCK:
        finished = dict(JOBS.get(job_id, {}))
    _push_for_job(finished)
    _gc_old_jobs()


def _worker_loop() -> None:
    """단일 워커 — 큐에서 잡을 하나씩 꺼내 순차 처리."""
    log.info("잡 워커 시작 — 순차 처리 모드")
    while True:
        job_id = JOB_QUEUE.get()
        try:
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                status = job.get("status") if job else None
            if status != "queued":
                continue  # 이미 처리됐거나 사라진 잡
            _run_job(job_id)
        except Exception as e:  # noqa: BLE001
            log.exception("워커 루프 오류: %s", e)
        finally:
            JOB_QUEUE.task_done()


def _notion_urls() -> dict:
    """통합 Notion 페이지 URL — 앱 + 웹 둘 다 노출."""
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


def _build_id() -> str:
    """정적 파일 캐시 무효화 — app.js / chat.js / style.css / sw.js mtime 해시."""
    static_dir = Path(__file__).parent / "static"
    h = hashlib.md5()
    for f in ("app.js", "chat.js", "style.css", "sw.js"):
        p = static_dir / f
        if p.exists():
            h.update(str(int(p.stat().st_mtime)).encode())
    return h.hexdigest()[:8]


# ── PIN 검증 ─────────────────────────────────────────────
def _pin_ok(supplied: str) -> tuple[bool, str]:
    """설정 API PIN 검증. (성공여부, 사유) — 잠금/미설정 처리.

    _PIN_LOCK 으로 카운터 갱신을 직렬화 — 동시 요청이 잠금을 우회하지 못하게.
    """
    now = time.time()
    with _PIN_LOCK:
        if now < _PIN_GUARD["locked_until"]:
            wait = int(_PIN_GUARD["locked_until"] - now)
            return False, f"PIN 시도 잠김 — {wait}초 후 재시도"
        real = os.getenv("ADMIN_PIN", "")
        if not real:
            return False, "ADMIN_PIN 미설정 — .env 에 ADMIN_PIN 추가 필요"
        if supplied and hmac.compare_digest(str(supplied), str(real)):
            _PIN_GUARD["fails"] = 0
            return True, ""
        _PIN_GUARD["fails"] += 1
        if _PIN_GUARD["fails"] >= _PIN_MAX_FAILS:
            _PIN_GUARD["locked_until"] = now + _PIN_LOCK_SECONDS
            _PIN_GUARD["fails"] = 0
            return False, f"PIN {_PIN_MAX_FAILS}회 실패 — {_PIN_LOCK_SECONDS // 60}분 잠금"
        left = _PIN_MAX_FAILS - _PIN_GUARD["fails"]
        return False, f"PIN 불일치 — {left}회 남음"


def _request_pin() -> str:
    """헤더 또는 바디에서 PIN 추출."""
    pin = request.headers.get("X-Admin-Pin", "")
    if not pin:
        data = request.get_json(silent=True) or {}
        pin = str(data.get("pin", ""))
    return pin


# ── 라우트 ───────────────────────────────────────────────
def _notion_enabled() -> bool:
    """수집 시 Notion 등록 여부 — config.json notion.register_on_collect (기본 False, v4.5 부터 옵션)."""
    try:
        from scripts import config_store
        return bool(config_store.get("notion.register_on_collect", False))
    except Exception:  # noqa: BLE001
        return False


@app.get("/")
def index():
    resp = make_response(render_template(
        "index.html", notion=_notion_urls(), notion_enabled=_notion_enabled(),
        catalog_url="/catalog", build_id=_build_id()))
    resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    return resp


@app.get("/sw.js")
def service_worker_root():
    """루트 스코프 서비스워커 — /static/sw.js 를 / 스코프로 서빙."""
    sw = Path(__file__).parent / "static" / "sw.js"
    resp = make_response(sw.read_text(encoding="utf-8"))
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp


@app.post("/api/collect")
def api_collect():
    data = request.get_json(silent=True) or request.form.to_dict()
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"ok": False, "error": "url 필수"}), 400
    if not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"ok": False, "error": "유효한 http(s) URL 필요"}), 400

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
    JOB_QUEUE.put(job_id)  # 워커가 순차 처리
    return jsonify({"ok": True, "job_id": job_id, "queue_size": JOB_QUEUE.qsize()})


@app.get("/api/status/<job_id>")
def api_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "job 없음"}), 404
    return jsonify({"ok": True, "job": job})


@app.get("/api/jobs/active")
def api_jobs_active():
    """진행 중 + 최근 1시간 내 완료 잡. queued 잡엔 대기 순번 부여."""
    now = time.time()
    items: list[dict] = []
    with JOBS_LOCK:
        for j in JOBS.values():
            done_at = j.get("done_at")
            if done_at is None or (now - done_at) < 3600:
                items.append({
                    "id": j["id"],
                    "url": j["url"],
                    "status": j["status"],
                    "stage": j.get("stage", ""),
                    "started_at": j.get("started_at", 0),
                    "done_at": done_at,
                    "elapsed": int(now - j.get("started_at", now)),
                    "result": j.get("result"),
                    "error": j.get("error"),
                })
    items.sort(key=lambda x: -x["started_at"])
    # queued 잡 대기 순번 (오래된 것부터 1번)
    queued = sorted((i for i in items if i["status"] == "queued"),
                    key=lambda x: x["started_at"])
    for pos, i in enumerate(queued, start=1):
        i["queue_pos"] = pos
    return jsonify({
        "ok": True,
        "items": items,
        "active_count": sum(1 for i in items if i["status"] in ("queued", "running")),
    })


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
    return jsonify({"ok": True, "total": len(items),
                    "by_grade": by_grade, "by_category": by_category})


# ── Web Push API ─────────────────────────────────────────
@app.get("/api/push/vapid")
def api_push_vapid():
    """클라이언트 구독용 공개 키."""
    return jsonify({
        "ok": True,
        "configured": push_mod.push_configured(),
        "public_key": push_mod.vapid_public_key(),
        "subscriptions": push_mod.subscription_count(),
    })


@app.post("/api/push/subscribe")
def api_push_subscribe():
    sub = request.get_json(silent=True) or {}
    if push_mod.add_subscription(sub):
        return jsonify({"ok": True, "subscriptions": push_mod.subscription_count()})
    return jsonify({"ok": False, "error": "구독 정보가 올바르지 않음"}), 400


@app.post("/api/push/unsubscribe")
def api_push_unsubscribe():
    data = request.get_json(silent=True) or {}
    endpoint = data.get("endpoint", "")
    push_mod.remove_subscription(endpoint)
    return jsonify({"ok": True, "subscriptions": push_mod.subscription_count()})


# ── 설정 API (PIN 보호) ──────────────────────────────────
@app.post("/api/settings/auth")
def api_settings_auth():
    """PIN 검증만 — 통과 시 설정 행 반환."""
    ok, reason = _pin_ok(_request_pin())
    if not ok:
        return jsonify({"ok": False, "error": reason}), 401
    return jsonify({"ok": True, "rows": settings_store.settings_view()})


@app.post("/api/settings")
def api_settings_post():
    ok, reason = _pin_ok(_request_pin())
    if not ok:
        return jsonify({"ok": False, "error": reason}), 401
    data = request.get_json(silent=True) or {}
    updates = data.get("updates") or {}
    if not isinstance(updates, dict):
        return jsonify({"ok": False, "error": "updates 형식 오류"}), 400
    applied = settings_store.update_env(updates)
    if applied and load_dotenv:
        # 변경 즉시 반영 — os.environ 갱신 (API 키는 호출 시점에 읽힘)
        load_dotenv(PROJECT_ROOT / ".env", override=True)
    return jsonify({"ok": True, "applied": applied,
                    "rows": settings_store.settings_view()})


def _last_failure() -> dict | None:
    """가장 최근 실패/중단 잡 요약 — 외부 모니터(112 등)가 healthz 로 감지."""
    with JOBS_LOCK:
        failed = [j for j in JOBS.values() if j.get("status") in ("failed", "interrupted")]
        if not failed:
            return None
        j = max(failed, key=lambda x: x.get("done_at") or 0)
        r = j.get("result") or {}
        return {
            "job_id": j.get("id"),
            "url": j.get("url"),
            "error_ko": r.get("error_ko") or j.get("error") or "",
            "at": j.get("done_at"),
        }


def _library_health() -> dict:
    """라이브러리 인덱스 요약 (실패해도 healthz 는 살아야 함)."""
    try:
        from scripts.library.index import get_index
        from scripts.library.search import load_vectors
        idx = get_index()
        vecs = load_vectors()
        embedded = sum(1 for r in idx.records if r.slug in vecs)
        return {"total": len(idx.records), "embedded": embedded, "version": idx.version}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


@app.get("/healthz")
def healthz():
    return jsonify({
        "ok": True,
        "service": "aiskillbox",
        "version": "4.5",
        "library": _library_health(),
        "notion_enabled": _notion_enabled(),
        "last_failure": _last_failure(),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "notion_configured": bool(os.getenv("NOTION_API_KEY")),
        "push_configured": push_mod.push_configured(),
        "push_subscriptions": push_mod.subscription_count(),
        "recent_count": len(_load_recent()),
        "active_jobs": sum(1 for j in JOBS.values() if j.get("status") == "running"),
        "queued_jobs": sum(1 for j in JOBS.values() if j.get("status") == "queued"),
        "worker_alive": bool(_worker_thread and _worker_thread.is_alive()),
        "notion": _notion_urls(),
    })


# ── 채팅 라우트 등록 (Opus 4.8 자가 운영 패널) ────────────
try:
    from scripts.chat.routes import register_chat_routes
    register_chat_routes(app)
except Exception as _chat_err:  # noqa: BLE001
    log.warning("채팅 라우트 등록 실패 — 채팅 비활성: %s", _chat_err)


# ── 스킬 라이브러리 라우트 (/api/library/* + /catalog) ─────
try:
    from scripts.library.routes import register_library_routes
    register_library_routes(app)
except Exception as _lib_err:  # noqa: BLE001
    log.warning("라이브러리 라우트 등록 실패 — 검색/카탈로그 비활성: %s", _lib_err)


# ── 초대코드 인증 — v4.6 전체 잠금 ─────────────────────────
# 의도적으로 try/except 없음: 게이트 등록이 실패하면 사이트가 무보호로 뜨는 것보다
# 서버 기동 실패(healthz 죽음 → 112 모니터 감지)가 낫다.
from scripts.auth_routes import register_auth  # noqa: E402

register_auth(app, pin_ok=_pin_ok)


# ── 시작 ─────────────────────────────────────────────────
_load_jobs()
_worker_thread = threading.Thread(target=_worker_loop, daemon=True, name="job-worker")
_worker_thread.start()
_requeue_pending()

if __name__ == "__main__":
    log.info("aiskillbox listening on http://0.0.0.0:%d", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=False)
