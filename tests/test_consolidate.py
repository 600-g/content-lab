"""library/consolidate — 이미 등록된 스킬 두 개를 하나로 합친다 (네트워크·프로세스 0, merge 주입).

사용자 원칙 (2026-09-16): 정확히 유사하고 카테고리가 겹치면 합쳐 간소화. 흡수된 스킬은 백업 후 삭제,
출처 URL 은 합집합으로 보존. 합병 LLM 이 실패하면 아무것도 지우지 않는다.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.analyzer import embedder
from scripts.analyzer.gemini import AnalysisResult
from scripts.library import consolidate as cs

SKILL = """---
name: {slug}
description: 설명 {slug}
origin: content-lab
grade: A
difficulty: 초급
category: 개발
ai_tools: ["Claude"]
sources:
  - https://example.com/{slug}
---

# 제목 {slug}

💡 콜아웃 {slug}

## 이게 뭔가요?
본문 {slug} """ + ("내용 " * 300)


def _write(root: Path, slug: str) -> Path:
    p = root / slug / "SKILL.md"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(SKILL.format(slug=slug), encoding="utf-8"); return p


def _merged(existing_path, new_result, url, src_type) -> AnalysisResult:
    body = "## 이게 뭔가요?\n합병 본문 " + ("내용 " * 400)
    r = AnalysisResult(skill_name="keeper", skill_title_ko="합쳐진 스킬", category="개발", grade="S", grade_reason="",
                       targets=[], summary="", when_to_use="", memo="", ai_tools=["Claude"], tags=[], difficulty="초급",
                       callout="합쳐진 콜아웃", body_md=body, body_content=body, raw={"body_md": body}, provider="claude")
    r.raw["_is_merged"] = True
    r.raw["_merged_source_urls"] = ["https://example.com/keeper", url]
    return r


class MergePairTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); d = Path(self.tmp.name)
        self.m, self.g, self.b = d / "mirror", d / "global", d / "backup"
        for root in (self.m, self.g):
            _write(root, "keeper"); _write(root, "absorbed")
        # merge_pair 는 실경로 embeddings.json 을 갱신한다 — 막지 않으면 유령 'keeper' 키 + 실제 API 호출 (gotcha 52)
        for name in ("get_or_embed", "invalidate"):
            patcher = mock.patch.object(embedder, name)
            patcher.start(); self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def test_result_from_skill_reads_title_callout_and_body(self):
        r = cs.result_from_skill(self.m / "absorbed" / "SKILL.md")
        self.assertEqual(r.skill_name, "absorbed"); self.assertEqual(r.skill_title_ko, "제목 absorbed")
        self.assertEqual(r.callout, "콜아웃 absorbed"); self.assertIn("본문 absorbed", r.body_md)
        self.assertEqual(r.category, "개발"); self.assertEqual(r.grade, "A")

    def test_merge_writes_keeper_and_removes_absorbed(self):
        out = cs.merge_pair("keeper", "absorbed", mirror_dir=self.m, global_dir=self.g, backup_dir=self.b, merge=_merged)
        self.assertTrue(out["ok"], out)
        for root in (self.m, self.g):
            text = (root / "keeper" / "SKILL.md").read_text()
            self.assertIn("합쳐진 스킬", text); self.assertIn("https://example.com/absorbed", text)
            self.assertFalse((root / "absorbed").exists(), "흡수된 스킬은 지운다")
            self.assertIn("`absorbed`", text, "원본 목록에 흡수된 문서")
        self.assertTrue((self.b / "absorbed" / "SKILL.md").exists(), "지우기 전 백업")
        self.assertEqual(out["provider"], "claude"); self.assertEqual(out["sources"], 2)

    def test_failed_merge_deletes_nothing(self):
        def fail(existing_path, new_result, url, src_type):
            return new_result   # merger 가 실패하면 신규 결과를 그대로 돌려준다 (_is_merged 없음)
        out = cs.merge_pair("keeper", "absorbed", mirror_dir=self.m, global_dir=self.g, backup_dir=self.b, merge=fail)
        self.assertFalse(out["ok"])
        self.assertTrue((self.m / "absorbed").exists()); self.assertTrue((self.g / "absorbed").exists())
        self.assertIn("본문 keeper", (self.m / "keeper" / "SKILL.md").read_text(), "keeper 도 그대로")

    def test_missing_skill_is_reported(self):
        out = cs.merge_pair("keeper", "nope", mirror_dir=self.m, global_dir=self.g, backup_dir=self.b, merge=_merged)
        self.assertFalse(out["ok"]); self.assertIn("nope", out["reason"])


SYNTH = """---
name: keeper
description: 하나로 합성한 설명
origin: content-lab
grade: S
difficulty: 초급
category: 개발
ai_tools: ["Claude"]
sources:
  - https://example.com/keeper
  - https://example.com/a
  - https://example.com/b
---

# 합성한 제목

💡 합성 콜아웃

## 이게 뭔가요?
합성 본문

## 따라하기
```
## 코드블록 안의 대제목은 프롬프트 원문이라 검사하지 않는다
```

## 출처

- [https://example.com/keeper](https://example.com/keeper)
"""


class ApplySynthesizedTest(unittest.TestCase):
    """2026-10-05 사용자 지시 — 여러 문서를 이어붙이지 말고 묶음 전체를 새로 쓴 한 문서로 교체."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); d = Path(self.tmp.name)
        self.m, self.g, self.b = d / "mirror", d / "global", d / "backup"
        for slug in ("keeper", "a", "b"):
            _write(self.m, slug)
        _write(self.g, "a")  # 흡수 대상 하나만 전역에 있다
        for name in ("get_or_embed", "invalidate"):
            patcher = mock.patch.object(embedder, name)
            patcher.start(); self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def _apply(self, content):
        return cs.apply_synthesized("keeper", ["a", "b"], content, mirror_dir=self.m, global_dir=self.g, backup_dir=self.b)

    def test_replaces_keeper_and_absorbs_all(self):
        out = self._apply(SYNTH)
        self.assertTrue(out["ok"], out)
        self.assertTrue((self.m / "keeper" / "SKILL.md").read_text().startswith(SYNTH.split("## 출처")[0][:200]))
        for slug in ("a", "b"):
            self.assertFalse((self.m / slug).exists()); self.assertTrue((self.b / slug / "SKILL.md").exists())
        self.assertFalse((self.g / "a").exists())
        self.assertEqual((self.g / "keeper" / "SKILL.md").read_text(), (self.m / "keeper" / "SKILL.md").read_text(),
                         "멤버 중 하나라도 전역이면 keeper 를 전역에")

    def test_originals_listed_in_synthesized_doc(self):
        self._apply(SYNTH)
        text = (self.m / "keeper" / "SKILL.md").read_text()
        self.assertIn("### 합쳐진 원본 문서", text)
        for slug in ("keeper", "a", "b"):
            self.assertIn(f"`{slug}`", text)
        self.assertIn("  - a | 제목 a | https://example.com/a", text)

    def test_missing_source_changes_nothing(self):
        out = self._apply(SYNTH.replace("  - https://example.com/b\n", ""))
        self.assertFalse(out["ok"]); self.assertIn("출처 누락", out["reason"])
        self.assertTrue((self.m / "b").exists()); self.assertIn("본문 keeper", (self.m / "keeper" / "SKILL.md").read_text())

    def test_merge_badge_and_bad_heading_rejected(self):
        bad = SYNTH.replace("# 합성한 제목", "# 합성한 제목 (합병됨)").replace("## 이게 뭔가요?", "## 핵심 패턴")
        probs = cs.check_synthesized(bad, "keeper", [])
        self.assertTrue(any("합병" in p for p in probs)); self.assertTrue(any("대제목" in p for p in probs))

    def test_wrong_slug_rejected(self):
        self.assertTrue(cs.check_synthesized(SYNTH, "other", []))


class NoMergeBadgeTest(unittest.TestCase):
    def test_render_has_no_merge_badge(self):
        from scripts.skill_builder import render_skill_md
        r = _merged(None, None, "https://example.com/x", "web")
        self.assertNotIn("합병됨", render_skill_md(r, "https://example.com/x", "web"))


if __name__ == "__main__":
    unittest.main()
