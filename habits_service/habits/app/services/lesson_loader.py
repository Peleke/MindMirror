from __future__ import annotations

import re
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class LessonSegment:
    id: str
    label: str
    selector: str


@dataclass
class LessonTemplateData:
    slug: str
    title: str
    markdown_content: str
    summary: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    est_read_minutes: Optional[int] = None
    subtitle: Optional[str] = None
    hero_image_url: Optional[str] = None
    segments: Optional[List[LessonSegment]] = None
    default_segment: Optional[str] = None


class LessonLoader:
    """Service for loading and parsing lesson templates with YAML frontmatter."""

    @staticmethod
    def parse_yaml_frontmatter(markdown_content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content.

        Args:
            markdown_content: The raw markdown content with optional YAML frontmatter

        Returns:
            Tuple of (frontmatter_dict, content_without_frontmatter)
        """
        # Check if content starts with YAML frontmatter
        if not markdown_content.startswith('---'):
            return {}, markdown_content

        # Find the end of frontmatter (next '---')
        lines = markdown_content.split('\n')
        frontmatter_end = None

        for i, line in enumerate(lines[1:], 1):  # Skip first line
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end is None:
            # No closing delimiter found, treat as regular content
            return {}, markdown_content

        # Extract frontmatter
        frontmatter_lines = lines[1:frontmatter_end]
        frontmatter_text = '\n'.join(frontmatter_lines)

        try:
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError as e:
            # If YAML parsing fails, treat as regular content
            return {}, markdown_content

        # Return remaining content
        remaining_content = '\n'.join(lines[frontmatter_end + 1:])

        # Remove leading newline if present
        if remaining_content.startswith('\n'):
            remaining_content = remaining_content[1:]

        return frontmatter, remaining_content

    @staticmethod
    def parse_segments_from_frontmatter(frontmatter: Dict[str, Any]) -> Optional[List[LessonSegment]]:
        """Parse segments array from frontmatter.

        Args:
            frontmatter: The parsed frontmatter dictionary

        Returns:
            List of LessonSegment objects, or None if not found
        """
        segments_data = frontmatter.get('segments')
        if not segments_data:
            return None

        segments = []
        for segment_data in segments_data:
            if isinstance(segment_data, dict):
                segment_id = segment_data.get('id')
                label = segment_data.get('label')
                selector = segment_data.get('selector')

                if segment_id and label and selector:
                    segments.append(LessonSegment(
                        id=segment_id,
                        label=label,
                        selector=selector
                    ))

        return segments if segments else None

    @classmethod
    def load_from_markdown(cls, slug: str, markdown_content: str) -> LessonTemplateData:
        """Load lesson template data from markdown content with YAML frontmatter.

        Args:
            slug: The lesson template slug
            markdown_content: The raw markdown content

        Returns:
            LessonTemplateData object with parsed information
        """
        frontmatter, content = cls.parse_yaml_frontmatter(markdown_content)

        # Parse segments
        segments = cls.parse_segments_from_frontmatter(frontmatter)

        # Extract metadata
        return LessonTemplateData(
            slug=slug,
            title=frontmatter.get('title', 'Untitled Lesson'),
            markdown_content=content,
            summary=frontmatter.get('summary'),
            tags=frontmatter.get('tags'),
            est_read_minutes=frontmatter.get('est_read_minutes'),
            subtitle=frontmatter.get('subtitle'),
            hero_image_url=frontmatter.get('hero_image_url'),
            segments=segments,
            default_segment=frontmatter.get('defaultSegment') or frontmatter.get('default_segment'),
        )

    @staticmethod
    def segments_to_json(segments: Optional[List[LessonSegment]]) -> Optional[List[Dict[str, str]]]:
        """Convert segments list to JSON-serializable format.

        Args:
            segments: List of LessonSegment objects

        Returns:
            List of dictionaries suitable for JSON storage
        """
        if not segments:
            return None

        return [
            {
                'id': segment.id,
                'label': segment.label,
                'selector': segment.selector
            }
            for segment in segments
        ]

    @staticmethod
    def segments_from_json(segments_json: Optional[List[Dict[str, str]]]) -> Optional[List[LessonSegment]]:
        """Convert JSON segments back to LessonSegment objects.

        Args:
            segments_json: List of segment dictionaries from JSON

        Returns:
            List of LessonSegment objects
        """
        if not segments_json:
            return None

        return [
            LessonSegment(
                id=segment['id'],
                label=segment['label'],
                selector=segment['selector']
            )
            for segment in segments_json
        ]
