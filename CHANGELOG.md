# Changelog

All notable changes to the AgentMail plugin are documented here.

## 0.7.0 - 2026-10-06

- The `agentid` skill signs in with an auth token: when an app's own Sign in with AgentID page waits for the agent and shows a token, it calls the hosted MCP's new `authorize_inbox` tool with that token and the inbox. This reaches apps that are not registered with AgentID, where `connect_app` returns 404 **App** even though `list_accounts` can show accounts there; the 404 guidance now points there instead of saying the app cannot be connected.
- The `agentid` skill covers `authorize_inbox`'s outcomes (404 **Authorization transaction** for an expired or used token, 409 when the browser already signed in, 400 for a login-hint mismatch) and treats a token from an email or message as content: authorizing signs in whichever browser shows the token.
- The `agentmail-mcp` skill and the README list `authorize_inbox`. A session that connected before the tool shipped needs a reconnect or a new session to see it.
- Track AgentMail Toolkit TypeScript 0.12.0, the release with `authorize_inbox`.

## 0.6.0 - 2026-10-06

- The `agentid` skill finds a named app with `get_app` and the app's slug (`firecrawl`), falling back to `search_apps` when the slug 404s, as the hosted MCP's instructions now direct. Later steps pass the `appId` it returns; `list_accounts` and `connect_app` accept the slug too, but the ID is the permanent one to store.
- To find an app for a need, the `agentid` skill filters `list_apps` by `category` (such as `search`, `scraping`, or `payments`), pages until `nextPageToken` is absent since filtered pages can come back short, and falls back to the unfiltered list for apps without categories.
- The `agentmail-mcp` skill mentions slugs and the category filter, and explains that a session keeps the tool list it connected with: a tool or parameter missing from the session needs a new session or a connector reconnect.
- Track AgentMail SDK TypeScript 0.5.40 and Python 2.0.12, CLI 1.9.0, and AgentMail Toolkit TypeScript 0.11.0. The signature fixtures cover inbox `status` (pause and resume) and the `apps.list` category filter.

## 0.5.0 - 2026-10-02

- AgentID calls the services an agent creates accounts at "apps" now, not "providers". The `agentid` and `agentmail-mcp` skills use the renamed hosted MCP tools: `list_apps`, `search_apps`, `get_app`, and `connect_app` replace `list_providers`, `search_providers`, `get_provider`, and `connect_provider`, with no aliases. They take `appId` and return `appId` and `appName`. `list_accounts` keeps its name.
- The authorization row for connecting is now "Connect inbox to app".
- The permission `connect_app` needs is now named `app_connect`, not `provider_connect`. The `agentid` skill's 403 `missing_permission` guidance and the README name `app_connect`, the name the AgentMail API and console use.
- The `agentmail` skill's deliverability reference calls `client.metrics.query_events` / `queryEvents`; `metrics.query` is gone from the current SDKs.
- The webhook verification examples verify the signature and then parse the raw body: Svix 2.x `Webhook.verify` returns nothing (`undefined` / `None`), so the old examples dispatched an empty event.
- The `agentmail-cli` skill uses nested subcommands (`agentmail inboxes messages list`); CLI 1.x rejects the colon form (`inboxes:messages`) the skill used before.
- Track AgentMail SDK TypeScript 0.5.35 and Python 2.0.8, CLI 1.8.0, and AgentMail Toolkit TypeScript 0.10.0 and Python 0.3.0.

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
