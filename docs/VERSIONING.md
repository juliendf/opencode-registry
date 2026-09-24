# Component Version and Change Detection

The installer tracks installed components in `~/.config/opencode/opencode-registry-installed.json`. Registry updates use semantic versions where available and source fingerprints for versionless catalog files.

## Version metadata

- Agents, subagents, and commands do not require a `version:` frontmatter field; source version metadata remains optional and registry-specific.
- Skills may supply `metadata.version` in `SKILL.md`.
- The installer database records the version presented at install time and a source fingerprint covering component source files. For agents and commands, the fingerprint also includes the configured model-tier resolution.
- Skill fingerprints include supporting files such as references and scripts, not only `SKILL.md`.

Do not add a version field solely to make OpenCode accept an agent definition. V2 agent behavior is documented at [OpenCode V2 Agents](https://opencode.ai/v2/docs/agents).

## Preview detected updates

```bash
opencode-config update --all --dry-run
```

The installer detects:

1. Components recorded as installed but missing from the target directory.
2. Source-file or model-tier-resolution fingerprint changes.
3. Newer semantic versions when both installed and registry versions are available.

Versionless components therefore still update when their source content changes. New/legacy tracking records without fingerprints establish a baseline on their first update.

## Apply updates

```bash
opencode-config update --all
opencode-config update <component-id>
```

Current update implementation re-copies the complete registry `opencode/` package when it detects any missing or changed component, even when a single component ID was selected. Registry-managed files may be overwritten by that copy. Files absent from registry source—such as user-installed Cavecrew components—remain untouched. Back up local edits to registry-managed files before updating.

## Model tiers and inheritance

By default, install/update resolves configured model tiers. To strip top-level `model`, `model_tier`, and `variant` from copied agent and command frontmatter:

```bash
opencode-config install --group advanced --inherit-model
opencode-config update --all --inherit-model
```

Flags apply only to that invocation. Update only runs when it finds a change; if it runs, the entire package is copied and inheritance applies to all copied agents/commands. To force a full conversion when no update is pending, reinstall the desired bundle with `install --inherit-model`. Skill entrypoints and prompt bodies remain unchanged.

## Verify state

```bash
opencode-config status
opencode-config list --installed
```

If database state and installed files disagree, preview `opencode-config sync --dry-run` before running `opencode-config sync`.
