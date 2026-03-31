#!/usr/bin/env python3
"""
Auto Approver for Gmail
Automatically moves files from Pending_Approval to Approved
No human intervention needed!

Usage:
    python auto_approver.py          # Run continuously
    python auto_approver.py --once   # Approve once and exit
"""

import os
import sys
import time
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
VAULT_DIR = Path(__file__).parent.parent / "AI_Employee_Vault"
PENDING_APPROVAL_DIR = VAULT_DIR / "Pending_Approval"
APPROVED_DIR = VAULT_DIR / "Approved"
LOGS_DIR = VAULT_DIR / "Logs"

# Ensure directories exist
for dir_path in [APPROVED_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def log_message(message: str):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"

    try:
        print(log_line)
    except UnicodeEncodeError:
        print(log_line.encode('cp1252', errors='replace').decode('cp1252'))

    log_file = LOGS_DIR / f"auto_approver_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{log_line}")


def auto_approve():
    """Move all files from Pending_Approval to Approved"""
    if not PENDING_APPROVAL_DIR.exists():
        return 0

    # Find all email reply files AND original email files
    reply_files = list(PENDING_APPROVAL_DIR.glob("EMAIL_REPLY_*.md"))
    original_files = list(PENDING_APPROVAL_DIR.glob("EMAIL_*.md"))
    
    # Remove duplicates (EMAIL_REPLY_*.md should not be in original_files)
    original_files = [f for f in original_files if not f.name.startswith("EMAIL_REPLY_")]
    
    all_files = reply_files + original_files
    moved = 0

    for file in all_files:
        try:
            dest = APPROVED_DIR / file.name
            shutil.move(str(file), str(dest))
            log_message(f"✅ Auto-approved: {file.name}")
            log_message(f"   📁 Moved: Pending_Approval → Approved")
            moved += 1
        except Exception as e:
            log_message(f"❌ Error moving {file.name}: {e}")

    return moved


def run_auto_approver():
    """Main auto approver loop"""
    log_message("🚀 Starting Auto Approver...")
    log_message(f"📁 Watching: {PENDING_APPROVAL_DIR}")
    log_message(f"📤 Output: {APPROVED_DIR}")

    while True:
        # Approve pending files
        moved = auto_approve()

        if moved > 0:
            log_message(f"✨ Auto-approved {moved} files")

        # Wait for next check (every 10 seconds)
        time.sleep(10)


if __name__ == "__main__":
    try:
        # Run once if called with --once
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            count = auto_approve()
            log_message(f"✅ Approved {count} files")
        else:
            run_auto_approver()
    except KeyboardInterrupt:
        log_message("\n👋 Auto Approver stopped by user")
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        sys.exit(1)
