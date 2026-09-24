# Changelog

## v1.0.0 — Major Reorganization

### Breaking Changes

**Agent restructuring:**
- `plan-design` + `plan-architecture` → merged into `plan`
- `build-code` → renamed to `build`
- `build-infrastructure` → replaced by `infrastructure-engineer` subagent

**Subagent consolidation:**
- 43 subagents → 10 subagents (flat structure, no category folders)
- 30+ former subagents converted to skills (language expertise, infrastructure patterns)
- Domain expertise now loaded via `skill()` instead of `task()`

**Removed fields:**
- `version:` removed from all agent/subagent frontmatter (caused API errors on some providers)

**Model tiers now optional:**
- Install no longer aborts when tiers are not configured
- Unconfigured tiers: `model_tier` line removed on install, components inherit caller model

### Added
- 40+ skills covering languages, architecture patterns, infrastructure, quality, and workflows
- New delegation model: `skill()` for knowledge, `task()` for autonomous execution
- `_shared/delegation-rules.md` rewritten for new architecture

### Changed
- Subagent path flattened: `subagents/01-core/` → `subagents/`
- `_shared/` files simplified (delegation-rules slimmed from 333 to 60 lines)
- Updated all documentation (README, AGENT-GUIDE, GETTING-STARTED, QUICKREF, FAQ)

### Token Optimization
- **5,103 lines → 2,961 lines (-42%)** across 33 agent/subagent/skill files
- Removed redundant persona lines, service catalogs, ASCII diagrams, tutorial-style examples
- Condensed code examples from 50-line tutorials to 10-line pattern gists
- Preserved all functional elements: permissions, tools, workflows, delegation rules, safety protocols

### Migration Required
See [MIGRATION.md](docs/MIGRATION.md) for upgrade steps.
