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

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `create_inbox` | Create a new email inbox |
| `list_inboxes` | List all inboxes |
| `get_inbox` | Get inbox details |
| `delete_inbox` | Delete an inbox |
| `send_message` | Send an email from an inbox |
| `reply_to_message` | Reply to an existing message |
| `list_threads` | List email threads in an inbox |
| `get_thread` | Get thread details and messages |
| `get_attachment` | Download an attachment |
| `update_message` | Update message labels |

## Best Practices

- Always send both `text` and `html` for best deliverability
- Use labels to organize messages (e.g. "outreach", "replied", "unreplied")
- Use `clientId` for idempotent create operations
- For real-time events, see [webhooks](references/webhooks.md) and [websockets](references/websockets.md)
