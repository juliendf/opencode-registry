"""
Integration tests for model tier feature end-to-end.

Tests the full pipeline: config → template resolution → copy → installed file.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner

from opencode_config.config import Config, DEFAULT_CONFIG
from opencode_config.utils.copy import CopyManager
from opencode_config.utils.template import TemplateEngine
from opencode_config.commands.models import models


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


@pytest.fixture
def config_file(temp_dir):
    return temp_dir / ".opencode-registry" / "config.json"


@pytest.fixture
def real_config(config_file):
    """Real Config instance with isolated temp config file."""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    return Config(config_file=config_file)


@pytest.fixture
def registry(temp_dir):
    """Minimal registry structure."""
    reg = temp_dir / "registry"
    (reg / "opencode" / "agents" / "subagents").mkdir(parents=True)
    (reg / "opencode" / "skills").mkdir(parents=True)
    (reg / "opencode" / "commands").mkdir(parents=True)
    (reg / "bundles").mkdir(parents=True)
    return reg


@pytest.fixture
def target_dir(temp_dir):
    t = temp_dir / ".config" / "opencode"
    t.mkdir(parents=True)
    return t


# ---------------------------------------------------------------------------
# Config + TemplateEngine integration
# ---------------------------------------------------------------------------

class TestConfigModelTierIntegration:
    def test_default_tiers_are_set(self, real_config):
        tiers = real_config.list_model_tiers()
        assert "high" in tiers
        assert "medium" in tiers
        assert "low" in tiers

    def test_set_and_retrieve_tier(self, real_config):
        real_config.set_model_tier("high", "my-provider/my-model")
        assert real_config.get_model_for_tier("high") == "my-provider/my-model"

    def test_config_persists_to_disk(self, config_file, real_config):
        real_config.set_model_tier("medium", "persisted/model")
        # Reload from disk
        reloaded = Config(config_file=config_file)
        assert reloaded.get_model_for_tier("medium") == "persisted/model"

    def test_unknown_tier_returns_none(self, real_config):
        assert real_config.get_model_for_tier("ultra") is None

    def test_all_three_tiers_resolve(self, real_config):
        # Tiers start unconfigured; set all three before asserting
        real_config.set_model_tier("high", "github-copilot/claude-sonnet-4.5")
        real_config.set_model_tier("medium", "github-copilot/claude-4.0")
        real_config.set_model_tier("low", "github-copilot/claude-haiku-4.5")
        for tier in ["high", "medium", "low"]:
            model = real_config.get_model_for_tier(tier)
            assert model is not None
            assert len(model) > 0


class TestTemplateEngineWithRealConfig:
    def test_tier_resolves_to_configured_model(self, real_config):
        engine = TemplateEngine(real_config)
        expected_high = real_config.get_model_for_tier("high")
        assert engine.resolve_model("high") == expected_high

    def test_custom_tier_model_reflected_in_engine(self, real_config):
        real_config.set_model_tier("low", "custom/cheapest-model")
        engine = TemplateEngine(real_config)
        assert engine.resolve_model("low") == "custom/cheapest-model"

    def test_process_content_replaces_tier_template(self, real_config):
        engine = TemplateEngine(real_config)
        content = "model: {{tier:medium}}"
        result = engine.process_content(content)
        expected = real_config.get_model_for_tier("medium")
        assert f"model: {expected}" in result


# ---------------------------------------------------------------------------
# Full pipeline: config → copy → installed file
# ---------------------------------------------------------------------------

class TestFullInstallPipeline:
    def _make_component(self, registry, name, tier):
        f = registry / "opencode" / "agents" / f"{name}.md"
        f.write_text(
            f"---\n"
            f"name: {name.title()}\n"
            f"description: Test component\n"
            f"type: agent\n"
            f"model_tier: {tier}\n"
            f"---\n\n"
            f"# {name.title()}\n"
        )
        return f

    def test_high_tier_resolved_in_installed_file(self, real_config, registry, target_dir):
        real_config.set_model_tier("high", "provider/high-model")
        self._make_component(registry, "architect", "high")

        cm = CopyManager(registry, target_dir, real_config)
        cm.install_package("opencode")

        installed = (target_dir / "agents" / "architect.md").read_text()
        assert "model: provider/high-model" in installed
        assert "model_tier" not in installed

    def test_low_tier_resolved_in_installed_file(self, real_config, registry, target_dir):
        real_config.set_model_tier("low", "provider/cheap-model")
        self._make_component(registry, "doc-writer", "low")

        cm = CopyManager(registry, target_dir, real_config)
        cm.install_package("opencode")

        installed = (target_dir / "agents" / "doc-writer.md").read_text()
        assert "model: provider/cheap-model" in installed

    def test_reinstall_after_tier_change_updates_model(self, real_config, registry, target_dir):
        """Re-running install after changing tier config should update the installed file."""
        real_config.set_model_tier("medium", "provider/old-model")
        self._make_component(registry, "coder", "medium")

        cm = CopyManager(registry, target_dir, real_config)
        cm.install_package("opencode")
        first_install = (target_dir / "agents" / "coder.md").read_text()
        assert "model: provider/old-model" in first_install

        # Change tier model and reinstall
        real_config.set_model_tier("medium", "provider/new-model")
        cm2 = CopyManager(registry, target_dir, real_config)
        cm2.install_package("opencode")
        second_install = (target_dir / "agents" / "coder.md").read_text()
        assert "model: provider/new-model" in second_install

    def test_model_override_takes_precedence_over_tier(self, real_config, registry, target_dir):
        real_config.set_model_tier("high", "provider/high-model")
        self._make_component(registry, "overridden", "high")

        cm = CopyManager(registry, target_dir, real_config)
        cm.install_package("opencode", model_override="provider/override-model")

        installed = (target_dir / "agents" / "overridden.md").read_text()
        assert "model: provider/override-model" in installed

    def test_multiple_components_different_tiers(self, real_config, registry, target_dir):
        real_config.set_model_tier("high", "provider/high-model")
        real_config.set_model_tier("medium", "provider/medium-model")
        real_config.set_model_tier("low", "provider/low-model")

        self._make_component(registry, "architect", "high")
        self._make_component(registry, "coder", "medium")
        self._make_component(registry, "documenter", "low")

        cm = CopyManager(registry, target_dir, real_config)
        cm.install_package("opencode")

        assert "model: provider/high-model" in (target_dir / "agents" / "architect.md").read_text()
        assert "model: provider/medium-model" in (target_dir / "agents" / "coder.md").read_text()
        assert "model: provider/low-model" in (target_dir / "agents" / "documenter.md").read_text()


# ---------------------------------------------------------------------------
# CLI `models` command integration
# ---------------------------------------------------------------------------

class TestModelsCommandIntegration:
    def _invoke(self, args, config_file):
        """Invoke models command with isolated config."""
        runner = CliRunner()
        # Patch Config to use our temp file
        from unittest.mock import patch
        with patch("opencode_config.commands.models.Config") as MockConfig:
            cfg = Config(config_file=config_file)
            MockConfig.return_value = cfg
            result = runner.invoke(models, args, catch_exceptions=False)
        return result, cfg

    def test_list_shows_all_tiers(self, config_file):
        config_file.parent.mkdir(parents=True, exist_ok=True)
        result, _ = self._invoke(["--list"], config_file)
        assert result.exit_code == 0
        assert "high" in result.output
        assert "medium" in result.output
        assert "low" in result.output

    def test_set_tier_updates_config(self, config_file):
        config_file.parent.mkdir(parents=True, exist_ok=True)
        result, cfg = self._invoke(["--set", "high", "new-provider/big-model"], config_file)
        assert result.exit_code == 0
        assert cfg.get_model_for_tier("high") == "new-provider/big-model"

    def test_set_invalid_tier_shows_error(self, config_file):
        config_file.parent.mkdir(parents=True, exist_ok=True)
        result, _ = self._invoke(["--set", "ultra", "some/model"], config_file)
        assert result.exit_code == 0
        assert "Error" in result.output or "Invalid" in result.output

    def test_no_args_shows_help_hint(self, config_file):
        config_file.parent.mkdir(parents=True, exist_ok=True)
        result, _ = self._invoke([], config_file)
        assert result.exit_code == 0
        assert "--list" in result.output or "No action" in result.output
