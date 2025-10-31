from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import re
import yaml


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass
class OutlineItem:
    level: int
    title: str
    anchor: str


@dataclass
class ParsedLesson:
    slug: str
    title: str
    summary: Optional[str]
    tags: List[str]
    markdown: str
    outline: List[OutlineItem]
    flags: Dict[str, Any]
    raw_frontmatter: Dict[str, Any]


def _parse_frontmatter(md: str) -> tuple[Dict[str, Any], str]:
    m = FRONTMATTER_RE.match(md)
    if not m:
        return {}, md
    fm_text, body = m.group(1), m.group(2)
    data = yaml.safe_load(fm_text) or {}
    return data, body


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    s = re.sub(r"\s+", "-", s)
    return s


def _extract_outline(body: str) -> List[OutlineItem]:
    outline: List[OutlineItem] = []
    for line in body.splitlines():
        mh = HEADING_RE.match(line)
        if not mh:
            continue
        level = len(mh.group(1))
        title = mh.group(2).strip()
        anchor = _slugify(title)
        outline.append(OutlineItem(level=level, title=title, anchor=anchor))
    return outline


def _first_sentence(text: str) -> Optional[str]:
    # naive: first non-empty line or split by period
    for para in text.splitlines():
        p = para.strip()
        if not p:
            continue
        # Split on sentence end
        parts = re.split(r"(?<=[.!?])\s+", p)
        return parts[0][:200]
    return None


def parse_markdown(md: str) -> ParsedLesson:
    fm, body = _parse_frontmatter(md)
    title = fm.get("title") or ""
    slug = fm.get("slug") or _slugify(title)
    tags = fm.get("tags") or []
    summary = fm.get("summary") or _first_sentence(body)
    outline = _extract_outline(body)
    flags = {
        "hasAddInGuide": bool(fm.get("hasAddInGuide")) or any("add-in" in i.title.lower() for i in outline),
        "hasSourcesTables": bool(fm.get("hasSourcesTables")) or any("sources of" in i.title.lower() for i in outline),
    }
    return ParsedLesson(
        slug=slug,
        title=title,
        summary=summary,
        tags=tags,
        markdown=body,
        outline=outline,
        flags=flags,
        raw_frontmatter=fm,
    )


