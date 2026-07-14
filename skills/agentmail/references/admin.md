# Admin: Sign-Up, Domains, and Lists

These are the admin-adjacent SDK calls with enough sharp edges to document directly. For scoped API keys, permissions, metrics, and pod administration, consult the current [AgentMail API reference](https://docs.agentmail.to/api-reference).

## Agent sign-up

Create an account and API key from code, no console needed. Requires `agentmail>=0.4.15` in Python. The endpoint is idempotent — calling again with the same email rotates the API key and resends the OTP.

```python
client = AgentMail()  # no api_key needed for sign-up
response = client.agent.sign_up(human_email="you@example.com", username="my-agent")
# response.api_key, response.inbox_id, response.organization_id

client = AgentMail(api_key=response.api_key)
client.agent.verify(otp_code="123456")
```

```typescript
const client = new AgentMailClient();
const response = await client.agent.signUp({ humanEmail: "you@example.com", username: "my-agent" });
// response.apiKey, response.inboxId, response.organizationId

const authed = new AgentMailClient({ apiKey: response.apiKey });
await authed.agent.verify({ otpCode: "123456" });
```

## Domains

Set `feedback_enabled` / `feedbackEnabled` to `true` on create to route bounce and complaint notifications to your inboxes (optional in the API and SDKs; the CLI requires the flag). The response's `records` field lists the SPF/DKIM/DMARC verification records to add at your registrar.

```python
domain = client.domains.create(domain="yourdomain.com", feedback_enabled=True)
# domain.records -> list of VerificationRecord objects
client.domains.verify(domain_id=domain.domain_id)
```

```typescript
const domain = await client.domains.create({ domain: "yourdomain.com", feedbackEnabled: true });
// domain.records -> verification records
await client.domains.verify(domain.domainId);
```

Custom domains require a paid plan; `@agentmail.to` inboxes are free and need no verification.

## Allow/block lists

Entries are flat: one `(inbox_id, direction, type, entry)` tuple per call — there is no batch update and no `.allow` / `.block` sub-namespace. `direction` is `"send"`, `"receive"`, or `"reply"`. `type` is `"allow"` or `"block"`; block takes priority over allow.

```python
client.inboxes.lists.create(inbox_id="agent@agentmail.to", direction="receive", type="allow", entry="boss@company.com")
client.inboxes.lists.create(inbox_id="agent@agentmail.to", direction="receive", type="block", entry="spammer@example.com")

entries = client.inboxes.lists.list(inbox_id="agent@agentmail.to", direction="receive", type="allow")
entry = client.inboxes.lists.get(inbox_id="agent@agentmail.to", direction="receive", type="allow", entry="boss@company.com")
client.inboxes.lists.delete(inbox_id="agent@agentmail.to", direction="receive", type="allow", entry="boss@company.com")
```

```typescript
await client.inboxes.lists.create("agent@agentmail.to", "receive", "allow", { entry: "boss@company.com" });
await client.inboxes.lists.create("agent@agentmail.to", "receive", "block", { entry: "spammer@example.com" });

const entries = await client.inboxes.lists.list("agent@agentmail.to", "receive", "allow");
await client.inboxes.lists.delete("agent@agentmail.to", "receive", "allow", "boss@company.com");
```

To replace an allow/block entry, delete the old one and create the new one — there is no bulk update.

## IMAP and SMTP

AgentMail inboxes are also reachable over standard IMAP and SMTP for legacy mail clients. See https://docs.agentmail.to/imap-smtp for host, port, and credential details.
