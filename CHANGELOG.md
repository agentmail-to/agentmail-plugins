# Changelog

All notable changes to the AgentMail plugin are documented here.

## Unreleased

- Track AgentMail Toolkit TypeScript 0.5.0 and Python 0.3.0.
- Document the toolkit's structured-output contract (every tool declares an output schema; MCP calls return validated `structuredContent`) and its framework-native error signaling (adapters throw / MCP returns `isError` on failure, instead of returning an error string). **Blocked on the 0.5.0 / 0.3.0 npm and PyPI publish — the compatibility CI gate stays red until those versions are the registry `latest`.**

## 0.4.0 - 2026-07-14

- Add `agent-email-patterns` and `email-for-ai-agents` skills, moved from the agentmail-skills repository.
- Document admin APIs in the `agentmail` skill: agent sign-up, domain management (including the `feedback_enabled` field), and allow/block lists; add pagination, retry semantics, and raw MIME guidance.
- Expand `agentmail-cli` with pods, webhooks, domains, forward, and HTML-send commands.
- Add per-client configuration and auth options to `agentmail-mcp`.
- Add a framework import table to `agentmail-toolkit`.
- Consolidate `agentmail-sdk` (agentmail-skills repo) into `agentmail`; the agentmail-skills repository becomes a read-only mirror.

## 0.3.0 - 2026-07-10

- Use the hosted AgentMail MCP server with OAuth for Claude, Codex, and Cursor.
- Replace legacy commands with portable `send-email`, `check-email`, and `manage-inboxes` skills.
- Update SDK, CLI, toolkit, webhook, and WebSocket guidance for current AgentMail releases.
- Add plugin validation, compatibility tracking, legal metadata, and repository maintenance instructions.
- Run blocking CI against pinned upstream versions only; move upstream drift detection to a weekly scheduled workflow.
- Add executable Svix webhook verification tests and verified LangChain and MCP toolkit adapter examples.

## 0.2.0 - 2026-07-09

- Consolidate the repository into one Open Plugins-compatible bundle for Cursor, Claude Code, and Codex.
