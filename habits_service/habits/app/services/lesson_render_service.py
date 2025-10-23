from __future__ import annotations

import re
from typing import List, Optional, Dict, Any
from .lesson_loader import LessonSegment, LessonLoader


class LessonRenderService:
    """Service for rendering segmented lesson content from markdown."""

    @staticmethod
    def extract_segments_from_markdown(markdown_content: str, segments: List[LessonSegment]) -> Dict[str, str]:
        """Extract content segments from markdown based on segment selectors.

        Args:
            markdown_content: The full markdown content
            segments: List of segment definitions

        Returns:
            Dictionary mapping segment ID to extracted content
        """
        results = {}

        for segment in segments:
            if segment.selector == "*":
                # Special case: full document
                results[segment.id] = markdown_content
            else:
                # Extract content for this segment
                content = LessonRenderService._extract_segment_content(
                    markdown_content, segment.selector
                )
                if content:
                    results[segment.id] = content.strip()

        return results

    @staticmethod
    def _extract_segment_content(markdown_content: str, selector: str) -> Optional[str]:
        """Extract content for a single segment based on its selector.

        Args:
            markdown_content: The full markdown content
            selector: The segment selector (e.g., "## Welcome", "## Tips")

        Returns:
            The extracted content, or None if not found
        """
        lines = markdown_content.split('\n')
        selector_pattern = LessonRenderService._create_selector_pattern(selector)

        start_line = None
        end_line = None

        for i, line in enumerate(lines):
            if selector_pattern.search(line):
                start_line = i
                break

        if start_line is None:
            return None

        # Find the next peer heading (same level or higher)
        current_level = LessonRenderService._get_heading_level(lines[start_line])
        if current_level == 0:
            return None

        # Look for the next heading of the same level or higher
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() and line.strip()[0] == '#':
                next_level = LessonRenderService._get_heading_level(line)
                if next_level <= current_level:
                    end_line = i
                    break

        if end_line is None:
            # No next heading found, take everything until the end
            end_line = len(lines)

        # Extract the content
        content_lines = lines[start_line:end_line]
        return '\n'.join(content_lines)

    @staticmethod
    def _create_selector_pattern(selector: str) -> re.Pattern[str]:
        """Create a regex pattern for matching the selector.

        Args:
            selector: The segment selector (e.g., "## Welcome", "## Tips")

        Returns:
            Compiled regex pattern
        """
        # Escape special regex characters
        escaped_selector = re.escape(selector)
        # Create pattern that matches the selector at start of line with optional whitespace
        pattern = f'^\\s*{escaped_selector}\\s*$'
        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def _get_heading_level(line: str) -> int:
        """Get the heading level from a markdown heading line.

        Args:
            line: The markdown line

        Returns:
            The heading level (1-6), or 0 if not a heading
        """
        stripped = line.strip()
        if not stripped.startswith('#'):
            return 0

        # Count the number of # characters
        level = 0
        for char in stripped:
            if char == '#':
                level += 1
            else:
                break

        return min(level, 6)  # Cap at 6 for safety

    @staticmethod
    def render_segments(
        markdown_content: str,
        segments: List[LessonSegment],
        segment_ids: Optional[List[str]] = None,
        default_segment: Optional[str] = None
    ) -> str:
        """Render lesson content for specified segments.

        Args:
            markdown_content: The full markdown content
            segments: List of available segments
            segment_ids: List of segment IDs to render, or None for default
            default_segment: Default segment ID to use when none specified

        Returns:
            Concatenated markdown content for the requested segments
        """
        if not segment_ids:
            # Use default segment or full content
            if default_segment:
                segment_ids = [default_segment]
            else:
                # Fallback to full content (special segment with selector "*")
                return markdown_content

        # Extract segment contents
        segment_contents = LessonRenderService.extract_segments_from_markdown(markdown_content, segments)

        # Collect content for requested segments
        rendered_parts = []
        for segment_id in segment_ids:
            if segment_id == "*":
                # Special case: full content
                rendered_parts.append(markdown_content)
                break
            elif segment_id in segment_contents:
                rendered_parts.append(segment_contents[segment_id])

        # If no segments were found, fallback to full content
        if not rendered_parts:
            return markdown_content

        # Concatenate all parts
        return '\n\n'.join(rendered_parts)

    @staticmethod
    def create_segments_from_markdown(markdown_content: str) -> List[LessonSegment]:
        """Auto-create segments from markdown headings.

        Args:
            markdown_content: The full markdown content

        Returns:
            List of LessonSegment objects based on headings
        """
        segments = []
        lines = markdown_content.split('\n')

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                heading_level = LessonRenderService._get_heading_level(line)
                if heading_level > 0:
                    # Create segment ID from heading text
                    heading_text = stripped[heading_level:].strip()
                    segment_id = LessonRenderService._create_segment_id(heading_text)

                    # Create selector from the heading
                    selector = stripped

                    segments.append(LessonSegment(
                        id=segment_id,
                        label=heading_text,
                        selector=selector
                    ))

        # Always add a "full" segment
        segments.append(LessonSegment(
            id="full",
            label="Full Lesson",
            selector="*"
        ))

        return segments

    @staticmethod
    def _create_segment_id(heading_text: str) -> str:
        """Create a segment ID from heading text.

        Args:
            heading_text: The heading text

        Returns:
            A clean segment ID
        """
        # Remove markdown formatting and create a clean ID
        clean_text = re.sub(r'[^\w\s-]', '', heading_text.lower())
        clean_text = re.sub(r'\s+', '-', clean_text.strip())
        return clean_text if clean_text else "segment"
