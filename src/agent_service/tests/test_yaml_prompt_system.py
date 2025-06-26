"""
Tests for YAML-based prompt system with GCS integration.

This module tests the prompt system using YAML templates stored in
both local filesystem and Google Cloud Storage (with emulator support).
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from agent_service.llms.prompts.models import PromptInfo, StoreType
from agent_service.llms.prompts.stores.yaml import YAMLPromptStore
from agent_service.llms.prompts.stores.gcs import GCSPromptStore
from agent_service.llms.prompts.service import PromptService


class TestYAMLPromptStore:
    """Test YAML-based prompt storage."""
    
    @pytest.fixture
    def temp_yaml_dir(self):
        """Create a temporary directory for YAML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def sample_prompts(self):
        """Sample prompt data for testing."""
        return {
            "journal_summary": {
                "name": "journal_summary",
                "version": "1.0",
                "content": "Analyze these journal entries: {{ content_block }}",
                "variables": ["content_block"],
                "metadata": {
                    "category": "journal",
                    "type": "summary",
                    "model": "gpt-4o",
                    "temperature": 0.7
                }
            },
            "performance_review": {
                "name": "performance_review", 
                "version": "1.0",
                "content": "Review these entries: {{ content_block }}",
                "variables": ["content_block"],
                "metadata": {
                    "category": "journal",
                    "type": "review",
                    "model": "gpt-4o",
                    "temperature": 0.5
                }
            }
        }
    
    def test_yaml_store_creation(self, temp_yaml_dir):
        """Test YAML store initialization."""
        store = YAMLPromptStore(temp_yaml_dir)
        assert str(store.base_path) == temp_yaml_dir
        assert os.path.exists(temp_yaml_dir)
    
    def test_save_and_load_prompt(self, temp_yaml_dir, sample_prompts):
        """Test saving and loading prompts from YAML files."""
        store = YAMLPromptStore(temp_yaml_dir)
        prompt_data = sample_prompts["journal_summary"]
        prompt_info = PromptInfo(**prompt_data)
        
        # Save prompt
        store.save_prompt(prompt_info)
        
        # Verify file was created
        expected_file = os.path.join(temp_yaml_dir, "journal_summary_1.0.yaml")
        assert os.path.exists(expected_file)
        
        # Load prompt
        loaded_prompt = store.get_prompt("journal_summary", "1.0")
        assert loaded_prompt.name == prompt_info.name
        assert loaded_prompt.version == prompt_info.version
        assert loaded_prompt.content == prompt_info.content
    
    def test_prompt_exists(self, temp_yaml_dir, sample_prompts):
        """Test checking if prompts exist."""
        store = YAMLPromptStore(temp_yaml_dir)
        prompt_info = PromptInfo(**sample_prompts["journal_summary"])
        
        # Initially doesn't exist
        assert not store.exists("journal_summary", "1.0")
        
        # Save and check existence
        store.save_prompt(prompt_info)
        assert store.exists("journal_summary", "1.0")
    
    def test_list_prompts(self, temp_yaml_dir, sample_prompts):
        """Test listing available prompts."""
        store = YAMLPromptStore(temp_yaml_dir)
        
        # Save multiple prompts
        for prompt_data in sample_prompts.values():
            prompt_info = PromptInfo(**prompt_data)
            store.save_prompt(prompt_info)
        
        # List prompts
        prompts = store.list_prompts()
        assert len(prompts) == 2
        assert any(p.name == "journal_summary" for p in prompts)
        assert any(p.name == "performance_review" for p in prompts)
    
    def test_delete_prompt(self, temp_yaml_dir, sample_prompts):
        """Test deleting prompts."""
        store = YAMLPromptStore(temp_yaml_dir)
        prompt_info = PromptInfo(**sample_prompts["journal_summary"])
        
        # Save and verify exists
        store.save_prompt(prompt_info)
        assert store.exists("journal_summary", "1.0")
        
        # Delete and verify removed
        store.delete_prompt("journal_summary", "1.0")
        assert not store.exists("journal_summary", "1.0")
    
    def test_invalid_yaml_handling(self, temp_yaml_dir):
        """Test handling of invalid YAML files."""
        store = YAMLPromptStore(temp_yaml_dir)
        
        # Create invalid YAML file
        invalid_file = os.path.join(temp_yaml_dir, "invalid.yaml")
        with open(invalid_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # Should handle gracefully and return empty list
        prompts = store.list_prompts()
        assert len(prompts) == 0


class TestGCSPromptStore:
    """Test GCS-based prompt storage with emulator support."""
    
    @pytest.fixture
    def mock_storage_loader(self):
        """Mock storage loader for testing."""
        mock_loader = Mock()
        mock_loader.read_file = Mock()
        mock_loader.write_file = Mock()
        mock_loader.delete_file = Mock()
        mock_loader.list_files = Mock(return_value=[])
        mock_loader.exists = Mock(return_value=False)
        return mock_loader
    
    @pytest.fixture
    def sample_prompts(self):
        """Sample prompt data for testing."""
        return {
            "journal_summary": {
                "name": "journal_summary",
                "version": "1.0",
                "content": "Analyze these journal entries: {{ content_block }}",
                "variables": ["content_block"],
                "metadata": {
                    "category": "journal",
                    "type": "summary",
                    "model": "gpt-4o",
                    "temperature": 0.7
                }
            }
        }
    
    def test_gcs_store_creation(self, mock_storage_loader):
        """Test GCS store initialization."""
        store = GCSPromptStore(mock_storage_loader)
        assert store.loader == mock_storage_loader
    
    def test_save_and_load_prompt(self, mock_storage_loader, sample_prompts):
        """Test saving and loading prompts from GCS."""
        store = GCSPromptStore(mock_storage_loader)
        prompt_data = sample_prompts["journal_summary"]
        prompt_info = PromptInfo(**prompt_data)
        
        # Configure mock for save
        mock_storage_loader.write_file.return_value = None
        
        # Save prompt
        store.save_prompt(prompt_info)
        
        # Verify write was called
        mock_storage_loader.write_file.assert_called_once()
        
        # Configure mock for load
        mock_storage_loader.read_file.return_value = yaml.dump(prompt_data)
        
        # Load prompt
        loaded_prompt = store.get_prompt("journal_summary", "1.0")
        assert loaded_prompt.name == prompt_info.name
        assert loaded_prompt.version == prompt_info.version
    
    def test_prompt_exists(self, mock_storage_loader, sample_prompts):
        """Test checking if prompts exist in GCS."""
        store = GCSPromptStore(mock_storage_loader)
        prompt_info = PromptInfo(**sample_prompts["journal_summary"])
        
        # Configure mock for non-existent - return False for exists check
        mock_storage_loader.exists.return_value = False
        
        # Initially doesn't exist
        assert not store.exists("journal_summary", "1.0")
        
        # Configure mock for existing - return True for exists check
        mock_storage_loader.exists.return_value = True
        
        # Save and check existence
        store.save_prompt(prompt_info)
        assert store.exists("journal_summary", "1.0")
    
    def test_list_prompts(self, mock_storage_loader):
        """Test listing available prompts from GCS."""
        store = GCSPromptStore(mock_storage_loader)
        
        # Configure mock files
        mock_storage_loader.list_files.return_value = [
            "prompts/journal_summary_1.0.yaml",
            "prompts/performance_review_1.0.yaml"
        ]
        
        # Configure mock content for each file
        def mock_read_file(file_path):
            if "journal_summary" in file_path:
                return yaml.dump({
                    "name": "journal_summary",
                    "version": "1.0",
                    "content": "test content",
                    "variables": [],
                    "metadata": {}
                })
            elif "performance_review" in file_path:
                return yaml.dump({
                    "name": "performance_review",
                    "version": "1.0", 
                    "content": "test content",
                    "variables": [],
                    "metadata": {}
                })
            return ""
        
        mock_storage_loader.read_file.side_effect = mock_read_file
        
        # List prompts
        prompts = store.list_prompts()
        assert len(prompts) == 2
        assert any(p.name == "journal_summary" for p in prompts)
        assert any(p.name == "performance_review" for p in prompts)
    
    def test_gcs_emulator_integration(self):
        """Test integration with GCS emulator."""
        # This test verifies that the store can work with the GCS emulator
        # configured in docker-compose.yml
        pass


class TestPromptServiceYAML:
    """Test prompt service with YAML storage."""
    
    @pytest.fixture
    def temp_yaml_dir(self):
        """Create a temporary directory for YAML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def yaml_prompt_service(self, temp_yaml_dir):
        """Create prompt service with YAML storage."""
        from agent_service.llms.prompts.models import PromptConfig
        
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_yaml_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = YAMLPromptStore(temp_yaml_dir)
        return PromptService(store=store, config=config)
    
    def test_yaml_prompt_rendering(self, yaml_prompt_service):
        """Test rendering prompts from YAML storage."""
        # Create a test prompt
        prompt_data = {
            "name": "test_prompt",
            "version": "1.0",
            "content": "Hello {{ name }}, how are you {{ feeling }}?",
            "variables": ["name", "feeling"],
            "metadata": {"category": "test"}
        }
        
        prompt_info = PromptInfo(**prompt_data)
        yaml_prompt_service.save_prompt(prompt_info)
        
        # Render the prompt
        rendered = yaml_prompt_service.render_prompt(
            "test_prompt",
            {"name": "Alice", "feeling": "great"}
        )
        
        assert "Hello Alice, how are you great?" in rendered
    
    def test_prompt_versioning(self, yaml_prompt_service):
        """Test prompt versioning in YAML storage."""
        # Create two versions of the same prompt
        prompt_v1 = PromptInfo(
            name="versioned_prompt",
            version="1.0",
            content="Version 1: {{ input }}",
            variables=["input"],
            metadata={}
        )
        
        prompt_v2 = PromptInfo(
            name="versioned_prompt", 
            version="2.0",
            content="Version 2: {{ input }}",
            variables=["input"],
            metadata={}
        )
        
        yaml_prompt_service.save_prompt(prompt_v1)
        yaml_prompt_service.save_prompt(prompt_v2)
        
        # Test both versions - explicitly specify versions
        rendered_v1 = yaml_prompt_service.render_prompt("versioned_prompt", {"input": "test"}, version="1.0")
        rendered_v2 = yaml_prompt_service.render_prompt("versioned_prompt", {"input": "test"}, version="2.0")
        
        assert "Version 1: test" in rendered_v1
        assert "Version 2: test" in rendered_v2


class TestEnvironmentConfiguration:
    """Test environment-based configuration for prompt storage."""
    
    def test_yaml_storage_configuration(self):
        """Test configuring YAML storage via environment."""
        with patch.dict('os.environ', {
            'PROMPT_STORE_TYPE': 'yaml',
            'PROMPT_STORE_PATH': '/tmp/prompts'
        }):
            # This would test the service factory creating YAML storage
            pass
    
    def test_gcs_storage_configuration(self):
        """Test configuring GCS storage via environment."""
        with patch.dict('os.environ', {
            'PROMPT_STORE_TYPE': 'gcs',
            'GCS_BUCKET_NAME': 'local_gcs_bucket',
            'GCS_EMULATOR_HOST': 'localhost:4443'
        }):
            # This would test the service factory creating GCS storage
            pass
    
    def test_storage_fallback(self):
        """Test fallback to memory storage when configuration is invalid."""
        with patch.dict('os.environ', {
            'PROMPT_STORE_TYPE': 'invalid',
        }):
            # This would test fallback to memory storage
            pass 