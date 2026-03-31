#!/usr/bin/env python3
"""
Gmail Auto Sender
Sends approved emails and moves them to /Done

Flow:
1. Watch /Approved for approved email drafts
2. Send email via Gmail API
3. Move to /Done after sending
4. Log activity
"""

import os
import sys
import time
import json
import base64
from datetime import datetime
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("⚠️  Gmail libraries not installed. Install with: pip install -r requirements.txt")

# Configuration
VAULT_DIR = Path(__file__).parent.parent / "AI_Employee_Vault"
APPROVED_DIR = VAULT_DIR / "Approved"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = VAULT_DIR / "Logs"

# Ensure directories exist
for dir_path in [APPROVED_DIR, DONE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Gmail OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Credentials are in project root (same folder as gmail_credentials.json)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TOKEN_FILE = PROJECT_ROOT / "token.json"
CREDENTIALS_FILE = PROJECT_ROOT / "gmail_credentials.json"


def log_message(message: str):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"

    try:
        print(log_line)
    except UnicodeEncodeError:
        print(log_line.encode('cp1252', errors='replace').decode('cp1252'))

    log_file = LOGS_DIR / f"gmail_sender_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{log_line}")


def get_gmail_service():
    """Authenticate and get Gmail service"""
    if not GMAIL_AVAILABLE:
        return None

    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif CREDENTIALS_FILE.exists():
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            log_message("❌ Gmail credentials not found. Run Gmail auth first.")
            return None

        # Save token
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def read_email_file(filepath):
    """Read approved email draft file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()

            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def create_email_message(to_email: str, subject: str, body: str) -> str:
    """Create RFC 2822 email message"""
    from_email = "me@gmail.com"  # Will be replaced by Gmail

    message = f"""From: {from_email}
To: {to_email}
Subject: {subject}
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"

{body}
"""
    return base64.urlsafe_b64encode(message.encode('utf-8')).decode('utf-8')


def send_email(service, to_email: str, subject: str, body: str) -> bool:
    """Send email via Gmail API"""
    try:
        message = create_email_message(to_email, subject, body)

        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': message}
        ).execute()

        log_message(f"✅ Email sent to: {to_email}")
        log_message(f"   Message ID: {sent_message['id']}")
        return True

    except Exception as e:
        log_message(f"❌ Error sending email: {e}")
        return False


def move_to_done(filepath: Path) -> bool:
    """Move processed email to Done folder"""
    try:
        dest = DONE_DIR / filepath.name
        filepath.rename(dest)
        log_message(f"📁 Moved to Done: {filepath.name}")
        return True
    except Exception as e:
        log_message(f"❌ Error moving file: {e}")
        return False


def move_original_email_to_done(reply_filename: str) -> bool:
    """Move the original email file (EMAIL_*.md) to Done folder after reply is sent"""
    try:
        # Look for original email file in Approved folder
        # Pattern: EMAIL_REPLY_*.md corresponds to EMAIL_*.md
        original_files = list(APPROVED_DIR.glob("EMAIL_*.md"))
        original_files = [f for f in original_files if not f.name.startswith("EMAIL_REPLY_")]
        
        for orig_file in original_files:
            # Move original email to Done
            dest = DONE_DIR / orig_file.name
            orig_file.rename(dest)
            log_message(f"📁 Moved original email to Done: {orig_file.name}")
            return True
        return False
    except Exception as e:
        log_message(f"❌ Error moving original email: {e}")
        return False


def process_approved_emails():
    """Process all approved emails in /Approved folder"""
    if not APPROVED_DIR.exists():
        return 0

    # Find all email files
    email_files = list(APPROVED_DIR.glob("EMAIL_*.md"))

    if not email_files:
        return 0

    log_message(f"📧 Found {len(email_files)} approved emails to send")

    # Get Gmail service
    service = get_gmail_service()
    sent_count = 0

    for email_file in email_files:
        log_message(f"\n📮 Processing: {email_file.name}")

        try:
            # Read email
            frontmatter, body = read_email_file(email_file)

            # Extract recipient and subject
            to_email = frontmatter.get('to', '')
            subject = frontmatter.get('subject', 'No Subject')

            # Extract reply content from body
            reply_body = body
            if "## Reply Content" in body:
                reply_body = body.split("## Reply Content")[1].strip()
            elif "## Email Reply" in body:
                reply_body = body.split("## Email Reply")[1].strip()

            if not to_email:
                log_message(f"⚠️  Skipping {email_file.name} - no recipient")
                continue

            # Send email
            if service:
                success = send_email(service, to_email, subject, reply_body)
                if success:
                    # Move reply draft to Done
                    move_to_done(email_file)
                    sent_count += 1
            else:
                log_message("⚠️  Gmail service not available, just moving to Done")
                move_to_done(email_file)
                sent_count += 1

        except Exception as e:
            log_message(f"❌ Error processing {email_file.name}: {e}")

    return sent_count


def run_auto_sender():
    """Main auto sender loop"""
    log_message("🚀 Starting Gmail Auto Sender...")
    log_message(f"📁 Watching: {APPROVED_DIR}")
    log_message(f"📤 Output: {DONE_DIR}")

    while True:
        # Process approved emails
        sent = process_approved_emails()

        if sent > 0:
            log_message(f"✨ Sent {sent} emails")

        # Wait for next check (every 30 seconds)
        time.sleep(30)


if __name__ == "__main__":
    try:
        # Run once if called with --once
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            count = process_approved_emails()
            log_message(f"✅ Processed {count} emails")
        else:
            run_auto_sender()
    except KeyboardInterrupt:
        log_message("\n👋 Auto Sender stopped by user")
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        sys.exit(1)
