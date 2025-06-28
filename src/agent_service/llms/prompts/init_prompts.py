"""
Initialize prompt store with required prompts.

This script sets up the prompt store with the required prompts
for the LLM service to function properly.
"""

from pathlib import Path
from typing import Any, Dict

import yaml

from .models import PromptConfig, PromptInfo, StoreType
from .service import PromptService
from .stores.local import LocalPromptStore


def load_prompt_from_yaml(yaml_path: Path) -> PromptInfo:
    """
    Load a prompt from a YAML file.

    Args:
        yaml_path: Path to the YAML file

    Returns:
        PromptInfo object
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return PromptInfo(**data)


def init_prompt_store(store_path: str = "prompts") -> PromptService:
    """
    Initialize the prompt store with required prompts.

    Args:
        store_path: Path to store prompts

    Returns:
        Configured PromptService
    """
    # Create prompt service with local store
    config = PromptConfig(
        store_type=StoreType.LOCAL,
        store_path=store_path,
        enable_caching=True,
        cache_size=100,
        cache_ttl=3600,
    )

    store = LocalPromptStore(base_path=store_path)
    prompt_service = PromptService(store=store, config=config)

    # Load prompts from templates
    templates_dir = Path(__file__).parent / "migrations" / "templates"

    if templates_dir.exists():
        for yaml_file in templates_dir.glob("*.yaml"):
            try:
                prompt_info = load_prompt_from_yaml(yaml_file)

                # Save to store if it doesn't exist
                if not prompt_service.exists(prompt_info.name, prompt_info.version):
                    prompt_service.save_prompt(prompt_info)
                    print(
                        f"Initialized prompt: {prompt_info.name}:{prompt_info.version}"
                    )
                else:
                    print(
                        f"Prompt already exists: {prompt_info.name}:{prompt_info.version}"
                    )

            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

    return prompt_service


def create_default_prompts(store_path: str = "prompts") -> None:
    """
    Create default prompts if they don't exist.

    Args:
        store_path: Path to store prompts
    """
    # Create journal summary prompt
    journal_summary = PromptInfo(
        name="journal_summary",
        version="1.0",
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
            "description": "Generate a concise summary of journal entries",
        },
    )

    # Create performance review prompt
    performance_review = PromptInfo(
        name="performance_review",
        version="1.0",
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
            "output_format": "structured",
        },
    )

    # Initialize store and save prompts
    prompt_service = init_prompt_store(store_path)

    # Save prompts
    for prompt in [journal_summary, performance_review]:
        if not prompt_service.exists(prompt.name, prompt.version):
            prompt_service.save_prompt(prompt)
            print(f"Created prompt: {prompt.name}:{prompt.version}")
        else:
            print(f"Prompt already exists: {prompt.name}:{prompt.version}")


if __name__ == "__main__":
    """Run the prompt initialization."""
    import sys

    store_path = sys.argv[1] if len(sys.argv) > 1 else "prompts"
    create_default_prompts(store_path)
    print(f"Prompt store initialized at: {store_path}")
