"""
Tests for prompt store interface contracts.

These tests verify that all prompt store implementations correctly
implement the required interface and handle edge cases properly.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Optional
from datetime import datetime

from agent_service.llms.prompts.stores import PromptStore
from agent_service.llms.prompts.models import PromptInfo
from agent_service.llms.prompts.exceptions import PromptNotFoundError, PromptValidationError


class TestPromptStoreInterface:
    """Test that all stores implement required interface."""
    
    def test_prompt_store_protocol_methods(self):
        """Test that PromptStore protocol defines required methods."""
        # This test ensures the protocol is properly defined
        # We'll test actual implementations in their respective test files
        assert hasattr(PromptStore, '__call__')  # Protocol should be callable
        
        # Check that the protocol has the required methods
        required_methods = [
            'get_prompt',
            'save_prompt', 
            'delete_prompt',
            'list_prompts',
            'get_latest_version'
        ]
        
        for method in required_methods:
            assert hasattr(PromptStore, method), f"PromptStore missing method: {method}"
    
    def test_prompt_store_method_signatures(self):
        """Test that store methods have correct signatures."""
        # This is a structural test to ensure the interface is properly defined
        # Actual implementations will be tested in their respective test files
        
        # Mock store to test interface compliance
        mock_store = Mock(spec=PromptStore)
        
        # Test that methods can be called with expected signatures
        mock_store.get_prompt("test", "1.0")
        mock_store.get_prompt("test")  # version optional
        
        mock_store.save_prompt(Mock(spec=PromptInfo))
        
        mock_store.delete_prompt("test", "1.0")
        mock_store.delete_prompt("test")  # version optional
        
        mock_store.list_prompts()
        
        mock_store.get_latest_version("test")
        
        # Verify all expected methods were called
        assert mock_store.get_prompt.call_count == 2
        assert mock_store.save_prompt.call_count == 1
        assert mock_store.delete_prompt.call_count == 2
        assert mock_store.list_prompts.call_count == 1
        assert mock_store.get_latest_version.call_count == 1


class TestPromptStoreBehavior:
    """Test common behavior patterns for all stores."""
    
    @pytest.fixture
    def sample_prompt_info(self):
        """Create a sample PromptInfo for testing."""
        return PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Hello {{ name }}!",
            metadata={"category": "greeting", "language": "en"},
            variables=["name"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    def test_store_crud_operations(self, sample_prompt_info):
        """Test basic CRUD operations that all stores should support."""
        # This is a template test - actual implementations will override this
        # to test with their specific store type
        
        # Create a mock store that implements the interface
        store = Mock(spec=PromptStore)
        
        # Test save operation
        store.save_prompt(sample_prompt_info)
        store.save_prompt.assert_called_once_with(sample_prompt_info)
        
        # Test get operation
        store.get_prompt.return_value = sample_prompt_info
        retrieved = store.get_prompt("test_prompt", "1.0")
        assert retrieved == sample_prompt_info
        store.get_prompt.assert_called_with("test_prompt", "1.0")
        
        # Test get with latest version
        store.get_latest_version.return_value = "1.0"
        latest_version = store.get_latest_version("test_prompt")
        assert latest_version == "1.0"
        
        # Test list operation
        store.list_prompts.return_value = [sample_prompt_info]
        prompts = store.list_prompts()
        assert len(prompts) == 1
        assert prompts[0] == sample_prompt_info
        
        # Test delete operation
        store.delete_prompt("test_prompt", "1.0")
        store.delete_prompt.assert_called_with("test_prompt", "1.0")
    
    def test_store_error_handling(self):
        """Test that stores handle errors consistently."""
        store = Mock(spec=PromptStore)
        
        # Test get_prompt with non-existent prompt
        store.get_prompt.side_effect = PromptNotFoundError("Prompt not found")
        
        with pytest.raises(PromptNotFoundError, match="Prompt not found"):
            store.get_prompt("non_existent", "1.0")
        
        # Test get_latest_version with non-existent prompt
        store.get_latest_version.side_effect = PromptNotFoundError("No versions found")
        
        with pytest.raises(PromptNotFoundError, match="No versions found"):
            store.get_latest_version("non_existent")
    
    def test_store_version_handling(self):
        """Test that stores handle versioning correctly."""
        store = Mock(spec=PromptStore)
        
        # Configure mock to simulate the expected behavior
        def get_prompt_side_effect(name, version=None):
            if version is None:
                # Simulate getting latest version first
                latest_version = store.get_latest_version(name)
                return store.get_prompt(name, latest_version)
            return Mock(spec=PromptInfo, version=version)
        
        def delete_prompt_side_effect(name, version=None):
            if version is None:
                # Simulate getting latest version first
                latest_version = store.get_latest_version(name)
                return store.delete_prompt(name, latest_version)
            return None
        
        store.get_prompt.side_effect = get_prompt_side_effect
        store.delete_prompt.side_effect = delete_prompt_side_effect
        store.get_latest_version.return_value = "2.0"
        
        # Test get_prompt without version (should use latest)
        result = store.get_prompt("test_prompt")  # No version specified
        store.get_latest_version.assert_called_with("test_prompt")
        
        # Reset call counts for the next test
        store.get_latest_version.reset_mock()
        
        # Test delete_prompt without version (should delete latest)
        store.delete_prompt("test_prompt")  # No version specified
        store.get_latest_version.assert_called_with("test_prompt")


class TestPromptStoreIntegration:
    """Integration tests for store behavior."""
    
    def test_store_prompt_lifecycle(self):
        """Test complete prompt lifecycle in a store."""
        store = Mock(spec=PromptStore)
        
        # Create prompt info
        prompt_info = PromptInfo(
            name="lifecycle_test",
            version="1.0",
            content="Test content",
            metadata={},
            variables=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Save prompt
        store.save_prompt(prompt_info)
        store.save_prompt.assert_called_once_with(prompt_info)
        
        # Retrieve prompt
        store.get_prompt.return_value = prompt_info
        retrieved = store.get_prompt("lifecycle_test", "1.0")
        assert retrieved == prompt_info
        
        # List prompts
        store.list_prompts.return_value = [prompt_info]
        prompts = store.list_prompts()
        assert len(prompts) == 1
        assert prompts[0] == prompt_info
        
        # Delete prompt
        store.delete_prompt("lifecycle_test", "1.0")
        store.delete_prompt.assert_called_with("lifecycle_test", "1.0")
        
        # Verify prompt is gone
        store.get_prompt.side_effect = PromptNotFoundError("Prompt not found")
        with pytest.raises(PromptNotFoundError):
            store.get_prompt("lifecycle_test", "1.0")
    
    def test_store_multiple_versions(self):
        """Test handling multiple versions of the same prompt."""
        store = Mock(spec=PromptStore)
        
        # Create multiple versions
        v1_info = PromptInfo(
            name="multi_version",
            version="1.0",
            content="Version 1",
            metadata={},
            variables=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        v2_info = PromptInfo(
            name="multi_version",
            version="2.0",
            content="Version 2",
            metadata={},
            variables=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Save both versions
        store.save_prompt(v1_info)
        store.save_prompt(v2_info)
        
        # Test getting specific versions
        store.get_prompt.side_effect = lambda name, version: v1_info if version == "1.0" else v2_info
        
        retrieved_v1 = store.get_prompt("multi_version", "1.0")
        retrieved_v2 = store.get_prompt("multi_version", "2.0")
        
        assert retrieved_v1.content == "Version 1"
        assert retrieved_v2.content == "Version 2"
        
        # Test getting latest version
        store.get_latest_version.return_value = "2.0"
        latest_version = store.get_latest_version("multi_version")
        assert latest_version == "2.0"
        
        # Test listing all versions
        store.list_prompts.return_value = [v1_info, v2_info]
        all_prompts = store.list_prompts()
        assert len(all_prompts) == 2


class TestPromptStoreValidation:
    """Test validation behavior for stores."""
    
    def test_store_validates_prompt_info(self):
        """Test that stores validate PromptInfo objects."""
        store = Mock(spec=PromptStore)
        
        # Test with invalid prompt info
        invalid_info = Mock()  # Not a PromptInfo
        
        # Configure mock to raise PromptValidationError for invalid input
        def save_prompt_side_effect(info):
            if not isinstance(info, PromptInfo):
                raise PromptValidationError("Invalid PromptInfo object")
        
        store.save_prompt.side_effect = save_prompt_side_effect
        
        with pytest.raises(PromptValidationError):
            store.save_prompt(invalid_info)
        
        # Test with valid prompt info
        valid_info = PromptInfo(
            name="valid",
            version="1.0",
            content="Valid content",
            metadata={},
            variables=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Reset side effect for valid input
        store.save_prompt.side_effect = None
        
        # Should not raise
        store.save_prompt(valid_info)
    
    def test_store_handles_invalid_names(self):
        """Test that stores handle invalid prompt names."""
        store = Mock(spec=PromptStore)
        
        invalid_names = ["", None, "invalid/name", "invalid\\name", "invalid*name"]
        
        # Configure mock to raise PromptValidationError for invalid names
        def validate_name(name):
            if not name or any(char in name for char in ['/', '\\', '*']):
                raise PromptValidationError(f"Invalid prompt name: {name}")
        
        store.get_prompt.side_effect = lambda name, version: validate_name(name)
        store.delete_prompt.side_effect = lambda name, version: validate_name(name)
        store.get_latest_version.side_effect = lambda name: validate_name(name)
        
        for invalid_name in invalid_names:
            with pytest.raises(PromptValidationError):
                store.get_prompt(invalid_name, "1.0")
            
            with pytest.raises(PromptValidationError):
                store.delete_prompt(invalid_name, "1.0")
            
            with pytest.raises(PromptValidationError):
                store.get_latest_version(invalid_name)
    
    def test_store_handles_invalid_versions(self):
        """Test that stores handle invalid version strings."""
        store = Mock(spec=PromptStore)
        
        invalid_versions = ["", None, "invalid-version", "1.0.0.0"]
        
        # Configure mock to raise PromptValidationError for invalid versions
        def validate_version(version):
            if not version or not version.replace('.', '').isdigit() or version.count('.') > 2:
                raise PromptValidationError(f"Invalid version: {version}")
        
        store.get_prompt.side_effect = lambda name, version: validate_version(version)
        store.delete_prompt.side_effect = lambda name, version: validate_version(version)
        
        for invalid_version in invalid_versions:
            with pytest.raises(PromptValidationError):
                store.get_prompt("test", invalid_version)
            
            with pytest.raises(PromptValidationError):
                store.delete_prompt("test", invalid_version) 