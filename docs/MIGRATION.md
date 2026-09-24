# Migrating to the Restructured Registry and OpenCode V2

OpenCode V2 continues to support supported V1 configuration and file-based definitions. This registry's current prompts target V2 tools and its catalog separates knowledge skills from independent execution subagents.

## Before switching registry catalogs

Preview uninstall from the registry catalog that installed the current files:

```bash
opencode-config uninstall --all --dry-run
```

Review every listed path. Then run `opencode-config uninstall --all` from that same registry if the preview contains only registry-managed files you intend to replace. The installer removes files represented by its registry source; it does not require deleting the entire OpenCode `agents/`, `skills/`, or `commands/` directories. Preserve custom components, configuration, credentials, and unrelated files.

Do not use blanket `rm -rf` commands against OpenCode directories. If the old registry source is no longer available, inspect and back up exact paths before manual cleanup.

## Install the restructured catalog

```bash
cd installer
python -m pip install -e .
cd ..

# Tier-based install remains the default
opencode-config install --group advanced

# Or explicitly make all installed agents and commands inherit the active session model
opencode-config install --group advanced --inherit-model
```

The `--inherit-model` flag is per invocation. It removes top-level `model`, `model_tier`, and `variant` from installed agent and command frontmatter, even when tier models are configured. It leaves source metadata, prompt bodies, and skill entrypoints unchanged. Update runs only when it detects missing components, changed source fingerprints, or version changes; when triggered, it recopies the full registry package, and the flag applies to all copied agent/command files. The choice is not saved as a persistent setting.

Without `--inherit-model`, configured model tiers are resolved as before. Unconfigured tiers remain optional and allow the component to inherit its caller's model.

## What changed in the registry

| Area | Current layout/use |
|---|---|
| Primary agents | Five: `ask-me-anything`, `plan`, `build`, `debug`, `review` |
| Execution subagents | Ten flat files under `opencode/agents/subagents/` |
| V2 subagent IDs | Include path prefix, such as `subagents/infrastructure-engineer` |
| Skills | 40+ knowledge workflows under `opencode/skills/<id>/SKILL.md` |
| Commands | Three custom commands under `opencode/commands/` |

Domain expertise such as Python, Kubernetes, or AWS patterns belongs in skills and loads through V2 `skill` with an exact skill ID. Use V2 `subagent` with an exact path-derived ID only when independent execution or context is useful. Review agent supports both primary and subagent modes.

## Verify

```bash
opencode --version
opencode-config status
```

In a project, ask `build` for a read-only recommendation that loads a skill and invokes one retained execution subagent. V2 JSON output should show separate `skill` and `subagent` tool events.

## OpenCode V2 references

- [Migration from V1](https://opencode.ai/v2/docs/migrate-v1)
- [Agents](https://opencode.ai/v2/docs/agents)
- [Skills](https://opencode.ai/v2/docs/skills)
- [Permissions](https://opencode.ai/v2/docs/permissions)
