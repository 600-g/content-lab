"""라이브러리 Flask 엔드포인트 — app.py 가 register_library_routes(app) 으로 등록.

읽기 전용 공개 API (사이트 자체가 공개). 모든 응답 JSON envelope {ok, ...}, GET 에 CORS *.

  GET /api/library/search?q=&k=&category=&grade=&mode=hybrid|keyword
  GET /api/library/skills?category=&grade=
  GET /api/library/skills/<slug>[?format=raw]
  GET /api/library/stats
  GET /catalog, /catalog.html        (인덱스 버전 키 캐시 + ETag)
"""
from __future__ import annotations

import hashlib
import logging
import threading
from typing import Callable, Optional

from flask import Flask, Response, jsonify, request

from scripts.library import catalog as lib_catalog
from scripts.library import search as lib_search
from scripts.library.index import get_index, is_valid_slug

logger = logging.getLogger(__name__)

_CATALOG_CACHE: dict = {"version": None, "html": "", "etag": ""}
_CATALOG_LOCK = threading.Lock()
# 게시글 상세 — 인덱스 버전이 바뀌면 통째로 버린다 (슬러그별 렌더 캐시)
_PAGE_CACHE: dict = {"version": None, "pages": {}}
_PAGE_LOCK = threading.Lock()


def _json_error(message: str, status: int) -> tuple[Response, int]:
    return jsonify({"ok": False, "error": message}), status


def register_library_routes(
    app: Flask,
    *,
    mirror_root=None,
    embed_fn: Optional[Callable[[str], Optional[list[float]]]] = None,
    vectors_loader: Optional[Callable[[], dict]] = None,
) -> None:
    """mirror_root / embed_fn / vectors_loader 는 테스트 주입용 — 운영에서는 기본값(None)."""

    def _index():
        return get_index(mirror_root)

    @app.after_request
    def _library_cors(resp: Response) -> Response:
        if request.path.startswith("/api/library/") and request.method in ("GET", "OPTIONS"):
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            # v4.6 전체 잠금 — 브라우저 cross-origin 호출은 X-Auth-Token 헤더로 인증
            resp.headers["Access-Control-Allow-Headers"] = "X-Auth-Token"
        return resp

    @app.get("/api/library/search")
    def library_search():
        q = request.args.get("q", "")
        k = request.args.get("k", lib_search.DEFAULT_K)
        res = lib_search.search(
            q,
            k=k,
            category=request.args.get("category") or None,
            grade=request.args.get("grade") or None,
            mode=request.args.get("mode", "hybrid"),
            index=_index(),
            embed_fn=embed_fn,
            vectors=vectors_loader() if vectors_loader else None,
        )
        return jsonify(res), (200 if res.get("ok") else 400)

    @app.get("/api/library/skills")
    def library_list():
        idx = _index()
        items = idx.filter(
            category=request.args.get("category") or None,
            grade=(request.args.get("grade") or "").upper() or None,
        )
        return jsonify({
            "ok": True,
            "total": len(items),
            "index_version": idx.version,
            "items": [{**r.meta(), "page_url": lib_catalog.post_url(r.slug)} for r in items],
        })

    @app.get("/api/library/skills/<path:slug>")
    def library_get(slug: str):
        if not is_valid_slug(slug):
            return _json_error("잘못된 슬러그", 400)
        rec = _index().get(slug)
        if rec is None:
            return _json_error(f"스킬 없음: {slug}", 404)
        if request.args.get("format") == "raw":
            return Response(rec.raw_md, mimetype="text/markdown")
        return jsonify({
            "ok": True,
            "slug": rec.slug,
            "meta": rec.meta(),
            "body_md": rec.body_md,
            "raw_md": rec.raw_md,
            "path": f"~/.claude/skills/{rec.slug}/SKILL.md",
            "page_url": lib_catalog.post_url(rec.slug),   # 사람이 읽는 게시글
            "catalog_url": f"/catalog#{rec.slug}",         # 구버전 링크 호환
        })

    @app.get("/api/library/stats")
    def library_stats():
        st = _index().stats()
        st["ok"] = True
        return jsonify(st)

    def _catalog_response() -> Response:
        idx = _index()
        with _CATALOG_LOCK:
            if _CATALOG_CACHE["version"] != idx.version:
                html_text = lib_catalog.render_catalog(idx)
                etag = '"' + hashlib.sha1(idx.version.encode("utf-8")).hexdigest()[:20] + '"'
                _CATALOG_CACHE.update({"version": idx.version, "html": html_text, "etag": etag})
                logger.info("카탈로그 재생성: %d건 (%d bytes)", len(idx.records), len(html_text))
            html_text = _CATALOG_CACHE["html"]
            etag = _CATALOG_CACHE["etag"]
        if request.headers.get("If-None-Match") == etag:
            resp = Response(status=304)
        else:
            resp = Response(html_text, mimetype="text/html")
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "no-cache"
        return resp

    @app.get("/catalog")
    def catalog_page():
        return _catalog_response()

    @app.get("/catalog.html")
    def catalog_page_html():
        return _catalog_response()

    @app.get("/skill/<path:slug>")
    def skill_post(slug: str):
        """게시글 상세 — 사이트 안에서 본문을 읽는 페이지 (외부 이탈은 [원본 ↗] 뿐)."""
        if not is_valid_slug(slug):
            return _json_error("잘못된 슬러그", 400)
        idx = _index()
        rec = idx.get(slug)
        if rec is None:
            return _json_error(f"스킬 없음: {slug}", 404)
        with _PAGE_LOCK:
            if _PAGE_CACHE["version"] != idx.version:
                _PAGE_CACHE.update({"version": idx.version, "pages": {}})
            cached = _PAGE_CACHE["pages"].get(slug)
            if cached is None:
                cached = lib_catalog.render_skill_page(rec, idx)
                _PAGE_CACHE["pages"][slug] = cached
        etag = '"' + hashlib.sha1(f"{idx.version}:{slug}".encode("utf-8")).hexdigest()[:20] + '"'
        if request.headers.get("If-None-Match") == etag:
            resp = Response(status=304)
        else:
            resp = Response(cached, mimetype="text/html")
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "no-cache"
        return resp
