# Email Automation Tool

This is a Flask-based web application that automates creating email drafts via the Gmail API. Users can upload an Excel file (.xlsx) containing recipient details (email, company_name, send_time, subject), provide an email template with a {company_name} placeholder, and optionally add a signature. The tool creates email drafts in Gmail's "Drafts" tab, which users can then manually schedule or send at the specified send_time using Gmail's interface. Additional features include email validation, previewing emails, and attaching multiple files.

## Features

* **Upload an Excel File**: Specify email recipients, company names, send times, and subjects in an Excel file.
* **Customizable Email Template**: Input an email template with a {company_name} placeholder for personalization.
* **Email Signature Support**: Add a custom signature to emails, appended with proper formatting.
* **Email Validation**: Validate email addresses in the Excel file, flagging invalid ones with row numbers.
* **Email Template Preview**: Preview emails with the template, signature, and recipient details before creating drafts.
* **Support for Multiple Attachments**: Attach multiple files (e.g., PDFs, Word docs) to email drafts, preserving original filenames.
* **Gmail Authentication**: Authenticate with Gmail using OAuth 2.0.
* **Create Email Drafts**: Create email drafts in Gmail's "Drafts" tab for manual sending or scheduling.
* **Responsive Web Interface**: Built with Bootstrap 5 for an attractive and responsive UI.
* **Error Handling**: Comprehensive error handling for invalid Excel files, API issues, and invalid email addresses.

## Prerequisites

* Python 3.11 or higher.
* A Google account (e.g., your_email@gmail.com) for Gmail API access.
* A Google Cloud project with the Gmail API enabled and OAuth 2.0 credentials.
* Internet connection for API calls and Bootstrap CDN.

## Setup Instructions

### Step 1: Clone or Create Project Directory

Create a project directory (e.g., C:\Mail Automation).

Place the following files in the directory:

* app.py: Flask backend.
* templates/index.html: Web interface.
* static/script.js: Client-side JavaScript.

Ensure the directory structure is:

```
Mail Automation/
├── credentials.json
├── token.json (generated after authentication)
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── script.js
├── attachments/ (created automatically for uploaded files)
```

### Step 2: Set Up Gmail API

#### Create a Google Cloud Project:

* Go to Google Cloud Console.
* Sign in with your Gmail account.
* Click the project dropdown and select New Project.
* Name it (e.g., EmailAutomationTool) and click Create.

#### Enable Gmail API:

* Navigate to APIs & Services > Library.
* Search for Gmail API and click Enable.

#### Configure OAuth Consent Screen:

* Go to APIs & Services > OAuth consent screen.
* Select External and click Create.
* Fill in:
  * App Name: Email Automation Tool
  * User Support Email: Your Gmail address
  * Developer Contact: Your Gmail address
* Click Save and Continue.
* Add the scope ../auth/gmail.compose (search and check the box).
* Click Update, then Save and Continue.
* Add your Gmail address as a test user and save.

#### Create OAuth 2.0 Credentials:

* Go to APIs & Services > Credentials.
* Click Create Credentials > OAuth 2.0 Client IDs.
* Select Desktop app, name it (e.g., Email Automation Desktop Client), and click Create.
* Add http://localhost:5000/callback under Authorized redirect URIs and save.
* Download the credentials as credentials.json and place it in the project directory.

### Step 3: Install Dependencies

Open a terminal in the project directory and install the required Python packages:

```bash
pip install flask pandas openpyxl google-auth-oauthlib google-api-python-client
```

### Step 4: Configure app.py

* Open app.py and replace 'your_email@gmail.com' in the create_message_with_attachment function with your actual Gmail address.
* Ensure the REDIRECT_URI is set to http://localhost:5000/callback.

## Usage Instructions

### Run the Flask Server

Start the Flask server:

```bash
python app.py
```

The server starts at http://localhost:5000.

### Authenticate with Gmail

* Open http://localhost:5000 in a browser.
* Click "Authenticate with Gmail."
* Sign in with your Gmail account (must be a test user) and authorize the app.
* You'll be redirected to the interface, and token.json will be created in the project directory.

### Prepare Excel File

Create an Excel file (e.g., companies.xlsx) with the following columns:

* email: Recipient's email (e.g., hiring@companyA.com).
* company_name: Company name (e.g., Company A).
* send_time: Intended send time in YYYY-MM-DD HH:MM format (e.g., 2025-06-16 14:30), for reference when manually scheduling in Gmail.
* subject: Email subject (e.g., Application for Software Engineer at Company A).

#### Example (5 entries):

| email | company_name | send_time | subject |
|-------|-------------|-----------|---------|
| hiring@companyA.com | Company A | 2025-06-16 14:30 | Application for Software Engineer at A |
| careers@companyB.com | Company B | 2025-06-16 15:00 | Application for Data Scientist at B |
| invalid-email | Company C | 2025-06-16 15:30 | Application for Product Manager at C |
| jobs@companyD.com | Company D | 2025-06-16 16:00 | Application for DevOps Engineer at D |
| hr@companyE.com | Company E | 2025-06-16 16:30 | Application for UX Designer at E |

Save the file in a known location.

### Upload Attachments (Optional)

* In the web interface, under "Upload Attachments," select files (e.g., resume.pdf, cover_letter.docx).
* Click "Upload Attachments."
* Supported formats: .pdf, .doc, .docx, .txt, .jpg, .png.
* Verify the attachments are listed in the "Current Attachment(s)" section.

### Preview Emails

* Upload the Excel file (companies.xlsx).
* Modify the email template (e.g., "Dear Hiring Manager at {company_name},\n\nI am applying for the position...").
* Add a signature if desired (e.g., "Best regards,\nJohn Doe\n+91 9876543210\njohn.doe@example.com").
* Click "Preview Emails."

#### Expected Behavior:

* If any email addresses are invalid (e.g., invalid-email), an error message will appear: "Invalid email addresses found: Row 3: invalid-email".
* If all emails are valid, a modal will display the preview with recipient details, subject, body, and signature.

### Create Email Drafts

* Ensure all email addresses are valid (fix any invalid ones based on the preview feedback).
* Click "Create Email Drafts with Attachments."

#### Expected Behavior:

* If any email addresses are invalid, they will be skipped, and the success message will list them (e.g., "Invalid Emails: Row 3: invalid-email").
* For valid emails, a success message will appear: "Created X drafts with Y attachment(s): resume.pdf, cover_letter.docx! Z failed. Check Gmail Drafts folder."

### Verify in Gmail

* Open Gmail and go to the "Drafts" tab (left sidebar).
* Confirm the drafts (e.g., 4 for the example file, excluding the invalid email).

To send or schedule, open each draft:

* To send immediately, click "Send."
* To schedule, click the dropdown next to the "Send" button, select "Schedule send," and set the time to match the send_time from the Excel file (e.g., 2025-06-16 14:30).

## Troubleshooting

### Authentication Errors

* Ensure your Gmail account is a test user in OAuth consent screen > Test users.
* Delete token.json and re-authenticate if issues persist.
* Verify credentials.json matches the project and includes http://localhost:5000/callback as a redirect URI.

### InsecureTransportError

* Confirm the redirect URI in Google Cloud Console and app.py is http://localhost:5000/callback.
* Ensure Flask runs on port 5000 (check for port conflicts).

### Excel File Issues

* Verify companies.xlsx has columns: email, company_name, send_time (YYYY-MM-DD HH:MM), and subject.
* Use future send times (relative to current IST time).
* Ensure email addresses are valid (e.g., user@domain.com). Invalid emails will be flagged with row numbers.

### API Quotas

* The Gmail API free tier supports 10–100 emails. Monitor usage in Google Cloud Console if scaling up.

### Flask Console Errors

* Check the terminal for detailed error messages and share them for debugging.

## Notes

* Replace Email: Update 'your_email@gmail.com' in app.py with your Gmail address.
* Time Zone: Use IST for send_time (e.g., 2025-06-16 14:30) in the Excel file. If scheduling in Gmail, it converts to UTC internally.
* Draft Creation: The current implementation creates drafts in Gmail. To send or schedule emails, you must manually handle each draft in Gmail. A future update may add direct scheduling via the Gmail API.
* No Subscription: Gmail API is free for personal use within quota limits.
* Security: Keep credentials.json and token.json secure. Do not share or upload to public repositories.
