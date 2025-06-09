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

app = Flask(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
TOKEN_FILE = 'token.json'
REDIRECT_URI = 'http://localhost:5000/callback'
ATTACHMENT_PATHS = []  # Store multiple attachment paths
ORIGINAL_FILENAMES = []  # Store original filenames

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

def create_message_with_attachment(to, subject, body, attachment_paths, original_filenames, signature):
    """Create email message with attachments using original filenames."""
    try:
        # Create multipart message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message['from'] = 'your_email@gmail.com'  # Replace with your Gmail address

        # Append the signature to the body with a double newline separator
        full_body = f"{body}\n\n{signature}" if signature else body
        
        # Convert plain text body to HTML for proper formatting in Gmail
        html_body = full_body.replace('\n', '<br>')  # Fixed: Use full_body instead of body
        html_body = f'<html><body>{html_body}</body></html>'

        # Add HTML body to email
        message.attach(MIMEText(html_body, 'html'))

        # Add attachments if they exist
        for attachment_path, original_filename in zip(attachment_paths, original_filenames):
            if os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                # Use original filename in the attachment header
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{original_filename}"'  # Fixed: Proper quotes around filename
                )
                message.attach(part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    
    except Exception as e:
        raise Exception(f"Error creating message: {str(e)}")

def create_draft_with_attachment(service, to, subject, body, signature):
    """Create a draft email with attachments."""
    try:
        # Create message with attachments using original filenames
        message = create_message_with_attachment(to, subject, body, ATTACHMENT_PATHS, ORIGINAL_FILENAMES, signature)
        
        # Create draft
        draft_body = {'message': message}
        result = service.users().drafts().create(userId='me', body=draft_body).execute()
        
        return {
            'status': 'success', 
            'message': f'✅ Draft created for {to} with {len(ORIGINAL_FILENAMES)} attachment(s): {", ".join(ORIGINAL_FILENAMES)} - Draft ID: {result["id"]}'  # Fixed: Improved string formatting
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

@app.route("/upload_attachment", methods=["POST"])
def upload_attachment():
    """Upload multiple attachment files with original filenames preserved."""
    global ATTACHMENT_PATHS, ORIGINAL_FILENAMES

    try:
        ATTACHMENT_PATHS = []
        ORIGINAL_FILENAMES = []

        files = request.files.getlist("attachments")
        if not files or all(file.filename == "" for file in files):
            return jsonify({
                "status": "error",
                "message": "No attachment files selected",
            }), 400

        allowed_extensions = {".pdf", ".doc", ".docx", ".txt", ".jpg", ".png"}
        for file in files:
            if file.filename == "":
                continue
            original_filename = file.filename
            if not any(original_filename.lower().endswith(ext) for ext in allowed_extensions):
                return jsonify({
                    "status": "error",
                    "message": (
                        f'File "{original_filename}" must be one of: '
                        f'{", ".join(allowed_extensions)}'
                    ),
                }), 400

            safe_filename = os.path.basename(original_filename)
            attachment_path = f"attachments/{safe_filename}"
            os.makedirs("attachments", exist_ok=True)
            file.save(attachment_path)

            ATTACHMENT_PATHS.append(attachment_path)
            ORIGINAL_FILENAMES.append(original_filename)

        return jsonify({
            "status": "success",
            "message": (
                f"{len(ORIGINAL_FILENAMES)} attachment(s) uploaded successfully: "
                f'{", ".join(ORIGINAL_FILENAMES)}'
            ),
            "filenames": ORIGINAL_FILENAMES,
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/preview_emails", methods=["POST"])
def preview_emails():
    """
    Generate a preview of emails by replacing placeholders in the template.

    Returns:
        JSON response with a list of previews (email, subject, body) for each recipient.
    """
    try:
        file = request.files["excel_file"]
        template = request.form["template"]
        signature = request.form.get("signature", "")  # Fixed: Retrieve signature

        if not file:
            return jsonify({
                "status": "error",
                "message": "No Excel file uploaded",
            }), 400

        # Read Excel file
        df = pd.read_excel(file, engine="openpyxl")
        required_columns = ["email", "company_name", "subject"]
        if not all(col in df.columns for col in required_columns):
            return jsonify({
                "status": "error",
                "message": "Excel file must contain: email, company_name, subject columns",
            }), 400

        previews = []
        for index, row in df.iterrows():
            email = row["email"]
            company_name = row["company_name"]
            subject = row["subject"]
            body = template.format(company_name=company_name)
            
            # Append the signature to the body with a double newline separator
            full_body = f"{body}\n\n{signature}" if signature else body
            
            previews.append({
                "email": email,
                "subject": subject,
                "body": full_body,  # Fixed: Use full_body to include signature
            })

        return jsonify({
            "status": "success",
            "previews": previews,
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/create_drafts', methods=['POST'])
def create_drafts():
    """Process Excel file and create draft emails with multiple attachments."""
    try:
        service = authenticate_gmail()
        file = request.files['excel_file']
        template = request.form['template']
        signature = request.form.get("signature", "")
        
        if not file:
            return jsonify({'status': 'error', 'message': 'No Excel file uploaded'}), 400

        # Check if attachment exists
        if not ATTACHMENT_PATHS or not all(os.path.exists(path) for path in ATTACHMENT_PATHS):
            return jsonify({'status': 'error', 'message': 'Please upload at least one attachment first'}), 400

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
            result = create_draft_with_attachment(service, email, subject, body, signature)
            results.append(result)

        success_count = len([r for r in results if r['status'] == 'success'])
        error_count = len([r for r in results if r['status'] == 'error'])

        return jsonify({
            'status': 'success', 
            'results': results,
            'summary': f'Created {success_count} drafts with {len(ORIGINAL_FILENAMES)} attachment(s): {", ".join(ORIGINAL_FILENAMES)}! {error_count} failed. Check Gmail Drafts folder.',
            'attachment_names': ORIGINAL_FILENAMES,
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/attachment_info')
def attachment_info():
    """Get current attachment information."""
    return jsonify({
        'filenames': ORIGINAL_FILENAMES,
        'paths': ATTACHMENT_PATHS,
        'exists': all(os.path.exists(path) for path in ATTACHMENT_PATHS) if ATTACHMENT_PATHS else False,
    })

if __name__ == '__main__':
    print("🚀 Email Draft Creator Started!")
    print("📧 Creates draft emails with attachments using original filenames")
    print("⏰ You can schedule them manually in Gmail later")
    app.run(debug=True, port=5000)