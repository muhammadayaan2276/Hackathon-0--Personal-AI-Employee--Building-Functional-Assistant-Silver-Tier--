# Personal AI Employee - Silver Tier 🥈

> **Autonomous AI Employee** | Gmail + LinkedIn Automation | Human-in-the-Loop

---

## 🔄 FLOW 1: GMAIL (Auto Send)

```
┌─────────────────────────────────────────────────────────┐
│  1️⃣ EMAIL AAYA (Gmail)                                 │
│     ↓ Automatic                                         │
│  2️⃣ Needs_Action/EMAIL_*.md                           │
│     ↓ Automatic (AI Processor)                          │
│  3️⃣ Pending_Approval/EMAIL_REPLY_*.md  ← AAPKA KAAM! │
│     ↓ YOU MOVE FILE                                     │
│  4️⃣ Approved/EMAIL_REPLY_*.md                         │
│     ↓ Automatic                                         │
│  5️⃣ Done/EMAIL_REPLY_*.md + Gmail pe Reply Sent! ✅   │
└─────────────────────────────────────────────────────────┘
```

### Gmail Steps

```bash
# Step 1: Start Orchestrator
cd "C:\Users\pc\Desktop\desktop-tutorial\Hackathon-0--Personal-AI-Employee--Bronze-Tier"
set GEMINI_API_KEY=YOUR_KEY
chcp 65001
python scripts\gmail_orchestrator.py

# Step 2: Gmail se email bhejo (apne hi address pe)

# Step 3: Wait 30 seconds

# Step 4: Check Pending_Approval
dir AI_Employee_Vault\Pending_Approval\

# Step 5: Obsidian mein file move karo → Approved/

# Step 6: Wait 30 seconds → Reply sent! ✅
```

---

## 🔄 FLOW 2: LINKEDIN (Manual Control)

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: Email create karo                              │
│  📁 Needs_Action/EMAIL_test.md                          │
│     ↓                                                   │
│  Step 2: Processor chalao                               │
│  ▶️ python scripts\claude_linkedin_processor.py --once │
│     ↓                                                   │
│  Step 3: Draft create hua                               │
│  📁 Pending_Approval/LINKEDIN_POST_*.md                 │
│     ↓                                                   │
│  Step 4: YOU approve (Obsidian mein move karo)          │
│  📁 Approved/LINKEDIN_POST_*.md                         │
│     ↓                                                   │
│  ⚠️ YAHAN RUK JAO! (Post abhi publish NAHI hui)        │
│     ↓                                                   │
│  Step 5: Jab ready ho, tab publish command chalao       │
│  ▶️ python scripts\ralph_linkedin_loop.py --once        │
│     ↓                                                   │
│  ✅ Post published!                                     │
│  📁 Done/LINKEDIN_POST_*.md                             │
└─────────────────────────────────────────────────────────┘
```

### LinkedIn Steps

```bash
# Step 1: Create test email in Needs_Action

# Step 2: Run processor
python scripts\claude_linkedin_processor.py --once

# Step 3: Check draft
dir AI_Employee_Vault\Pending_Approval\

# Step 4: Approve (Obsidian mein move karo → Approved/)

# Step 5: Publish when ready
python scripts\ralph_linkedin_loop.py --once

# ✅ Post published!
```

---

## 📁 FOLDERS

| Folder | Purpose |
|--------|---------|
| `Needs_Action/` | New emails (auto-created) |
| `Pending_Approval/` | Drafts waiting for YOU ⭐ |
| `Approved/` | Move approved files here |
| `Done/` | Completed tasks |

---

## 📋 QUICK COMMANDS

```bash
# Gmail Auth
python scripts/gmail_watcher.py --auth

# Gmail Orchestrator
python scripts\gmail_orchestrator.py

# LinkedIn Processor
python scripts\claude_linkedin_processor.py --once

# LinkedIn Publisher
python scripts\ralph_linkedin_loop.py --once

# Check pending
dir AI_Employee_Vault\Pending_Approval\
```

---

## 👤 YOUR JOB

1. **Check:** `Pending_Approval/` folder
2. **Move:** Approved files → `Approved/`
3. **LinkedIn:** Run `ralph_linkedin_loop.py --once` after approval

---

## 📚 GUIDES

- [START_HERE.md](./START_HERE.md)
- [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)

---

**Status:** ✅ Silver | **Vault:** `AI_Employee_Vault`
