# ✅ STEP 3 COMPLETE: PM2 Services Running!

## 🎉 Status: Services Online

```
┌────┬────────────────────┬──────────┬──────┬───────────┬──────────┬──────────┐
│ id │ name               │ mode     │ ↺    │ status    │ cpu      │ memory   │
├────┼────────────────────┼──────────┼──────┼───────────┼──────────┼──────────┤
│ 0  │ ai-employee-orche… │ fork     │ 0    │ online    │ 0%       │ 15.3mb   │
│ 1  │ ai-employee-gmail… │ fork     │ 0    │ online    │ 20.3%    │ 44.7mb   │
└────┴────────────────────┴──────────┴──────┴───────────┴──────────┴──────────┘
```

---

## 📋 What's Running

| Service | Purpose | Interval | Status |
|---------|---------|----------|--------|
| **ai-employee-orchestrator** | Reasoning engine | Every 5 min | ✅ Online |
| **ai-employee-gmail-watcher** | Gmail monitoring | Every 2 min | ✅ Online (needs auth) |

---

## ⚠️ IMPORTANT: Gmail Authentication Required

Gmail watcher ko authorize karna hai:

### Step 1: URL Copy Karo

Logs se ye URL copy karo:

```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=998564885592-hvol7lisnqpacj862flts0vqn8ajdmq9.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A55195%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly&state=nNR16qeFSBuzQP9GPXBQUPu6x0Olmq&code_challenge=4r7hvinw1WuENZ7KAppiSC-nElYwKfmEYalEmTEckyE&code_challenge_method=S256&access_type=offline
```

### Step 2: Browser Mein Paste Karo

1. URL browser mein paste karo
2. Apna Gmail account select karo
3. "Allow" permissions do:
   - ✅ Read emails
   - ✅ Send emails
   - ✅ Manage labels
4. Authorization code milega

### Step 3: Code Terminal Mein Paste Karo

Jo code milega usko terminal mein paste karo.

**Ya ye command run karo:**
```bash
python scripts/gmail_watcher.py --auth
```

---

## 📊 Useful Commands

```bash
# Status check
pm2 status

# Real-time logs
pm2 logs

# Gmail watcher logs only
pm2 logs ai-employee-gmail-watcher

# Orchestrator logs only
pm2 logs ai-employee-orchestrator

# Restart services
pm2 restart all

# Stop services
pm2 stop all
```

---

## 📁 Files Created

```
Project Root/
├── ecosystem.config.json       ✅ PM2 config
├── gmail_credentials.json      ✅ Gmail OAuth
├── AI_Employee_Vault/
│   └── Logs/
│       ├── pm2_orchestrator.log     ✅ Running
│       ├── pm2_orchestrator_error.log
│       ├── pm2_gmail_watcher.log    ✅ Running
│       └── pm2_gmail_watcher_error.log
└── token.json                     ⏳ Will be created after auth
```

---

## ✅ Verification Checklist

```bash
# 1. Services running hain?
pm2 status
# → Green "online" status ✅

# 2. Logs aa rahe hain?
pm2 logs --lines 20
# → Timestamps dikh rahe hain ✅

# 3. Gmail auth URL mili?
pm2 logs ai-employee-gmail-watcher
# → Authorization URL dikhai di ✅
```

---

## 🚀 Next Step: Complete Gmail Auth

1. ✅ **URL copy karo** (from logs above)
2. ✅ **Browser mein paste karo**
3. ✅ **Gmail login + Allow**
4. ✅ **Authorization code paste karo**
5. ✅ **token.json ban jayega**

---

## 📞 After Authentication

Jab Gmail auth complete ho jaye:

```bash
# Test run
python scripts/gmail_watcher.py --test

# Check Needs_Action folder
dir AI_Employee_Vault\Needs_Action\
# → EMAIL_*.md files (agar unread emails hain)
```

---

## 🎯 LinkedIn Setup (Optional for Now)

```bash
cd scripts/linkedin-mcp-server
npm install
npm run auth
```

---

*Last Updated: 2026-03-28 22:38 PKT | Tier: Silver*
