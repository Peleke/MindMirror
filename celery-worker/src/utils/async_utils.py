"""
Async utilities for running async code in sync contexts.
"""

import asyncio
import concurrent.futures


def run_async_in_sync(coro):
    """Run an async coroutine in a sync context, handling existing event loops."""
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we get here, an event loop is already running
        # We need to run the coroutine in a different way
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No event loop is running, we can create one
        return asyncio.run(coro) 