# 🚀 PM2 Setup - Complete Guide (Windows)

## Step 3: Watchers ko Alive karo

---

## 📋 Pre-Check: Kya Sab Hai?

```bash
# 1. Node.js installed hai?
node --version

# 2. Python installed hai?
python --version

# 3. PM2 installed hai?
pm2 --version
```

**Agar PM2 nahi hai to install karo:**
```bash
npm install -g pm2
```

---

## 🚀 Commands Run Karo (Step-by-Step)

### Step 1: Project Root Mein Jao

```bash
cd "C:\Users\pc\Desktop\desktop-tutorial\Hackathon-0--Personal-AI-Employee--Building-Autonomous--FTEs--Bronze-Tier-- - Copy"
```

### Step 2: Dependencies Install Karo

```bash
# Python dependencies
pip install -r requirements.txt
```

### Step 3: PM2 Se Sab Services Start Karo

```bash
# Ecosystem config se sab start hoga
pm2 start ecosystem.config.json
```

**Ya individually start karna hai to:**

```bash
# Gmail Watcher (every 2 min)
pm2 start scripts/gmail_watcher.py --interpreter python --name "gmail-watcher"

# Orchestrator (every 5 min)
pm2 start scripts/orchestrator.py --interpreter python --name "orchestrator"
```

### Step 4: Status Check Karo

```bash
pm2 status
```

**Expected Output:**
```
┌────┬─────────────────────┬──────────┬──────┬───────────┬──────────┬──────────┐
│ id │ name                │ mode     │ ↺    │ status    │ cpu      │ memory   │
├────┼─────────────────────┼──────────┼──────┼───────────┼──────────┼──────────┤
│ 0  │ gmail-watcher       │ fork     │ 0    │ online    │ 0%       │ 50mb     │
│ 1  │ orchestrator        │ fork     │ 0    │ online    │ 0%       │ 45mb     │
└────┴─────────────────────┴──────────┴──────┴───────────┴──────────┴──────────┘
```

### Step 5: Logs Dekho

```bash
# Real-time logs
pm2 logs

# Sirf gmail watcher logs
pm2 logs gmail-watcher

# Last 100 lines
pm2 logs --lines 100
```

### Step 6: Auto-Start on Boot Setup

```bash
# PM2 startup configure karo
pm2 startup

# Current process list save karo
pm2 save
```

**Output:**
```
[PM2] Init System found: windows
Platform: windows
```

---

## 📊 Useful PM2 Commands

```bash
# Status dekhna
pm2 status

# Logs dekhna
pm2 logs

# Restart karna
pm2 restart all

# Stop karna
pm2 stop all

# Delete karna
pm2 delete all

# Resources monitor karna
pm2 monit

# Specific service restart
pm2 restart gmail-watcher
```

---

## 🧪 Test Commands

```bash
# Gmail watcher test run (without PM2)
python scripts/gmail_watcher.py --test

# Orchestrator test run
python scripts/orchestrator.py --once

# Status check
python scripts/orchestrator.py --status
```

---

## 🔧 Troubleshooting

### "Python not found"

```bash
# Python path check karo
where python

# Agar python3 hai to
pm2 start scripts/gmail_watcher.py --interpreter python3 --name "gmail-watcher"
```

### "Module not found"

```bash
# Dependencies reinstall karo
pip install -r requirements.txt --upgrade
```

### "PM2 not recognized"

```bash
# PM2 install karo
npm install -g pm2

# Path refresh karo (new terminal kholo)
```

### Service baar baar restart ho rahi hai

```bash
# Logs check karo
pm2 logs gmail-watcher --err

# Test run manually
python scripts/gmail_watcher.py --test
```

---

## ✅ Verification Checklist

```bash
# 1. PM2 services running hain?
pm2 status
# → Green "online" status hona chahiye

# 2. Logs aa rahe hain?
pm2 logs --lines 20
# → Recent timestamps hone chahiye

# 3. Vault files update ho rahe hain?
dir AI_Employee_Vault\Logs\
# → New log files ban rahe hain

# 4. Needs_Action folder check karo
dir AI_Employee_Vault\Needs_Action\
# → EMAIL_*.md files (agar unread emails hain)
```

---

## 🎯 Quick Start Script

**One command se sab start karna hai to:**

```bash
# Windows batch file run karo
scripts\start-all.bat
```

**Ya Linux/Mac:**
```bash
bash scripts/start-all.sh
```

---

## 📁 File Locations After Start

```
Project Root/
├── AI_Employee_Vault/
│   ├── Logs/
│   │   ├── gmail_watcher_2026-03-28.log    ✅ New logs
│   │   ├── orchestrator_2026-03-28.log     ✅ New logs
│   │   └── pm2_*.log                       ✅ PM2 logs
│   ├── Needs_Action/
│   │   └── EMAIL_*.md                      ✅ New emails
│   └── .orchestrator_status.json           ✅ Health status
└── token.json                              ✅ Created after auth
```

---

## 🚀 Next: LinkedIn Authentication

```bash
cd scripts/linkedin-mcp-server
npm install
npm run auth
```

---

*Last Updated: 2026-03-28 | Tier: Silver*
