"""
Tests for config.py - Configuration management.
"""

import json
from opencode_config.config import Config


class TestConfig:
    """Test Config functionality."""

    def test_create_default_config(self, temp_dir):
        """Test creating default configuration."""
        config_file = temp_dir / "config.json"
        config = Config(config_file)

        assert config.data is not None
        assert "target" in config.data
        assert "registry_path" in config.data
        assert "install_method" in config.data
        assert "log_level" in config.data

    def test_auto_detect_registry(self, mock_registry):
        """Test auto-detection of registry path."""
        config_file = mock_registry / "config.json"

        # Change to registry directory and create config
        import os

        original_dir = os.getcwd()
        try:
            os.chdir(mock_registry)
            config = Config(config_file)

            # Use detect_registry_path method
            detected_path = config.detect_registry_path()
            assert detected_path is not None
            # Use resolve() to handle symlinks (like /var -> /private/var on macOS)
            assert detected_path.resolve() == mock_registry.resolve()
        finally:
            os.chdir(original_dir)

    def test_get_config_value(self, temp_dir):
        """Test getting configuration values."""
        config_file = temp_dir / "config.json"
        config = Config(config_file)

        config.set("custom_key", "custom_value")

        assert config.get("custom_key") == "custom_value"

    def test_get_config_default(self, temp_dir):
        """Test getting configuration with default value."""
        config_file = temp_dir / "config.json"
        config = Config(config_file)

        value = config.get("nonexistent", default="default_value")
        assert value == "default_value"

    def test_set_config_value(self, temp_dir):
        """Test setting configuration values."""
        config_file = temp_dir / "config.json"
        config = Config(config_file)

        config.set("test_key", "test_value")

        # Should be saved to file
        with open(config_file, "r") as f:
            data = json.load(f)

        assert data["test_key"] == "test_value"

    def test_persistence(self, temp_dir):
        """Test that configuration persists across instances."""
        config_file = temp_dir / "config.json"

        # Set value in first instance
        config1 = Config(config_file)
        config1.set("persistent_key", "persistent_value")

        # Load in second instance
        config2 = Config(config_file)
        assert config2.get("persistent_key") == "persistent_value"

    def test_set_target_directory(self, temp_dir):
        """Test setting target directory."""
        config_file = temp_dir / "config.json"
        config = Config(config_file)

        target_path = "/custom/target/path"
        config.set("target", target_path)

        assert config.get("target") == target_path

    def test_set_registry_path(self, temp_dir):
        """Test setting registry path."""
        config_file = temp_dir / "config.json"
        config = Config(config_file)

        registry_path = "/custom/registry/path"
        config.set("registry_path", registry_path)

        assert config.get("registry_path") == registry_path
