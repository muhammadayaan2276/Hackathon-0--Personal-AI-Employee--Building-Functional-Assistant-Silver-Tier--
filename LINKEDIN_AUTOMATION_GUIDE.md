# LinkedIn Automation - Complete Setup Guide

## 🎯 Overview

Complete LinkedIn automation system that:
1. **Watches** your Gmail for new emails
2. **Creates** LinkedIn post drafts using Claude AI
3. **Waits** for your approval
4. **Publishes** approved posts automatically
5. **Tracks** everything in your Obsidian vault

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Inbox/                    # Raw incoming emails
├── Needs_Action/             # New emails to process
├── Pending_Approval/         # LinkedIn drafts awaiting approval
├── Approved/                 # Posts you approved
├── Done/                     # Published posts
├── Plans/                    # Task plans with checkboxes
└── Logs/                     # Activity logs
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

Required packages:
```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
anthropic
playwright
```

### Step 2: Setup Gmail (Optional)

If you want email monitoring:

```bash
cd scripts/email-mcp-server
python auth.py
```

Follow the browser prompts to authenticate.

### Step 3: Setup Anthropic API (Optional)

For AI-powered post generation:

```bash
# Set environment variable
set ANTHROPIC_API_KEY=your-api-key-here
```

Or add to `.env` file.

### Step 4: Run the Automation

**Option A: Run All Components**
```bash
python orchestrator_linkedin.py
```

**Option B: Run Individual Components**
```bash
# Only email watcher
python orchestrator_linkedin.py --watcher

# Only Claude processor
python orchestrator_linkedin.py --processor

# Only Ralph Loop (publisher)
python orchestrator_linkedin.py --ralph
```

---

## 🔄 Complete Flow

### 1. Email Arrives
```
📧 Gmail receives email
   ↓
🐍 Watcher detects new email
   ↓
📄 Creates: /Needs_Action/EMAIL_20260328_103000.md
```

### 2. Claude Processes
```
🤖 Claude reads email
   ↓
🧠 Decides if it's LinkedIn-worthy
   ↓
📝 Creates: /Pending_Approval/LINKEDIN_POST_20260328_103500.md
   ↓
📁 Moves email to /Done
```

### 3. You Approve
```
👤 You review the draft
   ↓
✅ Move to /Approved (to publish)
   ❌ Move to /Rejected (to discard)
```

### 4. Ralph Publishes
```
🔄 Ralph Loop checks /Approved every 30s
   ↓
🚀 Calls LinkedIn MCP Server
   ↓
📤 Post published to LinkedIn
   ↓
📁 Moves to /Done
```

---

## 📋 File Formats

### Email File (Needs_Action)
```markdown
---
type: email
from: client@company.com
subject: New Product Launch
received: 2026-03-28T10:30:00Z
status: new
---

# Email: New Product Launch

**From:** client@company.com

## Content

We just launched our new AI product!
```

### LinkedIn Draft (Pending_Approval)
```markdown
---
type: linkedin_post
status: pending_approval
source_file: EMAIL_20260328_103000.md
created: 2026-03-28T10:35:00Z
---

# LinkedIn Post Draft

## Preview

🚀 Exciting News!

We just launched our new AI product!

#AI #ProductLaunch

---

## Approval Instructions

**To Approve:** Move to /Approved folder
**To Reject:** Move to /Rejected folder
```

---

## 🎛️ Configuration

### Environment Variables

```bash
# Gmail (optional)
GMAIL_CLIENT_ID=xxx
GMAIL_CLIENT_SECRET=xxx
GMAIL_REFRESH_TOKEN=xxx

# Anthropic (optional)
ANTHROPIC_API_KEY=xxx

# LinkedIn (via MCP)
LINKEDIN_SESSION_DIR=./linkedin-mcp-server/.linkedin-session
```

### Check Interval

Edit in scripts:
- `linkedin_automation_watcher.py`: `time.sleep(60)` - Check emails every 60s
- `claude_linkedin_processor.py`: `time.sleep(30)` - Process every 30s
- `ralph_linkedin_loop.py`: `time.sleep(30)` - Publish every 30s

---

## 🧪 Testing

### Test Email Watcher
```bash
python linkedin_automation_watcher.py
```

### Test Claude Processor
```bash
python claude_linkedin_processor.py --once
```

### Test Ralph Loop
```bash
python ralph_linkedin_loop.py --once
```

### Test Full Flow
1. Create test email file in `/Needs_Action`
2. Run processor
3. Check `/Pending_Approval` for draft
4. Move to `/Approved`
5. Run Ralph
6. Check LinkedIn

---

## 📊 Monitoring

### Check Status
```bash
python orchestrator_linkedin.py --status
```

### View Logs
```
AI_Employee_Vault/Logs/
├── linkedin_watcher_2026-03-28.md
├── claude_processor_2026-03-28.md
├── ralph_loop_2026-03-28.md
└── orchestrator_2026-03-28.md
```

### Dashboard
Open `AI_Employee_Vault/Dashboard.md` in Obsidian for real-time status.

---

## 🛠️ Troubleshooting

### Gmail Not Working
1. Check `credentials.json` exists
2. Re-run `python auth.py`
3. Check Gmail API is enabled

### Claude Not Generating
1. Check `ANTHROPIC_API_KEY` is set
2. Check API quota
3. Fallback: Template generation will be used

### LinkedIn Not Publishing
1. Check session is valid: `npm run test` in linkedin-mcp-server
2. Re-authenticate: `npm run auth`
3. Check browser is not blocking automation

### Files Not Moving
1. Check folder permissions
2. Close Obsidian (file locks)
3. Check file isn't open elsewhere

---

## 📝 Manual Workflow

If you want manual control:

### Create Post Manually
1. Create file in `/Pending_Approval/`
2. Write your post
3. Move to `/Approved`
4. Ralph will publish

### Approve/Reject
```bash
# Approve
move AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md AI_Employee_Vault/Approved/

# Reject
move AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md AI_Employee_Vault/Rejected/
```

---

## 🎯 Usage Examples

### Example 1: Product Launch Email

**Email Received:**
```
From: marketing@company.com
Subject: New Product Launch

We're excited to announce our new AI-powered analytics platform!
```

**Generated Post:**
```markdown
🚀 Exciting Launch!

We're thrilled to introduce our new AI-powered analytics platform!

This game-changing tool helps you:
✅ Real-time insights
✅ Predictive analytics
✅ Custom dashboards

#AI #Analytics #ProductLaunch
```

### Example 2: Company News

**Email Received:**
```
From: hr@company.com
Subject: New Team Member

Welcome Sarah as our new CTO!
```

**Generated Post:**
```markdown
👋 Welcome to the Team!

Excited to announce Sarah as our new CTO!

With 15+ years in tech leadership, she'll drive our innovation forward.

#TeamGrowth #Leadership #Welcome
```

---

## 🔐 Security

- Gmail credentials stored locally
- API keys in environment variables
- LinkedIn session encrypted
- All data stays in your vault

---

## 📈 Performance

- Email check: Every 60 seconds
- Processing: ~5 seconds per email
- Publishing: ~30 seconds per post
- Ralph Loop: Checks every 30 seconds

---

## 🆘 Support

### Common Issues

| Issue | Solution |
|-------|----------|
| "Not logged in" | Run `npm run auth` |
| "No emails found" | Check Gmail credentials |
| "Claude API error" | Check API key, fallback enabled |
| "Permission denied" | Close Obsidian, check file locks |

### Get Help

1. Check logs in `/Logs`
2. Run with `--verbose` flag
3. Check GitHub issues

---

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Gmail authenticated (optional)
- [ ] Anthropic API key set (optional)
- [ ] LinkedIn MCP working
- [ ] Folders created
- [ ] Orchestrator running
- [ ] Test post published

---

**🎉 You're all set! LinkedIn automation is ready!**
