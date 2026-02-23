"""
Template processing for model tier resolution.
"""

import re
from typing import Dict, Optional, Any
from ..config import Config


class TemplateEngine:
    """Handle template replacement in component files."""

    TIER_PATTERN = re.compile(r'\{\{tier:(\w+)\}\}')
    MODEL_PATTERN = re.compile(r'\{\{model:([^\}]+)\}\}')

    def __init__(self, config: Config):
        """
        Initialize template engine.

        Args:
            config: Config instance for tier resolution
        """
        self.config = config

    def process_content(
        self, content: str, overrides: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Replace template placeholders in content.

        Supported patterns:
        - {{tier:high}} → Resolves to configured model for 'high' tier
        - {{model:literal}} → Replaced with literal value

        Args:
            content: File content with potential templates
            overrides: Optional dict to override tier/model values

        Returns:
            Content with templates replaced

        Raises:
            ValueError: If tier reference is invalid
        """
        overrides = overrides or {}

        # Replace {{tier:X}} patterns
        def replace_tier(match):
            tier = match.group(1)
            # Check overrides first
            if tier in overrides:
                return overrides[tier]
            # Resolve from config
            model = self.config.get_model_for_tier(tier)
            if model is None:
                # Fallback to medium tier
                model = self.config.get_model_for_tier("medium")
                if model is None:
                    raise ValueError(
                        f"Invalid tier '{tier}' and fallback 'medium' not configured"
                    )
            return model

        # Replace {{model:X}} patterns (literal replacement)
        def replace_model(match):
            return match.group(1)

        content = self.TIER_PATTERN.sub(replace_tier, content)
        content = self.MODEL_PATTERN.sub(replace_model, content)

        return content

    def extract_tier_from_frontmatter(self, frontmatter: Dict[str, Any]) -> Optional[str]:
        """
        Extract model_tier from frontmatter.

        Args:
            frontmatter: Parsed YAML frontmatter dict

        Returns:
            Tier name or None if not specified
        """
        return frontmatter.get("model_tier")

    def extract_model_from_frontmatter(self, frontmatter: Dict[str, Any]) -> Optional[str]:
        """
        Extract model from frontmatter.

        Args:
            frontmatter: Parsed YAML frontmatter dict

        Returns:
            Model string or None if not specified
        """
        return frontmatter.get("model")

    def resolve_model(
        self, tier_or_model: Optional[str], default_tier: str = "medium"
    ) -> str:
        """
        Resolve tier reference or return literal model.

        Args:
            tier_or_model: Either tier name (high/medium/low) or literal model string
            default_tier: Fallback tier if resolution fails

        Returns:
            Resolved model string
        """
        if not tier_or_model:
            # No value specified, use default tier
            model = self.config.get_model_for_tier(default_tier)
            if model:
                return model
            # Fallback to medium if default doesn't exist
            return self.config.get_model_for_tier("medium") or "github-copilot/claude-sonnet-4"

        # Check if it's a tier reference
        if tier_or_model in ["high", "medium", "low"]:
            model = self.config.get_model_for_tier(tier_or_model)
            if model:
                return model
            # Fallback
            return self.config.get_model_for_tier(default_tier) or "github-copilot/claude-4.0"

        # It's a literal model string
        return tier_or_model

    def should_process_file(self, file_path: str) -> bool:
        """
        Determine if file should be processed for templates.

        Args:
            file_path: Path to file

        Returns:
            True if file should be processed
        """
        # Only process markdown files (agents, skills, commands)
        return file_path.endswith(".md")
