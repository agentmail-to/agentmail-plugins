#!/usr/bin/env python3
"""Check documented Python calls against agentmail 0.5.6 signatures."""

from __future__ import annotations

import inspect
import unittest

from agentmail import AgentMail


class PythonSdkSignatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = AgentMail(api_key="am_test_only")

    def assert_parameters(self, callable_object: object, required: set[str]) -> None:
        parameters = set(inspect.signature(callable_object).parameters)
        self.assertTrue(required <= parameters, f"missing {required - parameters} in {parameters}")

    def test_inbox_create_uses_request_object(self) -> None:
        parameters = set(inspect.signature(self.client.inboxes.create).parameters)
        self.assertIn("request", parameters)
        self.assertNotIn("username", parameters)
        self.assertNotIn("client_id", parameters)

    def test_core_message_methods(self) -> None:
        self.assert_parameters(self.client.inboxes.messages.send, {"inbox_id", "to", "subject", "text"})
        self.assert_parameters(self.client.inboxes.messages.get, {"inbox_id", "message_id"})
        self.assert_parameters(self.client.inboxes.messages.reply, {"inbox_id", "message_id", "text"})
        self.assert_parameters(self.client.inboxes.messages.forward, {"inbox_id", "message_id", "to"})
        self.assert_parameters(
            self.client.inboxes.messages.get_attachment,
            {"inbox_id", "message_id", "attachment_id"},
        )

    def test_thread_and_draft_methods(self) -> None:
        self.assert_parameters(self.client.inboxes.threads.get, {"inbox_id", "thread_id"})
        self.assert_parameters(self.client.inboxes.drafts.create, {"inbox_id", "to", "subject", "text"})
        self.assert_parameters(self.client.inboxes.drafts.update, {"inbox_id", "draft_id", "text"})


if __name__ == "__main__":
    unittest.main()
