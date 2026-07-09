---
description: Send an email using AgentMail
argument-hint: [recipient] [subject]
---

Help the user send an email using AgentMail.

1. Check if the user specified an inbox. If not, use `list_inboxes` to show available inboxes, or create one with `create_inbox`.
2. Compose the email with the provided recipient, subject, and body.
3. Use `send_message` to send. Always include both plain text and HTML versions.
4. Confirm success and provide the message ID.
