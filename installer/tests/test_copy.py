"""
Tests for copy.py - CopyManager file installation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from opencode_config.utils.copy import CopyManager
from opencode_config.config import Config


@pytest.fixture
def temp_dir():
    """Temporary directory for each test."""
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


@pytest.fixture
def mock_config(temp_dir):
    """Config instance pointing to temp dirs."""
    config = MagicMock(spec=Config)
    config.model_tiers = {
        "high": "github-copilot/claude-sonnet-4.5",
        "medium": "github-copilot/claude-sonnet-4",
        "low": "github-copilot/claude-haiku-4.5",
        "free": "github-copilot/gpt-4o-mini",
    }
    config.get_model_for_tier.side_effect = lambda tier: {
        "high": "github-copilot/claude-sonnet-4.5",
        "medium": "github-copilot/claude-sonnet-4",
        "low": "github-copilot/claude-haiku-4.5",
        "free": "github-copilot/gpt-4o-mini",
    }.get(tier)
    return config


@pytest.fixture
def registry(temp_dir):
    """Mock registry with opencode/ structure."""
    reg = temp_dir / "registry"
    (reg / "opencode" / "agents" / "subagents").mkdir(parents=True)
    (reg / "opencode" / "skills" / "my-skill").mkdir(parents=True)
    (reg / "opencode" / "commands").mkdir(parents=True)
    return reg


@pytest.fixture
def target_dir(temp_dir):
    """Target installation directory."""
    t = temp_dir / ".config" / "opencode"
    t.mkdir(parents=True)
    return t


@pytest.fixture
def copy_manager(registry, target_dir, mock_config):
    """Instantiated CopyManager for tests."""
    return CopyManager(registry, target_dir, mock_config)


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestCopyManagerInit:
    def test_init_sets_paths(self, registry, target_dir, mock_config):
        cm = CopyManager(registry, target_dir, mock_config)
        assert cm.registry_path == registry
        assert cm.target_dir == target_dir
        assert cm.config == mock_config

    def test_template_engine_created(self, copy_manager):
        assert copy_manager.template_engine is not None


# ---------------------------------------------------------------------------
# install_package
# ---------------------------------------------------------------------------

class TestInstallPackage:
    def test_install_missing_package_returns_false(self, copy_manager):
        result = copy_manager.install_package("nonexistent")
        assert result is False

    def test_install_creates_target_dirs(self, copy_manager, registry, target_dir):
        """Installing opencode/ should create agents/, skills/, commands/ in target."""
        # Add a dummy file so rglob finds something
        (registry / "opencode" / "agents" / "dummy.md").write_text(
            "---\nname: Dummy\ndescription: d\ntype: agent\n---\n# Dummy\n"
        )
        copy_manager.install_package("opencode")
        assert (target_dir / "agents").exists()
        assert (target_dir / "skills").exists()
        assert (target_dir / "commands").exists()

    def test_install_copies_plain_md_file(self, copy_manager, registry, target_dir):
        agent = registry / "opencode" / "agents" / "simple.md"
        agent.write_text(
            "---\nname: Simple\ndescription: s\ntype: agent\n---\n# Simple\n"
        )
        copy_manager.install_package("opencode")
        assert (target_dir / "agents" / "simple.md").exists()

    def test_install_resolves_model_tier(self, copy_manager, registry, target_dir):
        """model_tier in frontmatter should be replaced by model: <resolved>."""
        agent = registry / "opencode" / "agents" / "tiered.md"
        agent.write_text(
            "---\nname: Tiered\ndescription: t\ntype: agent\nmodel_tier: high\n---\n# Tiered\n"
        )
        copy_manager.install_package("opencode")
        installed_content = (target_dir / "agents" / "tiered.md").read_text()
        assert "model: github-copilot/claude-sonnet-4.5" in installed_content
        assert "model_tier" not in installed_content

    def test_install_applies_model_override(self, copy_manager, registry, target_dir):
        """--model flag overrides tier resolution in installed file."""
        agent = registry / "opencode" / "agents" / "overridden.md"
        agent.write_text(
            "---\nname: Overridden\ndescription: o\ntype: agent\nmodel_tier: high\n---\n# Overridden\n"
        )
        copy_manager.install_package("opencode", model_override="github-copilot/gpt-5")
        installed_content = (target_dir / "agents" / "overridden.md").read_text()
        assert "model: github-copilot/gpt-5" in installed_content
        assert "model_tier" not in installed_content

    def test_install_dry_run_does_not_create_files(self, copy_manager, registry, target_dir):
        agent = registry / "opencode" / "agents" / "dryrun.md"
        agent.write_text(
            "---\nname: DryRun\ndescription: d\ntype: agent\n---\n# DryRun\n"
        )
        copy_manager.install_package("opencode", dry_run=True)
        assert not (target_dir / "agents" / "dryrun.md").exists()

    def test_install_skips_hidden_files(self, copy_manager, registry, target_dir):
        (registry / "opencode" / "agents" / ".hidden.md").write_text("hidden")
        copy_manager.install_package("opencode")
        assert not (target_dir / "agents" / ".hidden.md").exists()

    def test_install_skips_pycache(self, copy_manager, registry, target_dir):
        pycache = registry / "opencode" / "__pycache__"
        pycache.mkdir()
        (pycache / "some.pyc").write_text("bytecode")
        copy_manager.install_package("opencode")
        assert not (target_dir / "__pycache__").exists()

    def test_install_returns_true_on_success(self, copy_manager, registry):
        agent = registry / "opencode" / "agents" / "ok.md"
        agent.write_text(
            "---\nname: Ok\ndescription: ok\ntype: agent\n---\n# Ok\n"
        )
        result = copy_manager.install_package("opencode")
        assert result is True


# ---------------------------------------------------------------------------
# uninstall_package
# ---------------------------------------------------------------------------

class TestUninstallPackage:
    def test_uninstall_removes_copied_file(self, copy_manager, registry, target_dir):
        agent = registry / "opencode" / "agents" / "removeme.md"
        agent.write_text(
            "---\nname: Remove\ndescription: r\ntype: agent\n---\n# Remove\n"
        )
        copy_manager.install_package("opencode")
        assert (target_dir / "agents" / "removeme.md").exists()

        copy_manager.uninstall_package("opencode")
        assert not (target_dir / "agents" / "removeme.md").exists()

    def test_uninstall_missing_package_returns_true(self, copy_manager):
        """Uninstalling a package that was never installed should succeed gracefully."""
        result = copy_manager.uninstall_package("nonexistent")
        assert result is True

    def test_uninstall_dry_run_leaves_files_intact(self, copy_manager, registry, target_dir):
        agent = registry / "opencode" / "agents" / "keepme.md"
        agent.write_text(
            "---\nname: Keep\ndescription: k\ntype: agent\n---\n# Keep\n"
        )
        copy_manager.install_package("opencode")
        copy_manager.uninstall_package("opencode", dry_run=True)
        assert (target_dir / "agents" / "keepme.md").exists()

    def test_uninstall_cleans_empty_dirs(self, copy_manager, registry, target_dir):
        """After uninstall, empty dirs should be removed."""
        agent = registry / "opencode" / "agents" / "cleanup.md"
        agent.write_text(
            "---\nname: Cleanup\ndescription: c\ntype: agent\n---\n# Cleanup\n"
        )
        copy_manager.install_package("opencode")
        copy_manager.uninstall_package("opencode")
        # agents/ dir should be gone since it's empty
        assert not (target_dir / "agents").exists()


# ---------------------------------------------------------------------------
# detect_installed_components
# ---------------------------------------------------------------------------

class TestDetectInstalledComponents:
    def test_empty_target_returns_empty_dict(self, copy_manager):
        result = copy_manager.detect_installed_components()
        assert result == {"agents": [], "subagents": [], "skills": [], "commands": []}

    def test_detects_primary_agents(self, copy_manager, target_dir):
        agents_dir = target_dir / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "my-agent.md").write_text("# My Agent\n")
        (agents_dir / "another.md").write_text("# Another\n")

        result = copy_manager.detect_installed_components()
        assert "my-agent" in result["agents"]
        assert "another" in result["agents"]

    def test_skips_shared_dir(self, copy_manager, target_dir):
        agents_dir = target_dir / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "_shared").mkdir()
        (agents_dir / "_shared" / "something.md").write_text("shared")

        result = copy_manager.detect_installed_components()
        assert "_shared" not in result["agents"]

    def test_detects_subagents(self, copy_manager, target_dir):
        subagents_dir = target_dir / "agents" / "subagents" / "01-core"
        subagents_dir.mkdir(parents=True)
        (subagents_dir / "backend-architect.md").write_text("# Backend\n")

        result = copy_manager.detect_installed_components()
        assert "backend-architect" in result["subagents"]

    def test_detects_skills(self, copy_manager, target_dir):
        skill_dir = target_dir / "skills" / "mcp-builder"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# MCP Builder\n")

        result = copy_manager.detect_installed_components()
        assert "mcp-builder" in result["skills"]

    def test_skill_without_skill_md_not_detected(self, copy_manager, target_dir):
        skill_dir = target_dir / "skills" / "incomplete-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "README.md").write_text("# Incomplete\n")

        result = copy_manager.detect_installed_components()
        assert "incomplete-skill" not in result["skills"]

    def test_detects_commands(self, copy_manager, target_dir):
        commands_dir = target_dir / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "deploy.md").write_text("# Deploy\n")

        result = copy_manager.detect_installed_components()
        assert "deploy" in result["commands"]


# ---------------------------------------------------------------------------
# _copy_and_process_file (via install_package)
# ---------------------------------------------------------------------------

class TestCopyAndProcessFile:
    def test_medium_tier_resolved(self, copy_manager, registry, target_dir):
        agent = registry / "opencode" / "agents" / "medium.md"
        agent.write_text(
            "---\nname: Medium\ndescription: m\ntype: agent\nmodel_tier: medium\n---\n# Medium\n"
        )
        copy_manager.install_package("opencode")
        content = (target_dir / "agents" / "medium.md").read_text()
        assert "model: github-copilot/claude-sonnet-4" in content
        assert "model_tier" not in content

    def test_low_tier_resolved(self, copy_manager, registry, target_dir):
        agent = registry / "opencode" / "agents" / "low.md"
        agent.write_text(
            "---\nname: Low\ndescription: l\ntype: agent\nmodel_tier: low\n---\n# Low\n"
        )
        copy_manager.install_package("opencode")
        content = (target_dir / "agents" / "low.md").read_text()
        assert "model: github-copilot/claude-haiku-4.5" in content

    def test_free_tier_resolved(self, copy_manager, registry, target_dir):
        agent = registry / "opencode" / "agents" / "free.md"
        agent.write_text(
            "---\nname: Free\ndescription: f\ntype: agent\nmodel_tier: free\n---\n# Free\n"
        )
        copy_manager.install_package("opencode")
        content = (target_dir / "agents" / "free.md").read_text()
        assert "model: github-copilot/gpt-4o-mini" in content
        assert "model_tier" not in content

    def test_model_tier_replaced_unconditionally(self, copy_manager, registry, target_dir):
        """model_tier: is always replaced with model: regardless of other fields."""
        agent = registry / "opencode" / "agents" / "tiered-only.md"
        agent.write_text(
            "---\nname: Tiered\ndescription: t\ntype: agent\nmodel_tier: low\n---\n# Tiered\n"
        )
        copy_manager.install_package("opencode")
        content = (target_dir / "agents" / "tiered-only.md").read_text()
        # Installed file should have model: not model_tier:
        assert "model: github-copilot/claude-haiku-4.5" in content
        assert "model_tier" not in content

    def test_non_md_file_copied_without_processing(self, copy_manager, registry, target_dir):
        """Non-markdown files should be copied as-is."""
        binary_like = registry / "opencode" / "agents" / "config.json"
        binary_like.write_text('{"key": "value"}')
        copy_manager.install_package("opencode")
        result = target_dir / "agents" / "config.json"
        assert result.exists()
        assert result.read_text() == '{"key": "value"}'
