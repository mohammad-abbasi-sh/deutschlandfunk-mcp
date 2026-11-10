"""MCP server: unofficial read-only access to Deutschlandfunk news
and radio via its official RSS feeds + article pages. No key, no
login. NOTE: DLF pages are JS-app shells — article text is extracted
from embedded JSON blobs, not from visible <p> tags (those are
navigation); the live stream URL 302-redirects to a signed CDN URL,
so the tool reports the canonical URL plus its reachability."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import domain as _dom
from . import http as _http

INSTRUCTIONS = """\
Unofficial read-only MCP server for Deutschlandfunk via its \
official RSS feeds (no key, no login): rolling news, latest \
contributions, news by topic, keyword search over recent items, \
full article text and the live stream link. NOTE: DLF article pages \
are JS-app shells — text is extracted from embedded JSON blobs, not \
from visible paragraphs; the live stream URL redirects (302) to a \
signed CDN URL, so the tool reports the canonical URL plus its \
reachability. Built by Mohammad Abbasi (mohammad-abbasi-sh) — \
https://almanibama.ir · https://mabbasi.ir — Germany MCP factory.\
"""

_SOURCE = "deutschlandfunk.de"
_DISCLAIMER = "Unofficial read-only data from deutschlandfunk.de RSS feeds and article pages; verify on the site before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


mcp = FastMCP("deutschlandfunk-mcp", instructions=INSTRUCTIONS)


def _feed(url: str, limit: int, extra: dict | None = None) -> str:
    lim = _dom.validate_limit(limit)
    items = _dom.parse_feed(_http.fetch_text(url))
    payload = {"total_results": len(items),
               "count": min(lim, len(items)), "items": items[:lim]}
    if extra:
        payload.update(extra)
    return _ok(payload)


@mcp.tool()
def dlf_latest_news(limit: int = 10) -> str:
    """Rolling Deutschlandfunk news headlines. limit: 1..50 (default 10)."""
    try:
        return _feed(_dom.NEWS_URL, limit)
    except (_http.DeutschlandfunkMcpError, ValueError) as e:
        return _err(e)


@mcp.tool()
def dlf_latest_contributions(limit: int = 10) -> str:
    """Latest Deutschlandfunk contributions (articles & audio features).
    limit: 1..50 (default 10)."""
    try:
        return _feed(_dom.BEITRAEGE_URL, limit)
    except (_http.DeutschlandfunkMcpError, ValueError) as e:
        return _err(e)


@mcp.tool()
def dlf_news_by_topic(topic: str, limit: int = 10) -> str:
    """Deutschlandfunk news by topic. topic: europa, gesellschaft,
    wirtschaft, wissen, kultur, sport or politik.
    limit: 1..50 (default 10)."""
    try:
        t = _dom.validate_topic(topic)
        return _feed(_dom.topic_url(t), limit, {"topic": t})
    except (_http.DeutschlandfunkMcpError, ValueError) as e:
        return _err(e)


@mcp.tool()
def dlf_search_news(query: str, limit: int = 10) -> str:
    """Keyword search over recent Deutschlandfunk items (the Agenda
    feed, several hundred latest items — not a full-archive search).
    query: keyword or phrase. limit: 1..50 (default 10)."""
    try:
        lim = _dom.validate_limit(limit)
        q = (query or "").strip()
        if not q:
            raise ValueError("query must not be empty")
        items = _dom.parse_feed(_http.fetch_text(_dom.AGENDA_URL))
        ql = q.casefold()
        hits = [i for i in items
                if ql in i["title"].casefold()
                or ql in i["description"].casefold()]
    except (_http.DeutschlandfunkMcpError, ValueError) as e:
        return _err(e)
    return _ok({"query": q, "searched": "recent items in the DLF Agenda feed",
                "total_results": len(hits),
                "count": min(lim, len(hits)), "items": hits[:lim]})


@mcp.tool()
def dlf_get_article(url: str) -> str:
    """Full text of one Deutschlandfunk article. url: a
    deutschlandfunk.de article link, e.g.
    https://www.deutschlandfunk.de/klimawandel-...-100.html
    (news-flash pages may return only the leader text)."""
    try:
        u = (url or "").strip()
        if not u.startswith("https://www.deutschlandfunk.de/"):
            raise ValueError("url must be a deutschlandfunk.de article link "
                             "(https://www.deutschlandfunk.de/...)")
        out = _dom.parse_article(_http.fetch_text(u))
        if not out["title"] and not out["body"]:
            raise ValueError("no article content found at that URL "
                             "(it may be a topic, programme or podcast page)")
    except (_http.DeutschlandfunkMcpError, ValueError) as e:
        return _err(e)
    return _ok({"url": u, "title": out["title"],
                "published": out["published"],
                "audio_url": out["audio_url"],
                "body": out["body"][:6000]})


@mcp.tool()
def dlf_listen_live() -> str:
    """Deutschlandfunk live stream link. Checks the canonical stream
    URL (from DLF's own pages) with a HEAD request and reports
    whether it answers; the URL itself 302-redirects to a signed CDN
    stream — open it in any audio player."""
    try:
        probe = _http.head_status(_dom.STREAM_URL)
        status = "live" if probe in (200, 301, 302) else "unreachable"
    except _http.DeutschlandfunkMcpError as e:
        return _err(e)
    return _ok({"station": "Deutschlandfunk Live",
                "stream_url": _dom.STREAM_URL,
                "http_status": probe, "status": status,
                "note": "The stream URL redirects (302) to a signed CDN URL; "
                        "open it in an audio player."})


@mcp.tool()
def dlf_health() -> str:
    """Check whether deutschlandfunk.de is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    sys.exit(main())
