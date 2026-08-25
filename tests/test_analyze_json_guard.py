"""analyze() 가 LLM JSON 파싱 실패로 잡을 죽이지 않는지 검증 (네트워크 0).

실사고: `job failed: JSON 블록 없음: {...` 3건. gemini.py 의 2차 _extract_json 이
except 블록 안에서 무방어로 호출돼 예외가 analyze() 밖으로 전파 → 워커가 잡 전체를
traceback 으로 실패 처리했고, 사용자에겐 한글 사유도 우회 안내도 가지 않았다.
"""
from __future__ import annotations

import unittest
from unittest import mock

from scripts.analyzer import gemini


TRUNCATED_WITH_NAME = (
    '{\n  "skill_name": "loop-engineering-mastery",\n'
    '  "skill_title_ko": "AI를 알아서 돌게 루프 설계하기",\n  "'
)
TRUNCATED_NO_NAME = '{\n  "category": "자동화",\n  "gra'
NOT_JSON = "죄송합니다. 요청을 처리할 수 없습니다."


class ExtractJsonTest(unittest.TestCase):
    def test_truncated_but_named_is_recovered(self):
        d = gemini._extract_json(TRUNCATED_WITH_NAME)
        self.assertEqual(d["skill_name"], "loop-engineering-mastery")

    def test_unrecoverable_shapes_still_raise(self):
        # 이 두 형태가 그대로 잡을 죽였다 — analyze() 가 반드시 감싸야 하는 입력.
        for bad in (TRUNCATED_NO_NAME, NOT_JSON):
            with self.assertRaises(Exception):
                gemini._extract_json(bad)


class AnalyzeDoesNotRaiseTest(unittest.TestCase):
    """두 모델 모두 파싱 불가여도 예외 대신 ok=False 결과로 정상 종료해야 한다."""

    def _analyze_with(self, gemini_text: str, gemma_text: str):
        fake_model = mock.Mock()
        fake_model.generate_content.return_value = mock.Mock(text=gemini_text)
        fake_genai = mock.Mock()
        fake_genai.GenerativeModel.return_value = fake_model

        scrape_dict = {
            "url": "https://example.com/a", "source_type": "web",
            "title": "제목", "text": "본문 " * 400, "meta": {},
        }
        with mock.patch.dict("sys.modules", {"google.generativeai": fake_genai}), \
             mock.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}), \
             mock.patch.object(gemini, "call_gemma_json", return_value=gemma_text), \
             mock.patch.object(gemini, "_quota_should_skip", return_value=False), \
             mock.patch.object(gemini, "_quota_increment"):
            return gemini.analyze(scrape_dict)

    def test_both_models_unparseable_returns_result_not_raise(self):
        r = self._analyze_with(NOT_JSON, TRUNCATED_NO_NAME)
        self.assertFalse(r.ok)
        self.assertIn("JSON", r.error)

    def test_error_message_is_korean_and_actionable(self):
        r = self._analyze_with(NOT_JSON, NOT_JSON)
        self.assertFalse(r.ok)
        self.assertIn("해석하지 못했습니다", r.error)

    def test_gemma_recovers_when_gemini_output_is_garbage(self):
        good = ('{"skill_name": "x-skill", "skill_title_ko": "테스트 스킬", '
                '"category": "개발", "grade": "A", "body_md": "본문"}')
        r = self._analyze_with(NOT_JSON, good)
        self.assertTrue(r.ok, r.error)
        self.assertEqual(r.skill_name, "x-skill")

    def test_empty_gemma_fallback_returns_result_not_raise(self):
        r = self._analyze_with(NOT_JSON, "")
        self.assertFalse(r.ok)
        self.assertIn("Gemma 폴백 실패", r.error)


if __name__ == "__main__":
    unittest.main()
