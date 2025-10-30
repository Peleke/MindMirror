"""MindMirror CLI commands."""

from .seed_habits import app as seed_habits
from .seed_movements import app as seed_movements
from .seed_pn_movements import app as seed_pn_movements
from .qdrant import app as qdrant
from .supabase import app as supabase

__all__ = [
    "qdrant",
    "supabase",
    "seed_habits",
    "seed_movements",
    "seed_pn_movements",
]