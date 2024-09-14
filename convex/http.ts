// convex/http/updateGuest.ts

import { httpAction } from "./_generated/server.js";
import { httpRouter } from "convex/server";
import { api } from "./_generated/api.js";
import { storeGuest, getAllGuestImages } from "./functions.js";


const http = httpRouter();

http.route({
  path: "/guests/images",
  method: "POST",
  handler: storeGuest, // httpActions
});

// Define a route using a path prefix
http.route({
  // Will match /getAuthorMessages/User+123 and /getAuthorMessages/User+234 etc.
  pathPrefix: "/guests/images",
  method: "GET",
  handler: getAllGuestImages,
});

export default http;
