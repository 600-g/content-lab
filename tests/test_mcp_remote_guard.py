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
