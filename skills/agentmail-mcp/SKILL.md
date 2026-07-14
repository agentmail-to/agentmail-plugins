---
name: agentmail-mcp
description: Configure or troubleshoot the hosted AgentMail MCP server for Codex, Claude Code, Cursor, or another Streamable HTTP MCP client. Use for installation, OAuth, API-key headers, connection failures, or MCP tool discovery; do not use for SDK code or direct email operations.
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

Complete the browser sign-in on first connection. Multi-organization OAuth sessions can use the server’s organization-selection tools.

## Clients without OAuth

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

## Verify

1. Restart the client or open a new session after installing the plugin.
2. Inspect MCP status in the client and complete authentication.
3. Call `list_inboxes` as a read-only smoke test.
4. Confirm that read, write, and destructive tool annotations produce the expected approval behavior.

The hosted server covers core inbox, message, thread, search, draft, attachment, and identity operations. Discover the live tool inventory from the MCP server instead of relying on a copied tool count.

## Troubleshoot

- A 404 usually means the URL is missing `/mcp`.
- A 401 with OAuth usually means the sign-in is incomplete or the session expired.
- A 401 with API-key auth usually means `AGENTMAIL_API_KEY` was not available to the client process or the key was revoked.
- Use the full `am_` key value and prefer the narrowest suitable organization, pod, or inbox scope.
- For a stdio-only client, use the supported npm or PyPI `agentmail-mcp` compatibility bridge. Both discover tools dynamically from the hosted server.
