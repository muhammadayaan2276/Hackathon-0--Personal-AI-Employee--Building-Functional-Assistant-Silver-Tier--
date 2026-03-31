#!/usr/bin/env python3
"""
Claude AI Processor for LinkedIn Automation

Reads emails from /Needs_Action and creates LinkedIn post drafts in /Pending_Approval

Flow:
1. Scan /Needs_Action for new emails
2. Use Claude to analyze and create LinkedIn posts
3. Save drafts to /Pending_Approval
4. Move processed emails to /Done
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
import re

# Configuration
VAULT_DIR = Path(__file__).parent.parent / "AI_Employee_Vault"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
PENDING_APPROVAL_DIR = VAULT_DIR / "Pending_Approval"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = VAULT_DIR / "Logs"
PLANS_DIR = VAULT_DIR / "Plans"

# Ensure directories exist
for dir_path in [PENDING_APPROVAL_DIR, DONE_DIR, LOGS_DIR, PLANS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def log_message(message: str):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    
    # Fix Windows console encoding
    try:
        print(log_line)
    except UnicodeEncodeError:
        print(log_line.encode('cp1252', errors='replace').decode('cp1252'))

    log_file = LOGS_DIR / f"claude_processor_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{log_line}")


def read_email_file(filepath):
    """Read email .md file and extract content"""
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
    
    return frontmatter, body


def create_linkedin_post_with_claude(email_content, email_body):
    """
    Use AI to create LinkedIn post from email
    Supports: Google Gemini (FREE), Ollama (FREE Local), or template fallback
    Returns: (post_content, should_post)
    """

    # Create prompt for AI
    prompt = f"""
You are a LinkedIn content strategist. Analyze this email and create a LinkedIn post if appropriate.

## Email Content:

**From:** {email_content.get('from', 'Unknown')}
**Subject:** {email_content.get('subject', 'No Subject')}
**Date:** {email_content.get('received', 'Unknown')}

**Body:**
{email_body}

## Instructions:

1. Analyze if this email contains content suitable for LinkedIn (product launches, achievements, news, insights, etc.)
2. If YES, create an engaging LinkedIn post with:
   - Catchy opening with emoji
   - Clear main message
   - Call to action or insight
   - 3-5 relevant hashtags
3. If NO, explain why it's not suitable

## Response Format:

```json
{{
  "should_post": true/false,
  "reason": "Why or why not",
  "post_content": "The LinkedIn post text (if should_post is true)",
  "hashtags": ["#tag1", "#tag2"],
  "tone": "professional/casual/enthusiastic",
  "target_audience": "Who this is for"
}}
```

Respond ONLY with the JSON.
"""

    # Try Google Gemini API (FREE)
    try:
        import os
        gemini_key = os.environ.get("GEMINI_API_KEY")
        
        if gemini_key:
            log_message("🤖 Using Google Gemini API (FREE)...")
            
            import urllib.request
            import json
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024
                }
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result_data = json.loads(response.read().decode('utf-8'))
            
            response_text = result_data['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from response
            json_match = re.search(r'```json\s*(.+?)\s*```', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(response_text)
            
            log_message("✅ Gemini API success!")
            return result, response_text
            
    except ImportError as e:
        log_message(f"⚠️  Import error: {e}")
    except Exception as e:
        log_message(f"⚠️  Gemini API error: {e}")

    # Try Ollama (FREE Local AI)
    try:
        import urllib.request
        import json
        
        log_message("🤖 Trying Ollama (Local FREE AI)...")
        
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result_data = json.loads(response.read().decode('utf-8'))
        
        response_text = result_data['response']
        
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.+?)\s*```', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            result = json.loads(response_text)
        
        log_message("✅ Ollama success!")
        return result, response_text
        
    except Exception as e:
        log_message(f"⚠️  Ollama not available: {e}")

    # Fallback: Template generation
    log_message("⚠️  No AI API available. Using template-based generation.")
    return generate_post_template(email_content, email_body)


def generate_post_template(email_content, email_body):
    """Fallback: Generate post without Claude"""
    
    subject = email_content.get('subject', 'Update')
    from_name = email_content.get('from', 'Someone')
    
    # Simple template-based generation
    post = f"""📢 {subject}

{email_body[:500]}...

#Update #Business #Professional"""
    
    return {
        "should_post": True,
        "reason": "Auto-generated (Claude not available)",
        "post_content": post,
        "hashtags": ["#Update", "#Business"],
        "tone": "professional"
    }, "Template generated"


def create_linkedin_draft(result, source_file):
    """Create LinkedIn post draft in /Pending_Approval"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"LINKEDIN_POST_{timestamp}.md"
    filepath = PENDING_APPROVAL_DIR / filename
    
    post_content = result.get('post_content', '')
    hashtags = result.get('hashtags', [])
    
    # Add hashtags if not in content
    if hashtags and not all(h in post_content for h in hashtags):
        post_content += "\n\n" + " ".join(hashtags)
    
    content = f"""---
type: linkedin_post
status: pending_approval
source_file: {source_file.name}
created: {datetime.now().isoformat()}
tone: {result.get('tone', 'professional')}
target_audience: {result.get('target_audience', 'General')}
---

# LinkedIn Post Draft

## Preview

{post_content}

---

## Metadata

- **Reason:** {result.get('reason', '')}
- **Tone:** {result.get('tone', 'professional')}
- **Target:** {result.get('target_audience', 'General')}

---

## Approval Instructions

**To Approve:**
1. Review the post content above
2. Edit if needed
3. Move this file to `/Approved` folder

**To Reject:**
1. Move this file to `/Rejected` folder
2. Add reason for rejection below

---

## Rejection Notes (if applicable)


"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    log_message(f"✅ Created draft: {filename}")
    return filepath


def create_plan_file(result, source_file):
    """Create a plan file with checkboxes"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Plan_LinkedIn_{timestamp}.md"
    filepath = PLANS_DIR / filename
    
    content = f"""---
type: plan
created: {datetime.now().isoformat()}
source: {source_file.name}
status: in_progress
---

# LinkedIn Post Plan

## Task
Create and publish LinkedIn post from email

## Checklist

- [x] Email received and processed
- [x] LinkedIn post draft created
- [ ] **Waiting for human approval**
- [ ] Post published to LinkedIn
- [ ] Moved to Done

## Post Details

**Tone:** {result.get('tone', 'professional')}  
**Audience:** {result.get('target_audience', 'General')}  
**Hashtags:** {', '.join(result.get('hashtags', []))}

## Notes

{result.get('reason', '')}

"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath


def move_to_done(filepath):
    """Move processed email to Done folder"""
    dest = DONE_DIR / filepath.name
    
    # If file already exists, add timestamp to avoid conflict
    if dest.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
        dest = DONE_DIR / new_name
    
    try:
        filepath.rename(dest)
        log_message(f"📁 Moved to Done: {dest.name}")
        return True
    except Exception as e:
        log_message(f"❌ Error moving file: {e}")
        return False


def process_needs_action():
    """Process all files in /Needs_Action"""
    
    if not NEEDS_ACTION_DIR.exists():
        log_message("⚠️  /Needs_Action folder not found")
        return 0
    
    # Find all email files
    email_files = list(NEEDS_ACTION_DIR.glob("EMAIL_*.md"))
    
    if not email_files:
        log_message("📭 No new emails to process")
        return 0
    
    log_message(f"📧 Found {len(email_files)} emails to process")
    
    processed = 0
    
    for email_file in email_files:
        log_message(f"\n📮 Processing: {email_file.name}")
        
        try:
            # Read email
            frontmatter, body = read_email_file(email_file)
            
            # Generate LinkedIn post with Claude
            result, raw_response = create_linkedin_post_with_claude(frontmatter, body)
            
            if result.get('should_post', False):
                # Create draft
                draft_file = create_linkedin_draft(result, email_file)
                
                # Create plan
                create_plan_file(result, email_file)
                
                log_message(f"✅ Draft created: {draft_file.name}")
            else:
                log_message(f"⊘ Skipped: {result.get('reason', 'Not suitable')}")
            
            # Move to Done
            move_to_done(email_file)
            processed += 1
        
        except Exception as e:
            log_message(f"❌ Error processing {email_file.name}: {e}")
    
    log_message(f"\n✅ Processed {processed} emails")
    return processed


def run_processor():
    """Main processor loop"""
    log_message("🚀 Starting Claude AI Processor...")
    log_message(f"📁 Watching: {NEEDS_ACTION_DIR}")
    log_message(f"📝 Output: {PENDING_APPROVAL_DIR}")
    
    while True:
        # Process any new emails
        processed = process_needs_action()
        
        if processed > 0:
            log_message(f"✨ Created {processed} LinkedIn post drafts")
        
        # Wait for next check (every 30 seconds)
        time.sleep(30)


if __name__ == "__main__":
    try:
        # Run once if called with --once
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            process_needs_action()
        else:
            run_processor()
    except KeyboardInterrupt:
        log_message("\n👋 Processor stopped by user")
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        sys.exit(1)
