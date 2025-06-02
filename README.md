# Email_Automation
Email Automation Tool
A Flask-based web application to automate scheduling emails using the Gmail API. Users can upload an Excel file (.xlsx) with recipient details and schedule personalized emails via Gmail's "Scheduled" tab — even if the browser or server is closed.

✨ Features
📄 Upload Excel file to specify recipients, company names, send times, and subjects

📨 Input a customizable email template with {company_name} placeholder

🔐 Authenticate with Gmail using OAuth 2.0

📅 Schedule emails in Gmail’s “Scheduled” tab for auto-sending

💻 Responsive UI with Bootstrap 5

⚠️ Error handling for invalid files or API issues

🛠 Prerequisites
Python 3.11 or higher

A Google account (e.g., your_email@gmail.com)

Gmail API enabled on Google Cloud Project

Internet connection

🔧 Setup Instructions
Step 1: Clone/Create Project Directory
Create a folder (e.g., C:\Mail Automation) and add these files:

pgsql
Copy
Edit
Mail Automation/
├── credentials.json
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── script.js
Step 2: Set Up Gmail API
Create Google Cloud Project
Go to Google Cloud Console

Click the project dropdown → New Project

Name it e.g., EmailAutomationTool → Click Create

Enable Gmail API
Navigate to APIs & Services > Library

Search “Gmail API” → Click Enable

Configure OAuth Consent Screen
Go to APIs & Services > OAuth consent screen

Select External → Click Create

Fill in:

App Name: Email Automation Tool

Support Email: Your Gmail

Developer Email: Your Gmail

Click Save and Continue

Add scope: ../auth/gmail.compose

Add your Gmail as a Test user → Click Save

Create OAuth Credentials
Go to APIs & Services > Credentials

Click Create Credentials > OAuth 2.0 Client ID

Select Desktop App → Name it e.g., Email Automation Desktop Client

Click Create

Under Authorized redirect URIs, add:

bash
Copy
Edit
http://localhost:5000/callback
Download credentials as credentials.json and place in the project directory

Step 3: Install Dependencies
In the project directory terminal, run:

bash
Copy
Edit
pip install flask google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas openpyxl
Step 4: Configure app.py
Replace 'your_email@gmail.com' in create_scheduled_draft with your Gmail

Confirm REDIRECT_URI is set to:

bash
Copy
Edit
http://localhost:5000/callback
🚀 Usage Instructions
1. Run the Flask App
bash
Copy
Edit
python app.py
Open in browser: http://localhost:5000

2. Authenticate with Gmail
Click Authenticate with Gmail

Log in and authorize

token.json will be created

3. Prepare Excel File
Create companies.xlsx with columns:

email	company_name	send_time	subject
hiring@companyA.com	Company A	2025-06-03 14:30	Application for Software Engineer at Company A
careers@companyB.com	Company B	2025-06-03 15:00	Application for Data Scientist at Company B
...	...	...	...

send_time: Format must be YYYY-MM-DD HH:MM (IST)

4. Schedule Emails
Upload companies.xlsx

Customize email template with {company_name}

Click Schedule Emails

You'll see:

sql
Copy
Edit
Emails scheduled successfully! Check Gmail’s ‘Scheduled’ tab.
5. Verify in Gmail
Go to Gmail → Scheduled tab
Check scheduled emails with correct subjects and times

🛠 Troubleshooting
🔑 Authentication Errors
Ensure your Gmail is added as a test user

Delete token.json and re-authenticate

Verify credentials.json and REDIRECT_URI are correct

🔐 InsecureTransportError
Ensure REDIRECT_URI is http://localhost:5000/callback

Confirm Flask is running on port 5000

📊 Excel File Issues
Columns must be: email, company_name, send_time, subject

Use future send times (IST)

📉 API Quotas
Gmail API free tier supports 10–100 emails/day

Monitor usage in Google Cloud Console

🧾 Flask Console Errors
Check terminal output for error messages

📌 Notes
Replace Email: Update 'your_email@gmail.com' in app.py

Time Zone: Use IST for send times

No Subscription: Gmail API is free (within limits)

Security: Do not share credentials.json or token.json

Testing Mode: No Google verification required
