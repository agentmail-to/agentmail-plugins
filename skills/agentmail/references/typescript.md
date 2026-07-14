# TypeScript SDK

These examples target `agentmail` 0.5.14. Path parameters are positional; request bodies are objects.

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

const threads = await client.inboxes.threads.list(inbox.inboxId, { limit: 20 });
const thread = await client.inboxes.threads.get(inbox.inboxId, message.threadId);
```

Follow `nextPageToken` when it is present. Use the `search` methods on inbox messages or threads for full-text queries.

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

const attachment = await client.inboxes.messages.getAttachment(
  inbox.inboxId,
  message.messageId,
  "att_456",
);
```

Send attachments with either base64 `content` or a supported `url`, plus a filename and content type.
