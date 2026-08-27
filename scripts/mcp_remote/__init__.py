"""aiskillbox 원격 MCP 커넥터 (OAuth 2.1 + Streamable HTTP).

app.py 가 register_mcp_remote(app) 한 줄로 등록한다.
설계: docs/superpowers/specs/2026-08-27-remote-mcp-oauth-design.md
"""
from __future__ import annotations

import logging

from flask import Flask

logger = logging.getLogger(__name__)


def register_mcp_remote(app: Flask) -> None:
    from scripts.mcp_remote import config as mcp_config
    from scripts.mcp_remote.oauth_grants import register_oauth_grants
    from scripts.mcp_remote.oauth_meta import register_oauth_meta
    from scripts.mcp_remote.transport import register_transport

    c = mcp_config.load()
    if not mcp_config.enabled(c):
        logger.info("mcp_remote 비활성 (config.json mcp_remote.enabled=false)")
        return
    register_oauth_meta(app)
    register_oauth_grants(app)
    register_transport(app)
    logger.info("원격 MCP 커넥터 등록 — resource=%s dcr=%s",
                mcp_config.resource_id(c), mcp_config.dynamic_registration(c))
