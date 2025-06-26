"""
Prompt migration utilities.

This package provides tools for migrating hardcoded prompts
to the new prompt storage system.
"""

from .legacy_prompts import LegacyPromptExtractor
from .prompt_migrator import PromptMigrator

__all__ = [
    'LegacyPromptExtractor',
    'PromptMigrator'
] 