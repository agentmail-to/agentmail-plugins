# AgentMail Plugin

Official [AgentMail](https://www.agentmail.to) plugin for AI coding agents. Give your agent its own email inboxes to send, receive, and manage emails.

One repo, one plugin, every agent. This repo follows the [Open Plugins](https://open-plugins.com) standard, so the same components work in Cursor, Claude Code, and OpenAI Codex.

## Structure

```
├── .plugin/plugin.json          # Open Plugins manifest (vendor-neutral)
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .cursor-plugin/plugin.json   # Cursor manifest
├── .codex-plugin/plugin.json    # Codex manifest
├── skills/                      # 4 Agent Skills (SKILL.md format)
├── commands/                    # Slash commands
├── .mcp.json                    # AgentMail MCP server config
└── assets/                      # Logo
```

## What's included

- **MCP server** — connects to the AgentMail API via the [`agentmail-mcp`](https://www.npmjs.com/package/agentmail-mcp) npm package
- **Skills** — `agentmail` (SDK reference), `agentmail-mcp` (MCP setup), `agentmail-cli` (CLI usage), `agentmail-toolkit` (framework integrations)
- **Commands** — `/send-email`, `/check-email`, `/manage-inboxes`

Capabilities:

- Creating and managing email inboxes
- Sending and receiving emails
- Managing threads and conversations
- Handling attachments
- Organizing with labels
- Creating drafts for human-in-the-loop approval
- Real-time notifications via webhooks and websockets
- Multi-tenant isolation with pods

## Installation

Get an API key at [console.agentmail.to](https://console.agentmail.to), then:

### Cursor

Install from the [Cursor plugin directory](https://cursor.directory/plugins), or add this repo from the Customize panel.

### Claude Code

```
/plugin marketplace add agentmail-to/agentmail-plugins
/plugin install agentmail@agentmail
```

### Codex

```
codex plugin marketplace add agentmail-to/agentmail-plugins
```

Then install `agentmail` from `/plugins`.

Set `AGENTMAIL_API_KEY` in your environment so the MCP server can authenticate.

## Links

- [AgentMail Docs](https://docs.agentmail.to)
- [agentmail-mcp on npm](https://www.npmjs.com/package/agentmail-mcp)
- [Agent Skills standard](https://agentskills.io)
- [Open Plugins standard](https://open-plugins.com)

## License

MIT
