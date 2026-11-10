"""Domain logic: shape Deutschlandfunk RSS feeds + article-page JSON
blobs into compact dicts (stdlib only).

Data source: DLF's official RSS feeds
(https://www.deutschlandfunk.de/{feed}.rss) and deutschlandfunk.de
article pages — free, no key, no login.

DLF pages are JS-app shells: article text lives in embedded
`<script class="js-client-queries" data-json="...">` blobs as an
`Article` object (articleTitle / articleLeader / articleCopyText
with ParagraphText blocks). There is no JSON-LD and the visible
`<p>` tags are navigation/topic descriptions, not the article body.
The live stream URL comes from a `Stream` blob on DLF pages
("Deutschlandfunk Live"); it 302-redirects to a signed CDN URL,
so the tool reports the canonical URL plus its HEAD status.
"""
from __future__ import annotations

import html as _html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

BASE = "https://www.deutschlandfunk.de"

TOPICS = {
    "europa": "europa-112.rss",
    "gesellschaft": "gesellschaft-106.rss",
    "wirtschaft": "wirtschaft-106.rss",
    "wissen": "wissen-106.rss",
    "kultur": "kulturportal-100.rss",
    "sport": "sportportal-100.rss",
    "politik": "politikportal-100.rss",
}

NEWS_URL = f"{BASE}/nachrichten-100.rss"
BEITRAEGE_URL = f"{BASE}/neue-beitraege-dlf-100.rss"
AGENDA_URL = f"{BASE}/agenda-104.rss"
STREAM_URL = "https://st01.sslstream.dlf.de/dlf/01/128/mp3/stream.mp3"

_BLOB_RE = re.compile(r'<script class="js-client-queries" data-json="([^"]*)"', re.S)
_TAG_RE = re.compile(r'<[^>]+>')


def validate_topic(topic: str) -> str:
    key = (topic or "").strip().lower()
    if key not in TOPICS:
        raise ValueError(
            f"unsupported topic: {topic!r} "
            f"(use one of: {', '.join(sorted(TOPICS))})"
        )
    return key


def validate_limit(limit: int) -> int:
    if not 1 <= limit <= 50:
        raise ValueError(f"limit out of range: {limit} (expected 1..50)")
    return limit


def topic_url(topic: str) -> str:
    return f"{BASE}/{TOPICS[topic]}"


def _parse_xml(text: str, what: str) -> ET.Element:
    try:
        return ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f"invalid {what}: {e}") from e


def parse_feed(text: str) -> list[dict]:
    """[{title, url, published, description}] — feed order."""
    root = _parse_xml(text, "RSS feed")
    channel = root.find("channel")
    if channel is None:
        raise ValueError("invalid RSS feed: no channel element")
    out = []
    for item in channel.findall("item"):
        desc = (item.findtext("description") or "").strip()
        desc = _TAG_RE.sub("", _html.unescape(desc)).strip()
        out.append({
            "title": item.findtext("title") or "",
            "url": item.findtext("link") or item.findtext("guid") or "",
            "published": item.findtext("pubDate") or "",
            "description": desc[:300],
        })
    return out


def _blobs(html_text: str) -> list[dict]:
    out = []
    for raw in _BLOB_RE.findall(html_text):
        try:
            d = json.loads(_html.unescape(raw))
        except json.JSONDecodeError:
            continue
        v = d.get("value")
        if isinstance(v, dict):
            out.append(v)
    return out


def parse_article(html_text: str) -> dict:
    """Extract title/leader/date/body/audio from the Article blob."""
    title, leader, published, body, audio = "", "", "", "", ""
    for v in _blobs(html_text):
        if v.get("__typename") == "Article":
            title = v.get("articleTitle") or ""
            leader = v.get("articleLeader") or ""
            raw_date = v.get("articlePublicationDate") or ""
            try:
                published = datetime.fromtimestamp(
                    int(raw_date) / 1000, tz=timezone.utc).isoformat()
            except (ValueError, TypeError):
                published = str(raw_date)
            paras = []
            if leader:
                paras.append(leader)
            for block in v.get("articleCopyText") or []:
                if isinstance(block, dict) and block.get("__typename") == "ParagraphText":
                    txt = (block.get("content") or "").strip()
                    if txt:
                        paras.append(txt)
            body = "\n\n".join(paras)
        elif v.get("__typename") == "Audio" and not audio:
            audio = v.get("audioUrl") or v.get("downloadUrl") or ""
    return {"title": title, "published": published, "body": body,
            "audio_url": audio}


def parse_stream(html_text: str) -> dict:
    """Extract the live-stream title + URL from a Stream blob."""
    for v in _blobs(html_text):
        if v.get("__typename") == "Stream" and v.get("url"):
            return {"title": v.get("title") or "Deutschlandfunk Live",
                    "url": v["url"]}
    return {}
