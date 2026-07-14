# Python SDK

These examples target `agentmail` 0.5.6. Python methods use snake_case, and configured organization-level inbox creation uses a request object.

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

Use `client.pods.inboxes.*` for pod-scoped inbox operations; do not pass `pod_id` to organization-level `client.inboxes.*` methods.

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

Use the `search` methods on inbox messages or threads for full-text queries. `get_raw` returns the raw MIME source of a message.

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

attachment = client.inboxes.messages.get_attachment(
    inbox_id=inbox.inbox_id,
    message_id=message.message_id,
    attachment_id="att_456",
)
```

Send attachments with either base64 `content` or a supported `url`, plus `filename` and `content_type`.
