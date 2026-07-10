import { AgentMailClient } from "agentmail";
import { AgentMailToolkit } from "agentmail-toolkit/ai-sdk";
import { AgentMailToolkit as LangChainAgentMailToolkit } from "agentmail-toolkit/langchain";
import { AgentMailToolkit as McpAgentMailToolkit } from "agentmail-toolkit/mcp";
import { createAgent } from "langchain";

function typecheckToolkitAdapters(client: AgentMailClient): void {
  void createAgent({
    model: process.env.LANGCHAIN_MODEL!,
    tools: new LangChainAgentMailToolkit().getTools(),
    systemPrompt: "Use email tools only when the user authorizes the external action.",
  });
  void new McpAgentMailToolkit(client).getTools();
}

async function typecheckCurrentSdk(client: AgentMailClient): Promise<void> {
  void new AgentMailToolkit();
  void new AgentMailToolkit(client);
  const inbox = await client.inboxes.create({
    username: "support",
    displayName: "Support Agent",
    clientId: "support-v1",
    metadata: { tenant: "acme" },
  });

  await client.inboxes.list({ limit: 20 });
  await client.inboxes.get(inbox.inboxId);
  await client.inboxes.update(inbox.inboxId, { displayName: "Customer Support" });

  const sent = await client.inboxes.messages.send(inbox.inboxId, {
    to: ["customer@example.com"],
    subject: "Hello",
    text: "Plain-text body",
    html: "<p>Plain-text body</p>",
  });

  await client.inboxes.messages.list(inbox.inboxId, { limit: 20 });
  const message = await client.inboxes.messages.get(inbox.inboxId, sent.messageId);
  await client.inboxes.messages.reply(inbox.inboxId, message.messageId, { text: "Thanks." });
  await client.inboxes.messages.forward(inbox.inboxId, message.messageId, {
    to: "teammate@example.com",
    subject: "Fwd: Hello",
    text: "For your review.",
  });
  await client.inboxes.messages.getAttachment(inbox.inboxId, message.messageId, "att_456");

  await client.inboxes.threads.list(inbox.inboxId, { limit: 20 });
  await client.inboxes.threads.get(inbox.inboxId, message.threadId);

  const draft = await client.inboxes.drafts.create(inbox.inboxId, {
    to: ["customer@example.com"],
    subject: "Pending approval",
    text: "Draft content",
    clientId: "draft-customer-123",
  });
  await client.inboxes.drafts.update(inbox.inboxId, draft.draftId, {
    text: "Revised draft content",
  });
}

async function typecheckWebSocket(client: AgentMailClient): Promise<void> {
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
      void event.inboxIds;
    } else if (event.type === "event" && event.eventType === "message.received") {
      void event.message.subject;
    }
  });
}

void typecheckCurrentSdk;
void typecheckWebSocket;
void typecheckToolkitAdapters;
