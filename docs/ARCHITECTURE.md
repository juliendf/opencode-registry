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
│  │  bundles/           (Bundle Definitions)                 │  │
│  │  ├── basic.yaml     (4 essential components)             │  │
│  │  ├── intermediate.yaml (10+ components)                  │  │
│  │  └── advanced.yaml  (all 55 components)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  installer/         (Python CLI Tool)                    │  │
│  │  └── src/opencode_config/                                │  │
│  │      ├── cli.py                                          │  │
│  │      ├── commands/  (8 command modules)                  │  │
│  │      └── utils/     (core utilities)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ opencode-config install
                         │ (via GNU Stow or symlinks)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              Target Installation Directory                      │
│              ~/.config/opencode/                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  agents/                                                  │  │
│  │  ├── plan-design.md           → symlink to registry      │  │
│  │  ├── plan-architecture.md     → symlink to registry      │  │
│  │  ├── build-code.md            → symlink to registry      │  │
│  │  ├── cngmember.md           (user's custom agent)      │  │
│  │  └── subagents/              → symlink to registry      │  │
│  │      └── [43 subagents]                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  skills/                                                  │  │
│  │  ├── project-docs/           → symlink to registry      │  │
│  │  ├── mcp-builder/            → symlink to registry      │  │
│  │  └── proofread-skills/       (user's custom skill)      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  commands/                    → symlink to registry      │  │
│  │  └── [3 commands]                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ Tracked by
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              Installation Database                              │
│              ~/.opencode-registry/                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  config.json                                             │  │
│  │  {                                                       │  │
│  │    "target_dir": "~/.config/opencode",                   │  │
│  │    "registry_path": "~/Documents/.../opencode-registry"  │  │
│  │  }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  installed.json                                          │  │
│  │  {                                                       │  │
│  │    "installed": {                                        │  │
  │  │      "agents": { ... },        (5 components)            │  │
│  │      "subagents": { ... },     (43 components)           │  │
│  │      "skills": { ... },        (3 components)            │  │
│  │      "commands": { ... }       (3 components)            │  │
│  │    },                                                    │  │
│  │    "bundles": { "basic": {...} },                        │  │
│  │    "logs": { ... }                                       │  │
│  │  }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Flow

```
┌─────────────┐
│   User      │
│  Terminal   │
└──────┬──────┘
       │
       │ opencode-config list
       │ opencode-config install --group basic
       │ opencode-config status
       │
       ▼
┌─────────────────────────────────────────┐
│         CLI Commands                    │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │  list    │  │  info    │            │
│  └──────────┘  └──────────┘            │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │ install  │  │  status  │            │
│  └──────────┘  └──────────┘            │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │  sync    │  │ uninstall│            │
│  └──────────┘  └──────────┘            │
└────────┬────────────────────────────────┘
         │
         │ Uses
         │
         ▼
┌─────────────────────────────────────────┐
│         Core Utilities                  │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  StowManager                     │   │
│  │  - Install/uninstall packages    │   │
│  │  - Detect installed components   │   │
│  │  - Verify symlinks               │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  InstalledDB                     │   │
│  │  - Track components              │   │
│  │  - Sync from disk                │   │
│  │  - Log actions                   │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  ManifestParser                  │   │
│  │  - Parse YAML frontmatter        │   │
│  │  - Extract metadata              │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  Config                          │   │
│  │  - Manage settings               │   │
│  │  - Auto-detect paths             │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
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
    │  3. Run Stow                │
    │  stow --dir registry        │
    │       --target ~/.config    │
    │       opencode              │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  4. Detect Components       │
    │  Scan ~/.config/opencode/   │
    │  - Find symlinks            │
    │  - Count by type            │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  5. Update Database         │
    │  installed.json             │
    │  - Add components           │
    │  - Add bundle               │
    │  - Log action               │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  6. Show Results            │
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
    │  Only count symlinks that   │
    │  point to registry          │
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
│   Registry   │────▶│   Stow       │────▶│   Target     │
│   Components │     │   Symlinks   │     │   Directory  │
└──────────────┘     └──────────────┘     └───────┬──────┘
                                                   │
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
│  ┌──────────────────┐        ┌──────────────────┐      │
│  │   GNU Stow       │        │   Symlinks       │      │
│  │   (preferred)    │   OR   │   (fallback)     │      │
│  └──────────────────┘        └──────────────────┘      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   File System                           │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ~/.config/opencode/    (Target)                 │   │
│  │  ~/.opencode-registry/  (Database)               │   │
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
│ INSTALLED  │  (Symlinked to ~/.config/opencode/)
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
│  REMOVED   │  (Symlink deleted, database updated)
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
│                  Symlink Isolation                      │
│                                                         │
│  Symlinks point FROM target TO source                   │
│  Breaking symlinks only affects target, not source      │
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
3. **Reversible:** Everything can be uninstalled cleanly
4. **Transparent:** Database shows exactly what's installed
5. **Safe:** Dry-run mode for all operations
