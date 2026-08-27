"""무차별 대입 가드 — auth_routes._RedeemGuard 와 같은 파라미터 (5회 실패 → 5분 잠금).

다른 모듈의 private 를 끌어다 쓰지 않고 같은 규칙을 복제한다. 대신 키별 추적을 더한다:
한 client_id 가 잠겨도 다른 클라이언트는 영향받지 않는다.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional


class FailGuard:
    def __init__(self, *, max_fails: int = 5, lock_seconds: int = 300,
                 clock: Callable[[], float] = time.time) -> None:
        self._max = max_fails
        self._lock_sec = lock_seconds
        self._clock = clock
        self._mu = threading.Lock()
        self._fails: dict[str, int] = {}
        self._until: dict[str, float] = {}

    def check(self, key: str = "global") -> Optional[str]:
        """잠겨 있으면 사용자에게 보여줄 사유, 아니면 None."""
        with self._mu:
            wait = int(self._until.get(key, 0.0) - self._clock())
            return f"시도 잠김 — {wait}초 후 재시도" if wait > 0 else None

    def fail(self, key: str = "global") -> None:
        with self._mu:
            c = self._fails.get(key, 0) + 1
            if c >= self._max:
                self._until[key] = self._clock() + self._lock_sec
                self._fails[key] = 0
            else:
                self._fails[key] = c

    def ok(self, key: str = "global") -> None:
        with self._mu:
            self._fails.pop(key, None)
            self._until.pop(key, None)
