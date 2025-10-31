import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from habits_service.app.services.lesson_render_service import LessonRenderService
from habits_service.app.services.lesson_loader import LessonSegment


class TestLessonRenderService:
    def test_extract_segment_content_single_segment(self):
        """Test extracting content for a single segment."""
        markdown = """# Main Title

## Introduction

This is the intro section content.

## Tips

This is the tips section content.

## Conclusion

This is the conclusion.
"""

        segments = [
            LessonSegment(id="intro", label="Introduction", selector="## Introduction"),
            LessonSegment(id="tips", label="Tips", selector="## Tips")
        ]

        result = LessonRenderService.extract_segments_from_markdown(markdown, segments)

        assert "intro" in result
        assert "tips" in result
        assert result["intro"] == "## Introduction\n\nThis is the intro section content."
        assert result["tips"] == "## Tips\n\nThis is the tips section content."

    def test_extract_segment_full_content(self):
        """Test extracting full content with wildcard selector."""
        markdown = """# Main Title

## Introduction

This is the intro.

## Tips

This is tips.
"""

        segments = [
            LessonSegment(id="full", label="Full Lesson", selector="*")
        ]

        result = LessonRenderService.extract_segments_from_markdown(markdown, segments)

        assert result["full"] == markdown

    def test_render_segments_single_segment(self):
        """Test rendering a single segment."""
        markdown = """# Main Title

## Introduction

This is the intro section content.

## Tips

This is the tips section content.
"""

        segments = [
            LessonSegment(id="intro", label="Introduction", selector="## Introduction"),
            LessonSegment(id="tips", label="Tips", selector="## Tips")
        ]

        result = LessonRenderService.render_segments(
            markdown, segments, ["intro"], "intro"
        )

        assert result.strip() == "## Introduction\n\nThis is the intro section content."

    def test_render_segments_multiple_segments(self):
        """Test rendering multiple segments concatenated."""
        markdown = """# Main Title

## Introduction

This is the intro.

## Tips

These are tips.

## Conclusion

This is the end.
"""

        segments = [
            LessonSegment(id="intro", label="Introduction", selector="## Introduction"),
            LessonSegment(id="tips", label="Tips", selector="## Tips"),
            LessonSegment(id="conclusion", label="Conclusion", selector="## Conclusion")
        ]

        result = LessonRenderService.render_segments(
            markdown, segments, ["intro", "tips"], "intro"
        )

        expected = "## Introduction\n\nThis is the intro.\n\n\n## Tips\n\nThese are tips."
        assert result == expected

    def test_render_segments_default_segment(self):
        """Test rendering with default segment when none specified."""
        markdown = """# Main Title

## Introduction

This is the intro.

## Tips

These are tips.
"""

        segments = [
            LessonSegment(id="intro", label="Introduction", selector="## Introduction"),
            LessonSegment(id="tips", label="Tips", selector="## Tips")
        ]

        result = LessonRenderService.render_segments(
            markdown, segments, None, "tips"
        )

        assert result.strip() == "## Tips\n\nThese are tips."

    def test_create_segments_from_markdown(self):
        """Test auto-creating segments from markdown headings."""
        markdown = """# Main Title

## Introduction

This is the intro.

## Tips for Success

These are tips.

### Sub-tip

More specific tip.

## Conclusion

This is the end.
"""

        segments = LessonRenderService.create_segments_from_markdown(markdown)

        # Should find the main headings and create segments
        assert len(segments) >= 4  # intro, tips, conclusion, plus full

        segment_ids = [s.id for s in segments]
        assert "introduction" in segment_ids or "intro" in segment_ids
        assert "tips-for-success" in segment_ids or "tips" in segment_ids
        assert "conclusion" in segment_ids
        assert "full" in segment_ids

    def test_create_segment_id(self):
        """Test creating clean segment IDs from headings."""
        assert LessonRenderService._create_segment_id("Introduction") == "introduction"
        assert LessonRenderService._create_segment_id("Tips for Success") == "tips-for-success"
        assert LessonRenderService._create_segment_id("Getting Started (Day 1)") == "getting-started-day-1"
        assert LessonRenderService._create_segment_id("  Special  Heading  ") == "special-heading"
