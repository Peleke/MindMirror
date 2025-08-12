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


