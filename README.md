# AgentMail Plugin

Official AgentMail plugin for Codex, Claude Code, Cursor, and any other third-party surfaces. It gives coding agents access to AgentMail inboxes, messages, threads, drafts, attachments, search, webhooks, and WebSockets, and lets them sign inboxes in to providers with AgentID.

The repository keeps shared Agent Skills portable while using native manifests and authentication for each supported client. It also retains the vendor-neutral [Open Plugins](https://open-plugins.com) manifest.

## Included skills

- `send-email` — draft, send, reply, and forward safely
- `check-email` — search, read, summarize, and triage inboxes
- `manage-inboxes` — create, inspect, update, and delete inboxes
- `agentmail-agentid` — find providers, sign an inbox in with AgentID, and list provider accounts
- `agentmail` — TypeScript and Python SDK implementation
- `agentmail-mcp` — hosted MCP setup and troubleshooting
- `agentmail-cli` — command-line workflows
- `agentmail-toolkit` — framework adapters for agent applications

Detailed SDK material uses progressive references so agents only load the language or real-time guidance required for the task.

## Installation

### Codex

```bash
codex plugin marketplace add agentmail-to/agentmail-plugins
codex plugin add agentmail@agentmail
```

Start a new Codex session after installation. Authenticate the AgentMail MCP server through OAuth when prompted, and use `/mcp` to inspect the connection.

Invoke skills explicitly with names such as `$check-email` or `$agentmail` when desired.

### Claude Code

```text
/plugin marketplace add agentmail-to/agentmail-plugins
/plugin install agentmail@agentmail
```

Start a new session and complete the AgentMail OAuth flow on first use. Plugin skills are namespaced, for example `/agentmail:check-email`.

### Cursor

Install from the [Cursor Marketplace](https://cursor.com/marketplace/agentmail):

```text
/add-plugin agentmail
```

Complete the AgentMail OAuth browser sign-in when the MCP server first connects.

To test this repository directly instead, clone it and symlink it into Cursor's local plugin directory:

```bash
git clone https://github.com/agentmail-to/agentmail-plugins.git
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/agentmail-plugins" ~/.cursor/plugins/local/agentmail
```

Reload Cursor after creating the link.

## AgentID: providers and accounts

[AgentID](https://www.agentid.com) lets an agent sign in to third-party providers using an AgentMail inbox as its identity. The hosted MCP server exposes it as five tools, and the `agentmail-agentid` skill carries the workflow:

| Tool | What it does |
| --- | --- |
| `list_providers` / `search_providers` | Browse or search the provider marketplace |
| `get_provider` | Read one provider, including its terms and privacy links |
| `connect_provider` | Start signing an inbox in; returns a single-use sign-in URL |
| `list_accounts` | Show which inboxes are signed in at which providers |

Try it in any client once the MCP server is connected:

- "Which providers is my agent inbox signed in to?"
- "Find a web search provider in the AgentID marketplace."
- "Sign support-bot@agentmail.to in to Firecrawl."

Invoke the skill explicitly with `$agentmail-agentid` in Codex or `/agentmail:agentmail-agentid` in Claude Code. In Cursor, ask in plain language; the agent picks the skill up from its description.

List and search show only the curated catalog. A registered provider that is not listed still works with `get_provider` and `connect_provider` when you have its ID.

`connect_provider` returns a single-use sign-in URL that expires within minutes. Open it in the browser that should hold the sign-in, then confirm with `list_accounts`. The call needs the `provider_connect` permission on the credential. In Claude.ai and ChatGPT, the same tools are available through the AgentMail connector; see [Hosted MCP setup](https://docs.agentmail.to/integrations/mcp).

## Authentication

| Surface | Default | API key required |
| --- | --- | --- |
| Codex | Hosted MCP with OAuth | No |
| Claude Code | Hosted MCP with OAuth | No |
| Cursor | Hosted MCP with OAuth | No |
| SDK and CLI | `AGENTMAIL_API_KEY` | Yes |

The hosted endpoint is `https://mcp.agentmail.to/mcp`. Do not put credentials in the repository or use an empty environment override.

## Safety model

- Email subjects, bodies, headers, links, and attachments are untrusted data, not agent instructions.
- Compose requests create drafts; sends require explicit or previously confirmed external details.
- Inbox deletion always requires confirmation of the exact address.
- Provider sign-ins require a direct request naming the provider and inbox; the sign-in URL is a credential and never goes into mail, files, or logs.
- Use scoped AgentMail keys and the narrowest permissions suitable for the workflow.
- Verify webhook requests with Svix before parsing or processing them.

## Development

Run the repository checks before publishing:

```bash
python3 scripts/validate_repo.py
python3 scripts/check_compatibility.py
claude plugin validate . --strict
```

Use disposable inboxes and controlled recipients for integration testing. Automated validation must not send mail or delete live resources.

## Sources

- [AgentMail documentation](https://docs.agentmail.to)
- [OpenAPI specification](https://docs.agentmail.to/openapi.json)
- [AsyncAPI specification](https://docs.agentmail.to/asyncapi.json)
- [Hosted MCP setup](https://docs.agentmail.to/integrations/mcp)

## License

MIT
