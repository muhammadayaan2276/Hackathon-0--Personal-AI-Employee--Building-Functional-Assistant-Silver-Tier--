#!/usr/bin/env python3
"""
LinkedIn Post Checker - Daily Cron Job

Checks /Approved/ folder for LinkedIn posts ready to publish.
Runs once daily via cron/PM2 schedule.

Usage:
    python3 scripts/linkedin_post_checker.py
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import json

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
VAULT_DIR = PROJECT_ROOT / "AI_Employee_Vault"
APPROVED_DIR = VAULT_DIR / "Approved"
LOGS_DIR = VAULT_DIR / "Logs"

# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging():
    """Configure logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    log_file = LOGS_DIR / f"linkedin_checker_{datetime.now().strftime('%Y-%m-%d')}.log"
    
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
# LinkedIn Post Checker
# =============================================================================

def check_approved_posts():
    """Check for approved LinkedIn posts ready to publish."""
    logger.info("=" * 50)
    logger.info("LinkedIn Post Checker - Daily Run")
    logger.info("=" * 50)
    
    if not APPROVED_DIR.exists():
        logger.warning(f"Approved directory not found: {APPROVED_DIR}")
        return []
    
    # Find all LINKEDIN_POST files in Approved
    approved_posts = list(APPROVED_DIR.glob("LINKEDIN_POST_*.md"))
    
    if not approved_posts:
        logger.info("No approved LinkedIn posts found")
        return []
    
    logger.info(f"Found {len(approved_posts)} approved post(s)")
    
    posts_to_publish = []
    
    for post_file in approved_posts:
        try:
            # Read file content
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            if '---' in content:
                frontmatter = content.split('---')[1]
                
                # Check if already processed
                if 'status: published' in frontmatter:
                    logger.info(f"Skipping {post_file.name} - already published")
                    continue
                
                # Check if it's a LinkedIn post
                if 'type: linkedin_post' not in frontmatter:
                    continue
                
                # Extract relevant info
                post_info = {
                    'file': str(post_file),
                    'name': post_file.name,
                    'content': content,
                }
                
                # Extract scheduled time if present
                if 'scheduled_time:' in frontmatter:
                    time_line = [l for l in frontmatter.split('\n') if 'scheduled_time:' in l]
                    if time_line:
                        post_info['scheduled_time'] = time_line[0].split(':')[1].strip()
                
                posts_to_publish.append(post_info)
                logger.info(f"✓ Found: {post_file.name}")
                
        except Exception as e:
            logger.error(f"Error reading {post_file.name}: {e}")
    
    return posts_to_publish


def notify_for_publishing(posts):
    """
    Notify the system that posts are ready for publishing.
    
    In a full implementation, this would:
    1. Call the LinkedIn MCP server
    2. Publish each post
    3. Move files to /Done/
    4. Update logs
    
    For now, it logs the posts that need publishing.
    """
    if not posts:
        return
    
    logger.info("\n" + "=" * 50)
    logger.info("Posts Ready for Publishing:")
    logger.info("=" * 50)
    
    for post in posts:
        logger.info(f"\n📝 File: {post['name']}")
        logger.info(f"   Scheduled: {post.get('scheduled_time', 'Not specified')}")
        logger.info(f"   Path: {post['file']}")
        
        # Extract preview of content
        if '## Post Content' in post['content']:
            preview = post['content'].split('## Post Content')[1].split('---')[0].strip()[:200]
            logger.info(f"   Preview: {preview}...")
    
    logger.info("\n" + "=" * 50)
    logger.info("Next Steps:")
    logger.info("1. AI Employee will detect these approved posts")
    logger.info("2. LinkedIn MCP server will publish them")
    logger.info("3. Files will be moved to /Done/ after publishing")
    logger.info("=" * 50)
    
    # Write status file for AI Employee to detect
    status_file = VAULT_DIR / ".linkedin_posts_to_publish.json"
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({
                'checked_at': datetime.now().isoformat(),
                'posts': [{'name': p['name'], 'file': p['file']} for p in posts]
            }, f, indent=2)
        logger.info(f"\n✓ Status written to: {status_file}")
    except Exception as e:
        logger.error(f"Failed to write status file: {e}")


def main():
    """Main entry point."""
    logger.info(f"Run time: {datetime.now().isoformat()}")
    
    # Check for approved posts
    posts = check_approved_posts()
    
    # Notify for publishing
    notify_for_publishing(posts)
    
    # Summary
    logger.info(f"\n✅ LinkedIn Post Checker completed")
    logger.info(f"   Posts found: {len(posts)}")
    logger.info(f"   Log file: {logging.getLogger().handlers[0].baseFilename}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
