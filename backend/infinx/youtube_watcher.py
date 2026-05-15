import asyncio
import logging
import json
import re
import os
from typing import Optional
from urllib.parse import urlparse, parse_qs

from browser.global_browser import use_global_browser
from browser.computer_use import analyze_screen
from infinx.youtube_api import YouTubeAPI

logger = logging.getLogger("infinx")

class InfinxAgent:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.caption_buffer = []
        self.last_processed_caption = ""
        self.is_running = False
        self.api = None
        
        # Load API if client_secret exists
        secret_path = os.path.join(os.path.dirname(__file__), "credit", "client_secret_1040128938222-d84ubjl8q6orcr82qmlno9ipcdetujtu.apps.googleusercontent.com.json")
        if os.path.exists(secret_path):
            self.api = YouTubeAPI(secret_path)

    async def start(self):
        self.is_running = True
        logger.info(f"Starting Infinx Agent on {self.target_url}")
        
        if self.api:
            try:
                self.api.authenticate()
                video_id = self._extract_video_id(self.target_url)
                if video_id:
                    self.api.get_live_chat_id(video_id)
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API: {e}. Falling back to Browser-only mode.")
                self.api = None
        
        # We use the global browser so it uses the persistent session
        async with use_global_browser(backend="playwright", headless=False, private_mode=False) as browser:
            await browser.navigate(self.target_url)
            await asyncio.sleep(5)
            
            # Greet the streamer
            greeting = "Hi Bumble bro!"
            if self.api and self.api.live_chat_id:
                self.api.post_message(greeting)
            else:
                await self._post_to_chat_browser(browser, greeting)
            
            # Press 'c' to turn on captions if they aren't already on
            if browser.backend == "playwright":
                await browser.page.keyboard.press("c")
                logger.info("Pressed 'c' to enable auto-captions.")
            
            await self._run_loop(browser)

    def _extract_video_id(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        if parsed.hostname == 'youtu.be':
            return parsed.path[1:]
        if parsed.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed.path == '/watch':
                return parse_qs(parsed.query).get('v', [None])[0]
        return None

    async def _run_loop(self, browser):
        while self.is_running:
            try:
                trigger_found = False
                trigger_context = ""
                
                # 1. Listen via YouTube Data API v3 (Live Chat)
                if self.api and self.api.live_chat_id:
                    chat_messages = self.api.poll_new_messages()
                    for msg in chat_messages:
                        logger.info(f"[Live Chat] {msg['author']}: {msg['text']}")
                        if re.search(r'\b(infin|infin ai agent|agent infin|nivora)\b', msg['text'].lower()):
                            trigger_found = True
                            trigger_context = f"{msg['author']} asked in chat: {msg['text']}"
                            break

                # 2. Listen via Auto-Captions (Browser DOM)
                if not trigger_found:
                    new_text = await self._read_latest_captions(browser)
                    if new_text and new_text != self.last_processed_caption:
                        self.caption_buffer.append(new_text)
                        self.last_processed_caption = new_text
                        if len(self.caption_buffer) > 5:
                            self.caption_buffer.pop(0)

                        combined_text = " ".join(self.caption_buffer).lower()
                        if re.search(r'\b(infin|infin ai agent|agent infin|nivora)\b', combined_text):
                            trigger_found = True
                            trigger_context = f"The streamer said: {combined_text}"
                
                # 3. Action if trigger found
                if trigger_found:
                    logger.info(f"Trigger detected! Context: {trigger_context}")
                    
                    # Take Screenshot
                    logger.info("Taking screenshot of the game...")
                    screenshot_base64 = await browser.capture_screenshot()
                    
                    # Analyze with Nova Pro
                    response = await self._analyze_puzzle(trigger_context, screenshot_base64)
                    
                    if response:
                        # Post to Chat (API first, fallback to browser)
                        success = False
                        if self.api and self.api.live_chat_id:
                            success = self.api.post_message(response)
                            
                        if not success:
                            logger.info("API post failed or not available. Using Browser to type in chat...")
                            await self._post_to_chat_browser(browser, response)
                        
                    # Clear buffer and cooldown
                    self.caption_buffer.clear()
                    await asyncio.sleep(15) 
                        
            except Exception as e:
                logger.error(f"Error in Infinx loop: {e}")
                
            await asyncio.sleep(2) # Polling interval

    async def _read_latest_captions(self, browser) -> str:
        if browser.backend != "playwright":
            return ""
        try:
            js_code = """
            () => {
                const segments = document.querySelectorAll('.ytp-caption-segment');
                if (!segments || segments.length === 0) return '';
                let text = '';
                segments.forEach(seg => text += seg.innerText + ' ');
                return text.trim();
            }
            """
            return await browser.page.evaluate(js_code)
        except Exception:
            return ""

    async def _analyze_puzzle(self, context_text: str, screenshot_base64: str) -> Optional[str]:
        prompt = f"""
        You are INFIN AI AGENT. You are watching bumblebabu's YouTube livestream.
        Context: "{context_text}"
        
        Look at the provided screenshot of his game. Identify the puzzle he is stuck on.
        Provide a SHORT, CONCISE answer suitable for a YouTube live chat. Keep it under 200 characters.
        CRITICAL RULE: You MUST reply in TANGLISH (Tamil language written using English alphabets).
        For example: "Code 1-2-3 mamey, try pannu!" or "Bro, andha red color key ah use pannunga."
        Act friendly, casual, and helpful like a true gaming bro.
        
        Return JSON exactly like this:
        {{"found_puzzle": true/false, "chat_response": "The code is 1-2-3!"}}
        """
        
        logger.info("Analyzing screenshot with Vision AI...")
        result = analyze_screen(prompt, screenshot_base64, temperature=0.3)
        
        if result.get("found_puzzle") and result.get("chat_response"):
            logger.info(f"AI formulated response: {result['chat_response']}")
            return result["chat_response"]
            
        logger.info("AI could not find a clear puzzle to solve or formulate a response.")
        return None

    async def _post_to_chat_browser(self, browser, message: str):
        if browser.backend != "playwright":
            return
        try:
            chat_frame = browser.page.frame_locator('iframe#chatframe')
            input_box = chat_frame.locator('div#input.yt-live-chat-text-input-field-renderer')
            await input_box.click(timeout=5000)
            await asyncio.sleep(0.5)
            await input_box.fill(message)
            await asyncio.sleep(0.5)
            await input_box.press("Enter")
            logger.info("Browser successfully posted to Live Chat!")
        except Exception as e:
            logger.error(f"Browser failed to post to chat: {e}")
