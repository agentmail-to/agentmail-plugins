---
name: manage-inboxes
description: Create, list, inspect, update, or delete AgentMail inboxes through the connected MCP server. Use when the user asks for a new agent email address, wants to inspect available inboxes, change an inbox display name or metadata, or remove an inbox.
---

# Manage Inboxes

Use AgentMail MCP inbox tools while preserving the user’s intended address, scope, and data.

## Workflow

- Use `list_inboxes` to discover inboxes and `get_inbox` for exact details.
- Use `create_inbox` only after the user asks for a new inbox. Pass a requested username, verified domain, display name, metadata, and client ID when supplied.
- Use `update_inbox` for display-name or metadata changes. Explain that metadata keys merge and that setting keys to null removes them.
- Use `delete_inbox` only after showing the exact inbox ID/address and receiving explicit confirmation. Deletion is destructive and can remove access to its mail.
- Return the inbox ID, email address, pod scope, display name, metadata, and creation time when relevant.

## Guardrails

- Do not invent a custom domain or assume it is verified.
- Use a stable client ID when the caller needs idempotent inbox creation.
- Do not broaden an inbox- or pod-scoped credential beyond its current scope.
- Never expose API keys or unrelated mailbox data in the result.
