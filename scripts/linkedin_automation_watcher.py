#!/usr/bin/env python3
"""
LinkedIn Automation Watcher
Monitors email and creates LinkedIn post drafts automatically

Flow:
1. Watch Gmail for new emails
2. Create .md files in /Needs_Action
3. Claude processes and creates LinkedIn drafts in /Pending_Approval
4. User approves by moving to /Approved
5. Ralph Loop publishes via MCP Server
6. Move to /Done
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
INBOX_DIR = VAULT_DIR / "Inbox"
LOGS_DIR = VAULT_DIR / "Logs"

# Ensure directories exist
for dir_path in [NEEDS_ACTION_DIR, INBOX_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Gmail OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = Path(__file__).parent / "email-mcp-server" / "token.json"
CREDENTIALS_FILE = Path(__file__).parent / "email-mcp-server" / "credentials.json"


def log_message(message: str):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    
    # Fix Windows console encoding
    try:
        print(log_line)
    except UnicodeEncodeError:
        print(log_line.encode('cp1252', errors='replace').decode('cp1252'))

    # Append to log file
    log_file = LOGS_DIR / f"linkedin_watcher_{datetime.now().strftime('%Y-%m-%d')}.md"
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


def fetch_recent_emails(service, max_results=10):
    """Fetch recent emails from Gmail"""
    if not service:
        return []
    
    try:
        # Fetch messages from last hour
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q='newer_than:1h'
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            msg_detail = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
            
            emails.append({
                'id': msg['id'],
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'snippet': msg_detail.get('snippet', '')
            })
        
        return emails
    
    except Exception as e:
        log_message(f"❌ Error fetching emails: {e}")
        return []


def get_full_email_body(service, email_id):
    """Get full email body"""
    if not service:
        return ""
    
    try:
        message = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        # Extract body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in message['payload']:
            import base64
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        return body
    
    except Exception as e:
        log_message(f"❌ Error getting email body: {e}")
        return ""


def create_email_file(email_data, body=""):
    """Create .md file in Needs_Action folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"EMAIL_{timestamp}_{email_data['id'][:8]}.md"
    filepath = NEEDS_ACTION_DIR / filename
    
    # Clean subject for filename
    subject = email_data['subject'].replace('/', '-').replace('\\', '-')[:50]
    
    content = f"""---
type: email
from: {email_data['from']}
to: {email_data['to']}
subject: {subject}
received: {email_data['date']}
gmail_id: {email_data['id']}
status: new
priority: normal
created: {datetime.now().isoformat()}
---

# Email: {subject}

**From:** {email_data['from']}  
**To:** {email_data['to']}  
**Date:** {email_data['date']}

---

## Content

{body if body else email_data['snippet']}

---

## Actions Required

- [ ] Review email content
- [ ] Create LinkedIn post if applicable
- [ ] Move to /Done when processed

"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    log_message(f"✅ Created: {filename}")
    return filepath


def check_existing_emails(processed_ids):
    """Check if email already processed"""
    if not NEEDS_ACTION_DIR.exists():
        return processed_ids
    
    # Scan existing files
    for file in NEEDS_ACTION_DIR.glob("EMAIL_*.md"):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'gmail_id:' in content:
                for line in content.split('\n'):
                    if 'gmail_id:' in line:
                        gmail_id = line.split(':')[1].strip()
                        processed_ids.add(gmail_id)
    
    return processed_ids


def run_watcher():
    """Main watcher loop"""
    log_message("🚀 Starting LinkedIn Automation Watcher...")
    log_message(f"📁 Vault: {VAULT_DIR}")
    log_message(f"📥 Watching: {NEEDS_ACTION_DIR}")
    
    # Track processed emails
    processed_ids = set()
    processed_ids = check_existing_emails(processed_ids)
    log_message(f"📋 Found {len(processed_ids)} previously processed emails")
    
    # Get Gmail service
    service = get_gmail_service()
    if service:
        log_message("✅ Gmail connected")
    else:
        log_message("⚠️  Running without Gmail (file watcher mode only)")
    
    iteration = 0
    
    while True:
        iteration += 1
        log_message(f"\n--- Iteration {iteration} ---")
        
        # Fetch new emails
        if service:
            emails = fetch_recent_emails(service, max_results=5)
            log_message(f"📧 Found {len(emails)} recent emails")
            
            for email in emails:
                if email['id'] not in processed_ids:
                    log_message(f"📮 New email: {email['subject']}")
                    
                    # Get full body
                    body = get_full_email_body(service, email['id'])
                    
                    # Create file
                    create_email_file(email, body)
                    
                    # Mark as processed
                    processed_ids.add(email['id'])
        else:
            log_message("⊘ Skipping Gmail check (no service)")
        
        # Save processed IDs
        processed_file = Path(__file__).parent / ".processed_emails.json"
        with open(processed_file, 'w') as f:
            json.dump(list(processed_ids), f)
        
        # Wait for next check (every 60 seconds)
        log_message("⏳ Waiting 60 seconds...")
        time.sleep(60)


if __name__ == "__main__":
    try:
        run_watcher()
    except KeyboardInterrupt:
        log_message("\n👋 Watcher stopped by user")
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        sys.exit(1)
