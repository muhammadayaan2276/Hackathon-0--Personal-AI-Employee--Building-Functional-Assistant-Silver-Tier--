# AI Employee Skills

This document lists all the skills (capabilities) of our Personal AI Employee.

---

## 📧 Skill 1: Gmail Watcher

**File:** `scripts/gmail_watcher.py`

**Capability:** Monitors Gmail for new important/unread emails

**Trigger:** Every 30 seconds

**Output:** Creates `EMAIL_*.md` files in `Needs_Action/` folder

**Usage:**
```bash
python scripts/gmail_watcher.py
```

---

## 🤖 Skill 2: Email Processor (AI Reply Generator)

**File:** `scripts/email_processor.py`

**Capability:** Reads emails and creates AI-generated reply drafts

**Input:** `Needs_Action/EMAIL_*.md`

**Output:** `Pending_Approval/EMAIL_REPLY_*.md`

**Usage:**
```bash
python scripts/email_processor.py
```

---

## 📤 Skill 3: Gmail Auto Sender

**File:** `scripts/gmail_auto_sender.py`

**Capability:** Sends approved emails via Gmail API

**Input:** `Approved/EMAIL_REPLY_*.md`

**Output:** Email sent + file moved to `Done/`

**Usage:**
```bash
python scripts/gmail_auto_sender.py
```

---

## 💼 Skill 4: LinkedIn Post Generator

**File:** `scripts/claude_linkedin_processor.py`

**Capability:** Creates LinkedIn post drafts from emails

**Input:** `Needs_Action/EMAIL_*.md`

**Output:** `Pending_Approval/LINKEDIN_POST_*.md`

**Usage:**
```bash
python scripts/claude_linkedin_processor.py --once
```

---

## 🚀 Skill 5: LinkedIn Auto Publisher (Ralph Loop)

**File:** `scripts/ralph_linkedin_loop.py`

**Capability:** Publishes approved LinkedIn posts via browser automation

**Input:** `Approved/LINKEDIN_POST_*.md`

**Output:** Post published on LinkedIn + file moved to `Done/`

**Usage:**
```bash
python scripts/ralph_linkedin_loop.py
```

---

## 🎯 Skill 6: Gmail Orchestrator

**File:** `scripts/gmail_orchestrator.py`

**Capability:** Runs all Gmail automation components together

**Components:**
- Gmail Watcher
- Email Processor
- Gmail Auto Sender

**Usage:**
```bash
python scripts/gmail_orchestrator.py
```

---

## 🎯 Skill 7: LinkedIn Orchestrator

**File:** `scripts/orchestrator_linkedin.py`

**Capability:** Runs all LinkedIn automation components together

**Components:**
- Email Watcher
- LinkedIn Processor
- Ralph Loop

**Usage:**
```bash
python scripts/orchestrator_linkedin.py
```

---

## 📋 Human-in-the-Loop Workflow

**For Email Replies:**
1. AI creates draft → `Pending_Approval/EMAIL_REPLY_*.md`
2. Human reviews and moves to → `Approved/`
3. Auto Sender sends email → `Done/`

**For LinkedIn Posts:**
1. AI creates draft → `Pending_Approval/LINKEDIN_POST_*.md`
2. Human reviews and moves to → `Approved/`
3. Ralph Loop publishes → `Done/`

---

## 🛠️ Installation

**Python Dependencies:**
```bash
pip install -r requirements.txt
```

**Required:**
- Python 3.13+
- Node.js v24+
- Gmail API credentials
- Gemini API Key

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/       # New items to process
├── Pending_Approval/   # Awaiting human approval
├── Approved/           # Ready for action
├── Done/               # Completed
├── Plans/              # AI-generated plans
├── Logs/               # Activity logs
└── Dashboard.md        # Real-time status
```
