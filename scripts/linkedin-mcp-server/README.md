---
type: setup_guide
component: linkedin_mcp_server
tier: Silver
---

# LinkedIn MCP Server Setup Guide

## Overview

The LinkedIn MCP Server enables your AI Employee to publish LinkedIn posts using browser automation (Playwright).

**Available Tools:**
- `linkedin_check_session` - Verify login status
- `linkedin_login` - Authenticate with LinkedIn
- `linkedin_post_publish` - Publish a new post
- `linkedin_take_screenshot` - Capture current page

---

## Prerequisites

1. **Node.js 18+** installed
2. **Playwright** browsers installed
3. **LinkedIn account** with posting permissions

---

## Step 1: Install Dependencies

```bash
cd scripts/linkedin-mcp-server
npm install
```

### Install Playwright Browsers

```bash
npx playwright install chromium
```

---

## Step 2: Authenticate with LinkedIn

Run the authentication script:

```bash
npm run auth
```

This will:
1. Open a browser window
2. Navigate to LinkedIn login
3. Wait for you to login manually
4. Save session cookies for future use
5. Optionally save credentials to `.env`

**Important:** 
- Check "Remember me" when logging in
- Complete any security challenges if prompted
- The session will be saved for 30 days

After successful authentication:
```
✅ Authentication complete!
✓ Saved LinkedIn session cookies
```

---

## Step 3: Verify Session

Test that the session works:

```bash
npm test
```

This will:
1. ✅ Check session validity
2. ✅ Navigate to LinkedIn feed
3. ✅ Take a test screenshot
4. ⚠️  Optionally publish a test post (confirms first)

---

## Step 4: Start MCP Server

### Option A: Direct Start

```bash
npm start
```

The server runs on stdio for MCP communication.

### Option B: Via Claude Code / Qwen Code

Add to your `mcp.json` in project root:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": [
        "scripts/linkedin-mcp-server/index.js"
      ],
      "cwd": "."
    }
  }
}
```

---

## Tool Reference

### linkedin_check_session

Verify if currently logged in to LinkedIn.

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "loggedIn": true,
  "profileName": "Your Name",
  "profileUrl": "https://www.linkedin.com/in/your-profile",
  "message": "LinkedIn session active"
}
```

---

### linkedin_login

Authenticate with LinkedIn.

**Parameters:**
```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

**Or use environment variables:**
```env
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Note:** If LinkedIn shows a security checkpoint, manual verification may be required.

---

### linkedin_post_publish

Publish a post to LinkedIn.

**Parameters:**
```json
{
  "content": "Your post content here...\n\n#Hashtag1 #Hashtag2",
  "imagePath": "/absolute/path/to/image.png"
}
```

**Content Guidelines:**
- Max 3000 characters
- Include hashtags at the end
- Use line breaks for readability
- Emojis are supported

**Image Guidelines:**
- PNG, JPG, or WEBP format
- Max 5 MB
- Recommended: 1200 x 627 px

**Response:**
```json
{
  "success": true,
  "postUrl": "https://www.linkedin.com/feed/update/urn:li:activity:123456789",
  "message": "Post published successfully",
  "screenshot": "base64_encoded_screenshot"
}
```

---

### linkedin_take_screenshot

Capture the current LinkedIn page.

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "screenshot": "base64_encoded_image"
}
```

---

## Usage with AI Employee

### Example: Publish Approved Post

```markdown
1. AI detects file in /Approved/LINKEDIN_POST_*.md
2. AI reads post content and hashtags
3. AI checks LinkedIn session:

```json
{
  "tool": "linkedin_check_session",
  "arguments": {}
}
```

4. If logged in, AI publishes post:

```json
{
  "tool": "linkedin_post_publish",
  "arguments": {
    "content": "Stop checking email every 5 minutes...\n\n#ProductivityTips #AI",
    "imagePath": "/path/to/image.png"
  }
}
```

5. AI saves screenshot to /Done/
6. AI logs action in /Logs/LinkedIn_Publishing.md
7. AI moves file to /Done/
```

---

## Session Management

### Session Storage

```
scripts/linkedin-mcp-server/.linkedin-session/
├── cookies.json    # LinkedIn session cookies
└── state.json      # Session metadata
```

### Session Lifecycle

| Event | Action |
|-------|--------|
| First run | Authenticate via `npm run auth` |
| Each post | Verify session active |
| Expired (~30 days) | Re-authenticate |
| Security challenge | Manual verification required |

### Extend Session

To extend session duration:
1. Login to LinkedIn in browser
2. Check "Remember me"
3. Run `npm run auth` again
4. New session will be saved

---

## File Structure

```
scripts/linkedin-mcp-server/
├── package.json           # Node.js dependencies
├── index.js              # MCP server main file
├── auth.js               # Authentication script
├── test.js               # Test suite
├── .linkedin-session/    # Session storage
│   └── cookies.json
├── .env                  # Credentials (created by auth.js)
├── README.md             # This file
└── test-*.png            # Test screenshots (deleted after tests)
```

---

## Troubleshooting

### "No session found"

Run authentication:
```bash
npm run auth
```

### "Session expired"

Re-authenticate:
```bash
npm run auth
# Choose option 3: Clear session and login
```

### "Security checkpoint detected"

LinkedIn may require additional verification:
1. Open LinkedIn in your browser
2. Complete any security challenges
3. Run `npm run auth` again

### "Post not publishing"

Check:
1. Session is valid: `npm test`
2. Content is under 3000 characters
3. Browser is not headless (for debugging)
4. No LinkedIn service outages

### "Browser won't open"

Install Playwright browsers:
```bash
npx playwright install chromium
```

### Rate Limiting

LinkedIn may limit automated actions:
- Wait 24 hours between posts
- Don't post more than 2-3 times per day
- Use the same session consistently

---

## Security Notes

1. **Never commit `.env`** to Git - it contains credentials
2. **Never commit session files** - they provide account access
3. **Add to `.gitignore`:**
   ```
   scripts/linkedin-mcp-server/.env
   scripts/linkedin-mcp-server/.linkedin-session/
   ```
4. **Use a dedicated LinkedIn account** if possible
5. **Review LinkedIn sessions** regularly in account settings

---

## Best Practices

### Content Formatting

```
✅ DO:
- Use short paragraphs (2-3 lines)
- Add 3-5 relevant hashtags
- Include emojis sparingly (2-4)
- Add call-to-action at end
- Keep under 1300 characters for optimal engagement

❌ DON'T:
- Write walls of text
- Use more than 5 hashtags
- Post controversial content
- Exceed 3000 character limit
```

### Posting Schedule

| Time | Audience | Best For |
|------|----------|----------|
| 8-9 AM | Commuters | Tips, news |
| 12-1 PM | Lunch break | Engagement |
| 5-6 PM | After work | Reflections |

### Image Best Practices

- Use high-quality images (min 600px wide)
- Include text overlay for key points
- Use consistent branding
- Recommended size: 1200 x 627 px

---

## Integration Examples

### Claude Code Integration

```bash
# In your Claude Code session
/mcp linkedin
```

Then use tools:
```
@linkedin linkedin_post_publish {"content": "...", "imagePath": "..."}
```

### Qwen Code Integration

The MCP server will be automatically available when configured in `mcp.json`.

---

## Performance Tips

- **Keep browser visible** for debugging (headless: false)
- **Reuse sessions** - don't re-authenticate every time
- **Wait for network idle** before actions
- **Take screenshots** for verification
- **Log all actions** for debugging

---

## Support

For issues:
1. Check logs in `AI_Employee_Vault/Logs/linkedin_mcp_*.md`
2. Run test suite: `npm test`
3. Verify session: `npm run auth` (view existing session)
4. Check LinkedIn for service status

---

*Version: 1.0 | Tier: Silver | Last Updated: 2026-03-28*
