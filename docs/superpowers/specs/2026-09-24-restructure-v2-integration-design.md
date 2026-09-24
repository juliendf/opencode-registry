# OpenCode V2 Integration on Restructure

## Goal

Apply OpenCode V2 support to restructured registry layout, retain skills for domain knowledge and subagents for independent execution, and keep all components inheriting active session model when requested.

## Source State and Constraints

- Authoritative source layout is current uncommitted `feat/restructure-subagents-skills` worktree at `restructure/`.
- Preserve all existing restructure changes; do not reset, clean, or commit them.
- Keep `opencode-v2-migration` worktree as source until integrated tests and global V2 smoke pass.
- Preserve `openpackage` and `productManagement` worktrees and their contents.
- Preserve untracked `opencode/skills/.openpackage/` from migration worktree in a sibling backup before removing that worktree.
- Do not push, merge, or commit integration changes without user approval.

## Architecture

### Component roles

- `build` and `plan` remain primary agents.
- Domain expertise moves through V2 `skill` calls to restructured skill IDs.
- Retained execution subagents use V2 `subagent` calls with full path-derived IDs, including the `subagents/` directory prefix (for example, `subagents/infrastructure-engineer`).
- Do not restore deleted specialist agent files or reuse old nested IDs. Keep `review` usable both as a primary and child agent with `mode: all`.
- Preserve restructure's component layout and counts:

```text
opencode/
├── agents/                         # Primary agents (5)
│   ├── ask-me-anything.md
│   ├── plan.md
│   ├── build.md
│   ├── debug.md
│   ├── review.md
│   └── subagents/                  # Specialist subagents (10, flat)
│       ├── infrastructure-engineer.md
│       ├── data-engineer.md
│       ├── ml-engineer.md
│       ├── mlops-engineer.md
│       ├── ai-engineer.md
│       ├── penetration-tester.md
│       ├── security-auditor.md
│       ├── mobile-developer.md
│       ├── cli-developer.md
│       └── fullstack-developer.md
├── skills/                         # Knowledge skills (40+)
│   ├── python-pro/
│   ├── typescript-pro/
│   ├── aws-patterns/
│   ├── kubernetes-patterns/
│   └── ...
└── commands/                       # Custom commands (3)
    ├── commit.md
    ├── documentation.md
    └── kb.md
```

The outline's `pentetration-tester` spelling is a typo; keep existing canonical filename `penetration-tester.md` and use V2 ID `subagents/penetration-tester`.

### Delegation tests

- Adapt `test_delegation.py` to V2 JSON event names and arguments, using actual V2 output fixtures.
- Test subagent tool calls only for agents retained as executable subagents.
- Add skill-loading coverage for domain expertise now represented by skills; do not interpret skill loads as subagent calls.
- Retain V2 response-text parsing and any V1 parser fallback only where it remains useful and covered.

### Installer and model inheritance

- Add `--inherit-model` to `install` and `update`; skip tier validation and remove top-level `model`, `model_tier`, and `variant` from installed agent/command frontmatter.
- Keep source tier metadata and default tier-based install behavior unchanged.
- Preserve skill entrypoint files byte-for-byte.
- Require the flag on each install/update invocation; do not store a persistent user-wide policy. Reject `--model` with `--inherit-model`.
- Restructure’s existing optional-tier behavior remains; explicit inherit mode overrides configured tiers when users want every component to follow session model.

### Documentation and local cutover

- Port V2 prerequisites, permissions semantics, skill/subagent usage, and inherit-model instructions into restructured docs without restoring obsolete component counts or paths.
- Before switching the global install, dry-run old registry uninstall from `opencode-v2-migration`, then remove only files present in that old registry source. Do not delete whole global `agents/`, `skills/`, or `commands/` directories; preserve unrelated items such as cavecrew components and auth/config files.
- Install restructured package with `--inherit-model`; verify new flat agents/skills, no model selector fields, and V2 execution/skill loading.
- Only after verification, move `.openpackage` metadata to approved sibling backup and remove `opencode-v2-migration` worktree. Leave its local branch unless user asks to delete it.

## Verification

1. Unit tests cover V2 tool event parsing, response text, skill ID extraction, and tierless installer behavior.
2. Full installer test suite passes on restructured tree.
3. Static checks confirm old nested subagent IDs are not used as V2 tool targets and model selectors are absent from tierless installed agent/command frontmatter.
4. Run a live V2 smoke test from restructure-installed global files: load a domain skill and invoke one retained execution subagent.
5. Dry-run and execute global uninstall/install only after showing exact paths affected; verify unrelated global components remain.

## Non-goals

- Committing or pushing uncommitted restructure work.
- Deleting `openpackage` or `productManagement` worktrees.
- Blanket deletion of user configuration or OpenCode-global directories.
