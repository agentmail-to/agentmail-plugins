---
name: agentmail-cli
description: Operate AgentMail from a shell with the official CLI. Use when the user wants commands for listing or creating inboxes, reading or searching mail, sending or replying, managing drafts, or scripting JSON/YAML output; do not use for SDK code, MCP setup, or framework adapters.
---

# AgentMail CLI

Install the CLI and provide the API key through the environment.

```bash
npm install -g agentmail-cli
export AGENTMAIL_API_KEY="am_..."
```

## Inboxes

```bash
agentmail inboxes list
agentmail inboxes get --inbox-id <inbox_id>
agentmail inboxes create --display-name "Support Agent" --username support
agentmail inboxes delete --inbox-id <inbox_id>
```

Confirm the exact inbox before running the destructive delete command.

## Messages and threads

```bash
agentmail inboxes:messages list --inbox-id <inbox_id>
agentmail inboxes:messages get --inbox-id <inbox_id> --message-id <message_id>

agentmail inboxes:messages send --inbox-id <inbox_id> \
  --to "recipient@example.com" \
  --subject "Hello" \
  --text "Message body"

agentmail inboxes:messages reply --inbox-id <inbox_id> \
  --message-id <message_id> \
  --text "Reply body"

agentmail inboxes:threads list --inbox-id <inbox_id>
agentmail inboxes:threads get --inbox-id <inbox_id> --thread-id <thread_id>
```

Use a message ID for replies. Fetch the full message before relying on body content.

## Drafts

```bash
agentmail inboxes:drafts create --inbox-id <inbox_id> \
  --to "recipient@example.com" \
  --subject "Pending approval" \
  --text "Draft body"

agentmail inboxes:drafts list --inbox-id <inbox_id>
agentmail inboxes:drafts get --inbox-id <inbox_id> --draft-id <draft_id>
agentmail inboxes:drafts send --inbox-id <inbox_id> --draft-id <draft_id>
```

## Structured output

The default output mode is `auto`. Use `--format` with `pretty`, `json`, `jsonl`, `yaml`, `raw`, or `explore`.

Use `--transform` and `--transform-error` for GJSON projections, and `--format-error` to control structured error output. Global options also include `--api-key`, `--base-url`, `--environment`, and `--debug`.

Run `agentmail --help` and the relevant resource’s `--help` before using an administrative command not covered here.
