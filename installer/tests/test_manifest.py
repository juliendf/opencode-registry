"""
Tests for manifest.py - Component manifest parsing and validation.
"""

from opencode_config.utils.manifest import ComponentManifest, ManifestParser


class TestComponentManifest:
    """Test ComponentManifest dataclass."""

    def test_create_basic_manifest(self):
        """Test creating a basic manifest."""
        manifest = ComponentManifest(
            id="test-agent", type="agent", name="Test Agent", description="A test agent"
        )

        assert manifest.id == "test-agent"
        assert manifest.type == "agent"
        assert manifest.name == "Test Agent"
        assert manifest.description == "A test agent"
        assert manifest.version == "1.0.0"  # Default
        assert manifest.tags == []  # Default
        assert manifest.dependencies == []  # Default

    def test_create_full_manifest(self):
        """Test creating a manifest with all fields."""
        manifest = ComponentManifest(
            id="test-skill",
            type="skill",
            name="Test Skill",
            description="A test skill",
            version="2.0.0",
            author="Test Author",
            tags=["test", "skill"],
            dependencies=["dep1", "dep2"],
            sources=[{"path": "SKILL.md", "dest": "skills/test-skill/SKILL.md"}],
        )

        assert manifest.version == "2.0.0"
        assert manifest.author == "Test Author"
        assert manifest.tags == ["test", "skill"]
        assert manifest.dependencies == ["dep1", "dep2"]
        assert len(manifest.sources) == 1


class TestManifestParser:
    """Test ManifestParser functionality."""

    def test_parse_frontmatter_agent(self, mock_agent_md):
        """Test parsing frontmatter from agent markdown file."""
        frontmatter = ManifestParser.parse_frontmatter(mock_agent_md)

        assert frontmatter is not None
        assert frontmatter["name"] == "Test Agent"
        assert frontmatter["description"] == "A test agent for unit testing"
        assert frontmatter["type"] == "agent"
        assert frontmatter["version"] == "1.2.3"
        assert frontmatter["author"] == "Test Author"
        assert frontmatter["tags"] == ["test", "mock"]

    def test_parse_frontmatter_skill(self, mock_skill_md):
        """Test parsing frontmatter from skill markdown file."""
        frontmatter = ManifestParser.parse_frontmatter(mock_skill_md)

        assert frontmatter is not None
        assert frontmatter["name"] == "Test Skill"
        assert frontmatter["metadata"]["version"] == "2.0.0"
        assert frontmatter["license"] == "MIT"

    def test_parse_frontmatter_command(self, mock_command_md):
        """Test parsing frontmatter from command markdown file."""
        frontmatter = ManifestParser.parse_frontmatter(mock_command_md)

        assert frontmatter is not None
        assert frontmatter["name"] == "Test Command"
        assert frontmatter["version"] == "1.0.0"
        assert frontmatter["agent"] == "test-agent"

    def test_parse_frontmatter_missing(self, temp_dir):
        """Test parsing file without frontmatter."""
        no_frontmatter = temp_dir / "no-frontmatter.md"
        no_frontmatter.write_text("# Just a regular markdown file\n\nNo frontmatter here.")

        frontmatter = ManifestParser.parse_frontmatter(no_frontmatter)
        assert frontmatter is None

    def test_parse_frontmatter_incomplete(self, temp_dir):
        """Test parsing file with incomplete frontmatter."""
        incomplete = temp_dir / "incomplete.md"
        incomplete.write_text("---\nname: Test\n")  # Missing closing ---

        frontmatter = ManifestParser.parse_frontmatter(incomplete)
        assert frontmatter is None

    def test_extract_version_agent(self):
        """Test version extraction for agents."""
        frontmatter = {"version": "1.5.0", "name": "Test"}
        version = ManifestParser._extract_version(frontmatter, "agent")
        assert version == "1.5.0"

    def test_extract_version_skill(self):
        """Test version extraction for skills."""
        frontmatter = {"metadata": {"version": "2.5.0", "category": "test"}}
        version = ManifestParser._extract_version(frontmatter, "skill")
        assert version == "2.5.0"

    def test_extract_version_skill_missing_metadata(self):
        """Test version extraction for skills without metadata."""
        frontmatter = {"name": "Test"}
        version = ManifestParser._extract_version(frontmatter, "skill")
        assert version == "1.0.0"  # Default

    def test_extract_version_default(self):
        """Test version extraction with missing version field."""
        frontmatter = {"name": "Test"}
        version = ManifestParser._extract_version(frontmatter, "agent")
        assert version == "1.0.0"  # Default

    def test_create_from_md_agent(self, mock_agent_md):
        """Test creating manifest from agent markdown file."""
        manifest = ManifestParser.create_from_md(mock_agent_md, "agent")

        assert manifest.id == "test-agent"
        assert manifest.type == "agent"
        assert manifest.name == "Test Agent"
        assert manifest.description == "A test agent for unit testing"
        assert manifest.version == "1.2.3"
        assert manifest.author == "Test Author"
        assert manifest.tags == ["test", "mock"]
        assert len(manifest.sources) == 1
        assert manifest.sources[0]["path"] == "test-agent.md"
        assert manifest.sources[0]["dest"] == "agents/test-agent.md"

    def test_create_from_md_skill(self, mock_skill_md):
        """Test creating manifest from skill markdown file."""
        manifest = ManifestParser.create_from_md(mock_skill_md, "skill")

        assert manifest.id == "test-skill"
        assert manifest.type == "skill"
        assert manifest.name == "Test Skill"
        assert manifest.version == "2.0.0"

    def test_create_from_md_no_frontmatter(self, temp_dir):
        """Test creating manifest from markdown file without frontmatter."""
        no_fm = temp_dir / "basic-agent.md"
        no_fm.write_text("# Basic Agent\n\nNo frontmatter.")

        manifest = ManifestParser.create_from_md(no_fm, "agent")

        assert manifest.id == "basic-agent"
        assert manifest.type == "agent"
        assert manifest.name == "Basic Agent"  # Generated from filename
        assert manifest.description == "OpenCode agent"
        assert manifest.version == "1.0.0"

    def test_validate_valid_manifest(self):
        """Test validating a valid manifest."""
        manifest = ComponentManifest(id="test", type="agent", name="Test", description="Test agent")

        errors = ManifestParser.validate(manifest)
        assert errors == []

    def test_validate_missing_id(self):
        """Test validating manifest with missing id."""
        manifest = ComponentManifest(id="", type="agent", name="Test", description="Test")

        errors = ManifestParser.validate(manifest)
        assert "Missing required field: id" in errors

    def test_validate_missing_type(self):
        """Test validating manifest with missing type."""
        manifest = ComponentManifest(id="test", type="", name="Test", description="Test")

        errors = ManifestParser.validate(manifest)
        assert "Missing required field: type" in errors

    def test_validate_invalid_type(self):
        """Test validating manifest with invalid type."""
        manifest = ComponentManifest(id="test", type="invalid", name="Test", description="Test")

        errors = ManifestParser.validate(manifest)
        assert any("Invalid type" in error for error in errors)

    def test_validate_missing_name(self):
        """Test validating manifest with missing name."""
        manifest = ComponentManifest(id="test", type="agent", name="", description="Test")

        errors = ManifestParser.validate(manifest)
        assert "Missing required field: name" in errors

    def test_validate_missing_description(self):
        """Test validating manifest with missing description."""
        manifest = ComponentManifest(id="test", type="agent", name="Test", description="")

        errors = ManifestParser.validate(manifest)
        assert "Missing required field: description" in errors

    def test_validate_multiple_errors(self):
        """Test validating manifest with multiple errors."""
        manifest = ComponentManifest(id="", type="invalid", name="", description="")

        errors = ManifestParser.validate(manifest)
        assert len(errors) == 4  # All required fields missing + invalid type


class TestManifestModelTier:
    """Test model_tier and model field parsing in manifest."""

    def test_create_from_md_with_model_tier(self, temp_dir, mock_registry):
        """Test creating manifest from agent with model_tier frontmatter."""
        agent_file = mock_registry / "opencode" / "agents" / "tiered-agent.md"
        agent_file.write_text(
            """---
name: "Tiered Agent"
description: "An agent with model tier"
type: "agent"
version: "1.0.0"
model: "claude-opus-4-5"
model_tier: "high"
---

# Tiered Agent
"""
        )
        manifest = ManifestParser.create_from_md(agent_file, "agent")

        assert manifest.model_tier == "high"
        assert manifest.model == "claude-opus-4-5"

    def test_create_from_md_model_tier_only(self, temp_dir, mock_registry):
        """Test creating manifest from agent with only model_tier (no model)."""
        agent_file = mock_registry / "opencode" / "agents" / "tier-only-agent.md"
        agent_file.write_text(
            """---
name: "Tier Only Agent"
description: "An agent with only model_tier"
type: "agent"
version: "1.0.0"
model_tier: "medium"
---

# Tier Only Agent
"""
        )
        manifest = ManifestParser.create_from_md(agent_file, "agent")

        assert manifest.model_tier == "medium"
        assert manifest.model is None

    def test_create_from_md_no_model_fields(self, mock_agent_md):
        """Test manifest from agent without any model fields defaults to None."""
        manifest = ManifestParser.create_from_md(mock_agent_md, "agent")

        assert manifest.model_tier is None
        assert manifest.model is None

    def test_create_from_md_low_tier(self, temp_dir, mock_registry):
        """Test creating manifest with low model tier."""
        agent_file = mock_registry / "opencode" / "agents" / "low-tier-agent.md"
        agent_file.write_text(
            """---
name: "Low Tier Agent"
description: "An agent with low tier"
type: "agent"
version: "1.0.0"
model_tier: "low"
---

# Low Tier Agent
"""
        )
        manifest = ManifestParser.create_from_md(agent_file, "agent")

        assert manifest.model_tier == "low"

    def test_component_manifest_defaults_model_fields(self):
        """Test that ComponentManifest defaults model and model_tier to None."""
        manifest = ComponentManifest(
            id="test", type="agent", name="Test", description="A test"
        )

        assert manifest.model_tier is None
        assert manifest.model is None

    def test_component_manifest_with_model_fields(self):
        """Test creating ComponentManifest with explicit model fields."""
        manifest = ComponentManifest(
            id="test",
            type="agent",
            name="Test",
            description="A test",
            model_tier="high",
            model="claude-opus-4-5",
        )

        assert manifest.model_tier == "high"
        assert manifest.model == "claude-opus-4-5"
