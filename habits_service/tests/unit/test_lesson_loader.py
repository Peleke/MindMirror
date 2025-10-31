import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from habits_service.app.services.lesson_loader import LessonLoader, LessonSegment


class TestLessonLoader:
    def test_parse_yaml_frontmatter_simple(self):
        """Test parsing YAML frontmatter from markdown."""
        markdown = """---
title: Test Lesson
summary: A test lesson
segments:
  - id: intro
    label: Introduction
    selector: "## Introduction"
  - id: full
    label: Full Lesson
    selector: "*"
---

# Test Lesson

This is the content.

## Introduction

This is the intro section.
"""

        frontmatter, content = LessonLoader.parse_yaml_frontmatter(markdown)

        assert frontmatter["title"] == "Test Lesson"
        assert frontmatter["summary"] == "A test lesson"
        assert frontmatter["segments"] == [
            {"id": "intro", "label": "Introduction", "selector": "## Introduction"},
            {"id": "full", "label": "Full Lesson", "selector": "*"}
        ]
        assert content == "# Test Lesson\n\nThis is the content.\n\n## Introduction\n\nThis is the intro section.\n"

    def test_parse_yaml_frontmatter_no_frontmatter(self):
        """Test parsing markdown without YAML frontmatter."""
        markdown = "# Test Lesson\n\nThis is the content."

        frontmatter, content = LessonLoader.parse_yaml_frontmatter(markdown)

        assert frontmatter == {}
        assert content == markdown

    def test_parse_segments_from_frontmatter(self):
        """Test parsing segments from frontmatter."""
        frontmatter = {
            "title": "Test Lesson",
            "segments": [
                {"id": "intro", "label": "Introduction", "selector": "## Intro"},
                {"id": "tips", "label": "Tips", "selector": "## Tips"},
                {"id": "full", "label": "Full Lesson", "selector": "*"}
            ]
        }

        segments = LessonLoader.parse_segments_from_frontmatter(frontmatter)

        assert len(segments) == 3
        assert segments[0].id == "intro"
        assert segments[0].label == "Introduction"
        assert segments[0].selector == "## Intro"
        assert segments[1].id == "tips"
        assert segments[2].id == "full"
        assert segments[2].selector == "*"

    def test_parse_segments_from_frontmatter_invalid(self):
        """Test parsing segments with invalid data."""
        frontmatter = {
            "title": "Test Lesson",
            "segments": [
                {"id": "intro", "label": "Introduction"},  # Missing selector
                {"label": "Tips", "selector": "## Tips"},  # Missing id
                "invalid_segment"  # Not a dict
            ]
        }

        segments = LessonLoader.parse_segments_from_frontmatter(frontmatter)

        assert segments is None

    def test_load_from_markdown(self):
        """Test loading lesson template data from markdown."""
        markdown = """---
title: Test Lesson
summary: A test lesson
segments:
  - id: intro
    label: Introduction
    selector: "## Introduction"
defaultSegment: intro
---

# Test Lesson

## Introduction

This is the intro.
"""

        lesson_data = LessonLoader.load_from_markdown("test-slug", markdown)

        assert lesson_data.slug == "test-slug"
        assert lesson_data.title == "Test Lesson"
        assert lesson_data.summary == "A test lesson"
        assert lesson_data.default_segment == "intro"
        assert len(lesson_data.segments) == 1
        assert lesson_data.segments[0].id == "intro"
        assert lesson_data.segments[0].selector == "## Introduction"

    def test_segments_to_json(self):
        """Test converting segments to JSON format."""
        segments = [
            LessonSegment(id="intro", label="Introduction", selector="## Intro"),
            LessonSegment(id="tips", label="Tips", selector="## Tips")
        ]

        json_segments = LessonLoader.segments_to_json(segments)

        assert json_segments == [
            {"id": "intro", "label": "Introduction", "selector": "## Intro"},
            {"id": "tips", "label": "Tips", "selector": "## Tips"}
        ]

    def test_segments_from_json(self):
        """Test converting JSON segments back to objects."""
        json_segments = [
            {"id": "intro", "label": "Introduction", "selector": "## Intro"},
            {"id": "tips", "label": "Tips", "selector": "## Tips"}
        ]

        segments = LessonLoader.segments_from_json(json_segments)

        assert len(segments) == 2
        assert segments[0].id == "intro"
        assert segments[0].label == "Introduction"
        assert segments[0].selector == "## Intro"
        assert segments[1].id == "tips"
        assert segments[1].label == "Tips"
