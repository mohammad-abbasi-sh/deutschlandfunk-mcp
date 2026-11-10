"""Live tests — hit the real deutschlandfunk.de RSS feeds + one article. Cautious: few requests.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set DLF_SKIP_LIVE=1)
"""
import json
import os
import pathlib
import sys
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from deutschlandfunk_mcp import server as srv

pytestmark = pytest.mark.live
SKIP = os.environ.get("DLF_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="DLF_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_news_live(self):
        out = json.loads(srv.dlf_latest_news(limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        print(f"\nLIVE news: {out['total_results']} — {out['items'][0]['title'][:60]}")

    def test_contributions_live(self):
        out = json.loads(srv.dlf_latest_contributions(limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)

    def test_topic_live(self):
        out = json.loads(srv.dlf_news_by_topic("wirtschaft", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        self.assertEqual(out["topic"], "wirtschaft")

    def test_search_live(self):
        out = json.loads(srv.dlf_search_news("Klima", limit=3))
        self.assertNotIn("error", out)
        print(f"\nLIVE search 'Klima': {out['total_results']} hits")

    def test_get_article_live(self):
        out = json.loads(srv.dlf_get_article(
            "https://www.deutschlandfunk.de/klimawandel-overshoot-klimaziel-co2-entnahme-emissionen-100.html"))
        self.assertNotIn("error", out)
        self.assertTrue(out["title"])
        self.assertGreater(len(out["body"]), 500)
        print(f"\nLIVE article: {out['title'][:70]} — body {len(out['body'])} chars")

    def test_listen_live(self):
        out = json.loads(srv.dlf_listen_live())
        self.assertNotIn("error", out)
        self.assertEqual(out["status"], "live")
        self.assertIn(out["http_status"], (200, 301, 302))

    def test_health_live(self):
        out = json.loads(srv.dlf_health())
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["http_status"], 200)
