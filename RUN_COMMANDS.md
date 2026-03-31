# 🚀 Ready-to-Run Commands - AI Employee Silver Tier

## Quick Start (Copy & Paste)

### 1. Install & Start Everything

```bash
# Install PM2 globally
npm install -g pm2

# Install Python dependencies
pip install -r requirements.txt

# Start all services
pm2 start ecosystem.config.json

# Check status
pm2 status
```

---

### 2. View Logs

```bash
# Real-time logs (all services)
pm2 logs

# Last 100 lines
pm2 logs --lines 100

# Orchestrator logs only
pm2 logs ai-employee-orchestrator

# Gmail watcher logs only
pm2 logs ai-employee-gmail-watcher
```

---

### 3. Daily LinkedIn Post Check (Cron)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 8 AM):
0 8 * * * cd /path/to/project && python3 scripts/linkedin_post_checker.py >> AI_Employee_Vault/Logs/cron_linkedin.log 2>&1
```

### Alternative: PM2 Schedule

```bash
# Install scheduler
pm2 install pm2-schedule

# Add scheduled job (daily at 8 AM)
pm2 start scripts/linkedin_post_checker.py --name ai-employee-linkedin --cron "0 8 * * *"
```

---

## Complete Command Reference

### PM2 Management

```bash
# Start all services
pm2 start ecosystem.config.json

# Start individual services
pm2 start scripts/orchestrator.py --name ai-employee-orchestrator --interpreter python3
pm2 start scripts/gmail_watcher.py --name ai-employee-gmail-watcher --interpreter python3

# View status
pm2 status
pm2 list

# Restart services
pm2 restart all
pm2 restart ai-employee-orchestrator
pm2 restart ai-employee-gmail-watcher

# Stop services
pm2 stop all
pm2 stop ai-employee-orchestrator

# Delete from PM2
pm2 delete all
pm2 delete ai-employee-orchestrator

# Auto-start on reboot
pm2 startup
pm2 save

# Monitor resources
pm2 monit
```

### Cron Jobs

```bash
# LinkedIn post checker - Daily at 8 AM
0 8 * * * cd /path/to/project && python3 scripts/linkedin_post_checker.py

# Health check - Every hour
0 * * * * cd /path/to/project && python3 scripts/orchestrator.py --status

# Log cleanup - Weekly on Sunday at 2 AM
0 2 * * 0 find /path/to/project/AI_Employee_Vault/Logs -name "*.log" -mtime +30 -delete
```

### Windows Task Scheduler

```powershell
# LinkedIn post checker - Daily at 8 AM
$action = New-ScheduledTaskAction -Execute "python3" -Argument "scripts/linkedin_post_checker.py" -WorkingDirectory "C:\path\to\project"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "AI-Employee-LinkedIn" -Action $action -Trigger $trigger
```

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PM2 Process Manager                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ai-employee-orchestrator (every 5 min)                 │
│  ├── Runs reasoning engine                              │
│  ├── Processes /Needs_Action/ items                     │
│  ├── Creates approval files                             │
│  └── Executes approved actions                          │
│                                                         │
│  ai-employee-gmail-watcher (every 2 min)                │
│  ├── Monitors Gmail for important emails                │
│  ├── Creates .md files in /Needs_Action/                │
│  └── Tracks processed emails                            │
│                                                         │
│  ai-employee-linkedin (daily at 8 AM - cron)            │
│  ├── Checks /Approved/ for LinkedIn posts               │
│  ├── Triggers publishing via MCP                        │
│  └── Logs publishing activity                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## One-Liner Status Check

```bash
echo "=== AI Employee Status ===" && pm2 status && echo "" && echo "=== Recent Activity ===" && pm2 logs --lines 20 --nostream
```

---

## Troubleshooting

```bash
# Service won't start - check errors
pm2 logs ai-employee-orchestrator --err

# Test scripts manually
python3 scripts/orchestrator.py --test
python3 scripts/gmail_watcher.py --test

# Force restart
pm2 restart all --update-env

# Clear all and start fresh
pm2 delete all && pm2 start ecosystem.config.json
```

---

## File Locations

| File | Purpose |
|------|---------|
| `ecosystem.config.json` | PM2 configuration |
| `scripts/orchestrator.py` | Main reasoning loop (5 min) |
| `scripts/gmail_watcher.py` | Gmail watcher (2 min) |
| `scripts/linkedin_post_checker.py` | Daily LinkedIn check |
| `AI_Employee_Vault/Logs/` | All log files |
| `AI_Employee_Vault/.orchestrator_status.json` | Health status |

---

*Copy any command block and paste directly into your terminal.*
