#!/usr/bin/env python3
"""
Gmail Watcher for Silver Tier Personal AI Employee

Monitors Gmail for important unread emails and creates .md files
in the Needs_Action folder for AI processing.

Runs every 2 minutes via cron/task scheduler.
"""

import os
import sys
import json
import logging
import base64
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
import time

# Gmail API dependencies
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# =============================================================================
# Configuration
# =============================================================================

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
VAULT_DIR = PROJECT_ROOT / "AI_Employee_Vault"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
LOGS_DIR = VAULT_DIR / "Logs"
CREDENTIALS_FILE = PROJECT_ROOT / "gmail_credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"
PROCESSED_CACHE = VAULT_DIR / ".processed_emails.json"

# Gmail settings
POLL_INTERVAL_SECONDS = 30  # 30 seconds (fast response)
MAX_RESULTS_PER_POLL = 10
IMPORTANT_LABEL = "IMPORTANT"
UNREAD_LABEL = "UNREAD"

# Scopes for Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging():
    """Configure logging to file and console."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    log_file = LOGS_DIR / f"gmail_watcher_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# =============================================================================
# BaseWatcher Class
# =============================================================================

class BaseWatcher:
    """
    Base class for all watcher scripts in the AI Employee system.
    
    Provides common functionality for monitoring, file creation,
    and processed item tracking.
    """
    
    def __init__(self, name: str, vault_dir: Path, poll_interval: int = 120):
        """
        Initialize the base watcher.
        
        Args:
            name: Name of this watcher (for logging and file naming)
            vault_dir: Path to the Obsidian vault directory
            poll_interval: Seconds between polling cycles
        """
        self.name = name
        self.vault_dir = vault_dir
        self.poll_interval = poll_interval
        self.needs_action_dir = vault_dir / "Needs_Action"
        self.processed_cache_file = vault_dir / f".processed_{name.lower()}.json"
        
        # Ensure directories exist
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        
        # Load processed items cache
        self.processed_items = self._load_processed_cache()
        
        logger.info(f"{self.name} initialized. Poll interval: {poll_interval}s")
    
    def _load_processed_cache(self) -> set:
        """Load the set of processed item IDs from cache file."""
        if self.processed_cache_file.exists():
            try:
                with open(self.processed_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert list to set for O(1) lookups
                    processed = set(data.get('processed_ids', []))
                    logger.info(f"Loaded {len(processed)} processed items from cache")
                    return processed
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load processed cache: {e}")
                return set()
        return set()
    
    def _save_processed_cache(self):
        """Save the processed items cache to file."""
        try:
            with open(self.processed_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'processed_ids': list(self.processed_items),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
            logger.debug("Saved processed items cache")
        except IOError as e:
            logger.error(f"Could not save processed cache: {e}")
    
    def _mark_as_processed(self, item_id: str):
        """Mark an item as processed."""
        self.processed_items.add(item_id)
        self._save_processed_cache()
    
    def _is_processed(self, item_id: str) -> bool:
        """Check if an item has already been processed."""
        return item_id in self.processed_items
    
    def _create_action_file(self, filename: str, content: str) -> Path:
        """
        Create an action file in the Needs_Action folder.
        
        Args:
            filename: Name of the file (without .md extension)
            content: Markdown content to write
            
        Returns:
            Path to the created file
        """
        file_path = self.needs_action_dir / f"{filename}.md"
        
        # Handle duplicate filenames
        counter = 1
        while file_path.exists():
            file_path = self.needs_action_dir / f"{filename}_{counter}.md"
            counter += 1
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Created action file: {file_path.name}")
            return file_path
        except IOError as e:
            logger.error(f"Failed to create action file {filename}: {e}")
            raise
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string for use in filenames."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Limit length
        return name[:100]
    
    def _cleanup_old_cache(self, max_age_days: int = 30):
        """Remove processed IDs older than max_age_days to prevent cache bloat."""
        # For Gmail, we keep all processed IDs to avoid re-processing
        # This method can be overridden for watchers that need cleanup
        pass
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Override this method in subclasses to implement specific monitoring logic.
        """
        logger.info(f"Starting {self.name} watcher loop")
        
        try:
            while True:
                start_time = time.time()
                
                try:
                    self.poll()
                except Exception as e:
                    logger.error(f"Error during poll: {e}", exc_info=True)
                
                # Calculate sleep time to maintain consistent interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.poll_interval - elapsed)
                
                if sleep_time > 0:
                    logger.debug(f"Sleeping for {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info(f"{self.name} watcher stopped by user")
        except Exception as e:
            logger.critical(f"Watcher crashed: {e}", exc_info=True)
            raise
    
    def poll(self):
        """
        Perform a single poll cycle.
        
        Override this method in subclasses to implement specific polling logic.
        """
        raise NotImplementedError("Subclasses must implement poll()")


# =============================================================================
# GmailWatcher Class
# =============================================================================

class GmailWatcher(BaseWatcher):
    """
    Gmail-specific watcher that monitors for important unread emails.
    
    Creates markdown files in Needs_Action folder for AI processing.
    """
    
    def __init__(self, vault_dir: Path = VAULT_DIR):
        """Initialize the Gmail watcher."""
        super().__init__("Gmail", vault_dir, POLL_INTERVAL_SECONDS)
        self.credentials_file = CREDENTIALS_FILE
        self.token_file = TOKEN_FILE
        self.service = None
        
    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        creds = None
        
        # Load existing token if available
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_file, SCOPES
                )
                logger.info("Loaded existing credentials")
            except Exception as e:
                logger.warning(f"Could not load token file: {e}")
                creds = None
        
        # Refresh or obtain new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed expired credentials")
                except Exception as e:
                    logger.warning(f"Could not refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not self.credentials_file.exists():
                    logger.error(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download gmail_credentials.json from Google Cloud Console"
                    )
                    return False
                
                try:
                    logger.info("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0, open_browser=False)
                    
                    # Save credentials for future use
                    with open(self.token_file, 'w', encoding='utf-8') as f:
                        f.write(creds.to_json())
                    logger.info("Credentials saved successfully")
                    
                except Exception as e:
                    logger.error(f"OAuth flow failed: {e}")
                    return False
        
        # Build the Gmail service
        try:
            self.service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service initialized")
            return True
        except Exception as e:
            logger.error(f"Could not build Gmail service: {e}")
            return False
    
    def _decode_body(self, message: dict) -> str:
        """
        Decode the email body from Gmail API response.
        
        Args:
            message: Gmail message resource
            
        Returns:
            Decoded email body as string
        """
        body = ""
        
        try:
            # Try to get body from different parts
            if "payload" in message:
                payload = message["payload"]
                
                # Check for direct body
                if "body" in payload and payload["body"].get("data"):
                    body = base64.urlsafe_b64decode(
                        payload["body"]["data"]
                    ).decode("utf-8", errors="replace")
                
                # Check multipart messages
                elif "parts" in payload:
                    for part in payload["parts"]:
                        # Prefer plain text, fallback to HTML
                        if part["mimeType"] == "text/plain":
                            if "data" in part["body"]:
                                body = base64.urlsafe_b64decode(
                                    part["body"]["data"]
                                ).decode("utf-8", errors="replace")
                                break
                        elif part["mimeType"] == "text/html" and not body:
                            if "data" in part["body"]:
                                body = base64.urlsafe_b64decode(
                                    part["body"]["data"]
                                ).decode("utf-8", errors="replace")
                    
                    # If still no body, check nested parts
                    if not body:
                        for part in payload["parts"]:
                            if "parts" in part:
                                for nested in part["parts"]:
                                    if nested["mimeType"] == "text/plain":
                                        if "data" in nested["body"]:
                                            body = base64.urlsafe_b64decode(
                                                nested["body"]["data"]
                                            ).decode("utf-8", errors="replace")
                                            break
                                if body:
                                    break
        except Exception as e:
            logger.warning(f"Could not decode email body: {e}")
            body = "[Could not decode email body]"
        
        return body
    
    def _get_email_headers(self, message: dict) -> dict:
        """
        Extract headers from Gmail message.
        
        Args:
            message: Gmail message resource
            
        Returns:
            Dictionary of email headers
        """
        headers = {}
        
        try:
            for header in message["payload"]["headers"]:
                name = header["name"].lower()
                value = header["value"]
                headers[name] = value
        except Exception as e:
            logger.warning(f"Could not extract headers: {e}")
        
        return headers
    
    def _determine_priority(self, headers: dict, labels: list) -> str:
        """
        Determine email priority based on headers and labels.
        
        Args:
            headers: Email headers dict
            labels: List of Gmail labels
            
        Returns:
            Priority string: 'urgent', 'high', 'normal', or 'low'
        """
        # Check for urgent indicators
        subject = headers.get("subject", "").lower()
        from_email = headers.get("from", "").lower()
        
        # Urgent keywords
        urgent_keywords = ["urgent", "asap", "emergency", "critical", "immediate"]
        if any(keyword in subject for keyword in urgent_keywords):
            return "urgent"
        
        # High priority indicators
        high_indicators = [
            "important" in [l.lower() for l in labels],
            any(keyword in subject for keyword in ["meeting", "call", "deadline", "review"]),
            "@" in from_email and not any(domain in from_email for domain in ["newsletter", "noreply", "no-reply"])
        ]
        
        if any(high_indicators):
            return "high"
        
        # Low priority indicators
        low_indicators = [
            any(keyword in from_email for keyword in ["newsletter", "noreply", "no-reply", "unsubscribe"]),
            any(keyword in subject for keyword in ["newsletter", "promotion", "sale", "offer"])
        ]
        
        if any(low_indicators):
            return "low"
        
        return "normal"
    
    def _create_email_markdown(self, message: dict) -> tuple[str, str]:
        """
        Create markdown content for an email.
        
        Args:
            message: Gmail message resource
            
        Returns:
            Tuple of (filename, markdown_content)
        """
        # Extract message data
        msg_id = message["id"]
        thread_id = message["threadId"]
        internal_date = message.get("internalDate", "")
        
        # Parse headers
        headers = self._get_email_headers(message)
        
        # Extract key fields
        subject = headers.get("subject", "No Subject")
        from_header = headers.get("from", "Unknown Sender")
        to_header = headers.get("to", "")
        date_header = headers.get("date", "")
        cc_header = headers.get("cc", "")
        
        # Get labels
        labels = message.get("labelIds", [])
        
        # Get body
        body = self._decode_body(message)
        
        # Determine priority
        priority = self._determine_priority(headers, labels)
        
        # Parse date
        try:
            received_date = parsedate_to_datetime(date_header).isoformat()
        except Exception:
            received_date = datetime.now().isoformat()
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize subject for filename
        safe_subject = self._sanitize_filename(subject[:50])
        
        # Generate filename
        filename = f"EMAIL_{timestamp}_{safe_subject}"
        
        # Extract sender email
        sender_email = ""
        if "<" in from_header:
            sender_email = from_header.split("<")[1].strip(">")
        else:
            sender_email = from_header
        
        # Create YAML frontmatter
        frontmatter = f"""---
type: email
message_id: {msg_id}
thread_id: {thread_id}
from: {from_header}
from_email: {sender_email}
to: {to_header}
cc: {cc_header}
subject: {subject}
received: {received_date}
priority: {priority}
status: unprocessed
labels: {labels}
---
"""
        
        # Create email body section
        body_section = f"""
## Email Content

{body}

---
## AI Processing Notes

### Classification
- **Category**: [client_inquiry | meeting_request | sales | newsletter | spam | other]
- **Requires Reply**: [yes/no]
- **Action Needed**: [Describe what action to take]

### Draft Reply (if needed)
[AI will draft reply here if response is needed]

---
## Approval Instructions
Move this file to /Pending_Approval/EMAIL_REPLY_{timestamp}.md when reply is drafted.
"""
        
        # Combine all sections
        content = frontmatter + body_section
        
        return filename, content
    
    def _fetch_important_unread_emails(self) -> list:
        """
        Fetch important unread emails from Gmail.
        
        Returns:
            List of Gmail message resources
        """
        if not self.service:
            logger.error("Gmail service not initialized")
            return []
        
        messages = []
        
        try:
            # Query for important, unread emails
            # Exclude spam and trash
            query = "is:important is:unread -in:spam -in:trash"
            
            response = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=MAX_RESULTS_PER_POLL
            ).execute()
            
            message_ids = response.get("messages", [])
            
            if not message_ids:
                logger.info("No new important unread emails")
                return []
            
            logger.info(f"Found {len(message_ids)} important unread emails")
            
            # Fetch full message details
            for msg in message_ids:
                try:
                    full_message = self.service.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="full"
                    ).execute()
                    messages.append(full_message)
                except HttpError as e:
                    logger.warning(f"Could not fetch message {msg['id']}: {e}")
                    
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching emails: {e}")
        
        return messages
    
    def poll(self):
        """
        Perform a single poll cycle for Gmail.
        
        Fetches important unread emails and creates action files.
        """
        logger.info("Starting Gmail poll cycle")
        
        # Ensure authenticated
        if not self.service:
            if not self._authenticate():
                logger.warning("Authentication failed, skipping this cycle")
                return
        
        # Fetch emails
        emails = self._fetch_important_unread_emails()
        
        if not emails:
            return
        
        # Process each email
        processed_count = 0
        for email in emails:
            msg_id = email["id"]
            
            # Skip if already processed
            if self._is_processed(msg_id):
                logger.debug(f"Email {msg_id} already processed, skipping")
                continue
            
            try:
                # Create markdown file
                filename, content = self._create_email_markdown(email)
                self._create_action_file(filename, content)
                
                # Mark as processed
                self._mark_as_processed(msg_id)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process email {msg_id}: {e}", exc_info=True)
        
        logger.info(f"Poll cycle complete. Processed {processed_count} new emails")
    
    def run_once(self):
        """Run a single poll cycle (useful for testing)."""
        logger.info("Running single poll cycle")
        self._authenticate()
        self.poll()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point for the Gmail watcher."""
    logger.info("=" * 60)
    logger.info("Gmail Watcher for Personal AI Employee (Silver Tier)")
    logger.info("=" * 60)
    
    # Verify vault directory exists
    if not VAULT_DIR.exists():
        logger.error(f"Vault directory not found: {VAULT_DIR}")
        sys.exit(1)
    
    # Verify credentials file exists
    if not CREDENTIALS_FILE.exists():
        logger.error(
            f"Gmail credentials file not found: {CREDENTIALS_FILE}\n"
            "Please download 'gmail_credentials.json' from Google Cloud Console:\n"
            "1. Go to https://console.cloud.google.com\n"
            "2. Enable Gmail API\n"
            "3. Create OAuth 2.0 credentials\n"
            "4. Download and save as 'gmail_credentials.json' in project root"
        )
        sys.exit(1)
    
    # Create and run watcher
    watcher = GmailWatcher()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            logger.info("Running in test mode (single poll)")
            watcher.run_once()
            return
        elif sys.argv[1] == "--auth":
            logger.info("Running authentication only")
            watcher._authenticate()
            return
    
    # Run continuous watcher
    watcher.run()


if __name__ == "__main__":
    main()
