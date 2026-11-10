# deutschlandfunk-mcp 📻

mcp-name: io.github.mohammad-abbasi-sh/deutschlandfunk-mcp

Unofficial **read-only** MCP server for **[deutschlandfunk.de](https://www.deutschlandfunk.de)** — Deutschlandfunk news & radio from its official RSS feeds: rolling news, latest contributions, topic feeds, keyword search, full article text and the live stream link. No key, no login. No key, no login.

> Built by Mohammad Abbasi as part of the "Germany MCP factory". Not affiliated with deutschlandfunk.de.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "deutschlandfunk": {
      "command": "uvx",
      "args": ["deutschlandfunk-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m deutschlandfunk_mcp.server` (needs `mcp<2`, `httpx`).

## Tools

| Tool | Description |
|------|-------------|
| `dlf_latest_news` | Rolling DLF news headlines — `limit` 1..50 |
| `dlf_latest_contributions` | Latest DLF contributions (articles & audio features) — `limit` 1..50 |
| `dlf_news_by_topic` | DLF news by topic — `topic` (europa/gesellschaft/wirtschaft/wissen/kultur/sport/politik), `limit` 1..50 |
| `dlf_search_news` | Keyword search over recent DLF items — `query`, `limit` 1..50 |
| `dlf_get_article` | Full text of one DLF article — `url` (a deutschlandfunk.de article link) |
| `dlf_listen_live` | Deutschlandfunk live stream link (verified reachable) — no arguments |
| `dlf_health` | Reachability probe (ok / blocked / error) — one polite request |

## Notes

- All data comes from **Deutschlandfunk's official RSS feeds** (free, no key, no login).
- DLF pages are JS-app shells: article text is extracted from embedded `js-client-queries` JSON blobs (`Article` with `ParagraphText` blocks) — there is no JSON-LD and the visible `<p>` tags are navigation/topic descriptions, not the article body.
- The live stream URL 302-redirects to a signed CDN URL; `dlf_listen_live` reports the canonical URL plus its HEAD reachability.
- Podcast show listing is not a tool: the podcasts page's `pathPodcast` fields are section navigation links, not per-show feeds (show feeds exist per show as `<slug>-100.rss` but are not reliably enumerable from the page).

Tests: 23/23 green (16 offline + 7 live, 2026-11-10).

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
