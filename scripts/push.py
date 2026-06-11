"""Web Push — 백그라운드 작업 완료 알림.

페이지가 떠 있을 때만 동작하던 `new Notification()` 의 한계를 넘어,
앱이 백그라운드/종료 상태여도 서비스워커가 푸시를 받아 알림을 띄운다.

- VAPID 키는 .env (`VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` / `VAPID_SUBJECT`)
- 구독은 `logs/push_subscriptions.json` 에 영속화
- 죽은 구독(404/410)은 발송 시 자동 제거
"""
from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger("aiskillbox.push")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUBS_FILE = PROJECT_ROOT / "logs" / "push_subscriptions.json"

_LOCK = threading.Lock()
_VAPID_CACHE: dict = {}


def vapid_public_key() -> str:
    """클라이언트 구독용 applicationServerKey (base64url)."""
    return os.getenv("VAPID_PUBLIC_KEY", "")


def push_configured() -> bool:
    return bool(os.getenv("VAPID_PUBLIC_KEY") and os.getenv("VAPID_PRIVATE_KEY"))


def _load_vapid():
    """py_vapid Vapid 객체 — .env 의 raw private key 로 1회 로드 후 캐시."""
    priv = os.getenv("VAPID_PRIVATE_KEY", "")
    if not priv:
        return None
    if _VAPID_CACHE.get("key") == priv and _VAPID_CACHE.get("obj"):
        return _VAPID_CACHE["obj"]
    try:
        from py_vapid import Vapid01
        obj = Vapid01.from_raw(priv.encode())
        _VAPID_CACHE["key"], _VAPID_CACHE["obj"] = priv, obj
        return obj
    except Exception as e:  # noqa: BLE001
        logger.warning("VAPID 로드 실패: %s", e)
        return None


# ── 구독 저장소 ──────────────────────────────────────────
def _read_subs() -> list[dict]:
    if not SUBS_FILE.exists():
        return []
    try:
        data = json.loads(SUBS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001
        return []


def _write_subs(subs: list[dict]) -> None:
    SUBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUBS_FILE.write_text(json.dumps(subs, ensure_ascii=False, indent=2), encoding="utf-8")


def subscription_count() -> int:
    with _LOCK:
        return len(_read_subs())


def add_subscription(sub: dict) -> bool:
    """브라우저 PushSubscription JSON 등록. endpoint 기준 중복 제거."""
    endpoint = (sub or {}).get("endpoint")
    if not endpoint or not (sub.get("keys") or {}).get("p256dh"):
        return False
    with _LOCK:
        subs = [s for s in _read_subs() if s.get("endpoint") != endpoint]
        subs.append(sub)
        _write_subs(subs)
    return True


def remove_subscription(endpoint: str) -> bool:
    if not endpoint:
        return False
    with _LOCK:
        subs = _read_subs()
        kept = [s for s in subs if s.get("endpoint") != endpoint]
        if len(kept) == len(subs):
            return False
        _write_subs(kept)
    return True


# ── 발송 ────────────────────────────────────────────────
def send_push(title: str, body: str, url: str = "/", tag: str = "aiskillbox") -> int:
    """모든 구독에 푸시 발송. 죽은 구독은 제거. 발송 성공 수 반환."""
    if not push_configured():
        return 0
    vapid = _load_vapid()
    if vapid is None:
        return 0
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning("pywebpush 미설치 — 푸시 생략")
        return 0

    with _LOCK:
        subs = _read_subs()
    if not subs:
        return 0

    payload = json.dumps({"title": title, "body": body, "url": url, "tag": tag},
                          ensure_ascii=False)
    claims = {"sub": os.getenv("VAPID_SUBJECT", "mailto:admin@600g.net")}
    sent = 0
    dead: list[str] = []
    for sub in subs:
        try:
            webpush(
                subscription_info=sub,
                data=payload,
                vapid_private_key=vapid,
                vapid_claims=dict(claims),
                ttl=600,
            )
            sent += 1
        except WebPushException as e:  # noqa: PERF203
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (404, 410):
                dead.append(sub.get("endpoint", ""))
            else:
                logger.warning("푸시 발송 실패 (%s): %s", status, e)
        except Exception as e:  # noqa: BLE001
            logger.warning("푸시 발송 오류: %s", e)

    if dead:
        with _LOCK:
            subs = [s for s in _read_subs() if s.get("endpoint") not in dead]
            _write_subs(subs)
        logger.info("죽은 구독 %d건 제거", len(dead))
    return sent
