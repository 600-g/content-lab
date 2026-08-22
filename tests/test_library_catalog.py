"""scripts.library.catalog 테스트 — 카드/섹션/XSS/CSP/딥링크."""
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

    def test_xss_body_is_neutralized(self):
        self.assertNotIn("<script>alert('xss')</script>", self.html)
        self.assertNotIn("<script>alert(&#x27;xss&#x27;)</script>", self.html)
        # 엔진 스크립트 1개 (nonce 달린 것) 만 존재
        scripts = re.findall(r"<script[^>]*>", self.html)
        self.assertEqual(len(scripts), 1, scripts)
        self.assertIn('nonce="testnonce123"', scripts[0])

    def test_csp_nonce_matches_script(self):
        m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', self.html)
        self.assertIsNotNone(m)
        self.assertIn("script-src 'nonce-testnonce123'", m.group(1))
        self.assertIn("default-src 'none'", m.group(1))

    def test_copy_button_carries_full_skill_md(self):
        # data-cmd 에 frontmatter 포함 전문 (속성 이스케이프 상태)
        self.assertIn("name: instagram-reels-script-automation", self.html)
        self.assertIn("SKILL.md 복사", self.html)

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
