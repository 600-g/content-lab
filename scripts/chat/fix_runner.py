"""fix 잡 러너 — 서버와 분리된 프로세스에서 Claude Code 로 코드 수정.

python -m scripts.chat.fix_runner <fix_id>

흐름:
1. 코드 스냅샷 (app.py / scripts / templates / static → logs/fix_snapshots/<id>/)
2. claude -p (Max 플랜, --model sonnet) 로 수정 실행 — 저장소 밖 수정 금지 가드레일
3. 검증: py_compile 전체 + (있으면) 실패 URL scrape-only 재시도 + 변경 JS node --check
4. 실패 → 스냅샷 대비 변경분만 원복 (신규 파일 삭제 포함)
5. 성공 + 변경 있음 → launchctl kickstart 로 서비스 재기동
6. 결과 Web Push + logs/fix_jobs.json 갱신
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIX_JOBS_FILE = PROJECT_ROOT / "logs" / "fix_jobs.json"
SNAPSHOT_ROOT = PROJECT_ROOT / "logs" / "fix_snapshots"
VENV_PY = PROJECT_ROOT / "venv" / "bin" / "python3"

CODE_PATHS = ("app.py", "scripts", "templates", "static")
IGNORE_DIRS = {"__pycache__"}
IGNORE_SUFFIXES = {".pyc"}

CLAUDE_TIMEOUT = 900       # 15분
SCRAPE_TEST_TIMEOUT = 240  # playwright 콜드 스타트 고려

# 코드 수정 모델 — 최소 Sonnet 5 (.env FIX_CLAUDE_MODEL 로 override)
DEFAULT_FIX_MODEL = "claude-sonnet-5"
# 별도 Claude 계정(예: Pro 플랜) 로그인 디렉토리 — 존재하면 그 계정으로 실행해
# 메인 Max 플랜 쿼터를 보존. 1회 로그인: CLAUDE_CONFIG_DIR=~/.claude-aibox claude → /login
DEFAULT_FIX_CONFIG_DIR = "~/.claude-aibox"

GUARDRAIL_PROMPT = """너는 aiskillbox(콘텐츠랩) 저장소의 자동 수리 에이전트다. 아래 지시에 따라 이 저장소 코드를 최소 수정으로 고쳐라.

규칙 (절대 준수):
- 이 저장소({root}) 밖의 파일은 절대 읽기 외 수정 금지.
- .env / logs/ / venv/ / skills/ / inbox/ 는 수정 금지. 코드(app.py, scripts/, templates/, static/)만 수정.
- git commit / git push / 서비스 재시작 금지 (재시작은 외부에서 자동 처리).
- 대규모 리팩토링 금지 — 문제 해결에 필요한 최소 변경만.
- 수정 후 반드시 `venv/bin/python3 -m py_compile <수정한 .py>` 로 문법 확인.
- 마지막에 무엇을 왜 고쳤는지 3줄 이내로 요약 출력.

[진단 컨텍스트]
{context}

[사용자 지시]
{instruction}
"""


# ── 잡 레코드 갱신 ────────────────────────────────────────
def _update(fix_id: str, **fields) -> dict:
    jobs: dict = {}
    try:
        jobs = json.loads(FIX_JOBS_FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        pass
    job = jobs.get(fix_id) or {"id": fix_id}
    job.update(fields)
    jobs[fix_id] = job
    FIX_JOBS_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    return job


# ── 스냅샷 / diff / 롤백 ─────────────────────────────────
def _iter_code_files() -> list[Path]:
    files: list[Path] = []
    for name in CODE_PATHS:
        p = PROJECT_ROOT / name
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*"):
                if not f.is_file():
                    continue
                if any(part in IGNORE_DIRS for part in f.parts):
                    continue
                if f.suffix in IGNORE_SUFFIXES:
                    continue
                files.append(f)
    return files


def _file_hash(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _prune_snapshots(keep: int = 5) -> None:
    if not SNAPSHOT_ROOT.exists():
        return
    dirs = sorted((d for d in SNAPSHOT_ROOT.iterdir() if d.is_dir()),
                  key=lambda d: d.stat().st_mtime, reverse=True)
    for old in dirs[keep:]:
        shutil.rmtree(old, ignore_errors=True)


def _snapshot(fix_id: str) -> tuple[Path, dict[str, str]]:
    """코드 파일 전체를 스냅샷 디렉토리로 복사. Returns (스냅샷 경로, rel→hash)."""
    _prune_snapshots()
    snap_dir = SNAPSHOT_ROOT / fix_id
    hashes: dict[str, str] = {}
    for f in _iter_code_files():
        rel = f.relative_to(PROJECT_ROOT)
        dst = snap_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        hashes[str(rel)] = _file_hash(f)
    return snap_dir, hashes


def _detect_changes(before: dict[str, str]) -> dict[str, list[str]]:
    after = {str(f.relative_to(PROJECT_ROOT)): _file_hash(f) for f in _iter_code_files()}
    changed = sorted(r for r in before if r in after and before[r] != after[r])
    created = sorted(r for r in after if r not in before)
    deleted = sorted(r for r in before if r not in after)
    return {"changed": changed, "created": created, "deleted": deleted}


def _rollback(snap_dir: Path, changes: dict[str, list[str]]) -> None:
    """fix 가 건드린 파일만 원복 — 전역 reset 금지 (기존 미커밋 변경 보존)."""
    for rel in changes["changed"] + changes["deleted"]:
        src = snap_dir / rel
        dst = PROJECT_ROOT / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for rel in changes["created"]:
        p = PROJECT_ROOT / rel
        try:
            p.unlink(missing_ok=True)
        except OSError:
            pass


# ── 검증 ─────────────────────────────────────────────────
def _verify(changes: dict[str, list[str]], failed_url: str) -> tuple[bool, str]:
    # 1) 파이썬 전체 컴파일
    r = subprocess.run(
        [str(VENV_PY), "-m", "compileall", "-q", "app.py", "scripts"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        return False, f"py_compile 실패:\n{(r.stderr or r.stdout)[-1500:]}"

    # 2) 변경된 JS 문법 확인 (node 있을 때만)
    node = shutil.which("node")
    if node:
        js_touched = [rel for rel in changes["changed"] + changes["created"]
                      if rel.endswith(".js")]
        for rel in js_touched:
            r = subprocess.run(
                [node, "--check", rel],
                cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=30,
            )
            if r.returncode != 0:
                return False, f"JS 문법 오류 ({rel}):\n{r.stderr[-800:]}"

    # 3) 실패했던 URL scrape-only 재시도
    if failed_url:
        test_code = (
            "import sys\n"
            "from scripts.scraper.router import scrape\n"
            f"r = scrape({failed_url!r})\n"
            "ok = bool(r.ok and (len(r.text or '') >= 80 or r.skip_reason))\n"
            "print('scrape_ok' if ok else 'scrape_fail: ' + str(r.error))\n"
            "sys.exit(0 if ok else 1)\n"
        )
        r = subprocess.run(
            [str(VENV_PY), "-c", test_code],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True,
            timeout=SCRAPE_TEST_TIMEOUT,
        )
        if r.returncode != 0:
            return False, f"재스크랩 실패:\n{(r.stdout + r.stderr)[-1200:]}"

    return True, "ok"


# ── 부수 동작 ─────────────────────────────────────────────
def _send_push(title: str, body: str, url: str = "/") -> None:
    try:
        from scripts import push as push_mod
        push_mod.send_push(title, body, url=url, tag="aiskillbox-fix")
    except Exception as e:  # noqa: BLE001
        print(f"[fix_runner] push 실패: {e}")


def _restart_service() -> None:
    try:
        subprocess.run(
            ["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/com.doogeun.aiskillbox"],
            capture_output=True, text=True, timeout=20,
        )
    except Exception as e:  # noqa: BLE001
        print(f"[fix_runner] 재기동 실패: {e}")


def _build_prompt(job: dict) -> str:
    ctx_parts = []
    src = job.get("source_context") or {}
    if src.get("url"):
        ctx_parts.append(f"실패한 수집 잡: url={src['url']}, stage={src.get('stage')}, "
                         f"error={src.get('error')}")
    if job.get("failed_url") and not src.get("url"):
        ctx_parts.append(f"문제의 URL: {job['failed_url']}")
    tail = (job.get("log_tail") or "").strip()
    if tail:
        ctx_parts.append(f"서버 stderr 로그 tail:\n{tail[-4000:]}")
    context = "\n\n".join(ctx_parts) or "(추가 컨텍스트 없음)"
    return GUARDRAIL_PROMPT.format(
        root=PROJECT_ROOT, context=context, instruction=job.get("instruction", ""),
    )


# ── 메인 ─────────────────────────────────────────────────
def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m scripts.chat.fix_runner <fix_id>")
        return 2
    fix_id = sys.argv[1]

    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    # claude / node 탐색 보장 (launchd PATH 편차 대비)
    env = dict(os.environ)
    if "/opt/homebrew/bin" not in env.get("PATH", ""):
        env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")
    os.environ["PATH"] = env["PATH"]

    jobs = json.loads(FIX_JOBS_FILE.read_text(encoding="utf-8"))
    job = jobs.get(fix_id)
    if not job:
        print(f"[fix_runner] 잡 없음: {fix_id}")
        return 2

    _update(fix_id, status="running", started_at=time.time(), pid=os.getpid())
    print(f"[fix_runner] {fix_id} 시작 — {job.get('instruction', '')[:120]}")

    snap_dir, before = _snapshot(fix_id)
    changes: dict[str, list[str]] = {"changed": [], "created": [], "deleted": []}

    try:
        prompt = _build_prompt(job)
        claude_bin = shutil.which("claude") or "/opt/homebrew/bin/claude"
        model = os.getenv("FIX_CLAUDE_MODEL", "").strip() or DEFAULT_FIX_MODEL
        # 별도 계정(Pro 플랜) 로그인 폴더가 있으면 그 계정으로 실행 — 없으면 기본(Max) 로그인.
        cfg_dir = os.path.expanduser(
            os.getenv("FIX_CLAUDE_CONFIG_DIR", "").strip() or DEFAULT_FIX_CONFIG_DIR)
        account = "default(본계정 구독)"
        if os.path.isdir(cfg_dir):
            env["CLAUDE_CONFIG_DIR"] = cfg_dir
            account = f"separate({cfg_dir})"
        _update(fix_id, model=model, claude_account=account)
        print(f"[fix_runner] model={model}, account={account}")
        r = subprocess.run(
            [claude_bin, "--dangerously-skip-permissions", "--model", model,
             "-p", prompt],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True,
            timeout=CLAUDE_TIMEOUT, env=env,
        )
        summary = (r.stdout or "").strip()[-4000:]
        if r.returncode != 0:
            raise RuntimeError(f"claude 종료 코드 {r.returncode}: {(r.stderr or '')[-800:]}")

        changes = _detect_changes(before)
        n_changed = sum(len(v) for v in changes.values())
        _update(fix_id, status="verifying", summary=summary, changed_files=changes)

        if n_changed == 0:
            _update(fix_id, status="no_change", done_at=time.time(),
                    verify="변경 없음 — 코드 수정이 불필요했거나 실패")
            _send_push("aiskillbox · 🔧 자동수정", "코드 변경 없이 종료됐어요. 채팅에서 결과를 확인하세요.")
            return 0

        ok, verify_msg = _verify(changes, job.get("failed_url", ""))
        if not ok:
            _rollback(snap_dir, changes)
            _update(fix_id, status="rolled_back", done_at=time.time(),
                    verify=verify_msg, error="검증 실패 → 자동 원복")
            _send_push("aiskillbox · ❌ 자동수정 실패", "검증 실패로 원복했어요. 채팅에서 로그를 확인하세요.")
            print(f"[fix_runner] {fix_id} 검증 실패 → 원복\n{verify_msg}")
            return 1

        _update(fix_id, status="success", done_at=time.time(), verify=verify_msg)
        _send_push("aiskillbox · ✅ 자동수정 완료",
                   f"파일 {n_changed}건 수정 + 검증 통과. 서비스 재기동 중.")
        print(f"[fix_runner] {fix_id} 성공 — {changes}")
        _restart_service()
        return 0

    except subprocess.TimeoutExpired:
        changes = _detect_changes(before)
        _rollback(snap_dir, changes)
        _update(fix_id, status="failed", done_at=time.time(),
                error=f"타임아웃({CLAUDE_TIMEOUT}s) → 원복")
        _send_push("aiskillbox · ❌ 자동수정 실패", "시간 초과로 중단하고 원복했어요.")
        return 1
    except Exception as e:  # noqa: BLE001
        changes = _detect_changes(before)
        _rollback(snap_dir, changes)
        _update(fix_id, status="failed", done_at=time.time(), error=f"{e} → 원복")
        _send_push("aiskillbox · ❌ 자동수정 실패", str(e)[:180])
        print(f"[fix_runner] {fix_id} 실패: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
