# Gmail Automation - Task Scheduler Setup Guide

## Method 1: Manual Setup (No Admin Required)

### Step 1: Open Task Scheduler
1. Press `Windows + R`
2. Type: `taskschd.msc`
3. Press Enter

### Step 2: Create Basic Task
1. Click **"Create Basic Task..."** in right panel
2. Name: `Gmail Automation`
3. Description: `Automatically start Gmail watcher on login`
4. Click **Next**

### Step 3: Set Trigger
1. Select: **"When I log on"**
2. Click **Next**

### Step 4: Set Action
1. Select: **"Start a program"**
2. Click **Next**
3. Browse and select: `start_gmail_automation.bat`
   - Location: `C:\Users\pc\Desktop\desktop-tutorial\Hackathon-0--Personal-AI-Employee--Building-Autonomous--FTEs--Bronze-Tier-- - Copy\start_gmail_automation.bat`
4. Click **Next**

### Step 5: Finish
1. Check: **"Open the Properties dialog..."**
2. Click **Finish**

### Step 6: Advanced Settings
In Properties dialog:
1. ✅ Check: **"Run with highest privileges"**
2. Tab: **Conditions**
   - ✅ Uncheck: "Start the task only if the computer is on AC power"
3. Tab: **Settings**
   - ✅ Check: "Allow task to be run on demand"
   - ✅ Check: "If the task fails, restart every: 1 minute"
   - Set: "Attempt to restart up to: 3 times"
4. Click **OK**

---

## Method 2: PowerShell (Run as Administrator)

1. Right-click PowerShell → **Run as Administrator**
2. Run this command:

```powershell
$taskName = "Gmail Automation"
$taskPath = "C:\Users\pc\Desktop\desktop-tutorial\Hackathon-0--Personal-AI-Employee--Building-Autonomous--FTEs--Bronze-Tier-- - Copy"
$batchFile = "$taskPath\start_gmail_automation.bat"

$trigger = New-ScheduledTaskTrigger -AtLogOn
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batchFile`"" -WorkingDirectory $taskPath
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Principal $principal -Force

Write-Host "✅ Gmail Automation task created successfully!"
```

---

## Method 3: Quick Start (Manual)

Agar Task Scheduler setup nahi karna, toh ye shortcut use karo:

### Create Desktop Shortcut:
1. Right-click on Desktop → **New** → **Shortcut**
2. Location: 
   ```
   C:\Users\pc\Desktop\desktop-tutorial\Hackathon-0--Personal-AI-Employee--Building-Autonomous--FTEs--Bronze-Tier-- - Copy\start_gmail_automation.bat
   ```
3. Name: `Start Gmail Automation`
4. Right-click shortcut → **Properties**
5. Click **"Run as administrator"**
6. Click **OK**

### Usage:
Jab bhi automation start karna ho, shortcut pe double-click karo!

---

## Verify Setup

### Check if task exists:
```cmd
schtasks /Query /TN "Gmail Automation"
```

### Run task manually:
```cmd
schtasks /Run /TN "Gmail Automation"
```

### Delete task (if needed):
```cmd
schtasks /Delete /TN "Gmail Automation" /F
```

---

## Startup Folder Alternative ✅ (COMPLETED)

**Already configured!** A PowerShell script has been created to automatically add the shortcut to Startup.

### Run the Script:
```powershell
powershell -ExecutionPolicy Bypass -File "create_startup_shortcut.ps1"
```

### What it does:
- Creates a shortcut in Windows Startup folder
- Points to `start_gmail_automation.bat`
- Runs automatically on Windows login

### Startup Folder Location:
```
C:\Users\pc\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```

### Manual Alternative:
1. Press `Windows + R`
2. Type: `shell:startup`
3. Press Enter
4. Create shortcut to `start_gmail_automation.bat`

---

## Quick Commands Reference

| Action | Command |
|--------|---------|
| **Open Task Scheduler** | `taskschd.msc` |
| **Open Startup Folder** | `shell:startup` |
| **Query Task** | `schtasks /Query /TN "Gmail Automation"` |
| **Run Task** | `schtasks /Run /TN "Gmail Automation"` |
| **Delete Task** | `schtasks /Delete /TN "Gmail Automation" /F` |
| **Run Startup Script** | `powershell -File create_startup_shortcut.ps1` |

---

## ✅ Complete!

**3 Methods Available:**

| Method | Admin Required | Auto-Start | Difficulty |
|--------|---------------|------------|------------|
| **Task Scheduler** | ✅ Yes | On Login | Medium |
| **PowerShell Script** | ❌ No | On Login | Easy |
| **Desktop Shortcut** | ❌ No | Manual | Easiest |

**Recommended:** Use the **PowerShell Script** (`create_startup_shortcut.ps1`) - No admin needed and runs on login!

Ab Gmail Automation automatically start hoga jab aap login karoge! 🚀
