#!/usr/bin/env python3
"""Exercise the documented Svix webhook verification path with signed fixtures."""

from __future__ import annotations

import base64
import json
import unittest
from datetime import datetime, timedelta, timezone

from svix.webhooks import Webhook, WebhookVerificationError

SECRET = "whsec_" + base64.b64encode(b"agentmail-plugins-test-secret-32").decode()
PAYLOAD = json.dumps({"type": "event", "event_type": "message.received"})


def signed_headers(payload: str, timestamp: datetime) -> dict[str, str]:
    return {
        "svix-id": "msg_test",
        "svix-timestamp": str(int(timestamp.timestamp())),
        "svix-signature": Webhook(SECRET).sign("msg_test", timestamp, payload),
    }


class WebhookVerificationTests(unittest.TestCase):
    def test_valid_signature_verifies(self) -> None:
        now = datetime.now(tz=timezone.utc)
        event = Webhook(SECRET).verify(PAYLOAD, signed_headers(PAYLOAD, now))
        self.assertEqual(event["event_type"], "message.received")

    def test_tampered_body_is_rejected(self) -> None:
        headers = signed_headers(PAYLOAD, datetime.now(tz=timezone.utc))
        with self.assertRaises(WebhookVerificationError):
            Webhook(SECRET).verify(PAYLOAD.replace("received", "sent"), headers)

    def test_stale_timestamp_is_rejected(self) -> None:
        stale = datetime.now(tz=timezone.utc) - timedelta(minutes=10)
        with self.assertRaises(WebhookVerificationError):
            Webhook(SECRET).verify(PAYLOAD, signed_headers(PAYLOAD, stale))


if __name__ == "__main__":
    unittest.main()
