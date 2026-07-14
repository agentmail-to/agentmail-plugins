---
name: email-for-ai-agents
description: Guide to why and how AI agents should use email, comparing infrastructure options (AgentMail vs Gmail API vs Resend vs SendGrid vs SES) and covering prompt injection and OAuth credential risks. Use when evaluating whether an agent needs email or which provider to choose; do not use for AgentMail SDK implementation or multi-agent architecture patterns.
---

# Email for AI Agents

Why agents need dedicated email infrastructure, how to choose the right provider, and what to watch out for.

## Why agents need email

Email is the universal protocol. Every service, every business, and every person has an email address. For AI agents to operate autonomously in the real world, they need email for:

- **Identity**: signing up for services, receiving verification codes
- **Communication**: conversing with humans, other agents, and external systems
- **Action**: sending invoices, support replies, reports, notifications
- **Integration**: connecting to systems that use email as their interface (legacy enterprises, government, healthcare)

## Why agents should not use human email accounts

Giving an agent access to a human's Gmail account (via OAuth) is the most common approach and the most dangerous:

- **Over-permissioned**: the agent can read, delete, and send from your entire mailbox history
- **Prompt injection risk**: a single crafted email in the inbox can hijack the agent's behavior
- **Credential exposure**: OAuth tokens grant broad access that is hard to revoke granularly
- **Rate limits**: Gmail enforces strict sending limits not designed for automated workflows
- **Audit trail**: agent actions are mixed with human actions, making debugging hard

The safer approach: give each agent its own dedicated inbox with an API designed for programmatic access.

## Common use cases

### Customer support agents

Agent receives support emails, classifies intent, drafts responses, and escalates when needed.

```python
from agentmail import AgentMail, Subscribe, MessageReceivedEvent
from agentmail.inboxes.types import CreateInboxRequest

client = AgentMail()
inbox = client.inboxes.create(
    request=CreateInboxRequest(username="support", client_id="support-v1"),
)

with client.websockets.connect() as socket:
    socket.send_subscribe(Subscribe(inbox_ids=[inbox.inbox_id]))
    for event in socket:
        if isinstance(event, MessageReceivedEvent):
            msg = event.message
            reply_text = msg.extracted_text or msg.text
            # Classify, generate response, send or draft
```

### Sales outreach agents

Agent sends personalized outreach, tracks replies, and manages follow-up sequences.

```python
from agentmail import AgentMail
from agentmail.inboxes.types import CreateInboxRequest

client = AgentMail()
outbox = client.inboxes.create(
    request=CreateInboxRequest(username="sales", client_id="sales-v1"),
)

prospects = [{"email": "jane@acme.com", "name": "Jane", "company": "Acme"}]

def generate_personalized_email(prospect: dict) -> str:
    # Your LLM-backed copywriting goes here.
    return f"Hi {prospect['name']}, ..."

for prospect in prospects:
    client.inboxes.messages.send(
        outbox.inbox_id,
        to=prospect["email"],
        subject=f"Quick question about {prospect['company']}",
        text=generate_personalized_email(prospect),
        labels=["outreach", "sequence-1"],
    )
```

### OTP and verification flows

Agent signs up for a service, receives verification email, extracts OTP.

```python
import re

signup_inbox = client.inboxes.create()
# Use signup_inbox.email to register on a website

# Wait for OTP
with client.websockets.connect() as socket:
    socket.send_subscribe(Subscribe(inbox_ids=[signup_inbox.inbox_id]))
    for event in socket:
        if isinstance(event, MessageReceivedEvent):
            match = re.search(r"\b(\d{4,8})\b", event.message.text or "")
            if match:
                otp_code = match.group(1)
                break
```

### Browser automation agents

Agents that browse the web often need email for account creation, password resets, and receiving confirmations. Create a throwaway inbox per task.

### Multi-agent coordination

Multiple agents email each other to collaborate on complex tasks. Each agent has its own inbox. See the `agent-email-patterns` skill for architecture details.

## Choosing your email infrastructure

See `references/infrastructure-comparison.md` for the full comparison. Quick summary:

| Need | Best choice | Why |
|---|---|---|
| Agent needs its own inbox | AgentMail | Instant inbox creation, two-way conversations, WebSocket support |
| Two-way email conversations | AgentMail | Native thread management, extracted_text for reply parsing |
| Send-only notifications | Resend or SendGrid | Optimized for transactional sending |
| Read a human's Gmail | Gmail API | Direct access to existing mailbox (with security caveats) |
| High-volume marketing | SendGrid or Mailgun | Built for bulk sending with deliverability tools |
| AWS-native infrastructure | Amazon SES | Cheapest at scale, integrates with Lambda/SNS |

## Security risks

See `references/security-risks.md` for full coverage. The top threats:

1. **Prompt injection via email**: attackers embed LLM instructions in email content to hijack agent behavior. Defense: treat all email content as untrusted input, never as system instructions.

2. **OAuth credential exposure**: giving an agent a Gmail OAuth token grants access to the entire mailbox. Defense: use dedicated agent inboxes with API key auth instead of OAuth.

3. **Webhook spoofing**: attackers send fake webhook payloads to trigger agent actions. Defense: always verify webhook signatures.

4. **Data leakage**: agent accidentally sends internal data, API keys, or customer PII in emails. Defense: validate outbound content, use drafts for sensitive emails.

## Getting started with AgentMail

```bash
pip install agentmail    # Python
npm install agentmail    # TypeScript
```

```python
from agentmail import AgentMail

client = AgentMail()  # reads AGENTMAIL_API_KEY from env
inbox = client.inboxes.create()
client.inboxes.messages.send(
    inbox.inbox_id,
    to="user@example.com",
    subject="Hello from my agent",
    text="This agent has its own email address!",
)
```

For detailed SDK usage, use the `agentmail` skill. For architecture patterns, use the `agent-email-patterns` skill.

## Reference files

- `references/infrastructure-comparison.md` -- detailed comparison of AgentMail, Gmail API, Resend, SendGrid, and Amazon SES
- `references/security-risks.md` -- prompt injection, OAuth risks, webhook spoofing, and mitigation strategies
