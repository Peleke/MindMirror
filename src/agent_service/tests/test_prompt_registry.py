"""
Tests for prompt registry functionality.

These tests verify that the prompt registry correctly manages prompt templates,
handles versioning, validation, and provides proper error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from agent_service.llms.prompts.registry import PromptRegistry, PromptNotFoundError, PromptValidationError
from agent_service.llms.prompts.loader import PromptLoader, TemplateError


class TestPromptRegistry:
    """Test prompt registry functionality."""
    
    def test_prompt_registry_initialization(self):
        """Test that prompt registry initializes correctly."""
        registry = PromptRegistry()
        assert registry.prompts == {}
        assert registry.loader is not None
        assert isinstance(registry.loader, PromptLoader)
    
    def test_prompt_registry_with_custom_loader(self):
        """Test that prompt registry works with custom loader."""
        mock_loader = Mock(spec=PromptLoader)
        registry = PromptRegistry(loader=mock_loader)
        assert registry.loader == mock_loader
    
    def test_register_prompt_from_string(self):
        """Test registering a prompt from string."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}, how are you?"
        registry.register_prompt("greeting", prompt_content)
        
        assert "greeting" in registry.prompts
        assert registry.prompts["greeting"]["content"] == prompt_content
        assert registry.prompts["greeting"]["version"] == "1.0"
    
    def test_register_prompt_with_version(self):
        """Test registering a prompt with custom version."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}!"
        registry.register_prompt("greeting", prompt_content, version="2.0")
        
        assert registry.prompts["greeting"]["version"] == "2.0"
    
    def test_register_prompt_with_metadata(self):
        """Test registering a prompt with metadata."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}!"
        metadata = {"category": "greeting", "language": "en"}
        registry.register_prompt("greeting", prompt_content, metadata=metadata)
        
        assert registry.prompts["greeting"]["metadata"] == metadata
    
    def test_register_prompt_duplicate(self):
        """Test that registering duplicate prompt raises error."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}!"
        registry.register_prompt("greeting", prompt_content)
        
        with pytest.raises(ValueError, match="Prompt 'greeting' already registered"):
            registry.register_prompt("greeting", "Different content")
    
    def test_register_prompt_override(self):
        """Test that registering with override works."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}!"
        registry.register_prompt("greeting", prompt_content)
        
        new_content = "Hi {{ name }}!"
        registry.register_prompt("greeting", new_content, override=True)
        
        assert registry.prompts["greeting"]["content"] == new_content
    
    def test_get_prompt(self):
        """Test getting a registered prompt."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}!"
        registry.register_prompt("greeting", prompt_content)
        
        prompt = registry.get_prompt("greeting")
        
        assert prompt["content"] == prompt_content
        assert prompt["version"] == "1.0"
    
    def test_get_prompt_not_found(self):
        """Test that getting non-existent prompt raises error."""
        registry = PromptRegistry()
        
        with pytest.raises(PromptNotFoundError, match="Prompt 'missing' not found"):
            registry.get_prompt("missing")
    
    def test_render_prompt(self):
        """Test rendering a prompt with variables."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}! You have {{ count }} messages."
        registry.register_prompt("greeting", prompt_content)
        
        result = registry.render_prompt("greeting", name="Alice", count=3)
        
        assert result == "Hello Alice! You have 3 messages."
    
    def test_render_prompt_with_invalid_template(self):
        """Test that invalid template raises error."""
        registry = PromptRegistry()
        
        invalid_content = "Hello {{ name }}, {% if %} invalid syntax"
        registry.register_prompt("invalid", invalid_content)
        
        with pytest.raises(PromptValidationError, match="Invalid template syntax"):
            registry.render_prompt("invalid", name="Alice")
    
    def test_render_prompt_missing_variables(self):
        """Test that missing variables are handled gracefully."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}! You have {{ count }} messages."
        registry.register_prompt("greeting", prompt_content)
        
        # Should handle missing variables gracefully
        result = registry.render_prompt("greeting", name="Alice")
        
        assert "Hello Alice!" in result
        assert "You have  messages." in result  # count is empty
    
    def test_list_prompts(self):
        """Test listing all registered prompts."""
        registry = PromptRegistry()
        
        registry.register_prompt("greeting", "Hello {{ name }}!")
        registry.register_prompt("farewell", "Goodbye {{ name }}!")
        registry.register_prompt("welcome", "Welcome {{ name }}!")
        
        prompts = registry.list_prompts()
        
        assert "greeting" in prompts
        assert "farewell" in prompts
        assert "welcome" in prompts
        assert len(prompts) == 3
    
    def test_get_prompt_info(self):
        """Test getting detailed prompt information."""
        registry = PromptRegistry()
        
        prompt_content = "Hello {{ name }}!"
        metadata = {"category": "greeting", "language": "en"}
        registry.register_prompt("greeting", prompt_content, metadata=metadata)
        
        info = registry.get_prompt_info("greeting")
        
        assert info["name"] == "greeting"
        assert info["content"] == prompt_content
        assert info["version"] == "1.0"
        assert info["metadata"] == metadata
        assert "name" in info["variables"]
    
    def test_validate_prompt(self):
        """Test prompt validation."""
        registry = PromptRegistry()
        
        # Valid prompt
        valid_content = "Hello {{ name }}!"
        assert registry.validate_prompt(valid_content) is True
        
        # Invalid prompt
        invalid_content = "Hello {{ name }}, {% if %} invalid"
        assert registry.validate_prompt(invalid_content) is False
    
    def test_update_prompt(self):
        """Test updating an existing prompt."""
        registry = PromptRegistry()
        
        original_content = "Hello {{ name }}!"
        registry.register_prompt("greeting", original_content)
        
        new_content = "Hi {{ name }}!"
        registry.update_prompt("greeting", new_content)
        
        assert registry.prompts["greeting"]["content"] == new_content
        assert registry.prompts["greeting"]["version"] == "1.1"
    
    def test_update_prompt_not_found(self):
        """Test that updating non-existent prompt raises error."""
        registry = PromptRegistry()
        
        with pytest.raises(PromptNotFoundError, match="Prompt 'missing' not found"):
            registry.update_prompt("missing", "New content")
    
    def test_delete_prompt(self):
        """Test deleting a prompt."""
        registry = PromptRegistry()
        
        registry.register_prompt("greeting", "Hello {{ name }}!")
        assert "greeting" in registry.prompts
        
        registry.delete_prompt("greeting")
        assert "greeting" not in registry.prompts
    
    def test_delete_prompt_not_found(self):
        """Test that deleting non-existent prompt raises error."""
        registry = PromptRegistry()
        
        with pytest.raises(PromptNotFoundError, match="Prompt 'missing' not found"):
            registry.delete_prompt("missing")
    
    def test_search_prompts(self):
        """Test searching prompts by content or metadata."""
        registry = PromptRegistry()
        
        registry.register_prompt("greeting", "Hello {{ name }}!", metadata={"category": "greeting"})
        registry.register_prompt("farewell", "Goodbye {{ name }}!", metadata={"category": "farewell"})
        registry.register_prompt("welcome", "Welcome {{ name }}!", metadata={"category": "greeting"})
        
        # Search by content
        results = registry.search_prompts("Hello")
        assert len(results) == 1
        assert "greeting" in results
        
        # Search by metadata
        results = registry.search_prompts(metadata={"category": "greeting"})
        assert len(results) == 2
        assert "greeting" in results
        assert "welcome" in results


class TestPromptRegistryIntegration:
    """Integration tests for prompt registry."""
    
    def test_load_prompts_from_directory(self):
        """Test loading prompts from directory."""
        registry = PromptRegistry()
        
        # Mock directory structure
        mock_templates = {
            "greeting.j2": "Hello {{ name }}!",
            "farewell.j2": "Goodbye {{ name }}!",
            "welcome.j2": "Welcome {{ name }} to {{ service }}!"
        }
        
        with patch.object(registry.loader, 'load_templates_from_directory') as mock_load:
            mock_load.return_value = {
                name.replace('.j2', ''): Mock() for name in mock_templates.keys()
            }
            
            with patch.object(registry.loader, 'get_template') as mock_get_template:
                def mock_template_side_effect(template_name):
                    mock_template = Mock()
                    mock_template.source = mock_templates[f"{template_name}.j2"]
                    return mock_template
                
                mock_get_template.side_effect = mock_template_side_effect
                
                registry.load_prompts_from_directory("/tmp/prompts")
                
                assert "greeting" in registry.prompts
                assert "farewell" in registry.prompts
                assert "welcome" in registry.prompts
    
    def test_prompt_versioning(self):
        """Test prompt versioning functionality."""
        registry = PromptRegistry()
        
        # Register initial version
        registry.register_prompt("greeting", "Hello {{ name }}!", version="1.0")
        
        # Update to new version
        registry.update_prompt("greeting", "Hi {{ name }}!", version="2.0")
        
        # Check version history
        assert registry.prompts["greeting"]["version"] == "2.0"
        
        # Get specific version (if implemented)
        # This would require additional versioning functionality
    
    def test_prompt_categories(self):
        """Test prompt categorization."""
        registry = PromptRegistry()
        
        registry.register_prompt("greeting", "Hello {{ name }}!", metadata={"category": "greeting"})
        registry.register_prompt("farewell", "Goodbye {{ name }}!", metadata={"category": "farewell"})
        registry.register_prompt("welcome", "Welcome {{ name }}!", metadata={"category": "greeting"})
        
        greeting_prompts = registry.get_prompts_by_category("greeting")
        assert len(greeting_prompts) == 2
        assert "greeting" in greeting_prompts
        assert "welcome" in greeting_prompts
    
    def test_prompt_export_import(self):
        """Test prompt export and import functionality."""
        registry = PromptRegistry()
        
        registry.register_prompt("greeting", "Hello {{ name }}!", metadata={"category": "greeting"})
        registry.register_prompt("farewell", "Goodbye {{ name }}!", metadata={"category": "farewell"})
        
        # Export prompts
        exported = registry.export_prompts()
        
        # Create new registry and import
        new_registry = PromptRegistry()
        new_registry.import_prompts(exported)
        
        assert "greeting" in new_registry.prompts
        assert "farewell" in new_registry.prompts
        assert new_registry.prompts["greeting"]["content"] == "Hello {{ name }}!"


class TestPromptRegistryErrorHandling:
    """Test error handling in prompt registry."""
    
    def test_register_invalid_prompt(self):
        """Test that invalid prompt registration is handled."""
        registry = PromptRegistry()
        
        invalid_content = "Hello {{ name }}, {% if %} invalid syntax"
        
        with pytest.raises(PromptValidationError, match="Invalid template syntax"):
            registry.register_prompt("invalid", invalid_content, validate=True)
    
    def test_render_with_template_error(self):
        """Test that template rendering errors are handled."""
        registry = PromptRegistry()
        
        # Register a prompt that will cause rendering error
        prompt_content = "Hello {{ name }}, you have {{ count }} messages."
        registry.register_prompt("greeting", prompt_content)
        
        # This should handle the missing variable gracefully
        result = registry.render_prompt("greeting", name="Alice")
        assert "Hello Alice" in result
    
    def test_loader_error_propagation(self):
        """Test that loader errors are properly propagated."""
        registry = PromptRegistry()
        
        with patch.object(registry.loader, 'load_template_from_string') as mock_load:
            mock_load.side_effect = TemplateError("Loader error")
            
            with pytest.raises(TemplateError, match="Loader error"):
                registry.register_prompt("test", "Hello {{ name }}") 