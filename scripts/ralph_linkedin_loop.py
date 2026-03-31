#!/usr/bin/env python3
"""
Ralph Loop for LinkedIn Automation

Monitors /Approved folder and publishes posts via MCP Server

Flow:
1. Watch /Approved for new post drafts
2. Call LinkedIn MCP Server to publish
3. Move published posts to /Done
4. Log activity
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
VAULT_DIR = Path(__file__).parent.parent / "AI_Employee_Vault"
APPROVED_DIR = VAULT_DIR / "Approved"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = VAULT_DIR / "Logs"
LINKEDIN_MCP_DIR = Path(__file__).parent / "linkedin-mcp-server"

# Ensure directories exist
for dir_path in [DONE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# MCP Server configuration
MCP_SERVER_URL = "http://localhost:8809"
MCP_CLIENT = Path(__file__).parent / "mcp-client.py"


def log_message(message: str):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    
    # Fix Windows console encoding
    try:
        print(log_line)
    except UnicodeEncodeError:
        print(log_line.encode('cp1252', errors='replace').decode('cp1252'))

    log_file = LOGS_DIR / f"ralph_loop_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{log_line}")


def strip_markdown(text):
    """Remove markdown formatting from text"""
    import re

    # Remove headers (# Header -> Header)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Remove bold (**text** -> text)
    text = text.replace('**', '')

    # Remove italic (*text* -> text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)

    # Remove links ([text](url) -> text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove code blocks (```code``` -> code)
    text = re.sub(r'```[\s\S]*?```', '', text)

    # Remove inline code (`code` -> code)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove blockquotes (> text -> text)
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def read_post_file(filepath):
    """Read LinkedIn post draft file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()

            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    # Extract post content from body
    post_content = body
    if "## Preview" in body:
        post_content = body.split("## Preview")[1].strip()
        if "---" in post_content:
            post_content = post_content.split("---")[0].strip()

    # Strip markdown formatting for LinkedIn
    post_content = strip_markdown(post_content)

    return frontmatter, post_content


def publish_via_mcp(post_content):
    """Publish post using LinkedIn MCP Server"""
    log_message("📡 Calling LinkedIn MCP Server...")
    
    try:
        # Check if MCP client exists
        if not MCP_CLIENT.exists():
            log_message("⚠️  MCP client not found, using direct method")
            return publish_direct(post_content)
        
        # Call MCP server
        cmd = [
            sys.executable,
            str(MCP_CLIENT),
            "call",
            "-u", MCP_SERVER_URL,
            "-t", "linkedin_post_publish",
            "-p", json.dumps({"content": post_content})
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log_message("✅ MCP Server responded successfully")
            return True, result.stdout
        else:
            log_message(f"❌ MCP Server error: {result.stderr}")
            return False, result.stderr
    
    except subprocess.TimeoutExpired:
        log_message("❌ MCP Server timeout")
        return False, "Timeout"
    
    except Exception as e:
        log_message(f"❌ MCP Server error: {e}")
        return False, str(e)


def publish_direct(post_content):
    """Direct publishing using Playwright (fallback)"""
    log_message("📡 Publishing directly via Playwright...")

    context = None
    browser = None

    try:
        # Import playwright
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # Launch browser with persistent context
            user_data_dir = LINKEDIN_MCP_DIR / ".linkedin-session" / "user-data"

            # Create user data dir if it doesn't exist
            user_data_dir.mkdir(parents=True, exist_ok=True)

            # Use launch_persistent_context properly
            log_message("🌐 Opening browser with persistent session...")
            context = p.chromium.launch_persistent_context(
                str(user_data_dir),
                headless=False,
                viewport={"width": 1920, "height": 1080},
                args=["--disable-gpu", "--no-sandbox"]
            )

            # Get the page from context
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to LinkedIn
            log_message("📍 Navigating to LinkedIn...")
            page.goto("https://www.linkedin.com/feed/", wait_until="commit", timeout=30000)
            page.wait_for_timeout(5000)

            # Check if logged in
            if "/login" in page.url:
                log_message("❌ Not logged in!")
                context.close()
                return False, "Not logged in"

            # Click "Start a post"
            log_message("📝 Opening post composer...")
            post_input = page.locator('div[aria-label*="Start a post"]').first
            post_input.click(force=True)
            page.wait_for_timeout(5000)

            # Take screenshot to debug
            page.screenshot(path="debug_ralph.png")
            log_message("📸 Debug screenshot saved")

            # Find editor and type content
            log_message("⌨️  Typing content...")
            
            # Type in smaller chunks with better timing to avoid issues
            chunks = [post_content[i:i+200] for i in range(0, len(post_content), 200)]
            
            for i, chunk in enumerate(chunks[:15]):  # Max 3000 chars
                # Re-find editor before each chunk to avoid stale element
                editor = page.locator('div[contenteditable="true"][role="textbox"]').first
                editor.wait_for(state='visible', timeout=5000)
                editor.focus()
                page.wait_for_timeout(1000)
                
                log_message(f"  Typing chunk {i+1}/{min(len(chunks), 15)}...")
                editor.type(chunk, delay=50)
                page.wait_for_timeout(2000)  # Wait between chunks

            page.wait_for_timeout(3000)

            try:
                # Find the blue Post button in the dialog
                post_button = page.locator('button:has-text("Post")').last

                # Wait for it to be attached
                post_button.wait_for(state='attached', timeout=5000)

                # Check if enabled
                is_enabled = post_button.is_enabled()
                log_message(f"  Post button enabled: {is_enabled}")

                if is_enabled:
                    # Scroll into view and click
                    post_button.scroll_into_view_if_needed()
                    post_button.click(force=True)
                    log_message("  ✓ Post button clicked!")
                    result = True
                else:
                    log_message("  Post button is disabled")
                    result = False

            except Exception as e:
                log_message(f"  Error clicking Post button: {e}")
                result = False

            page.wait_for_timeout(10000)

            # Take final screenshot
            page.screenshot(path="debug_ralph_final.png")
            log_message("📸 Final screenshot saved")

            if result:
                log_message("✅ Post published!")
                context.close()
                return True, "Published successfully"
            else:
                log_message("❌ Post button not found")
                context.close()
                return False, "Post button not found"

    except ImportError:
        log_message("❌ Playwright not installed")
        return False, "Playwright not installed"

    except Exception as e:
        log_message(f"❌ Publishing error: {e}")
        # Clean up on error
        try:
            if context:
                context.close()
        except:
            pass
        return False, str(e)


def move_to_done(filepath, post_url=""):
    """Move published post to Done folder"""

    # Read current content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update status
    content = content.replace(
        "status: pending_approval",
        f"status: published\npublished_at: {datetime.now().isoformat()}\npost_url: {post_url}"
    )

    # Move file - handle existing files
    dest = DONE_DIR / filepath.name
    
    # If file already exists, add timestamp
    if dest.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
        dest = DONE_DIR / new_name

    # Write updated content
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(content)

    # Delete original
    filepath.unlink()

    log_message(f"📁 Moved to Done: {dest.name}")
    return True


def update_plan_file(source_file, status):
    """Update the related plan file"""
    plans_dir = VAULT_DIR / "Plans"
    
    if not plans_dir.exists():
        return
    
    # Find matching plan
    source_name = source_file.name
    for plan_file in plans_dir.glob(f"Plan_LinkedIn_*.md"):
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if source_name in content:
            # Update checkboxes
            content = content.replace(
                "- [ ] **Waiting for human approval**",
                "- [x] **Waiting for human approval**"
            )
            content = content.replace(
                "- [ ] Post published to LinkedIn",
                f"- [x] Post published to LinkedIn ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            )
            
            with open(plan_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            log_message(f"📝 Updated plan: {plan_file.name}")
            break


def process_approved_posts():
    """Process all files in /Approved"""
    
    if not APPROVED_DIR.exists():
        return 0
    
    # Find all post files
    post_files = list(APPROVED_DIR.glob("LINKEDIN_POST_*.md"))
    
    if not post_files:
        return 0
    
    log_message(f"📋 Found {len(post_files)} posts to publish")
    
    published = 0
    failed = 0
    
    for post_file in post_files:
        log_message(f"\n📮 Processing: {post_file.name}")
        
        try:
            # Read post
            frontmatter, post_content = read_post_file(post_file)
            
            # Publish via MCP
            success, result = publish_via_mcp(post_content)
            
            if success:
                # Move to Done
                move_to_done(post_file, post_url=result)
                
                # Update plan
                update_plan_file(post_file, "published")
                
                published += 1
            else:
                log_message(f"❌ Failed to publish: {result}")
                failed += 1
        
        except Exception as e:
            log_message(f"❌ Error processing {post_file.name}: {e}")
            failed += 1
    
    log_message(f"\n✅ Published: {published}, ❌ Failed: {failed}")
    return published


def run_ralph_loop():
    """Main Ralph Loop"""
    log_message("🔄 Starting Ralph Loop for LinkedIn Automation...")
    log_message(f"📁 Watching: {APPROVED_DIR}")
    log_message(f"📤 Publishing to: LinkedIn")
    
    iteration = 0
    
    while True:
        iteration += 1
        log_message(f"\n--- Ralph Loop Iteration {iteration} ---")
        
        # Process approved posts
        published = process_approved_posts()
        
        if published > 0:
            log_message(f"🎉 Published {published} posts!")
        
        # Wait for next check (every 30 seconds)
        log_message("⏳ Waiting 30 seconds...")
        time.sleep(30)


if __name__ == "__main__":
    try:
        # Run once if called with --once
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            process_approved_posts()
        else:
            run_ralph_loop()
    except KeyboardInterrupt:
        log_message("\n👋 Ralph Loop stopped by user")
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        sys.exit(1)
