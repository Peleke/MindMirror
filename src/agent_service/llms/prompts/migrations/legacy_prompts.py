"""
Legacy prompt extraction utilities.

This module provides tools for extracting hardcoded prompts
from existing services and converting them to the new format.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..models import PromptInfo
from ..exceptions import PromptValidationError


@dataclass
class LegacyPrompt:
    """Represents a legacy prompt extracted from hardcoded strings."""
    
    name: str
    content: str
    variables: List[str]
    metadata: Dict[str, Any]
    source_file: str
    source_method: str


class LegacyPromptExtractor:
    """
    Extractor for hardcoded prompts from existing services.
    
    This class provides methods to extract and convert hardcoded
    prompts to the new PromptInfo format.
    """
    
    def __init__(self):
        """Initialize the extractor."""
        self.extracted_prompts: List[LegacyPrompt] = []
    
    def extract_from_llm_service(self) -> List[LegacyPrompt]:
        """
        Extract hardcoded prompts from LLMService.
        
        Returns:
            List of extracted legacy prompts
        """
        prompts = []
        
        # Journal Summary Prompt
        journal_summary_prompt = LegacyPrompt(
            name="journal_summary",
            content="""As an AI companion, your task is to provide a brief, insightful summary based on the user's recent journal entries.
Analyze the following entries and identify the main themes, recurring thoughts, or significant events.
The summary should be gentle, encouraging, and forward-looking, like a friendly observer.
Do not be overly conversational or ask questions. Focus on synthesizing the information into a cohesive insight.

Journal Entries:
{{ content_block }}

Synthesize these entries into a single, concise paragraph of 2-4 sentences.""",
            variables=["content_block"],
            metadata={
                "category": "journal",
                "type": "summary",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 250,
                "description": "Generate a concise summary of journal entries"
            },
            source_file="src/agent_service/services/llm_service.py",
            source_method="get_journal_summary"
        )
        prompts.append(journal_summary_prompt)
        
        # Performance Review Prompt
        performance_review_prompt = LegacyPrompt(
            name="performance_review",
            content="""Analyze the following journal entries from the past two weeks to generate a performance review.
The user is focused on self-improvement. Your task is to identify one key success and one primary area for improvement.
Based on this analysis, create a new, targeted journaling prompt to help them reflect further.

Journal Entries:
{{ content_block }}

Based on these entries, provide the following in a structured format:
1.  **Key Success**: A specific, positive achievement or consistent behavior.
2.  **Improvement Area**: A constructive, actionable area where the user can focus their efforts.
3.  **Journal Prompt**: A new, open-ended question that encourages reflection on the improvement area.

Please format your response as follows:
SUCCESS: [Your identified key success here]
IMPROVEMENT: [Your identified improvement area here]
PROMPT: [Your generated journal prompt here]""",
            variables=["content_block"],
            metadata={
                "category": "journal",
                "type": "review",
                "model": "gpt-4o",
                "temperature": 0.5,
                "max_tokens": 500,
                "description": "Generate a structured performance review from journal entries",
                "output_format": "structured"
            },
            source_file="src/agent_service/services/llm_service.py",
            source_method="generate_performance_review"
        )
        prompts.append(performance_review_prompt)
        
        self.extracted_prompts.extend(prompts)
        return prompts
    
    def extract_from_string(self, content: str, name: str, 
                           source_file: str = "unknown", 
                           source_method: str = "unknown",
                           metadata: Optional[Dict[str, Any]] = None) -> LegacyPrompt:
        """
        Extract a prompt from a string and convert to template format.
        
        Args:
            content: The hardcoded prompt content
            name: Name for the prompt
            source_file: Source file path
            source_method: Source method name
            metadata: Additional metadata
            
        Returns:
            LegacyPrompt object
        """
        # Convert f-string style variables to Jinja2 template variables
        template_content = self._convert_fstring_to_template(content)
        
        # Extract variables from the template
        variables = self._extract_template_variables(template_content)
        
        # Create metadata
        prompt_metadata = metadata or {}
        prompt_metadata.update({
            "source_file": source_file,
            "source_method": source_method,
            "extracted_at": "legacy_migration"
        })
        
        legacy_prompt = LegacyPrompt(
            name=name,
            content=template_content,
            variables=variables,
            metadata=prompt_metadata,
            source_file=source_file,
            source_method=source_method
        )
        
        self.extracted_prompts.append(legacy_prompt)
        return legacy_prompt
    
    def _convert_fstring_to_template(self, content: str) -> str:
        """
        Convert f-string style variables to Jinja2 template variables.
        
        Args:
            content: Content with f-string variables
            
        Returns:
            Content with Jinja2 template variables
        """
        # Replace f-string variables with Jinja2 template variables
        # This is a simple conversion - more complex cases may need manual review
        
        # Replace {variable} with {{ variable }}
        template_content = re.sub(r'\{(\w+)\}', r'{{ \1 }}', content)
        
        # Handle cases where we have literal braces that shouldn't be converted
        # This is a simplified approach - in practice, you might need more sophisticated parsing
        
        return template_content
    
    def _extract_template_variables(self, template_content: str) -> List[str]:
        """
        Extract variable names from Jinja2 template.
        
        Args:
            template_content: Template content
            
        Returns:
            List of variable names
        """
        # Simple regex to find Jinja2 variables
        variable_pattern = r'\{\{\s*(\w+)\s*\}\}'
        matches = re.findall(variable_pattern, template_content)
        return list(set(matches))  # Remove duplicates
    
    def convert_to_prompt_info(self, legacy_prompt: LegacyPrompt, version: str = "1.0") -> PromptInfo:
        """
        Convert a LegacyPrompt to PromptInfo.
        
        Args:
            legacy_prompt: The legacy prompt to convert
            version: Version for the new prompt
            
        Returns:
            PromptInfo object
        """
        return PromptInfo(
            name=legacy_prompt.name,
            version=version,
            content=legacy_prompt.content,
            metadata=legacy_prompt.metadata,
            variables=legacy_prompt.variables
        )
    
    def get_all_extracted_prompts(self) -> List[LegacyPrompt]:
        """Get all extracted prompts."""
        return self.extracted_prompts.copy()
    
    def clear_extracted_prompts(self) -> None:
        """Clear all extracted prompts."""
        self.extracted_prompts.clear()
    
    def validate_extracted_prompts(self) -> List[str]:
        """
        Validate all extracted prompts.
        
        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []
        
        for prompt in self.extracted_prompts:
            try:
                # Try to create PromptInfo to validate
                self.convert_to_prompt_info(prompt)
            except PromptValidationError as e:
                errors.append(f"Prompt '{prompt.name}': {str(e)}")
            except Exception as e:
                errors.append(f"Prompt '{prompt.name}': Unexpected error - {str(e)}")
        
        return errors 