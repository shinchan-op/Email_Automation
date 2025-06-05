import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for local testing

from flask import Flask, request, jsonify, render_template, redirect, url_for
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import os

app = Flask(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
TOKEN_FILE = 'token.json'
REDIRECT_URI = 'http://localhost:5000/callback'
ATTACHMENT_PATH = None  # Will be set dynamically with original filename
ORIGINAL_FILENAME = None  # Store original filename

def authenticate_gmail():
    """Authenticate with Gmail API and return the service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri=REDIRECT_URI)
        creds = flow.run_local_server(port=5000, open_browser=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_message_with_attachment(to, subject, body, attachment_path, original_filename):
    """Create email message with attachment using original filename."""
    try:
        # Create multipart message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message['from'] = 'your_email@gmail.com'  # Replace with your Gmail address

        # Convert plain text body to HTML for proper formatting in Gmail
        html_body = body.replace('\n', '<br>')
        html_body = f'<html><body>{html_body}</body></html>'

        # Add HTML body to email
        message.attach(MIMEText(html_body, 'html'))

        # Add attachment if file exists
        if os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            # Use original filename in the attachment header
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {original_filename}'
            )
            message.attach(part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    
    except Exception as e:
        raise Exception(f"Error creating message: {str(e)}")

def create_draft_with_attachment(service, to, subject, body):
    """Create a draft email with attachment."""
    try:
        # Create message with attachment using original filename
        message = create_message_with_attachment(to, subject, body, ATTACHMENT_PATH, ORIGINAL_FILENAME)
        
        # Create draft
        draft_body = {'message': message}
        result = service.users().drafts().create(userId='me', body=draft_body).execute()
        
        return {
            'status': 'success', 
            'message': f'✅ Draft created for {to} with attachment "{ORIGINAL_FILENAME}" - Draft ID: {result["id"]}'
        }
        
    except HttpError as error:
        return {
            'status': 'error', 
            'message': f'❌ Error creating draft for {to}: {str(error)}'
        }

@app.route('/')
def index():
    """Render the main web interface."""
    return render_template('index.html')

@app.route('/auth')
def auth():
    """Initiate Gmail authentication."""
    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri=REDIRECT_URI)
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return redirect(authorization_url)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Authentication initialization failed: {str(e)}'}), 500

@app.route('/callback')
def callback():
    """Handle OAuth callback."""
    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri=REDIRECT_URI)
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        return redirect(url_for('index'))
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Authentication callback failed: {str(e)}'}), 500

@app.route('/upload_attachment', methods=['POST'])
def upload_attachment():
    """Upload common attachment file with original filename preserved."""
    global ATTACHMENT_PATH, ORIGINAL_FILENAME
    
    try:
        if 'attachment' not in request.files:
            return jsonify({'status': 'error', 'message': 'No attachment file uploaded'}), 400
        
        file = request.files['attachment']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Store original filename
        ORIGINAL_FILENAME = file.filename
        
        # Create a safe path with original filename
        # Remove any path characters to prevent directory traversal
        safe_filename = os.path.basename(ORIGINAL_FILENAME)
        ATTACHMENT_PATH = f'attachments/{safe_filename}'
        
        # Create attachments directory if it doesn't exist
        os.makedirs('attachments', exist_ok=True)
        
        # Save the attachment with original filename
        file.save(ATTACHMENT_PATH)
        
        return jsonify({
            'status': 'success', 
            'message': f'Attachment "{ORIGINAL_FILENAME}" uploaded successfully',
            'filename': ORIGINAL_FILENAME
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/create_drafts', methods=['POST'])
def create_drafts():
    """Process Excel file and create draft emails with attachments."""
    try:
        service = authenticate_gmail()
        file = request.files['excel_file']
        template = request.form['template']
        
        if not file:
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

        # Check if attachment exists
        if not ATTACHMENT_PATH or not os.path.exists(ATTACHMENT_PATH):
            return jsonify({'status': 'error', 'message': 'Please upload a common attachment first'}), 400

        # Read Excel file - only need email, company_name, subject columns
        df = pd.read_excel(file, engine='openpyxl')
        required_columns = ['email', 'company_name', 'subject']
        if not all(col in df.columns for col in required_columns):
            return jsonify({
                'status': 'error', 
                'message': 'Excel file must contain: email, company_name, subject columns'
            }), 400

        results = []
        
        for index, row in df.iterrows():
            email = row['email']
            company_name = row['company_name']
            subject = row['subject']
            body = template.format(company_name=company_name)
            
            # Create draft immediately
            result = create_draft_with_attachment(service, email, subject, body)
            results.append(result)

        success_count = len([r for r in results if r['status'] == 'success'])
        error_count = len([r for r in results if r['status'] == 'error'])

        return jsonify({
            'status': 'success', 
            'results': results,
            'summary': f'Created {success_count} drafts with attachment "{ORIGINAL_FILENAME}"! {error_count} failed. Check Gmail Drafts folder.',
            'attachment_name': ORIGINAL_FILENAME
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/attachment_info')
def attachment_info():
    """Get current attachment information."""
    return jsonify({
        'filename': ORIGINAL_FILENAME,
        'path': ATTACHMENT_PATH,
        'exists': ATTACHMENT_PATH and os.path.exists(ATTACHMENT_PATH) if ATTACHMENT_PATH else False
    })

if __name__ == '__main__':
    print("🚀 Email Draft Creator Started!")
    print("📧 Creates draft emails with attachments using original filenames")
    print("⏰ You can schedule them manually in Gmail later")
    app.run(debug=True, port=5000)