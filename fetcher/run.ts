import { google } from "googleapis"
import os from 'os';
import fs from 'fs';
import path from 'path';

const drive = google.drive('v3');

async function runSample(fileId: string) {
  // Obtain user credentials to use for the request
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


  return drive.files
    .get({fileId, alt: 'media'}, {responseType: 'stream'})
    .then(res => {
      return new Promise((resolve, reject) => {
        const filePath = path.join(os.tmpdir(), fileId + ".jpg");
        const dest = fs.createWriteStream(filePath);
        console.log('writing to', filePath);

        res.data
          .on('end', () => {
            console.log('Done downloading file to',filePath);
            resolve(filePath);
          }).pipe(dest)
      });
    });
}

console.log('starting')
runSample("1xM_ZwSokKCtZq1FFTAtIijydRYy7MQCH")