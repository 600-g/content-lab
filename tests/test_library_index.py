"""scripts.library.index / scripts.library.search 단위 테스트 (unittest, 외부 네트워크 0)."""
from __future__ import annotations

import shutil
import unittest

from tests.fixtures import SKILLS, make_mirror

from scripts.library import index as lib_index
from scripts.library import search as lib_search


class FrontmatterParseTest(unittest.TestCase):
    def test_parse_full_frontmatter(self):
        text = (
            "---\nname: foo\ndescription: 설명 한 줄: 콜론 포함\norigin: content-lab\n"
            "grade: S\ndifficulty: 초급\ncategory: 콘텐츠\nai_tools: [\"ChatGPT\", \"Claude\"]\n"
            "sources:\n  - https://a.example/1\n  - https://b.example/2\n---\n\n# 제목\n\n본문\n"
        )
        meta, body = lib_index.parse_frontmatter(text)
        self.assertEqual(meta["name"], "foo")
        self.assertEqual(meta["description"], "설명 한 줄: 콜론 포함")
        self.assertEqual(meta["grade"], "S")
        self.assertEqual(meta["ai_tools"], ["ChatGPT", "Claude"])
        self.assertEqual(meta["sources"], ["https://a.example/1", "https://b.example/2"])
        self.assertTrue(body.startswith("# 제목"))

    def test_no_frontmatter_returns_empty_meta(self):
        meta, body = lib_index.parse_frontmatter("# 그냥 본문\n\n내용")
        self.assertEqual(meta, {})
        self.assertEqual(body, "# 그냥 본문\n\n내용")


class LoadIndexTest(unittest.TestCase):
    def setUp(self):
        self.root = make_mirror()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_loads_all_records_and_fills_missing_fields(self):
        idx = lib_index.load_index(self.root)
        self.assertEqual(len(idx.records), len(SKILLS))
        legacy = idx.get("legacy-no-meta")
        self.assertIsNotNone(legacy)
        self.assertEqual(legacy.category, "기타")   # 누락 → 보정
        self.assertEqual(legacy.grade, "")
        self.assertEqual(legacy.title, "옛 포맷 스킬")  # H1 에서 제목 추출

        reels = idx.get("instagram-reels-script-automation")
        self.assertEqual(reels.category, "콘텐츠")
        self.assertEqual(reels.ai_tools, ("ChatGPT", "Claude"))
        self.assertEqual(reels.source_types, ("youtube",))
        self.assertIn("후킹", reels.body_md)
        self.assertTrue(reels.raw_md.startswith("---"))

    def test_source_type_detection(self):
        idx = lib_index.load_index(self.root)
        self.assertEqual(idx.get("notion-mcp-setup").source_types, ("notion",))
        self.assertEqual(idx.get("stock-analysis-prompts").source_types, ("web", "github"))

    def test_stats_and_filter(self):
        idx = lib_index.load_index(self.root)
        st = idx.stats()
        self.assertEqual(st["total"], 4)
        self.assertEqual(st["by_category"]["콘텐츠"], 1)
        self.assertEqual(st["by_grade"]["S"], 1)
        only_dev = idx.filter(category="개발")
        self.assertEqual([r.slug for r in only_dev], ["notion-mcp-setup"])

    def test_version_changes_when_file_changes(self):
        idx1 = lib_index.load_index(self.root)
        p = self.root / "legacy-no-meta" / "SKILL.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n추가 줄\n", encoding="utf-8")
        import os, time
        t = time.time() + 5
        os.utime(p, (t, t))
        idx2 = lib_index.load_index(self.root)
        self.assertNotEqual(idx1.version, idx2.version)

    def test_broken_file_is_skipped_not_fatal(self):
        bad = self.root / "broken"
        bad.mkdir()
        (bad / "SKILL.md").write_bytes(b"\xff\xfe\x00 not utf8 \x80")
        idx = lib_index.load_index(self.root)
        self.assertEqual(len(idx.records), len(SKILLS))  # broken 제외, 나머지 정상

    def test_get_index_cache_invalidates_on_change(self):
        idx1 = lib_index.get_index(self.root, force=True)
        (self.root / "new-skill").mkdir()
        (self.root / "new-skill" / "SKILL.md").write_text(
            "---\nname: new-skill\ndescription: 새 스킬\norigin: content-lab\nsources:\n  - https://x.example\n---\n\n# 새 스킬\n", encoding="utf-8"
        )
        idx2 = lib_index.get_index(self.root, force=True)
        self.assertEqual(len(idx2.records), len(idx1.records) + 1)


class TokenizeTest(unittest.TestCase):
    def test_korean_bigrams_and_english_words(self):
        toks = lib_search.tokenize("인스타그램 Reels 대본, ChatGPT!")
        self.assertIn("인스타그램", toks)
        self.assertIn("인스", toks)      # 2-gram
        self.assertIn("타그", toks)
        self.assertIn("reels", toks)
        self.assertIn("chatgpt", toks)
        self.assertNotIn("reel", toks)   # 영문 prefix 확장 안 함

    def test_empty(self):
        self.assertEqual(lib_search.tokenize(""), [])
        self.assertEqual(lib_search.tokenize("   "), [])


class KeywordSearchTest(unittest.TestCase):
    def setUp(self):
        self.root = make_mirror()
        self.idx = lib_index.load_index(self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_title_match_outranks_body_mention(self):
        # "인스타" 는 reels 제목/설명 + legacy 본문 한 번 — 제목 가중으로 reels 가 1위
        ranked = lib_search.keyword_rank("인스타 대본", self.idx)
        self.assertEqual(ranked[0][0], "instagram-reels-script-automation")
        slugs = [s for s, _ in ranked]
        self.assertIn("legacy-no-meta", slugs)
        self.assertNotIn("stock-analysis-prompts", slugs)

    def test_english_tool_name(self):
        ranked = lib_search.keyword_rank("gemini 주식", self.idx)
        self.assertEqual(ranked[0][0], "stock-analysis-prompts")

    def test_no_match_returns_empty(self):
        # 주의: 한글은 2-gram 매칭이라 "없는단어" 같은 질의는 설명의 "없는" 에 걸린다 (의도된 동작).
        self.assertEqual(lib_search.keyword_rank("zzqqxx 쿼터니언", self.idx), [])

    def test_korean_bigram_recall(self):
        # "인스타그램" 으로 물어도 "인스타" 만 있는 본문이 잡혀야 한다
        ranked = lib_search.keyword_rank("인스타그램", self.idx)
        self.assertIn("instagram-reels-script-automation", [s for s, _ in ranked])


class FusionTest(unittest.TestCase):
    def test_rrf_prefers_items_present_in_both_lists(self):
        kw = [("a", 10.0), ("b", 5.0), ("c", 1.0)]
        sem = [("c", 0.9), ("a", 0.8)]
        fused = lib_search.rrf_fuse({"kw": kw, "sem": sem})
        order = [s for s, _ in fused]
        # a: kw rank1 + sem rank2, c: kw rank3 + sem rank1, b: kw rank2 only
        self.assertEqual(order[0], "a")
        self.assertIn(order[1], ("c",))  # c (두 리스트) 가 b (한 리스트) 보다 위
        self.assertEqual(order[-1], "b")

    def test_rrf_single_list_keeps_order(self):
        fused = lib_search.rrf_fuse({"kw": [("x", 3.0), ("y", 2.0)]})
        self.assertEqual([s for s, _ in fused], ["x", "y"])


class SearchApiTest(unittest.TestCase):
    """search() — 의미 검색은 embed 함수를 주입해서 네트워크 없이 검증."""

    def setUp(self):
        self.root = make_mirror()
        self.idx = lib_index.load_index(self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_keyword_mode_when_embedding_unavailable(self):
        res = lib_search.search(
            "인스타 대본", index=self.idx, mode="hybrid",
            embed_fn=lambda q: None, vectors={},
        )
        self.assertTrue(res["ok"])
        self.assertFalse(res["semantic_used"])
        self.assertEqual(res["results"][0]["slug"], "instagram-reels-script-automation")
        r0 = res["results"][0]
        for key in ("title", "description", "category", "grade", "score", "kw_rank", "snippet", "detail_url"):
            self.assertIn(key, r0)

    def test_hybrid_uses_vectors_when_available(self):
        # 질의 벡터 [1,0], notion-mcp 가 [1,0] 으로 완전 일치, 나머지는 직교
        vectors = {
            "notion-mcp-setup": [1.0, 0.0],
            "instagram-reels-script-automation": [0.0, 1.0],
        }
        res = lib_search.search(
            "워크스페이스 연결", index=self.idx, mode="hybrid",
            embed_fn=lambda q: [1.0, 0.0], vectors=vectors,
        )
        self.assertTrue(res["semantic_used"])
        self.assertEqual(res["results"][0]["slug"], "notion-mcp-setup")
        self.assertEqual(res["results"][0]["sem_rank"], 1)

    def test_filters_and_k(self):
        res = lib_search.search(
            "프롬프트", index=self.idx, k=1, category="업무",
            embed_fn=lambda q: None, vectors={},
        )
        self.assertEqual(len(res["results"]), 1)
        self.assertEqual(res["results"][0]["category"], "업무")

    def test_query_validation(self):
        res = lib_search.search("a", index=self.idx, embed_fn=lambda q: None, vectors={})
        self.assertFalse(res["ok"])
        self.assertIn("error", res)

    def test_embed_exception_is_swallowed(self):
        def boom(q):
            raise RuntimeError("quota")
        res = lib_search.search("인스타", index=self.idx, embed_fn=boom, vectors={"x": [1.0]})
        self.assertTrue(res["ok"])
        self.assertFalse(res["semantic_used"])


if __name__ == "__main__":
    unittest.main()
