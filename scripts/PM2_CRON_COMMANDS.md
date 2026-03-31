# AI Employee - PM2 & Cron Commands

## Quick Reference

Copy and run these commands directly in your terminal.

---

## Prerequisites

### Install PM2 (if not already installed)

```bash
# Global install
npm install -g pm2

# Verify installation
pm2 --version
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## PM2 Commands

### Start All Services

```bash
# From project root directory
pm2 start ecosystem.config.json
```

### Start Individual Services

```bash
# Start orchestrator only
pm2 start scripts/orchestrator.py --name ai-employee-orchestrator --interpreter python3

# Start Gmail watcher only
pm2 start scripts/gmail_watcher.py --name ai-employee-gmail-watcher --interpreter python3
```

### Check Status

```bash
# View all services
pm2 status

# View detailed status
pm2 list

# View specific service
pm2 show ai-employee-orchestrator
```

### View Logs

```bash
# All logs
pm2 logs

# Orchestrator logs only
pm2 logs ai-employee-orchestrator

# Gmail watcher logs only
pm2 logs ai-employee-gmail-watcher

# Follow logs in real-time
pm2 logs --lines 100
```

### Restart Services

```bash
# Restart all
pm2 restart all

# Restart specific service
pm2 restart ai-employee-orchestrator
pm2 restart ai-employee-gmail-watcher

# Restart with no delay
pm2 restart all --update-env
```

### Stop Services

```bash
# Stop all
pm2 stop all

# Stop specific service
pm2 stop ai-employee-orchestrator
pm2 stop ai-employee-gmail-watcher
```

### Delete Services

```bash
# Delete all from PM2
pm2 delete all

# Delete specific service
pm2 delete ai-employee-orchestrator
pm2 delete ai-employee-gmail-watcher
```

### Auto-Start on Server Reboot

```bash
# Setup PM2 startup
pm2 startup

# Save current process list
pm2 save
```

### Monitor Resources

```bash
# Real-time monitoring
pm2 monit

# Detailed stats
pm2 monit --chart
```

---

## Cron Commands (Daily LinkedIn Post Check)

### Option 1: Crontab Entry

```bash
# Edit crontab
crontab -e

# Add this line for daily LinkedIn post check at 8:00 AM
0 8 * * * cd /path/to/Hackathon-0--Personal-AI-Employee && python3 scripts/linkedin_post_checker.py >> AI_Employee_Vault/Logs/cron_linkedin.log 2>&1
```

### Option 2: PM2 Schedule (Recommended)

```bash
# Install pm2-schedule if not available
pm2 install pm2-schedule

# Add daily LinkedIn post check at 8:00 AM
pm2 start scripts/linkedin_post_checker.py --name ai-employee-linkedin --interpreter python3 --cron "0 8 * * *"
```

### Option 3: Windows Task Scheduler

```powershell
# Open Task Scheduler
taskschd.msc

# Or create via PowerShell
$action = New-ScheduledTaskAction -Execute "python3" -Argument "scripts/linkedin_post_checker.py" -WorkingDirectory "C:\path\to\Hackathon-0--Personal-AI-Employee"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "AI-Employee-LinkedIn" -Action $action -Trigger $trigger
```

---

## Complete Setup Sequence

### Fresh Installation

```bash
# 1. Navigate to project directory
cd /path/to/Hackathon-0--Personal-AI-Employee

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install PM2
npm install -g pm2

# 4. Start all services
pm2 start ecosystem.config.json

# 5. Verify services are running
pm2 status

# 6. Setup auto-start on reboot
pm2 startup
pm2 save

# 7. View logs
pm2 logs --lines 50
```

### Update Existing Installation

```bash
# 1. Pull latest changes
git pull

# 2. Install new dependencies
pip install -r requirements.txt --upgrade

# 3. Restart all services
pm2 restart all --update-env

# 4. Verify
pm2 status
```

---

## Troubleshooting Commands

### Service Won't Start

```bash
# Check error logs
pm2 logs ai-employee-orchestrator --err

# Check Python path
which python3

# Test script manually
python3 scripts/orchestrator.py --test
```

### High Memory Usage

```bash
# View memory usage
pm2 monit

# Restart with memory limit
pm2 restart ai-employee-orchestrator --max-memory-restart 500M
```

### Check Process IDs

```bash
# Get PIDs
pm2 list

# Or use system commands
ps aux | grep orchestrator
ps aux | grep gmail_watcher
```

### Force Stop and Cleanup

```bash
# Stop all
pm2 stop all

# Delete all
pm2 delete all

# Clear logs
pm2 flush

# Start fresh
pm2 start ecosystem.config.json
```

---

## Health Check Commands

### Check Orchestrator Status

```bash
# Via PM2
pm2 show ai-employee-orchestrator

# Via status file
cat AI_Employee_Vault/.orchestrator_status.json

# Via script
python3 scripts/orchestrator.py --status
```

### Test Individual Components

```bash
# Test Gmail watcher
python3 scripts/gmail_watcher.py --test

# Test orchestrator (run once)
python3 scripts/orchestrator.py --once
```

### View Recent Logs

```bash
# Last 100 lines
tail -n 100 AI_Employee_Vault/Logs/orchestrator_*.log

# Gmail watcher logs
tail -n 100 AI_Employee_Vault/Logs/gmail_watcher_*.log

# PM2 logs
pm2 logs --lines 100 --nostream
```

---

## Production Deployment

### Start in Production Mode

```bash
# Set production environment
export NODE_ENV=production

# Start with PM2
pm2 start ecosystem.config.json --env production

# Verify
pm2 status
```

### Backup Before Update

```bash
# Save PM2 process list
pm2 save

# Backup credentials
cp gmail_credentials.json ~/backup/
cp token.json ~/backup/

# Backup vault
cp -r AI_Employee_Vault ~/backup/
```

### Rollback

```bash
# Stop current
pm2 stop all

# Restore backup
cp ~/backup/gmail_credentials.json .
cp ~/backup/token.json .

# Restart
pm2 start ecosystem.config.json
```

---

## Quick Status Dashboard

```bash
# One-liner to check everything
echo "=== AI Employee Status ===" && \
pm2 status && \
echo "" && \
echo "=== Recent Logs ===" && \
pm2 logs --lines 10 --nostream
```

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PM2 Process Manager                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐       │
│  │ ai-employee-         │    │ ai-employee-         │       │
│  │ orchestrator         │    │ gmail-watcher        │       │
│  │                      │    │                      │       │
│  │ - Runs every 5 min   │    │ - Runs every 2 min   │       │
│  │ - Coordinates all    │    │ - Monitors Gmail     │       │
│  │ - Health checks      │    │ - Creates .md files  │       │
│  └──────────────────────┘    └──────────────────────┘       │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐       │
│  │ ai-employee-         │    │ (Optional)           │       │
│  │ linkedin (cron)      │    │ MCP Servers          │       │
│  │                      │    │ - Gmail MCP          │       │
│  │ - Daily at 8 AM      │    │ - LinkedIn MCP       │       │
│  │ - Checks approvals   │    │                      │       │
│  └──────────────────────┘    └──────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

*Version: 1.0 | Last Updated: 2026-03-28*
