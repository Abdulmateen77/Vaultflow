import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const detection = v.object({
  type: v.string(),
  start: v.number(),
  end: v.number(),
  source: v.string(),
});

export const log = mutation({
  args: {
    inputText: v.string(),
    redactedText: v.string(),
    detections: v.array(detection),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("redactionLogs", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const list = query({
  args: {
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("redactionLogs")
      .withIndex("by_created_at")
      .order("desc")
      .take(Math.min(args.limit ?? 50, 100));
  },
});
