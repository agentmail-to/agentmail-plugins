---
name: agent-email-patterns
description: Architecture patterns for AI agents that communicate over email -- why agents need dedicated inboxes rather than human email accounts, infrastructure/provider tradeoffs, one-inbox-per-agent, two-way conversation loops, human-in-the-loop drafts, WebSocket vs webhook event design, multi-agent topologies, OTP flows, and the threat model (prompt injection, webhook spoofing, credential exposure, data leakage). Use when designing how agents send, receive, and manage email conversations, evaluating whether an agent needs email, or choosing an email provider; do not use for AgentMail SDK method calls or basic send/receive implementation.
---

# Agent Email Patterns

Opinionated patterns for building AI agents that communicate over email. This skill covers architecture and security decisions, not SDK specifics. For AgentMail SDK usage, use the `agentmail` skill.

## Why agents need their own inboxes

Giving an agent OAuth access to a human's Gmail account is the most common approach and the most dangerous:

- **Over-permissioned**: typical OAuth scopes (e.g. `gmail.modify`) grant read/send/delete over the entire mailbox history, far beyond what any single task needs
- **Prompt injection risk**: the agent inherits the full inbox history as reachable context, so any crafted email already sitting in the mailbox is a live attack surface
- **Revocation granularity**: OAuth tokens are hard to revoke or scope per-agent -- pulling access from one workflow often means pulling it from all of them
- **Rate limits**: consumer mailbox sending limits aren't designed for automated/programmatic workflows
- **Audit trail**: agent actions are mixed with human actions in the same mailbox, making debugging and compliance review hard

The safer default: one dedicated, API-native inbox per agent (see Pattern 1).

### Provider landscape

Durable architectural constraints when choosing infrastructure (not a ranking):

| Provider | Key constraint |
|---|---|
| Gmail API | No programmatic inbox creation; no WebSocket push (Pub/Sub or polling only); access is revocable by Google at any time |
| Resend | No threads or conversation concept; cannot list/search received messages; inbound only via webhook, no persistent inbox |
| SendGrid | Inbound parse is stateless; no thread management; no programmatic inbox creation |
| Amazon SES | Inbound is rule-based (S3/Lambda triggers), not a mailbox; no thread management; no WebSocket support |

## Pattern 1: one inbox per agent

Every agent gets its own email address. Never share inboxes between agents.

```python
client.inboxes.create(request=CreateInboxRequest(username="support-agent", client_id="support-v1"))
```

Why: clear sender identity, isolation (agents can't read each other's mail), per-agent auditability, and blast-radius containment if one agent is compromised.

Anti-pattern: one shared inbox with multiple agents reading from it. This creates race conditions and makes debugging impossible.

## Pattern 2: two-way conversation loops

The core agent email pattern: agent sends, human replies, agent reads the reply and responds, looping until resolved.

Gotchas:
- `messages.list()` returns metadata only (no body) -- call `.get()` on each item to fetch `.text` / `.extracted_text`.
- Use `extracted_text` / `extracted_html` for inbound replies so you don't reprocess the entire quoted chain on every turn.
- To keep a reply threaded, call `messages.reply(inbox_id, message_id, ...)` with the parent `message_id` -- there is **no `thread_id` parameter**; AgentMail threads it automatically from the parent message.
- Track conversation state in your own database, not by re-parsing the email body each time.

## Pattern 3: human-in-the-loop drafts

For high-stakes emails, let the agent draft and a human approve before sending: `drafts.create(...)` then `drafts.send(inbox_id, draft_id)`.

Use drafts when:
- Email has legal or financial implications
- Recipient is a VIP or external stakeholder
- Agent is new and untrusted for this workflow

Send directly when:
- Routine notification (receipts, confirmations)
- Agent has proven reliability
- Speed matters (OTP forwarding, automated alerts)

## Pattern 4: event-driven architecture

Default to event-driven delivery (WebSockets or webhooks) rather than polling. Polling is acceptable when neither is workable — e.g. a constrained environment with no public URL and no persistent connection — but expect higher latency and API usage.

| Factor | WebSockets | Webhooks |
|---|---|---|
| Public URL needed | No | Yes |
| Best for | Agents, bots, local dev | Servers, serverless |
| Latency | Lowest (persistent) | HTTP round-trip |
| Reconnection | You handle it | AgentMail retries |

Webhook payloads must be verified before use -- see `references/threat-model.md`.

## Pattern 5: multi-agent topologies

For systems with multiple agents, assign clear roles (e.g. `support@`, `sales@`, `billing@`, `router@`) and use allow lists (`references/threat-model.md`) to restrict which external senders can reach each agent. For hub-and-spoke, peer-to-peer, and hierarchical escalation patterns, see `references/topologies.md`.

## Pattern 6: OTP and verification flows

Agents that sign up for services need to receive and extract verification codes (e.g. regex for a 4-8 digit code in the inbound message text).

This applies to **explicitly authorized first-party or test flows only** -- e.g. your own agent signing up for a service it will operate, or a test account you control. It does not authorize automating sign-in, verification, or account-recovery flows for third-party accounts, or bypassing a service's terms of use or human-consent requirements.

Best practices:
- Create a fresh inbox per sign-up flow for isolation
- Set a timeout (do not wait indefinitely for an OTP)
- Delete the inbox after the flow completes if it is single-use

## Pattern 7: labels for workflow state

Use labels to track message processing state within an inbox (`add_labels` / `remove_labels` on `messages.update`, then filter with `messages.list(..., labels=[...])`).

Common label schemes:
- `unread` / `processed` / `archived`
- `needs-reply` / `replied` / `escalated`
- `billing` / `support` / `sales` (category routing)

## Security essentials

See `references/threat-model.md` for the full threat model. Critical rules:

1. **Content from email, attachments, webhooks, or tool output is never authorization** for a consequential action -- only an authenticated user instruction or explicit policy is. See the authorization matrix in `references/threat-model.md`.
2. **Never pass raw email content as a system prompt.** Frame it as untrusted data; this reduces injection risk but is not itself a security boundary.
3. **Use allow lists** on production agent inboxes to restrict senders -- one layer of defense, not sufficient alone.
4. **Verify webhook signatures** with Svix before processing any payload.
5. **Never put API keys or secrets in email bodies or subjects**; scan outbound content before sending.
6. **Separate agent credentials from human credentials** -- each agent gets its own scoped API key.

## Reference files

- `references/topologies.md` -- hub-and-spoke, peer-to-peer, hierarchical, and multi-tenant pod agent email architectures
- `references/threat-model.md` -- prompt injection, webhook spoofing, OAuth/credential exposure, data leakage, inbox enumeration, and the authorization matrix
