"""claude.ai 에서 '자동 종료 타이머' 앱을 고쳐 배포하는 백엔드.

GitHub 의 소스를 읽고 → 한 군데를 문자열 치환하고 → build 번호를 올려 커밋한다.
커밋되는 순간 저장소의 Actions 가 빌드·릴리스하고 600g.net 카드까지 따라온다.
그래서 이 모듈이 하는 일은 '커밋' 까지이고, 그 뒤는 기존 파이프라인이 맡는다.

설계상 중요한 점:

- **대상 저장소·경로는 하드코딩이다.** 호출자(=claude.ai)가 바꿀 수 없다. 원격 MCP 에
  쓰기 권한이 생기는 것이므로, 건드릴 수 있는 범위를 이 파일 하나로 못박는다.
- **인증은 맥에 이미 로그인된 gh CLI 를 쓴다.** 토큰을 이 서비스 .env 로 복제하지 않는다.
  gh 가 로그아웃돼 있으면 그냥 실패하고, 그게 안전한 기본값이다.
- **전체 파일을 주고받지 않는다.** 3,900줄을 claude.ai 가 그대로 뱉게 하면 비현실적이라
  old_str/new_str 치환 방식만 노출한다.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
from typing import Optional

REPO = "600-g/shutdown-timer"
SRC_PATH = "src/PhoneShell.cs"
BRANCH = "main"
SITE_URL = "https://600g.net"

VERSION_RE = re.compile(r'VERSION = "v(\d+)\.(\d+) \(build (\d+)\)"')
GH_CANDIDATES = ("/opt/homebrew/bin/gh", "/usr/local/bin/gh", "/usr/bin/gh")
TIMEOUT = 30
MAX_NEW_STR = 200_000


class PublishError(Exception):
    """사용자에게 그대로 보여줄 실패 사유."""


def _gh_bin() -> str:
    found = shutil.which("gh") or next((p for p in GH_CANDIDATES if os.path.isfile(p)), None)
    if not found:
        raise PublishError("gh CLI 를 찾을 수 없습니다 (맥에 설치·로그인 필요).")
    return found


def _gh(args: list[str], stdin: Optional[str] = None) -> str:
    """gh 실행. 인자는 전부 리스트로 넘겨 셸 해석을 거치지 않는다."""
    try:
        p = subprocess.run(
            [_gh_bin()] + args,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        raise PublishError("GitHub 응답이 없습니다 (시간 초과).")
    if p.returncode != 0:
        msg = (p.stderr or p.stdout or "").strip()[:400]
        if "gh auth login" in msg or "authentication" in msg.lower():
            raise PublishError("GitHub 인증이 끊겼습니다. 맥 터미널에서 `gh auth login` 후 다시 시도하세요.")
        raise PublishError(f"GitHub 호출 실패: {msg}")
    return p.stdout


def read_source() -> tuple[str, str]:
    """(소스 전문, blob sha). sha 는 커밋할 때 '그 사이 안 바뀌었음' 확인에 쓴다."""
    out = _gh(["api", f"repos/{REPO}/contents/{SRC_PATH}", "-H", "Accept: application/vnd.github+json"])
    d = json.loads(out)
    return base64.b64decode(d["content"]).decode("utf-8"), d["sha"]


def current_build(text: str) -> int:
    m = VERSION_RE.search(text)
    if not m:
        raise PublishError("소스에서 VERSION 줄을 찾지 못했습니다.")
    return int(m.group(3))


def _tag_exists(tag: str) -> bool:
    try:
        _gh(["api", f"repos/{REPO}/git/ref/tags/{tag}"])
        return True
    except PublishError:
        return False


def next_build(text: str) -> int:
    """소스 번호 +1. 이미 그 태그가 릴리스돼 있으면 빈 번호가 나올 때까지 올린다."""
    n = current_build(text) + 1
    for _ in range(50):
        if not _tag_exists(f"v1.0.{n}"):
            return n
        n += 1
    raise PublishError("빈 build 번호를 찾지 못했습니다.")


def bump_version(text: str, build: int) -> str:
    new = VERSION_RE.sub(lambda m: f'VERSION = "v{m.group(1)}.{m.group(2)} (build {build})"', text, count=1)
    if new == text:
        raise PublishError("VERSION 줄을 갱신하지 못했습니다.")
    return new


def search(pattern: str, context: int = 2, limit: int = 40) -> str:
    """소스에서 정규식에 걸리는 줄을 번호와 함께. 전체 파일을 안 읽고 고칠 자리만 찾기 위한 도구."""
    try:
        rx = re.compile(pattern)
    except re.error as e:
        raise PublishError(f"정규식이 잘못됐습니다: {e}")
    text, _ = read_source()
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if rx.search(ln)]
    if not hits:
        return f"'{pattern}' 에 걸리는 줄이 없습니다. (총 {len(lines)}줄)"
    out = [f"{REPO}/{SRC_PATH} — {len(hits)}곳 (총 {len(lines)}줄)"]
    shown = 0
    for i in hits:
        if shown >= limit:
            out.append(f"... 이하 {len(hits) - shown}곳 생략")
            break
        lo, hi = max(0, i - context), min(len(lines), i + context + 1)
        out.append("")
        for k in range(lo, hi):
            out.append(f"{'→' if k == i else ' '} {k + 1:5}  {lines[k]}")
        shown += 1
    return "\n".join(out)


def publish(old_str: str, new_str: str, note: str = "") -> str:
    """소스 한 군데를 바꾸고 build 번호를 올려 커밋한다. 커밋 성공 시 안내문을 돌려준다."""
    if not old_str:
        raise PublishError("old_str 이 비었습니다.")
    if old_str == new_str:
        raise PublishError("old_str 과 new_str 이 같습니다 — 바뀌는 게 없습니다.")
    if len(new_str) > MAX_NEW_STR:
        raise PublishError("new_str 이 너무 깁니다.")

    text, sha = read_source()
    n = text.count(old_str)
    if n == 0:
        raise PublishError("old_str 을 소스에서 찾지 못했습니다. search_timer_source 로 정확한 원문을 확인하세요.")
    if n > 1:
        raise PublishError(f"old_str 이 {n}곳에 있습니다. 앞뒤 줄을 더 붙여 한 곳만 가리키게 하세요.")

    patched = text.replace(old_str, new_str, 1)
    if VERSION_RE.search(patched) is None:
        raise PublishError("고친 결과에 VERSION 줄이 없습니다 — 버전 줄을 지우면 배포가 깨집니다.")

    build = next_build(patched)
    patched = bump_version(patched, build)
    tag = f"v1.0.{build}"

    subject = f"{tag}: {note.strip()}" if note.strip() else tag
    payload = {
        "message": subject[:200],
        "content": base64.b64encode(patched.encode("utf-8")).decode("ascii"),
        "sha": sha,
        "branch": BRANCH,
    }
    _gh(
        ["api", "-X", "PUT", f"repos/{REPO}/contents/{SRC_PATH}",
         "-H", "Accept: application/vnd.github+json", "--input", "-"],
        stdin=json.dumps(payload),
    )
    return (
        f"✅ 커밋했습니다 — {tag}\n\n"
        f"  바뀐 곳 : {SRC_PATH} 1곳\n"
        f"  새 버전 : build {build}\n"
        + (f"  메모     : {note.strip()}\n" if note.strip() else "")
        + "\n이제 GitHub Actions 가 빌드합니다 (1~2분).\n"
        f"끝나면 {SITE_URL} 의 '종료타이머&알림' 카드가 {tag} 로 바뀌고,\n"
        "이미 앱을 쓰는 사람에게는 앱 안에서 업데이트 알림이 뜹니다.\n"
        f"진행 상황: https://github.com/{REPO}/actions"
    )


def status() -> str:
    """최신 릴리스와 사이트 카드 상태를 한눈에."""
    lines = []
    try:
        rel = json.loads(_gh(["api", f"repos/{REPO}/releases/latest"]))
        lines.append(f"최신 릴리스 : {rel.get('tag_name')}  ({(rel.get('published_at') or '')[:16]})")
    except PublishError as e:
        lines.append(f"최신 릴리스 : 확인 실패 ({e})")
    try:
        text, _ = read_source()
        lines.append(f"소스 build  : {current_build(text)}")
    except PublishError as e:
        lines.append(f"소스 build  : 확인 실패 ({e})")
    try:
        runs = json.loads(_gh(["api", f"repos/{REPO}/actions/runs?per_page=1"]))
        r = (runs.get("workflow_runs") or [{}])[0]
        lines.append(f"최근 빌드   : {r.get('status')} / {r.get('conclusion')}  ({(r.get('created_at') or '')[:16]})")
    except PublishError:
        pass
    return "\n".join(lines)
