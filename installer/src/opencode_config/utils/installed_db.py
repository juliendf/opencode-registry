"""
Installation database (installed.json) management.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import platform


class InstalledDB:
    """Manages the installed.json database."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Path.home() / ".config" / "opencode" / "opencode-registry-installed.json")
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load database from file or create default."""
        if self.db_path.exists():
            with open(self.db_path, "r") as f:
                return json.load(f)
        return self._create_default()

    def _create_default(self) -> Dict[str, Any]:
        """Create default database structure."""
        return {
            "version": "1.0",
            "lastUpdated": self._timestamp(),
            "installMethod": "unknown",
            "targetDirectory": str(Path.home() / ".config" / "opencode"),
            "registry": {"source": "local", "path": None},
            "installed": {"agents": {}, "subagents": {}, "skills": {}, "commands": {}},
            "bundles": {},
            "logs": {"installation": []},
            "metadata": {
                "osType": platform.system().lower(),
                "pythonVersion": platform.python_version(),
                "registryVersion": "0.1.0",
            },
        }

    def save(self):
        """Save database to file."""
        self.data["lastUpdated"] = self._timestamp()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def _timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat() + "Z"

    def add_component(self, component_type: str, component_id: str, metadata: Dict[str, Any]):
        """Add a component to the database."""
        component_type_key = (
            f"{component_type}s" if not component_type.endswith("s") else component_type
        )

        if component_type_key not in self.data["installed"]:
            self.data["installed"][component_type_key] = {}

        self.data["installed"][component_type_key][component_id] = {
            **metadata,
            "installedAt": self._timestamp(),
        }
        self.save()

    def remove_component(self, component_type: str, component_id: str):
        """Remove a component from the database."""
        component_type_key = (
            f"{component_type}s" if not component_type.endswith("s") else component_type
        )

        if component_type_key in self.data["installed"]:
            self.data["installed"][component_type_key].pop(component_id, None)
        self.save()

    def get_component(self, component_type: str, component_id: str) -> Optional[Dict[str, Any]]:
        """Get component metadata from database."""
        component_type_key = (
            f"{component_type}s" if not component_type.endswith("s") else component_type
        )
        return self.data["installed"].get(component_type_key, {}).get(component_id)

    def is_installed(self, component_id: str) -> bool:
        """Check if a component is installed."""
        for component_type in self.data["installed"].values():
            if component_id in component_type:
                return True
        return False

    def get_installed_version(self, component_id: str) -> Optional[str]:
        """Get the installed version of a component."""
        for component_type in self.data["installed"].values():
            if component_id in component_type:
                return component_type[component_id].get("version", "unknown")
        return None

    def get_all_installed(self) -> List[Dict[str, Any]]:
        """Get all installed components."""
        components = []
        for component_type, items in self.data["installed"].items():
            for component_id, metadata in items.items():
                components.append(
                    {"id": component_id, "type": component_type.rstrip("s"), **metadata}
                )
        return components

    def log_action(
        self, action: str, components: List[str], method: str, status: str, duration: str = "0s"
    ):
        """Log an installation action."""
        self.data["logs"]["installation"].append(
            {
                "timestamp": self._timestamp(),
                "action": action,
                "components": components,
                "method": method,
                "status": status,
                "duration": duration,
            }
        )
        self.save()

    def add_bundle(self, bundle_name: str, components: List[str]):
        """Add a bundle to the database."""
        self.data["bundles"][bundle_name] = {
            "name": bundle_name,
            "installedAt": self._timestamp(),
            "components": components,
        }
        self.save()

    def set_install_method(self, method: str):
        """Set the installation method."""
        self.data["installMethod"] = method
        self.save()

    def set_target_directory(self, target: str):
        """Set the target directory."""
        self.data["targetDirectory"] = target
        self.save()

    def set_registry_path(self, path: str):
        """Set the registry path."""
        self.data["registry"]["path"] = path
        self.save()

    def sync_from_detected(
        self,
        detected_components: Dict[str, List[str]],
        install_method: str = "copy",
        component_versions: Optional[Dict[str, str]] = None,
    ):
        """
        Sync database from detected components on disk.

        Args:
            detected_components: Dict mapping component types to lists of IDs
            install_method: Installation method used
            component_versions: Optional dict mapping component IDs to their versions
        """
        # Clear existing components
        self.data["installed"] = {"agents": {}, "subagents": {}, "skills": {}, "commands": {}}

        # Add all detected components
        for comp_type, comp_ids in detected_components.items():
            for comp_id in comp_ids:
                # Get version from component_versions dict if available, otherwise default to "1.0.0"
                version = "1.0.0"
                if component_versions and comp_id in component_versions:
                    version = component_versions[comp_id]

                self.data["installed"][comp_type][comp_id] = {
                    "id": comp_id,
                    "type": comp_type.rstrip("s"),
                    "version": version,
                    "installMethod": install_method,
                    "installedAt": self._timestamp(),
                }

        self.save()
