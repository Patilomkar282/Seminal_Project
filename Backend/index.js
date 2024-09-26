const express = require('express');
const multer = require('multer');
const { google } = require('googleapis');
const fs = require('fs');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path'); // Import path module

const app = express();
const port = 5000;

app.use(cors({
    origin: 'http://localhost:3000', // React app URL
    methods: 'GET,POST,PUT,DELETE,OPTIONS',
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true, // If your requests require credentials
}));

const upload = multer({ dest: 'uploads/' }); // Store temporarily in uploads

app.post('/upload', upload.single('file'), async (req, res) => {
    const file = req.file;

    if (!file) {
        return res.status(400).send('No file uploaded.');
    }

    // Run the Python script to check for suspicious content
    
    const pythonScriptPath = path.join(__dirname, '../ML_Model/Machine_Learning_Model/checkfile.py'); // Ensure this points to your Python script
   // console.log(`Python script path: ${pythonScriptPath}`);
    exec(`python "${pythonScriptPath}" "${file.path}"`, (error, stdout, stderr) => {
      if (error) {
          console.error(`Error executing Python script: ${stderr}`);
          return res.status(500).send('Error checking file for suspicious content.');
      }
      console.log(`Python script output: ${stdout}`);
  
      // Check if the output is "True" or "False"
      const isSuspicious = stdout.trim() === 'True'; // If model returns 'True', file is suspicious
      

  
      if (isSuspicious) {
          // If the file is suspicious, return an error response
          console.log('Suspicious file detected. Upload aborted.');
          return res.status(400).send('The file contains suspicious content and cannot be uploaded.');
      } else {
          // If the model returns 'False', the file is not suspicious; proceed with upload
          console.log('File is safe. Proceeding to upload.');
  
          // Google Drive authentication
          const auth = new google.auth.GoogleAuth({
              keyFile: path.join(__dirname, 'config', 'Credential.json'),
              scopes: ['https://www.googleapis.com/auth/drive.file'],
          });
  
          const drive = google.drive({ version: 'v3', auth });
  
          // Upload file to Google Drive
          const fileMetadata = {
              name: file.originalname,
          };
          const media = {
              mimeType: file.mimetype,
              body: fs.createReadStream(file.path), // Read the uploaded file
          };
  
          // Upload to Google Drive
          drive.files.create({
              resource: fileMetadata,
              media: media,
              fields: 'id',
          }).then(async (response) => {
              await drive.permissions.create({
                  fileId: response.data.id,
                  requestBody: {
                      role: 'reader',
                      type: 'user',
                      emailAddress: 'Patilomkar2820@gmail.com',
                  },
              });
              console.log(`File shared with your email: Patilomkar2820@gmail.com`);
  
              // Clean up the local file after upload
              fs.unlinkSync(file.path); // Remove file from local uploads
  
              res.status(200).send(`File uploaded successfully to Google Drive: ${response.data.id}`);
          }).catch(error => {
              console.error('Error uploading to Google Drive:', error);
              res.status(500).send('Error uploading file to Google Drive.');
          });
      }
  });

});
  

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

