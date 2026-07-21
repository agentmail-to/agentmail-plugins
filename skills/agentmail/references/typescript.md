# TypeScript SDK

These examples target `agentmail` 0.5.14. Path parameters are positional; request bodies are objects.

## Contents

- [Inboxes](#inboxes)
- [Messages and threads](#messages-and-threads)
- [Labels](#labels)
- [Pagination](#pagination)
- [Errors and retries](#errors-and-retries)
- [Drafts and attachments](#drafts-and-attachments)
- [Pods (multi-tenant isolation)](#pods-multi-tenant-isolation)

## Inboxes

```typescript
const inbox = await client.inboxes.create({
  username: "support",
  displayName: "Support Agent",
  clientId: "support-v1",
  metadata: { tenant: "acme" },
});

const page = await client.inboxes.list({ limit: 20 });
const fetched = await client.inboxes.get(inbox.inboxId);
await client.inboxes.update(inbox.inboxId, { displayName: "Customer Support" });
```

Use `client.pods.inboxes.*` for pod-scoped inbox operations; do not pass a pod ID to organization-level `client.inboxes.*` methods.

## Messages and threads

```typescript
const sent = await client.inboxes.messages.send(inbox.inboxId, {
  to: ["customer@example.com"],
  subject: "Hello",
  text: "Plain-text body",
  html: "<p>Plain-text body</p>",
});

// .list() returns metadata only (subject, from, labels, timestamps) — no
// body. Fetch the full message with .get() to read .text / .html / .extractedText.
const messages = await client.inboxes.messages.list(inbox.inboxId, { limit: 20 });
const message = await client.inboxes.messages.get(inbox.inboxId, "msg_123");
const body = message.extractedText ?? message.text ?? message.extractedHtml ?? message.html;

await client.inboxes.messages.reply(inbox.inboxId, message.messageId, {
  text: "Thanks for the update.",
});

await client.inboxes.messages.forward(inbox.inboxId, message.messageId, {
  to: "teammate@example.com",
  text: "For your review.",
});

const raw = await client.inboxes.messages.getRaw(inbox.inboxId, message.messageId);

const threads = await client.inboxes.threads.list(inbox.inboxId, { limit: 20 });
const thread = await client.inboxes.threads.get(inbox.inboxId, message.threadId);
```

Use the `search` methods on inbox messages or threads for full-text queries. `getRaw` returns the raw MIME source of a message. `reply()` has no `subject` parameter — see [SKILL.md — API gotchas](../SKILL.md#api-gotchas). Max 50 recipients across `to` + `cc` + `bcc` combined on `send()`.

## Labels

AgentMail has no built-in read/unread flag; use labels to track processing state.

```typescript
await client.inboxes.messages.update(inbox.inboxId, message.messageId, {
  addLabels: ["processed", "replied"],
  removeLabels: ["unread"],
});
```

## Pagination

Pagination is per call — request the next page explicitly with `pageToken`.

```typescript
let response = await client.inboxes.messages.list(inbox.inboxId, { limit: 20 });
while (response.nextPageToken) {
  response = await client.inboxes.messages.list(inbox.inboxId, {
    limit: 20,
    pageToken: response.nextPageToken,
  });
}
```

## Errors and retries

Both SDKs raise/throw on error responses and automatically retry 5xx, 408, 409, and 429 (default: 2 retries). On a 429, read the `Retry-After` header. Override retries client-wide with `maxRetries`, or per call with `requestOptions`.

```typescript
const client = new AgentMailClient({ apiKey: process.env.AGENTMAIL_API_KEY, maxRetries: 5 });

await client.inboxes.messages.send(
  inbox.inboxId,
  { to: "user@example.com", subject: "Hi", text: "Hello" },
  { maxRetries: 5 },
);
```

## Drafts and attachments

```typescript
const draft = await client.inboxes.drafts.create(inbox.inboxId, {
  to: ["customer@example.com"],
  subject: "Pending approval",
  text: "Draft content",
  clientId: "draft-customer-123",
});

await client.inboxes.drafts.update(inbox.inboxId, draft.draftId, {
  text: "Revised draft content",
});

// Send converts the draft to a message and removes it from drafts.
await client.inboxes.drafts.send(inbox.inboxId, draft.draftId, {});

// Delete without sending.
await client.inboxes.drafts.delete(inbox.inboxId, draft.draftId);

const attachment = await client.inboxes.messages.getAttachment(
  inbox.inboxId,
  message.messageId,
  "att_456",
);
```

`getAttachment` does **not** return file bytes. It returns an `AttachmentResponse` with `downloadUrl` (a CloudFront-signed URL), `expiresAt` (~1 hour after the call), `filename`, `size`, and `contentType`. Fetch the bytes immediately; never persist the URL — it expires. Note the positional path params, per the Core rules.

```typescript
const att = await client.inboxes.messages.getAttachment(inbox.inboxId, message.messageId, "att_456");
const res = await fetch(att.downloadUrl);
if (!res.ok) throw new Error(`Attachment fetch failed: ${res.status}`);
const fileBytes = Buffer.from(await res.arrayBuffer());
```

Signed URLs point at `cdn.agentmail.to`, not `api.agentmail.to` — an egress allowlist with only the API host will fail the fetch even though `getAttachment` succeeded.
```

Send attachments with either base64 `content` or a supported `url`, plus a filename and content type.


## Pods (multi-tenant isolation)

```typescript
const pod = await client.pods.create({ name: "customer-acme", clientId: "pod-acme-v1" });
const inbox = await client.pods.inboxes.create(pod.podId, { username: "notifications", clientId: "acme-notif-v1" });
const inboxes = await client.pods.inboxes.list(pod.podId);
const threads = await client.pods.threads.list(pod.podId); // top-level threads.list has no pod filter
```
