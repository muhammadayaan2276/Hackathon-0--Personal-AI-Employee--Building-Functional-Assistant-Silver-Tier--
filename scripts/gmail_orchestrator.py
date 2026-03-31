#!/usr/bin/env python3
"""
Gmail Orchestrator - Silver Tier
Only handles Gmail automation (no LinkedIn)

Flow:
1. Gmail Watcher → Fetch emails
2. Email Processor → Create reply drafts
3. Human Approval → Move files
4. Auto Sender → Send approved emails

Usage:
    python gmail_orchestrator.py          # Run all components
    python gmail_orchestrator.py --status # Show status only
"""

import os
import sys
import time
import signal
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPTS_DIR = Path(__file__).parent
VAULT_DIR = SCRIPTS_DIR.parent / "AI_Employee_Vault"

# Component scripts
GMAIL_WATCHER = SCRIPTS_DIR / "gmail_watcher.py"
EMAIL_PROCESSOR = SCRIPTS_DIR / "email_processor.py"
AUTO_SENDER = SCRIPTS_DIR / "gmail_auto_sender.py"
# AUTO_APPROVER = SCRIPTS_DIR / "auto_approver.py"  # Disabled - Human approval required

# Process handles
processes = []
running = True


def log_message(message: str):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    global running
    log_message("\n👋 Stopping Gmail Orchestrator...")
    running = False

    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
            log_message(f"🛑 Stopped process: {proc.pid}")

    sys.exit(0)


def start_gmail_watcher():
    """Start Gmail Watcher"""
    log_message("📧 Starting Gmail Watcher...")

    proc = subprocess.Popen(
        [sys.executable, str(GMAIL_WATCHER)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    def stream_output():
        for line in proc.stdout:
            if running:
                print(f"  [Gmail] {line.strip()}")

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()

    return proc


def start_email_processor():
    """Start Email Processor (AI)"""
    log_message("🤖 Starting Email Processor...")

    proc = subprocess.Popen(
        [sys.executable, str(EMAIL_PROCESSOR)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    def stream_output():
        for line in proc.stdout:
            if running:
                print(f"  [Processor] {line.strip()}")

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()

    return proc


def start_auto_approver():
    """Start Auto Approver (auto-approves reply drafts)"""
    log_message("🤖 Starting Auto Approver...")

    proc = subprocess.Popen(
        [sys.executable, str(AUTO_APPROVER)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    def stream_output():
        for line in proc.stdout:
            if running:
                print(f"  [Approver] {line.strip()}")

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()

    return proc


def start_auto_sender():
    """Start Auto Sender (sends approved emails)"""
    log_message("📤 Starting Auto Sender...")

    proc = subprocess.Popen(
        [sys.executable, str(AUTO_SENDER)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    def stream_output():
        for line in proc.stdout:
            if running:
                print(f"  [Sender] {line.strip()}")

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()

    return proc


def check_prerequisites():
    """Check if all required components are available"""
    log_message("🔍 Checking prerequisites...")

    issues = []

    # Check scripts exist
    if not GMAIL_WATCHER.exists():
        issues.append(f"Missing: {GMAIL_WATCHER}")
    if not EMAIL_PROCESSOR.exists():
        issues.append(f"Missing: {EMAIL_PROCESSOR}")
    if not AUTO_SENDER.exists():
        issues.append(f"Missing: {AUTO_SENDER}")

    # Check vault exists
    if not VAULT_DIR.exists():
        issues.append(f"Missing vault: {VAULT_DIR}")

    # Check required folders
    required_folders = [
        VAULT_DIR / "Needs_Action",
        VAULT_DIR / "Pending_Approval",
        VAULT_DIR / "Approved",
        VAULT_DIR / "Done"
    ]

    for folder in required_folders:
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            log_message(f"📁 Created: {folder}")

    # Check Gmail credentials
    credentials_file = SCRIPTS_DIR / "email-mcp-server" / "credentials.json"
    if not credentials_file.exists():
        log_message("⚠️  Gmail credentials not found")
        log_message("   Run Gmail auth setup to enable email monitoring")

    if issues:
        log_message("❌ Prerequisites check failed:")
        for issue in issues:
            log_message(f"   - {issue}")
        return False

    log_message("✅ Prerequisites check passed")
    return True


def print_status():
    """Print current status of automation"""
    log_message("\n📊 Gmail Automation Status")
    log_message("=" * 50)

    # Check folders
    log_message("\n📁 Folders:")
    folders = {
        "Needs_Action": VAULT_DIR / "Needs_Action",
        "Pending_Approval": VAULT_DIR / "Pending_Approval",
        "Approved": VAULT_DIR / "Approved",
        "Done": VAULT_DIR / "Done"
    }

    for name, path in folders.items():
        if path.exists():
            email_count = len(list(path.glob("EMAIL_*.md")))
            log_message(f"   {name}: {email_count} emails")
        else:
            log_message(f"   {name}: Not found")

    # Check processes
    log_message("\n🔄 Processes:")
    for i, proc in enumerate(processes):
        status = "Running" if proc.poll() is None else "Stopped"
        log_message(f"   Process {i+1}: {status} (PID: {proc.pid})")

    log_message("\n" + "=" * 50)


def run_orchestrator():
    """Run the orchestrator with all components"""
    global running

    log_message("🚀 Starting Gmail Orchestrator (Silver Tier)")
    log_message(f"📁 Vault: {VAULT_DIR}")

    # Check prerequisites
    if not check_prerequisites():
        log_message("❌ Fix prerequisites and try again")
        return

    # Start all components
    processes.append(start_gmail_watcher())
    time.sleep(2)

    processes.append(start_email_processor())
    time.sleep(2)

    # Auto Approver DISABLED - Human must manually move files from Pending_Approval to Approved
    # processes.append(start_auto_approver())
    # time.sleep(2)

    processes.append(start_auto_sender())
    time.sleep(2)

    # Print initial status
    print_status()

    log_message("\n✅ Gmail Automation is running!")
    log_message("Press Ctrl+C to stop all components")

    # Keep running
    while running:
        try:
            time.sleep(10)

            # Check if any process died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    log_message(f"⚠️  Process {i+1} died, restarting...")
                    if i == 0:
                        processes[i] = start_gmail_watcher()
                    elif i == 1:
                        processes[i] = start_email_processor()
                    elif i == 2:
                        processes[i] = start_auto_sender()

        except KeyboardInterrupt:
            signal_handler(None, None)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Automation Orchestrator")
    parser.add_argument("--status", action="store_true", help="Show current status")

    args = parser.parse_args()

    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.status:
        print_status()
        return

    # Run orchestrator
    run_orchestrator()


if __name__ == "__main__":
    main()
