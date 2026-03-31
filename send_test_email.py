#!/usr/bin/env python3
"""Send a test email via Gmail API"""

import base64
from email.mime.text import MIMEText
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Configuration
PROJECT_ROOT = Path(__file__).parent
TOKEN_FILE = PROJECT_ROOT / "token.json"
CREDENTIALS_FILE = PROJECT_ROOT / "gmail_credentials.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate():
    """Authenticate with Gmail API"""
    creds = None
    
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif CREDENTIALS_FILE.exists():
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def send_email(service, to_email, subject, body):
    """Send an email"""
    message = MIMEText(body)
    message['to'] = to_email
    message['from'] = to_email
    message['subject'] = subject
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    try:
        sent = service.users().messages().send(
            userId='me', 
            body={'raw': raw_message}
        ).execute()
        print(f"✅ Email sent! Message ID: {sent['id']}")
        return sent
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("📧 Sending test email...")
    service = authenticate()
    
    # Send SINGLE test email
    send_email(
        service,
        to_email="a89760059@gmail.com",
        subject="Single File Test - Only One Email",
        body="This is a test email to verify that only ONE reply draft is created.\n\nPlease process this email."
    )
    
    print("\n✅ Done! Wait 35 seconds and check Pending_Approval folder.")
