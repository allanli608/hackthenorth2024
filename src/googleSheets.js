"use strict";
// src/googleSheets.ts
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSheetData = getSheetData;
const googleapis_1 = require("googleapis");
const google_auth_library_1 = require("google-auth-library");
const KEYFILEPATH = 'path/to/your-service-account-key.json'; // Update this path
const SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly'];
const SPREADSHEET_ID = 'your_spreadsheet_id'; // Replace with your Google Sheets ID
const RANGE = 'Sheet1!A:E'; // Adjust range according to your sheet
const sheets = googleapis_1.google.sheets({ version: 'v4', auth: new google_auth_library_1.GoogleAuth({
        keyFile: KEYFILEPATH,
        scopes: SCOPES,
    }) });
function getSheetData() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const response = yield sheets.spreadsheets.values.get({
                spreadsheetId: SPREADSHEET_ID,
                range: RANGE,
            });
            return response.data.values || [];
        }
        catch (error) {
            console.error('Error fetching data from Google Sheets:', error);
            throw error;
        }
    });
}
