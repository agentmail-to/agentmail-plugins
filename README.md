# AgentMail Plugin

Official AgentMail plugin for Codex, Claude Code, Cursor, and any other third-party surfaces. It gives coding agents access to AgentMail inboxes, messages, threads, drafts, attachments, search, webhooks, and WebSockets, and lets them sign inboxes in to apps with AgentID.

The repository keeps shared Agent Skills portable while using native manifests and authentication for each supported client. It also retains the vendor-neutral [Open Plugins](https://open-plugins.com) manifest.

## Included skills

- `send-email` — draft, send, reply, and forward safely
- `check-email` — search, read, summarize, and triage inboxes
- `manage-inboxes` — create, inspect, update, and delete inboxes
- `agentid` — create accounts for your agent at apps like Firecrawl with AgentID, and list where it has accounts
- `agentmail` — TypeScript and Python SDK implementation
- `agentmail-mcp` — hosted MCP setup and troubleshooting
- `agentmail-cli` — command-line workflows
- `agentmail-toolkit` — framework adapters for agent applications
- `agent-email-patterns` — agent email architecture, security, and provider tradeoffs

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

To test this repository directly instead, clone it into Cursor's local plugin
directory:

```bash
mkdir -p ~/.cursor/plugins/local
git clone https://github.com/agentmail-to/agentmail-plugins.git ~/.cursor/plugins/local/agentmail
```

Reload Cursor after cloning. Cursor only follows local-plugin symlinks whose
targets also resolve inside `~/.cursor/plugins/local`, so a symlink to a checkout
elsewhere is not a supported test setup.

## Updating an existing installation

Plugin releases use one synchronized version across all package manifests. After
an update is published, refresh the source and load the new plugin in a new
session:

### Codex

```bash
codex plugin marketplace upgrade agentmail
```

### Claude Code

```bash
claude plugin update agentmail@agentmail
```

Run `/reload-plugins` in an existing Claude Code session, or start a new one.
Third-party Claude marketplaces do not enable automatic updates by default.

### Cursor

Update AgentMail from the Cursor Marketplace after the new revision has passed
Cursor's review, then start a new chat. Public Cursor plugin updates are reviewed
before publication, so a repository release can precede marketplace availability.

## AgentID: create accounts for your agent

[AgentID](https://www.agentid.com) lets your agent create an account at a third-party service, such as a scraping, search, or database API, using an AgentMail inbox as its identity. No password or sign-up form: the inbox address is the account's email, and the app's mail lands in that inbox.

Ask in plain language once the MCP server is connected:

- "Create an account at Firecrawl for my agent."
- "My agent needs a web search API. Set one up."
- "Log my agent back in to Turso."
- "Which services is support-bot@agentmail.to signed up for?"

The `agentid` skill carries the whole job. It finds the app, picks the inbox that will own the account (creating one if needed), and checks for an existing account and the app's sign-up cap. Then it hands you a single-use sign-in link and confirms the account exists. Finally it helps you get what you came for, usually an API key stored in your secret store. Invoke it explicitly with `$agentid` in Codex or `/agentmail:agentid` in Claude Code; in Cursor, just ask.

| Tool | What it does |
| --- | --- |
| `search_apps` | Find an app by name |
| `list_apps` | Browse the marketplace; used to match a need such as "web search" to an app |
| `get_app` | Read one app, including its terms, privacy links, and sign-up cap |
| `connect_app` | Create an account, or sign an existing one back in; returns a single-use sign-in link |
| `list_accounts` | Show which inboxes have accounts at which apps |

List and search show only the curated catalog. A registered app that is not listed still works with `get_app` and `connect_app` when you have its ID. The sign-in link expires within minutes and needs the `app_connect` permission on the credential. In Claude.ai and ChatGPT, the same tools come through the AgentMail connector; see [Hosted MCP setup](https://docs.agentmail.to/integrations/mcp).

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
- App sign-ins require a direct request naming the app and inbox; the sign-in URL is a credential and never goes into mail, files, or logs.
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

The complete contract-driven release and marketplace procedure lives in
[`docs/release.md`](docs/release.md). Follow it whenever packaged content changes;
an MCP implementation-only release does not automatically require a plugin bump.

## Sources

- [AgentMail documentation](https://docs.agentmail.to)
- [OpenAPI specification](https://docs.agentmail.to/openapi.json)
- [AsyncAPI specification](https://docs.agentmail.to/asyncapi.json)
- [Hosted MCP setup](https://docs.agentmail.to/integrations/mcp)

## License

MIT
