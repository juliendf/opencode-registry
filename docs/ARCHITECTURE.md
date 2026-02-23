# OpenCode Registry Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    OpenCode Registry                            │
│                                                                 │
│  GitHub Repo (Source of Truth)                                 │
│  └─ 55 Components: Primary Agents, Subagents, Skills, Commands │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Git Clone / Pull
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              Local Registry Directory                           │
│              ~/opencode-registry/                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  opencode/          (Component Library)                  │  │
│  │  ├── agents/        (7 primary agents)                   │  │
│  │  │   └── subagents/ (43 specialized subagents)           │  │
│  │  ├── skills/        (3 skills)                           │  │
│  │  └── commands/      (2 commands)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  installer/         (CLI Tool)                           │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  CopyManager                                       │  │  │
│  │  │  - Install/uninstall packages                      │  │  │
│  │  │  - Detect installed components                     │  │  │
│  │  │  - Process model_tier templates                    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  TemplateEngine                                    │  │  │
│  │  │  - Resolve model tiers                             │  │  │
│  │  │  - Process {{tier:X}} patterns                     │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  InstalledDB                                       │  │  │
│  │  │  - Track components                                │  │  │
│  │  │  - Sync from disk                                  │  │  │
│  │  │  - Log actions                                     │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  ManifestParser                                    │  │  │
│  │  │  - Parse YAML frontmatter                          │  │  │
│  │  │  - Extract metadata                                │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Config                                            │  │  │
│  │  │  - Manage settings                                 │  │  │
│  │  │  - Auto-detect paths                               │  │  │
│  │  │  - Model tier configuration                        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Installation Flow

```
User runs: opencode-config install --group basic

    ┌─────────────────────────────┐
    │  1. Load Configuration      │
    │  - Target dir               │
    │  - Registry path            │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  2. Read Bundle YAML        │
    │  bundles/basic.yaml         │
    │  - List of component IDs    │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  3. Resolve Model Tiers     │
    │  config model_tiers         │
    │  - high → claude-sonnet-4.5 │
    │  - medium → claude-sonnet-4 │
    │  - low → claude-haiku-4.5   │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  4. Copy & Process Files    │
    │  CopyManager copies each    │
    │  file; model_tier: replaced │
    │  with model: <resolved>     │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  5. Detect Components       │
    │  Scan ~/.config/opencode/   │
    │  - Find copied .md files    │
    │  - Count by type            │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  6. Update Database         │
    │  installed.json             │
    │  - Add components           │
    │  - Add bundle               │
    │  - Log action               │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  7. Show Results            │
    │  "✓ Bundle installed        │
    │   Components: 55"           │
    └─────────────────────────────┘
```

## Sync Flow

```
User runs: opencode-config sync

    ┌─────────────────────────────┐
    │  1. Scan Target Directory   │
    │  ~/.config/opencode/        │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  2. Detect Components       │
    │  ┌───────────────────────┐  │
    │  │ agents/*.md            │  │
    │  │ → Primary agents      │  │
    │  ├───────────────────────┤  │
    │  │ agents/subagents/**    │  │
    │  │ → Subagents           │  │
    │  ├───────────────────────┤  │
    │  │ skills/*/              │  │
    │  │ → Skills              │  │
    │  ├───────────────────────┤  │
    │  │ commands/*.md          │  │
    │  │ → Commands            │  │
    │  └───────────────────────┘  │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  3. Filter Registry Items   │
    │  Only count files that      │
    │  came from registry         │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  4. Rebuild Database        │
    │  Clear existing components  │
    │  Add detected components    │
    │  Preserve bundles & logs    │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  5. Show Summary            │
    │  "Detected 60 components:   │
    │   - Agents: 8               │
    │   - Subagents: 43           │
    │   - Skills: 5               │
    │   - Commands: 4"            │
    └─────────────────────────────┘
```

## Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Registry   │────▶│  CopyManager │────▶│   Target     │
│   Components │     │  + Template  │     │   Directory  │
└──────────────┘     │  Engine      │     └───────┬──────┘
                     └──────────────┘             │
                                                  │
                                                  ▼
                                         ┌──────────────┐
                                         │   Database   │
                                         │   Tracking   │
                                         └──────────────┘
                                                  │
                                                  │
                                                  ▼
                                         ┌──────────────┐
                                         │   Status     │
                                         │   Display    │
                                         └──────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                        │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Terminal │  │  Colors  │  │  Tables  │             │
│  │  (bash)  │  │  (Rich)  │  │  (Rich)  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   CLI Framework                         │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Click 8.0+ (Command handling)                   │   │
│  │  - Decorators, arguments, options                │   │
│  │  - Help generation, validation                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                Business Logic                           │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐       │
│  │  Python    │  │   YAML     │  │    JSON     │       │
│  │  3.8+      │  │  Parser    │  │   Parser    │       │
│  └────────────┘  └────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Installation Layer                     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │   CopyManager + TemplateEngine                   │   │
│  │   (file copy with model tier resolution)         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   File System                           │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ~/.config/opencode/    (Target)                 │   │
│  │  ~/.config/opencode/opencode-registry-*.json     │   │
│  │  ~/Documents/.../opencode-registry (Source)      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Lifecycle

```
┌────────────┐
│  CREATED   │  (Author writes component.md with frontmatter)
└─────┬──────┘
      │
      ▼
┌────────────┐
│  PUBLISHED │  (Pushed to GitHub registry)
└─────┬──────┘
      │
      ▼
┌────────────┐
│ AVAILABLE  │  (Shows in 'list' command)
└─────┬──────┘
      │
      │ User runs: opencode-config install
      │
      ▼
┌────────────┐
│ INSTALLED  │  (Copied to ~/.config/opencode/, model: resolved)
└─────┬──────┘
      │
      │ Tracked in installed.json
      │
      ▼
┌────────────┐
│  TRACKED   │  (Shows in 'status' command)
└─────┬──────┘
      │
      │ User runs: opencode-config uninstall
      │
      ▼
┌────────────┐
│  REMOVED   │  (File deleted, database updated)
└────────────┘
```

## Security Model

```
┌─────────────────────────────────────────────────────────┐
│                   Read-Only Source                      │
│                                                         │
│  The registry is never modified by the CLI              │
│  All changes are in target directory and database       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Copy Isolation                         │
│                                                         │
│  Files are copied FROM registry TO target               │
│  Registry source files are never touched                │
│  Deleting installed files only affects target           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   User Ownership                        │
│                                                         │
│  User's custom files are never modified or deleted      │
│  Registry components installed alongside, not replacing │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Dry-Run Protection                      │
│                                                         │
│  All destructive operations support --dry-run           │
│  Preview before committing changes                      │
└─────────────────────────────────────────────────────────┘
```

---

**Architecture Principles:**

1. **Source of Truth:** GitHub registry, never modified locally
2. **Merge-Friendly:** Coexists with user's custom components
3. **Model-Aware:** Each component's model tier is resolved at install time
4. **Reversible:** Everything can be uninstalled cleanly
5. **Transparent:** Database shows exactly what's installed
6. **Safe:** Dry-run mode for all operations
