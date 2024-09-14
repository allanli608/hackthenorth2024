import { google } from "googleapis"
import os from 'os';
import fs from 'fs';
import path from 'path';

const auth = new google.auth.GoogleAuth({
    keyFile: path.join(__dirname, '../creds.json'),
    scopes: [
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/drive.appdata',
      'https://www.googleapis.com/auth/drive.file',
      'https://www.googleapis.com/auth/drive.metadata',
      'https://www.googleapis.com/auth/drive.metadata.readonly',
      'https://www.googleapis.com/auth/drive.photos.readonly',
      'https://www.googleapis.com/auth/drive.readonly',
    ],
  });
  google.options({auth});

const drive = google.drive('v3');
const sheets = google.sheets('v4')


async function downloadFile(fileId: string, email: string) {
  return drive.files
    .get({fileId, alt: 'media'}, {responseType: 'stream'})
    .then(res => {
      return new Promise((resolve, reject) => {

        let type = ""
        if (res.headers["content-type"] === "image/jpeg") {
          type = ".jpg"
        } else if (res.headers["content-type"] === "image/png") {
          type = ".png"
        } else {
          console.log(`Unknown type ${res.headers["content-type"]}`)
          return;
        }

        const filePath = path.join("photos", email + type);
        const dest = fs.createWriteStream(filePath);
        res.data
          .on('end', () => {
            console.log('Done downloading file to',filePath);
            resolve(filePath);
          }).pipe(dest)
      });
    });
}

async function loadImages() {
    console.log("fetching....")
    let downloaded = 0;
    const res = await sheets.spreadsheets.values.get(
      {
        auth: auth,
        spreadsheetId: '1ihI0L2EgxmN0_8GrVlKnBoKrikL3BOGryokf9j4V8n0',
        range: 'Form Responses 1!A2:E',
      }
    );
    const rows = res.data.values ?? [];
    for (const row of rows) {
        const email = row[1];
        const imageURL = row[4];
        const imgPath = path.join("photos", email);
        if (!fs.existsSync(imgPath + ".jpg") && !fs.existsSync(imgPath + ".png")) {
            await downloadFile(imageURL.replace("https://drive.google.com/open?id=", ""), email)
            downloaded++;
        } else {
            console.log(`skipping ${email}`);
        }
    }
    console.log(`Downloaded ${downloaded} images`);
    setTimeout(loadImages, 5 * 1000);
  }

  loadImages()

