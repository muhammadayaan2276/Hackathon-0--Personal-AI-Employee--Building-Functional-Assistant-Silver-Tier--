---
type: setup_guide
component: email_mcp_server
tier: Silver
---

# Email MCP Server Setup Guide

## Overview

The Email MCP Server enables your AI Employee to send Gmail replies, create drafts, and manage emails via the Model Context Protocol (MCP).

**Available Tools:**
- `email_send` - Send emails immediately
- `email_draft` - Create draft emails
- `email_mark_read` - Mark emails as read
- `email_list` - List recent emails
- `email_read` - Read specific email

---

## Prerequisites

1. **Node.js 18+** installed
2. **Google Cloud Project** with Gmail API enabled
3. **OAuth 2.0 Credentials** (gmail_credentials.json)

---

## Step 1: Install Dependencies

```bash
cd scripts/email-mcp-server
npm install
```

---

## Step 2: Authenticate with Gmail

Run the authentication script:

```bash
npm run auth
```

This will:
1. Display an authorization URL
2. Open the URL in your browser
3. Ask you to sign in to Google
4. Request Gmail permissions
5. Give you an authorization code
6. Save credentials to `.env` file

**Save the authorization code** and paste it when prompted.

After successful authentication, you'll see:
```
✅ Authentication complete!
✓ Saved credentials to .env file
```

---

## Step 3: Verify Configuration

Check that `.env` file was created:

```bash
# Should show your credentials (keep this secure!)
cat .env
```

Expected content:
```env
GMAIL_CLIENT_ID=123456789-abc...apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-abcdef123456
GMAIL_REFRESH_TOKEN=1//0gABC...
GMAIL_SENDER_EMAIL=your-email@gmail.com
```

---

## Step 4: Run Tests

Test all email functions:

```bash
npm test
```

This will:
1. ✅ List recent emails
2. ✅ Read an email
3. ✅ Create a draft email
4. ✅ Send a test email (confirms first)
5. ✅ Mark email as read

---

## Step 5: Start MCP Server

### Option A: Direct Start

```bash
npm start
```

The server runs on stdio (standard in/out) for MCP communication.

### Option B: Via Claude Code / Qwen Code

Add to your `mcp.json` in project root:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": [
        "scripts/email-mcp-server/index.js"
      ],
      "env": {
        "GMAIL_CLIENT_ID": "your-client-id",
        "GMAIL_CLIENT_SECRET": "your-client-secret",
        "GMAIL_REFRESH_TOKEN": "your-refresh-token",
        "GMAIL_SENDER_EMAIL": "your-email@gmail.com"
      }
    }
  }
}
```

Or reference the `.env` file:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": ["scripts/email-mcp-server/index.js"],
      "cwd": "scripts/email-mcp-server"
    }
  }
}
```

---

## Tool Reference

### email_send

Send an email immediately.

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body content",
  "inReplyTo": "message-id-being-replied-to",  // optional
  "threadId": "gmail-thread-id"  // optional
}
```

**Example:**
```json
{
  "to": "client@example.com",
  "subject": "Re: Project Inquiry",
  "body": "Hi Client,\n\nThank you for reaching out. I'd be happy to help.\n\nBest regards,\nYour Name"
}
```

**Response:**
```json
{
  "success": true,
  "messageId": "18abc123def456",
  "threadId": "18abc123def456",
  "message": "Email sent successfully to client@example.com"
}
```

---

### email_draft

Create a draft email without sending.

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body content",
  "inReplyTo": "message-id-being-replied-to"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "draftId": "18abc123def456",
  "message": "Draft created successfully for client@example.com",
  "preview": "Email body content..."
}
```

---

### email_mark_read

Mark email(s) as read.

**Parameters:**
```json
{
  "messageIds": ["msg-id-1", "msg-id-2"],  // optional
  "threadIds": ["thread-id-1"]  // optional
}
```

**Response:**
```json
{
  "success": true,
  "markedCount": 2,
  "messageIds": ["msg-id-1", "msg-id-2"],
  "message": "Marked 2 email(s) as read"
}
```

---

### email_list

List recent emails.

**Parameters:**
```json
{
  "maxResults": 10,  // optional, default: 10, max: 100
  "query": "is:unread",  // optional, Gmail search query
  "labelIds": ["UNREAD", "IMPORTANT"]  // optional
}
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "messages": [
    {
      "id": "18abc123def456",
      "threadId": "18abc123def456",
      "from": "sender@example.com",
      "to": "you@gmail.com",
      "subject": "Email Subject",
      "date": "2026-03-28T10:30:00Z",
      "snippet": "Preview text..."
    }
  ],
  "message": "Found 5 email(s)"
}
```

---

### email_read

Read a specific email by ID.

**Parameters:**
```json
{
  "messageId": "18abc123def456"
}
```

**Response:**
```json
{
  "success": true,
  "email": {
    "id": "18abc123def456",
    "threadId": "18abc123def456",
    "from": "sender@example.com",
    "to": "you@gmail.com",
    "subject": "Email Subject",
    "date": "2026-03-28T10:30:00Z",
    "body": "Full email body content...",
    "labels": ["INBOX", "IMPORTANT"]
  },
  "message": "Email retrieved successfully"
}
```

---

## Usage with AI Employee

### Example: Process Email Reply

```markdown
1. AI reads email from /Needs_Action/EMAIL_xxx.md
2. AI drafts reply using Company Handbook guidelines
3. AI creates approval file in /Pending_Approval/
4. Human moves file to /Approved/
5. AI calls email_send MCP tool:

```json
{
  "tool": "email_send",
  "arguments": {
    "to": "client@example.com",
    "subject": "Re: Project Inquiry",
    "body": "Hi Client,\n\nThank you for reaching out...\n\nBest regards,\nYour Name",
    "threadId": "18abc123def456"
  }
}
```

6. AI moves original to /Done/
7. AI logs action in /Logs/
```

---

## File Structure

```
scripts/email-mcp-server/
├── package.json        # Node.js dependencies
├── index.js           # MCP server main file
├── auth.js            # OAuth2 authentication
├── test.js            # Test suite
├── .env               # Credentials (created by auth.js)
├── .env.example       # Template for .env
└── README.md          # This file
```

---

## Troubleshooting

### "Missing configuration" error

Run authentication again:
```bash
npm run auth
```

### "Invalid credentials" error

1. Delete `.env` file
2. Re-run `npm run auth`
3. Ensure you copy the full authorization code

### "Token expired" error

Refresh token should be long-lived. If it expires:
1. Re-run `npm run auth`
2. Make sure to use a fresh authorization

### "Gmail API not enabled" error

1. Go to Google Cloud Console
2. Enable Gmail API for your project
3. Wait a few minutes for propagation

### Server won't start

Check Node.js version:
```bash
node --version  # Should be 18+
```

Update if needed:
```bash
nvm install 18
nvm use 18
```

---

## Security Notes

1. **Never commit `.env`** to Git - it contains secrets
2. **Add to `.gitignore`:**
   ```
   scripts/email-mcp-server/.env
   gmail_credentials.json
   ```
3. **Use a dedicated Google account** if possible
4. **Review OAuth permissions** regularly in Google Account settings

---

## Integration Examples

### Claude Code Integration

```bash
# In your Claude Code session
/mcp gmail
```

Then use tools:
```
@gmail email_send {"to": "...", "subject": "...", "body": "..."}
```

### Qwen Code Integration

The MCP server will be automatically available when configured in `mcp.json`.

---

## Performance Tips

- **Batch operations:** Use `email_mark_read` with multiple IDs
- **Throttle requests:** Gmail API has rate limits (~250 requests/second)
- **Cache results:** Store email content locally when possible
- **Use queries:** Filter with Gmail search syntax for faster results

---

## Support

For issues:
1. Check logs in `AI_Employee_Vault/Logs/email_mcp_*.md`
2. Run test suite: `npm test`
3. Verify credentials in `.env`
4. Check Google Cloud Console for API errors

---

*Version: 1.0 | Tier: Silver | Last Updated: 2026-03-28*
