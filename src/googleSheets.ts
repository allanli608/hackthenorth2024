// src/googleSheets.ts

import { google } from 'googleapis';
import { GoogleAuth } from 'google-auth-library';

const KEYFILEPATH = 'path/to/your-service-account-key.json'; // Update this path
const SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly'];
const SPREADSHEET_ID = 'your_spreadsheet_id'; // Replace with your Google Sheets ID
const RANGE = 'Sheet1!A:E'; // Adjust range according to your sheet

const sheets = google.sheets({ version: 'v4', auth: new GoogleAuth({
  keyFile: KEYFILEPATH,
  scopes: SCOPES,
}) });

export async function getSheetData(): Promise<any[][]> {
  try {
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: RANGE,
    });
    return response.data.values || [];
  } catch (error) {
    console.error('Error fetching data from Google Sheets:', error);
    throw error;
  }
}
