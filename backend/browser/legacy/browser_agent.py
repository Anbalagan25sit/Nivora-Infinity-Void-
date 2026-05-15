"""
browser_agent.py — Friendly Browser Automation Agent

BrowserAgent extends GenericAgent to provide intelligent browser automation capabilities
with a warm, friendly personality. Specializes in web form filling, data extraction,
social media management, and e-commerce assistance.

Features:
- Smart browser automation using Playwright, browser-use, and vision AI
- Friendly, approachable communication style
- Safe automation with user consent for sensitive actions
- Seamless transfers to/from other agents
- Advanced visual element detection and interaction
"""

import logging
from typing import Optional

from livekit.agents.llm import function_tool, ChatContext

from aws_nova_llm import get_nova_pro_llm
from generic_agent import GenericAgent
from browser_agent_prompts import build_browser_agent_instructions

logger = logging.getLogger(__name__)


class BrowserAgent(GenericAgent):
    """
    BrowserAgent — Friendly Browser Automation Assistant

    A warm, helpful agent that specializes in browser automation tasks including:
    - Web form filling and submission
    - Data extraction and scraping
    - Social media management (with user consent)
    - E-commerce assistance and price comparison
    - Website navigation and interaction

    The agent communicates in a friendly, encouraging tone while ensuring
    user safety and consent for sensitive operations.
    """

    def __init__(self, chat_ctx: ChatContext = None, entry_topic: str = None) -> None:
        """
        Initialize BrowserAgent with friendly personality and browser automation tools.

        Args:
            chat_ctx: Shared conversation context from previous agents
            entry_topic: Optional topic that triggered transfer to this agent
        """
        # Build context-aware instructions
        base_instructions = build_browser_agent_instructions(entry_topic)

        transfer_instructions = """

AGENT TRANSFER CAPABILITY:

🔄 **Transfer TO Nivora** for technical/coding questions:
- Code debugging, development, or programming help
- API integration or technical documentation
- Software installation or configuration issues
- Technical tutorials or learning programming concepts

Examples: "Debug this JavaScript", "How does React work?", "Help with my API"

🔄 **Transfer TO Infin** for life management tasks:
- Calendar scheduling and appointments
- Email composition and management
- Note-taking and reminders
- Travel planning and bookings
- Personal task organization

Examples: "Schedule a meeting", "Send an email", "Set a reminder", "Check my calendar"

🌐 **STAY with BrowserAgent** for all web-related tasks:
- Website navigation and browsing
- Form filling and submission
- Online shopping and price comparison
- Social media posting and management
- Web scraping and data extraction
- Website account management
- Online research and information gathering
- E-commerce transactions and order tracking

SCREEN SHARE VISION CAPABILITY:
You have access to the describe_screen_share tool which uses AWS Nova Pro vision AI
to analyze the user's shared screen. This is especially useful for:
- Understanding complex website layouts and forms
- Identifying buttons, links, and interactive elements
- Reading error messages and troubleshooting web issues
- Analyzing e-commerce pages and shopping carts
- Understanding social media interfaces

When user shares screen:
- Proactively offer to analyze it for browser automation opportunities
- Use it to better understand what they want to accomplish
- Combine visual understanding with your automation capabilities

CONVERSATION FLOW:
- Always explain what you're doing in friendly, clear terms
- Ask for confirmation before sensitive actions (purchases, posting, form submission)
- Offer helpful tips and suggestions proactively
- When task is complete, ask if there's anything else you can help with
- Only suggest transfers when the request is clearly outside your domain

CRITICAL: You are a VOICE assistant. Never output <thinking> tags or internal monologue.
Stay friendly, warm, and encouraging in all interactions!
"""

        super().__init__(
            instructions=base_instructions + transfer_instructions,
            llm=get_nova_pro_llm(temperature=0.7),
            chat_ctx=chat_ctx,
            voice_id="browser_jenny_neural",  # Use the mapped voice ID
            agent_name="Browser Assistant"
        )

        # Import browser automation tools
        from tools import (
            # Core browser tools
            web_automate, browser_navigate_and_analyze, fill_web_form,
            browser_extract_data, extract_contact_info, open_website,
            web_search, play_youtube_video, open_youtube,
            # Enhanced browser tools
            browser_visual_click, smart_form_fill_enhanced,
            ecommerce_price_compare, social_media_compose,
            website_data_mining,
            # Utility tools
            describe_screen_share, get_weather,
        )

        # Set up tools for browser automation using update_tools method
        browser_tools = [
            # Core browser automation
            web_automate,
            browser_navigate_and_analyze,
            fill_web_form,
            browser_extract_data,
            extract_contact_info,
            open_website,

            # Enhanced browser automation (browser agent specialization)
            browser_visual_click,
            smart_form_fill_enhanced,
            ecommerce_price_compare,
            social_media_compose,
            website_data_mining,

            # Research and utility
            web_search,
            get_weather,

            # Media (for social media management)
            play_youtube_video,
            open_youtube,

            # Screen analysis
            describe_screen_share,
        ]

        # Use the proper LiveKit method to update tools
        self.update_tools(browser_tools)

        self.entry_topic = entry_topic
        logger.info(f"BrowserAgent initialized with entry topic: {entry_topic}")

    def _get_goodbye_message(self) -> str:
        """Return a friendly goodbye message."""
        return "Thanks for letting me help you browse the web today! Feel free to come back anytime you need assistance with websites, forms, or online tasks. Have a wonderful day! 😊"

    @function_tool
    async def call_nivora_agent(self, topic: str = ""):
        """
        Transfer the conversation to Nivora for technical/coding assistance.

        Args:
            topic: The technical topic or problem the user needs help with
        """
        logger.info(f"BrowserAgent transferring to Nivora with topic: {topic}")

        # Import here to avoid circular imports
        from multi_agent_livekit import NivoraAgent

        # Create Nivora agent with shared context
        nivora_agent = NivoraAgent(
            chat_ctx=self.chat_ctx,
            entry_topic=topic or "technical assistance"
        )

        # Switch voice before transfer
        await nivora_agent.switch_voice()

        # Return agent and friendly handoff message
        transfer_msg = f"I think Nivora would be perfect for helping with {topic}! Let me connect you with our technical specialist." if topic else "Let me connect you with Nivora for technical assistance!"
        return nivora_agent, transfer_msg

    @function_tool
    async def call_infin_agent(self, reason: str = ""):
        """
        Transfer the conversation to Infin for life management assistance.

        Args:
            reason: The reason for transferring (calendar, email, etc.)
        """
        logger.info(f"BrowserAgent transferring to Infin with reason: {reason}")

        # Import here to avoid circular imports
        from multi_agent_livekit import InfinAgent

        # Create Infin agent with shared context
        infin_agent = InfinAgent(
            chat_ctx=self.chat_ctx,
            returning=False
        )

        # Switch voice before transfer
        await infin_agent.switch_voice()

        # Return agent and friendly handoff message
        transfer_msg = f"Infin is perfect for {reason}! Let me connect you with our life management assistant." if reason else "Let me connect you with Infin for life management assistance!"
        return infin_agent, transfer_msg

    @function_tool
    async def browser_visual_click(self, description: str, confirm_action: bool = True) -> str:
        """
        Click an element using visual description and browser-use technology.

        Args:
            description: Visual description of what to click (e.g., "the blue Submit button", "Login link in top right")
            confirm_action: Whether to ask user confirmation for sensitive actions

        Returns:
            Result of the click action
        """
        try:
            if confirm_action and any(word in description.lower() for word in ["submit", "buy", "purchase", "delete", "post"]):
                return f"I found the '{description}' element, but I'd like to confirm before clicking it since it might perform an important action. Should I proceed? Just say 'yes' to continue!"

            # Use the enhanced browser automation engine with visual mode
            from global_browser import use_global_browser

            async with use_global_browser(backend="auto", visual_mode=True) as browser:
                result = await browser.click_element(text=description, vision_fallback=True)

                if result["success"]:
                    method = result.get("method", "unknown")
                    if method == "browser_use_visual":
                        return f"✅ Successfully clicked '{description}' using visual detection! The browser automation worked perfectly."
                    else:
                        return f"✅ Successfully clicked '{description}' using {method} method!"
                else:
                    return f"❌ I couldn't find or click '{description}'. Could you describe it differently or check if the element is visible? Error: {result.get('error', 'Unknown error')}"

        except Exception as e:
            logger.error(f"Visual click failed: {e}")
            return f"I encountered an issue while trying to click '{description}': {str(e)}. Let me try a different approach or you could try manually!"

    @function_tool
    async def smart_form_fill(self, form_data: dict, submit_form: bool = False) -> str:
        """
        Intelligently fill out web forms using visual understanding.

        Args:
            form_data: Dictionary mapping field names to values (e.g., {"email": "user@example.com", "name": "John Doe"})
            submit_form: Whether to submit the form after filling (will ask for confirmation)

        Returns:
            Result of the form filling operation
        """
        try:
            if submit_form:
                return "I can help fill out the form, but I'll need your confirmation before submitting it. Let me fill it out first, then I'll ask if you want me to submit it!"

            # Use enhanced browser automation with visual capabilities
            from global_browser import use_global_browser

            async with use_global_browser(backend="auto", visual_mode=True) as browser:
                result = await browser.fill_form(form_data, submit=False)

                if result["success"]:
                    filled_fields = result.get("filled_fields", [])
                    success_count = sum(1 for field in filled_fields if field.get("status") == "success")
                    total_fields = len(filled_fields)

                    response = f"✅ Great! I successfully filled out {success_count} out of {total_fields} fields in the form!"

                    if success_count < total_fields:
                        failed_fields = [field["field"] for field in filled_fields if field.get("status") != "success"]
                        response += f" I had some trouble with these fields: {', '.join(failed_fields)}. You might need to fill these manually."

                    response += " Would you like me to submit the form now, or do you want to review it first?"
                    return response

                else:
                    return f"❌ I had trouble filling out the form: {result.get('error', 'Unknown error')}. Let me try a different approach or we can fill it step by step!"

        except Exception as e:
            logger.error(f"Smart form fill failed: {e}")
            return f"I encountered an issue while filling the form: {str(e)}. We can try filling it manually field by field if you'd like!"

    @function_tool
    async def extract_page_data(self, query: str) -> str:
        """
        Extract specific data from the current webpage using AI.

        Args:
            query: Description of what data to extract (e.g., "all product prices", "contact information", "article headlines")

        Returns:
            Extracted data formatted for the user
        """
        try:
            from global_browser import use_global_browser

            async with use_global_browser(backend="auto", visual_mode=True) as browser:
                result = await browser.extract_data(query)

                if isinstance(result, dict) and result.get("data"):
                    data_items = result["data"]
                    count = result.get("count", len(data_items) if isinstance(data_items, list) else 1)
                    page_title = result.get("page_title", "this page")

                    response = f"🎯 I found {count} items matching '{query}' on {page_title}:\n\n"

                    if isinstance(data_items, list):
                        for i, item in enumerate(data_items[:10], 1):  # Show first 10 items
                            response += f"{i}. {str(item)}\n"
                        if len(data_items) > 10:
                            response += f"\n... and {len(data_items) - 10} more items!"
                    else:
                        response += str(data_items)

                    response += f"\n\n💡 {result.get('summary', 'Data extraction completed successfully!')}"
                    return response

                else:
                    return f"❌ I couldn't extract '{query}' from this page. The page might not contain that type of information, or it might be in a format that's difficult to parse. Would you like me to try a different approach?"

        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return f"I encountered an issue while extracting '{query}': {str(e)}. Let me try analyzing the page differently!"

    @function_tool
    async def price_comparison(self, product: str, max_sites: int = 5) -> str:
        """
        Compare prices for a product across multiple websites.

        Args:
            product: Product name or description to search for
            max_sites: Maximum number of sites to check (default 5)

        Returns:
            Price comparison results
        """
        try:
            # This is a simplified implementation - in reality, you'd search specific retailer sites
            from global_browser import use_global_browser

            response = f"🛍️ Let me search for the best prices on '{product}' across multiple sites!\n\n"

            # List of popular shopping sites to check
            shopping_sites = [
                "amazon.com",
                "ebay.com",
                "walmart.com",
                "target.com",
                "bestbuy.com"
            ]

            results = []

            async with use_global_browser(backend="auto", visual_mode=True) as browser:
                for site in shopping_sites[:max_sites]:
                    try:
                        # Navigate to site and search for product
                        search_url = f"https://{site}"
                        await browser.navigate(search_url)

                        # Use web search since direct site automation might be complex
                        search_result = await browser.extract_data(f"search results for {product} with prices")

                        if search_result.get("data"):
                            results.append(f"✅ {site}: Found results")
                        else:
                            results.append(f"❌ {site}: No clear results")

                    except Exception as site_error:
                        results.append(f"❌ {site}: Could not access")
                        continue

            response += "\n".join(results)
            response += f"\n\n💡 For the most accurate and up-to-date pricing, I recommend visiting these sites directly and searching for '{product}'. Each site may have different deals, shipping options, and availability!"

            return response

        except Exception as e:
            logger.error(f"Price comparison failed: {e}")
            return f"I had trouble comparing prices for '{product}': {str(e)}. You might want to manually check your favorite shopping sites for the best deals!"

    @function_tool
    async def social_media_post(self, platform: str, content: str, confirm_post: bool = True) -> str:
        """
        Help compose and post content to social media platforms (with user confirmation).

        Args:
            platform: Social media platform (e.g., "LinkedIn", "Twitter", "Facebook")
            content: Content to post
            confirm_post: Whether to require confirmation before posting (recommended)

        Returns:
            Result of the social media posting
        """
        try:
            if confirm_post:
                return f"""📱 I can help you post to {platform}! Here's what I've prepared:

**Content:** "{content}"

**⚠️ IMPORTANT CONFIRMATION NEEDED:**
Before I post this to your {platform} account, please confirm:
1. You're logged into the correct {platform} account
2. This content represents you appropriately
3. You want this posted publicly (or to your selected audience)

Just say "yes, post it" and I'll proceed with posting to {platform}!

*Note: I'll navigate to {platform}, compose the post, and show you a preview before final submission.*"""

            # If confirmation bypassed, attempt to post
            from global_browser import use_global_browser

            async with use_global_browser(backend="auto", visual_mode=True) as browser:
                # Navigate to the platform
                platform_urls = {
                    "linkedin": "https://linkedin.com",
                    "twitter": "https://twitter.com",
                    "facebook": "https://facebook.com",
                    "instagram": "https://instagram.com"
                }

                platform_key = platform.lower()
                if platform_key not in platform_urls:
                    return f"❌ I don't have posting support for {platform} yet. I can help with LinkedIn, Twitter, Facebook, and Instagram."

                await browser.navigate(platform_urls[platform_key])

                # This is a simplified implementation - real social media posting would need
                # specific form handling for each platform
                result = await browser.fill_form({
                    "post_content": content,
                    "status": content
                }, submit=False)

                return f"✅ I've helped compose your post for {platform}! The content has been prepared but you'll need to review and submit it manually for safety. This ensures your post looks exactly how you want it!"

        except Exception as e:
            logger.error(f"Social media posting failed: {e}")
            return f"I had trouble with your {platform} post: {str(e)}. Social media platforms have complex interfaces, so you might need to post this manually. I can help you optimize the content though!"