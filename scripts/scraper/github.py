"""GitHub 전용 — REST API로 repo 메타 + README 직접 추출.

Playwright보다 10배 빠르고 정확. 미인증 호출 한도 60/h (충분).
"""
from __future__ import annotations

import base64
import logging
import re
from urllib.parse import urlparse

import requests

from .router import ScrapeResult

logger = logging.getLogger(__name__)

GH_API = "https://api.github.com"
TIMEOUT = 20
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "aiskillbox/4.0 (content-lab)",
}


def _parse_url(url: str) -> tuple[str, str, str | None]:
    """https://github.com/owner/repo[/...] → (owner, repo, sub_path)."""
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    if len(parts) < 2:
        raise ValueError(f"GitHub URL 형식 아님: {url}")
    owner, repo = parts[0], parts[1].replace(".git", "")
    sub_path = "/".join(parts[2:]) if len(parts) > 2 else None
    return owner, repo, sub_path


def _fetch_repo(owner: str, repo: str) -> dict:
    r = requests.get(f"{GH_API}/repos/{owner}/{repo}", headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _fetch_readme(owner: str, repo: str) -> str:
    try:
        r = requests.get(
            f"{GH_API}/repos/{owner}/{repo}/readme",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        content_b64 = data.get("content", "")
        if data.get("encoding") == "base64" and content_b64:
            return base64.b64decode(content_b64).decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        logger.warning("readme fetch failed: %s", e)
    return ""


def _fetch_file(owner: str, repo: str, file_path: str, ref: str = "HEAD") -> str:
    """특정 파일 직접 fetch (raw)."""
    try:
        r = requests.get(
            f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{file_path}",
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.text
    except Exception:  # noqa: BLE001
        pass
    return ""


def scrape(url: str) -> ScrapeResult:
    owner, repo, sub_path = _parse_url(url)
    logger.info("github scrape owner=%s repo=%s sub=%s", owner, repo, sub_path)

    try:
        repo_info = _fetch_repo(owner, repo)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return ScrapeResult(
                url=url, source_type="github", title="", text="",
                meta={}, ok=False, error="404 — repo 존재 안 함 또는 private",
            )
        raise

    title = f"{owner}/{repo}"
    description = repo_info.get("description") or ""

    # 본문 텍스트 조립
    text_parts = []
    text_parts.append(f"[GitHub Repo] {title}")
    if description:
        text_parts.append(f"[Description] {description}")

    # 메타
    stars = repo_info.get("stargazers_count", 0)
    forks = repo_info.get("forks_count", 0)
    language = repo_info.get("language") or ""
    topics = repo_info.get("topics") or []
    license_info = (repo_info.get("license") or {}).get("name", "") or ""
    homepage = repo_info.get("homepage") or ""

    text_parts.append(
        f"[Stats] ★{stars} | Fork {forks} | Lang {language} | "
        f"License {license_info} | Topics: {', '.join(topics)}"
    )
    if homepage:
        text_parts.append(f"[Homepage] {homepage}")

    # 특정 파일 지정 (/blob/main/foo.md) → 그 파일만 가져옴
    if sub_path and sub_path.startswith(("blob/", "tree/")):
        m = re.match(r"(?:blob|tree)/([^/]+)/(.+)", sub_path)
        if m:
            ref, file_path = m.group(1), m.group(2)
            content = _fetch_file(owner, repo, file_path, ref)
            if content:
                text_parts.append(f"[File: {file_path}]\n{content[:50000]}")
    else:
        readme = _fetch_readme(owner, repo)
        if readme:
            text_parts.append(f"[README]\n{readme[:50000]}")

    text = "\n\n".join(text_parts)
    meta = {
        "owner": owner,
        "repo": repo,
        "stars": stars,
        "forks": forks,
        "language": language,
        "topics": topics,
        "license": license_info,
        "homepage": homepage,
        "default_branch": repo_info.get("default_branch", "main"),
        "created_at": repo_info.get("created_at", ""),
        "updated_at": repo_info.get("updated_at", ""),
    }

    return ScrapeResult(
        url=url,
        source_type="github",
        title=title,
        text=text,
        meta=meta,
    )
