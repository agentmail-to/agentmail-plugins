# Python SDK

These examples target `agentmail` 0.5.6. Python methods use snake_case, and configured organization-level inbox creation uses a request object.

## Contents

- [Inboxes](#inboxes)
- [Messages and threads](#messages-and-threads)
- [Labels](#labels)
- [Pagination](#pagination)
- [Errors and retries](#errors-and-retries)
- [Drafts and attachments](#drafts-and-attachments)
- [Pods (multi-tenant isolation)](#pods-multi-tenant-isolation)
- [Async client](#async-client)

## Inboxes

```python
from agentmail.inboxes.types import CreateInboxRequest

inbox = client.inboxes.create(
    request=CreateInboxRequest(
        username="support",
        display_name="Support Agent",
        client_id="support-v1",
        metadata={"tenant": "acme"},
    )
)

page = client.inboxes.list(limit=20)
fetched = client.inboxes.get(inbox_id=inbox.inbox_id)
client.inboxes.update(inbox_id=inbox.inbox_id, display_name="Customer Support")
```

Use `client.pods.inboxes.*` for pod-scoped inbox operations; do not pass `pod_id` to organization-level `client.inboxes.*` methods. Unlike `client.inboxes.create`, `client.pods.inboxes.create` takes flat kwargs, not a request object. See [SKILL.md — API gotchas](../SKILL.md#api-gotchas).

## Messages and threads

```python
sent = client.inboxes.messages.send(
    inbox_id=inbox.inbox_id,
    to="customer@example.com",
    subject="Hello",
    text="Plain-text body",
    html="<p>Plain-text body</p>",
)

# .list() returns MessageItem objects (metadata only: subject, from, labels,
# timestamps). There is no body. Fetch the full message with .get() to read
# .text / .html / .extracted_text.
messages = client.inboxes.messages.list(inbox_id=inbox.inbox_id, limit=20)
message = client.inboxes.messages.get(
    inbox_id=inbox.inbox_id,
    message_id="msg_123",
)
body = message.extracted_text or message.text or message.extracted_html or message.html

client.inboxes.messages.reply(
    inbox_id=inbox.inbox_id,
    message_id=message.message_id,
    text="Thanks for the update.",
)

client.inboxes.messages.forward(
    inbox_id=inbox.inbox_id,
    message_id=message.message_id,
    to="teammate@example.com",
    text="For your review.",
)

raw = client.inboxes.messages.get_raw(
    inbox_id=inbox.inbox_id,
    message_id=message.message_id,
)

threads = client.inboxes.threads.list(inbox_id=inbox.inbox_id, limit=20)
thread = client.inboxes.threads.get(
    inbox_id=inbox.inbox_id,
    thread_id=message.thread_id,
)
```

Use the `search` methods on inbox messages or threads for full-text queries. `get_raw` returns the raw MIME source of a message. `reply()` has no `subject` parameter — see [SKILL.md — API gotchas](../SKILL.md#api-gotchas). Max 50 recipients across `to` + `cc` + `bcc` combined on `send()`.

## Labels

AgentMail has no built-in read/unread flag; use labels to track processing state.

```python
client.inboxes.messages.update(
    inbox_id=inbox.inbox_id,
    message_id=message.message_id,
    add_labels=["processed", "replied"],
    remove_labels=["unread"],
)
```

## Pagination

Pagination is per call — request the next page explicitly with `page_token`.

```python
response = client.inboxes.messages.list(inbox_id=inbox.inbox_id, limit=20)
while response.next_page_token:
    response = client.inboxes.messages.list(
        inbox_id=inbox.inbox_id,
        limit=20,
        page_token=response.next_page_token,
    )
```

## Errors and retries

Both SDKs raise/throw on error responses and automatically retry 5xx, 408, 409, and 429 (default: 2 retries). On a 429, read the `Retry-After` header. The `AgentMail` constructor has no `max_retries` argument — override retries per call with `request_options`.

```python
client.inboxes.messages.send(
    inbox_id=inbox.inbox_id,
    to="user@example.com",
    subject="Hi",
    text="Hello",
    request_options={"max_retries": 5},
)
```

## Drafts and attachments

```python
draft = client.inboxes.drafts.create(
    inbox_id=inbox.inbox_id,
    to="customer@example.com",
    subject="Pending approval",
    text="Draft content",
    client_id="draft-customer-123",
)

client.inboxes.drafts.update(
    inbox_id=inbox.inbox_id,
    draft_id=draft.draft_id,
    text="Revised draft content",
)

# Send converts the draft to a message and removes it from drafts.
client.inboxes.drafts.send(inbox_id=inbox.inbox_id, draft_id=draft.draft_id)

# Delete without sending.
client.inboxes.drafts.delete(inbox_id=inbox.inbox_id, draft_id=draft.draft_id)

attachment = client.inboxes.messages.get_attachment(
    inbox_id=inbox.inbox_id,
    message_id=message.message_id,
    attachment_id="att_456",
)
```

`get_attachment` does **not** return file bytes. It returns an `AttachmentResponse` with `download_url` (a CloudFront-signed URL), `expires_at` (~1 hour after the call), `filename`, `size`, and `content_type`. The signed URL is public-readable during its window — no auth header on the GET. Fetch the bytes immediately; never persist the URL (a later worker sees an expired-signature 403). Store the bytes or the `attachment_id` and re-fetch a fresh URL on demand.

```python
import urllib.request

att = client.inboxes.messages.get_attachment(
    inbox_id=inbox.inbox_id, message_id=message.message_id, attachment_id="att_456",
)
with urllib.request.urlopen(att.download_url, timeout=30) as r:
    file_bytes = r.read()
```

Signed URLs point at `cdn.agentmail.to`, not `api.agentmail.to` — sandboxes that only allow the API host will 403/timeout on the fetch even though `get_attachment` succeeded.

Send attachments with either base64 `content` or a supported `url`, plus `filename` and `content_type`.

## Pods (multi-tenant isolation)

Each pod is an isolated set of inboxes (one per customer/tenant). Note `pods.inboxes.create` takes flat kwargs, unlike top-level `inboxes.create`.

```python
pod = client.pods.create(name="customer-acme", client_id="pod-acme-v1")
inbox = client.pods.inboxes.create(pod_id=pod.pod_id, username="notifications", client_id="acme-notif-v1")
inboxes = client.pods.inboxes.list(pod_id=pod.pod_id)
threads = client.pods.threads.list(pod_id=pod.pod_id)   # top-level threads.list has no pod filter
pods = client.pods.list()
client.pods.delete(pod_id=pod.pod_id)
```

## Async client

For async codebases, use `AsyncAgentMail` in place of `AgentMail`; it mirrors the same method names with `await`.

```python
from agentmail import AsyncAgentMail

client = AsyncAgentMail()
inbox = await client.inboxes.create(request=CreateInboxRequest(username="support"))
```
