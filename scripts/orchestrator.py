#!/usr/bin/env python3
"""
Master Orchestrator for Silver Tier Personal AI Employee

Coordinates all watchers and the reasoning engine.
Designed to run continuously with PM2 or as a system service.

Components:
- Gmail Watcher (every 2 minutes)
- Reasoning Engine (every 5 minutes)
- LinkedIn Post Publisher (on approval)
- Health checks and logging
"""

import os
import sys
import time
import logging
import subprocess
import signal
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread, Event
import json

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
VAULT_DIR = PROJECT_ROOT / "AI_Employee_Vault"
LOGS_DIR = VAULT_DIR / "Logs"

# Poll intervals (seconds)
GMAIL_POLL_INTERVAL = 120      # 2 minutes
REASONING_POLL_INTERVAL = 300  # 5 minutes
HEALTH_CHECK_INTERVAL = 60     # 1 minute

# Component paths
GMAIL_WATCHER_SCRIPT = SCRIPT_DIR / "gmail_watcher.py"
REASONING_SCRIPT = SCRIPT_DIR / "orchestrator.py"

# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging():
    """Configure logging to file and console."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    log_file = LOGS_DIR / f"orchestrator_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# =============================================================================
# Health Status
# =============================================================================

HEALTH_STATUS = {
    "orchestrator": {
        "status": "starting",
        "started_at": None,
        "last_check": None,
    },
    "gmail_watcher": {
        "status": "stopped",
        "pid": None,
        "last_run": None,
        "errors": 0,
    },
    "reasoning_engine": {
        "status": "stopped",
        "pid": None,
        "last_run": None,
        "errors": 0,
    },
}

# =============================================================================
# Component Runner Class
# =============================================================================

class ComponentRunner:
    """Runs and monitors a component script."""
    
    def __init__(self, name: str, script: Path, interval: int):
        self.name = name
        self.script = script
        self.interval = interval
        self.stop_event = Event()
        self.thread = None
        self.last_run = None
        self.error_count = 0
        self.is_running = False
        
    def run_once(self):
        """Run the component once."""
        try:
            logger.info(f"Running {self.name}...")
            
            if not self.script.exists():
                logger.warning(f"Script not found: {self.script}")
                return False
            
            # Run as subprocess
            result = subprocess.run(
                [sys.executable, str(self.script), "--test"],
                capture_output=True,
                text=True,
                timeout=min(self.interval - 10, 60)  # Max 60s timeout
            )
            
            if result.returncode == 0:
                logger.info(f"{self.name} completed successfully")
                self.last_run = datetime.now()
                self.error_count = 0
                return True
            else:
                logger.error(f"{self.name} failed: {result.stderr}")
                self.error_count += 1
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"{self.name} timed out")
            self.error_count += 1
            return False
        except Exception as e:
            logger.error(f"{self.name} error: {e}")
            self.error_count += 1
            return False
    
    def run_loop(self):
        """Continuous run loop."""
        logger.info(f"Starting {self.name} loop (interval: {self.interval}s)")
        
        while not self.stop_event.is_set():
            self.is_running = True
            self.run_once()
            self.is_running = False
            
            # Wait for next interval
            self.stop_event.wait(self.interval)
        
        logger.info(f"{self.name} loop stopped")
    
    def start(self):
        """Start the component in a background thread."""
        if self.thread and self.thread.is_alive():
            logger.warning(f"{self.name} already running")
            return
        
        self.stop_event.clear()
        self.thread = Thread(target=self.run_loop, daemon=True)
        self.thread.start()
        logger.info(f"{self.name} started")
    
    def stop(self):
        """Stop the component."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=10)
        logger.info(f"{self.name} stopped")

# =============================================================================
# Orchestrator Class
# =============================================================================

class Orchestrator:
    """Main orchestrator for all AI Employee components."""
    
    def __init__(self):
        self.components = {}
        self.stop_event = Event()
        self.health_thread = None
        
        # Initialize components
        self.components['gmail_watcher'] = ComponentRunner(
            'Gmail Watcher', GMAIL_WATCHER_SCRIPT, GMAIL_POLL_INTERVAL
        )
        
        self.components['reasoning_engine'] = ComponentRunner(
            'Reasoning Engine', REASONING_SCRIPT, REASONING_POLL_INTERVAL
        )
        
        # Update health status
        HEALTH_STATUS["orchestrator"]["started_at"] = datetime.now().isoformat()
    
    def start_all(self):
        """Start all components."""
        logger.info("=" * 60)
        logger.info("Starting AI Employee Orchestrator")
        logger.info("=" * 60)
        
        for name, component in self.components.items():
            component.start()
            HEALTH_STATUS[name]["status"] = "running"
        
        # Start health check thread
        self.health_thread = Thread(target=self._health_check_loop, daemon=True)
        self.health_thread.start()
        
        HEALTH_STATUS["orchestrator"]["status"] = "running"
        logger.info("All components started")
    
    def stop_all(self):
        """Stop all components."""
        logger.info("Stopping all components...")
        
        for name, component in self.components.items():
            component.stop()
            HEALTH_STATUS[name]["status"] = "stopped"
        
        self.stop_event.set()
        HEALTH_STATUS["orchestrator"]["status"] = "stopped"
        logger.info("All components stopped")
    
    def _health_check_loop(self):
        """Periodic health check."""
        while not self.stop_event.is_set():
            try:
                self._perform_health_check()
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            self.stop_event.wait(HEALTH_CHECK_INTERVAL)
    
    def _perform_health_check(self):
        """Perform health check on all components."""
        timestamp = datetime.now().isoformat()
        HEALTH_STATUS["orchestrator"]["last_check"] = timestamp
        
        for name, component in self.components.items():
            status = {
                "status": "running" if component.is_running else "idle",
                "last_run": component.last_run.isoformat() if component.last_run else None,
                "errors": component.error_count,
            }
            HEALTH_STATUS[name].update(status)
            
            # Log if component has errors
            if component.error_count > 0:
                logger.warning(f"{name} has {component.error_count} consecutive errors")
        
        # Write health status to file
        self._write_health_status()
    
    def _write_health_status(self):
        """Write health status to JSON file."""
        status_file = VAULT_DIR / ".orchestrator_status.json"
        try:
            with open(status_file, 'w') as f:
                json.dump(HEALTH_STATUS, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write health status: {e}")
    
    def get_status(self):
        """Get current orchestrator status."""
        return HEALTH_STATUS
    
    def run_forever(self):
        """Run the orchestrator forever."""
        self.start_all()
        
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.stop_all()

# =============================================================================
# Signal Handlers
# =============================================================================

orchestrator_instance = None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    if orchestrator_instance:
        orchestrator_instance.stop_all()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point."""
    global orchestrator_instance
    
    logger.info("=" * 60)
    logger.info("AI Employee Master Orchestrator v1.0")
    logger.info("=" * 60)
    
    # Verify vault directory
    if not VAULT_DIR.exists():
        logger.error(f"Vault directory not found: {VAULT_DIR}")
        sys.exit(1)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            # Show current status
            status_file = VAULT_DIR / ".orchestrator_status.json"
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f, indent=2)
                    print(json.dumps(status, indent=2))
            else:
                print("No status file found. Orchestrator may not be running.")
            return
        
        elif sys.argv[1] == "--once":
            # Run all components once (for testing)
            logger.info("Running all components once (test mode)")
            
            for name, component in [
                ('Gmail Watcher', ComponentRunner('Gmail Watcher', GMAIL_WATCHER_SCRIPT, 60)),
                ('Reasoning Engine', ComponentRunner('Reasoning Engine', REASONING_SCRIPT, 60)),
            ]:
                logger.info(f"Running {name}...")
                component.run_once()
            
            logger.info("All components completed")
            return
    
    # Start orchestrator
    orchestrator_instance = Orchestrator()
    orchestrator_instance.run_forever()

if __name__ == "__main__":
    main()
