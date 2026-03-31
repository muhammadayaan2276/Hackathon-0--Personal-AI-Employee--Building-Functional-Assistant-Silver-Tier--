# 🚀 Complete Setup Guide - Silver Tier AI Employee

## Quick Navigation

- [Step 4: Main AI Employee (Reasoning Loop)](#step-4-main-ai-employee-reasoning-loop)
- [Step 5: Approval Workflow](#step-5-approval-workflow)
- [Step 6: LinkedIn Posting Test](#step-6-linkedin-posting-test)
- [Immediate Next Actions](#abhi-kya-karo-immediate-next-actions)

---

## Step 4: Main AI Employee (Reasoning Loop)

### Option A: Qwen/Claude Code Mein Direct Prompt

Ye prompt copy karke AI mein paste karo:

```markdown
You are my active Silver Tier AI Employee.
Current time: {{current_date_time}}

## Your Tasks

1. **Read all files** from `/Needs_Action/` folder
2. **Analyze every Gmail message** using Company_Handbook.md rules
3. **Create detailed Plan.md** in `/Plans/` folder with clear checkboxes
4. **For any reply or LinkedIn post**: Create approval file in `/Pending_Approval/`
5. **Follow all rules** from Company_Handbook.md strictly

## After Creating Plan

Tell me:
- What you did
- What needs my approval
- What actions are pending

## Important Rules

- NEVER send emails without approval
- NEVER post on LinkedIn without approval
- ALWAYS create Plan.md before processing
- ALWAYS follow Company_Handbook.md
```

---

### Option B: Agent Skill Activate Karo

```bash
# Qwen Code mein
skill: "silver-tier-reasoning"

# Ya command se
/agent-skill Silver_Tier_Reasoning_Engine --run
```

---

### Option C: Shortcut File Bana Lo

**`run_employee.bat`** (Windows):
```batch
@echo off
echo ==============================================
echo   AI Employee - Reasoning Loop
echo ==============================================
echo.
echo Current Time: %DATE% %TIME%
echo.
echo Opening Obsidian Vault...
start "" "AI_Employee_Vault"
echo.
echo Next Steps:
echo 1. Check Needs_Action folder
echo 2. Run AI Employee reasoning
echo 3. Review Pending_Approval files
echo.
pause
```

**`run_employee.sh`** (Linux/Mac):
```bash
#!/bin/bash
echo "=============================================="
echo "  AI Employee - Reasoning Loop"
echo "=============================================="
echo ""
echo "Current Time: $(date)"
echo ""
echo "Opening Obsidian Vault..."
open AI_Employee_Vault  # Mac
# xdg-open AI_Employee_Vault  # Linux
echo ""
echo "Next Steps:"
echo "1. Check Needs_Action folder"
echo "2. Run AI Employee reasoning"
echo "3. Review Pending_Approval files"
```

---

### Option D: Automated Schedule (Recommended)

**PM2 se auto-run every 5 minutes:**

```bash
# Orchestrator already running hai via PM2
pm2 status

# Logs dekho
pm2 logs ai-employee-orchestrator
```

Orchestrator automatically:
- Every 5 minutes reasoning engine chalata hai
- Needs_Action process karta hai
- Plans create karta hai
- Approvals manage karta hai

---

## Step 5: Approval Workflow

### Kaise Kaam Karega

```
┌─────────────────────────────────────────────────────────────┐
│                    Approval Workflow                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. AI creates file in /Pending_Approval/                   │
│     EMAIL_REPLY_20260328_103000.md                          │
│     LINKEDIN_POST_2026-03-28_Achievement.md                 │
│                                                              │
│  2. YOU review file in Obsidian                             │
│     • Read content                                          │
│     • Check tone, hashtags, approval instructions           │
│                                                              │
│  3. YOU decide:                                             │
│     ✅ Approve → Move to /Approved/                         │
│     ❌ Reject → Move to /Rejected/ with reason              │
│     ✏️  Edit → Make changes, leave in Pending_Approval      │
│                                                              │
│  4. AI detects file in /Approved/                           │
│     • Sends email (via Gmail MCP)                           │
│     • Publishes LinkedIn (via LinkedIn MCP)                 │
│     • Moves file to /Done/                                  │
│     • Logs action in /Logs/                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Approval File Example

**File:** `AI_Employee_Vault/Pending_Approval/EMAIL_REPLY_20260328_103000.md`

```markdown
---
type: email_reply
to: client@example.com
subject: Re: Project Inquiry
priority: high
created: 2026-03-28T10:30:00Z
status: pending_approval
---

## Draft Reply

Hi Client Name,

Thank you for reaching out regarding the project. I'd be happy to help...

Best regards,
Your Name

---
## Approval Instructions

**To Approve:**
Move this file to `/Approved/EMAIL_REPLY_20260328_103000.md`

**To Reject:**
Move to `/Rejected/` with reason.

**To Edit:**
Make changes and leave in Pending_Approval.
```

---

### Obsidian Mein Kaise Move Karein

1. **Obsidian kholo** → AI_Employee_Vault
2. **Navigate to:** `Pending_Approval` folder
3. **File select karo** → Right-click → "Move file to..."
4. **Select folder:** `Approved` ya `Rejected`
5. **Ya manually:** File ko drag-drop karo

---

### Approval Commands

```bash
# Check pending approvals
dir AI_Employee_Vault\Pending_Approval\

# View file content
type AI_Employee_Vault\Pending_Approval\EMAIL_REPLY_*.md

# Move to Approved (PowerShell)
Move-Item "AI_Employee_Vault\Pending_Approval\file.md" "AI_Employee_Vault\Approved\"

# Move to Approved (Command Prompt)
move "AI_Employee_Vault\Pending_Approval\file.md" "AI_Employee_Vault\Approved\"
```

---

## Step 6: LinkedIn Posting Test

### Test Sequence

1. **AI creates LinkedIn post draft:**
   ```
   /Pending_Approval/LINKEDIN_POST_2026-03-28_Test.md
   ```

2. **YOU review and approve:**
   - File ko `/Approved/` mein move karo

3. **AI detects approved file:**
   - Reasoning engine automatically detect karega
   - LinkedIn MCP server use karega
   - Post publish hoga

4. **Verify:**
   - LinkedIn pe post dikhai dega
   - Screenshot save hoga `/Done/` mein
   - Log entry banegi `/Logs/LinkedIn_Publishing.md`

---

### Manual LinkedIn Post Test

```bash
# LinkedIn MCP server test
cd scripts/linkedin-mcp-server

# Install dependencies (if not done)
npm install

# Authenticate
npm run auth

# Test publish
npm test
```

---

## Abhi Kya Karo? (Immediate Next Actions)

### ✅ Priority 1: Gmail Authentication Complete

```bash
# URL copy karo (from PM2 logs)
pm2 logs ai-employee-gmail-watcher --lines 50

# Ya direct auth run karo
python scripts/gmail_watcher.py --auth
```

**Steps:**
1. URL browser mein paste karo
2. Gmail login + Allow
3. Authorization code paste karo
4. `token.json` ban jayega

---

### ✅ Priority 2: Test Reasoning Loop

```bash
# Orchestrator status check
pm2 status

# Logs dekho
pm2 logs ai-employee-orchestrator --lines 50

# Check if Plans folder mein files ban rahe hain
dir AI_Employee_Vault\Plans\
```

---

### ✅ Priority 3: Check Needs_Action

```bash
# Check if any emails processed
dir AI_Employee_Vault\Needs_Action\

# If empty, Gmail watcher wait kar raha hai
# Auth complete karo pehle
```

---

### ✅ Priority 4: LinkedIn MCP Setup (Optional)

```bash
cd scripts/linkedin-mcp-server

# Install
npm install

# Authenticate
npm run auth
# → Browser khulega, LinkedIn login karo
```

---

## 📊 Complete Status Check

```bash
# Sab PM2 services
pm2 status

# Gmail watcher logs
pm2 logs ai-employee-gmail-watcher

# Orchestrator logs
pm2 logs ai-employee-orchestrator

# Vault folders
dir AI_Employee_Vault\Needs_Action\
dir AI_Employee_Vault\Plans\
dir AI_Employee_Vault\Pending_Approval\
dir AI_Employee_Vault\Approved\
dir AI_Employee_Vault\Done\
```

---

## 🎯 Daily Workflow

### Morning (9 AM)

```bash
# 1. Check overnight activity
pm2 logs --lines 100

# 2. Check Needs_Action
dir AI_Employee_Vault\Needs_Action\

# 3. Review Pending_Approval
dir AI_Employee_Vault\Pending_Approval\

# 4. Approve files (move to /Approved/)
```

### Throughout Day

```bash
# Check status
pm2 status

# Review new approvals
dir AI_Employee_Vault\Pending_Approval\

# Move approved files to /Approved/
```

### Evening (6 PM)

```bash
# Check daily logs
type AI_Employee_Vault\Logs\Daily_Log_*.md

# Review Dashboard
open AI_Employee_Vault\Dashboard.md

# Plan tomorrow's goals
```

---

## 🔧 Troubleshooting

### "No files in Needs_Action"

```bash
# Gmail watcher check karo
pm2 logs ai-employee-gmail-watcher

# Auth complete nahi hua?
python scripts/gmail_watcher.py --auth
```

### "Orchestrator errors"

```bash
# Logs check karo
pm2 logs ai-employee-orchestrator --err

# Restart karo
pm2 restart ai-employee-orchestrator
```

### "LinkedIn MCP not working"

```bash
# Session check
cd scripts/linkedin-mcp-server
npm run auth

# Re-authenticate if needed
```

---

## 📞 Quick Reference

| Action | Command |
|--------|---------|
| Check services | `pm2 status` |
| View logs | `pm2 logs` |
| Gmail auth | `python scripts/gmail_watcher.py --auth` |
| LinkedIn auth | `npm run auth` (in linkedin-mcp-server) |
| Restart all | `pm2 restart all` |
| Check Needs_Action | `dir AI_Employee_Vault\Needs_Action\` |
| Check Pending_Approval | `dir AI_Employee_Vault\Pending_Approval\` |

---

*Last Updated: 2026-03-28 22:45 PKT | Tier: Silver*
