"""
Version comparison utilities for semantic versioning.
"""

from typing import Tuple
import re


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse a semantic version string into (major, minor, patch) tuple.

    Args:
        version_str: Version string like "1.2.3" or "v1.2.3"

    Returns:
        Tuple of (major, minor, patch) as integers

    Raises:
        ValueError: If version string is invalid
    """
    # Remove 'v' prefix if present
    version_str = version_str.lstrip("v").strip('"').strip("'")

    # Match semantic version pattern
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str)
    if not match:
        raise ValueError(f"Invalid semantic version: {version_str}")

    return tuple(int(x) for x in match.groups())


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two semantic version strings.

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    try:
        v1 = parse_version(version1)
        v2 = parse_version(version2)

        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except ValueError:
        # If parsing fails, fall back to string comparison
        if version1 < version2:
            return -1
        elif version1 > version2:
            return 1
        else:
            return 0


def is_newer_version(available: str, installed: str) -> bool:
    """
    Check if available version is newer than installed version.

    Args:
        available: Available version string
        installed: Installed version string

    Returns:
        True if available is newer than installed
    """
    return compare_versions(available, installed) > 0


def format_version(version: str) -> str:
    """
    Format a version string consistently (remove quotes, normalize).

    Args:
        version: Version string to format

    Returns:
        Normalized version string
    """
    return version.strip().strip('"').strip("'").lstrip("v")
