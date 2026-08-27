"""무차별 대입 가드 — auth_routes._RedeemGuard 와 같은 파라미터 (5회 실패 → 5분 잠금).

다른 모듈의 private 를 끌어다 쓰지 않고 같은 규칙을 복제한다. 대신 키별 추적을 더한다:
한 client_id 가 잠겨도 다른 클라이언트는 영향받지 않는다.

/oauth/authorize 는 무인증 공개 엔드포인트이고 키가 공격자 제어값(client_id 쿼리 파라미터)이라
키가 무제한 증식할 수 있다 — 만료 축출 + 상한(max_keys)으로 launchd 상주 프로세스에서 메모리가
무한히 쌓이는 것을 막는다.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

MAX_KEYS = 2048


class FailGuard:
    def __init__(self, *, max_fails: int = 5, lock_seconds: int = 300,
                 clock: Callable[[], float] = time.time,
                 max_keys: int = MAX_KEYS) -> None:
        self._max = max_fails
        self._lock_sec = lock_seconds
        self._clock = clock
        self._mu = threading.Lock()
        self._fails: dict[str, int] = {}
        self._until: dict[str, float] = {}
        self._max_keys = max_keys

    def _evict_locked(self) -> None:
        """만료 축출 + 상한 유지. `_until` 과 `_fails` 를 **독립적으로** max_keys 이내로 유지한다.

        두 버킷을 하나의 공유 예산으로 두면 어느 한쪽의 플러딩이 다른 쪽의 정상 항목을
        밀어낸다 — (a) `_fails` 플러딩(수많은 저카운트 키)이 예산을 다 써서 이미 확정된
        `_until` 잠금을 밀어내면 활성 잠금이 증발한다(test_active_locks_survive_eviction),
        (b) 반대로 `_until` 플러딩(수많은 만료된/오래된 잠금)이 예산을 다 써서 `_fails` 를
        통째로 비우면 어떤 키도 max_fails 에 도달하지 못해 새 잠금이 영원히 생기지 않는다
        (무인증 엔드포인트에서 도달 가능한 회귀 — R-2). 그래서 각 버킷을 자신의 max_keys
        예산 안에서만 축출한다: `_until` 은 만료가 임박한 것부터, `_fails` 는 카운트가
        낮은 것부터. 호출자가 이미 self._mu 를 잡고 있어야 한다.
        """
        now = self._clock()
        for k in [k for k, t in self._until.items() if t <= now]:
            self._until.pop(k, None)
            self._fails.pop(k, None)
        over_until = len(self._until) - self._max_keys
        if over_until > 0:
            for k, _ in sorted(self._until.items(), key=lambda kv: kv[1])[:over_until]:
                self._until.pop(k, None)
        over_fails = len(self._fails) - self._max_keys
        if over_fails > 0:
            for k, _ in sorted(self._fails.items(), key=lambda kv: kv[1])[:over_fails]:
                self._fails.pop(k, None)

    def check(self, key: str = "global") -> Optional[str]:
        """잠겨 있으면 사용자에게 보여줄 사유, 아니면 None."""
        with self._mu:
            self._evict_locked()
            wait = int(self._until.get(key, 0.0) - self._clock())
            return f"시도 잠김 — {wait}초 후 재시도" if wait > 0 else None

    def fail(self, key: str = "global") -> None:
        with self._mu:
            self._evict_locked()
            c = self._fails.get(key, 0) + 1
            if c >= self._max:
                self._until[key] = self._clock() + self._lock_sec
                self._fails.pop(key, None)
            else:
                self._fails[key] = c

    def ok(self, key: str = "global") -> None:
        with self._mu:
            self._fails.pop(key, None)
            self._until.pop(key, None)
