"""
Configuration management for opencode-config CLI.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "target": "~/.config/opencode",
    "registry_path": None,  # Auto-detected or set by user
    "install_method": "auto",  # auto, stow, symlink
    "log_level": "info",
}


class Config:
    """Manages CLI configuration."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path.home() / ".opencode-registry" / "config.json"
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        return DEFAULT_CONFIG.copy()

    def save(self):
        """Save configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.data[key] = value
        self.save()

    @property
    def target_dir(self) -> Path:
        """Get target directory as Path object."""
        return Path(os.path.expanduser(self.get("target")))

    @property
    def registry_path(self) -> Optional[Path]:
        """Get registry path as Path object."""
        path = self.get("registry_path")
        return Path(path) if path else None

    def detect_registry_path(self) -> Optional[Path]:
        """Auto-detect registry path by looking for opencode/ directory and bundles/."""
        # Check current directory and parent directories
        current = Path.cwd()
        for _ in range(5):  # Check up to 5 levels up
            # Must have both opencode/ and bundles/ directories to be valid
            if (current / "opencode").exists() and (current / "bundles").exists():
                return current
            current = current.parent
        return None
