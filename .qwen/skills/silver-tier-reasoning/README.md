# Silver Tier Reasoning Engine

## Quick Start

```bash
# Activate the skill
skill: "silver-tier-reasoning"

# Or run directly
/agent-skill Silver_Tier_Reasoning_Engine --run
```

---

## Core Workflow

```
┌─────────────────┐
│  /Needs_Action/ │ ← Read all incoming items
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Plan.md │ ← Always create plan first
│   in /Plans/    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Process Items  │ ← Analyze and decide actions
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────────┐ ┌─────────────┐
│Simple     │ │Needs        │
│Archive to │ │Approval →   │
│/Done/     │ │/Pending_    │
│           │ │Approval/    │
└───────────┘ └─────────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │  Human      │
                 │  Reviews    │
                 └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │  /Approved/ │ ← Execute with MCP
                 └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │  /Done/     │ ← Move completed
                 └─────────────┘
```

---

## Key Rules

| Rule | Description |
|------|-------------|
| **1. Plan First** | Always create Plan.md before processing |
| **2. Approval Required** | Never send emails/posts without approval |
| **3. Priority Order** | Process urgent → high → normal → low |
| **4. Log Everything** | All actions go to /Logs/ |
| **5. Clean Up** | Move completed to /Done/ |

---

## Item Processing

### Email Decision Tree

```
EMAIL received
    │
    ├─ Spam/Promotional? → Archive to /Done/PROCESSED/
    │
    ├─ Client Inquiry? → Draft reply → /Pending_Approval/
    │
    ├─ Meeting Request? → Draft availability → /Pending_Approval/
    │
    └─ FYI/Newsletter? → Archive to /Done/PROCESSED/
```

### LinkedIn Post Decision

```
Check Business_Goals.md and /Done/
    │
    ├─ Milestone completed? → Create achievement post
    │
    ├─ Learning/insight? → Create value post
    │
    ├─ Business update? → Create update post
    │
    └─ Nothing notable? → Skip today
```

---

## File Templates

### Plan.md Template

```markdown
---
type: processing_plan
created: 2026-03-28T08:00:00Z
status: in_progress
---

# Processing Plan: 2026-03-28

## Items Queue

### 1. EMAIL_20260328_103000_Client_Inquiry.md
- **Type:** Email
- **Priority:** High
- **Action:** Draft reply
- **Status:** ⬜ Pending

## Tasks

- [ ] Process urgent items
- [ ] Draft email replies
- [ ] Create LinkedIn drafts
- [ ] Execute approved actions
- [ ] Update Dashboard.md
```

### Email Reply Draft

```markdown
---
type: email_reply
to: client@example.com
subject: Re: Inquiry
status: pending_approval
---

## Draft Reply

Hi [Name],

Thank you for reaching out...

Best regards,
[Your Name]

---
## Approval Instructions
Move to /Approved to send, /Rejected to decline.
```

### LinkedIn Post Draft

```markdown
---
type: linkedin_post
post_type: achievement
scheduled_time: 09:00
status: pending_approval
hashtags: [AI, Automation, Milestone]
---

## Post Content

[Hook line]

[Main content]

[Call-to-action]

---
## Hashtags
#AI #Automation #Milestone

---
## Approval Instructions
Move to /Approved to publish.
```

---

## MCP Integration

### Send Email

```json
{
  "tool": "email_send",
  "arguments": {
    "to": "client@example.com",
    "subject": "Re: Inquiry",
    "body": "Email content..."
  }
}
```

### Publish LinkedIn Post

```json
{
  "tool": "linkedin_post_publish",
  "arguments": {
    "content": "Post content...",
    "hashtags": ["AI", "Automation"]
  }
}
```

---

## Quality Checklist

### Before Any Action

- [ ] Read Company_Handbook.md guidelines
- [ ] Checked Business_Goals.md for context
- [ ] Created Plan.md in /Plans/
- [ ] Priority correctly assigned

### Before Sending Email

- [ ] Recipient name correct
- [ ] Tone professional and warm
- [ ] All questions addressed
- [ ] No spelling errors
- [ ] Approval file created

### Before Publishing Post

- [ ] Strong hook (first 40 chars)
- [ ] Clear value proposition
- [ ] 3-5 relevant hashtags
- [ ] Call-to-action included
- [ ] Approval file created

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No plan created | Always create Plan.md first |
| Direct posting | Never post without approval |
| Wrong folder | Check item type and routing |
| Missing logs | Log every action in /Logs/ |

---

## Files to Monitor

| File/Folder | Purpose |
|-------------|---------|
| `/Needs_Action/` | Input queue |
| `/Pending_Approval/` | Awaiting review |
| `/Approved/` | Ready to execute |
| `/Plans/` | Active plans |
| `/Done/` | Completed items |
| `/Logs/` | Activity logs |
| `Company_Handbook.md` | Guidelines |
| `Business_Goals.md` | Context |
| `Dashboard.md` | System state |

---

*Version: 1.0 | Tier: Silver | Human-in-Loop: Required*
