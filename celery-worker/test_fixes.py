#!/usr/bin/env python3
"""
Simple test script to verify that our import fixes work correctly.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all the imports work correctly."""
    try:
        # Test Pub/Sub client imports
        from src.clients.pubsub_client import get_pubsub_client, PubSubClient
        print("✅ Pub/Sub client imports work")
        
        # Test task imports
        from src.tasks.journal_tasks import queue_journal_entry_indexing
        print("✅ Journal tasks imports work")
        
        from src.tasks.health_tasks import queue_health_check
        print("✅ Health tasks imports work")
        
        from src.tasks.tradition_tasks import queue_tradition_reindex
        print("✅ Tradition tasks imports work")
        
        # Test task processors imports
        from src.tasks.task_processors import get_journal_processor, get_tradition_processor, get_health_processor
        print("✅ Task processors imports work")
        
        print("\n🎉 All imports work correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 