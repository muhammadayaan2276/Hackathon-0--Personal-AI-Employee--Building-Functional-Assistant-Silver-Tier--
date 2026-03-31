# LinkedIn Post Generator Skill

## Quick Start

### Activate the Skill

```bash
# In Claude Code or Qwen Code
skill: "linkedin-post-generator"
```

### Run Manually

```bash
# Generate a post now
/agent-skill LinkedIn_Post_Generator --run-now
```

### Schedule Daily Execution

```bash
# Add to your daily automation routine
/agent-skill LinkedIn_Post_Generator --schedule "0 8 * * *"
```

---

## How It Works

```
┌─────────────────────────┐
│  1. Check Business_Goals.md  │
│     - Completed goals    │
│     - Progress updates   │
│     - Milestones         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  2. Scan /Done/ folder     │
│     - Recent tasks       │
│     - Email replies      │
│     - Published posts    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  3. Evaluate Content       │
│     - Is it valuable?    │
│     - Is it unique?      │
│     - Is it timely?      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  4. Create Post Draft      │
│     - Professional tone  │
│     - Hashtags (3-5)     │
│     - Call-to-action     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  5. Save to Pending_Approval│
│     ⚠️ NEVER post directly │
└─────────────────────────┘
```

---

## Post Types

| Type | When to Use | Example Hook |
|------|-------------|--------------|
| **Achievement** | Milestones, wins | "Processed 100+ emails in 30 days..." |
| **Value** | Tips, tutorials | "Stop checking email every 5 minutes..." |
| **Journey** | Learnings, stories | "6 months ago, I knew nothing about AI..." |
| **Update** | Business news | "Excited to share our new automation system..." |
| **Engagement** | Questions, opinions | "Unpopular opinion: Most productivity advice is wrong..." |

---

## Output Format

Posts are created in `/Pending_Approval/` with this structure:

```
AI_Employee_Vault/
└── Pending_Approval/
    └── LINKEDIN_POST_2026-03-28_Milestone.md
```

### File Contents

```yaml
---
type: linkedin_post
skill: LinkedIn_Post_Generator
generated_at: 2026-03-28T08:00:00Z
scheduled_date: 2026-03-28
scheduled_time: 09:00
post_type: achievement
topic: milestone
status: pending_approval
hashtags: [AI, Automation, Milestone]
---

## Post Content

[Hook line]

[Main content - 2-4 paragraphs]

[Call-to-action]

---
## Hashtags
#AI #Automation #Milestone

---
## Approval Instructions
Move to /Approved to publish, /Rejected to decline.
```

---

## Approval Workflow

### To Approve
1. Review the post content
2. Move file to `/Approved/LINKEDIN_POST_YYYY-MM-DD.md`
3. AI will publish at scheduled time

### To Reject
1. Add rejection reason in file comments
2. Move to `/Rejected/`

### To Request Changes
1. Edit the post content directly
2. Leave in `/Pending_Approval/`
3. AI will revise and resubmit

---

## Content Guidelines

### ✅ DO
- Start with a strong hook (first 40 chars visible in feed)
- Use short paragraphs for readability
- Include 2-4 relevant emojis
- Add 3-5 hashtags
- End with engagement question
- Provide clear value to readers

### ❌ DON'T
- Write walls of text
- Use more than 5 hashtags
- Be overly promotional (>20%)
- Use clickbait hooks
- Post controversial topics
- Exceed 1,300 characters

---

## Scheduling

### Optimal Posting Times

| Time | Audience | Best For |
|------|----------|----------|
| 8-9 AM | Commuters | Tips, news |
| 12-1 PM | Lunch break | Engagement, stories |
| 5-6 PM | After work | Reflections, wins |

### Posting Frequency

- **Minimum:** 3 posts per week
- **Maximum:** 2 posts per day
- **Optimal:** 1 post per day (weekdays)

---

## Examples

### Achievement Post

```
100 emails processed. 95% approval rate. Here's what worked:

Building an AI employee wasn't easy. The first week, I doubted everything.

But I kept iterating:
→ Refined classification rules
→ Improved response templates  
→ Added human-in-the-loop approvals

The result? 4-hour average response time.

The biggest lesson: AI amplifies humans, doesn't replace them.

What's your AI automation experience been like?

#AI #Automation #Milestone #ProductivityTips #AIAgent
```

### Value/Tip Post

```
Stop checking email every 5 minutes. Do this instead:

I used to lose 3+ hours daily to email distractions.

Then I implemented the AI Employee Email System:

1️⃣ Gmail Watcher polls every 2 minutes
2️⃣ AI classifies and drafts replies
3️⃣ I review only important decisions
4️⃣ Approved emails send automatically

Now I check email 2x/day. Response time improved 40%.

The secret? Automate the routine. Decide on the important.

What's your best email productivity hack?

#ProductivityTips #AI #Automation #EmailManagement #TimeManagement
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No post generated | No worthy content in past 48 hours |
| Similar to recent post | Skill detected duplicate topic |
| Wrong tone | Review Company_Handbook.md guidelines |
| Missing hashtags | Skill uses 3-5 relevant tags |

---

## Integration

This skill integrates with:

- **Business_Goals.md** - Goal tracking source
- **/Done/ folder** - Completed tasks source
- **/Logs/ folder** - Activity logging
- **Company_Handbook.md** - Content guidelines
- **/Pending_Approval/** - Approval workflow

---

## Configuration

Edit skill behavior in the skill definition:

```yaml
linkedin_post_generator:
  enabled: true
  run_schedule: "0 8 * * *"  # Daily at 8 AM
  check_hours_back: 48       # Look back 48 hours
  min_posts_per_week: 3      # Minimum frequency
  max_posts_per_day: 2       # Maximum frequency
  require_approval: true     # HITL required
```

---

*Version: 1.0 | Tier: Silver | Human-in-Loop: Required*
