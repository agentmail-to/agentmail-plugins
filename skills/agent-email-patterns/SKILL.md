---
name: agent-email-patterns
description: Architecture patterns for AI agents that communicate over email, covering two-way conversation loops, human-in-the-loop drafts, WebSocket vs webhook event design, multi-agent topologies, OTP flows, and prompt-injection defense. Use when designing how agents send, receive, and manage email conversations; do not use for AgentMail SDK method calls or basic send/receive implementation.
---

# Agent Email Patterns

Opinionated patterns for building AI agents that communicate over email. This skill covers architecture decisions, not SDK specifics. For AgentMail SDK usage, use the `agentmail` skill.

## Pattern 1: one inbox per agent

Every agent gets its own email address. Never share inboxes between agents.

```python
from agentmail import AgentMail
from agentmail.inboxes.types import CreateInboxRequest

client = AgentMail()

support_inbox = client.inboxes.create(
    request=CreateInboxRequest(
        username="support-agent",
        display_name="Acme Support",
        client_id="support-v1",  # idempotent
    ),
)
# support-agent@agentmail.to is now live
```

Why:
- **Identity**: recipients see a clear sender
- **Isolation**: agents cannot access each other's email
- **Auditability**: every message is traceable to one agent
- **Security**: compromising one agent does not expose others

Anti-pattern: one shared inbox with multiple agents reading from it. This creates race conditions and makes debugging impossible.

## Pattern 2: two-way conversation loops

The core agent email pattern: agent sends, human replies, agent reads the reply and responds.

```
Agent sends initial email
  -> Human replies
    -> Agent reads reply (use extracted_text to strip quoted history)
      -> Agent decides next action and responds
        -> Loop continues until resolved
```

Implementation:

```python
# 1. Agent sends the opening message
client.inboxes.messages.send(
    inbox_id,
    to="user@example.com",
    subject="Your support ticket #1234",
    text="We received your request. Can you clarify the issue?",
)

# 2. Later: agent reads the reply.
# messages.list() returns MessageItem objects (metadata only — NO body).
# Fetch the full Message with .get() to access .text / .extracted_text.
response = client.inboxes.messages.list(inbox_id, limit=5)
for item in response.messages:
    msg = client.inboxes.messages.get(
        inbox_id=item.inbox_id,
        message_id=item.message_id,
    )
    # extracted_text strips quoted history and signatures
    new_content = msg.extracted_text or msg.text
    # Feed new_content to your LLM for next response
```

Key rules:
- Always use `extracted_text` / `extracted_html` for inbound replies to avoid processing the entire quoted chain
- Track conversation state in your database, not in the email body
- To keep messages grouped in the same thread, call `client.inboxes.messages.reply(inbox_id, message_id, ...)` with the parent `message_id` — AgentMail routes the reply into the existing thread automatically. There is no `thread_id` parameter on the reply call.

## Pattern 3: human-in-the-loop drafts

For high-stakes emails, let the agent draft and a human approve before sending.

```python
# Agent drafts
draft = client.inboxes.drafts.create(
    inbox_id,
    to="important-client@example.com",
    subject="Contract proposal",
    text=agent_generated_text,
)
# Human reviews in console or via API, then:
client.inboxes.drafts.send(inbox_id, draft.draft_id)
```

Use drafts when:
- Email has legal or financial implications
- Recipient is a VIP or external stakeholder
- Agent is new and untrusted for this workflow

Send directly when:
- Routine notification (receipts, confirmations)
- Agent has proven reliability
- Speed matters (OTP forwarding, automated alerts)

## Pattern 4: event-driven architecture

Never poll for new emails. Use WebSockets or webhooks.

**WebSockets** (best for agents, no public URL needed):

```python
from agentmail import AgentMail, Subscribe, MessageReceivedEvent

client = AgentMail()
with client.websockets.connect() as socket:
    socket.send_subscribe(Subscribe(inbox_ids=[inbox_id]))
    for event in socket:
        if isinstance(event, MessageReceivedEvent):
            process_email(event.message)
```

**Webhooks** (for servers with public endpoints):

```python
webhook = client.webhooks.create(
    url="https://your-server.com/agent/email",
    event_types=["message.received"],
)
```

Decision guide:

| Factor | WebSockets | Webhooks |
|---|---|---|
| Public URL needed | No | Yes |
| Best for | Agents, bots, local dev | Servers, serverless |
| Latency | Lowest (persistent) | HTTP round-trip |
| Reconnection | You handle it | AgentMail retries |

## Pattern 5: multi-agent topologies

For systems with multiple agents, assign clear roles:

```
support@agentmail.to     -> customer support
sales@agentmail.to       -> sales inquiries
billing@agentmail.to     -> invoices and payments
router@agentmail.to      -> intake, routes to correct agent
```

Agents can email each other for internal coordination:

```python
# Support agent escalates to sales
client.inboxes.messages.send(
    support_inbox_id,
    to=sales_inbox.email,
    subject="Lead handoff: Acme Corp",
    text="Customer wants enterprise pricing. Full thread below.",
)
```

Use allow lists (`references/security.md`) to restrict which external senders can reach each agent. For hub-and-spoke, peer-to-peer, and hierarchical escalation patterns, see `references/multi-agent-topologies.md`.

## Pattern 6: OTP and verification flows

Agents that sign up for services need to receive and extract verification codes.

```python
import re

inbox = client.inboxes.create()
# Use inbox.email to sign up for a service

# Listen for OTP via WebSocket
with client.websockets.connect() as socket:
    socket.send_subscribe(Subscribe(inbox_ids=[inbox.inbox_id]))
    for event in socket:
        if isinstance(event, MessageReceivedEvent):
            text = event.message.text or ""
            match = re.search(r"\b(\d{4,8})\b", text)
            if match:
                otp = match.group(1)
                break
```

Best practices:
- Create a fresh inbox per sign-up flow for isolation
- Set a timeout (do not wait indefinitely for OTP)
- Delete the inbox after the flow completes if it is single-use

## Pattern 7: labels for workflow state

Use labels to track message processing state within an inbox:

```python
# When agent processes a message
client.inboxes.messages.update(
    inbox_id, message_id,
    add_labels=["processed", "needs-followup"],
    remove_labels=["unread"],
)

# Query by label
unprocessed = client.inboxes.messages.list(inbox_id, labels=["unread"])
```

Common label schemes:
- `unread` / `processed` / `archived`
- `needs-reply` / `replied` / `escalated`
- `billing` / `support` / `sales` (category routing)

## Security essentials

See `references/security.md` for full coverage. Critical rules:

1. **Sanitize inbound email before passing to LLM** -- prompt injection via email is a real attack vector. Never pass raw email content directly as a system prompt.
2. **Use allow lists** on production agent inboxes to restrict senders.
3. **Verify webhook signatures** to prevent spoofed events.
4. **Never put API keys or secrets in email bodies or subjects.**
5. **Separate agent credentials from human credentials** -- each agent gets its own API key.

## Reference files

- `references/multi-agent-topologies.md` -- hub-and-spoke, peer-to-peer, and hierarchical agent email architectures
- `references/security.md` -- prompt injection defense, sender validation, credential isolation
