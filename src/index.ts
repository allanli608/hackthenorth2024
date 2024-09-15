import { GoogleSpreadsheet } from 'google-spreadsheet';
import { JWT } from 'google-auth-library';

const creds = {
    "type": "service_account",
    "project_id": "htn2024-digital-bouncer",
    "private_key_id": "e4898f71e5c424cd31813dded1d0c2b4265398ae",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC+DTKvzwTu0T7X\nI2wwV4Z2aiJsscD9EI0LoGQb+3Z89VR4s5qeC3cZxHxfpdtM1mAPMWX8/cA8W8C7\nhDVrgL0VPEq7b92lPMQMokCZGjBM2YU8WmoT7lGcaSrAdaE69+FCJVElKPwnvJFH\nZkr2ZEUGTtbh4JbzMREUw5K3SmNfkI2b1ieEr2qBmkSWpWexJcIlF2wM2sgiIg94\n+XL1yRkL3bwi9FUdrygxIA748n23LdPTpwxc/lcyBieXagZh+uFh6Th64Ijt3Yan\n5rTohsxM99zs2FiU5gPax8+jWz0hJbyputj21RqGvySqEkwErGTrxxNf82AyChGz\n0FOUTC8LAgMBAAECggEAF3FhUzZiEWNWMQt5iO0C9RBadrXmbFDiVRDPyHPYRcmt\nRcZByET5x//op5O53VyENNuPDQnv8IIQ4BCK1lvm9vuc7En8OSmptTU+aqREWPZr\n7OnqM9Mt1fFTCLJ51OBGtPYNcFwB3pTwBrKjhIkRyplnAC3H8O+Yf8swCdPvNhZU\nEplomTF+l8wQANV6FHKSA+CeaH9MxbVEzt8meqP3EBSyxcsxhWYCrp4yReSgvBrk\nhThvmdawSo26Vi9wH3ggknxOX9jK6yhus/F+qd8uJDWw1I4AZrJpFW8Ng1GsJ6uU\noZXty+ngWGlhA6OZKj83i4li9RbRNfSIQGyf1+v4YQKBgQDtC6kTfuEjEvbmnpRv\nllEqigNA/YaD1dFVJil/zjzE6/M6gVWObhWhNEMTtJa/MDApIm2voFb68kpNAWYo\nBvaUBCd+yZDHgWAklG4/+grAvu1peH7NoderHm/YawjZNysoFRrFoPcnZf8wIrUY\nZqilzjZeWoek1SCHwR2aO1VQTwKBgQDNP5EsQstfVPd7dGjJLQzh4i8TlzEjldiQ\npQW95XnH5kns14T1B0UpnLFg+uyyuUposZLkVBQaNu38qbgsazj+3/IWB7oSHTcF\nuMTBlkOMxwwxAiFl0CH8xzuf/vdUzDhCVbdGlBKCciTdsii8G+mYhUdJRfdgQ0UN\nJdhWJcuqhQKBgQDOCJuN0XNYLAykSOOV1d54jfrkCzhW8IsBaqkZaCXTt43ypSW7\nJZ3xPt6qiwWX6geCSWVzCHdxqRTBt9yWH+9EmhPGFOadMatiQA1P2EJuY8UxLkVw\n8CHnnw3x2p6XRmdhcG6TpiQMf4/9w70KF3iwnPsOqbtKnuCmfkj/nGC76wKBgBYr\ngpvcTylp/R15soPgeN7BVsJv91/XpL/jA17CtcfQ6TVLBlKNSXw4L7TBBeY8O3xZ\niftd1ZoLSuOa1Yj+v/ZP7E9S4FdqjnHwxlf+yicfrQJyL3dW5wTt5FPg74haUs1f\ngt99yQ4MFE1aHCpNfYr7Ans4soLUYVYNO3P6uygdAoGBAJm+CEfXcfuLvRc1u5qn\nuRwF8ywXOUej+BGwt1mH2q/9uESUzZEtXs+dMaR9EL6/3cu/wwr20YS26PjUOoRb\ny0y52SPBfsCbcZDewtmjdjgYxGyGhSkSs7oHTPe1A++erQeANQONiRqqUSzPsj4Z\nh8IzgC02Mc+MzOx/Eg5ThNES\n-----END PRIVATE KEY-----\n",
    "client_email": "digital-bouncer@htn2024-digital-bouncer.iam.gserviceaccount.com",
    "client_id": "111439126704886746720",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/digital-bouncer%40htn2024-digital-bouncer.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
  }
  
  
const SCOPES = [
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.file',
];

const jwt = new JWT({
  email: creds.client_email,
  key: creds.private_key,
  scopes: SCOPES,
});

const fetchRows = async () => {
    const doc = new GoogleSpreadsheet('1ihI0L2EgxmN0_8GrVlKnBoKrikL3BOGryokf9j4V8n0', jwt);
    await doc.loadInfo(); // loads document properties and worksheets
    const sheet = doc.sheetsByIndex[0];
    const rows = await sheet.getRows();
    console.log(rows);

}

fetchRows();

// await doc.updateProperties({ title: 'renamed doc' });

// const sheet = doc.sheetsByIndex[0]; // or use `doc.sheetsById[id]` or `doc.sheetsByTitle[title]`
// console.log(sheet.title);
// console.log(sheet.rowCount);

// // adding / removing sheets
// const newSheet = await doc.addSheet({ title: 'another sheet' });
// await newSheet.delete();