#!/usr/bin/env python3
"""
Qdrant Knowledge Base Builder CLI

Build and manage Qdrant-based knowledge bases for traditions.
This script replaces the legacy FAISS-based build_knowledge_base.py.

Usage:
    python scripts/build_qdrant_knowledge_base.py --tradition canon-default --verbose
    python scripts/build_qdrant_knowledge_base.py --all --clear-existing
    python scripts/build_qdrant_knowledge_base.py --dry-run
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_service.qdrant_data_processing import QdrantKnowledgeBaseBuilder
from agent_service.vector_stores.qdrant_client import QdrantClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ProgressReporter:
    """Real-time progress reporting for knowledge base building."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.start_time = None

    def start(self, message: str):
        """Start progress tracking."""
        self.start_time = time.time()
        print(f"🚀 {message}")
        if self.verbose:
            print("=" * 60)

    def update(self, message: str, level: str = "info"):
        """Update progress with a message."""
        if level == "error":
            print(f"❌ {message}")
        elif level == "warning":
            print(f"⚠️  {message}")
        elif level == "success":
            print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")

    def finish(self, success: bool, summary: str):
        """Complete progress tracking."""
        duration = time.time() - self.start_time if self.start_time else 0
        status = "✅ COMPLETED" if success else "❌ FAILED"
        print(f"\n{status} in {duration:.2f}s")
        print(f"📊 {summary}")
        if self.verbose:
            print("=" * 60)


async def validate_environment() -> bool:
    """Validate that all required services are available."""
    logger.info("🔍 Validating environment...")

    try:
        # Check Qdrant connection
        client = QdrantClient()
        health = await client.health_check()

        if not health:
            logger.error("❌ Qdrant service is not available")
            logger.error(
                "   Please ensure Qdrant is running (docker-compose up qdrant)"
            )
            return False

        logger.info("✅ Qdrant service is available")
        return True

    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        return False


async def discover_traditions(source_dirs: List[str]) -> dict:
    """Discover available traditions and their document counts."""
    builder = QdrantKnowledgeBaseBuilder()
    traditions = builder.discover_source_directories(source_dirs)

    # Count documents in each tradition
    tradition_info = {}
    for tradition, dirs in traditions.items():
        total_files = 0
        for directory in dirs:
            pdf_count = len(list(directory.glob("*.pdf")))
            txt_count = len(list(directory.glob("*.txt")))
            total_files += pdf_count + txt_count

        tradition_info[tradition] = {
            "directories": [str(d) for d in dirs],
            "file_count": total_files,
        }

    return tradition_info


async def dry_run(args: argparse.Namespace) -> None:
    """Preview what would be built without making changes."""
    reporter = ProgressReporter(args.verbose)
    reporter.start("DRY RUN - Previewing knowledge base build")

    # Discover traditions
    traditions = await discover_traditions(args.source_dirs)

    if not traditions:
        reporter.update("No traditions found in source directories", "error")
        return

    print("\n📋 BUILD PREVIEW")
    print("=" * 50)

    for tradition, info in traditions.items():
        # Skip if specific tradition requested and this isn't it
        if args.tradition and tradition != args.tradition:
            continue

        print(f"\n🏛️  Tradition: {tradition}")
        print(f"   📁 Source directories: {len(info['directories'])}")
        for directory in info["directories"]:
            print(f"      • {directory}")
        print(f"   📄 Documents found: {info['file_count']}")

        if args.clear_existing:
            print(f"   🗑️  Would clear existing collection: {tradition}_knowledge")

    if args.tradition:
        if args.tradition not in traditions:
            reporter.update(f"Tradition '{args.tradition}' not found", "error")
            print(f"\n💡 Available traditions: {', '.join(traditions.keys())}")
            return
        count = 1
        files = traditions[args.tradition]["file_count"]
    else:
        count = len(traditions)
        files = sum(info["file_count"] for info in traditions.values())

    print(f"\n📊 SUMMARY")
    print(f"   • Traditions to build: {count}")
    print(f"   • Total documents: {files}")
    print(f"   • Clear existing: {'Yes' if args.clear_existing else 'No'}")

    reporter.finish(True, f"Would process {count} traditions with {files} documents")


async def build_knowledge_base(args: argparse.Namespace) -> bool:
    """Build the knowledge base with the specified options."""
    reporter = ProgressReporter(args.verbose)

    # Start build process
    action = "Rebuilding" if args.clear_existing else "Building"
    target = f"tradition '{args.tradition}'" if args.tradition else "all traditions"
    reporter.start(f"{action} knowledge base for {target}")

    try:
        # Create builder
        builder = QdrantKnowledgeBaseBuilder()

        # Run the build
        results = await builder.build_all_traditions(
            source_dirs=args.source_dirs,
            specific_tradition=args.tradition,
            clear_existing=args.clear_existing,
        )

        # Report results
        if results["status"] == "error":
            reporter.update(
                f"Build failed: {results.get('message', 'Unknown error')}", "error"
            )
            return False

        # Success statistics
        successful = results["successful_traditions"]
        total_chunks = results["total_chunks"]
        total_files = results["total_files_processed"]
        failed_files = results["total_files_failed"]
        duration = results["duration_seconds"]

        if args.verbose:
            print(f"\n📊 DETAILED RESULTS")
            print("=" * 40)
            for tradition, result in results["traditions"].items():
                status_icon = "✅" if result.get("status") == "success" else "❌"
                chunks = result.get("processed_chunks", 0)
                print(f"{status_icon} {tradition}: {chunks} chunks")
                if result.get("status") == "error":
                    print(f"    Error: {result.get('message', 'Unknown')}")

        # Summary
        reporter.finish(
            success=True,
            summary=f"{len(successful)} traditions, {total_chunks} chunks, {total_files} files ({failed_files} failed)",
        )

        if successful:
            print(
                f"\n🎉 Successfully built knowledge bases for: {', '.join(successful)}"
            )
            print(
                f"⚡ Performance: {total_chunks/duration:.1f} chunks/second"
                if duration > 0
                else ""
            )

        if failed_files > 0:
            reporter.update(f"{failed_files} files failed to process", "warning")

        return True

    except Exception as e:
        reporter.update(f"Build failed with exception: {e}", "error")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return False


async def list_collections(args: argparse.Namespace) -> None:
    """List existing Qdrant collections."""
    try:
        client = QdrantClient()
        collections = await client.list_collections()

        if not collections:
            print("📭 No collections found in Qdrant")
            return

        print(f"📚 Found {len(collections)} collections:")
        for collection in collections:
            print(f"   • {collection}")

            if args.verbose:
                # Get collection info
                try:
                    info = await client.get_collection_info(collection)
                    count = (
                        info.vectors_count
                        if hasattr(info, "vectors_count")
                        else "unknown"
                    )
                    print(f"     Documents: {count}")
                except Exception as e:
                    print(f"     Error getting info: {e}")

    except Exception as e:
        logger.error(f"Failed to list collections: {e}")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build and manage Qdrant knowledge bases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build knowledge base for specific tradition
  python scripts/build_qdrant_knowledge_base.py --tradition canon-default --verbose
  
  # Build all traditions, clearing existing data
  python scripts/build_qdrant_knowledge_base.py --all --clear-existing
  
  # Preview what would be built for specific tradition
  python scripts/build_qdrant_knowledge_base.py --tradition canon-default --dry-run
  
  # Preview all traditions
  python scripts/build_qdrant_knowledge_base.py --all --dry-run
  
  # List existing collections
  python scripts/build_qdrant_knowledge_base.py --list-collections
        """,
    )

    # Target options (can be combined with other flags)
    parser.add_argument(
        "--tradition", type=str, help="Build knowledge base for specific tradition only"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build knowledge bases for all discovered traditions",
    )

    # Action options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be built without making changes",
    )
    parser.add_argument(
        "--list-collections",
        action="store_true",
        help="List existing Qdrant collections",
    )

    # Configuration options
    parser.add_argument(
        "--source-dirs",
        nargs="+",
        default=["local_gcs_bucket", "pdfs"],
        help="Base directories to scan for traditions (default: local_gcs_bucket pdfs)",
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing collections before building",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("agent_service").setLevel(logging.DEBUG)

    # Handle list collections (priority action)
    if args.list_collections:
        if not await validate_environment():
            sys.exit(1)
        await list_collections(args)
        return

    # Handle dry run
    if args.dry_run:
        await dry_run(args)
        return

    # Validate target selection
    if args.tradition and args.all:
        logger.error("Cannot specify both --tradition and --all")
        sys.exit(1)

    # Default to --all if no specific target
    if not args.tradition and not args.all:
        args.all = True

    # Validate environment
    if not await validate_environment():
        logger.error("Environment validation failed. Please check your setup.")
        sys.exit(1)

    # Build knowledge base
    success = await build_knowledge_base(args)

    if not success:
        logger.error("Knowledge base build failed")
        sys.exit(1)

    logger.info("🎉 Knowledge base build completed successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
