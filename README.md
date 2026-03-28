# Invitation Automation System

A Flask web application for creating personalized PDF invitations from a template and an Excel contact list.

## Features
- **Personalized PDFs**: Automatically place names on your invitation template.
- **Excel Template**: Download a demo Excel file to see the required format.
- **ZIP Download**: Download all generated PDFs in a single ZIP file.
- **Admin Logs**: Monitor system usage and print counts at `/admin/logs`.

## How to Run

### 1. Install Dependencies
Make sure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Start the Application
Run the main application script:
```bash
python app.py
```

### 3. Open in Browser
Open your browser and navigate to:
`http://localhost:5000`

## Usage Instructions
1. **Upload Files**: Upload your PDF invitation template and your Excel contact list.
2. **Position Name**: Click on the PDF preview to set where you want the names to appear.
3. **Adjust Style**: Use the sidebar to change font size, color, and family.
4. **Generate**: Click "Generate PDFs" to create personalized invitations.
5. **Download**: Click the download button to get all invitations in a ZIP file.

## Admin Access
To view system usage logs and statistics:
`http://localhost:5000/admin/logs`
