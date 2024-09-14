// convex/http/updateGuest.ts

import { httpAction } from "../_generated/server";
import { HttpRouter } from "convex/server";
import { api } from "../_generated/api.js";

/**
 * HTTP endpoint to update the Convex database with new guest data.
 */
export default httpAction(async (ctx, request) => {
   // Parse the JSON body
  const { name, email, imageUrl, token } = await request.json();

  // Verify the token
  const expectedToken = "YOUR_SECURE_TOKEN"; // Replace with your secure token
  if (token !== expectedToken) {
    return new Response("Unauthorized", { status: 401 });
  }

  // Call the mutation to insert the guest data
  await ctx.runMutation(api.guests.storeGuest, {
    name,
    email,
    imageUrl,
  });

  // Return a success response
  return new Response(JSON.stringify({ success: true }), {
    headers: { "Content-Type": "application/json" },
  });
});
