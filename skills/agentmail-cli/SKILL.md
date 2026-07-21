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

Subcommands for a resource nested under another use a colon, e.g. `inboxes:messages`, `inboxes:threads`, `pods:inboxes`, `pods:threads`.

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

# HTML body instead of plain text
agentmail inboxes:messages send --inbox-id <inbox_id> \
  --to "recipient@example.com" \
  --subject "Hello" \
  --html "<h1>Hello</h1>"

agentmail inboxes:messages reply --inbox-id <inbox_id> \
  --message-id <message_id> \
  --text "Reply body"

agentmail inboxes:messages forward --inbox-id <inbox_id> \
  --message-id <message_id> \
  --to "someone@example.com"

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

## Pods

Pods group inboxes together.

```bash
agentmail pods create --name "My Pod"
agentmail pods list

agentmail pods:inboxes create --pod-id <pod_id> --display-name "Pod Inbox"
agentmail pods:inboxes list --pod-id <pod_id>

agentmail pods:threads list --pod-id <pod_id>
agentmail pods:threads get --pod-id <pod_id> --thread-id <thread_id>
```

## Webhooks

```bash
agentmail webhooks create --url "https://example.com/webhook" --event-type message.received
agentmail webhooks list
```

## Domains

```bash
agentmail domains create --domain example.com

# Optional: route bounce/complaint notifications to your inboxes.
agentmail domains create --domain example.com --feedback-enabled

agentmail domains verify --domain-id <domain_id>
agentmail domains get-zone-file --domain-id <domain_id>
```

## Global flags

| Flag | Purpose |
| --- | --- |
| `--api-key` | Override `AGENTMAIL_API_KEY` for this call |
| `--base-url` | Point at a non-default API host |
| `--environment` | Select a named environment |
| `--format` | Output format (see below) |
| `--format-error` | Control structured error output |
| `--transform` | GJSON projection of a successful response |
| `--transform-error` | GJSON projection of an error response |
| `--debug` | Verbose request/response logging |

## Output formats

`--format` accepts: `auto` (default), `pretty`, `json`, `jsonl`, `yaml`, `raw`, `explore`.

Run `agentmail --help` and the relevant resource's `--help` before using an administrative command not covered here.
