"""scripts.mcp_remote.guard — 무차별 대입 가드 (시계 주입, 네트워크 0)."""
from __future__ import annotations

import unittest

from scripts.mcp_remote.guard import FailGuard


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, sec):
        self.t += sec


class FailGuardTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.g = FailGuard(max_fails=5, lock_seconds=300, clock=self.clock)

    def test_four_failures_do_not_lock(self):
        for _ in range(4):
            self.g.fail("c1")
        self.assertIsNone(self.g.check("c1"))

    def test_fifth_failure_locks(self):
        for _ in range(5):
            self.g.fail("c1")
        msg = self.g.check("c1")
        self.assertIsNotNone(msg)
        self.assertIn("초", msg)

    def test_lock_expires(self):
        for _ in range(5):
            self.g.fail("c1")
        self.clock.advance(301)
        self.assertIsNone(self.g.check("c1"))

    def test_success_resets_counter(self):
        for _ in range(4):
            self.g.fail("c1")
        self.g.ok("c1")
        self.g.fail("c1")
        self.assertIsNone(self.g.check("c1"))

    def test_keys_are_independent(self):
        for _ in range(5):
            self.g.fail("c1")
        self.assertIsNotNone(self.g.check("c1"))
        self.assertIsNone(self.g.check("c2"))

    def test_expired_locks_are_evicted(self):
        for i in range(3):
            for _ in range(5):
                self.g.fail(f"k{i}")
        self.clock.advance(301)
        self.g.check("k0")
        self.assertEqual(len(self.g._until), 0)
        self.assertEqual(len(self.g._fails), 0)

    def test_key_count_is_bounded(self):
        g = FailGuard(max_fails=5, lock_seconds=300, clock=self.clock, max_keys=10)
        for i in range(50):
            g.fail(f"k{i}")
        # 상한을 넘는 건 eviction 이 따라잡기 전 딱 한 키 추가분뿐이어야 한다.
        self.assertLessEqual(len(g._fails) + len(g._until), 11)

    def test_active_locks_survive_eviction(self):
        g = FailGuard(max_fails=5, lock_seconds=300, clock=self.clock, max_keys=10)
        for _ in range(5):
            g.fail("locked")
        for i in range(50):
            g.fail(f"noise{i}")
        self.assertIsNotNone(g.check("locked"))

    def test_new_key_can_still_lock_when_until_is_at_cap(self):
        """회귀 가드 (R-2) — _until 이 상한을 넘겨도 새 키가 정상적으로 잠겨야 한다.

        _fails 를 통째로 비우면 어떤 키도 max_fails 에 도달하지 못한다.
        """
        g = FailGuard(max_fails=5, lock_seconds=300, clock=self.clock, max_keys=10)
        for i in range(30):                 # _until 을 상한 위로 채운다
            for _ in range(5):
                g.fail(f"noise{i}")
        for _ in range(5):
            g.fail("victim")
        self.assertIsNotNone(g.check("victim"))
