#!/usr/bin/env python3
"""Check documented Python calls against agentmail 0.5.6 signatures."""

import inspect

from agentmail import AgentMail

client = AgentMail(api_key="am_test_only")


def params(callable_object: object) -> set:
    return set(inspect.signature(callable_object).parameters)


create_params = params(client.inboxes.create)
assert "request" in create_params
assert "username" not in create_params
assert "client_id" not in create_params

assert {"inbox_id", "to", "subject", "text"} <= params(client.inboxes.messages.send)
assert {"inbox_id", "message_id"} <= params(client.inboxes.messages.get)
assert {"inbox_id", "message_id", "text"} <= params(client.inboxes.messages.reply)
assert {"inbox_id", "message_id", "to"} <= params(client.inboxes.messages.forward)
assert {"inbox_id", "message_id", "attachment_id"} <= params(client.inboxes.messages.get_attachment)
assert {"inbox_id", "thread_id"} <= params(client.inboxes.threads.get)
assert {"inbox_id", "to", "subject", "text"} <= params(client.inboxes.drafts.create)
assert {"inbox_id", "draft_id", "text"} <= params(client.inboxes.drafts.update)

print("Python SDK signature checks passed")
