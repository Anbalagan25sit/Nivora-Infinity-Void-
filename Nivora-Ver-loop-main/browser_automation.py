"""
browser_automation.py — Intelligent Browser Automation Engine
Combines Playwright + Selenium with AWS Nova Pro vision for robust web automation.

Architecture:
- Playwright (primary): Modern async API, better performance
- Selenium (fallback): Wider browser support, mature ecosystem
- Vision integration: Nova Pro analyzes page when DOM selectors fail

Usage:
    async with BrowserAutomationEngine() as browser:
        await browser.navigate("https://example.com")
        await browser.click_element(selector="#login-btn")
        data = await browser.extract_data("extract all product prices")
"""

import asyncio
import base64
import io
import logging
import re
from typing import Dict, List, Optional, Literal, Any
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import playwright (primary)
try:
    from playwright.async_api import async_playwright, Page, Browser, Playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available. Install with: pip install playwright && python -m playwright install chromium")

# Try to import selenium (fallback)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available. Install with: pip install selenium")

# Try to import browser-use (visual automation)
try:
    from browser_use_adapter import BrowserUseAdapter, is_browser_use_available
    BROWSER_USE_AVAILABLE = is_browser_use_available()
except ImportError:
    BROWSER_USE_AVAILABLE = False
    logger.warning("browser-use adapter not available.")


class BrowserAutomationEngine:
    """
    Intelligent browser automation that combines:
    1. Playwright for fast, reliable DOM-based automation
    2. Vision AI (Nova Pro) for complex visual understanding
    3. Fallback strategies when selectors fail
    """

    def __init__(self, backend: Literal["playwright", "selenium", "browser_use", "auto"] = "auto", headless: bool = False, visual_mode: bool = False):
        """
        Initialize browser automation engine.

        Args:
            backend: "playwright", "selenium", "browser_use", or "auto" (auto-detect best available)
            headless: Run browser in headless mode (no visible window)
            visual_mode: Prefer visual automation methods when available
        """
        # Auto-detect best available backend
        if backend == "auto":
            # Prefer browser-use for visual tasks, Playwright for standard automation
            if visual_mode and BROWSER_USE_AVAILABLE:
                backend = "browser_use"
            elif PLAYWRIGHT_AVAILABLE:
                backend = "playwright"
            elif BROWSER_USE_AVAILABLE:
                backend = "browser_use"
            elif SELENIUM_AVAILABLE:
                backend = "selenium"
            else:
                raise RuntimeError(
                    "No browser automation library available. "
                    "Install playwright: pip install playwright && python -m playwright install chromium"
                )

        self.backend = backend
        self.headless = headless
        self.visual_mode = visual_mode

        # Playwright state
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        # Selenium state
        self.driver = None

        # browser-use adapter state
        self.browser_use_adapter: Optional[BrowserUseAdapter] = None

        logger.info(f"BrowserAutomationEngine initialized with backend: {backend} (visual_mode: {visual_mode})")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def start(self):
        """Initialize browser automation backend."""
        if self.backend == "browser_use":
            if not BROWSER_USE_AVAILABLE:
                raise RuntimeError("browser-use adapter not available.")

            self.browser_use_adapter = BrowserUseAdapter(headless=self.headless)
            await self.browser_use_adapter.start()
            logger.info("browser-use adapter started")

        elif self.backend == "playwright":
            if not PLAYWRIGHT_AVAILABLE:
                raise RuntimeError("Playwright not available. Install with: pip install playwright")

            self.playwright = await async_playwright().start()

            # Use a SEPARATE persistent profile for automation (not main Chrome profile)
            # This way cookies/sessions persist between runs, but doesn't conflict with running Chrome
            import os
            import pathlib

            # Create automation profile directory
            automation_profile = pathlib.Path.home() / ".nivora_browser_profile"
            automation_profile.mkdir(parents=True, exist_ok=True)

            logger.info(f"Using persistent browser profile: {automation_profile}")

            # Use persistent context to save cookies/sessions
            try:
                self.browser = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=str(automation_profile),
                    headless=self.headless,
                    channel="chrome",  # Use installed Chrome, not Chromium
                    args=[
                        '--start-maximized',
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-blink-features=AutomationControlled',
                    ] if not self.headless else [],
                    # Accept downloads, enable persistent storage
                    accept_downloads=True,
                )
                self.page = self.browser.pages[0] if self.browser.pages else await self.browser.new_page()
                logger.info("✅ Playwright started with persistent profile - cookies/sessions will be saved!")
            except Exception as e:
                logger.error(f"Could not start persistent context: {e}")
                # Fallback to regular browser (no session persistence)
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    channel="chrome",
                    args=['--start-maximized'] if not self.headless else []
                )
                context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080} if not self.headless else None
                )
                self.page = await context.new_page()
                logger.warning("⚠️ Started without persistent profile - you'll need to login each time")

        elif self.backend == "selenium":
            if not SELENIUM_AVAILABLE:
                raise RuntimeError("Selenium not available. Install with: pip install selenium")

            import os
            chrome_user_data = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(f"--user-data-dir={chrome_user_data}")
            options.add_argument("--profile-directory=Default")

            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium browser started with Chrome profile")

    async def close(self):
        """Clean up browser resources."""
        try:
            if self.browser_use_adapter:
                await self.browser_use_adapter.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            if self.driver:
                self.driver.quit()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    # ═══════════════════════════════════════════════════════════
    # CORE NAVIGATION
    # ═══════════════════════════════════════════════════════════

    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> Dict:
        """
        Navigate to URL with smart waiting and fallback strategies.

        Args:
            url: Target URL
            wait_until: "networkidle" (strictest), "load" (standard), "domcontentloaded" (fastest)
                       Default changed to "domcontentloaded" for better reliability

        Returns:
            Dict with success status, title, and URL
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            if self.backend == "browser_use":
                return await self.browser_use_adapter.navigate(url, wait_until)
            elif self.backend == "playwright":
                # Try with smart fallback strategy
                try:
                    # First try with the requested wait strategy (60s timeout for slow sites)
                    await self.page.goto(url, wait_until=wait_until, timeout=60000)
                except Exception as e:
                    logger.warning(f"Navigation with '{wait_until}' failed, trying 'domcontentloaded': {e}")
                    # Fallback to faster wait strategy
                    try:
                        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    except Exception as e2:
                        logger.warning(f"Navigation with 'domcontentloaded' failed, trying 'commit': {e2}")
                        # Last resort - just wait for navigation to start
                        await self.page.goto(url, wait_until="commit", timeout=15000)

                title = await self.page.title()
                current_url = self.page.url
            else:  # selenium
                self.driver.get(url)
                title = self.driver.title
                current_url = self.driver.current_url

            logger.info(f"Navigated to: {url} (title: {title})")
            return {"success": True, "title": title, "url": current_url}

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e), "url": url}

    async def go_back(self) -> Dict:
        """Navigate back in browser history."""
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.go_back()
            elif self.backend == "playwright":
                await self.page.go_back()
            else:
                self.driver.back()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def refresh(self) -> Dict:
        """Refresh current page."""
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.refresh()
            elif self.backend == "playwright":
                await self.page.reload()
            else:
                self.driver.refresh()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # SMART ELEMENT INTERACTION
    # ═══════════════════════════════════════════════════════════

    async def click_element(
        self,
        selector: str = None,
        text: str = None,
        vision_fallback: bool = True,
        timeout: int = 5000
    ) -> Dict:
        """
        Click an element using multiple strategies:
        1. CSS selector (fastest)
        2. Text content matching
        3. browser-use visual discovery (if available)
        4. Vision AI coordinates (fallback)

        Args:
            selector: CSS selector (e.g., "#login-btn", ".submit-button")
            text: Text content to search for (e.g., "Login", "Submit")
            vision_fallback: Use vision AI if DOM methods fail
            timeout: Maximum wait time in milliseconds

        Returns:
            Dict with success status and method used
        """
        try:
            # If browser-use backend, delegate to it directly
            if self.backend == "browser_use":
                return await self.browser_use_adapter.click_element(
                    selector=selector,
                    text=text,
                    vision_fallback=vision_fallback,
                    timeout=timeout
                )

            # Strategy 1: CSS Selector
            if selector:
                if self.backend == "playwright":
                    await self.page.click(selector, timeout=timeout)
                else:
                    element = WebDriverWait(self.driver, timeout/1000).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    element.click()
                logger.info(f"Clicked element by selector: {selector}")
                return {"success": True, "method": "selector", "selector": selector}

            # Strategy 2: Text Content
            elif text:
                if self.backend == "playwright":
                    await self.page.get_by_text(text, exact=False).click(timeout=timeout)
                else:
                    xpath = f"//*[contains(text(), '{text}')]"
                    element = self.driver.find_element(By.XPATH, xpath)
                    element.click()
                logger.info(f"Clicked element by text: {text}")
                return {"success": True, "method": "text", "text": text}

            # Strategy 3: browser-use visual fallback (if available and not already used)
            elif vision_fallback and text and BROWSER_USE_AVAILABLE and self.backend != "browser_use":
                logger.info("Attempting browser-use visual fallback...")
                try:
                    # Create temporary browser-use adapter for visual discovery
                    temp_adapter = BrowserUseAdapter(headless=self.headless)
                    await temp_adapter.start()

                    # Get current URL to navigate browser-use to same page
                    current_url = await self.get_current_url()
                    await temp_adapter.navigate(current_url)

                    # Try visual click
                    result = await temp_adapter.click_element(text=text)
                    await temp_adapter.close()

                    if result["success"]:
                        logger.info(f"browser-use visual click successful: {text}")
                        return {"success": True, "method": "browser_use_visual", "text": text}
                except Exception as browser_use_error:
                    logger.warning(f"browser-use fallback failed: {browser_use_error}")

            # Strategy 4: Traditional Vision AI Fallback (existing implementation)
            elif vision_fallback and text:
                logger.info("Attempting traditional vision AI fallback for click...")
                screenshot = await self.capture_screenshot()
                coords = await self._vision_find_element(screenshot, text)

                if coords:
                    await self.click_at_coordinates(coords['x'], coords['y'])
                    logger.info(f"Clicked at vision coordinates: ({coords['x']}, {coords['y']})")
                    return {"success": True, "method": "vision", "coordinates": coords}
                else:
                    return {"success": False, "error": "Vision AI could not locate element"}

            return {"success": False, "error": "No selector or text provided"}

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Click failed: {error_msg}")

            # Try browser-use fallback if enabled, available, and not already tried
            if (vision_fallback and text and BROWSER_USE_AVAILABLE and
                self.backend != "browser_use" and "timeout" in error_msg.lower()):
                try:
                    logger.info("DOM click timeout, trying browser-use fallback...")
                    temp_adapter = BrowserUseAdapter(headless=self.headless)
                    await temp_adapter.start()
                    current_url = await self.get_current_url()
                    await temp_adapter.navigate(current_url)
                    result = await temp_adapter.click_element(text=text)
                    await temp_adapter.close()

                    if result["success"]:
                        return {"success": True, "method": "browser_use_timeout_fallback", "text": text}
                except Exception as browser_use_error:
                    logger.error(f"browser-use timeout fallback also failed: {browser_use_error}")

            # Try traditional vision fallback if enabled and not already tried
            if vision_fallback and text and "timeout" in error_msg.lower():
                try:
                    logger.info("DOM click timeout, trying traditional vision fallback...")
                    screenshot = await self.capture_screenshot()
                    coords = await self._vision_find_element(screenshot, text)
                    if coords:
                        await self.click_at_coordinates(coords['x'], coords['y'])
                        return {"success": True, "method": "vision_fallback", "coordinates": coords}
                except Exception as vision_error:
                    logger.error(f"Vision fallback also failed: {vision_error}")

            return {"success": False, "error": error_msg}

    async def click_at_coordinates(self, x: int, y: int) -> Dict:
        """Click at specific screen coordinates."""
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.click_at_coordinates(x, y)
            elif self.backend == "playwright":
                await self.page.mouse.click(x, y)
            else:
                # Selenium requires ActionChains for coordinate clicking
                from selenium.webdriver import ActionChains
                actions = ActionChains(self.driver)
                actions.move_by_offset(x, y).click().perform()
                actions.reset_actions()  # Reset to origin

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
            if self.backend == "browser_use":
                return await self.browser_use_adapter.type_text(selector, text, clear_first, press_enter)
            elif self.backend == "playwright":
                if clear_first:
                    await self.page.fill(selector, text)
                else:
                    await self.page.type(selector, text, delay=50)

                if press_enter:
                    await self.page.press(selector, "Enter")
            else:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if clear_first:
                    element.clear()
                element.send_keys(text)

                if press_enter:
                    from selenium.webdriver.common.keys import Keys
                    element.send_keys(Keys.RETURN)

            logger.info(f"Typed text into: {selector}")
            return {"success": True, "selector": selector}

        except Exception as e:
            logger.error(f"Type text failed: {e}")
            return {"success": False, "error": str(e)}

    async def select_dropdown(self, selector: str, value: str = None, text: str = None) -> Dict:
        """Select option from dropdown by value or visible text."""
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.select_dropdown(selector, value, text)
            elif self.backend == "playwright":
                if value:
                    await self.page.select_option(selector, value=value)
                elif text:
                    await self.page.select_option(selector, label=text)
            else:
                from selenium.webdriver.support.ui import Select
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                select = Select(element)
                if value:
                    select.select_by_value(value)
                elif text:
                    select.select_by_visible_text(text)

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # INTELLIGENT FORM FILLING
    # ═══════════════════════════════════════════════════════════

    async def fill_form(self, form_data: Dict[str, str], submit: bool = False) -> Dict:
        """
        Intelligently fill a form by:
        1. Using browser-use agent (if available and configured)
        2. Analyzing form structure with vision AI
        3. Mapping fields to inputs
        4. Filling and optionally submitting

        Args:
            form_data: Dict mapping field labels/names to values
                      e.g., {"email": "user@example.com", "password": "secret"}
            submit: Whether to submit the form after filling

        Returns:
            Dict with filled fields and success status
        """
        try:
            # Strategy 1: Use browser-use for intelligent form filling
            if self.backend == "browser_use":
                return await self.browser_use_adapter.fill_form(form_data, submit)

            # Strategy 2: Use vision AI to understand form structure (existing implementation)
            # Capture current page state
            screenshot = await self.capture_screenshot()

            # Use vision AI to understand form structure
            loop = asyncio.get_running_loop()
            from computer_use import analyze_screen

            prompt = f"""
Analyze this form and identify all input fields.
For each field, provide the CSS selector and field type.

Return JSON in this exact format:
{{
    "fields": [
        {{"label": "Email", "selector": "input[type='email']", "type": "email"}},
        {{"label": "Password", "selector": "input[type='password']", "type": "password"}},
        {{"label": "Name", "selector": "input[name='name']", "type": "text"}}
    ]
}}

Return ONLY valid JSON, no markdown, no explanation.
"""

            # Use executor to avoid blocking the event loop
            analysis = await loop.run_in_executor(None, analyze_screen, prompt, screenshot, 0.1)

            if "error" in analysis:
                # Fallback: try common selectors
                logger.warning("Vision analysis failed, using common selectors")
                return await self._fill_form_fallback(form_data, submit)

            fields = analysis.get("fields", [])
            if not fields:
                return await self._fill_form_fallback(form_data, submit)

            # Fill each field
            filled_fields = []
            for field in fields:
                field_label = field.get('label', '').lower()
                field_selector = field.get('selector', '')

                if not field_selector:
                    continue

                # Match form_data keys to field labels
                for data_key, data_value in form_data.items():
                    if data_key.lower() in field_label or field_label in data_key.lower():
                        result = await self.type_text(field_selector, data_value, clear_first=True)
                        if result["success"]:
                            filled_fields.append({
                                "field": field_label,
                                "status": "success"
                            })
                        else:
                            filled_fields.append({
                                "field": field_label,
                                "status": "failed",
                                "error": result.get("error")
                            })
                        break

            # Submit form if requested
            if submit:
                submit_result = await self._submit_form()
                return {
                    "success": True,
                    "filled_fields": filled_fields,
                    "submitted": submit_result["success"]
                }

            return {"success": True, "filled_fields": filled_fields}

        except Exception as e:
            logger.error(f"Form filling failed: {e}")
            return {"success": False, "error": str(e)}

    async def _fill_form_fallback(self, form_data: Dict[str, str], submit: bool = False) -> Dict:
        """Fallback form filling using common selectors."""
        filled_fields = []

        # Common selector patterns for form fields
        selector_map = {
            "email": ["input[type='email']", "input[name*='email']", "#email"],
            "password": ["input[type='password']", "input[name*='password']", "#password"],
            "username": ["input[name*='user']", "#username", "input[name*='login']"],
            "name": ["input[name*='name']", "#name"],
            "phone": ["input[type='tel']", "input[name*='phone']"],
            "message": ["textarea", "input[name*='message']"],
        }

        for key, value in form_data.items():
            selectors = selector_map.get(key.lower(), [f"input[name*='{key}']"])

            for selector in selectors:
                try:
                    result = await self.type_text(selector, value, clear_first=True)
                    if result["success"]:
                        filled_fields.append({"field": key, "status": "success"})
                        break
                except:
                    continue

        if submit:
            await self._submit_form()

        return {"success": True, "filled_fields": filled_fields}

    async def _submit_form(self) -> Dict:
        """Submit the current form."""
        try:
            # Try multiple submit strategies
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Submit')",
                "button:has-text('Send')",
                "form button"
            ]

            for selector in submit_selectors:
                try:
                    if self.backend == "playwright":
                        await self.page.click(selector, timeout=2000)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        element.click()
                    logger.info(f"Form submitted via: {selector}")
                    return {"success": True, "method": selector}
                except:
                    continue

            # Fallback: press Enter on first input
            if self.backend == "playwright":
                await self.page.press("input", "Enter")
            else:
                from selenium.webdriver.common.keys import Keys
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if inputs:
                    inputs[0].send_keys(Keys.RETURN)

            return {"success": True, "method": "enter_key"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # DATA EXTRACTION
    # ═══════════════════════════════════════════════════════════

    async def extract_data(self, query: str) -> Dict:
        """
        Extract structured data from page using AI.

        Args:
            query: Description of what to extract
                   Examples: "extract all product prices", "get table data",
                            "find contact info", "list all links"

        Returns:
            Dict with extracted data
        """
        try:
            # Strategy 1: Use browser-use agent for intelligent data extraction
            if self.backend == "browser_use":
                return await self.browser_use_adapter.extract_data(query)

            # Strategy 2: Use vision AI analysis (existing implementation)
            screenshot = await self.capture_screenshot()

            loop = asyncio.get_running_loop()
            from computer_use import analyze_screen

            prompt = f"""
Task: {query}

Analyze this webpage screenshot and extract the requested data.
Return structured JSON with the extracted information.

Example format:
{{
    "data": [...list of extracted items...],
    "count": N,
    "page_title": "...",
    "summary": "brief summary of what was found"
}}

Return ONLY valid JSON, no markdown, no explanation.
"""

            # Use executor to avoid blocking the event loop
            result = await loop.run_in_executor(None, analyze_screen, prompt, screenshot, 0.1)

            if isinstance(result, dict):
                logger.info(f"Data extraction successful: {result.get('count', 'unknown')} items")
                return result
            else:
                return {"data": [], "error": "Invalid response format"}

        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return {"success": False, "error": str(e), "data": []}

    async def get_page_text(self) -> str:
        """Extract all visible text from current page."""
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.get_page_text()
            elif self.backend == "playwright":
                text = await self.page.inner_text("body")
            else:
                text = self.driver.find_element(By.TAG_NAME, "body").text
            return text
        except Exception as e:
            logger.error(f"Get page text failed: {e}")
            return ""

    async def get_element_text(self, selector: str) -> str:
        """Get text content of specific element."""
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.get_element_text(selector)
            elif self.backend == "playwright":
                return await self.page.inner_text(selector)
            else:
                return self.driver.find_element(By.CSS_SELECTOR, selector).text
        except Exception as e:
            logger.error(f"Get element text failed: {e}")
            return ""

    # ═══════════════════════════════════════════════════════════
    # VISION AI INTEGRATION
    # ═══════════════════════════════════════════════════════════

    async def capture_screenshot(self, full_page: bool = False) -> Image.Image:
        """
        Capture screenshot of current page.

        Args:
            full_page: Capture entire page (may be very tall) vs viewport only

        Returns:
            PIL Image object
        """
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.capture_screenshot(full_page)
            elif self.backend == "playwright":
                screenshot_bytes = await self.page.screenshot(full_page=full_page)
                return Image.open(io.BytesIO(screenshot_bytes))
            else:
                # Selenium doesn't support full_page easily, always captures viewport
                png = self.driver.get_screenshot_as_png()
                return Image.open(io.BytesIO(png))
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            # Return blank image as fallback
            return Image.new('RGB', (1920, 1080), color='white')

    async def _vision_find_element(self, screenshot: Image.Image, description: str) -> Optional[Dict]:
        """Use vision AI to find element coordinates on page."""
        try:
            from computer_use import analyze_screen

            prompt = f"""
Find the "{description}" element on this webpage screenshot.
Return the center coordinates where this element is located.

Return JSON in this exact format:
{{
    "found": true,
    "x": 640,
    "y": 400,
    "confidence": 0.9,
    "description": "Found at top-right corner"
}}

If not found:
{{
    "found": false,
    "reason": "Element not visible on page"
}}

Return ONLY valid JSON.
"""

            result = analyze_screen(prompt, screenshot, temperature=0.1)

            if result.get("found"):
                return {
                    "x": result.get("x", 0),
                    "y": result.get("y", 0),
                    "confidence": result.get("confidence", 0)
                }
            else:
                logger.warning(f"Vision AI couldn't find: {description}")
                return None

        except Exception as e:
            logger.error(f"Vision element finding failed: {e}")
            return None

    async def analyze_page_with_vision(self, question: str) -> str:
        """
        Ask AI to analyze current page.

        Args:
            question: Question about the page
                     Examples: "What is the main heading?", "Is this a login page?",
                              "What products are shown?", "Summarize this article"

        Returns:
            String answer from AI
        """
        try:
            # Strategy 1: Use browser-use agent for page analysis
            if self.backend == "browser_use":
                return await self.browser_use_adapter.analyze_page_with_vision(question)

            # Strategy 2: Use traditional vision AI analysis
            screenshot = await self.capture_screenshot()

            loop = asyncio.get_running_loop()
            from computer_use import analyze_screen

            prompt = f"""
Question: {question}

Analyze this webpage screenshot and answer the question.
Return JSON with your answer:
{{
    "answer": "your detailed answer here",
    "page_type": "login page / product page / article / etc",
    "key_elements": ["list of important elements visible"]
}}

Return ONLY valid JSON.
"""

            # Use executor to avoid blocking the event loop
            result = await loop.run_in_executor(None, analyze_screen, prompt, screenshot, 0.3)

            if isinstance(result, dict):
                return result.get("answer", str(result))
            return str(result)

        except Exception as e:
            logger.error(f"Page analysis failed: {e}")
            return f"Analysis error: {e}"

    # ═══════════════════════════════════════════════════════════
    # HELPER UTILITIES
    # ═══════════════════════════════════════════════════════════

    async def wait_for_element(self, selector: str, timeout: int = 5000, state: str = "visible") -> bool:
        """
        Wait for element to appear/disappear.

        Args:
            selector: CSS selector
            timeout: Maximum wait time in milliseconds
            state: "visible", "hidden", "attached"

        Returns:
            True if element reached desired state, False if timeout
        """
        try:
            if self.backend == "playwright":
                await self.page.wait_for_selector(selector, timeout=timeout, state=state)
            else:
                if state == "visible":
                    WebDriverWait(self.driver, timeout/1000).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                    )
                elif state == "hidden":
                    WebDriverWait(self.driver, timeout/1000).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                    )
                else:  # attached
                    WebDriverWait(self.driver, timeout/1000).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
            return True
        except Exception as e:
            logger.warning(f"Wait for element timeout: {selector}")
            return False

    async def scroll_to_element(self, selector: str):
        """Scroll element into view."""
        try:
            if self.backend == "playwright":
                await self.page.locator(selector).scroll_into_view_if_needed()
            else:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
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

            if self.backend == "playwright":
                await self.page.evaluate(script)
            else:
                self.driver.execute_script(script)

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_javascript(self, script: str) -> Any:
        """Execute custom JavaScript on the page."""
        try:
            if self.backend == "playwright":
                return await self.page.evaluate(script)
            else:
                return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return None

    async def get_current_url(self) -> str:
        """Get current page URL."""
        if self.backend == "browser_use":
            return await self.browser_use_adapter.get_current_url()
        elif self.backend == "playwright":
            return self.page.url
        else:
            return self.driver.current_url

    async def get_page_title(self) -> str:
        """Get current page title."""
        try:
            if self.backend == "browser_use":
                return await self.browser_use_adapter.get_page_title()
            elif self.backend == "playwright":
                return await self.page.title()
            else:
                return self.driver.title
        except:
            return ""


# ═══════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════

async def test_browser_automation():
    """Test browser automation features."""
    print("=" * 60)
    print("Browser Automation Engine Test")
    print("=" * 60)

    # Test multiple backends
    backends = ["auto"]
    if PLAYWRIGHT_AVAILABLE:
        backends.append("playwright")
    if BROWSER_USE_AVAILABLE:
        backends.append("browser_use")
    if SELENIUM_AVAILABLE:
        backends.append("selenium")

    for backend in backends:
        print(f"\n{'='*20} Testing {backend} backend {'='*20}")

        try:
            async with BrowserAutomationEngine(backend=backend, headless=False) as browser:
                # Test 1: Navigation
                print(f"\n[TEST 1] Navigating to example.com using {backend}...")
                result = await browser.navigate("https://example.com")
                print(f"  Result: {result}")

                await asyncio.sleep(2)

                # Test 2: Screenshot
                print(f"\n[TEST 2] Capturing screenshot using {backend}...")
                screenshot = await browser.capture_screenshot()
                print(f"  Screenshot size: {screenshot.size}")

                # Test 3: Page analysis
                print(f"\n[TEST 3] Analyzing page with {backend}...")
                analysis = await browser.analyze_page_with_vision("What is the main heading on this page?")
                print(f"  Analysis: {analysis}")

                # Test 4: Click test (will fail on example.com but shows the flow)
                print(f"\n[TEST 4] Attempting to click 'More information' link with {backend}...")
                result = await browser.click_element(text="More information", vision_fallback=True)
                print(f"  Result: {result}")

                await asyncio.sleep(2)

        except Exception as e:
            print(f"  Error testing {backend}: {e}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_browser_automation())
