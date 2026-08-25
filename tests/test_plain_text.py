"""붙여넣은 일반 텍스트 입력 경로 검증 (네트워크 0).

배경: 스크랩이 구조적으로 불가능한 출처(ChatGPT 공유 링크, IG 피드, 로그인 벽)에 대해
collect.py 는 계속 "본문을 직접 텍스트로 옮겨 등록해 주세요" 라고 안내해 왔는데,
/api/collect 가 http(s) URL 이 아니면 400 으로 튕겨 그 경로가 실재하지 않았다.
"""
from __future__ import annotations

import unittest

from scripts.scraper import plain_text


SAMPLE = (
    "# Claude Code 토큰 절약 5가지\n\n"
    "매 세션 컨텍스트를 줄이는 방법을 정리한다.\n\n"
    "## 따라하기\n"
    "1. `/compact` 로 대화를 압축한다\n"
    "2. CLAUDE.md 를 200줄 밑으로 유지한다\n"
    "3. 서브에이전트에 탐색을 위임한다\n"
) + ("실전에서 검증한 절약 패턴을 계속 덧붙인다. " * 20)


class PasteIdTest(unittest.TestCase):
    def test_same_text_same_id(self):
        self.assertEqual(plain_text.paste_id(SAMPLE), plain_text.paste_id(SAMPLE))

    def test_whitespace_only_diff_is_same(self):
        # 붙여넣기는 줄바꿈/들여쓰기가 쉽게 흔들린다 — 중복 감지가 그것 때문에 깨지면 안 된다.
        a = plain_text.paste_id("가나다  라마바\n\n사아자")
        b = plain_text.paste_id("가나다 라마바\n사아자\n")
        self.assertEqual(a, b)

    def test_different_text_different_id(self):
        self.assertNotEqual(plain_text.paste_id(SAMPLE), plain_text.paste_id(SAMPLE + "다른 내용"))

    def test_paste_url_roundtrip(self):
        u = plain_text.paste_url(SAMPLE)
        self.assertTrue(u.startswith("paste://"))
        self.assertTrue(plain_text.is_paste_source(u))

    def test_real_urls_are_not_paste(self):
        for u in ("https://youtu.be/abc", "http://x.com/y", "", "notion.site/abc"):
            self.assertFalse(plain_text.is_paste_source(u), u)


class DeriveTitleTest(unittest.TestCase):
    def test_markdown_heading_wins(self):
        self.assertEqual(plain_text.derive_title(SAMPLE), "Claude Code 토큰 절약 5가지")

    def test_first_meaningful_line_when_no_heading(self):
        t = plain_text.derive_title("\n\n---\n인스타 릴스 대본 자동화 프롬프트\n나머지 본문\n")
        self.assertEqual(t, "인스타 릴스 대본 자동화 프롬프트")

    def test_url_only_line_is_not_a_title(self):
        t = plain_text.derive_title("https://example.com/very/long\n실제 제목은 이 줄이다\n")
        self.assertEqual(t, "실제 제목은 이 줄이다")

    def test_fallback_when_nothing_usable(self):
        self.assertEqual(plain_text.derive_title("---\n===\n"), "붙여넣은 텍스트")


class PlainTextScrapeTest(unittest.TestCase):
    def test_wraps_text_as_scrape_result(self):
        r = plain_text.scrape(SAMPLE)
        self.assertTrue(r.ok)
        self.assertEqual(r.source_type, "text")
        self.assertEqual(r.title, "Claude Code 토큰 절약 5가지")
        self.assertEqual(r.text, SAMPLE.strip())
        self.assertEqual(r.meta["input_kind"], "paste")
        self.assertTrue(plain_text.is_paste_source(r.url))

    def test_explicit_title_wins(self):
        r = plain_text.scrape(SAMPLE, title="내가 지은 제목")
        self.assertEqual(r.title, "내가 지은 제목")

    def test_origin_url_becomes_the_source(self):
        # 본문만 손으로 옮긴 경우 — 출처는 사용자가 준 원본 URL 이어야 한다.
        r = plain_text.scrape(SAMPLE, origin_url="https://chatgpt.com/share/abc")
        self.assertEqual(r.url, "https://chatgpt.com/share/abc")
        self.assertFalse(plain_text.is_paste_source(r.url))
        self.assertEqual(r.meta["origin_url"], "https://chatgpt.com/share/abc")

    def test_empty_text_is_not_ok(self):
        r = plain_text.scrape("   \n  ")
        self.assertFalse(r.ok)

    def test_oversized_text_is_truncated(self):
        r = plain_text.scrape("가" * (plain_text.TEXT_MAX_LEN + 5000))
        self.assertEqual(len(r.text), plain_text.TEXT_MAX_LEN)


class PastePromptTest(unittest.TestCase):
    def test_prompt_gets_paste_context(self):
        from scripts.analyzer.prompt import build_prompt, PASTE_CONTEXT
        p = build_prompt(plain_text.scrape(SAMPLE).to_dict())
        self.assertIn(PASTE_CONTEXT.strip(), p)

    def test_url_prompt_has_no_paste_context(self):
        from scripts.analyzer.prompt import build_prompt, PASTE_CONTEXT
        p = build_prompt({
            "url": "https://youtu.be/abc", "source_type": "youtube",
            "title": "제목", "text": SAMPLE, "meta": {},
        })
        self.assertNotIn(PASTE_CONTEXT.strip(), p)


class PasteIdentifierLeakTest(unittest.TestCase):
    """paste://<hash> 는 내부 식별자다 — LLM 도 최종 문서도 이걸 링크로 보면 안 된다."""

    def test_prompt_never_shows_the_raw_identifier(self):
        from scripts.analyzer.prompt import build_prompt
        d = plain_text.scrape(SAMPLE).to_dict()
        p = build_prompt(d)
        # 실측: 식별자를 노출하면 모델이 [제목](paste://...) 죽은 링크를 본문에 박았다.
        self.assertNotIn("paste://", p)
        self.assertIn("원본 링크 없음", p)

    def test_prompt_keeps_real_origin_url(self):
        from scripts.analyzer.prompt import build_prompt
        d = plain_text.scrape(SAMPLE, origin_url="https://chatgpt.com/share/x").to_dict()
        self.assertIn("https://chatgpt.com/share/x", build_prompt(d))

    def test_stray_paste_links_are_scrubbed_from_body(self):
        from scripts.skill_builder.md_generator import _scrub_paste_links
        body = "앞 [ChatGPT 프로젝트 기능](paste://ba24cd7951b1fd38) 뒤"
        out = _scrub_paste_links(body)
        self.assertNotIn("paste://", out)
        self.assertIn("ChatGPT 프로젝트 기능", out)

    def test_scrub_leaves_real_links_alone(self):
        from scripts.skill_builder.md_generator import _scrub_paste_links
        body = "[문서](https://example.com/a) 와 [영상](https://youtu.be/b)"
        self.assertEqual(_scrub_paste_links(body), body)

    def test_scrub_handles_empty_link_text(self):
        from scripts.skill_builder.md_generator import _scrub_paste_links
        self.assertEqual(_scrub_paste_links("[](paste://abc123)"), "직접 입력한 텍스트")


class PasteRenderingTest(unittest.TestCase):
    """paste:// 는 진짜 URL 이 아니다 — 어디서도 클릭 가능한 링크로 렌더되면 안 된다."""

    def test_library_index_maps_paste_to_text_source(self):
        from scripts.library.index import source_type
        self.assertEqual(source_type("paste://abc123"), "text")
        self.assertEqual(source_type("https://github.com/a/b"), "github")

    def test_skill_md_renders_paste_source_as_label(self):
        from scripts.skill_builder.md_generator import _source_line
        self.assertNotIn("](", _source_line("paste://deadbeef"))
        self.assertIn("직접 입력", _source_line("paste://deadbeef"))
        self.assertIn("](https://x.com/y)", _source_line("https://x.com/y"))

    def test_catalog_origin_button_skips_paste_only_sources(self):
        from scripts.library import catalog
        self.assertTrue(catalog._is_paste("paste://abc"))
        self.assertFalse(catalog._is_paste("https://notion.site/abc"))


if __name__ == "__main__":
    unittest.main()
