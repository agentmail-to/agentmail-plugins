# Admin: Domains, Allow/Block Lists, and IMAP/SMTP

These are the admin-adjacent SDK calls with enough sharp edges to document directly. For scoped API keys, permissions, metrics, and pod administration, consult the current [AgentMail API reference](https://docs.agentmail.to/api-reference). For the agent sign-up flow, see the main [SKILL.md](../SKILL.md#agent-sign-up).

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

### DKIM/SPF gotchas

- **AWS Route 53 DKIM records**: the DKIM TXT value must be split into two quoted strings with no space between them. `"first-part""second-part"` is correct; `"first-part" "second-part"` (with a space) breaks verification.
- **One SPF record per domain**: a domain can only have a single SPF TXT record. If you already send mail through another service, merge AgentMail's `include:` into the existing record instead of adding a second one, e.g. `v=spf1 include:spf.agentmail.to include:other.com ~all`.

## Allow/block lists

Entries are flat: one `(inbox_id, direction, type, entry)` tuple per call — there is no batch update and no `.allow` / `.block` sub-namespace. `direction` is `"send"`, `"receive"`, or `"reply"`. `type` is `"allow"` or `"block"`; block takes priority over allow. `create` also accepts an optional `reason` for documenting why an entry was added.

```python
client.inboxes.lists.create(inbox_id="agent@agentmail.to", direction="receive", type="allow", entry="boss@company.com")
client.inboxes.lists.create(inbox_id="agent@agentmail.to", direction="receive", type="block", entry="spammer@example.com", reason="repeated abuse")

entries = client.inboxes.lists.list(inbox_id="agent@agentmail.to", direction="receive", type="allow")
entry = client.inboxes.lists.get(inbox_id="agent@agentmail.to", direction="receive", type="allow", entry="boss@company.com")
client.inboxes.lists.delete(inbox_id="agent@agentmail.to", direction="receive", type="allow", entry="boss@company.com")
```

```typescript
await client.inboxes.lists.create("agent@agentmail.to", "receive", "allow", { entry: "boss@company.com" });
await client.inboxes.lists.create("agent@agentmail.to", "receive", "block", { entry: "spammer@example.com", reason: "repeated abuse" });

const entries = await client.inboxes.lists.list("agent@agentmail.to", "receive", "allow");
await client.inboxes.lists.delete("agent@agentmail.to", "receive", "allow", "boss@company.com");
```

To replace an allow/block entry, delete the old one and create the new one — there is no bulk update.

## IMAP and SMTP

AgentMail inboxes are also reachable over standard IMAP and SMTP for legacy mail clients. Authenticate with the inbox address as the username and an API key as the password.

| Protocol | Host | Port | Auth |
|---|---|---|---|
| IMAP | `imap.agentmail.to` | 993 (SSL) | inbox address + API key |
| SMTP | `smtp.agentmail.to` | 465 (SSL) | inbox address + API key |

See https://docs.agentmail.to/imap-smtp for further setup details.
