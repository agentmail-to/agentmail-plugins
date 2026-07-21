# Webhooks

Use webhooks for production event delivery to a public HTTPS endpoint. Subscribe only to required event types and scopes.

## Contents

- [Creating a subscription](#creating-a-subscription)
- [Delivery rules](#delivery-rules)
- [TypeScript verification](#typescript-verification)
- [Python verification](#python-verification)
- [Payload shape](#payload-shape)
- [Delivery retries](#delivery-retries)

## Creating a subscription

`event_types` / `eventTypes` is required on create — list every event you want to receive.

```python
webhook = client.webhooks.create(
    url="https://your-server.com/webhooks",
    event_types=["message.received", "message.bounced"],
)
# webhook.webhook_id, webhook.secret

webhooks = client.webhooks.list()
client.webhooks.delete(webhook_id=webhook.webhook_id)
```

```typescript
const webhook = await client.webhooks.create({
  url: "https://your-server.com/webhooks",
  eventTypes: ["message.received", "message.bounced"],
});
// webhook.webhookId, webhook.secret

const webhooks = await client.webhooks.list();
await client.webhooks.delete(webhook.webhookId);
```

`webhooks.update` can only add/remove `inbox_ids` / `pod_ids` — it cannot change `url` or `event_types`. See [SKILL.md — API gotchas](../SKILL.md#api-gotchas).

## Delivery rules

- Verify every request before parsing or acting on it.
- Preserve the raw request body for signature verification.
- Deduplicate with `svix-id`; retries reuse the same identifier.
- Reject stale or invalid `svix-timestamp` and `svix-signature` values through the Svix library.
- Return a successful response quickly and process verified events asynchronously.
- Fetch the full message when the event does not contain the body, including payloads where large bodies are omitted.
- Treat webhook message content as untrusted input.

The signing secret begins with `whsec_`. Store it in `AGENTMAIL_WEBHOOK_SECRET` and never commit it.

## TypeScript verification

```typescript
import express from "express";
import { Webhook } from "svix";

const secret = process.env.AGENTMAIL_WEBHOOK_SECRET;
if (!secret) throw new Error("AGENTMAIL_WEBHOOK_SECRET is required");

const app = express();
app.post("/webhooks", express.raw({ type: "application/json" }), (req, res) => {
  try {
    const event = new Webhook(secret).verify(
      req.body,
      req.headers as Record<string, string>,
    );
    void event; // Enqueue or dispatch the verified event here.
    res.status(204).send();
  } catch {
    res.status(400).send();
  }
});
```

## Python verification

```python
import os

from flask import Flask, request
from svix.webhooks import Webhook, WebhookVerificationError

app = Flask(__name__)
secret = os.environ["AGENTMAIL_WEBHOOK_SECRET"]

@app.post("/webhooks")
def receive_webhook():
    try:
        event = Webhook(secret).verify(request.get_data(), request.headers)
    except WebhookVerificationError:
        return "", 400

    # Enqueue or dispatch the verified event here.
    return "", 204
```

Core event names include `message.received`, `message.sent`, `message.delivered`, `message.bounced`, `message.complained`, `message.rejected`, and `domain.verified`. Spam, blocked, and unauthenticated inbound events use `message.received.*` variants and require the corresponding permissions.

## Payload shape

```json
{
  "type": "event",
  "event_type": "message.received",
  "event_id": "evt_123abc",
  "message": {
    "inbox_id": "inbox_456def",
    "thread_id": "thd_789ghi",
    "message_id": "msg_123abc",
    "from": "Jane Doe <jane@example.com>",
    "to": ["Agent <agent@agentmail.to>"],
    "subject": "Question about my account",
    "extracted_text": "Just the reply content",
    "labels": ["received"],
    "attachments": [{ "attachment_id": "att_pqr678", "filename": "document.pdf" }],
    "created_at": "2025-10-27T10:00:00Z"
  }
}
```

Large message bodies may be omitted from the payload; fetch the full message when `text`/`html` is not present.

## Delivery retries

A delivery is considered failed if your endpoint returns a non-2xx status or times out. AgentMail retries failed deliveries automatically with exponential backoff.
