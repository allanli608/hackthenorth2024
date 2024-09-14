// convex/functions.ts

import { internalMutation, mutation, query, internalQuery } from "./_generated/server";
import { v } from "convex/values";
import { Doc } from "./_generated/dataModel";
import { google } from "googleapis";


/**
 * Mutation to add a guest with an image URL to the Convex database.
 */

export const storeGuest = internalMutation({
  // Define the arguments schema using Convex's schema builder `s`
  args: {
    name: v.string(),
    email: v.string(),
    imageUrl: v.string(),
  },
  // The handler function that performs the database operation
  handler: async (ctx, args) => {
    const { name, email, imageUrl } = args;

    // Insert the guest data into the "guests" collection
    const guests = {name, email, imageUrl};
    await ctx.db.insert("guests", guests);
  },
});

const SHEET_ID = '1ihI0L2EgxmN0_8GrVlKnBoKrikL3BOGryokf9j4V8n0'; // Replace with your Google Sheet ID
const RANGE = 'Sheet1!E:E'; // Adjust the range to include the image URL column

// Authentication to Google Sheets API (using a service account)
async function getSheetData() {
  const auth = new google.auth.GoogleAuth({
    keyFile: "htn2024-digital-bouncer-e566e0a9a479.json", // Replace with the path to your Google service account key
    scopes: ["https://www.googleapis.com/auth/spreadsheets.readonly"],
  });

  const sheets = google.sheets({ version: "v4", auth });
  
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SHEET_ID,
    range: RANGE, // Adjust the range to the correct columns
  });

  const rows = response.data.values;
  if (!rows || rows.length === 0) {
    console.log("No data found.");
    return [];
  }

  const imageUrls = rows
    .slice(1)  // Skip the first row
    .map(row => row[0])  // Get the image URL from column E
    .filter(url => url !== undefined && url !== '');  // Filter out empty or undefined values

  return imageUrls;
}


// Convex Query to Store Guest Images
export const getAllGuestImages = internalQuery({
  handler: async (ctx): Promise<Doc<"guests">[]> => {
    // Fetch all guest images from Google Sheets
    const imageUrls = await getSheetData();

    // Now that you have the image URLs, you can insert them into the Convex guests collection
    const guests = await ctx.db.query("guests").collect();
  
  // You can use this opportunity to update or return the guest images
    return guests.map(guest => ({
      ...guest,
      imageUrl: imageUrls[guest._creationTime] || guest.imageUrl, // Assuming you can map based on index or some other field
    }));
  }
});