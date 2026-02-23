"""
Tests for template engine functionality.
"""

import pytest
from pathlib import Path
from opencode_config.config import Config
from opencode_config.utils.template import TemplateEngine


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary config for testing."""
    config_file = tmp_path / "config.json"
    config = Config(config_file)
    config.set_model_tier("high", "test-model-high")
    config.set_model_tier("medium", "test-model-medium")
    config.set_model_tier("low", "test-model-low")
    return config


def test_template_engine_init(temp_config):
    """Test template engine initialization."""
    engine = TemplateEngine(temp_config)
    assert engine.config == temp_config


def test_process_content_tier_replacement(temp_config):
    """Test {{tier:X}} replacement."""
    engine = TemplateEngine(temp_config)
    
    content = "model: {{tier:high}}"
    result = engine.process_content(content)
    assert result == "model: test-model-high"
    
    content = "model: {{tier:medium}}"
    result = engine.process_content(content)
    assert result == "model: test-model-medium"
    
    content = "model: {{tier:low}}"
    result = engine.process_content(content)
    assert result == "model: test-model-low"


def test_process_content_model_replacement(temp_config):
    """Test {{model:X}} literal replacement."""
    engine = TemplateEngine(temp_config)
    
    content = "model: {{model:custom-model}}"
    result = engine.process_content(content)
    assert result == "model: custom-model"


def test_process_content_no_templates(temp_config):
    """Test content without templates passes through."""
    engine = TemplateEngine(temp_config)
    
    content = "model: literal-model"
    result = engine.process_content(content)
    assert result == "model: literal-model"


def test_process_content_with_overrides(temp_config):
    """Test override functionality."""
    engine = TemplateEngine(temp_config)
    
    content = "model: {{tier:high}}"
    overrides = {"high": "override-model"}
    result = engine.process_content(content, overrides)
    assert result == "model: override-model"


def test_process_content_invalid_tier_fallback(temp_config):
    """Test fallback to medium for invalid tier."""
    engine = TemplateEngine(temp_config)
    
    content = "model: {{tier:invalid}}"
    result = engine.process_content(content)
    assert result == "model: test-model-medium"


def test_process_content_invalid_tier_no_fallback():
    """Test error when no fallback available."""
    config_file = Path("/tmp/test_config_empty.json")
    config = Config(config_file)
    config.data["model_tiers"] = {}  # Empty tiers
    
    engine = TemplateEngine(config)
    content = "model: {{tier:invalid}}"
    
    with pytest.raises(ValueError, match="Invalid tier"):
        engine.process_content(content)


def test_extract_tier_from_frontmatter(temp_config):
    """Test extracting tier from frontmatter."""
    engine = TemplateEngine(temp_config)
    
    frontmatter = {"model_tier": "high"}
    tier = engine.extract_tier_from_frontmatter(frontmatter)
    assert tier == "high"
    
    frontmatter = {}
    tier = engine.extract_tier_from_frontmatter(frontmatter)
    assert tier is None


def test_extract_model_from_frontmatter(temp_config):
    """Test extracting model from frontmatter."""
    engine = TemplateEngine(temp_config)
    
    frontmatter = {"model": "custom-model"}
    model = engine.extract_model_from_frontmatter(frontmatter)
    assert model == "custom-model"
    
    frontmatter = {}
    model = engine.extract_model_from_frontmatter(frontmatter)
    assert model is None


def test_resolve_model_tier_reference(temp_config):
    """Test resolving tier references."""
    engine = TemplateEngine(temp_config)
    
    assert engine.resolve_model("high") == "test-model-high"
    assert engine.resolve_model("medium") == "test-model-medium"
    assert engine.resolve_model("low") == "test-model-low"


def test_resolve_model_literal(temp_config):
    """Test resolving literal model strings."""
    engine = TemplateEngine(temp_config)
    
    assert engine.resolve_model("custom/model") == "custom/model"
    assert engine.resolve_model("provider/model-name") == "provider/model-name"


def test_resolve_model_none_uses_default(temp_config):
    """Test None value uses default tier."""
    engine = TemplateEngine(temp_config)
    
    result = engine.resolve_model(None)
    assert result == "test-model-medium"


def test_resolve_model_custom_default(temp_config):
    """Test custom default tier."""
    engine = TemplateEngine(temp_config)
    
    result = engine.resolve_model(None, default_tier="low")
    assert result == "test-model-low"


def test_should_process_file(temp_config):
    """Test file processing determination."""
    engine = TemplateEngine(temp_config)
    
    assert engine.should_process_file("agent.md") is True
    assert engine.should_process_file("skill/SKILL.md") is True
    assert engine.should_process_file("command.md") is True
    assert engine.should_process_file("readme.txt") is False
    assert engine.should_process_file("image.png") is False


def test_multiple_replacements(temp_config):
    """Test multiple template replacements in same content."""
    engine = TemplateEngine(temp_config)
    
    content = """
    agent1: {{tier:high}}
    agent2: {{tier:medium}}
    agent3: {{model:literal-model}}
    """
    
    result = engine.process_content(content)
    assert "test-model-high" in result
    assert "test-model-medium" in result
    assert "literal-model" in result
