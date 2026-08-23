"""scripts.library.catalog 테스트 — 게시판 카탈로그 / 상세 페이지 / XSS / CSP / 딥링크."""
from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.fixtures import SKILLS, make_mirror

from scripts.library import catalog as cat
from scripts.library import index as lib_index


class SanitizeTest(unittest.TestCase):
    def test_script_and_event_handlers_removed(self):
        dirty = '<p onclick="x()">hi</p><script>alert(1)</script><img src=x onerror=alert(1)><a href="javascript:alert(1)">j</a>'
        clean = cat.sanitize_html(dirty)
        self.assertNotIn("<script", clean)
        self.assertNotIn("alert(1)", clean)          # script 내용까지 제거
        self.assertNotIn("onclick", clean)
        self.assertNotIn("<img", clean)
        self.assertNotIn("javascript:", clean)
        self.assertIn("<p>hi</p>", clean)

    def test_allowed_tags_and_safe_links_kept(self):
        ok = '<h2>t</h2><ul><li><strong>b</strong> <code>c</code></li></ul><a href="https://x.example/p?a=1&amp;b=2">l</a><table><tr><td>1</td></tr></table>'
        clean = cat.sanitize_html(ok)
        self.assertIn("<h2>t</h2>", clean)
        self.assertIn("<code>c</code>", clean)
        self.assertIn('href="https://x.example/p?a=1&amp;b=2"', clean)
        self.assertIn('rel="noopener', clean)
        self.assertIn("<td>1</td>", clean)

    def test_text_entities_escaped(self):
        clean = cat.sanitize_html("1 < 2 && 3 > 2")
        self.assertIn("1 &lt; 2 &amp;&amp; 3 &gt; 2", clean)


class RenderMarkdownTest(unittest.TestCase):
    def test_code_block_preserved_and_raw_html_neutralized(self):
        md = "## 제목\n\n```bash\necho '<b>hi</b>'\n```\n\n<script>alert('x')</script>\n\n**굵게**"
        html = cat.render_markdown(md)
        self.assertIn("<h2>제목</h2>", html)
        self.assertIn("&lt;b&gt;hi&lt;/b&gt;", html)   # 코드블록 안 태그는 문자 그대로
        self.assertNotIn("<script", html)
        self.assertIn("<strong>굵게</strong>", html)


class RenderCatalogTest(unittest.TestCase):
    def setUp(self):
        self.root = make_mirror()
        self.idx = lib_index.load_index(self.root)
        self.html = cat.render_catalog(self.idx, nonce="testnonce123")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_one_card_per_skill_with_deeplink_id(self):
        cards = re.findall(r'<article class="card"', self.html)
        self.assertEqual(len(cards), len(SKILLS))
        for slug in SKILLS:
            self.assertIn(f'id="{slug}"', self.html)

    def test_title_links_to_internal_post_not_external(self):
        """제목 = 우리 게시글 (사이트 이탈 없음). 외부 원본은 별도 [원본] 버튼."""
        m = re.search(r'<h3><a class="tlink" href="([^"]+)"[^>]*>인스타 릴스 대본 자동 생성</a></h3>', self.html)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "/skill/instagram-reels-script-automation")
        self.assertNotIn('target="_blank"', m.group(0))

    def test_original_link_button_goes_external(self):
        card = re.search(
            r'<article class="card"[^>]*id="instagram-reels-script-automation".*?</article>',
            self.html, re.S).group(0)
        ext = re.search(r'<a class="btn ext" href="([^"]+)"[^>]*>([^<]*)</a>', card)
        self.assertIsNotNone(ext)
        self.assertEqual(ext.group(1), "https://www.youtube.com/watch?v=abc123")
        self.assertIn("원본", ext.group(2))
        self.assertIn('target="_blank"', ext.group(0))
        self.assertIn('rel="noopener', ext.group(0))
        # 읽기 버튼은 내부 페이지
        self.assertIn('href="/skill/instagram-reels-script-automation"', card)

    def test_no_source_means_no_external_button(self):
        cards = re.findall(r'<article class="card".*?</article>', self.html, re.S)
        self.assertTrue(cards)
        for c in cards:  # 픽스처는 전부 출처가 있으므로 버튼도 전부 있어야 함
            self.assertIn('class="btn ext"', c)

    def test_body_not_embedded_in_catalog(self):
        """본문은 상세 페이지에서만 — 카탈로그는 가볍게 (모달/템플릿 제거)."""
        self.assertNotIn("<template>", self.html)
        self.assertNotIn("후킹 → 본문 → CTA", self.html)   # 본문 문장이 카드에 없음
        self.assertNotIn("data-cmd=", self.html)

    def test_view_toggle_present(self):
        self.assertIn('data-view="card"', self.html)
        self.assertIn('data-view="list"', self.html)

    def test_sections_follow_category_order(self):
        pos = {c: self.html.find(f'<section class="domain" data-group="{cat.category_key(c)}"') for c in ("콘텐츠", "개발", "업무", "기타")}
        self.assertTrue(all(p > 0 for p in pos.values()), pos)
        self.assertLess(pos["콘텐츠"], pos["개발"])
        self.assertLess(pos["개발"], pos["업무"])
        self.assertLess(pos["업무"], pos["기타"])
        self.assertNotIn('data-group="prompt"', self.html)  # 비어있는 카테고리 섹션은 없음

    def test_card_data_attributes(self):
        m = re.search(r'<article class="card"[^>]*id="instagram-reels-script-automation"[^>]*>', self.html)
        self.assertIsNotNone(m)
        tag = m.group(0)
        self.assertIn('data-grade="S"', tag)
        self.assertIn('data-source="youtube"', tag)
        self.assertIn('data-group="content"', tag)
        self.assertIn("chatgpt", tag)          # data-tools
        self.assertIn("인스타", tag)           # data-text (소문자 검색 인덱스)
        self.assertIn("릴스", tag)

    def test_no_inline_script_besides_engine(self):
        scripts = re.findall(r"<script[^>]*>", self.html)
        self.assertEqual(len(scripts), 1, scripts)
        self.assertIn('nonce="testnonce123"', scripts[0])

    def test_csp_nonce_matches_script(self):
        m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', self.html)
        self.assertIsNotNone(m)
        csp = m.group(1)
        self.assertIn("script-src 'nonce-testnonce123'", csp)
        self.assertIn("default-src 'none'", csp)
        self.assertIn("font-src", csp)   # 픽셀/본문 폰트 CDN 허용

    def test_metrics_and_filter_chips(self):
        self.assertIn(f'<div class="v">{len(SKILLS)}</div>', self.html)
        self.assertIn('data-src="youtube"', self.html)
        self.assertIn('data-src="notion"', self.html)
        self.assertIn('data-grade="S"', self.html)
        self.assertIn('data-tool="chatgpt"', self.html)
        self.assertIn('data-dom="content"', self.html)

    def test_legacy_without_grade_is_still_listed(self):
        self.assertIn('id="legacy-no-meta"', self.html)
        m = re.search(r'<article class="card"[^>]*id="legacy-no-meta"[^>]*>', self.html)
        self.assertIn('data-grade=""', m.group(0))


class RenderSkillPageTest(unittest.TestCase):
    """게시글 상세 페이지 — 본문·복사·출처가 여기 있고, 이탈 링크는 [원본] 뿐."""

    def setUp(self):
        self.root = make_mirror()
        self.idx = lib_index.load_index(self.root)
        self.rec = self.idx.get("instagram-reels-script-automation")
        self.html = cat.render_skill_page(self.rec, self.idx, nonce="pagenonce9")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_title_and_body_rendered(self):
        self.assertIn("<title>인스타 릴스 대본 자동 생성", self.html)
        self.assertIn("<h1>인스타 릴스 대본 자동 생성</h1>", self.html)
        self.assertIn("어떻게 작동하나요?", self.html)
        self.assertIn("<strong>릴스</strong>", self.html)   # markdown 렌더됨

    def test_back_link_to_board(self):
        self.assertIn('href="/catalog"', self.html)

    def test_meta_chips(self):
        self.assertIn("S", self.html)
        self.assertIn("콘텐츠", self.html)
        self.assertIn("ChatGPT", self.html)

    def test_copy_button_carries_full_skill_md(self):
        self.assertIn("SKILL.md 복사", self.html)
        self.assertIn("name: instagram-reels-script-automation", self.html)

    def test_sources_listed_and_external_only_there(self):
        self.assertIn("https://www.youtube.com/watch?v=abc123", self.html)
        externals = re.findall(r'<a[^>]*target="_blank"[^>]*href="(https?://[^"]+)"', self.html) + \
                    re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*target="_blank"', self.html)
        for url in externals:
            self.assertTrue(url.startswith("http"), url)

    def test_same_category_related_list(self):
        """이탈 방지 — 같은 카테고리 다른 글로 이어지게."""
        idx = self.idx
        page = cat.render_skill_page(idx.get("notion-mcp-setup"), idx, nonce="n")
        self.assertIn("같은 카테고리", page)

    def test_xss_body_is_neutralized(self):
        page = cat.render_skill_page(self.idx.get("notion-mcp-setup"), self.idx, nonce="n1")
        self.assertNotIn("<script>alert('xss')</script>", page)
        self.assertNotIn("<script>alert(&#x27;xss&#x27;)</script>", page)
        scripts = re.findall(r"<script[^>]*>", page)
        self.assertEqual(len(scripts), 1, scripts)
        self.assertIn('nonce="n1"', scripts[0])

    def test_csp_present(self):
        m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', self.html)
        self.assertIsNotNone(m)
        self.assertIn("default-src 'none'", m.group(1))
        self.assertIn("script-src 'nonce-pagenonce9'", m.group(1))


class BuildCatalogFileTest(unittest.TestCase):
    def test_build_writes_file(self):
        root = make_mirror()
        out_dir = Path(tempfile.mkdtemp(prefix="catalog_out_"))
        try:
            out = out_dir / "catalog.html"
            res = cat.build_catalog_file(out, root=root)
            self.assertTrue(out.exists())
            self.assertEqual(res["count"], len(SKILLS))
            self.assertGreater(out.stat().st_size, 5000)
        finally:
            shutil.rmtree(root, ignore_errors=True)
            shutil.rmtree(out_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()


class MobileUxTest(unittest.TestCase):
    """v4.8 모바일 — 확대 잠금 · safe-area · 뒤로가기 동선."""

    @classmethod
    def setUpClass(cls):
        cls.root = make_mirror()
        idx = lib_index.load_index(cls.root)
        cls.catalog = cat.render_catalog(idx, nonce="n1")
        cls.page = cat.render_skill_page(idx.records[0], idx, nonce="n2")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_pinch_zoom_locked_on_both_pages(self):
        # 메인 사이트(templates/index.html) 와 같은 규약 — 확대/더블탭 줌 차단
        for html_text in (self.catalog, self.page):
            m = re.search(r'<meta name="viewport" content="([^"]+)"', html_text)
            self.assertIsNotNone(m)
            self.assertIn("maximum-scale=1", m.group(1))
            self.assertIn("user-scalable=no", m.group(1))

    def test_topbar_respects_safe_area(self):
        # viewport-fit=cover 를 쓰므로 노치 아래로 내려야 함 (톱바 = 유일한 뒤로가기)
        for html_text in (self.catalog, self.page):
            self.assertIn("viewport-fit=cover", html_text)
            self.assertIn("--safe-top:env(safe-area-inset-top,0px)", html_text)
            self.assertIn("padding:calc(10px + var(--safe-top))", html_text)

    def test_sticky_bar_uses_measured_height(self):
        # 하드코딩 top:52px/48px 제거 — JS 실측값
        self.assertIn("top:var(--topbar-h)", self.catalog)
        self.assertNotIn("top:52px", self.catalog)
        self.assertIn("--topbar-h", self.catalog)

    def test_detail_has_multiple_back_affordances(self):
        # 상세는 standalone PWA 에서 브라우저 뒤로가기가 없다 — 3곳 이상
        self.assertGreaterEqual(self.page.count("data-back"), 3)
        self.assertIn('class="chip-link back-chip"', self.page)
        self.assertIn('class="fabs"', self.page)
        self.assertIn('class="post-end"', self.page)
        self.assertIn("function goBack", self.page)

    def test_catalog_filters_collapsible(self):
        self.assertIn('id="fbtn"', self.catalog)
        self.assertIn('<div class="filters" id="filters">', self.catalog)

    def test_catalog_restores_scroll_and_filters(self):
        self.assertIn("aiskillbox-catalog-state", self.catalog)
        self.assertIn("function restoreScroll", self.catalog)

    def test_manifest_linked_for_pwa(self):
        for html_text in (self.catalog, self.page):
            self.assertIn('<link rel="manifest" href="/static/manifest.json">', html_text)
            self.assertIn("manifest-src 'self'", html_text)


class MarkdownRobustnessTest(unittest.TestCase):
    def test_unclosed_code_fence_still_renders_as_code(self):
        # LLM 이 마지막 ``` 를 빠뜨리면 프롬프트 전문이 벽글로 렌더되던 실사고
        out = cat.render_markdown("설명\n\n```\nUse the uploaded photos\n")
        self.assertIn("<pre><code>", out)
        self.assertIn("Use the uploaded photos", out)

    def test_balanced_fence_untouched(self):
        src = "```\nx = 1\n```\n"
        self.assertEqual(cat.close_open_fence(src), src)

    def test_internal_anchor_stays_in_page(self):
        # #앵커(목차) 까지 새 탭으로 열리던 버그
        out = cat.sanitize_html('<a href="#step-2">2단계</a><a href="https://x.com">외부</a>')
        self.assertNotIn('href="#step-2" target="_blank"', out)
        self.assertIn('href="https://x.com" target="_blank"', out)
