# deutschlandfunk-mcp 📻

mcp-name: io.github.mohammad-abbasi-sh/deutschlandfunk-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **[deutschlandfunk.de](https://www.deutschlandfunk.de)** — اخبار و رادیوی دویچلندفونک از فیدهای RSS رسمی: اخبار جاری، تازه‌ترین مطالب، فیدهای موضوعی، جست‌وجوی کلیدواژه، متن کامل مقاله و لینک پخش زنده. بدون کلید، بدون ورود. بدون کلید، بدون ورود.

> ساختهٔ محمد عباسی، بخشی از «کارخانهٔ MCP آلمان». وابسته به deutschlandfunk.de نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP کلاینت اضافه کنید (stdio):

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

یا به‌صورت محلی اجرا کنید: `python -m deutschlandfunk_mcp.server` (نیازمند `mcp<2` و `httpx`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `dlf_latest_news` | تیترهای خبری جاری DLF |
| `dlf_latest_contributions` | تازه‌ترین مطالب DLF |
| `dlf_news_by_topic` | اخبار DLF بر اساس موضوع |
| `dlf_search_news` | جست‌وجوی مطالب اخیر DLF با کلیدواژه |
| `dlf_get_article` | متن کامل یک مقالهٔ DLF |
| `dlf_listen_live` | لینک پخش زندهٔ دویچلندفونک |
| `dlf_health` | بررسی دسترس‌پذیری (ok / blocked / error) — یک درخواست مؤدبانه |

## توسعه

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## لایسنس

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
