#!/usr/bin/env python3
"""
Email Processor (AI)
Reads emails from /Needs_Action and creates reply drafts in /Pending_Approval

Flow:
1. Scan /Needs_Action for new emails
2. Use AI to analyze and create reply drafts
3. Save drafts to /Pending_Approval
4. Move processed emails to /Done

Usage:
    python email_processor.py          # Run continuously
    python email_processor.py --once   # Process once and exit
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from pathlib import Path

# Configuration
VAULT_DIR = Path(__file__).parent.parent / "AI_Employee_Vault"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
PENDING_APPROVAL_DIR = VAULT_DIR / "Pending_Approval"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = VAULT_DIR / "Logs"
PLANS_DIR = VAULT_DIR / "Plans"

# Ensure directories exist
for dir_path in [PENDING_APPROVAL_DIR, DONE_DIR, LOGS_DIR, PLANS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def log_message(message: str):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"

    try:
        print(log_line)
    except UnicodeEncodeError:
        print(log_line.encode('cp1252', errors='replace').decode('cp1252'))

    log_file = LOGS_DIR / f"email_processor_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{log_line}")


def read_email_file(filepath):
    """Read email .md file and extract content"""
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


def create_reply_with_ai(email_content, email_body):
    """
    Use AI to create email reply
    Supports: Google Gemini (FREE), or template fallback
    Returns: (reply_data, raw_response)
    """

    # Create prompt for AI
    prompt = f"""
You are an email assistant. Analyze this email and create a professional reply.

## Email Content:

**From:** {email_content.get('from', 'Unknown')}
**To:** {email_content.get('to', 'me@gmail.com')}
**Subject:** {email_content.get('subject', 'No Subject')}
**Date:** {email_content.get('received', 'Unknown')}

**Body:**
{email_body}

## Instructions:

1. Analyze the email and determine what type of response is needed
2. Create a professional, polite reply
3. If no reply is needed, explain why

## Response Format:

```json
{{
  "needs_reply": true/false,
  "reason": "Why reply is needed or not",
  "reply_subject": "Re: Original Subject",
  "reply_body": "The email reply text",
  "priority": "high/normal/low",
  "category": "inquiry/meeting/payment/spam/other"
}}
```

Respond ONLY with the JSON.
"""

    # Try Google Gemini API (FREE)
    try:
        gemini_key = os.environ.get("GEMINI_API_KEY")

        if gemini_key:
            log_message("🤖 Using Google Gemini API (FREE)...")

            import urllib.request

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"

            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result_data = json.loads(response.read().decode('utf-8'))

            response_text = result_data['candidates'][0]['content']['parts'][0]['text']

            # Extract JSON from response
            json_match = re.search(r'```json\s*(.+?)\s*```', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(response_text)

            log_message("✅ Gemini API success!")
            return result, response_text

    except Exception as e:
        log_message(f"⚠️  Gemini API error: {e}")

    # Fallback: Template generation
    log_message("⚠️  No AI API available. Using template-based generation.")
    return generate_reply_template(email_content, email_body)


def generate_reply_template(email_content, email_body):
    """Fallback: Generate reply without AI"""

    subject = email_content.get('subject', 'No Subject')
    from_name = email_content.get('from', 'Someone')

    # Simple template-based generation
    reply = f"""Hi,

Thank you for your email regarding "{subject}".

I have received your message and will review it shortly. I will get back to you 
within 24-48 hours with a detailed response.

Best regards,
Me"""

    return {
        "needs_reply": True,
        "reason": "Auto-generated (AI not available)",
        "reply_subject": f"Re: {subject}",
        "reply_body": reply,
        "priority": "normal",
        "category": "general"
    }, "Template generated"


def create_reply_draft(result, source_file):
    """Create email reply draft in /Pending_Approval"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"EMAIL_REPLY_{timestamp}.md"
    filepath = PENDING_APPROVAL_DIR / filename

    reply_subject = result.get('reply_subject', 'Re: No Subject')
    reply_body = result.get('reply_body', '')

    # Get recipient from original email
    original_from = source_file.read_text(encoding='utf-8')
    to_email = ""
    for line in original_from.split('\n'):
        if 'from:' in line.lower():
            to_email = line.split(':', 1)[1].strip()
            # Extract email address if present
            if '<' in to_email:
                to_email = to_email.split('<')[1].strip('>')
            break

    content = f"""---
type: email_reply
status: pending_approval
source_file: {source_file.name}
created: {datetime.now().isoformat()}
priority: {result.get('priority', 'normal')}
category: {result.get('category', 'general')}
to: {to_email}
subject: {reply_subject}
---

# Email Reply Draft

## Reply Details

**To:** {to_email}
**Subject:** {reply_subject}
**Priority:** {result.get('priority', 'normal')}
**Category:** {result.get('category', 'general')}

---

## Reply Content

{reply_body}

---

## Metadata

- **Reason:** {result.get('reason', '')}
- **Source:** {source_file.name}

---

## Approval Instructions

**To Approve:**
1. Review the reply content above
2. Edit if needed
3. Move this file to `/Approved` folder

**To Reject:**
1. Move this file to `/Rejected` folder
2. Add reason for rejection below

---

## Rejection Notes (if applicable)


"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    log_message(f"✅ Created reply draft: {filename}")
    return filepath


def create_plan_file(result, source_file):
    """Create a plan file with checkboxes"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Plan_Email_{timestamp}.md"
    filepath = PLANS_DIR / filename

    content = f"""---
type: plan
created: {datetime.now().isoformat()}
source: {source_file.name}
status: in_progress
---

# Email Reply Plan

## Task
Create and send email reply

## Checklist

- [x] Email received and processed
- [x] Reply draft created
- [ ] **Waiting for human approval**
- [ ] Reply sent via Gmail
- [ ] Moved to Done

## Reply Details

**Priority:** {result.get('priority', 'normal')}
**Category:** {result.get('category', 'general')}
**To:** {result.get('to', 'Unknown')}

## Notes

{result.get('reason', '')}

"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def move_to_pending_approval(filepath):
    """Move email file to Pending_Approval folder (waiting for reply approval)"""
    dest = PENDING_APPROVAL_DIR / filepath.name
    # Handle duplicates
    counter = 1
    while dest.exists():
        dest = PENDING_APPROVAL_DIR / f"{filepath.stem}_{counter}.md"
        counter += 1
    try:
        filepath.rename(dest)
        log_message(f"📁 Moved to Pending_Approval: {dest.name}")
        return True
    except Exception as e:
        log_message(f"❌ Error moving file: {e}")
        return False


def move_to_done(filepath):
    """Move processed email to Done folder"""
    dest = DONE_DIR / filepath.name
    try:
        filepath.rename(dest)
        log_message(f"📁 Moved to Done: {filepath.name}")
        return True
    except Exception as e:
        log_message(f"❌ Error moving file: {e}")
        return False


def process_needs_action():
    """Process all files in /Needs_Action"""

    if not NEEDS_ACTION_DIR.exists():
        log_message("⚠️  /Needs_Action folder not found")
        return 0

    # Find all email files
    email_files = list(NEEDS_ACTION_DIR.glob("EMAIL_*.md"))

    if not email_files:
        log_message("📭 No new emails to process")
        return 0

    log_message(f"📧 Found {len(email_files)} emails to process")

    processed = 0

    for email_file in email_files:
        log_message(f"\n📮 Processing: {email_file.name}")

        try:
            # Read email
            frontmatter, body = read_email_file(email_file)

            # Generate reply with AI
            result, raw_response = create_reply_with_ai(frontmatter, body)

            if result.get('needs_reply', False):
                # Create draft in Pending_Approval
                draft_file = create_reply_draft(result, email_file)

                # Create plan
                create_plan_file(result, email_file)

                # Move original email to Done (reply draft is in Pending_Approval)
                move_to_done(email_file)

                log_message(f"✅ Reply draft created: {draft_file.name}")
                log_message(f"📁 File in Pending_Approval: {draft_file.name}")
                log_message(f"📁 Original email moved to Done: {email_file.name}")
                log_message(f"⏳ Waiting for human approval...")
                processed += 1
            else:
                log_message(f"⊘ No reply needed: {result.get('reason', 'Not applicable')}")
                # Still move to done if no reply needed
                move_to_done(email_file)
                processed += 1

        except Exception as e:
            log_message(f"❌ Error processing {email_file.name}: {e}")

    log_message(f"\n✅ Processed {processed} emails")
    return processed


def run_processor():
    """Main processor loop"""
    log_message("🚀 Starting Email Processor...")
    log_message(f"📁 Watching: {NEEDS_ACTION_DIR}")
    log_message(f"📝 Output: {PENDING_APPROVAL_DIR}")

    while True:
        # Process any new emails
        processed = process_needs_action()

        if processed > 0:
            log_message(f"✨ Created {processed} reply drafts")

        # Wait for next check (every 30 seconds)
        time.sleep(30)


if __name__ == "__main__":
    try:
        # Run once if called with --once
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            process_needs_action()
        else:
            run_processor()
    except KeyboardInterrupt:
        log_message("\n👋 Processor stopped by user")
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        sys.exit(1)
