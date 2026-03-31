# 📧 Gmail Credentials - Setup Complete Guide

## ✅ Status: Credentials Found!

Aapke paas already credentials file hai. Bas chhota sa setup baaki hai.

---

## Step 1: Credentials File Verify

**File Location:**
```
gmail_credentials.json → Project root mein hai ✅
```

**Details:**
- **Project ID:** hackathon-0-silver-tier-491413
- **Client ID:** 998564885592-hvol7lisnqpacj862flts0vqn8ajdmq9.apps.googleusercontent.com
- **Type:** Installed Application (Desktop)

---

## Step 2: Install Python Dependencies

```bash
# Navigate to project root
cd "C:\Users\pc\Desktop\desktop-tutorial\Hackathon-0--Personal-AI-Employee--Building-Autonomous--FTEs--Bronze-Tier-- - Copy"

# Install Gmail API dependencies
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed google-auth-2.x.x google-auth-oauthlib-1.x.x google-api-python-client-2.x.x
```

---

## Step 3: First-Time Authentication

Gmail watcher ko pehli baar chalane par browser khulega:

```bash
# Run Gmail watcher with auth flag
python scripts/gmail_watcher.py --auth
```

**What Happens:**

1. ✅ Browser automatically khulega
2. ✅ Google login page aayega
3. ✅ Apna Gmail account se login karo
4. ✅ "Allow" permissions dene honge:
   - Read emails
   - Send emails
   - Manage drafts
5. ✅ Authorization code milega
6. ✅ Code paste karna hai terminal mein
7. ✅ `token.json` automatically ban jayega

---

## Step 4: Test Gmail Watcher

```bash
# Test run (single poll)
python scripts/gmail_watcher.py --test
```

**Expected Output:**
```
INFO - Gmail Watcher for Personal AI Employee (Silver Tier)
INFO - Starting Gmail poll cycle
INFO - Found X important unread emails
INFO - Created action file: EMAIL_20260328_103000_Subject.md
INFO - Poll cycle complete. Processed X new emails
```

---

## Step 5: Verify Files Created

Authentication ke baad ye files banengi:

```
Project Root/
├── gmail_credentials.json    ✅ Already exists
├── token.json                ✅ Created after auth
└── AI_Employee_Vault/
    └── Needs_Action/
        └── EMAIL_*.md        ✅ Created on first poll
```

---

## 🔧 Troubleshooting

### "Credentials file not found"

```bash
# Verify file exists
dir gmail_credentials.json

# If missing, copy from credentials.json
copy credentials.json gmail_credentials.json
```

### "Token expired" ya "Invalid credentials"

```bash
# Delete old token
del token.json

# Re-authenticate
python scripts/gmail_watcher.py --auth
```

### "Gmail API not enabled"

1. Google Cloud Console kholo: https://console.cloud.google.com
2. Select project: `hackathon-0-silver-tier-491413`
3. APIs & Services → Library
4. Search "Gmail API" → Enable

### Browser nahi khul raha

```bash
# Manual auth URL copy karke browser mein paste karna
python scripts/gmail_watcher.py --auth
# URL display hoga → copy → browser mein paste
```

---

## 📋 Gmail API Permissions

Jo permissions request hongi:

| Permission | Why Needed |
|------------|------------|
| Read emails | Important emails detect karne ke liye |
| Send emails | Reply bhejne ke liye |
| Manage drafts | Draft replies create karne ke liye |
| Mark as read | Processed emails track karne ke liye |

**Security:**
- ✅ Sirf aapke account pe access
- ✅ Kisi third-party ko data share nahi hota
- ✅ Token.json local machine pe rehta hai
- ✅ Kabhi bhi revoke kar sakte ho

---

## 🚀 Quick Start Commands

```bash
# Full authentication
python scripts/gmail_watcher.py --auth

# Test run
python scripts/gmail_watcher.py --test

# Run continuously (every 2 min)
python scripts/gmail_watcher.py

# Via PM2 (recommended)
pm2 start scripts/gmail_watcher.py --name ai-employee-gmail --interpreter python
```

---

## ✅ Next Step: LinkedIn Authentication

Gmail setup ke baad LinkedIn credentials setup karna:

```bash
cd scripts/linkedin-mcp-server
npm install
npm run auth
```

---

## 📞 Support

Agar koi issue ho:

1. Check logs: `AI_Employee_Vault/Logs/gmail_watcher_*.log`
2. Verify credentials file format
3. Check Gmail API enabled hai
4. Token delete karke re-authenticate karo

---

*Last Updated: 2026-03-28 | Tier: Silver*
