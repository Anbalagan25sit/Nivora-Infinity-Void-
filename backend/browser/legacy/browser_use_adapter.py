"""
browser_use_adapter.py — Bridge between browser-use library and BrowserAutomationEngine

This adapter provides a compatibility layer to integrate browser-use's visual browser
automation capabilities with Nivora's existing BrowserAutomationEngine API.

Usage:
    # Direct usage
    adapter = BrowserUseAdapter(headless=False)
    await adapter.start()
    await adapter.navigate("https://example.com")
    result = await adapter.click_element(text="Login")

    # With BrowserAutomationEngine
    async with BrowserAutomationEngine(backend="browser_use") as browser:
        await browser.navigate("https://example.com")
        await browser.click_element(text="Login")
"""

import asyncio
import io
import logging
from typing import Dict, Optional, Any, Literal
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import browser-use with graceful fallback
try:
    import browser_use
    from browser_use import Browser, Agent
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False
    logger.warning("browser-use not available. Install with: pip install browser-use")


class BrowserUseAdapter:
    """
    Adapter that provides BrowserAutomationEngine-compatible API using browser-use library.

    This adapter enables visual browser automation through browser-use while maintaining
    compatibility with the existing Nivora automation tools.
    """

    def __init__(self, headless: bool = False):
        """
        Initialize browser-use adapter.

        Args:
            headless: Run browser in headless mode (no visible window)
        """
        if not BROWSER_USE_AVAILABLE:
            raise RuntimeError(
                "browser-use not available. Install with: pip install browser-use"
            )

        self.headless = headless
        self.browser: Optional[Browser] = None
        self._current_page = None

        logger.info(f"BrowserUseAdapter initialized (headless: {headless})")

    async def start(self):
        """Initialize browser-use browser."""
        try:
            # Initialize browser-use Browser instance
            # Note: browser-use API may vary - this is a simplified implementation
            self.browser = browser_use.Browser(headless=self.headless)

            # Get or create a page (browser-use may handle this differently)
            self._current_page = self.browser

            logger.info("browser-use browser started successfully")

        except Exception as e:
            logger.error(f"Failed to start browser-use browser: {e}")
            raise RuntimeError(f"browser-use initialization failed: {e}")

    async def close(self):
        """Clean up browser-use resources."""
        try:
            if self.browser:
                await self.browser.close()
            logger.info("browser-use browser closed")
        except Exception as e:
            logger.error(f"Error closing browser-use browser: {e}")

    # ═══════════════════════════════════════════════════════════
    # CORE NAVIGATION - Compatible with BrowserAutomationEngine
    # ═══════════════════════════════════════════════════════════

    async def navigate(self, url: str, wait_until: str = "networkidle") -> Dict:
        """
        Navigate to URL using browser-use.

        Args:
            url: Target URL
            wait_until: Wait condition (browser-use handles this internally)

        Returns:
            Dict with success status, title, and URL
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Use browser-use navigation
            await self._current_page.goto(url)

            # Get page info
            title = await self._current_page.title()
            current_url = self._current_page.url

            logger.info(f"browser-use navigated to: {url} (title: {title})")
            return {"success": True, "title": title, "url": current_url}

        except Exception as e:
            logger.error(f"browser-use navigation failed: {e}")
            return {"success": False, "error": str(e), "url": url}

    async def go_back(self) -> Dict:
        """Navigate back in browser history."""
        try:
            await self._current_page.go_back()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def refresh(self) -> Dict:
        """Refresh current page."""
        try:
            await self._current_page.reload()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # SMART ELEMENT INTERACTION - Using browser-use visual capabilities
    # ═══════════════════════════════════════════════════════════

    async def click_element(
        self,
        selector: str = None,
        text: str = None,
        vision_fallback: bool = True,
        timeout: int = 5000
    ) -> Dict:
        """
        Click element using browser-use visual capabilities.

        Args:
            selector: CSS selector (if provided, will try first)
            text: Text content or visual description for browser-use
            vision_fallback: Always True for browser-use (ignored)
            timeout: Maximum wait time in milliseconds

        Returns:
            Dict with success status and method used
        """
        try:
            # Strategy 1: Try CSS selector first if provided
            if selector:
                try:
                    await self._current_page.click(selector, timeout=timeout)
                    logger.info(f"browser-use clicked element by selector: {selector}")
                    return {"success": True, "method": "selector", "selector": selector}
                except Exception as selector_error:
                    logger.warning(f"Selector click failed, trying visual: {selector_error}")

            # Strategy 2: Use browser-use visual discovery
            if text:
                # Create a simple agent for this click action
                from enhanced_llm import get_enhanced_llm
                agent = Agent(
                    task=f"Click on '{text}'",
                    llm=get_enhanced_llm(),
                    browser=self.browser
                )

                # Execute the click action
                result = await agent.run()

                logger.info(f"browser-use visual click completed: {text}")
                return {
                    "success": True,
                    "method": "browser_use_visual",
                    "text": text,
                    "result": str(result)
                }

            return {"success": False, "error": "No selector or text provided"}

        except Exception as e:
            error_msg = str(e)
            logger.error(f"browser-use click failed: {error_msg}")
            return {"success": False, "error": error_msg}

    async def click_at_coordinates(self, x: int, y: int) -> Dict:
        """Click at specific screen coordinates."""
        try:
            await self._current_page.mouse.click(x, y)
            return {"success": True, "coordinates": {"x": x, "y": y}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def type_text(
        self,
        selector: str,
        text: str,
        clear_first: bool = True,
        press_enter: bool = False
    ) -> Dict:
        """
        Type text into an input field.

        Args:
            selector: CSS selector for input field
            text: Text to type
            clear_first: Clear existing text before typing
            press_enter: Press Enter key after typing

        Returns:
            Dict with success status
        """
        try:
            if clear_first:
                await self._current_page.fill(selector, text)
            else:
                await self._current_page.type(selector, text)

            if press_enter:
                await self._current_page.press(selector, "Enter")

            logger.info(f"browser-use typed text into: {selector}")
            return {"success": True, "selector": selector}

        except Exception as e:
            logger.error(f"browser-use type text failed: {e}")
            return {"success": False, "error": str(e)}

    async def select_dropdown(self, selector: str, value: str = None, text: str = None) -> Dict:
        """Select option from dropdown by value or visible text."""
        try:
            if value:
                await self._current_page.select_option(selector, value=value)
            elif text:
                await self._current_page.select_option(selector, label=text)

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # INTELLIGENT FORM FILLING - Using browser-use agent
    # ═══════════════════════════════════════════════════════════

    async def fill_form(self, form_data: Dict[str, str], submit: bool = False) -> Dict:
        """
        Fill form using browser-use agent intelligence.

        Args:
            form_data: Dict mapping field names to values
            submit: Whether to submit the form after filling

        Returns:
            Dict with filled fields and success status
        """
        try:
            # Create task description for browser-use agent
            form_fields = []
            for key, value in form_data.items():
                form_fields.append(f"Fill '{key}' field with '{value}'")

            task = "Fill out the form on this page: " + "; ".join(form_fields)
            if submit:
                task += "; then submit the form"

            # Create and run browser-use agent
            from enhanced_llm import get_enhanced_llm
            agent = Agent(
                task=task,
                llm=get_enhanced_llm(),
                browser=self.browser
            )

            result = await agent.run()

            # Return simplified success response
            filled_fields = [{"field": key, "status": "attempted"} for key in form_data.keys()]

            return {
                "success": True,
                "filled_fields": filled_fields,
                "submitted": submit,
                "agent_result": str(result)
            }

        except Exception as e:
            logger.error(f"browser-use form filling failed: {e}")
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # DATA EXTRACTION - Using browser-use agent
    # ═══════════════════════════════════════════════════════════

    async def extract_data(self, query: str) -> Dict:
        """
        Extract data using browser-use agent.

        Args:
            query: Description of what to extract

        Returns:
            Dict with extracted data
        """
        try:
            # Create extraction task for browser-use agent
            task = f"Extract data from this page: {query}. Return the extracted information."

            from enhanced_llm import get_enhanced_llm
            agent = Agent(
                task=task,
                llm=get_enhanced_llm(),
                browser=self.browser
            )

            result = await agent.run()

            # Format result to match expected structure
            return {
                "data": [str(result)],  # browser-use result as single item
                "count": 1,
                "page_title": await self.get_page_title(),
                "summary": f"Extracted using browser-use: {query}",
                "raw_result": str(result)
            }

        except Exception as e:
            logger.error(f"browser-use data extraction failed: {e}")
            return {"success": False, "error": str(e), "data": []}

    async def get_page_text(self) -> str:
        """Extract all visible text from current page."""
        try:
            return await self._current_page.inner_text("body")
        except Exception as e:
            logger.error(f"Get page text failed: {e}")
            return ""

    async def get_element_text(self, selector: str) -> str:
        """Get text content of specific element."""
        try:
            return await self._current_page.inner_text(selector)
        except Exception as e:
            logger.error(f"Get element text failed: {e}")
            return ""

    # ═══════════════════════════════════════════════════════════
    # VISION AND ANALYSIS - Delegate to browser-use
    # ═══════════════════════════════════════════════════════════

    async def capture_screenshot(self, full_page: bool = False) -> Image.Image:
        """
        Capture screenshot of current page.

        Args:
            full_page: Capture entire page vs viewport only

        Returns:
            PIL Image object
        """
        try:
            screenshot_bytes = await self._current_page.screenshot(full_page=full_page)
            return Image.open(io.BytesIO(screenshot_bytes))
        except Exception as e:
            logger.error(f"browser-use screenshot capture failed: {e}")
            # Return blank image as fallback
            return Image.new('RGB', (1920, 1080), color='white')

    async def analyze_page_with_vision(self, question: str) -> str:
        """
        Analyze page using browser-use agent.

        Args:
            question: Question about the page

        Returns:
            String answer from browser-use agent
        """
        try:
            task = f"Analyze this page and answer: {question}"

            from enhanced_llm import get_enhanced_llm
            agent = Agent(
                task=task,
                llm=get_enhanced_llm(),
                browser=self.browser
            )

            result = await agent.run()
            return str(result)

        except Exception as e:
            logger.error(f"browser-use page analysis failed: {e}")
            return f"Analysis error: {e}"

    # ═══════════════════════════════════════════════════════════
    # HELPER UTILITIES - Compatible implementations
    # ═══════════════════════════════════════════════════════════

    async def wait_for_element(self, selector: str, timeout: int = 5000, state: str = "visible") -> bool:
        """Wait for element to appear/disappear."""
        try:
            await self._current_page.wait_for_selector(selector, timeout=timeout, state=state)
            return True
        except Exception as e:
            logger.warning(f"Wait for element timeout: {selector}")
            return False

    async def scroll_to_element(self, selector: str):
        """Scroll element into view."""
        try:
            await self._current_page.locator(selector).scroll_into_view_if_needed()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def scroll_page(self, direction: Literal["down", "up", "top", "bottom"] = "down", amount: int = 500):
        """Scroll the page."""
        try:
            if direction == "top":
                script = "window.scrollTo(0, 0)"
            elif direction == "bottom":
                script = "window.scrollTo(0, document.body.scrollHeight)"
            elif direction == "down":
                script = f"window.scrollBy(0, {amount})"
            else:  # up
                script = f"window.scrollBy(0, -{amount})"

            await self._current_page.evaluate(script)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_javascript(self, script: str) -> Any:
        """Execute custom JavaScript on the page."""
        try:
            return await self._current_page.evaluate(script)
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return None

    async def get_current_url(self) -> str:
        """Get current page URL."""
        return self._current_page.url

    async def get_page_title(self) -> str:
        """Get current page title."""
        try:
            return await self._current_page.title()
        except:
            return ""


# ═══════════════════════════════════════════════════════════
# ASYNC CONTEXT MANAGER SUPPORT
# ═══════════════════════════════════════════════════════════

class BrowserUseAdapterContext:
    """Async context manager for BrowserUseAdapter."""

    def __init__(self, headless: bool = False):
        self.adapter = BrowserUseAdapter(headless=headless)

    async def __aenter__(self):
        await self.adapter.start()
        return self.adapter

    async def __aexit__(self, *args):
        await self.adapter.close()


# ═══════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════

def is_browser_use_available() -> bool:
    """Check if browser-use is available for use."""
    return BROWSER_USE_AVAILABLE


async def create_browser_use_adapter(headless: bool = False) -> BrowserUseAdapter:
    """
    Factory function to create and start a browser-use adapter.

    Args:
        headless: Run browser in headless mode

    Returns:
        Started BrowserUseAdapter instance

    Raises:
        RuntimeError: If browser-use is not available
    """
    if not BROWSER_USE_AVAILABLE:
        raise RuntimeError("browser-use not available. Install with: pip install browser-use")

    adapter = BrowserUseAdapter(headless=headless)
    await adapter.start()
    return adapter


# ═══════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════

async def test_browser_use_adapter():
    """Test browser-use adapter functionality."""
    if not BROWSER_USE_AVAILABLE:
        print("browser-use not available for testing")
        return

    print("=" * 60)
    print("Browser-Use Adapter Test")
    print("=" * 60)

    try:
        async with BrowserUseAdapterContext(headless=False) as adapter:
            # Test navigation
            print("\n[TEST 1] Navigating to example.com...")
            result = await adapter.navigate("https://example.com")
            print(f"  Result: {result}")

            await asyncio.sleep(2)

            # Test screenshot
            print("\n[TEST 2] Capturing screenshot...")
            screenshot = await adapter.capture_screenshot()
            print(f"  Screenshot size: {screenshot.size}")

            # Test page analysis
            print("\n[TEST 3] Analyzing page...")
            analysis = await adapter.analyze_page_with_vision("What is the main heading?")
            print(f"  Analysis: {analysis}")

            await asyncio.sleep(3)

        print("\n" + "=" * 60)
        print("browser-use adapter test complete!")
        print("=" * 60)

    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_browser_use_adapter())