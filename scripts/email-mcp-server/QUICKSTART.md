# Email MCP Server - Quick Start

## 3-Minute Setup

```bash
# 1. Install dependencies
cd scripts/email-mcp-server
npm install

# 2. Authenticate with Gmail
npm run auth
# → Follow the URL, paste the code

# 3. Test everything works
npm test

# 4. Start the server
npm start
```

---

## Available Tools

| Tool | Description |
|------|-------------|
| `email_send` | Send an email immediately |
| `email_draft` | Create a draft email |
| `email_mark_read` | Mark emails as read |
| `email_list` | List recent emails |
| `email_read` | Read a specific email |

---

## Example Usage

### Send Email
```json
{
  "tool": "email_send",
  "arguments": {
    "to": "client@example.com",
    "subject": "Re: Inquiry",
    "body": "Hi Client,\n\nThank you for reaching out.\n\nBest regards,\nYour Name"
  }
}
```

### Create Draft
```json
{
  "tool": "email_draft",
  "arguments": {
    "to": "client@example.com",
    "subject": "Re: Inquiry",
    "body": "Hi Client,\n\nLet me get back to you soon.\n\nBest regards,\nYour Name"
  }
}
```

### Mark as Read
```json
{
  "tool": "email_mark_read",
  "arguments": {
    "messageIds": ["msg-id-1", "msg-id-2"]
  }
}
```

---

## Configuration

After running `npm run auth`, your `.env` file contains:

```env
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
GMAIL_SENDER_EMAIL=your-email@gmail.com
```

---

## MCP Server Config

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": ["scripts/email-mcp-server/index.js"],
      "cwd": "."
    }
  }
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auth failed | Run `npm run auth` again |
| Module not found | Run `npm install` |
| Token expired | Re-run `npm run auth` |

---

*For full documentation, see README.md*
