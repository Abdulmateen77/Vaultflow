import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const log = mutation({
  args: {
    role: v.string(),
    timestamp: v.string(),
    ticketId: v.string(),
    output: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("agentLogs", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const list = query({
  args: {
    limit: v.optional(v.number()),
    role: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const limit = Math.min(args.limit ?? 50, 100);
    if (args.role) {
      return await ctx.db
        .query("agentLogs")
        .withIndex("by_role", (q) => q.eq("role", args.role!))
        .order("desc")
        .take(limit);
    }
    return await ctx.db
      .query("agentLogs")
      .withIndex("by_created_at")
      .order("desc")
      .take(limit);
  },
});
