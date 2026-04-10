---
name: agentmail
description: Give AI agents their own email inboxes using the AgentMail API. Use when building email agents, sending/receiving emails programmatically, managing inboxes, handling attachments, organizing with labels, creating drafts for human approval, or setting up real-time notifications via webhooks/websockets. Supports multi-tenant isolation with pods.
---

# AgentMail SDK

AgentMail is an API-first email platform for AI agents. Install the SDK and initialize the client.

## Installation

```bash
# TypeScript/Node
npm install agentmail

# Python
pip install agentmail
```

## Setup

```typescript
import { AgentMailClient } from "agentmail";
const client = new AgentMailClient({ apiKey: "YOUR_API_KEY" });
```

```python
from agentmail import AgentMail
client = AgentMail(api_key="YOUR_API_KEY")
```

## Inboxes

Create scalable inboxes on-demand. Each inbox has a unique email address.

```typescript
const autoInbox = await client.inboxes.create();
const customInbox = await client.inboxes.create({
  username: "support",
  domain: "yourdomain.com",
});
const inboxes = await client.inboxes.list();
const fetchedInbox = await client.inboxes.get({ inboxId: "inbox@agentmail.to" });
await client.inboxes.delete({ inboxId: "inbox@agentmail.to" });
```

```python
inbox = client.inboxes.create()
inbox = client.inboxes.create(username="support", domain="yourdomain.com")
inboxes = client.inboxes.list()
inbox = client.inboxes.get(inbox_id="inbox@agentmail.to")
client.inboxes.delete(inbox_id="inbox@agentmail.to")
```

## Messages

Always send both `text` and `html` for best deliverability.

```typescript
await client.inboxes.messages.send({
  inboxId: "agent@agentmail.to",
  to: "recipient@example.com",
  subject: "Hello",
  text: "Plain text version",
  html: "<p>HTML version</p>",
  labels: ["outreach"],
});
await client.inboxes.messages.reply({
  inboxId: "agent@agentmail.to",
  messageId: "msg_123",
  text: "Thanks for your email!",
});
const messages = await client.inboxes.messages.list({ inboxId: "agent@agentmail.to" });
const message = await client.inboxes.messages.get({ inboxId: "agent@agentmail.to", messageId: "msg_123" });
await client.inboxes.messages.update({
  inboxId: "agent@agentmail.to",
  messageId: "msg_123",
  addLabels: ["replied"],
  removeLabels: ["unreplied"],
});
```

```python
client.inboxes.messages.send(inbox_id="agent@agentmail.to", to="recipient@example.com", subject="Hello", text="Plain text version", html="<p>HTML version</p>", labels=["outreach"])
client.inboxes.messages.reply(inbox_id="agent@agentmail.to", message_id="msg_123", text="Thanks for your email!")
messages = client.inboxes.messages.list(inbox_id="agent@agentmail.to")
message = client.inboxes.messages.get(inbox_id="agent@agentmail.to", message_id="msg_123")
client.inboxes.messages.update(inbox_id="agent@agentmail.to", message_id="msg_123", add_labels=["replied"], remove_labels=["unreplied"])
```

## Threads

```typescript
const threads = await client.inboxes.threads.list({ inboxId: "agent@agentmail.to", labels: ["unreplied"] });
const thread = await client.inboxes.threads.get({ inboxId: "agent@agentmail.to", threadId: "thd_123" });
const allThreads = await client.threads.list();
```

```python
threads = client.inboxes.threads.list(inbox_id="agent@agentmail.to", labels=["unreplied"])
thread = client.inboxes.threads.get(inbox_id="agent@agentmail.to", thread_id="thd_123")
all_threads = client.threads.list()
```

## Attachments

```typescript
const content = Buffer.from(fileBytes).toString("base64");
await client.inboxes.messages.send({
  inboxId: "agent@agentmail.to",
  to: "recipient@example.com",
  subject: "Report",
  text: "See attached.",
  attachments: [{ content, filename: "report.pdf", contentType: "application/pdf" }],
});
const fileData = await client.inboxes.messages.getAttachment({ inboxId: "agent@agentmail.to", messageId: "msg_123", attachmentId: "att_456" });
```

```python
import base64
content = base64.b64encode(file_bytes).decode()
client.inboxes.messages.send(inbox_id="agent@agentmail.to", to="recipient@example.com", subject="Report", text="See attached.", attachments=[{"content": content, "filename": "report.pdf", "content_type": "application/pdf"}])
file_data = client.inboxes.messages.get_attachment(inbox_id="agent@agentmail.to", message_id="msg_123", attachment_id="att_456")
```

## Drafts

```typescript
const draft = await client.inboxes.drafts.create({ inboxId: "agent@agentmail.to", to: "recipient@example.com", subject: "Pending approval", text: "Draft content" });
await client.inboxes.drafts.send({ inboxId: "agent@agentmail.to", draftId: draft.draftId });
```

```python
draft = client.inboxes.drafts.create(inbox_id="agent@agentmail.to", to="recipient@example.com", subject="Pending approval", text="Draft content")
client.inboxes.drafts.send(inbox_id="agent@agentmail.to", draft_id=draft.draft_id)
```

## Pods

Multi-tenant isolation for SaaS platforms.

```typescript
const pod = await client.pods.create({ clientId: "customer_123" });
const inbox = await client.inboxes.create({ podId: pod.podId });
const inboxes = await client.inboxes.list({ podId: pod.podId });
```

```python
pod = client.pods.create(client_id="customer_123")
inbox = client.inboxes.create(pod_id=pod.pod_id)
inboxes = client.inboxes.list(pod_id=pod.pod_id)
```

## Idempotency

Use `clientId` for safe retries on create operations.

```typescript
const inbox = await client.inboxes.create({ clientId: "unique-idempotency-key" });
```

```python
inbox = client.inboxes.create(client_id="unique-idempotency-key")
```

## Real-Time Events

- [webhooks.md](references/webhooks.md) - HTTP-based notifications (requires public URL)
- [websockets.md](references/websockets.md) - Persistent connection (no public URL needed)
