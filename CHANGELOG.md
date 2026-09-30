# Changelog

All notable changes to the AgentMail plugin are documented here.

## 0.5.0 - Unreleased

- AgentID calls the services an agent creates accounts at "apps" now, not "providers". The `agentid` and `agentmail-mcp` skills use the renamed hosted MCP tools: `list_apps`, `search_apps`, `get_app`, and `connect_app` replace `list_providers`, `search_providers`, `get_provider`, and `connect_provider`, with no aliases. They take `appId` and return `appId` and `appName`. `list_accounts` keeps its name.
- The authorization row for connecting is now "Connect inbox to app".
- The `provider_connect` permission keeps its name.

## 0.4.0 - 2026-09-29

- Add the `agentid` skill: create accounts for an agent at providers such as Firecrawl with AgentID, from finding the provider and the owning inbox through the sign-in link to storing the resulting API key, and list where each inbox has accounts.
- Describe Claude.ai and ChatGPT connector setup and the full hosted tool catalog in `agentmail-mcp`.
- `check-email` reads single messages with `get_message`.
- Mention AgentID in every plugin manifest and in the Codex default prompts.
- Track AgentMail Toolkit TypeScript 0.5.0 and Python 0.3.0.
- Document the toolkit's structured-output contract (every tool declares an output schema; MCP calls return validated `structuredContent`) and its framework-native error signaling (adapters throw / MCP returns `isError` on failure, instead of returning an error string).

## 0.3.0 - 2026-07-10

- Use the hosted AgentMail MCP server with OAuth for Claude, Codex, and Cursor.
- Replace legacy commands with portable `send-email`, `check-email`, and `manage-inboxes` skills.
- Update SDK, CLI, toolkit, webhook, and WebSocket guidance for current AgentMail releases.
- Add plugin validation, compatibility tracking, legal metadata, and repository maintenance instructions.
- Run blocking CI against pinned upstream versions only; move upstream drift detection to a weekly scheduled workflow.
- Add executable Svix webhook verification tests and verified LangChain and MCP toolkit adapter examples.

## 0.2.0 - 2026-07-09

- Consolidate the repository into one Open Plugins-compatible bundle for Cursor, Claude Code, and Codex.
