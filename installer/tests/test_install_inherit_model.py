"""Tests for per-invocation model inheritance during install and update."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from opencode_config.config import Config
from opencode_config.utils.installed_db import InstalledDB
from opencode_config.utils.manifest import ManifestParser


def _create_registry(root: Path) -> tuple[Path, dict[str, str]]:
    registry = root / "registry"
    agents = registry / "opencode" / "agents"
    subagents = agents / "subagents"
    commands = registry / "opencode" / "commands"
    skills = registry / "opencode" / "skills" / "test-skill"
    for directory in (subagents, commands, skills):
        directory.mkdir(parents=True, exist_ok=True)

    agent_text = (
        "---\nname: Primary\ndescription: Primary agent\ntype: agent\n"
        'model_tier: high\nmodel: "vendor/source-model"\nvariant: source-variant\n'
        'metadata:\n  model: "vendor/nested-model"\n'
        "---\n\n# Primary body\nKeep this prompt unchanged.\n"
    )
    subagent_text = (
        "---\nname: Specialist\ndescription: Specialist\ntype: subagent\n"
        "model_tier: medium\nmodel:\n  providerID: vendor\n"
        "  model: source-model\n  variant: source-variant\n"
        "---\n\n# Specialist body\nKeep this prompt unchanged.\n"
    )
    command_text = (
        "---\nname: Test Command\ndescription: Test command\ntype: command\n"
        'model_tier: low\nmodel: "vendor/source-model"\nvariant: source-variant\n'
        "---\n\n# Command body\nKeep this template unchanged.\n"
    )
    skill_text = (
        '---\nname: test-skill\ndescription: Test skill\nmodel: "vendor/skill-model"\n'
        "---\n\n# Skill body\nThis entrypoint must remain byte-for-byte unchanged.\n"
    )
    source_files = {
        "agents/primary.md": agent_text,
        "agents/subagents/specialist.md": subagent_text,
        "commands/test-command.md": command_text,
        "skills/test-skill/SKILL.md": skill_text,
    }
    for relative_path, content in source_files.items():
        path = registry / "opencode" / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return registry, source_files


def _configure_cli(
    root: Path,
    registry: Path,
    target: Path,
    monkeypatch: pytest.MonkeyPatch,
    model_tiers: dict[str, str | None],
) -> Path:
    from opencode_config.commands import install as install_command

    config_file = root / "registry-config.json"
    config_file.write_text(
        json.dumps(
            {
                "registry_path": str(registry),
                "target": str(target),
                "model_tiers": model_tiers,
            }
        ),
        encoding="utf-8",
    )
    database_file = root / "installed.json"
    monkeypatch.setattr(install_command, "Config", lambda: Config(config_file))
    monkeypatch.setattr(install_command, "InstalledDB", lambda: InstalledDB(database_file))
    return database_file


def test_install_inherit_model_strips_selectors_and_preserves_bodies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, source_files = _create_registry(tmp_path)
    target = tmp_path / "target"
    tiers = {
        "high": "provider/high-model",
        "medium": "provider/medium-model",
        "low": "provider/low-model",
        "free": "provider/free-model",
    }
    _configure_cli(tmp_path, registry, target, monkeypatch, tiers)

    from opencode_config.commands import install as install_command

    result = CliRunner().invoke(
        install_command.install,
        ["primary", "--target", str(target), "--inherit-model"],
    )

    assert result.exit_code == 0, result.output
    for relative_path in (
        "agents/primary.md",
        "agents/subagents/specialist.md",
        "commands/test-command.md",
    ):
        installed = target / relative_path
        frontmatter = ManifestParser.parse_frontmatter(installed)
        assert frontmatter is not None
        assert not {"model", "model_tier", "variant"} & frontmatter.keys()
        if relative_path == "agents/primary.md":
            assert frontmatter["metadata"]["model"] == "vendor/nested-model"
        source_body = source_files[relative_path].split("---", 2)[2]
        installed_body = installed.read_text(encoding="utf-8").split("---", 2)[2]
        assert installed_body == source_body

    skill_path = target / "skills/test-skill/SKILL.md"
    assert skill_path.read_text(encoding="utf-8") == source_files["skills/test-skill/SKILL.md"]


def test_install_inherit_model_does_not_require_configured_tiers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, _ = _create_registry(tmp_path)
    target = tmp_path / "target"
    _configure_cli(
        tmp_path,
        registry,
        target,
        monkeypatch,
        {"high": None, "medium": None, "low": None, "free": None},
    )

    from opencode_config.commands import install as install_command

    monkeypatch.setattr(
        install_command,
        "run_wizard",
        lambda _config: pytest.fail("inherit mode must skip the tier wizard"),
    )
    result = CliRunner().invoke(
        install_command.install,
        ["primary", "--target", str(target), "--inherit-model"],
    )

    assert result.exit_code == 0, result.output


def test_install_rejects_model_with_inherit_model_before_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, _ = _create_registry(tmp_path)
    target = tmp_path / "target"
    database_file = _configure_cli(
        tmp_path,
        registry,
        target,
        monkeypatch,
        {"high": None, "medium": None, "low": None, "free": None},
    )

    from opencode_config.commands import install as install_command

    result = CliRunner().invoke(
        install_command.install,
        [
            "primary",
            "--target",
            str(target),
            "--model",
            "provider/override",
            "--inherit-model",
        ],
    )

    assert result.exit_code == 2
    assert "cannot be used with --inherit-model" in result.output
    assert not target.exists()
    assert not database_file.exists()


def test_update_inherit_model_restores_missing_component_without_selectors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, _ = _create_registry(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    config_file = tmp_path / "registry-config.json"
    config_file.write_text(
        json.dumps(
            {
                "registry_path": str(registry),
                "target": str(target),
                "model_tiers": {
                    "high": "provider/high-model",
                    "medium": "provider/medium-model",
                    "low": "provider/low-model",
                    "free": "provider/free-model",
                },
            }
        ),
        encoding="utf-8",
    )
    database_file = tmp_path / "installed.json"

    from opencode_config.commands import update as update_command

    monkeypatch.setattr(update_command, "Config", lambda: Config(config_file))
    monkeypatch.setattr(update_command, "InstalledDB", lambda: InstalledDB(database_file))
    InstalledDB(database_file).add_component(
        "agent", "primary", {"version": "N/A", "name": "Primary"}
    )

    runner = CliRunner()
    help_result = runner.invoke(update_command.update, ["--help"])
    assert "--inherit-model" in help_result.output

    result = runner.invoke(update_command.update, ["--all", "--inherit-model"])

    assert result.exit_code == 0, result.output
    for relative_path in (
        "agents/primary.md",
        "agents/subagents/specialist.md",
        "commands/test-command.md",
    ):
        frontmatter = ManifestParser.parse_frontmatter(target / relative_path)
        assert frontmatter is not None
        assert not {"model", "model_tier", "variant"} & frontmatter.keys()


def test_update_detects_changed_versionless_source_and_preserves_custom_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = tmp_path / "registry"
    agent_source = registry / "opencode/agents/primary.md"
    agent_source.parent.mkdir(parents=True)
    original = (
        "---\nname: Primary\ndescription: Primary agent\ntype: agent\n---\n" "# Original revision\n"
    )
    agent_source.write_text(original, encoding="utf-8")
    target = tmp_path / "target"
    tiers = {
        "high": "provider/high-model",
        "medium": "provider/medium-model",
        "low": "provider/low-model",
        "free": "provider/free-model",
    }
    database_file = _configure_cli(tmp_path, registry, target, monkeypatch, tiers)

    from opencode_config.commands import install as install_command

    install_result = CliRunner().invoke(
        install_command.install,
        ["primary", "--target", str(target)],
    )
    assert install_result.exit_code == 0, install_result.output

    custom_file = target / "agents/custom-agent.md"
    custom_content = "---\nname: Custom\n---\nKeep my custom agent.\n"
    custom_file.write_text(custom_content, encoding="utf-8")
    revised = original.replace("Original revision", "Revised revision")
    agent_source.write_text(revised, encoding="utf-8")

    from opencode_config.commands import update as update_command

    monkeypatch.setattr(update_command, "Config", lambda: Config(tmp_path / "registry-config.json"))
    monkeypatch.setattr(update_command, "InstalledDB", lambda: InstalledDB(database_file))
    update_result = CliRunner().invoke(update_command.update, ["--all"])

    assert update_result.exit_code == 0, update_result.output
    assert "updated 1" in update_result.output
    assert (target / "agents/primary.md").read_text(encoding="utf-8") == revised
    assert custom_file.read_text(encoding="utf-8") == custom_content
    installed_record = InstalledDB(database_file).get_component("agent", "primary")
    assert installed_record is not None
    assert installed_record.get("sourceFingerprint")
