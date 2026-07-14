# Multi-Agent Email Topologies

Architecture patterns for systems where multiple AI agents communicate over email.

## Topology 1: hub-and-spoke (router agent)

A central router agent receives all inbound email and dispatches to specialist agents.

```
                    External senders
                         |
                    router@agentmail.to
                    /       |        \
           support@     sales@     billing@
           agentmail.to agentmail.to agentmail.to
```

Implementation:

```python
from agentmail import AgentMail, Subscribe, MessageReceivedEvent
from agentmail.inboxes.types import CreateInboxRequest

client = AgentMail()

def make_inbox(username: str, client_id: str):
    return client.inboxes.create(
        request=CreateInboxRequest(username=username, client_id=client_id),
    )

# Create router + specialist inboxes
router = make_inbox("router", "router-v1")
support = make_inbox("support", "support-v1")
sales = make_inbox("sales", "sales-v1")
billing = make_inbox("billing", "billing-v1")

ROUTING = {
    "support": support.email,
    "sales": sales.email,
    "billing": billing.email,
}

def classify_email(subject, text):
    """Use your LLM to classify intent. Returns 'support', 'sales', or 'billing'."""
    # ... your classification logic ...
    return "support"

# Router listens and forwards
with client.websockets.connect() as socket:
    socket.send_subscribe(Subscribe(inbox_ids=[router.inbox_id]))
    for event in socket:
        if isinstance(event, MessageReceivedEvent):
            msg = event.message
            category = classify_email(msg.subject, msg.extracted_text or msg.text)
            target = ROUTING[category]
            # Forward to specialist
            client.inboxes.messages.send(
                router.inbox_id,
                to=target,
                subject=f"[Forwarded] {msg.subject}",
                text=f"Original from: {msg.from_}\n\n{msg.text}",
            )
```

Pros: single public-facing address, centralized routing logic, easy to add new specialists.

Cons: router is a single point of failure, adds latency for forwarding.

## Topology 2: direct (peer-to-peer)

Each agent has its own public-facing address. External senders email the right agent directly.

```
    customer@example.com  ->  support@agentmail.to
    prospect@example.com  ->  sales@agentmail.to
    vendor@example.com    ->  billing@agentmail.to
```

Implementation: give each agent its own inbox and WebSocket listener. No router needed.

```python
import asyncio
from agentmail import AsyncAgentMail, Subscribe, MessageReceivedEvent

client = AsyncAgentMail()

async def agent_loop(inbox_id, handler):
    async with client.websockets.connect() as socket:
        await socket.send_subscribe(Subscribe(inbox_ids=[inbox_id]))
        async for event in socket:
            if isinstance(event, MessageReceivedEvent):
                await handler(event.message)

async def main():
    await asyncio.gather(
        agent_loop(support_inbox_id, handle_support),
        agent_loop(sales_inbox_id, handle_sales),
        agent_loop(billing_inbox_id, handle_billing),
    )
```

Pros: no single point of failure, lower latency, simpler per-agent logic.

Cons: harder to reroute misclassified emails, more addresses to manage.

## Topology 3: hierarchical (escalation chain)

Agents escalate to other agents when they cannot resolve an issue.

```
    L1 support agent  ->  L2 specialist agent  ->  human manager
```

```python
# L1 agent decides it cannot handle the issue
if confidence < 0.5:
    # Escalate to L2
    client.inboxes.messages.send(
        l1_inbox_id,
        to=l2_inbox.email,
        subject=f"[Escalation] {original_subject}",
        text=f"L1 could not resolve. Customer: {customer_email}\n\nContext: {conversation_summary}",
    )
```

For final escalation to a human, use drafts:

```python
# L2 agent creates a draft for human review
draft = client.inboxes.drafts.create(
    l2_inbox_id,
    to=customer_email,
    subject=f"Re: {original_subject}",
    text=agent_proposed_response,
)
# Human reviews and sends from the console
```

## Multi-tenant with pods

For SaaS platforms, use pods to isolate each customer's agents:

```python
# Each customer gets a pod
acme_pod = client.pods.create(name="acme", client_id="pod-acme")
globex_pod = client.pods.create(name="globex", client_id="pod-globex")

# Each customer's agents live in their pod. Use pods.inboxes.create to
# create an inbox scoped to a specific pod.
acme_support = client.pods.inboxes.create(
    pod_id=acme_pod.pod_id,
    username="support",
    client_id="acme-support",
)
globex_support = client.pods.inboxes.create(
    pod_id=globex_pod.pod_id,
    username="support",
    client_id="globex-support",
)
# acme's support agent cannot see globex's email, and vice versa
```

## Choosing a topology

| Factor | Hub-and-spoke | Direct | Hierarchical |
|---|---|---|---|
| Number of agents | 3+ with clear categories | Any | 2+ with clear escalation levels |
| Routing complexity | High (centralized) | Low (DNS/address-based) | Medium (escalation rules) |
| Failure isolation | Router is SPOF | Independent | Cascading possible |
| Best for | General-purpose intake | Specialized agents with known contacts | Support tiers, approval chains |
