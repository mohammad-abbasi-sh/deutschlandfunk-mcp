"""Offline tests — parse real captured DLF RSS feeds + a structural article
fixture, no network."""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from deutschlandfunk_mcp import domain as dom
from deutschlandfunk_mcp import server as srv

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


class TestTopics(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(dom.validate_topic("wirtschaft"), "wirtschaft")
        self.assertEqual(dom.validate_topic("Kultur"), "kultur")
        self.assertEqual(dom.topic_url("politik"),
                         "https://www.deutschlandfunk.de/politikportal-100.rss")

    def test_invalid(self):
        for bad in ["", "news", "politik-100", "sport-100"]:
            with self.assertRaises(ValueError, msg=bad):
                dom.validate_topic(bad)

    def test_limit(self):
        self.assertEqual(dom.validate_limit(10), 10)
        with self.assertRaises(ValueError):
            dom.validate_limit(0)
        with self.assertRaises(ValueError):
            dom.validate_limit(51)


class TestFixtures(unittest.TestCase):
    def test_feed_nachrichten(self):
        items = dom.parse_feed(_read("feed-nachrichten.xml"))
        self.assertEqual(len(items), 41)
        self.assertTrue(all(i["title"] and i["url"] and i["published"] for i in items))

    def test_feed_beitraege(self):
        items = dom.parse_feed(_read("feed-beitraege.xml"))
        self.assertEqual(len(items), 92)

    def test_feed_agenda(self):
        items = dom.parse_feed(_read("feed-agenda.xml"))
        self.assertEqual(len(items), 50)

    def test_feed_wirtschaft(self):
        items = dom.parse_feed(_read("feed-wirtschaft.xml"))
        self.assertEqual(len(items), 30)

    def test_article_fixture(self):
        out = dom.parse_article(_read("article-de.html"))
        self.assertEqual(out["title"], "Testbeitrag über Deutschland")
        self.assertTrue(out["body"].startswith(
            "Die Einleitung des Testbeitrags fasst das Thema"))
        self.assertIn("erste Absatz", out["body"])
        self.assertIn("zweite Absatz", out["body"])
        self.assertNotIn("Listenpunkt", out["body"])
        self.assertNotIn("Themen Die Nachrichten", out["body"])
        self.assertEqual(out["audio_url"],
                         "https://ondemand-mp3.dradio.de/file/dradio/2026/11/10/testbeitrag.mp3")
        self.assertTrue(out["published"].startswith("2026-11-09"))

    def test_stream_fixture(self):
        out = dom.parse_stream(_read("article-de.html"))
        self.assertEqual(out["title"], "Deutschlandfunk Live")
        self.assertTrue(out["url"].startswith("https://st01.sslstream.dlf.de/"))

    def test_bad_feed(self):
        with self.assertRaises(ValueError):
            dom.parse_feed("<rss><unclosed")


class TestServerOffline(unittest.TestCase):
    def test_news_mock(self):
        with mock.patch("deutschlandfunk_mcp.http.fetch_text",
                        return_value=_read("feed-nachrichten.xml")):
            out = json.loads(srv.dlf_latest_news(limit=3))
        self.assertEqual(out["total_results"], 41)
        self.assertEqual(out["count"], 3)
        self.assertIn("fetched_at", out)
        self.assertEqual(out["source"], "deutschlandfunk.de")

    def test_search_mock(self):
        with mock.patch("deutschlandfunk_mcp.http.fetch_text",
                        return_value=_read("feed-agenda.xml")):
            out = json.loads(srv.dlf_search_news("Trump", limit=5))
        self.assertGreaterEqual(out["total_results"], 1)
        self.assertTrue(all("trump" in (i["title"] + i["description"]).casefold()
                            for i in out["items"]))

    def test_bad_topic(self):
        out = json.loads(srv.dlf_news_by_topic("news", limit=3))
        self.assertIn("error", out)

    def test_get_article_mock(self):
        with mock.patch("deutschlandfunk_mcp.http.fetch_text",
                        return_value=_read("article-de.html")):
            out = json.loads(srv.dlf_get_article(
                "https://www.deutschlandfunk.de/testbeitrag-100.html"))
        self.assertEqual(out["title"], "Testbeitrag über Deutschland")
        self.assertIn("zweite Absatz", out["body"])

    def test_get_article_bad_url(self):
        out = json.loads(srv.dlf_get_article("https://example.com/x"))
        self.assertIn("error", out)

    def test_listen_live_mock(self):
        with mock.patch("deutschlandfunk_mcp.http.head_status",
                        return_value=302):
            out = json.loads(srv.dlf_listen_live())
        self.assertEqual(out["status"], "live")
        self.assertEqual(out["http_status"], 302)
        self.assertTrue(out["stream_url"].startswith("https://st01.sslstream.dlf.de/"))


if __name__ == "__main__":
    unittest.main()
