// convex/functions.ts

import { mutation } from "./_generated/server";
import { v } from "convex/values";

/**
 * Mutation to add a guest with an image URL to the Convex database.
 */
export const storeGuest = mutation({
  // Define the arguments schema using Convex's schema builder `s`
  args: {
    name: v.string(),
    email: v.string(),
    imageUrl: v.string(),
  },
  // The handler function that performs the database operation
  handler: async (ctx, args) => {
    const { db } = ctx;
    const { name, email, imageUrl } = args;

    // Insert the guest data into the "guests" collection
    await db.insert("guests", {
      name,
      email,
      imageUrl,
    });

    // Optionally, you can return some confirmation or the inserted document ID
    return { success: true };
  },
});


// export const getGuestImage = query({
//   args: { taskId: v.id("tasks") },
//   handler: async (ctx, args) => {
//     const task = await ctx.db.get(args.taskId);
//     // do something with `task`
//   },
// });