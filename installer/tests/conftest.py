"""
Pytest configuration and shared fixtures.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def mock_registry(temp_dir):
    """Create a mock OpenCode registry structure."""
    registry = temp_dir / "registry"
    registry.mkdir()

    # Create directory structure
    (registry / "opencode").mkdir()
    (registry / "opencode" / "agents").mkdir()
    (registry / "opencode" / "agents" / "subagents").mkdir()
    (registry / "opencode" / "skills").mkdir()
    (registry / "opencode" / "commands").mkdir()
    (registry / "bundles").mkdir()

    return registry


@pytest.fixture
def mock_agent_md(mock_registry):
    """Create a mock agent markdown file with frontmatter."""
    agent_file = mock_registry / "opencode" / "agents" / "test-agent.md"
    agent_file.write_text(
        """---
name: "Test Agent"
description: "A test agent for unit testing"
type: "agent"
version: "1.2.3"
author: "Test Author"
tags: ["test", "mock"]
---

# Test Agent

This is a test agent.
"""
    )
    return agent_file


@pytest.fixture
def mock_skill_md(mock_registry):
    """Create a mock skill markdown file with frontmatter."""
    skill_dir = mock_registry / "opencode" / "skills" / "test-skill"
    skill_dir.mkdir()

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        """---
name: "Test Skill"
description: "A test skill for unit testing"
type: "skill"
license: "MIT"
compatibility: "all"
metadata:
  version: "2.0.0"
  category: "testing"
---

# Test Skill

This is a test skill.
"""
    )
    return skill_file


@pytest.fixture
def mock_command_md(mock_registry):
    """Create a mock command markdown file with frontmatter."""
    command_file = mock_registry / "opencode" / "commands" / "test-command.md"
    command_file.write_text(
        """---
name: "Test Command"
description: "A test command for unit testing"
type: "command"
version: "1.0.0"
agent: "test-agent"
---

# Test Command

This is a test command.
"""
    )
    return command_file


@pytest.fixture
def mock_config_dir(temp_dir):
    """Create a mock config directory."""
    config_dir = temp_dir / ".opencode-registry"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_target_dir(temp_dir):
    """Create a mock target directory for installations."""
    target = temp_dir / ".config" / "opencode"
    target.mkdir(parents=True)
    return target
