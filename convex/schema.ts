import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  redactionLogs: defineTable({
    inputText: v.string(),
    redactedText: v.string(),
    detections: v.array(
      v.object({
        type: v.string(),
        start: v.number(),
        end: v.number(),
        source: v.string(),
      }),
    ),
    createdAt: v.number(),
  }).index("by_created_at", ["createdAt"]),
  agentLogs: defineTable({
    role: v.string(),
    timestamp: v.string(),
    ticketId: v.string(),
    output: v.string(),
    createdAt: v.number(),
  })
    .index("by_created_at", ["createdAt"])
    .index("by_role", ["role"])
    .index("by_ticket", ["ticketId"]),
});
