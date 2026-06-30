#!/usr/bin/env python3
"""
Chartink MCP Server
Uses browser session cookies to run screeners on Chartink.
"""

import json
from typing import Any
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

BASE_URL = "https://chartink.com"
SCREENER_PROCESS = f"{BASE_URL}/screener/process"
BACKTEST_PROCESS = f"{BASE_URL}/backtest/process"

app = Server("chartink")

_session = requests.Session()
_session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
})


def _get_xsrf_token() -> str:
    """Return the XSRF-TOKEN cookie value (URL-decoded). Refreshes from the
    screener page if not present in the session."""
    token = _session.cookies.get("XSRF-TOKEN", domain="chartink.com")
    if token:
        return unquote(token)
    # Refresh by hitting any chartink page
    resp = _session.get(f"{BASE_URL}/screeners/", timeout=15)
    resp.raise_for_status()
    token = _session.cookies.get("XSRF-TOKEN", domain="chartink.com")
    if not token:
        raise RuntimeError("XSRF-TOKEN not found — are you logged in?")
    return unquote(token)


def _post_screener(scan_clause: str, max_rows: int = 160, referer: str = f"{BASE_URL}/screeners/") -> dict:
    xsrf = _get_xsrf_token()
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "x-xsrf-token": xsrf,
        "referer": referer,
        "origin": BASE_URL,
    }
    resp = _session.post(
        SCREENER_PROCESS,
        data={"max_rows": max_rows, "scan_clause": scan_clause},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _post_backtest(scan_clause: str, max_rows: int = 160, referer: str = f"{BASE_URL}/screeners/") -> dict:
    xsrf = _get_xsrf_token()
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "x-xsrf-token": xsrf,
        "referer": referer,
        "origin": BASE_URL,
    }
    resp = _session.post(
        BACKTEST_PROCESS,
        data={"max_rows": max_rows, "scan_clause": scan_clause},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="set_cookies",
            description=(
                "Set your Chartink browser session cookies so the server can make "
                "authenticated requests. Paste the raw Cookie header string from "
                "Chrome DevTools → Network → any chartink.com request → Headers → Cookie."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cookie_string": {
                        "type": "string",
                        "description": "Raw Cookie header, e.g. 'XSRF-TOKEN=abc; ci_session=xyz; ...'",
                    }
                },
                "required": ["cookie_string"],
            },
        ),
        Tool(
            name="run_screener",
            description=(
                "Run a Chartink screener scan clause and return matching stocks. "
                "Uses the /screener/process endpoint. "
                "Requires cookies to be set first via set_cookies."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scan_clause": {
                        "type": "string",
                        "description": "Chartink scan condition string",
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "Max results to return (default 160)",
                        "default": 160,
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional label for this screener",
                    },
                },
                "required": ["scan_clause"],
            },
        ),
        Tool(
            name="run_multiple_screeners",
            description=(
                "Run multiple Chartink scan clauses in one call and return combined results. "
                "Each screener runs independently. Useful for comparing multiple strategies."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "screeners": {
                        "type": "array",
                        "description": "List of screeners to run",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Label for this screener"},
                                "scan_clause": {"type": "string", "description": "Chartink scan condition"},
                                "max_rows": {"type": "integer", "default": 160},
                            },
                            "required": ["name", "scan_clause"],
                        },
                    }
                },
                "required": ["screeners"],
            },
        ),
        Tool(
            name="run_backtest",
            description=(
                "Run a Chartink backtest scan clause using the /backtest/process endpoint. "
                "Requires cookies to be set first via set_cookies."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scan_clause": {
                        "type": "string",
                        "description": "Chartink scan condition string",
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "Max results to return (default 160)",
                        "default": 160,
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional label for this backtest",
                    },
                },
                "required": ["scan_clause"],
            },
        ),
        Tool(
            name="run_saved_screener",
            description=(
                "Fetch and run a saved Chartink screener by its URL slug "
                "(the part after /screener/ in the URL, e.g. 'short-term-breakouts'). "
                "Extracts the scan clause from the page and runs it."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Screener slug from chartink.com/screener/<slug>",
                    },
                    "max_rows": {
                        "type": "integer",
                        "default": 160,
                    },
                },
                "required": ["slug"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:

    if name == "set_cookies":
        cookie_string = arguments["cookie_string"]
        _session.cookies.clear()
        for part in cookie_string.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                _session.cookies.set(k.strip(), v.strip(), domain="chartink.com")
        token = _session.cookies.get("XSRF-TOKEN", domain="chartink.com")
        status = "XSRF-TOKEN found ✓" if token else "Warning: XSRF-TOKEN not in cookies"
        return [TextContent(type="text", text=f"Cookies set. {status}")]

    elif name == "run_screener":
        scan_clause = arguments["scan_clause"]
        max_rows = arguments.get("max_rows", 160)
        label = arguments.get("name", "Screener")
        try:
            data = _post_screener(scan_clause, max_rows)
            stocks = data.get("data", [])
            result = {"screener": label, "count": len(stocks),
                      "returned": min(len(stocks), max_rows), "stocks": stocks[:max_rows]}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "run_multiple_screeners":
        screeners = arguments["screeners"]
        results = []
        for s in screeners:
            mr = s.get("max_rows", 160)
            try:
                data = _post_screener(s["scan_clause"], mr)
                stocks = data.get("data", [])
                results.append({"screener": s["name"], "count": len(stocks),
                                "returned": min(len(stocks), mr), "stocks": stocks[:mr]})
            except Exception as e:
                results.append({"screener": s["name"], "error": str(e)})
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    elif name == "run_backtest":
        scan_clause = arguments["scan_clause"]
        max_rows = arguments.get("max_rows", 160)
        label = arguments.get("name", "Backtest")
        try:
            data = _post_backtest(scan_clause, max_rows)
            stocks = data.get("data", [])
            result = {"backtest": label, "count": len(stocks),
                      "returned": min(len(stocks), max_rows), "stocks": stocks[:max_rows]}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "run_saved_screener":
        slug = arguments["slug"]
        max_rows = arguments.get("max_rows", 160)
        try:
            url = f"{BASE_URL}/screener/{slug}"
            resp = _session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            clause_tag = (
                soup.find("input", {"name": "scan_clause"}) or
                soup.find("textarea", {"name": "scan_clause"})
            )
            if not clause_tag:
                return [TextContent(type="text", text=f"Could not extract scan_clause from {url}.")]
            scan_clause = (clause_tag.get("value") or clause_tag.string or "").strip()
            data = _post_screener(scan_clause, max_rows, referer=url)
            stocks = data.get("data", [])
            result = {"screener": slug, "scan_clause": scan_clause, "count": len(stocks),
                      "returned": min(len(stocks), max_rows), "stocks": stocks[:max_rows]}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
