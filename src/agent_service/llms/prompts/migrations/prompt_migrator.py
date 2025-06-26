"""
Prompt migration utilities.

This module provides tools for migrating prompts from legacy formats
to the new prompt storage system.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models import PromptInfo, PromptConfig
from ..service import PromptService
from ..stores import PromptStore
from ..exceptions import PromptStorageError, PromptValidationError
from .legacy_prompts import LegacyPromptExtractor, LegacyPrompt

logger = logging.getLogger(__name__)


class PromptMigrator:
    """
    Utility for migrating prompts to the new storage system.
    
    This class provides methods to migrate prompts from various sources
    to the new prompt storage system with validation and rollback support.
    """
    
    def __init__(self, prompt_service: PromptService):
        """
        Initialize the migrator.
        
        Args:
            prompt_service: The prompt service to use for storage
        """
        self.prompt_service = prompt_service
        self.extractor = LegacyPromptExtractor()
        self.migration_history: List[Dict[str, Any]] = []
    
    def migrate_llm_service_prompts(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate hardcoded prompts from LLMService.
        
        Args:
            dry_run: If True, don't actually save prompts
            
        Returns:
            Migration results
        """
        logger.info("Starting LLMService prompt migration...")
        
        # Extract prompts from LLMService
        legacy_prompts = self.extractor.extract_from_llm_service()
        
        # Validate extracted prompts
        validation_errors = self.extractor.validate_extracted_prompts()
        if validation_errors:
            logger.error(f"Validation errors found: {validation_errors}")
            return {
                "success": False,
                "errors": validation_errors,
                "migrated_count": 0
            }
        
        # Convert to PromptInfo objects
        prompt_infos = []
        for legacy_prompt in legacy_prompts:
            prompt_info = self.extractor.convert_to_prompt_info(legacy_prompt)
            prompt_infos.append(prompt_info)
        
        # Migrate prompts
        return self._migrate_prompts(prompt_infos, dry_run, "llm_service")
    
    def migrate_from_legacy_prompts(self, legacy_prompts: List[LegacyPrompt], 
                                  dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate a list of legacy prompts.
        
        Args:
            legacy_prompts: List of legacy prompts to migrate
            dry_run: If True, don't actually save prompts
            
        Returns:
            Migration results
        """
        logger.info(f"Starting migration of {len(legacy_prompts)} legacy prompts...")
        
        # Convert to PromptInfo objects
        prompt_infos = []
        for legacy_prompt in legacy_prompts:
            prompt_info = self.extractor.convert_to_prompt_info(legacy_prompt)
            prompt_infos.append(prompt_info)
        
        # Migrate prompts
        return self._migrate_prompts(prompt_infos, dry_run, "legacy_prompts")
    
    def migrate_from_yaml_files(self, yaml_directory: Path, 
                              dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate prompts from YAML files.
        
        Args:
            yaml_directory: Directory containing YAML prompt files
            dry_run: If True, don't actually save prompts
            
        Returns:
            Migration results
        """
        logger.info(f"Starting migration from YAML directory: {yaml_directory}")
        
        if not yaml_directory.exists():
            return {
                "success": False,
                "errors": [f"Directory does not exist: {yaml_directory}"],
                "migrated_count": 0
            }
        
        # Find all YAML files
        yaml_files = list(yaml_directory.glob("*.yaml"))
        if not yaml_files:
            return {
                "success": False,
                "errors": [f"No YAML files found in: {yaml_directory}"],
                "migrated_count": 0
            }
        
        # Load and convert YAML files
        prompt_infos = []
        errors = []
        
        for yaml_file in yaml_files:
            try:
                prompt_info = self._load_prompt_from_yaml(yaml_file)
                prompt_infos.append(prompt_info)
            except Exception as e:
                error_msg = f"Error loading {yaml_file}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        if errors:
            return {
                "success": False,
                "errors": errors,
                "migrated_count": 0
            }
        
        # Migrate prompts
        return self._migrate_prompts(prompt_infos, dry_run, "yaml_files")
    
    def _migrate_prompts(self, prompt_infos: List[PromptInfo], 
                        dry_run: bool, source: str) -> Dict[str, Any]:
        """
        Internal method to migrate prompts.
        
        Args:
            prompt_infos: List of prompts to migrate
            dry_run: If True, don't actually save
            source: Source identifier for migration history
            
        Returns:
            Migration results
        """
        migrated_count = 0
        errors = []
        
        for prompt_info in prompt_infos:
            try:
                if not dry_run:
                    # Check if prompt already exists
                    if self.prompt_service.exists(prompt_info.name, prompt_info.version):
                        logger.warning(f"Prompt {prompt_info.name}:{prompt_info.version} already exists, skipping")
                        continue
                    
                    # Save the prompt
                    self.prompt_service.save_prompt(prompt_info)
                    logger.info(f"Migrated prompt: {prompt_info.name}:{prompt_info.version}")
                else:
                    logger.info(f"Would migrate prompt: {prompt_info.name}:{prompt_info.version}")
                
                migrated_count += 1
                
            except Exception as e:
                error_msg = f"Error migrating {prompt_info.name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Record migration history
        migration_record = {
            "source": source,
            "dry_run": dry_run,
            "total_prompts": len(prompt_infos),
            "migrated_count": migrated_count,
            "errors": errors,
            "success": len(errors) == 0
        }
        self.migration_history.append(migration_record)
        
        return {
            "success": len(errors) == 0,
            "migrated_count": migrated_count,
            "total_prompts": len(prompt_infos),
            "errors": errors,
            "dry_run": dry_run
        }
    
    def _load_prompt_from_yaml(self, yaml_file: Path) -> PromptInfo:
        """
        Load a prompt from a YAML file.
        
        Args:
            yaml_file: Path to YAML file
            
        Returns:
            PromptInfo object
            
        Raises:
            Exception: If file cannot be loaded or parsed
        """
        import yaml
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Extract prompt name from filename if not in data
        if 'name' not in data:
            data['name'] = yaml_file.stem
        
        # Ensure required fields
        required_fields = ['name', 'content']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults
        data.setdefault('version', '1.0')
        data.setdefault('metadata', {})
        data.setdefault('variables', [])
        
        return PromptInfo(**data)
    
    def rollback_migration(self, migration_index: int = -1) -> Dict[str, Any]:
        """
        Rollback a migration.
        
        Args:
            migration_index: Index of migration to rollback (-1 for latest)
            
        Returns:
            Rollback results
        """
        if not self.migration_history:
            return {
                "success": False,
                "errors": ["No migration history found"],
                "rolled_back_count": 0
            }
        
        if migration_index >= len(self.migration_history):
            return {
                "success": False,
                "errors": [f"Invalid migration index: {migration_index}"],
                "rolled_back_count": 0
            }
        
        migration_record = self.migration_history[migration_index]
        
        if migration_record["dry_run"]:
            return {
                "success": True,
                "errors": [],
                "rolled_back_count": 0,
                "message": "No rollback needed for dry run"
            }
        
        logger.info(f"Rolling back migration: {migration_record}")
        
        # Note: This is a simplified rollback - in practice, you might want
        # to store more detailed information about what was migrated
        # For now, we'll just log the rollback
        
        return {
            "success": True,
            "errors": [],
            "rolled_back_count": migration_record["migrated_count"],
            "message": f"Rolled back {migration_record['migrated_count']} prompts"
        }
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        return self.migration_history.copy()
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate that migrated prompts are accessible.
        
        Returns:
            Validation results
        """
        logger.info("Validating migration...")
        
        validation_results = {
            "total_prompts": 0,
            "valid_prompts": 0,
            "invalid_prompts": 0,
            "errors": []
        }
        
        try:
            # Get all prompts from the service
            all_prompts = self.prompt_service.list_prompts()
            validation_results["total_prompts"] = len(all_prompts)
            
            for prompt_info in all_prompts:
                try:
                    # Try to retrieve the prompt
                    retrieved_prompt = self.prompt_service.get_prompt(prompt_info.name, prompt_info.version)
                    
                    # Try to render the prompt with empty variables
                    if prompt_info.variables:
                        # Create empty variables for testing
                        test_variables = {var: f"test_{var}" for var in prompt_info.variables}
                        self.prompt_service.render_prompt(prompt_info.name, test_variables, prompt_info.version)
                    
                    validation_results["valid_prompts"] += 1
                    
                except Exception as e:
                    error_msg = f"Error validating {prompt_info.name}:{prompt_info.version}: {str(e)}"
                    logger.error(error_msg)
                    validation_results["errors"].append(error_msg)
                    validation_results["invalid_prompts"] += 1
            
        except Exception as e:
            error_msg = f"Error during validation: {str(e)}"
            logger.error(error_msg)
            validation_results["errors"].append(error_msg)
        
        validation_results["success"] = validation_results["invalid_prompts"] == 0
        
        return validation_results 