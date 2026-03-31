# 🚀 START HERE - Silver Tier AI Employee Quick Start

## ✅ Setup Status

| Step | Status | Notes |
|------|--------|-------|
| 1. Files Organization | ✅ **COMPLETE** | Sab files sahi jagah hain |
| 2. Gmail Credentials | ✅ **COMPLETE** | `gmail_credentials.json` ready |
| 3. PM2 Services | ✅ **RUNNING** | Dono services online hain |
| 4. Gmail Authentication | ⏳ **PENDING** | URL se authorize karna hai |
| 5. LinkedIn MCP | ⏳ **OPTIONAL** | Baad mein setup kar sakte hain |

---

## 🎯 ABHI KYA KARNA HAI? (Next 10 Minutes)

### 1️⃣ Gmail Authentication Complete (REQUIRED)

**URL kholo aur authorize karo:**

```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=998564885592-hvol7lisnqpacj862flts0vqn8ajdmq9.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A55195%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly&state=nNR16qeFSBuzQP9GPXBQUPu6x0Olmq&code_challenge=4r7hvinw1WuENZ7KAppiSC-nElYwKfmEYalEmTEckyE&code_challenge_method=S256&access_type=offline
```

**Ya ye command run karo:**
```bash
python scripts/gmail_watcher.py --auth
```

**Steps:**
1. Browser mein URL khulega
2. Gmail account select karo
3. "Allow" permissions do
4. Authorization code milega
5. Terminal mein paste karo

---

### 2️⃣ Test Karo Sab Chal Raha Hai

```bash
# PM2 status check
pm2 status

# Gmail watcher logs
pm2 logs ai-employee-gmail-watcher --lines 20

# Orchestrator logs
pm2 logs ai-employee-orchestrator --lines 20
```

---

### 3️⃣ Obsidian Vault Kholo

```bash
# Obsidian open karo
# File → Open Folder as Vault
# Select: AI_Employee_Vault folder
```

**Files dekho:**
- `Dashboard.md` - Main control panel
- `Company_Handbook.md` - All rules
- `Business_Goals.md` - Your goals

---

### 4️⃣ Pehla AI Employee Run

**Qwen/Claude Code mein ye prompt paste karo:**

```markdown
You are my active Silver Tier AI Employee.
Current time: 2026-03-28 22:45 PKT

## Your Tasks

1. Read all files from `/Needs_Action/` folder
2. Analyze every Gmail message using Company_Handbook.md
3. Create detailed Plan.md in `/Plans/` folder with checkboxes
4. For any reply or LinkedIn post: create approval file in `/Pending_Approval/`
5. Follow all rules from Company_Handbook.md strictly

## After Creating Plan

Tell me:
- What you did
- What needs my approval
- What actions are pending
```

---

## 📊 Daily Workflow

### Morning Check (9 AM)

```bash
# 1. PM2 status
pm2 status

# 2. Check logs
pm2 logs --lines 50

# 3. Check Needs_Action
dir AI_Employee_Vault\Needs_Action\

# 4. Review Pending_Approval
dir AI_Employee_Vault\Pending_Approval\
```

### Approve Files (As Needed)

```bash
# Obsidian mein jao
# Pending_Approval folder kholo
# Files review karo
# Approved files ko /Approved/ mein move karo
```

### Evening Review (6 PM)

```bash
# Daily logs check
type AI_Employee_Vault\Logs\Daily_Log_*.md

# Dashboard update
open AI_Employee_Vault\Dashboard.md
```

---

## 🔧 Quick Commands Reference

### PM2 Commands

```bash
pm2 status              # Services status
pm2 logs                # Real-time logs
pm2 restart all         # Restart all services
pm2 stop all            # Stop all services
```

### Gmail Commands

```bash
python scripts/gmail_watcher.py --auth   # Authenticate
python scripts/gmail_watcher.py --test   # Test run
```

### LinkedIn Commands

```bash
cd scripts/linkedin-mcp-server
npm install           # Install dependencies
npm run auth          # Authenticate
npm test              # Test publish
```

---

## 📁 Important Folders

```
AI_Employee_Vault/
├── Needs_Action/         # New emails/items (AI processes)
├── Plans/                # Processing plans (AI creates)
├── Pending_Approval/     # Needs your approval ⭐
├── Approved/             # Ready to execute (move files here)
├── Rejected/             # Declined items
├── Done/                 # Completed tasks
└── Logs/                 # Activity logs
```

---

## ⚠️ Important Rules

### NEVER (AI ke liye)

- ❌ Send email without approval
- ❌ Post LinkedIn without approval
- ❌ Skip Company_Handbook rules
- ❌ Process without creating Plan.md

### ALWAYS (AI ke liye)

- ✅ Create approval files in `/Pending_Approval/`
- ✅ Follow Company_Handbook.md
- ✅ Log every action
- ✅ Move completed to `/Done/`

### YOUR Job (Human ke liye)

- ✅ Review `/Pending_Approval/` files daily
- ✅ Move approved files to `/Approved/`
- ✅ Check `Dashboard.md` regularly
- ✅ Update `Business_Goals.md`

---

## 🎯 Success Checklist

```bash
# ✅ PM2 services running
pm2 status
# → Green "online" for both services

# ✅ Gmail authenticated
python scripts/gmail_watcher.py --test
# → "Poll cycle complete" message

# ✅ Obsidian vault open
# → Dashboard.md visible

# ✅ First reasoning loop run
# → Plan.md created in /Plans/

# ✅ First approval pending
# → File in /Pending_Approval/
```

---

## 📞 Support Files

| File | Purpose |
|------|---------|
| `COMPLETE_SETUP_GUIDE.md` | Full step-by-step guide |
| `STEP3_COMPLETE.md` | PM2 setup details |
| `GMAIL_CREDENTIALS_SETUP.md` | Gmail auth guide |
| `RUN_COMMANDS.md` | All commands reference |
| `Company_Handbook.md` | All AI rules |

---

## 🚀 Next Steps After Setup

1. ✅ **Gmail Auth Complete** ← ABHI
2. ⏳ **Test Reasoning Loop** ← Iske baad
3. ⏳ **LinkedIn MCP Setup** ← Optional
4. ⏳ **Daily Operations** ← Rozana

---

**Ready? Chalo shuru karte hain!** 🎉

1. Gmail auth URL kholo (upar diya hai)
2. Authorize karo
3. Test command run karo
4. Obsidian vault kholo
5. Pehla AI Employee prompt run karo

---

*Last Updated: 2026-03-28 22:45 PKT | Tier: Silver*
