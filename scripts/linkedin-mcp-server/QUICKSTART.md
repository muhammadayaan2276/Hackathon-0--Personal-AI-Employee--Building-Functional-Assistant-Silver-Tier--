# LinkedIn MCP Server - Quick Start

## 3-Minute Setup

```bash
# 1. Install dependencies
cd scripts/linkedin-mcp-server
npm install

# 2. Install Playwright browser
npx playwright install chromium

# 3. Authenticate with LinkedIn
npm run auth
# → Browser opens, login manually

# 4. Test everything works
npm test

# 5. Start the server
npm start
```

---

## Available Tools

| Tool | Description |
|------|-------------|
| `linkedin_check_session` | Verify if logged in |
| `linkedin_login` | Authenticate |
| `linkedin_post_publish` | Publish a post |
| `linkedin_take_screenshot` | Capture page |

---

## Example Usage

### Check Session
```json
{
  "tool": "linkedin_check_session",
  "arguments": {}
}
```

### Publish Post
```json
{
  "tool": "linkedin_post_publish",
  "arguments": {
    "content": "Excited to share my latest achievement! 🚀\n\n#Milestone #AI #Automation",
    "imagePath": "/path/to/image.png"
  }
}
```

---

## MCP Server Config

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": ["scripts/linkedin-mcp-server/index.js"],
      "cwd": "."
    }
  }
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No session | Run `npm run auth` |
| Browser won't open | `npx playwright install chromium` |
| Post fails | Check session with `npm test` |

---

*For full documentation, see README.md*
