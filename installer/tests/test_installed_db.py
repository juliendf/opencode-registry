"""
Tests for installed_db.py - Installation database management.
"""

from opencode_config.utils.installed_db import InstalledDB


class TestInstalledDB:
    """Test InstalledDB functionality."""

    def test_create_default_database(self, temp_dir):
        """Test creating a new database with default structure."""
        db_path = temp_dir / "installed.json"
        db = InstalledDB(db_path)

        assert db.data["version"] == "1.0"
        assert "installed" in db.data
        assert "agents" in db.data["installed"]
        assert "skills" in db.data["installed"]
        assert "commands" in db.data["installed"]
        assert "subagents" in db.data["installed"]
        assert "bundles" in db.data
        assert "logs" in db.data
        assert "metadata" in db.data

    def test_save_and_load_database(self, temp_dir):
        """Test saving and loading database."""
        db_path = temp_dir / "installed.json"

        # Create and save
        db1 = InstalledDB(db_path)
        db1.add_component("agent", "test-agent", {"version": "1.0.0"})

        # Load in new instance
        db2 = InstalledDB(db_path)
        assert "test-agent" in db2.data["installed"]["agents"]

    def test_add_component_agent(self, temp_dir):
        """Test adding an agent component."""
        db = InstalledDB(temp_dir / "installed.json")

        db.add_component("agent", "build-general", {"version": "1.0.0", "installMethod": "stow"})

        assert "build-general" in db.data["installed"]["agents"]
        component = db.data["installed"]["agents"]["build-general"]
        assert component["version"] == "1.0.0"
        assert component["installMethod"] == "stow"
        assert "installedAt" in component

    def test_add_component_skill(self, temp_dir):
        """Test adding a skill component."""
        db = InstalledDB(temp_dir / "installed.json")

        db.add_component("skill", "mcp-builder", {"version": "2.0.0", "installMethod": "symlink"})

        assert "mcp-builder" in db.data["installed"]["skills"]

    def test_add_component_creates_type_key(self, temp_dir):
        """Test that adding component creates type key if missing."""
        db = InstalledDB(temp_dir / "installed.json")

        # Remove a type key
        del db.data["installed"]["agents"]

        # Add component should recreate it
        db.add_component("agent", "test", {"version": "1.0.0"})

        assert "agents" in db.data["installed"]
        assert "test" in db.data["installed"]["agents"]

    def test_remove_component(self, temp_dir):
        """Test removing a component."""
        db = InstalledDB(temp_dir / "installed.json")

        # Add then remove
        db.add_component("agent", "test-agent", {"version": "1.0.0"})
        assert "test-agent" in db.data["installed"]["agents"]

        db.remove_component("agent", "test-agent")
        assert "test-agent" not in db.data["installed"]["agents"]

    def test_remove_nonexistent_component(self, temp_dir):
        """Test removing a component that doesn't exist."""
        db = InstalledDB(temp_dir / "installed.json")

        # Should not raise error
        db.remove_component("agent", "nonexistent")

    def test_get_component(self, temp_dir):
        """Test getting component metadata."""
        db = InstalledDB(temp_dir / "installed.json")

        db.add_component("agent", "test-agent", {"version": "1.5.0", "installMethod": "stow"})

        component = db.get_component("agent", "test-agent")
        assert component is not None
        assert component["version"] == "1.5.0"

    def test_get_nonexistent_component(self, temp_dir):
        """Test getting component that doesn't exist."""
        db = InstalledDB(temp_dir / "installed.json")

        component = db.get_component("agent", "nonexistent")
        assert component is None

    def test_is_installed(self, temp_dir):
        """Test checking if component is installed."""
        db = InstalledDB(temp_dir / "installed.json")

        db.add_component("agent", "test-agent", {"version": "1.0.0"})

        assert db.is_installed("test-agent") is True
        assert db.is_installed("nonexistent") is False

    def test_get_installed_version(self, temp_dir):
        """Test getting installed version of a component."""
        db = InstalledDB(temp_dir / "installed.json")

        db.add_component("agent", "test-agent", {"version": "1.5.0"})

        version = db.get_installed_version("test-agent")
        assert version == "1.5.0"

    def test_get_installed_version_missing(self, temp_dir):
        """Test getting version of component that isn't installed."""
        db = InstalledDB(temp_dir / "installed.json")

        version = db.get_installed_version("nonexistent")
        assert version is None

    def test_get_installed_version_no_version_field(self, temp_dir):
        """Test getting version when component has no version field."""
        db = InstalledDB(temp_dir / "installed.json")

        # Manually add component without version
        db.data["installed"]["agents"]["test"] = {"id": "test"}

        version = db.get_installed_version("test")
        assert version == "unknown"

    def test_get_all_installed(self, temp_dir):
        """Test getting all installed components."""
        db = InstalledDB(temp_dir / "installed.json")

        db.add_component("agent", "agent1", {"version": "1.0.0"})
        db.add_component("skill", "skill1", {"version": "2.0.0"})
        db.add_component("command", "cmd1", {"version": "1.5.0"})

        all_installed = db.get_all_installed()

        assert len(all_installed) == 3
        ids = [c["id"] for c in all_installed]
        assert "agent1" in ids
        assert "skill1" in ids
        assert "cmd1" in ids

    def test_get_all_installed_empty(self, temp_dir):
        """Test getting all installed when nothing is installed."""
        db = InstalledDB(temp_dir / "installed.json")

        all_installed = db.get_all_installed()
        assert all_installed == []

    def test_log_action(self, temp_dir):
        """Test logging an installation action."""
        db = InstalledDB(temp_dir / "installed.json")

        db.log_action(
            action="install",
            components=["agent1", "skill1"],
            method="stow",
            status="success",
            duration="2.5s",
        )

        logs = db.data["logs"]["installation"]
        assert len(logs) == 1
        assert logs[0]["action"] == "install"
        assert logs[0]["components"] == ["agent1", "skill1"]
        assert logs[0]["method"] == "stow"
        assert logs[0]["status"] == "success"
        assert logs[0]["duration"] == "2.5s"
        assert "timestamp" in logs[0]

    def test_add_bundle(self, temp_dir):
        """Test adding a bundle to the database."""
        db = InstalledDB(temp_dir / "installed.json")

        db.add_bundle("basic", ["agent1", "agent2", "skill1"])

        assert "basic" in db.data["bundles"]
        bundle = db.data["bundles"]["basic"]
        assert bundle["name"] == "basic"
        assert bundle["components"] == ["agent1", "agent2", "skill1"]
        assert "installedAt" in bundle

    def test_set_install_method(self, temp_dir):
        """Test setting installation method."""
        db = InstalledDB(temp_dir / "installed.json")

        db.set_install_method("stow")
        assert db.data["installMethod"] == "stow"

        db.set_install_method("symlink")
        assert db.data["installMethod"] == "symlink"

    def test_set_target_directory(self, temp_dir):
        """Test setting target directory."""
        db = InstalledDB(temp_dir / "installed.json")

        db.set_target_directory("/custom/path")
        assert db.data["targetDirectory"] == "/custom/path"

    def test_set_registry_path(self, temp_dir):
        """Test setting registry path."""
        db = InstalledDB(temp_dir / "installed.json")

        db.set_registry_path("/path/to/registry")
        assert db.data["registry"]["path"] == "/path/to/registry"

    def test_sync_from_detected(self, temp_dir):
        """Test syncing database from detected components."""
        db = InstalledDB(temp_dir / "installed.json")

        # Add some existing components
        db.add_component("agent", "old-agent", {"version": "1.0.0"})

        # Sync with new detected components
        detected = {"agents": ["agent1", "agent2"], "skills": ["skill1"], "commands": []}

        db.sync_from_detected(detected, "stow")

        # Old component should be gone
        assert "old-agent" not in db.data["installed"]["agents"]

        # New components should be present
        assert "agent1" in db.data["installed"]["agents"]
        assert "agent2" in db.data["installed"]["agents"]
        assert "skill1" in db.data["installed"]["skills"]

        # Check default version
        assert db.data["installed"]["agents"]["agent1"]["version"] == "1.0.0"

    def test_sync_from_detected_with_versions(self, temp_dir):
        """Test syncing with component versions provided."""
        db = InstalledDB(temp_dir / "installed.json")

        detected = {"agents": ["agent1"], "skills": ["skill1"], "commands": []}

        versions = {"agent1": "1.5.0", "skill1": "2.0.0"}

        db.sync_from_detected(detected, "stow", component_versions=versions)

        # Check versions were set correctly
        assert db.data["installed"]["agents"]["agent1"]["version"] == "1.5.0"
        assert db.data["installed"]["skills"]["skill1"]["version"] == "2.0.0"

    def test_timestamp_format(self, temp_dir):
        """Test timestamp format is ISO 8601."""
        db = InstalledDB(temp_dir / "installed.json")

        timestamp = db._timestamp()

        # Should end with 'Z' for UTC
        assert timestamp.endswith("Z")

        # Should contain 'T' separator
        assert "T" in timestamp

    def test_persistence(self, temp_dir):
        """Test that changes persist across instances."""
        db_path = temp_dir / "installed.json"

        # Create and modify
        db1 = InstalledDB(db_path)
        db1.add_component("agent", "test", {"version": "1.0.0"})

        # Load fresh instance
        db2 = InstalledDB(db_path)
        assert db2.is_installed("test")
        assert db2.get_installed_version("test") == "1.0.0"
