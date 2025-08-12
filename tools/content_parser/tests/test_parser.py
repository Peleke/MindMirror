from __future__ import annotations

import pytest

from content_parser.parser import parse_markdown


def test_parse_minimal_frontmatter_and_outline():
    md = """---
slug: prioritize-protein
title: Prioritize Protein
tags: [nutrition, protein]
---

## Section One
Body

### Subsection
More
"""
    parsed = parse_markdown(md)
    assert parsed.slug == "prioritize-protein"
    assert parsed.title == "Prioritize Protein"
    assert parsed.tags == ["nutrition", "protein"]
    assert len(parsed.outline) >= 2
    assert parsed.outline[0].level == 2 and parsed.outline[0].title == "Section One"


def test_detect_optional_sections():
    md = """---
title: With Sections
---

## Protein Add-In Guide
text

## Sources of Protein
table
"""
    parsed = parse_markdown(md)
    assert parsed.flags["hasAddInGuide"] is True
    assert parsed.flags["hasSourcesTables"] is True


def test_parse_real_assets_outline_and_summary():
    # Reads real content; verifies outline and summary derivation work without frontmatter
    import os
    # Prefer mounted /data when running in container with repo mounted at /workspace
    mounted_base = "/data/habits/programs/unfck-your-eating"
    if os.path.exists(mounted_base):
        base = mounted_base
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/habits/programs/unfck-your-eating"))
    # Pick a representative file that has headings and content
    target = os.path.join(base, "005_lesson.md")
    with open(target, "r", encoding="utf-8") as f:
        md = f.read()
    parsed = parse_markdown(md)
    # No frontmatter present, so slug may default from title if detected, otherwise empty; outline must exist
    assert isinstance(parsed.outline, list) and len(parsed.outline) >= 1
    # Summary should be derived from first sentence of body
    assert isinstance(parsed.summary, str) and len(parsed.summary) > 0

