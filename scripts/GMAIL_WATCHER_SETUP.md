---
type: setup_guide
component: gmail_watcher
tier: Silver
---

# Gmail Watcher Setup Guide

## Overview

The Gmail Watcher monitors your Gmail inbox for **important, unread emails** and creates Markdown files in the `Needs_Action` folder for AI processing.

**Poll Interval:** Every 2 minutes

---

## Prerequisites

1. **Python 3.13+** installed
2. **Google Cloud Project** with Gmail API enabled
3. **OAuth 2.0 Credentials** downloaded

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2: Set Up Google Cloud Project

### 2.1 Create Project & Enable API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable **Gmail API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2.2 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen if prompted:
   - User Type: **External**
   - App name: `Personal AI Employee`
   - User support email: Your email
   - Developer contact: Your email
4. Create OAuth Client ID:
   - Application type: **Desktop app**
   - Name: `AI Employee Gmail Watcher`
5. Download the credentials JSON file

### 2.3 Save Credentials

Save the downloaded file as `gmail_credentials.json` in the project root:

```
Hackathon-0--Personal-AI-Employee/
├── gmail_credentials.json    ← Put file here
├── scripts/
│   └── gmail_watcher.py
└── AI_Employee_Vault/
```

---

## Step 3: First-Time Authentication

Run the watcher with the `--auth` flag to authenticate:

```bash
python scripts/gmail_watcher.py --auth
```

This will:
1. Open a browser window (or provide a URL)
2. Ask you to sign in to Google
3. Request permission to read your Gmail
4. Save a `token.json` file for future use

**Note:** The token file is saved in the project root and contains your refresh token. Keep it secure!

---

## Step 4: Test the Watcher

Run a single poll cycle to test:

```bash
python scripts/gmail_watcher.py --test
```

Check the output:
- Look for "Found X important unread emails"
- Check `AI_Employee_Vault/Needs_Action/` for created files
- Review `AI_Employee_Vault/Logs/gmail_watcher_YYYY-MM-DD.log`

---

## Step 5: Run Continuously

### Option A: Direct Execution

```bash
python scripts/gmail_watcher.py
```

Press `Ctrl+C` to stop.

### Option B: Windows Task Scheduler

1. Open **Task Scheduler**
2. Create a new task:
   - **Name:** `AI Employee Gmail Watcher`
   - **Trigger:** At log on / Daily
   - **Action:** Start a program
     - Program: `python.exe`
     - Arguments: `scripts/gmail_watcher.py`
     - Start in: `<project_root>`

### Option C: Cron (Linux/Mac)

```bash
crontab -e
```

Add line to run every 2 minutes:
```
*/2 * * * * cd /path/to/project && python scripts/gmail_watcher.py
```

---

## How It Works

### Email Filtering

The watcher only processes emails that are:
- ✅ Marked as **Important** by Gmail
- ✅ **Unread**
- ✅ **Not in Spam**
- ✅ **Not in Trash**

### Priority Detection

Emails are classified by priority:

| Priority | Indicators |
|----------|------------|
| **Urgent** | Subject contains "urgent", "ASAP", "emergency" |
| **High** | Important label, meeting requests, client emails |
| **Normal** | Standard important emails |
| **Low** | Newsletters, promotions, noreply addresses |

### File Creation

For each new email, creates:

```
AI_Employee_Vault/Needs_Action/EMAIL_20260328_103000_Subject_Line.md
```

With YAML frontmatter:
```yaml
---
type: email
message_id: <gmail_id>
from: Sender Name <email@example.com>
subject: Email Subject
received: 2026-03-28T10:30:00Z
priority: high
status: unprocessed
---
```

### Processed Tracking

- Processed email IDs saved to `.processed_emails.json`
- Prevents duplicate file creation
- Cache persists across restarts

---

## Logs

Logs are saved to:
```
AI_Employee_Vault/Logs/gmail_watcher_YYYY-MM-DD.log
```

Log levels:
- **INFO:** Normal operation, emails found/processed
- **DEBUG:** Detailed polling information
- **WARNING:** Non-critical issues
- **ERROR:** Failed operations

---

## Troubleshooting

### "Credentials file not found"

Ensure `gmail_credentials.json` is in the project root (same level as `scripts/`).

### "Token expired" or authentication errors

Delete `token.json` and re-run authentication:
```bash
rm token.json
python scripts/gmail_watcher.py --auth
```

### No emails being processed

1. Check if emails are marked as **Important** in Gmail
2. Verify emails are **Unread**
3. Check logs for filtering details
4. Test with a known important email

### "Gmail API not enabled"

Go to Google Cloud Console and enable Gmail API for your project.

### Rate limiting errors

Gmail API has rate limits. If you hit them:
- Increase `POLL_INTERVAL_SECONDS` in the script
- Reduce `MAX_RESULTS_PER_POLL`

---

## Configuration

Edit these values in `gmail_watcher.py`:

```python
# Poll interval (default: 2 minutes)
POLL_INTERVAL_SECONDS = 120

# Max emails per poll (default: 10)
MAX_RESULTS_PER_POLL = 10

# Processed cache file
PROCESSED_CACHE = VAULT_DIR / ".processed_emails.json"
```

---

## Security Notes

1. **Never commit** `gmail_credentials.json` or `token.json` to Git
2. Add to `.gitignore`:
   ```
   gmail_credentials.json
   token.json
   ```
3. Store credentials securely
4. Use a dedicated Google account if possible

---

## Next Steps

After Gmail Watcher creates files in `Needs_Action`:

1. **AI Processing:** Claude reads files and classifies emails
2. **Draft Replies:** AI creates draft responses
3. **Human Approval:** You review drafts in `Pending_Approval`
4. **Send:** Approved replies are sent via email

See `Company_Handbook.md` for Gmail reply guidelines.

---

## Support

For issues:
1. Check logs in `AI_Employee_Vault/Logs/`
2. Verify credentials and permissions
3. Test with `--test` flag first
4. Review Google Cloud Console for API errors
