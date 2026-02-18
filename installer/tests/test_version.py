"""
Tests for version.py - Semantic version parsing and comparison.
"""

import pytest
from opencode_config.utils.version import (
    parse_version,
    compare_versions,
    is_newer_version,
    format_version,
)


class TestParseVersion:
    """Test version parsing functionality."""

    def test_parse_basic_version(self):
        """Test parsing a basic semantic version."""
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_parse_version_with_v_prefix(self):
        """Test parsing version with 'v' prefix."""
        assert parse_version("v1.2.3") == (1, 2, 3)

    def test_parse_version_with_quotes(self):
        """Test parsing version with quotes."""
        assert parse_version('"1.2.3"') == (1, 2, 3)
        assert parse_version("'1.2.3'") == (1, 2, 3)

    def test_parse_zero_version(self):
        """Test parsing version with zeros."""
        assert parse_version("0.0.0") == (0, 0, 0)

    def test_parse_large_numbers(self):
        """Test parsing version with large numbers."""
        assert parse_version("10.20.30") == (10, 20, 30)

    def test_parse_invalid_version(self):
        """Test parsing invalid version strings."""
        with pytest.raises(ValueError):
            parse_version("1.2")

        with pytest.raises(ValueError):
            parse_version("1.2.3.4")

        with pytest.raises(ValueError):
            parse_version("abc")

        with pytest.raises(ValueError):
            parse_version("1.x.3")


class TestCompareVersions:
    """Test version comparison functionality."""

    def test_equal_versions(self):
        """Test comparing equal versions."""
        assert compare_versions("1.2.3", "1.2.3") == 0

    def test_newer_major_version(self):
        """Test newer major version."""
        assert compare_versions("2.0.0", "1.9.9") == 1
        assert compare_versions("1.9.9", "2.0.0") == -1

    def test_newer_minor_version(self):
        """Test newer minor version."""
        assert compare_versions("1.3.0", "1.2.9") == 1
        assert compare_versions("1.2.9", "1.3.0") == -1

    def test_newer_patch_version(self):
        """Test newer patch version."""
        assert compare_versions("1.2.4", "1.2.3") == 1
        assert compare_versions("1.2.3", "1.2.4") == -1

    def test_compare_with_v_prefix(self):
        """Test comparison with 'v' prefix."""
        assert compare_versions("v1.2.3", "1.2.3") == 0
        assert compare_versions("v2.0.0", "v1.0.0") == 1

    def test_compare_invalid_versions_fallback(self):
        """Test comparison fallback for invalid versions."""
        # Should fall back to string comparison without raising
        result = compare_versions("invalid1", "invalid2")
        assert isinstance(result, int)


class TestIsNewerVersion:
    """Test is_newer_version helper."""

    def test_newer_version(self):
        """Test detecting newer version."""
        assert is_newer_version("2.0.0", "1.0.0") is True
        assert is_newer_version("1.1.0", "1.0.0") is True
        assert is_newer_version("1.0.1", "1.0.0") is True

    def test_same_version(self):
        """Test same version."""
        assert is_newer_version("1.0.0", "1.0.0") is False

    def test_older_version(self):
        """Test older version."""
        assert is_newer_version("1.0.0", "2.0.0") is False
        assert is_newer_version("1.0.0", "1.1.0") is False
        assert is_newer_version("1.0.0", "1.0.1") is False


class TestFormatVersion:
    """Test version formatting."""

    def test_format_clean_version(self):
        """Test formatting already clean version."""
        assert format_version("1.2.3") == "1.2.3"

    def test_format_version_with_v(self):
        """Test formatting version with 'v' prefix."""
        assert format_version("v1.2.3") == "1.2.3"

    def test_format_version_with_quotes(self):
        """Test formatting version with quotes."""
        assert format_version('"1.2.3"') == "1.2.3"
        assert format_version("'1.2.3'") == "1.2.3"

    def test_format_version_with_whitespace(self):
        """Test formatting version with whitespace."""
        assert format_version("  1.2.3  ") == "1.2.3"

    def test_format_version_combined(self):
        """Test formatting version with multiple formatting issues."""
        assert format_version('  "v1.2.3"  ') == "1.2.3"
