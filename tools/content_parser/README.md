## Content Parser (decoupled)

A lightweight, decoupled parser for lesson markdown with YAML frontmatter, designed to be used inside seeders now and moved to a Cloud Function later without changes.

### What it does
- Parses YAML frontmatter from a lesson markdown file
  - Supported keys: `slug`, `title`, `summary?`, `tags?` (list), `stepRefs?` (list), `hasAddInGuide?` (bool), `hasSourcesTables?` (bool)
- Extracts a document outline from headings (H1–H6) for future section-level rendering
- Derives a summary from the first sentence if frontmatter is missing it
- Detects optional sections by headings (e.g., “Add‑In Guide”, “Sources of …”) if flags aren’t provided
- Produces DTOs only (no DB calls), so it can run in a seeder, a job, or a Cloud Function

### Project layout
```
content_parser/
  __init__.py           # re-exports parse_markdown + DTOs
  parser.py             # pure parsing logic (frontmatter + outline + flags)

tests/
  test_parser.py        # unit tests for parser behavior
Dockerfile              # build-and-test container
```

### Install (Poetry)
From this directory:
```
poetry install --no-root
```

Run tests:
```
poetry run pytest -q
```

### Docker (no host deps)
Build and run tests inside container:
```
docker build -t content-parser:test tools/content_parser
# Option A: mount only the parser (no real assets) → tests skip external data
docker run --rm -v $(pwd)/tools/content_parser:/app content-parser:test

# Option B: mount repo root to expose real assets at /data for tests
docker run --rm -v $(pwd):/workspace -v $(pwd)/tools/content_parser:/app content-parser:test
```

### Usage
```python
from content_parser.parser import parse_markdown

with open("data/habits/programs/unfck-your-eating/005_lesson.md", "r", encoding="utf-8") as f:
    text = f.read()

parsed = parse_markdown(text)
print(parsed.slug, parsed.title, parsed.summary)
for sec in parsed.outline:
    print(sec.level, sec.title, sec.anchor)

# Flags inferred from headings or frontmatter
print(parsed.flags)  # {"hasAddInGuide": True/False, "hasSourcesTables": True/False}
```

### Frontmatter reference (proposed)
```yaml
---
slug: prioritize-protein
title: Prioritize Protein
summary: Optional short teaser; if omitted, derived from first sentence
tags: [nutrition, protein]
# Optional: day placement – either here or a program manifest
stepRefs:
  - program: unfck-your-eating
    stepSlug: protein-week   # optional; or use sequenceIndex on the program manifest
    dayIndex: 0
hasAddInGuide: true          # optional; auto-detected by headings as fallback
hasSourcesTables: true       # optional; auto-detected by headings as fallback
---
```

### Notes
- Keep parser pure and IO-free. Seeders or Cloud Functions are responsible for:
  - Computing `content_hash`/`version`
  - Upserting lessons/programs/steps and associations
  - Persisting extra metadata (e.g., outline JSON) for future section-level rendering
- Parser is intentionally forgiving when frontmatter is missing; it falls back to deriving a slug from the title and a summary from the text.


