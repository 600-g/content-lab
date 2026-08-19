"""Claude Code 에스컬레이션 — 자연어 수정 요청을 백그라운드 fix 잡으로 실행.

- 채팅의 escalate_fix 도구가 start_fix() 호출 → 잡 스펙을 logs/fix_jobs.json 에
  기록하고 scripts.chat.fix_runner 를 detached subprocess 로 spawn.
- 러너는 서버와 별도 프로세스 그룹 (start_new_session=True) — fix 성공 시
  서버를 재기동해도 러너 자신은 살아남는다.
- 동시 실행 1개 (fix_jobs.json 의 활성 잡 + pid 생존 확인).
- 이 모듈은 잡 생성/조회만. 실제 실행·검증·롤백은 fix_runner.py.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import threading
import time
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIX_JOBS_FILE = PROJECT_ROOT / "logs" / "fix_jobs.json"
FIX_RUNNER_LOG = PROJECT_ROOT / "logs" / "fix_runner.log"
VENV_PY = PROJECT_ROOT / "venv" / "bin" / "python3"
JOBS_KEEP = 20
ACTIVE_STATUSES = ("queued", "running", "verifying")

_LOCK = threading.Lock()


def _read_jobs() -> dict[str, dict]:
    if not FIX_JOBS_FILE.exists():
        return {}
    try:
        data = json.loads(FIX_JOBS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _write_jobs(jobs: dict[str, dict]) -> None:
    FIX_JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    items = sorted(jobs.values(), key=lambda j: j.get("created_at", 0), reverse=True)
    kept = {j["id"]: j for j in items[:JOBS_KEEP]}
    FIX_JOBS_FILE.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")


def _pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def get_running() -> dict | None:
    """활성 fix 잡 (러너 프로세스가 실제 살아있는 것만)."""
    for j in _read_jobs().values():
        if j.get("status") in ACTIVE_STATUSES and _pid_alive(j.get("pid")):
            return j
    return None


def _source_job_context(source_job_id: str | None) -> dict:
    """실패한 수집 잡의 에러 정보를 fix 컨텍스트로 추출."""
    if not source_job_id:
        return {}
    jobs_file = PROJECT_ROOT / "logs" / "jobs.json"
    try:
        data = json.loads(jobs_file.read_text(encoding="utf-8"))
        j = data.get(source_job_id) or {}
        r = j.get("result") or {}
        return {
            "url": j.get("url", ""),
            "status": j.get("status", ""),
            "error": r.get("error_ko") or j.get("error") or "",
            "stage": j.get("stage", ""),
        }
    except Exception:  # noqa: BLE001
        return {}


def _stderr_tail(lines: int = 60) -> str:
    log_file = PROJECT_ROOT / "logs" / "launchd_stderr.log"
    if not log_file.exists():
        return ""
    try:
        r = subprocess.run(
            ["tail", "-n", str(lines), str(log_file)],
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout[-6000:]
    except Exception:  # noqa: BLE001
        return ""


def start_fix(instruction: str, *, failed_url: str | None = None,
              source_job_id: str | None = None) -> dict:
    """fix 잡 생성 + 러너 spawn. Returns 잡 요약 dict (ok=False 면 사유)."""
    instruction = (instruction or "").strip()
    if len(instruction) < 5:
        return {"ok": False, "error": "instruction 이 너무 짧습니다 (5자 이상)"}
    if len(instruction) > 4000:
        return {"ok": False, "error": "instruction 이 너무 깁니다 (4000자 이하)"}

    with _LOCK:
        running = get_running()
        if running:
            return {
                "ok": False,
                "error": f"이미 수정 작업이 실행 중입니다 (id={running['id']}, "
                         f"status={running['status']}). fix_status 로 확인하세요.",
                "running_id": running["id"],
            }

        fix_id = uuid.uuid4().hex[:12]
        src = _source_job_context(source_job_id)
        record = {
            "id": fix_id,
            "instruction": instruction,
            "failed_url": failed_url or src.get("url") or "",
            "source_job_id": source_job_id or "",
            "source_context": src,
            "log_tail": _stderr_tail(),
            "status": "queued",
            "created_at": time.time(),
            "pid": None,
        }
        jobs = _read_jobs()
        jobs[fix_id] = record
        _write_jobs(jobs)

        try:
            FIX_RUNNER_LOG.parent.mkdir(parents=True, exist_ok=True)
            with FIX_RUNNER_LOG.open("a", encoding="utf-8") as out:
                proc = subprocess.Popen(
                    [str(VENV_PY), "-m", "scripts.chat.fix_runner", fix_id],
                    cwd=str(PROJECT_ROOT),
                    stdout=out, stderr=out,
                    start_new_session=True,  # 서버 재기동에도 러너 생존
                )
        except Exception as e:  # noqa: BLE001
            record["status"] = "failed"
            record["error"] = f"러너 spawn 실패: {e}"
            jobs[fix_id] = record
            _write_jobs(jobs)
            return {"ok": False, "error": record["error"]}

        record["pid"] = proc.pid
        jobs[fix_id] = record
        _write_jobs(jobs)

    return {
        "ok": True,
        "fix_id": fix_id,
        "pid": proc.pid,
        "hint": "백그라운드에서 Claude Code 가 수정 중입니다 (최대 15분). "
                "완료/실패 시 Web Push 알림이 가고, fix_status 로도 확인할 수 있어요. "
                "성공 시 서비스가 자동 재기동됩니다.",
    }


def fix_status(limit: int = 5) -> dict:
    """최근 fix 잡 상태. 러너가 죽었는데 활성 상태로 남은 잡은 stale 마킹."""
    jobs = sorted(_read_jobs().values(), key=lambda j: j.get("created_at", 0), reverse=True)
    out = []
    for j in jobs[:max(1, int(limit))]:
        stale = j.get("status") in ACTIVE_STATUSES and not _pid_alive(j.get("pid"))
        out.append({
            "id": j.get("id"),
            "status": ("stale(러너 사망)" if stale else j.get("status")),
            "instruction": (j.get("instruction") or "")[:200],
            "failed_url": j.get("failed_url", ""),
            "created_at": j.get("created_at"),
            "done_at": j.get("done_at"),
            "model": j.get("model"),
            "claude_account": j.get("claude_account"),
            "changed_files": j.get("changed_files"),
            "verify": j.get("verify"),
            "error": j.get("error"),
            "summary": (j.get("summary") or "")[:500],
        })
    return {"ok": True, "jobs": out}
