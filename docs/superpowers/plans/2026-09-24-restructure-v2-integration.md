# Restructure + OpenCode V2 Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply V2 behavior to restructured registry layout, install all agents and commands without pinned model selectors, and retire old migration worktree after verified cutover.

**Architecture:** Treat existing dirty `feat/restructure-subagents-skills` tree as source of truth. Knowledge loads through V2 skills; retained execution agents run through V2 subagent calls. Port V2 event tests and tierless installer mode, then replace only registry-managed global components from the old catalog with the restructured catalog.

**Tech Stack:** Python 3.8+, Click, pytest, YAML frontmatter, OpenCode V2 CLI.

**Spec:** `docs/superpowers/specs/2026-09-24-restructure-v2-integration-design.md`

## Global Constraints

- Keep exact restructured component layout and counts: five primary agents, ten flat subagents, 40+ skills, and three commands.
- Use canonical filename `penetration-tester.md` and V2 ID `subagents/penetration-tester`; fix typo references to `pentetration-tester`.
- Preserve all existing uncommitted restructure changes; do not reset, clean, or commit them.
- Keep tier installation as default; `--inherit-model` omits model selectors only when explicitly supplied.
- Use `--inherit-model` for both installation and update; flags are per invocation and not persisted.
- Preserve untracked `.openpackage` data by moving it to approved sibling backup before removing migration worktree.
- Preserve unrelated OpenCode global files, custom components, and authentication/configuration.
- Do not remove `openpackage` or `productManagement` worktrees or commit/push branches.

## Review Focus

- V2 skill calls and subagent calls are distinct tools; domain knowledge must load a skill, not invoke nonexistent specialist agents.
- Flat subagent filenames use V2 path-derived IDs prefixed by `subagents/`; preserve that prefix exactly.
- Skill support files must install unchanged; inherit mode strips selectors only from agent/command frontmatter.
- Global cleanup must remove only paths from old registry source; never delete whole OpenCode directories.
- Migration worktree removal must happen only after all intended code/tests are in restructure, `.openpackage` is backed up, and global smoke passes.

---

### Task 1: Prepare and baseline restructure workspace

**Files:**
- No repository files changed.

**Interfaces:**
- Produces: isolated Python test environment and baseline result for current dirty restructure state.

- [ ] **Step 1: Create local virtual environment and install dev extras**

Run from `restructure/`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e "installer[dev]"
```

Expected: editable installer package and pytest installed in ignored `.venv`.

- [ ] **Step 2: Run baseline suite before integration edits**

```bash
.venv/bin/python -m pytest installer/tests -q
```

Expected: record pass/fail count. If current restructure state fails, record exact failures and stop for review before adding migration changes.

- [ ] **Step 3: Record source inventory**

```bash
find opencode/agents -maxdepth 2 -type f -name '*.md' | sort
find opencode/skills -mindepth 2 -maxdepth 2 -name SKILL.md | sort
```

Expected: primary agents include `build.md`, `plan.md`, `ask-me-anything.md`, `debug.md`, `review.md`; files under `agents/subagents/` use V2 IDs `subagents/infrastructure-engineer`, `subagents/data-engineer`, `subagents/ml-engineer`, `subagents/mlops-engineer`, `subagents/ai-engineer`, `subagents/penetration-tester`, `subagents/security-auditor`, `subagents/mobile-developer`, `subagents/cli-developer`, and `subagents/fullstack-developer`.

---

### Task 2: Make agent prompts V2-first for skill and subagent tools

**Files:**
- Modify: `opencode/agents/_shared/delegation-rules.md`
- Modify: `opencode/agents/build.md`
- Modify: `opencode/agents/plan.md`
- Modify: `opencode/agents/ask-me-anything.md`
- Modify: `opencode/agents/debug.md`
- Modify: `opencode/agents/review.md`

**Interfaces:**
- Consumes: restructure skill IDs and flat subagent IDs from Task 1.
- Produces: prompts that load expertise with V2 `skill` tool and use V2 `subagent` tool only for retained child agents.

- [ ] **Step 1: Find stale V1 tool syntax and obsolete specialist IDs**

```bash
rg -n 'task\(|subagent_type|subagents/[0-9]{2}-|pentetration-tester' opencode/agents
```

Expected: results identify V1 call examples, obsolete nested IDs, and the misspelled penetration-tester reference.

- [ ] **Step 2: Rewrite routing guidance around knowledge skills and execution subagents**

Update `_shared/delegation-rules.md`: map domain expertise to actual skill IDs under `opencode/skills/`; use V2 `skill` calls for knowledge-only work; use V2 `subagent` calls with flat agent IDs for independent tool execution. Replace V1 `task(subagent_type=...)` examples with the observed V2 tool input shape. Do not classify every domain question as a subagent task.

- [ ] **Step 3: Update restructured primary-agent prompts and IDs**

Remove V1 `task()` calls from `build.md`, `plan.md`, `ask-me-anything.md`, `debug.md`, and `review.md`. Ensure examples use existing flat IDs, fix `pentetration-tester` to `penetration-tester`, and set `review.md` to `mode: all` so it remains primary-selectable and V2-subagent-capable.

- [ ] **Step 4: Check prompt IDs and tool names**

```bash
rg -n 'task\(|subagent_type|subagents/[0-9]{2}-|pentetration-tester' opencode/agents
```

Expected: no V1-only tool examples or obsolete nested IDs remain except explicit compatibility notes.

- [ ] **Step 5: Capture V2 skill and subagent events from a temporary install**

Stage restructured files into a temporary `.opencode` project without changing global config:

```python
import tempfile
from pathlib import Path

from opencode_config.config import Config
from opencode_config.utils.copy import CopyManager

scratch = Path(tempfile.mkdtemp(prefix="restructure-v2-smoke-"))
config_file = scratch / "registry-config.json"
config_file.write_text(
    '{"model_tiers":{"high":null,"medium":null,"low":null,"free":null}}'
)
config = Config(config_file=config_file)
target = scratch / ".opencode"
if not CopyManager(Path.cwd(), target, config).install_package("opencode"):
    raise RuntimeError("Failed to stage restructured components")
print(scratch)
```

From printed project directory, run:

```bash
opencode run --agent build --model opencode/mimo-v2.6-flash-free --format json "Do not edit files. Load python-pro skill for one typing recommendation, then use subagent ID subagents/infrastructure-engineer once for one read-only infrastructure recommendation. Summarize both."
```

Expected: output contains a V2 `skill` event with ID `python-pro` and a `subagent` event with agent ID `subagents/infrastructure-engineer`. Save minimal sanitized tool events as the two fixtures in Task 3; preserve V2 structure, IDs, and required input keys, replacing prompt/output/session-specific values with fixture strings. Skip live capture and report blocker if no model is available; do not invent event shape.

---

### Task 3: Update V2 delegation and skill event tests

**Files:**
- Modify: `test_delegation.py`
- Create: `installer/tests/test_restructure_v2_events.py`
- Create: `installer/tests/fixtures/v2_subagent_event.jsonl`
- Create: `installer/tests/fixtures/v2_skill_event.jsonl`

**Interfaces:**
- Produces: tested `parse_subagent_calls(raw_output: str) -> list[str]` and `parse_skill_calls(raw_output: str) -> list[str]` in the root harness.
- Consumes: real V2 event shapes captured from Task 2's temporary-project smoke.

- [ ] **Step 1: Write failing fixture parser tests**

```python
from pathlib import Path

import test_delegation as harness


def test_parse_v2_subagent_returns_flat_agent_id() -> None:
    raw = (Path(__file__).parent / "fixtures" / "v2_subagent_event.jsonl").read_text()
    assert harness.parse_subagent_calls(raw) == ["subagents/infrastructure-engineer"]


def test_parse_v2_skill_returns_skill_id() -> None:
    raw = (Path(__file__).parent / "fixtures" / "v2_skill_event.jsonl").read_text()
    assert harness.parse_skill_calls(raw) == ["python-pro"]
```

Run:

```bash
.venv/bin/python -m pytest installer/tests/test_restructure_v2_events.py -q
```

Expected: FAIL by assertion because current harness only extracts V1 `task` events and does not parse skill calls.

- [ ] **Step 2: Add V2 event parsing, preserving V1 task fallback where valid**

Parse line-delimited JSON safely. For V2, inspect `part.type == "tool"`, extract `state.input.agent` for `subagent`, and `state.input.id` for `skill`. Retain V1 `task` parsing only as compatibility fallback. Keep response text parser unchanged if V2 fixture confirms `type: text` plus `part.text` shape.

- [ ] **Step 3: Verify parser tests pass**

```bash
.venv/bin/python -m pytest installer/tests/test_restructure_v2_events.py -q
```

Expected: flat ID and skill ID fixtures both parse exactly.

- [ ] **Step 4: Update integration harness expectations to restructured catalog**

Replace deleted IDs such as `subagents/02-languages/python-pro` with retained flat execution IDs. Add an expected-skill assertion for the read-only Python expertise case; do not count skill events as subagent calls. Update verbose labels from `task` to `subagent`/`skill`.

- [ ] **Step 5: Run parser and harness listing checks**

```bash
.venv/bin/python -m pytest installer/tests/test_restructure_v2_events.py -q
.venv/bin/python test_delegation.py --list
```

Expected: parser tests pass and all listed agents match restructure inventory.

---

### Task 4: Port tierless model inheritance to restructured installer

**Files:**
- Modify: `installer/src/opencode_config/commands/install.py`
- Modify: `installer/src/opencode_config/commands/update.py`
- Modify: `installer/src/opencode_config/utils/copy.py`
- Modify: `installer/src/opencode_config/utils/installed_db.py`
- Create: `installer/tests/test_install_inherit_model.py`

**Interfaces:**
- Produces: `install --inherit-model`, `update --inherit-model`, `CopyManager.install_package(..., inherit_model: bool = False)`, and source fingerprints persisted for versionless update detection.
- Consumes: default optional-tier behavior already present in restructure; inheritance flag overrides configured tiers.

- [ ] **Step 1: Write failing install inheritance test**

Create a temp registry with primary agent, flat subagent, command, and `SKILL.md`. Give agents/commands `model_tier`, `model`, and `variant` fields; set all tiers to real test values. Invoke CLI install with `--inherit-model` and assert no selectors remain in installed agent/command frontmatter, prompt body and skill file remain unchanged, and no model tier value is required.

- [ ] **Step 2: Run failing install test**

```bash
.venv/bin/python -m pytest installer/tests/test_install_inherit_model.py -q
```

Expected: FAIL because `--inherit-model` is not recognized.

- [ ] **Step 3: Implement install and copy behavior**

Add mutually exclusive `--inherit-model` and `--model` options. Skip model wizard/check in inheritance mode. Have `CopyManager` remove top-level `model`, `model_tier`, and `variant` only from agent/command frontmatter; preserve body, skills, and default tier resolution. Reject both flags together before filesystem/database writes.

- [ ] **Step 4: Verify install test passes**

```bash
.venv/bin/python -m pytest installer/tests/test_install_inherit_model.py -q
```

Expected: no selectors in installed agents/commands, unchanged bodies/skills, successful install without tier setup.

- [ ] **Step 5: Test and implement update inheritance**

First add an update CLI test confirming `--inherit-model` appears in help and that a missing installed component is restored with no selectors. Run it to verify failure before adding the update flag. Then add the flag and pass it to `CopyManager.install_package` during update re-copy. Use source fingerprints to detect versionless source changes and model-tier resolution changes. Update re-copies the full registry package when any missing/source/version change is detected; the per-call inherit flag applies to every agent/command copied by that update. Reinstall with `install --group advanced --inherit-model` to force a full conversion when no update is pending.

- [ ] **Step 6: Run focused installer tests**

```bash
.venv/bin/python -m pytest installer/tests/test_install_inherit_model.py installer/tests/test_copy.py -q
```

Expected: inherit mode and existing tier mode both pass.

---

### Task 5: Refresh V2 docs while preserving restructure layout

**Files:**
- Modify: `README.md`
- Modify: `docs/GETTING-STARTED.md`
- Modify: `docs/FAQ.md`
- Modify: `docs/PERMISSIONS.md`
- Modify: `docs/MIGRATION.md`
- Modify: `AGENTS.md` only for obsolete model/subagent paths or CLI guidance.

**Interfaces:**
- Consumes: skill-first knowledge, V2 subagent calls, flat inventory, and `--inherit-model` behavior from Tasks 2–4.
- Produces: docs that describe V2 without reverting restructure component names/counts.

- [ ] **Step 1: Update V2 prerequisites and new usage**

Replace V1 docs links and `@mention`/`task()` guidance with V2 docs and skill/subagent usage. Preserve restructure agent/skill/command tree exactly. Document `--inherit-model` and per-invocation update flag.

- [ ] **Step 2: Rewrite permissions guide for V2**

Use ordered `permissions` arrays, V2 actions (`bash` → `shell`, `task` → `subagent`, `write`/`patch` → `edit`), global-before-agent append precedence, and last-match semantics. State that supported V1 frontmatter remains compatibility input.

- [ ] **Step 3: Search only user-facing docs and active prompts**

```bash
rg -n 'OpenCode 1\.2\.5|@mention|opencode\.ai/docs/|task\(' README.md docs/GETTING-STARTED.md docs/FAQ.md docs/PERMISSIONS.md docs/MIGRATION.md opencode/agents test_delegation.py
```

Expected: no V1-only syntax remains except an explicit compatibility note or Python decorator example.

---

### Task 6: Replace global catalog and retire migration worktree

**Files:**
- No source files except updates required by cutover test results.
- Preserve: `opencode-v2-migration/opencode/skills/.openpackage/` in sibling backup `/Users/julien/Documents/devops/perso/opencode-v2-migration-artifacts/opencode-skills-openpackage/`.

**Interfaces:**
- Consumes: passing restructure tests and restructured installer.
- Produces: global OpenCode V2 installation from restructure source with inherited session model; old migration worktree removed; other worktrees untouched.

- [ ] **Step 1: Run old V2 registry uninstaller dry-run**

From the old migration worktree, run:

```bash
.venv/bin/opencode-config uninstall --all --dry-run
```

Expected: only paths from old registry `opencode/` tree are listed; no whole-directory deletion.

- [ ] **Step 2: Remove old registry-managed files**

Run `.venv/bin/opencode-config uninstall --all` from old migration worktree and confirm its prompt. This removes only paths matched by old registry source and clears tracking DB; it must not run `rm -rf` on global OpenCode directories.

- [ ] **Step 3: Install restructure catalog with inheritance**

From restructure worktree, run:

```bash
.venv/bin/opencode-config install --group advanced --inherit-model
.venv/bin/opencode-config status
```

Expected: restructured agents, flat subagents, skills, and commands are detected; no tier wizard; model selectors absent from installed agent/command frontmatter.

- [ ] **Step 4: Smoke-test current V2 global install**

Run one read-only model call that asks `build` to load a domain skill and one retained execution subagent. Verify V2 JSON shows the skill and subagent tool events; no files are edited.

- [ ] **Step 5: Preserve package metadata, then remove old migration worktree**

Create sibling backup directory `/Users/julien/Documents/devops/perso/opencode-v2-migration-artifacts` and move `opencode/skills/.openpackage/` there. Confirm every V2 implementation/test/document change was ported to restructure and old worktree contains no unrecognized user files. Then remove only `/Users/julien/Documents/devops/perso/opencode-registry/opencode-v2-migration`; keep its branch ref unless user asks to delete it. Leave `openpackage` and `productManagement` worktrees untouched.

- [ ] **Step 6: Final suite and layout verification**

```bash
.venv/bin/python -m pytest installer/tests -q
git diff --check
git worktree list
```

Expected: full suite passes, integrated changes remain uncommitted, migration worktree absent, backup and other worktrees preserved.
