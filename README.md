# Email Automation Tool

This is a Flask-based web application that automates scheduling emails via the Gmail API. Users can upload an Excel file (`.xlsx`) containing recipient details (`email`, `company_name`, `send_time`, `subject`) and provide an email template with a `{company_name}` placeholder. The tool schedules emails in Gmail’s “Scheduled” tab, allowing them to be sent automatically at specified times, even if the browser or server is closed.

---

## Features

- Upload an Excel file to specify email recipients, company names, send times, and subjects.
- Input a customizable email template with `{company_name}` for personalization.
- Authenticate with Gmail using OAuth 2.0.
- Schedule emails as drafts in Gmail’s “Scheduled” tab for automatic sending.
- Responsive, attractive web interface using Bootstrap 5.
- Error handling for invalid Excel files or API issues.

---

## Prerequisites

- Python 3.11 or higher.
- A Google account (e.g., `your_email@gmail.com`) for Gmail API access.
- A Google Cloud project with the Gmail API enabled and OAuth 2.0 credentials.
- Internet connection for API calls and Bootstrap CDN.

---

## Setup Instructions

### Step 1: Clone or Create Project Directory

Create a project directory (e.g., `C:\Mail Automation`).

Place the following files in the directory:

- `app.py`: Flask backend
- `templates/index.html`: Web interface
- `static/script.js`: Client-side JavaScript

Ensure the directory structure is:

```
Mail Automation/
├── credentials.json
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── script.js
```

---

### Step 2: Set Up Gmail API

#### Create a Google Cloud Project:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Gmail account.
3. Click the project dropdown and select **New Project**.
4. Name it (e.g., **EmailAutomationTool**) and click **Create**.

#### Enable Gmail API:

1. Navigate to **APIs & Services > Library**.
2. Search for **Gmail API** and click **Enable**.

#### Configure OAuth Consent Screen:

1. Go to **APIs & Services > OAuth consent screen**.
2. Select **External** and click **Create**.
3. Fill in:
   - **App Name**: Email Automation Tool
   - **User Support Email**: Your Gmail address
   - **Developer Contact**: Your Gmail address
4. Click **Save and Continue**.
5. Add the scope `../auth/gmail.compose` (search and check the box).
6. Click **Update**, then **Save and Continue**.
7. Add your Gmail address as a **test user** and save.

#### Create OAuth 2.0 Credentials:

1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth 2.0 Client IDs**.
3. Select **Desktop app**, name it (e.g., Email Automation Desktop Client), and click **Create**.
4. Add `http://localhost:5000/callback` under **Authorized redirect URIs** and save.
5. Download the credentials as `credentials.json` and place it in the project directory.

---

### Step 3: Install Dependencies

Open a terminal in the project directory and install required Python packages:

```bash
pip install flask google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas openpyxl
```

---

### Step 4: Configure `app.py`

- Open `app.py` and replace `'your_email@gmail.com'` in the `create_scheduled_draft` function with your actual Gmail address.
- Ensure the `REDIRECT_URI` is set to `http://localhost:5000/callback`.

---

## Usage Instructions

### Run the Flask Server:

```bash
python app.py
```

The server starts at `http://localhost:5000`.

### Authenticate with Gmail:

1. Open `http://localhost:5000` in a browser.
2. Click “Authenticate with Gmail.”
3. Sign in with your Gmail account (must be a test user) and authorize the app.
4. You’ll be redirected to the interface, and `token.json` will be created.

---

### Prepare Excel File:

Create an Excel file (`companies.xlsx`) with the following columns:

- `email`: Recipient’s email (e.g., `hiring@companyA.com`)
- `company_name`: Company name (e.g., `Company A`)
- `send_time`: Send time in `YYYY-MM-DD HH:MM` format (e.g., `2025-06-03 14:30`)
- `subject`: Email subject (e.g., `Application for Software Engineer at Company A`)

#### Example (10 entries):

| email                | company_name | send_time          | subject                                         |
|----------------------|--------------|--------------------|-------------------------------------------------|
| hiring@companyA.com  | Company A    | 2025-06-03 14:30   | Application for Software Engineer at Company A |
| careers@companyB.com | Company B    | 2025-06-03 15:00   | Application for Data Scientist at Company B    |
| jobs@companyC.com    | Company C    | 2025-06-03 15:30   | Application for Product Manager at Company C   |
| recruit@companyD.com | Company D    | 2025-06-03 16:00   | Application for DevOps Engineer at Company D   |
| hr@companyE.com      | Company E    | 2025-06-03 16:30   | Application for UX Designer at Company E       |
| jobs@companyF.com    | Company F    | 2025-06-04 09:00   | Application for Marketing Manager at Company F |
| careers@companyG.com | Company G    | 2025-06-04 09:30   | Application for AI Researcher at Company G     |
| hiring@companyH.com  | Company H    | 2025-06-04 10:00   | Application for Backend Developer at Company H |
| recruit@companyI.com | Company I    | 2025-06-04 10:30   | Application for Frontend Developer at Company I|
| hr@companyJ.com      | Company J    | 2025-06-04 11:00   | Application for Project Manager at Company J   |

Save the file in a known location.

---

### Schedule Emails:

1. In the web interface, upload `companies.xlsx`.
2. Modify the email template (uses `{company_name}` for personalization).
3. Click “Schedule Emails.”
4. See a success message:  
   **“Emails scheduled successfully! Check Gmail’s ‘Scheduled’ tab.”**  
   with details for each email.

---

### Verify in Gmail:

1. Open Gmail and go to the **“Scheduled”** tab (left sidebar).
2. Confirm scheduled emails (e.g., 10 for the example file) with specified subjects and send times.
3. Gmail sends them automatically at the scheduled times.

---

## Troubleshooting

### Authentication Errors:

- Ensure your Gmail account is a **test user** in **OAuth consent screen > Test users**.
- Delete `token.json` and re-authenticate if issues persist.
- Verify `credentials.json` matches the project and includes `http://localhost:5000/callback` as a redirect URI.

### InsecureTransportError:

- Confirm the redirect URI in **Google Cloud Console** and `app.py` is `http://localhost:5000/callback`.
- Ensure Flask runs on port **5000** (check for port conflicts).

### Excel File Issues:

- Verify `companies.xlsx` has columns: `email`, `company_name`, `send_time` (`YYYY-MM-DD HH:MM`), and `subject`.
- Use **future** send times (relative to current IST time).

### API Quotas:

- The Gmail API free tier supports **10–100 emails**. Monitor usage in Google Cloud Console if scaling up.

### Flask Console Errors:

- Check the terminal for detailed error messages and share them for debugging.

---

## Notes

- **Replace Email**: Update `'your_email@gmail.com'` in `app.py` with your Gmail address.
- **Time Zone**: Use **IST** for `send_time` (e.g., `2025-06-03 14:30`). Gmail API converts it to UTC.
- **No Subscription**: Gmail API is free for personal use within quota limits.
- **Security**: Keep `credentials.json` and `token.json` secure. Do **not** share or upload to public repositories.
- **Testing Mode**: The app is in testing mode, suitable for personal use. Google verification is not required.
