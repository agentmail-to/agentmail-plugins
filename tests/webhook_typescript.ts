import express from "express";
import { Webhook } from "svix";

const secret = process.env.AGENTMAIL_WEBHOOK_SECRET;
if (!secret) throw new Error("AGENTMAIL_WEBHOOK_SECRET is required");

const app = express();
app.post("/webhooks", express.raw({ type: "application/json" }), (req, res) => {
  try {
    const event = new Webhook(secret).verify(
      req.body,
      req.headers as Record<string, string>,
    );
    void event;
    res.status(204).send();
  } catch {
    res.status(400).send();
  }
});

void app;
