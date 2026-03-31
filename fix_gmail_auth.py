#!/usr/bin/env python3
"""
Fix Gmail Authentication - Get SEND permission
Run this script to re-authorize with full permissions
"""

import os
import sys
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GMAIL_AVAILABLE = True
except ImportError:
    print("❌ Gmail libraries not installed!")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Configuration
PROJECT_ROOT = Path(__file__).parent
CREDENTIALS_FILE = PROJECT_ROOT / "gmail_credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"

# FULL permissions for reading AND sending emails
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.send',      # Send emails
    'https://www.googleapis.com/auth/gmail.modify'     # Modify labels
]

def main():
    print("=" * 60)
    print("  GMAIL AUTHENTICATION FIX - GET SEND PERMISSION")
    print("=" * 60)
    print()

    # Check credentials file
    if not CREDENTIALS_FILE.exists():
        print("❌ Credentials file not found!")
        print(f"   Expected: {CREDENTIALS_FILE}")
        print()
        print("Please download gmail_credentials.json from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Enable Gmail API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download and save as 'gmail_credentials.json'")
        sys.exit(1)

    print("✅ Credentials file found")
    print()

    # Remove old token file (has insufficient permissions)
    if TOKEN_FILE.exists():
        print("🗑️  Removing old token file (insufficient permissions)...")
        TOKEN_FILE.unlink()
        print("✅ Old token removed")
        print()

    # Start OAuth flow with FULL permissions
    print("🔐 Starting OAuth authorization flow...")
    print()
    print("📋 Required Permissions:")
    print("   ✅ Read emails from Gmail")
    print("   ✅ Send emails via Gmail")
    print("   ✅ Modify email labels")
    print()

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES)
        
        print("🌐 Opening browser for authentication...")
        print()
        print("⚠️  IMPORTANT: When Google asks for permissions,")
        print("   make sure you see ALL these permissions:")
        print("   - Read your Gmail messages")
        print("   - Send emails on your behalf")
        print("   - Manage your Gmail labels")
        print()
        print("If you don't see 'Send emails' permission,")
        print("something is wrong with the credentials file.")
        print()
        
        creds = flow.run_local_server(port=0, open_browser=True)

        # Save new credentials
        print()
        print("💾 Saving new credentials with SEND permission...")
        
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())

        print("✅ Authentication successful!")
        print()
        print("=" * 60)
        print("  GMAIL SEND PERMISSION GRANTED!")
        print("=" * 60)
        print()
        print("✅ Your Gmail automation can now:")
        print("   - Read incoming emails")
        print("   - Create reply drafts")
        print("   - Send approved replies automatically")
        print()
        print("🚀 Next steps:")
        print("   1. Move your pending file to /Approved folder")
        print("   2. Wait 30 seconds")
        print("   3. Email will be sent automatically!")
        print()

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure Gmail API is enabled in Google Cloud Console")
        print("2. Make sure OAuth consent screen is configured")
        print("3. Make sure credentials file is valid")
        sys.exit(1)


if __name__ == "__main__":
    main()
