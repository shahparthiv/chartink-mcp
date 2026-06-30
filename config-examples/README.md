# Config Examples

Ready-to-use configuration templates. **Copy the one for your client and replace `/absolute/path/to/chartink-mcp/` with the real path on your machine.**

Find your absolute paths after installing (see the main [README](../README.md)):

```bash
cd chartink-mcp
echo "$(pwd)/venv/bin/python"   # → "command"
echo "$(pwd)/server.py"         # → "args"[0]
```

---

## `claude_desktop_config.json` — Claude Desktop

Merge the `mcpServers` block into your existing config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Then **restart Claude Desktop**.

## `.mcp.json` — Claude Code

Place in your project root (or merge into an existing `.mcp.json`).
Alternatively, register it via the CLI:

```bash
claude mcp add chartink -- /absolute/path/to/chartink-mcp/venv/bin/python /absolute/path/to/chartink-mcp/server.py
```

---

> **Windows paths:** use the venv launcher `venv\\Scripts\\python.exe` and escape backslashes in JSON, e.g.
> `"command": "C:\\Users\\you\\chartink-mcp\\venv\\Scripts\\python.exe"`.

After configuring, **authenticate once** by setting your Chartink cookies — see the [main README → Authentication](../README.md#authentication-one-time-per-session).
