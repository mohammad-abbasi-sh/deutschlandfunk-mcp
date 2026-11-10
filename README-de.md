# deutschlandfunk-mcp 📻

mcp-name: io.github.mohammad-abbasi-sh/deutschlandfunk-mcp

Inoffizieller **nur lesender** MCP-Server für **[deutschlandfunk.de](https://www.deutschlandfunk.de)** — Deutschlandfunk-Nachrichten & Radio über die offiziellen RSS-Feeds: laufende Nachrichten, neueste Beiträge, Ressort-Feeds, Stichwortsuche, Volltexte und Livestream-Link. Kein Schlüssel, kein Login. Kein Schlüssel, keine Anmeldung.

> Gebaut von Mohammad Abbasi als Teil der "Germany MCP factory". Nicht mit deutschlandfunk.de verbunden.

## Für KI-Agenten

Zur MCP-Client-Konfiguration hinzufügen (stdio):

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

Oder lokal starten: `python -m deutschlandfunk_mcp.server` (benötigt `mcp<2`, `httpx`).

## Tools

| Tool | Beschreibung |
|------|-------------|
| `dlf_latest_news` | Laufende DLF-Nachrichten |
| `dlf_latest_contributions` | Neueste DLF-Beiträge |
| `dlf_news_by_topic` | DLF-Nachrichten nach Ressort |
| `dlf_search_news` | Neueste DLF-Beiträge nach Stichwort suchen |
| `dlf_get_article` | Volltext eines DLF-Artikels |
| `dlf_listen_live` | Livestream-Link des Deutschlandfunks |
| `dlf_health` | Erreichbarkeitsprüfung (ok / blocked / error) — eine höfliche Anfrage |

## Entwicklung

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## Lizenz

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
