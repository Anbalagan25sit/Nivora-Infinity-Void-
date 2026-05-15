import asyncio
import logging
import contextlib

logger = logging.getLogger(__name__)

_global_browser = None

async def get_global_browser(backend="playwright", headless=False, private_mode=False):
    """
    Get or create a persistent, global browser instance.
    By default, uses private_mode=False to persist login sessions (e.g. for @nivora_dev).
    """
    global _global_browser
    if _global_browser is None:
        from browser_automation import BrowserAutomationEngine
        _global_browser = BrowserAutomationEngine(
            backend=backend, 
            headless=headless,
            private_mode=private_mode
        )
        await _global_browser.start()
        logger.info(f"Started global browser (private_mode={private_mode}, headless={headless})")
    
    return _global_browser

@contextlib.asynccontextmanager
async def use_global_browser(backend="playwright", headless=False, private_mode=False, visual_mode=False):
    """
    Context manager that yields the global browser instance without closing it.
    Use this to seamlessly replace `async with BrowserAutomationEngine(...)`.
    """
    browser = await get_global_browser(backend=backend, headless=headless, private_mode=private_mode)
    try:
        yield browser
    finally:
        # We DO NOT close the global browser here. It persists across tool calls.
        pass

async def close_global_browser():
    """Close the global browser instance."""
    global _global_browser
    if _global_browser is not None:
        await _global_browser.close()
        _global_browser = None
        logger.info("Closed global browser")

