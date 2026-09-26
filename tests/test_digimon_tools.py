"""scripts/library/digimon_tools.py — 디지몬 진화 도감 MCP 도구 (가짜 백엔드, 네트워크 0)."""
from __future__ import annotations

import unittest

from scripts.library import digimon_tools as dt
from scripts.library import mcp_server

ENC = {"ok": True, "site_agree": {"match": 8, "mismatch": 2}, "ranks": {"성장기": ["파피몬", "아구몬"]},
       "species": {
           "아구몬": {"name": "아구몬", "stage": "성장기", "attr": "백신", "stats": {"hp": 90, "atk": 20, "spd": 30}, "dims": ["아구몬 EX"], "from": [], "to": [],
                   "rank": {"stage": "성장기", "total": 140, "grade": "A", "pos": 2, "n": 2}},
           "파피몬": {"name": "파피몬", "stage": "성장기", "attr": "데이터", "stats": {"hp": 100, "atk": 15, "spd": 40}, "dims": ["파피몬 EX"], "dims_est": [],
                   "rank": {"stage": "성장기", "total": 155, "grade": "S", "pos": 1, "n": 2},
                   "from": [{"name": "뿔몬", "cond": {"evotime_h": 1}, "kind": "measured"}],
                   "to": [{"name": "가루몬", "cond": {"vital": 1200, "pp": 5, "battle": 48, "evotime_h": 24}, "kind": "measured"}],
                   "site_to": [{"name": "가루몬", "cond": {"vital": "1200"}}, {"name": "고릴라몬", "cond": {"vital": "1000", "pp": "5"}}]},
           "가루몬": {"name": "가루몬", "stage": "성숙기", "attr": "백신", "stats": None, "dims": ["파피몬 EX"], "from": [], "to": []},
           "오메가몬 X": {"name": "오메가몬 X", "stage": "초궁극체", "attr": "백신", "stats": None, "dims": [], "dims_est": ["아구몬 EX"], "from": [], "to": []},
           "파피몬 EX 알": {"name": "파피몬 EX 알", "stage": "알", "stats": None, "dims": ["파피몬 EX"], "from": [], "to": []}},
       "dims": {"파피몬 EX": {"name": "파피몬 EX", "region": "서버 해안", "total": 20,
                            "layout": {"check": {"named": 3, "tiles": 4, "bad": 0},
                                       "tiles": [{"col": 0, "name": "파피몬 EX 알", "basis": "pixel"}, {"col": 1, "name": "파피몬", "basis": "pixel"},
                                                 {"col": 2, "name": "가루몬", "basis": "shape"}, {"col": 2, "name": None}],
                                       "lines": [[0, 1], [1, 2], [1, 3]], "site_lines": []}}}}
ROUTE = {"ok": True, "name": "가루몬", "count": 1, "routes": [{"names": ["파피몬 EX 알", "파피몬", "가루몬"], "text": "파피몬 EX 알 → 파피몬 → 가루몬 (바이탈 1200+)"}]}


def fake(path: str) -> dict:
    if path == "/api/encyclo":
        return ENC
    if path.startswith("/api/evo/route"):
        return ROUTE
    raise AssertionError(path)


class DigimonToolsTest(unittest.TestCase):
    def setUp(self):
        dt.set_fetcher(fake)

    def tearDown(self):
        dt.set_fetcher(None)

    def test_species_shows_bot_values_and_site_only_as_unverified(self):
        text, err = dt.call("digimon_species", {"name": "파피몬"})
        self.assertFalse(err)
        self.assertIn("체력 100", text)
        self.assertIn("→ 가루몬: 바이탈 1200+ · PP 5+ · 배틀 48+ · 진화시간 24시간 (봇 기록)", text)
        self.assertIn("→ 고릴라몬: 바이탈 1000+ · PP 5+ (사이트 값 · 검증 전)", text)
        self.assertIn("80% 일치", text)

    def test_name_matching_is_forgiving(self):
        self.assertEqual(dt.find_species(ENC, "오메가몬(X항체)"), "오메가몬 X")
        self.assertEqual(dt.find_species(ENC, "파피"), "파피몬")
        text, err = dt.call("digimon_species", {"name": "없는몬"})
        self.assertTrue(err)

    def test_dim_tree(self):
        text, err = dt.call("digimon_dim", {"dim": "파피몬ex"})
        self.assertFalse(err)
        self.assertIn("획득처 서버 해안", text)
        self.assertIn("- 성숙기: 가루몬 (추정), ???", text)
        self.assertIn("파피몬 → 가루몬", text)

    def test_route_and_search(self):
        text, err = dt.call("digimon_route", {"name": "가루몬", "limit": 3})
        self.assertFalse(err); self.assertIn("1. 파피몬 EX 알 → 파피몬 → 가루몬", text)
        text, err = dt.call("digimon_search", {"query": "파피"})
        self.assertFalse(err); self.assertIn("- 파피몬 · 성장기", text); self.assertIn("[DIM] 파피몬 EX", text); self.assertNotIn("알 ·", text)

    def test_rank_and_grade(self):
        text, err = dt.call("digimon_species", {"name": "파피몬"})
        self.assertIn("등급 S — 성장기 총합 155 · 1위/2", text)
        text, err = dt.call("digimon_rank", {"stage": "성장기", "sort": "atk"})
        self.assertFalse(err); self.assertTrue(text.splitlines()[1].startswith("1. 아구몬 [A] 체력 90 · 전투력 20"))
        self.assertTrue(dt.call("digimon_rank", {"sort": "zzz"})[1])

    def test_backend_down_is_error_not_crash(self):
        def boom(path):
            raise OSError("connection refused")
        dt.set_fetcher(boom)
        text, err = dt.call("digimon_species", {"name": "파피몬"})
        self.assertTrue(err); self.assertIn("연결하지 못했습니다", text)

    def test_dispatched_through_mcp_server(self):
        resp = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "digimon_species", "arguments": {"name": "파피몬"}}})
        self.assertFalse(resp["result"]["isError"])
        self.assertIn("# 파피몬", resp["result"]["content"][0]["text"])
        names = {t["name"] for t in mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]}
        self.assertIn("digimon_route", names)


if __name__ == "__main__":
    unittest.main()
