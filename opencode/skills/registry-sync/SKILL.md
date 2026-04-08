---
model_tier: "medium"
name: registry-sync
description: Discover and sync OpenCode components (agents, subagents, skills, commands, MCP servers) from the registry's MCP server. Compares versions against locally installed components and presents a sync plan before making changes.
compatibility: opencode
license: MIT
metadata:
  version: "1.0.0"
---

# Registry Sync

Discover available components from the OpenCode Registry MCP server, compare them against locally installed versions, and sync new or updated components to the local OpenCode configuration directory.

## Prerequisites

This skill requires the **opencode-registry** MCP server to be running and connected. The server exposes `list_*` and `get_*` tools for each component type:

- `list_agents`, `get_agent`
- `list_subagents`, `get_subagent`
- `list_skills`, `get_skill`
- `list_commands`, `get_command`
- `list_mcp_servers`, `get_mcp_server`

If these tools are not available, inform the user that the registry MCP server needs to be configured and running.

## When to Use This Skill

Activate when the user wants to:

- Sync components from the registry to their local OpenCode config
- Check which components are available vs. installed
- Update outdated components to newer versions
- Install specific components by name or type
- See what's new or changed in the registry

**Do NOT use this skill for:**

- Creating new components in the registry (use `create_*` MCP tools directly)
- Editing component content (edit files directly)
- Managing the MCP server itself (starting/stopping)

## Key Concepts

### Local Config Directory

Components are installed to `~/.config/opencode/` with this structure:

```text
~/.config/opencode/
  agents/
    <agent-slug>.md
    subagents/
      <category>/
        <subagent-slug>.md
  skills/
    <skill-slug>/
      SKILL.md
      [additional files]
  commands/
    <command-slug>.md
```

MCP server definitions are informational -- they describe how to configure an MCP server in `opencode.json`, not files that get copied to a specific location.

### Version Comparison

Components use semantic versioning in their frontmatter (`metadata.version` or `version` field). The sync decision logic:

| Local State | Remote Version | Action |
|---|---|---|
| Not installed | Any | **New** -- available to install |
| Installed, same version | Same | **Up to date** -- skip |
| Installed, lower version | Higher | **Outdated** -- available to update |
| Installed, higher version | Lower | **Ahead** -- skip (local is newer) |
| Installed, no version | Any | **Unknown** -- flag for review |
| Not installed | No version | **New (unversioned)** -- available to install |

### Version Extraction

Versions can appear in different frontmatter locations depending on component type:

- **Agents/subagents**: No standard version field (use content hash as fallback -- compare body text)
- **Skills**: `metadata.version` in frontmatter
- **Commands**: `version` in frontmatter
- **MCP servers**: `version` in frontmatter

When no version field exists, fall back to comparing the full markdown body content. If bodies differ, mark as **Changed** in the sync plan.

## Workflow

### Step 1: Determine Scope

Parse the user's request to determine what to sync:

- **All components**: "sync everything", "sync all", "check for updates"
- **Specific type**: "sync agents", "sync skills", "update subagents"
- **Specific component**: "sync the golang-pro subagent", "install kb-search skill"
- **Status check only**: "what's available?", "show me what's outdated"

If the scope is unclear, default to a **status check** (show what's available and what's outdated) without syncing.

### Step 2: Discover Remote Components

Call the appropriate `list_*` tools to get the registry inventory. For each component type in scope:

1. Call `list_agents` / `list_subagents` / `list_skills` / `list_commands` / `list_mcp_servers`
2. Record the metadata: `slug`, `name`, `version`, `description`, and for subagents the `category`

For subagents, call `list_subagents` without a category filter to get all subagents across all categories.

### Step 3: Scan Local Components

For each discovered remote component, check the corresponding local path:

| Type | Local Path |
|---|---|
| agent | `~/.config/opencode/agents/<slug>.md` |
| subagent | `~/.config/opencode/agents/subagents/<category>/<slug>.md` |
| skill | `~/.config/opencode/skills/<slug>/SKILL.md` |
| command | `~/.config/opencode/commands/<slug>.md` |
| mcp-server | N/A (informational only -- show config snippet) |

For each local file that exists:

1. Read the file
2. Extract the version from frontmatter (location depends on type -- see Version Extraction above)
3. Compare against the remote version

### Step 4: Build Sync Plan

Compile a sync plan table showing every component in scope:

```markdown
## Sync Plan

### Agents (3 available, 1 new, 1 outdated)
| Component | Local Version | Remote Version | Status | Action |
|---|---|---|---|---|
| ask-me-anything | 1.0.0 | 1.0.0 | Up to date | Skip |
| debug | 0.9.0 | 1.1.0 | Outdated | Update |
| new-agent | -- | 1.0.0 | New | Install |

### Subagents (46 available, 2 new)
...

### Skills (8 available, all up to date)
...

### Commands (3 available)
...

### MCP Servers (1 available)
| Server | Description | Transport | Status |
|---|---|---|---|
| ragclaw | Go-to knowledge base for AI agents | stdio | Config snippet available |
```

**Always present this plan to the user and ask for confirmation before writing any files.**

If the user only asked for status ("what's available?"), stop here -- do not prompt for sync.

### Step 5: Confirm and Execute

After presenting the plan, ask the user what to do:

- **Sync all** -- install new + update outdated
- **Install new only** -- skip updates
- **Update outdated only** -- skip new installs
- **Cherry-pick** -- user specifies which components to sync
- **Cancel** -- do nothing

Once confirmed, for each component to sync:

1. Call `get_<type>` with the component's slug (and category for subagents) to get the full content
2. Determine the local file path
3. Create parent directories if they don't exist (`mkdir -p`)
4. Write the content to the local file path

**For skills**: The `get_skill` response includes a `files` array listing additional files in the skill directory. For each file, you'll need to fetch its content. Since the MCP resource `opencode://skills/{slug}` returns all files, read the resource to get the complete skill content including auxiliary files. Write `SKILL.md` and each auxiliary file to `~/.config/opencode/skills/<slug>/`.

**For MCP servers**: Do NOT write a file. Instead, show the user the configuration snippet they need to add to their `opencode.json` (or equivalent). Example:

```json
{
  "mcp": {
    "<server-slug>": {
      "command": "<command>",
      "args": ["<args>"]
    }
  }
}
```

### Step 6: Report Results

After syncing, show a summary:

```markdown
## Sync Complete

- Installed: 2 new components (new-agent, my-skill)
- Updated: 1 component (debug: 0.9.0 -> 1.1.0)
- Skipped: 15 up-to-date components
- Errors: 0
```

If any errors occurred (e.g. file write failures), list them with details.

## Error Handling

- **MCP server not connected**: Tell the user to configure and start the opencode-registry MCP server
- **MCP tool call fails**: Report the error for the specific component, continue with others
- **Local file write fails**: Report the error, do not retry automatically
- **No components found**: The registry might be empty or the MCP server is pointing to the wrong directory -- suggest checking the `--dir` flag
- **Version parse failure**: If a version string isn't valid semver, treat it as a content comparison instead

## Examples

**User**: "Sync all components from the registry"
**Agent**: Discovers all 5 types -> builds plan -> presents table -> asks confirmation -> syncs

**User**: "What's available in the registry?"
**Agent**: Discovers all types -> presents plan as status check -> stops (no sync)

**User**: "Update my agents"
**Agent**: Discovers agents only -> compares -> presents plan for agents -> asks confirmation

**User**: "Install the golang-pro subagent"
**Agent**: Calls `get_subagent` with category + slug -> writes to local path -> confirms

**User**: "Is my kb-search skill up to date?"
**Agent**: Compares local vs remote version -> reports status
