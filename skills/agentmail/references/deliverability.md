# Deliverability Triage

Use this when "my agent's email didn't arrive." Find the branch that matches the symptom.

## Sent, but bounced

- Subscribe to the `message.bounced` event (webhook or WebSocket) — a successful `send()` call only confirms AgentMail accepted the message, not that it was delivered.
- Check whether `feedback_enabled` is set on the sending domain. When enabled, AgentMail routes bounce and complaint notifications to your inboxes; if it was never set, you may be missing that feedback entirely. See [admin.md](admin.md#domains).
- Self-monitor bounce rate with `client.metrics.query(event_types=["message.bounced"], ...)` / `client.metrics.query({ eventTypes: ["message.bounced"], ... })`.

## Delivered, but landing in spam

- Check the sending domain's DKIM and SPF records for the two known misconfigurations: a Route 53 DKIM TXT value with a space between its quoted halves, and a second competing SPF record instead of one merged record. See [admin.md](admin.md#dkimspf-gotchas).
- Confirm the domain was actually verified — `domains.create()` returns a `records` field listing what to add at your registrar; `domains.verify()` must succeed afterward.

## Inbound mail never arrives ("blocked" or missing)

- Check the receiving inbox's allow/block lists for `direction="receive"`. A block entry — or a receive-direction allow list that excludes the sender — will filter the message before it reaches you. Block always takes priority over allow. See [admin.md](admin.md#allowblock-lists).
- If the credential has the required label permissions, subscribe to `message.received.spam` / `message.received.blocked` to see mail AgentMail classified as spam or blocked rather than routed to plain `message.received`. See [websockets.md](websockets.md) / [webhooks.md](webhooks.md).

## Domain not verified

- Custom domains need verification before they're fully usable; `@agentmail.to` inboxes need none. Add the SPF/DKIM/DMARC records from the `records` field returned by `domains.create()` at your registrar, then call `domains.verify(domain_id)`.
