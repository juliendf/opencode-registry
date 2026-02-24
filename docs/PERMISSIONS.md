# Permissions & Tools Guide

How OpenCode permission system works in this registry, and how to configure agent autonomy.

## How Permissions Work

OpenCode has **two levels** of permission configuration:

```
~/.config/opencode/opencode.json   ← Global (your machine)
opencode/agents/<agent>.md         ← Agent-level (frontmatter)
```

**Critical rule:** Agent-level permissions **override** global config entirely for that agent. They do not merge — the last matching pattern wins within a given scope.

```
Global:  "grep *": "allow"
Agent:   "*": "ask"           ← This wins. grep will ask.

Global:  "grep *": "allow"
Agent:   (no bash section)    ← Global wins. grep is allowed.
```

This means: if an agent defines `bash: "*": "ask"`, your global read-only allowlist is completely ignored for that agent.

---

## Tools vs Bash

OpenCode provides **dedicated tools** that bypass the bash permission system entirely:

| Dedicated Tool | Replaces bash | Permission key |
|----------------|---------------|----------------|
| `Read`         | `cat`, `head`, `tail` | `read` |
| `Grep`         | `grep`, `rg`  | `grep` (tool, not bash) |
| `Glob`         | `find`, `ls`  | `glob` (tool, not bash) |
| `Edit`         | `sed`, `awk`  | `edit` |
| `Write`        | `echo >`, `cat <<EOF` | `write` |

Agents in this registry have all dedicated tools enabled by default (`grep: true`, `read: true`, `glob: true`, etc.).

**Prefer dedicated tools** — they are faster, safer, and don't require bash permission rules.

**Use bash for:** actual system commands, CLI tools, package managers, runtime execution.

---

## Agent Frontmatter Structure

```yaml
---
description: "..."
mode: primary | subagent
tools:
  bash: true        # Enable bash tool
  read: true        # Enable Read tool  (file reading)
  grep: true        # Enable Grep tool  (content search)
  glob: true        # Enable Glob tool  (file pattern matching)
  edit: true        # Enable Edit tool  (file editing)
  write: true       # Enable Write tool (file writing)
  webfetch: true    # Enable WebFetch tool
permission:
  read: allow | ask | deny     # Dedicated Read tool permission
  edit:
    "*": "ask"                 # Ask before editing any file
    "src/**": "allow"          # Allow editing src/ freely
  write:
    "*": "ask"
  bash:
    "kubectl apply*": "ask"    # Specific overrides
    "rm -rf*": "deny"          # Hard deny
    # No "*": "ask" here → inherits global config
---
```

---

## This Registry's Approach

### What agents define (safety-critical only)

Agents only override permissions for **domain-specific dangerous operations**:

| Agent category | What they restrict |
|----------------|--------------------|
| All agents | `"rm -rf*": "ask"`, `"git push --force*": "ask"` |
| Kubernetes | `"kubectl apply*": "ask"`, `"kubectl delete*": "ask"` |
| Terraform | `"terraform apply*": "ask"`, `"terraform destroy*": "ask"` |
| Cloud (AWS/GCP/Azure) | `"*create*": "ask"`, `"*delete*": "ask"` |
| Database | `"psql*": "ask"`, `"mysql*": "ask"` |
| Git | `"git push*": "ask"`, `"git commit*": "ask"` |

Agents do **not** define `bash: "*": "ask"` — this would override your global config and block all read-only commands.

### What global config defines (read-only allowlist)

Your `~/.config/opencode/opencode.json` defines the broad read-only allowlist that all agents inherit:

```json
{
  "permission": {
    "read": "allow",
    "write": "ask",
    "bash": {
      "*": "ask",
      "grep *": "allow",
      "cat *": "allow",
      "ls *": "allow",
      "tail *": "allow",
      "find *": "allow",
      "diff *": "allow",
      "git status*": "allow",
      "git log*": "allow",
      "kubectl get *": "allow",
      "kubectl describe *": "allow",
      ...
    }
  }
}
```

---

## Recommended Global Config

A comprehensive read-only allowlist for `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": "allow",
    "write": "ask",
    "bash": {
      "*": "ask",

      "grep *": "allow",
      "echo *": "allow",
      "find *": "allow",
      "wc *": "allow",
      "ls *": "allow",
      "head *": "allow",
      "cat *": "allow",
      "tail *": "allow",
      "file *": "allow",
      "stat *": "allow",
      "du *": "allow",
      "df *": "allow",

      "which *": "allow",
      "whereis *": "allow",
      "type *": "allow",
      "pwd": "allow",
      "whoami": "allow",
      "env": "allow",
      "printenv *": "allow",
      "date": "allow",
      "uname *": "allow",

      "sort *": "allow",
      "uniq *": "allow",
      "diff *": "allow",
      "cut *": "allow",
      "awk *": "allow",
      "sed -n *": "allow",
      "column *": "allow",

      "ps *": "allow",
      "pgrep *": "allow",

      "git status*": "allow",
      "git log*": "allow",
      "git diff*": "allow",
      "git show*": "allow",
      "git branch*": "allow",
      "git remote*": "allow",

      "kubectl get *": "allow",
      "kubectl describe *": "allow",
      "kubectl logs *": "allow",
      "kubectl config current-context": "allow",
      "kubectl config get-contexts": "allow",

      "docker ps*": "allow",
      "docker images": "allow",
      "docker inspect *": "allow",

      "npm list*": "allow",
      "npm info*": "allow",
      "pip list*": "allow",
      "pip show*": "allow"
    }
  }
}
```

---

## When to Add Agent-Level Bash Rules

Only add bash rules to an agent when the agent has **domain-specific dangerous operations** that the global config doesn't cover.

**Good — agent-specific safety rule:**
```yaml
permission:
  bash:
    "terraform apply*": "ask"
    "terraform destroy*": "ask"
```

**Bad — blocks global read-only config:**
```yaml
permission:
  bash:
    "*": "ask"            # Never add this. It overrides global config entirely.
    "git status*": "allow"
```

**Bad — duplicating what global config already covers:**
```yaml
permission:
  bash:
    "grep *": "allow"     # Already in global config, don't repeat in every agent.
    "ls *": "allow"
```

---

## Debugging Permission Issues

If an agent keeps asking for permission on read-only commands:

**1. Check if agent has `"*": "ask"` in its bash section:**
```bash
grep -r '"*": "ask"' opencode/agents/
```

**2. Remove the wildcard, keep specific rules:**
```yaml
# Before
permission:
  bash:
    "*": "ask"
    "kubectl apply*": "ask"

# After
permission:
  bash:
    "kubectl apply*": "ask"   # Only keep domain-specific rules
```

**3. Verify your global config is valid JSON:**
```bash
python3 -m json.tool ~/.config/opencode/opencode.json
```

**4. Confirm the command pattern matches:**

OpenCode uses glob pattern matching with **last rule wins** semantics:
```json
"git *": "allow",
"git push *": "ask"    ← This wins for git push (more specific, defined last)
```

---

## Pattern Matching Reference

| Pattern | Matches |
|---------|---------|
| `"*"` | Everything |
| `"git *"` | Any git subcommand |
| `"kubectl get *"` | kubectl get with any args |
| `"kubectl *list*"` | kubectl commands containing "list" |
| `"rm -rf*"` | rm -rf with any path |
| `"terraform apply*"` | terraform apply with any flags |

Rules are evaluated **top to bottom, last match wins**. Put specific rules after general ones.
