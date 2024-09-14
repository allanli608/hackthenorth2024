// convex/schema.ts

import { defineSchema, defineTable} from 'convex/server';
import { v } from "convex/values";


export default defineSchema({
  guests: defineTable({
    name: v.string(),
    email: v.string(),
    imageUrl: v.string(),
  }),
});
