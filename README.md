# AgentMail Agent Plugins

Official [AgentMail](https://www.agentmail.to) plugins for AI coding agents. Give your agent its own email inboxes to send, receive, and manage emails.

## Plugins

### [Codex](./codex)

Plugin for [OpenAI Codex](https://developers.openai.com/codex). Includes 4 skills, MCP server config, and logo assets.

### [Claude Code](./claude-code)

Plugin for [Claude Code](https://docs.claude.com). Includes MCP server config for the AgentMail API.

## What's included

Both plugins connect to the AgentMail API via the `agentmail-mcp` npm package and provide tools for:

- Creating and managing email inboxes
- Sending and receiving emails
- Managing threads and conversations
- Handling attachments
- Organizing with labels
- Creating drafts for human-in-the-loop approval
- Real-time notifications via webhooks and websockets
- Multi-tenant isolation with pods

## Getting an API key

Sign up at [console.agentmail.to](https://console.agentmail.to) to get your API key.

## Links

- [AgentMail Docs](https://docs.agentmail.to)
- [agentmail-mcp on npm](https://www.npmjs.com/package/agentmail-mcp)
- [AgentMail MCP Server repo](https://github.com/agentmail-to/agentmail-smithery-mcp)
- [Agent Skills](https://agentskills.io)

## License

MIT
