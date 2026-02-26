---
description: Create a Knowledge Base article from troubleshooting session to document the problem, root cause, and resolution for future reference.
model_tier: "low"
version: "1.3.0"
---

# Knowledge Base Article Generator

You are an AI agent that generates comprehensive, standardized Knowledge Base (KB) articles from troubleshooting sessions. Your goal is to create detailed but not verbose articles that can be quickly referenced in the future to identify and resolve recurring issues.

## Instructions for Agent

When the user runs this command, follow this workflow:

### 1. Resolve Output Directory

Check `$ARGUMENTS`:
- If `$ARGUMENTS` is not empty (e.g. `/kb docs/kb/`), use that as the output directory. Create the directory if it does not exist.
- If `$ARGUMENTS` is empty (command was run as `/kb` with no arguments), use the current working directory.

Example usage:
- `/kb` → saves to current directory
- `/kb docs/kb/` → saves to `docs/kb/` directory (created if needed)
- `/kb ~/kb/` → saves to home directory's `kb/` folder

### 2. Analyze the Conversation

Review the troubleshooting conversation to identify:
- **All distinct problems encountered**: A session may surface multiple independent issues — treat each one separately
- **Symptoms**: What error messages, behaviors, or observables were observed per problem?
- **Investigation steps**: What commands, logs, or diagnostics were performed?
- **Root cause**: Why did each issue occur? Assess your confidence: was the cause confirmed, suspected, or unknown?
- **Quick fix / workaround**: Was there a fast workaround used to unblock the situation before a proper fix?
- **Resolution**: What was the definitive fix for each problem?
- **Verification**: How was each fix confirmed to work?
- **Time to resolve**: Estimate how long the troubleshooting session took from the conversation timeline
- **Severity**: How severe was the impact? (critical / high / medium / low)
- **Related links**: Only if URLs or ticket references were explicitly mentioned in the conversation

### 3. Gather Environment Context

Extract relevant environment information (shared across all problems in the session):
- Cluster/environment name (e.g., EKS production, AKS dev)
- Software versions (Kubernetes, applications, tools)
- Namespace or project context
- Any relevant configuration or infrastructure details

### 4. Determine Article Structure

**If the session had a single problem:** generate one article using the single-problem template.

**If the session had multiple distinct problems:** generate one article per problem, each as a separate file. Also generate a single **Session Index** file that lists all problems with links to each article.

- One file per problem: `<output-dir>/kb-<short-title>-<YYYYMMDD>.md`
- Index file: `<output-dir>/kb-session-index-<YYYYMMDD>.md`

### 5. Generate the KB Article(s)

Create markdown files with the following standardized structure. Be detailed but avoid unnecessary verbosity — focus on actionable information.

## KB Article Template

Use this structure for each problem:

```markdown
---
title: "[SHORT PROBLEM TITLE]"
date: YYYY-MM-DD
kb_category: troubleshooting
severity: high
---

# [Problem Title]

> TL;DR — [One sentence that captures the essence of the problem and resolution]

## Summary
[2-3 sentence overview of the problem and how it was resolved]

## Environment
| Key             | Value                    |
| --------------- | ------------------------ |
| Environment     | [e.g., EKS production]   |
| Version         | [e.g., Kubernetes v1.28] |
| Time to resolve | [e.g., ~45 min]          |

## Symptoms
- [Error message or log snippet]
- [Observed behavior]
- [Related metrics or alerts]

## Root Cause
> Confidence: Confirmed

[Clear explanation of why the issue occurred. Include technical details if relevant.]

## Investigation
- [Command or diagnostic step 1]
- [Command or diagnostic step 2]
- [Key finding from investigation]

## Quick Fix / Workaround
> Use this to unblock immediately. Does not address the root cause.

[Short description of the workaround, or "None identified" if not applicable]

OPTIONAL_BASH_BLOCK

## Resolution
> Permanent fix that addresses the root cause.

1. [First step taken]
2. [Second step taken]
3. [Final resolution step]

## Verification
- [Command to verify fix works]
- [Expected output or behavior]

## Prevention
- [How to avoid this issue in the future]
- [Monitoring or alerting to add]
- [Best practices to implement]

OPTIONAL_RELATED_SECTION
```

Where:
- `severity:` must be one of: `critical`, `high`, `medium`, `low` — pick the correct value, never write the full list
- `> Confidence:` must be one of: `Confirmed`, `Suspected`, `Unknown` — pick one, never write all three
- `OPTIONAL_BASH_BLOCK` — replace with a `bash` code block if workaround commands exist, remove entirely if not
- `OPTIONAL_RELATED_SECTION` — replace with a `## Related` section listing URLs/tickets only if they were explicitly mentioned in the session, otherwise remove entirely

## Session Index Template (multi-problem sessions only)

```markdown
---
title: "Troubleshooting Session - [YYYYMMDD]"
date: YYYY-MM-DD
kb_category: session-index
---

# Troubleshooting Session - [YYYYMMDD]

## Overview
[1-2 sentence summary of the overall session context]

## Environment
| Key         | Value                    |
| ----------- | ------------------------ |
| Environment | [e.g., EKS production]   |
| Version     | [e.g., Kubernetes v1.28] |

## Problems Encountered

| #   | Problem       | Severity | Time to Resolve | Quick Fix | Discovered via | Article                |
| --- | ------------- | -------- | --------------- | --------- | -------------- | ---------------------- |
| 1   | [Short title] | high     | ~30 min         | Yes       | —              | [kb-title-YYYYMMDD.md] |
| 2   | [Short title] | medium   | ~10 min         | No        | #1             | [kb-title-YYYYMMDD.md] |
```

Where:
- `Severity` and `Time to Resolve` use the actual resolved values, not a list of options
- `Discovered via` is the `#` of the problem that led to finding this one (e.g. `#1` if problem 2 was found while investigating problem 1), or `—` if it was independently reported

## Guidelines

### For the Title
- Keep it short but descriptive
- Include the key technology/component
- Example: "Pod CrashLoopBackOff due to OOM in production"

### For TL;DR
- One sentence maximum
- Should help someone quickly decide if this article matches their issue
- Capture: what broke, why it broke, and/or how it was fixed — in any format that works

### For Severity
- `critical` — production down, data loss, security breach
- `high` — major feature broken, significant user impact
- `medium` — degraded performance, workaround available
- `low` — cosmetic, minor inconvenience, no user impact

### For Root Cause confidence
- `Confirmed` — root cause was proven (e.g. a config value was wrong, a bug was found)
- `Suspected` — most likely cause based on evidence but not 100% proven
- `Unknown` — issue was resolved (e.g. by restart) but cause was never identified

### For Time to Resolve
- Estimate from the conversation timeline (e.g. `~20 min`, `~2 h`)
- If not determinable from the conversation, omit the row from the table

### For Root Cause
- Be specific about the technical cause
- Include relevant configuration or code if applicable
- Explain the chain of events if multiple factors contributed

### For Quick Fix / Workaround
- Only include if a real workaround was discussed or implied in the session
- Clearly mark it as temporary — it unblocks but does not fix
- If none exists, write `None identified` — do not invent one
- Keep it short: one paragraph max + commands if applicable

### For Resolution
- Number each step clearly
- Include actual commands with proper escaping
- Be precise — someone should be able to follow these steps exactly

### For Verification
- Provide concrete commands to verify the fix
- Show expected output when possible

### For Prevention
- Suggest monitoring or alerting to detect recurrence
- Recommend automation or tooling improvements

### For Related
- Only write this section if URLs, ticket numbers, or documentation references were explicitly mentioned during the session
- If nothing was referenced, omit the section entirely — do not add placeholder text

### For Discovered via (session index only)
- Use the `#` number of the problem that led to uncovering this one (e.g. `#1`)
- Use `—` if the problem was independently reported or initiated
- A problem can be discovered via another even if they have different root causes

## Output Requirements

1. **Resolve the output directory** from `$ARGUMENTS`:
   - If `$ARGUMENTS` is non-empty, use it as the output path. Create the directory if needed.
   - If `$ARGUMENTS` is empty (no arguments provided), use the current working directory.

2. **Generate the file(s)**:
   - Single problem: `kb-<short-title>-<YYYYMMDD>.md`
   - Multiple problems: one file per problem + one session index file

3. **After creating the file(s)**, show the user:
   - Output directory used
   - List of all files saved with their full paths
   - One-line summary per problem documented
   - Ask if they want to make any edits

4. **Quality checks**:
   - `severity` in frontmatter is a single value, not a list
   - Root cause confidence is a single word, not a list
   - `Related` section is absent unless links were explicitly mentioned
   - Quick Fix / Workaround is clearly distinct from Resolution
   - No sensitive data in any section (see Privacy & Security Guardrails)

## Privacy & Security Guardrails

Before writing anything to the article, **scan and sanitize** all content. This is mandatory and non-negotiable.

### Never include

| Category                     | Examples                                                                            |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| Passwords / secrets / tokens | `password=abc123`, `Bearer eyJ...`, `AWS_SECRET_ACCESS_KEY`, API keys, private keys |
| Local filesystem paths       | `/Users/myuser/Documents/...`, `/home/user/...`, `C:\Users\...`                     |
| Personal identifiable info   | Full names, email addresses, phone numbers, personal IPs                            |
| Internal hostnames / IPs     | `10.x.x.x` private IPs, internal FQDNs unless generic (e.g. `my-service.internal`)  |
| Cloud account identifiers    | AWS account IDs, subscription IDs, project IDs                                      |
| SSH keys / certificates      | Any PEM-formatted content, `-----BEGIN ...-----` blocks                             |

### Replacement rules

When sensitive content is found, replace it with a generic placeholder — **never omit the line entirely** if it is contextually useful:

| Replaced with   | Use for                                    |
| --------------- | ------------------------------------------ |
| `<REDACTED>`    | Passwords, tokens, secrets                 |
| `<LOCAL_PATH>`  | Local filesystem paths                     |
| `<ACCOUNT_ID>`  | Cloud account/subscription IDs             |
| `<INTERNAL_IP>` | Private IP addresses                       |
| `<USERNAME>`    | Usernames embedded in paths or URLs        |
| `<YOUR_VALUE>`  | Any other context-specific sensitive value |

**Example transformation:**
```
# Before
kubectl exec -n prod deploy/api -- env | grep DB_PASSWORD=s3cr3t!
Logs path: /Users/myuser/debug.log

# After
kubectl exec -n prod deploy/api -- env | grep DB_PASSWORD=<REDACTED>
Logs path: <LOCAL_PATH>
```

### URL sanitization

- Strip credentials from URLs: `https://user:pass@host` → `https://<USERNAME>:<REDACTED>@host`
- Keep hostnames only if they are public/generic (e.g. `my-cluster.us-east-1.eks.amazonaws.com` is fine, `internal-corp.example.com` is not)

## Agent Behavior Notes

- **Don't ask for input**: Use the conversation history to extract all needed information
- **Be thorough but focused**: Include relevant technical details, skip irrelevant context
- **Write for your future self**: Imagine you'll need to debug this issue in 6 months — what would you need to know?
- **Include actual values**: Don't use placeholders like `<cluster-name>` — use the actual values from the session, **unless they fall under the privacy guardrails above**
- **Format commands properly**: Use code blocks with the appropriate language identifier
- **Sanitize before writing**: Apply privacy guardrails to every section before saving the file — no exceptions
