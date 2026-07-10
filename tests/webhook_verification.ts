import assert from "node:assert/strict";
import { Webhook } from "svix";

const secret = "whsec_" + Buffer.from("agentmail-plugins-test-secret-32").toString("base64");
const payload = JSON.stringify({ type: "event", event_type: "message.received" });

function signedHeaders(body: string, timestamp: Date): Record<string, string> {
  return {
    "svix-id": "msg_test",
    "svix-timestamp": String(Math.floor(timestamp.getTime() / 1000)),
    "svix-signature": new Webhook(secret).sign("msg_test", timestamp, body),
  };
}

const verified = new Webhook(secret).verify(payload, signedHeaders(payload, new Date()));
assert.deepEqual(verified, JSON.parse(payload));

assert.throws(() =>
  new Webhook(secret).verify(payload.replace("received", "sent"), signedHeaders(payload, new Date())),
);

const stale = new Date(Date.now() - 10 * 60 * 1000);
assert.throws(() => new Webhook(secret).verify(payload, signedHeaders(payload, stale)));

console.log("webhook verification fixtures passed");
