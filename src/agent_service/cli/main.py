"""
Main CLI entry point for agent service.

Usage:
    python -m agent_service.cli.main <command> [options]
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from agent_service.cli.data_management import cli

if __name__ == "__main__":
    sys.exit(cli()) 