#!/usr/bin/env python3
"""
LinkedIn Automation Orchestrator

Runs all components of the LinkedIn automation system:
1. Email Watcher - Monitors Gmail
2. Claude Processor - Creates LinkedIn drafts
3. Ralph Loop - Publishes approved posts

Usage:
    python orchestrator_linkedin.py          # Run all components
    python orchestrator_linkedin.py --watcher # Run only watcher
    python orchestrator_linkedin.py --processor # Run only processor
    python orchestrator_linkedin.py --ralph   # Run only Ralph loop
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
WATCHER_SCRIPT = SCRIPTS_DIR / "linkedin_automation_watcher.py"
PROCESSOR_SCRIPT = SCRIPTS_DIR / "claude_linkedin_processor.py"
RALPH_SCRIPT = SCRIPTS_DIR / "ralph_linkedin_loop.py"

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
    log_message("\n👋 Shutting down LinkedIn Automation...")
    running = False
    
    # Terminate all processes
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
            log_message(f"🛑 Stopped process: {proc.pid}")
    
    sys.exit(0)


def start_watcher():
    """Start the Email Watcher"""
    log_message("📧 Starting Email Watcher...")

    proc = subprocess.Popen(
        [sys.executable, str(WATCHER_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )

    # Stream output
    def stream_output():
        for line in proc.stdout:
            if running:
                print(f"  [Watcher] {line.strip()}")

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()

    return proc


def start_processor():
    """Start the Claude Processor"""
    log_message("🤖 Starting Claude Processor...")

    proc = subprocess.Popen(
        [sys.executable, str(PROCESSOR_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )

    # Stream output
    def stream_output():
        for line in proc.stdout:
            if running:
                print(f"  [Processor] {line.strip()}")

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()

    return proc


def start_ralph():
    """Start the Ralph Loop"""
    log_message("🔄 Starting Ralph Loop...")

    proc = subprocess.Popen(
        [sys.executable, str(RALPH_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )

    # Stream output
    def stream_output():
        for line in proc.stdout:
            if running:
                print(f"  [Ralph] {line.strip()}")

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()

    return proc


def check_prerequisites():
    """Check if all required components are available"""
    log_message("🔍 Checking prerequisites...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check scripts exist
    if not WATCHER_SCRIPT.exists():
        issues.append(f"Missing: {WATCHER_SCRIPT}")
    if not PROCESSOR_SCRIPT.exists():
        issues.append(f"Missing: {PROCESSOR_SCRIPT}")
    if not RALPH_SCRIPT.exists():
        issues.append(f"Missing: {RALPH_SCRIPT}")
    
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
    
    # Check Gmail credentials (optional)
    credentials_file = SCRIPTS_DIR / "email-mcp-server" / "credentials.json"
    if not credentials_file.exists():
        log_message("⚠️  Gmail credentials not found (Gmail watcher will be disabled)")
        log_message("   Run Gmail auth setup to enable email monitoring")
    
    # Check Anthropic API key (optional)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        log_message("⚠️  ANTHROPIC_API_KEY not set (will use template generation)")
        log_message("   Set API key for Claude AI processing")
    
    if issues:
        log_message("❌ Prerequisites check failed:")
        for issue in issues:
            log_message(f"   - {issue}")
        return False
    
    log_message("✅ Prerequisites check passed")
    return True


def print_status():
    """Print current status of automation"""
    log_message("\n📊 LinkedIn Automation Status")
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
            count = len(list(path.glob("*.md")))
            log_message(f"   {name}: {count} files")
        else:
            log_message(f"   {name}: Not found")
    
    # Check processes
    log_message("\n🔄 Processes:")
    for i, proc in enumerate(processes):
        status = "Running" if proc.poll() is None else "Stopped"
        log_message(f"   Process {i+1}: {status} (PID: {proc.pid})")
    
    log_message("\n" + "=" * 50)


def run_orchestrator(components=None):
    """Run the orchestrator with specified components"""
    global running
    
    log_message("🚀 Starting LinkedIn Automation Orchestrator")
    log_message(f"📁 Vault: {VAULT_DIR}")
    
    # Check prerequisites
    if not check_prerequisites():
        log_message("❌ Fix prerequisites and try again")
        return
    
    # Default: run all components
    if components is None:
        components = ["watcher", "processor", "ralph"]
    
    # Start requested components
    if "watcher" in components:
        processes.append(start_watcher())
        time.sleep(2)
    
    if "processor" in components:
        processes.append(start_processor())
        time.sleep(2)
    
    if "ralph" in components:
        processes.append(start_ralph())
        time.sleep(2)
    
    # Print initial status
    print_status()
    
    log_message("\n✅ LinkedIn Automation is running!")
    log_message("Press Ctrl+C to stop all components")
    
    # Keep running
    while running:
        try:
            time.sleep(10)
            
            # Check if any process died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    log_message(f"⚠️  Process {i+1} died, restarting...")
                    if i == 0 and "watcher" in components:
                        processes[i] = start_watcher()
                    elif i == 1 and "processor" in components:
                        processes[i] = start_processor()
                    elif i == 2 and "ralph" in components:
                        processes[i] = start_ralph()
        
        except KeyboardInterrupt:
            signal_handler(None, None)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Automation Orchestrator")
    parser.add_argument("--watcher", action="store_true", help="Run only Email Watcher")
    parser.add_argument("--processor", action="store_true", help="Run only Claude Processor")
    parser.add_argument("--ralph", action="store_true", help="Run only Ralph Loop")
    parser.add_argument("--status", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Determine components to run
    components = None
    
    if args.watcher:
        components = ["watcher"]
    elif args.processor:
        components = ["processor"]
    elif args.ralph:
        components = ["ralph"]
    elif args.status:
        print_status()
        return
    # Default: run all
    
    # Run orchestrator
    run_orchestrator(components)


if __name__ == "__main__":
    main()
