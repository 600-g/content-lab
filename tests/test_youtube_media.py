"""유튜브 — 자막이 없으면 영상 자체를 미디어 이해 단계로 넘기는지 (네트워크 0)."""
from __future__ import annotations

import unittest
from unittest import mock

from scripts.scraper import youtube


META = {"id": "abc123", "title": "제목", "description": "설명문", "duration": 90, "channel": "c"}


class YoutubeMediaFlagTest(unittest.TestCase):
    def test_no_subtitles_flags_media(self):
        with mock.patch.object(youtube, "_run_yt_dlp", return_value=META), \
             mock.patch.object(youtube, "_fetch_subtitles", return_value=""):
            r = youtube.scrape("https://www.youtube.com/watch?v=abc123")
        self.assertEqual(r.meta["media"], [{"kind": "youtube", "url": "https://www.youtube.com/watch?v=abc123", "key": "yt:abc123"}])
        self.assertIn("[설명]", r.text)

    def test_subtitles_present_means_no_media(self):
        with mock.patch.object(youtube, "_run_yt_dlp", return_value=META), \
             mock.patch.object(youtube, "_fetch_subtitles", return_value="자막 텍스트"):
            r = youtube.scrape("https://www.youtube.com/watch?v=abc123")
        self.assertNotIn("media", r.meta)

    def test_too_long_video_is_not_flagged(self):
        with mock.patch.object(youtube, "_run_yt_dlp", return_value={**META, "duration": 7200}), \
             mock.patch.object(youtube, "_fetch_subtitles", return_value=""):
            r = youtube.scrape("https://www.youtube.com/watch?v=abc123")
        self.assertNotIn("media", r.meta)


if __name__ == "__main__":
    unittest.main()
