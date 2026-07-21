---
name: agentmail-mcp
description: Configure or troubleshoot the hosted AgentMail MCP server for Codex, Claude Code, Cursor, or another Streamable HTTP MCP client. Use for installation, OAuth, API-key headers, connection failures, or MCP tool discovery. Do not use when the connection already works and the user just wants to send, check, or manage mail — use the sibling action skills for that.
---

# AgentMail MCP

Prefer the hosted Streamable HTTP server:

```text
https://mcp.agentmail.to/mcp
```

It avoids a local Node.js process and the slower release cadence of the published local MCP package.

## Claude Code, Codex, and Cursor

Use OAuth. Do not put an empty API key in the configuration.

```json
{
  "mcpServers": {
    "agentmail": {
      "type": "http",
      "url": "https://mcp.agentmail.to/mcp"
    }
  }
}
```

Claude Code can also install it directly:

```bash
claude mcp add --transport http agentmail https://mcp.agentmail.to/mcp
```

Complete the browser sign-in on first connection. Multi-organization OAuth sessions can use the server's organization-selection tools.

## Per-client configuration

Add the same `type: http` server entry to the client's MCP config file:

- Cursor: `.cursor/mcp.json`
- VS Code: `.vscode/mcp.json`
- Windsurf: its MCP config file
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows)

## Auth options

- **OAuth** — browser-based sign-in, for clients that support remote MCP OAuth. Use the bare URL with no credentials.
- **`x-api-key` header** — recommended for clients without OAuth support (see below).
- **`Authorization: Bearer <am_...>` header** — an alternative header form some clients require.
- **`apiKey` query param** — supported but not recommended; prefer a header so the key doesn't end up in logs or history.

For a Streamable HTTP client that cannot complete OAuth, export `AGENTMAIL_API_KEY` and send it as a header:

```json
{
  "mcpServers": {
    "agentmail": {
      "type": "http",
      "url": "https://mcp.agentmail.to/mcp",
      "headers": {
        "x-api-key": "${env:AGENTMAIL_API_KEY}"
      }
    }
  }
}
```

Avoid query-string credentials when header authentication is available.

## Tool Discovery

MCP clients get the tool catalog and schemas live from the hosted runtime; do not rely on a copied tool count. The same generated contract is published at `https://github.com/agentmail-to/agentmail-mcp/blob/main/mcp-manifest.json` — treat the hosted runtime plus that manifest as the authoritative catalog. OAuth sessions can surface extra organization-selection tools beyond the base set.

## Stdio Compatibility

For a stdio-only client, use the supported npm or PyPI `agentmail-mcp` package. Both are thin stdio bridges to the same hosted runtime: they discover tools dynamically and carry no separate AgentMail tool logic of their own.

## Verify

1. Restart the client or open a new session after installing the plugin.
2. Inspect MCP status in the client and complete authentication.
3. Call `list_inboxes` as a read-only smoke test.
4. Confirm that read, write, and destructive tool annotations produce the expected approval behavior.

## Troubleshoot

- A 404 usually means the URL is missing `/mcp`.
- "Invalid API key" or a 401 with API-key auth usually means the key is wrong, revoked, lacks the necessary permissions, or `AGENTMAIL_API_KEY` was not available to the client process.
- "Unauthorized" or a 401 with OAuth usually means the sign-in is incomplete or the session expired — drop any `apiKey` query param and let the client complete the browser-based OAuth flow instead.
- Use the full `am_` key value and prefer the narrowest suitable organization, pod, or inbox scope.
- For a stdio-only client, see Stdio Compatibility above.
