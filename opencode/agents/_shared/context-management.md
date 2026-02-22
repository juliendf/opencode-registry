---
name: Context Management
description: Guidelines for managing conversation context and session length across all agents
type: shared-config
mode: all
hidden: true
version: "1.0.0"
---

# Context Management Guidelines

All agents must monitor conversation length and manage context proactively to maintain effectiveness.

## Context Window Awareness

**Monitor for these signals:**
- Conversation spans 50+ messages
- Multiple complex topics discussed
- Repeated file reads or tool calls
- Slower response times
- User mentions context/memory issues

## When Approaching Context Limits

**Proactive actions (before hitting 80% capacity):**

1. **Use todowrite as checkpoint:**
   ```
   todowrite: Capture current state
   - Files modified: src/auth.ts, src/middleware.ts
   - Completed: JWT setup, middleware implementation
   - In progress: Testing auth flow
   - Next: Add protected routes, update docs
   ```

2. **Summarize key context:**
   - Critical decisions made and rationale
   - File paths and changes
   - Error traces or debugging insights
   - Requirements or constraints discovered

3. **Suggest session refresh:**
   ```
   "We've covered a lot. I recommend starting a fresh session with this summary:
   - Implemented JWT auth in src/auth.ts
   - Added middleware to protect routes
   - Next: Add /api/protected endpoint
   This will give us a clean context for the remaining work."
   ```

## What to Preserve

**Essential context to carry forward:**
- File paths and locations
- Error messages and stack traces
- User requirements and constraints
- Decisions made (with brief rationale)
- Next steps from todos

**What to drop:**
- Intermediate debugging attempts
- Full file contents (summarize changes instead)
- Tangential discussions
- Redundant explanations

## Session Handoff Pattern

When context is full:

1. **Create comprehensive summary:**
   ```markdown
   ## Session Summary
   **Goal:** Add user authentication with JWT
   
   **Completed:**
   - Installed jsonwebtoken (package.json)
   - Created src/auth/jwt.ts with sign/verify functions
   - Added src/middleware/auth.ts for route protection
   - Tests passing in tests/auth.test.ts
   
   **Next Steps:**
   - Add POST /api/login endpoint
   - Update API docs
   - Add rate limiting to login
   
   **Key Decisions:**
   - Using HS256 algorithm (symmetric key)
   - 24h token expiration
   - Storing user ID only in payload
   ```

2. **Save to file or todowrite**
3. **Suggest user starts fresh with summary**

## Special Cases

**Long debugging sessions:**
- Summarize: "Traced issue to X, tried Y and Z, narrowed to file:line"
- Drop: Full output of failed attempts

**Large refactors:**
- Track files changed in todowrite
- Summarize pattern applied, not every edit

**Multi-agent workflows:**
- Each subagent call is fresh context
- Include relevant summary in subagent prompt
- Synthesize results concisely on return

## Best Practices

1. **Be preemptive** - Don't wait for degraded performance
2. **Use tools** - todowrite is state persistence
3. **Summarize, don't repeat** - Reference decisions made, don't re-explain
4. **Chunk work** - Suggest natural breakpoints for session refresh
5. **Trust the user** - They can start new sessions; just provide good handoff

---

**This protocol applies to all agents (primary and subagents).**
