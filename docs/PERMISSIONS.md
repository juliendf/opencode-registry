# OpenCode V2 Permissions Guide

OpenCode V2 uses ordered permission rules to control tools, skills, subagents, shell commands, and file access. Registry agent files may retain supported V1 frontmatter for compatibility, but new permission examples should use V2 `permissions` arrays.

## Rule format

Each rule has an action, resource, and effect:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" },
  ],
}
```

Effects are `allow`, `ask`, and `deny`. If no rule matches, OpenCode asks. Rules are evaluated in order; **the last matching rule wins**. Put broad rules first, followed by narrower exceptions.

## Global and agent-specific rules

Global rules belong in `~/.config/opencode/opencode.json` or a project `opencode.json(c)`. Agent-specific rules belong in an agent's `permissions` frontmatter:

```yaml
---
description: Reviews code without modifying it
mode: all
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
---
```

Global rules are combined before agent-specific rules; agent-specific rules append and can refine them. Last matching rule still wins. Rules are not replaced wholesale by the agent block.

## V2 action names

| Action | Resource example | Covers |
|---|---|---|
| `read` | `src/**` | Read files |
| `edit` | `src/**` | Edit, write, and patch operations |
| `shell` | `git status *` | Shell commands |
| `glob` | `**/*.py` | File pattern search |
| `grep` | `TODO` | Content search |
| `subagent` | `subagents/infrastructure-engineer` | Launching a child agent by exact ID |
| `skill` | `python-pro` | Loading a skill by exact ID |
| `webfetch` | `https://example.com/**` | Fetching a URL |
| `websearch` | `OpenCode V2 permissions` | Web searches |

V2 action names differ from V1: `bash` becomes `shell`, `task` becomes `subagent`, and `write`/`patch` become `edit`. The V1 `permission` field becomes `permissions` when using native V2 configuration.

## Allow specific skills and subagents

Skill and subagent resources must match their IDs exactly. Subagent filenames under `agents/subagents/` have V2 IDs prefixed with `subagents/`:

```yaml
permissions:
  - action: skill
    resource: "*"
    effect: deny
  - action: skill
    resource: python-pro
    effect: allow
  - action: subagent
    resource: "*"
    effect: deny
  - action: subagent
    resource: subagents/infrastructure-engineer
    effect: allow
```

Put deny-all rules before allowed exceptions so the later exact rule takes precedence.

## Restrict risky operations

Use narrowly scoped rules for sensitive actions. Shell runs with the host user's filesystem, process, and network authority; avoid broad shell allowlists.

```jsonc
{
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" },
    { "action": "edit", "resource": "*.env", "effect": "deny" },
  ],
}
```

For file paths outside the active project, configure `external_directory` access separately; read/edit permissions alone do not grant that boundary.

## Compatibility

OpenCode V2 continues to accept supported V1 permission frontmatter and configuration as compatibility input. V1 names such as `permission`, `bash`, and `task` should not be copied into new V2 examples. See the [V2 migration guide](https://opencode.ai/v2/docs/migrate-v1) and [V2 permissions reference](https://opencode.ai/v2/docs/permissions) for current behavior.
