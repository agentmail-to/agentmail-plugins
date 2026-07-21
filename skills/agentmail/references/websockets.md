# WebSockets

Use WebSockets for low-latency events without exposing a public webhook endpoint. Reconnect, resubscribe, and make event processing idempotent.

## TypeScript

Current event objects use `type: "event"`; the API event name is in `eventType`.

```typescript
import { AgentMailClient } from "agentmail";

const client = new AgentMailClient({
  apiKey: process.env.AGENTMAIL_API_KEY,
});
const socket = await client.websockets.connect();

socket.on("open", () => {
  socket.sendSubscribe({
    type: "subscribe",
    inboxIds: ["agent@agentmail.to"],
    eventTypes: ["message.received"],
  });
});

socket.on("message", (event) => {
  if (event.type === "subscribed") {
    console.log("Subscribed", event.inboxIds);
  } else if (event.type === "event" && event.eventType === "message.received") {
    console.log(event.message.subject);
  }
});
```

Do not compare `event.type` to `message.received`; that is an API event name, not the envelope discriminator.

## Python

Use generated event classes, and inspect `event.event_type` when distinguishing received-message variants. For async code, use `AsyncAgentMail` and `async with` / `async for` — see [python.md](python.md#async-client).

```python
from agentmail import AgentMail, MessageReceivedEvent, Subscribe, Subscribed

client = AgentMail()

with client.websockets.connect() as socket:
    socket.send_subscribe(
        Subscribe(
            inbox_ids=["agent@agentmail.to"],
            event_types=["message.received"],
        )
    )

    for event in socket:
        if isinstance(event, Subscribed):
            print("Subscribed", event.inbox_ids)
        elif isinstance(event, MessageReceivedEvent):
            print(event.event_type, event.message.subject)
```

Explicitly subscribe to `message.received.spam`, `message.received.blocked`, or `message.received.unauthenticated` only when the credential has the required label permissions and the application intentionally processes those messages.

## Event types

| Event | Python class | TypeScript type |
|---|---|---|
| Subscription confirmed | `Subscribed` | `AgentMail.Subscribed` |
| New email received | `MessageReceivedEvent` | `AgentMail.MessageReceivedEvent` |
| Email sent | `MessageSentEvent` | `AgentMail.MessageSentEvent` |
| Email delivered | `MessageDeliveredEvent` | `AgentMail.MessageDeliveredEvent` |
| Email bounced | `MessageBouncedEvent` | `AgentMail.MessageBouncedEvent` |
| Spam complaint | `MessageComplainedEvent` | `AgentMail.MessageComplainedEvent` |
| Email rejected | `MessageRejectedEvent` | `AgentMail.MessageRejectedEvent` |
| Domain verified | `DomainVerifiedEvent` | `AgentMail.DomainVerifiedEvent` |

## Reconnection

The SDK does not auto-reconnect. Reconnect with exponential backoff and resubscribe on every connection:

```python
backoff = 1
while True:
    try:
        with client.websockets.connect() as socket:
            socket.send_subscribe(Subscribe(inbox_ids=["agent@agentmail.to"]))
            backoff = 1  # reset after a successful connection
            for event in socket:
                ...
    except Exception:
        time.sleep(backoff)
        backoff = min(backoff * 2, 60)
```
