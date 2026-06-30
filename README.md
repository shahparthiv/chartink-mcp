# Chartink MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that lets Claude — or any MCP-compatible AI agent — run **[Chartink](https://chartink.com) stock screeners and backtests** for the Indian (NSE/BSE) market directly from a chat.

You describe a strategy in plain English, the agent writes the Chartink **scan clause**, and this server runs it against Chartink and returns the matching stocks.

> Bundled with a **`chartink-query` skill** (see [`skills/`](skills/)) that teaches the agent the full Chartink scan-clause syntax — every indicator, function, and gotcha — so it writes correct queries on the first try.

---

## Features

| Tool | What it does |
|------|--------------|
| `set_cookies` | Authenticate using your Chartink browser session cookies. |
| `run_screener` | Run a scan clause and return matching stocks (`/screener/process`). |
| `run_multiple_screeners` | Run several scan clauses in one call (compare strategies). |
| `run_backtest` | Run a scan clause through Chartink's `/backtest/process` endpoint. |
| `run_saved_screener` | Fetch a public saved screener by its URL slug and run it. |

---

## Requirements

- **Python 3.10+** (developed on 3.11)
- A **Chartink account** (free works for most scans; some features need premium)
- An MCP-compatible client: **Claude Desktop**, **Claude Code**, or any agent that speaks MCP over stdio

---

## Installation

```bash
# 1. Clone
git clone https://github.com/<your-username>/chartink-mcp.git
cd chartink-mcp

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

Dependencies (`requirements.txt`): `mcp`, `requests`, `beautifulsoup4`.

Note the **absolute path** to the venv's Python and to `server.py` — you'll need them for the client config:

```bash
echo "$(pwd)/venv/bin/python"   # → command
echo "$(pwd)/server.py"         # → args[0]
```

---

## Configuration

The server runs over **stdio**. Point your MCP client at the venv Python + `server.py`. Ready-to-edit templates live in [`config-examples/`](config-examples/).

### Claude Desktop

Edit the config file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chartink": {
      "command": "/absolute/path/to/chartink-mcp/venv/bin/python",
      "args": ["/absolute/path/to/chartink-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop. You should see the `chartink` tools appear.

### Claude Code

Create (or edit) `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "chartink": {
      "command": "/absolute/path/to/chartink-mcp/venv/bin/python",
      "args": ["/absolute/path/to/chartink-mcp/server.py"]
    }
  }
}
```

Or add it via the CLI:

```bash
claude mcp add chartink -- /absolute/path/to/chartink-mcp/venv/bin/python /absolute/path/to/chartink-mcp/server.py
```

### Any other MCP client

Use the generic stdio form — run the command below and speak MCP to its stdin/stdout:

```
/absolute/path/to/chartink-mcp/venv/bin/python /absolute/path/to/chartink-mcp/server.py
```

---

## Authentication (one-time per session)

Chartink's scan endpoints need a valid session, so you pass it your browser cookies once.

1. Log in to **[chartink.com](https://chartink.com)** in Chrome.
2. Open **DevTools → Network** tab.
3. Click any request to `chartink.com`, go to **Headers → Request Headers**, and copy the **entire `Cookie:` value** (it contains `XSRF-TOKEN=...; ci_session=...; ...`).
4. In your AI chat, tell the agent to set the cookies, e.g.:

   > "Set my Chartink cookies: `XSRF-TOKEN=...; ci_session=...; ...`"

   (This calls `set_cookies`.) You'll get back **"XSRF-TOKEN found ✓"** if it worked.

Cookies live for the duration of the server process. Re-run `set_cookies` if requests start failing (session expired).

> ⚠️ **Never commit your cookies.** They are credentials. The `.gitignore` already excludes common secret/cache files, but treat the cookie string like a password.

---

## Usage examples

Once configured and authenticated, just talk to the agent:

> "Find NSE stocks within 5% of their 52-week high with rising volume."

> "Run this scan clause and show me the matches:
> `( {cash} ( latest rsi( 14 ) > 60 and latest close > latest sma( latest close , 50 ) ) )`"

> "Run the saved screener `short-term-breakouts`."

> "Compare two strategies: an RSI breakout vs a MACD crossover."

The agent writes the scan clause (using the bundled skill), the server runs it, and you get the stock list back.

### Scan-clause shape (quick primer)

```
( {cash} ( <condition> [and|or <condition>] ... ) )
```

`{cash}` = all NSE cash stocks. Conditions use Chartink's English-like grammar, e.g.
`latest close > latest sma( latest close , 50 )`. See the bundled **skill** for the full syntax.

---

## The `chartink-query` skill

The [`skills/chartink-query/`](skills/chartink-query/) folder is a portable **Claude skill** that documents the entire Chartink scan-clause language — price/volume attributes, timeframes & candle offsets, every indicator (SMA, EMA, RSI, MACD, ADX, Bollinger, Stochastic, Supertrend, Donchian, VWAP, OBV, pivots…), functions (`max`/`min`/`count`/`abs`), crossover construction, segments, and the supported fundamental fields — plus a library of ready-to-use example queries.

With the skill installed, the agent writes **valid scan clauses on the first try** and can produce both the MCP/API form and the copy-paste form for chartink.com.

### Install the skill

**Claude Code** — copy it into either location:

```bash
# user-level (available in every project)
cp -r skills/chartink-query ~/.claude/skills/

# or project-level
mkdir -p .claude/skills && cp -r skills/chartink-query .claude/skills/
```

**Claude Desktop / other agents** — point your skills directory at `skills/chartink-query/`, or paste the contents of `SKILL.md` into your system prompt / project knowledge.

Then just ask: *"write a chartink query for stocks breaking a 20-day high with a volume surge"* and the skill handles the syntax.

---

## Project structure

```
chartink-mcp/
├── server.py                     # the MCP server
├── requirements.txt
├── README.md
├── LICENSE
└── skills/
    └── chartink-query/           # portable Claude skill for Chartink syntax
        ├── SKILL.md
        ├── reference.md          # full keyword/indicator/function catalog
        └── examples.md           # ready-to-use query patterns
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tools don't appear in the client | Check the absolute paths in the config; restart the client. |
| `XSRF-TOKEN not found` / `are you logged in?` | Re-run `set_cookies` with a fresh cookie string from a logged-in browser. |
| Requests suddenly fail | Session expired — set cookies again. |
| `run_saved_screener` says "Could not extract scan_clause" | That scan is **private** (its clause isn't in the public page). Ask the owner for the clause and use `run_screener` instead. |
| `run_backtest` returns empty | Chartink's full target/stop backtest is a website/premium feature; the endpoint may not return rich data via API. Use the website's Backtest tab for performance stats. |

---

## Disclaimer

This project is for **educational and research purposes only**. It is **not investment advice**, and the authors are not SEBI-registered advisers. Screener output and any backtests are **not** recommendations to buy or sell. Always do your own due diligence and manage your own risk. Use in accordance with Chartink's terms of service.

---

## Contributing

Issues and PRs welcome. Ideas: caching, richer backtest parsing, more example skills, tests.

## License

[MIT](LICENSE)
