"""
social_automation.py — Advanced Social Media Browser Automation
Enables Instagram DMs, Twitter DMs, WhatsApp, and more using vision AI + Playwright.

Features:
- Instagram: Open profile, send DM, like posts, follow users, story viewer
- Twitter/X: Send DM, tweet, like, retweet, follow
- WhatsApp Web: Send message to contact
- LinkedIn: Send connection request, message

All automation uses vision AI (Nova Pro) to intelligently find and interact with UI elements.
"""

import asyncio
import logging
import os
import re
import urllib.parse
from typing import Dict, Optional, Annotated, Literal

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════


@function_tool()
async def instagram_login(context: RunContext) -> str:
    """
    Open the Instagram login page and wait for the user to manually log in.
    USE THIS TOOL when the user explicitly asks to log in to Instagram, or asks to log in to the 'nivora_dev' account.
    """
    try:
        from global_browser import use_global_browser
        import asyncio
        logger.info("[Instagram] Opening login page")
        
        async with use_global_browser(backend="auto", headless=False) as browser:
            await browser.navigate("https://www.instagram.com/accounts/login/")
            
            for _ in range(45):
                await asyncio.sleep(2)
                try:
                    current_url = await browser.get_current_url()
                    if "accounts/login" not in current_url:
                        return "Successfully logged into Instagram! The session is now saved and I can send DMs."
                except:
                    pass
                    
            return "Opened the Instagram login page. Please log in manually. Let me know when you are done."
            
    except Exception as e:
        logger.error(f"[Instagram] Login error: {e}")
        return f"Failed to open login page: {e}"


@function_tool()
async def instagram_open_profile(
    context: RunContext,
    username: Annotated[str, "Instagram username (without @). E.g. 'cristiano', 'therock'"],
) -> str:
    """
    Open an Instagram profile in the browser.

    Examples:
    - instagram_open_profile("cristiano") - Opens Cristiano Ronaldo's profile
    - instagram_open_profile("therock") - Opens The Rock's profile
    """
    try:
        from global_browser import use_global_browser

        # Clean username
        username = username.strip().lstrip("@")
        url = f"https://www.instagram.com/{username}/"

        logger.info(f"[Instagram] Opening profile: {username}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            result = await browser.navigate(url)

            if not result["success"]:
                return f"Failed to open Instagram profile: {result.get('error')}"

            await asyncio.sleep(3)  # Let page load

            # Analyze the profile page
            screenshot = await browser.capture_screenshot()
            from computer_use import analyze_screen

            analysis = analyze_screen(
                """Analyze this Instagram profile page. Return JSON with:
                {
                    "username": "the username shown",
                    "display_name": "full name if visible",
                    "followers": "follower count",
                    "following": "following count",
                    "posts": "post count",
                    "bio": "bio text if visible",
                    "is_private": true/false,
                    "is_verified": true/false,
                    "profile_loaded": true/false
                }
                Return ONLY valid JSON.""",
                screenshot,
                temperature=0.1
            )

            if analysis.get("profile_loaded", False):
                name = analysis.get("display_name", username)
                followers = analysis.get("followers", "?")
                verified = " (Verified)" if analysis.get("is_verified") else ""
                private = " [Private Account]" if analysis.get("is_private") else ""

                return (
                    f"Opened Instagram profile: @{username}{verified}{private}\n"
                    f"Name: {name}\n"
                    f"Followers: {followers}\n"
                    f"Bio: {analysis.get('bio', 'N/A')}"
                )
            else:
                return f"Opened Instagram page for @{username}. Profile may require login to view."

    except Exception as e:
        logger.error(f"[Instagram] Profile open error: {e}")
        return f"Failed to open Instagram profile: {e}"


@function_tool()
async def instagram_send_dm(
    context: RunContext,
    username: Annotated[str, "Instagram username to DM (without @). E.g. 'cristiano'"],
    message: Annotated[str, "Message to send"],
) -> str:
    """
    Send a Direct Message on Instagram using browser automation with vision AI.

    IMPORTANT: Requires you to be logged into Instagram in your browser.

    Examples:
    - instagram_send_dm("friend_username", "Hey! How are you?")
    - instagram_send_dm("business_account", "I'm interested in your product")

    The tool will:
    1. Navigate to the user's profile
    2. Click the "Message" button
    3. Type and send your message
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        username = username.strip().lstrip("@")

        logger.info(f"[Instagram] Sending DM to: {username}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            # Step 1: Go to user's profile
            profile_url = f"https://www.instagram.com/{username}/"
            result = await browser.navigate(profile_url)

            if not result["success"]:
                return f"Failed to navigate to @{username}'s profile"

            await asyncio.sleep(3)

            # Step 2: Find and click Message button
            screenshot = await browser.capture_screenshot()

            # Use vision to find the Message button
            button_prompt = """
            Find the "Message" button on this Instagram profile page.
            Return JSON with:
            {
                "found": true/false,
                "button_selector": "CSS selector or description of the button",
                "button_text": "exact text on the button",
                "x": center X coordinate,
                "y": center Y coordinate,
                "login_required": true/false,
                "reason": "why button wasn't found if not found"
            }
            Return ONLY valid JSON.
            """

            button_analysis = analyze_screen(button_prompt, screenshot, temperature=0.1)

            if not button_analysis.get("found", False):
                reason = button_analysis.get("reason", "Message button not found")
                if button_analysis.get("login_required"):
                    return "You need to be logged into Instagram to send DMs. Please log in first."
                return f"Could not find Message button for @{username}: {reason}"

            # Dismiss any annoying popups (like "Turn on Notifications") before clicking
            if browser.backend == "playwright":
                try:
                    not_now_count = await browser.page.get_by_text("Not Now", exact=True).count()
                    if not_now_count > 0:
                        logger.info("[Instagram] Found 'Not Now' popup, dismissing it.")
                        await browser.page.get_by_text("Not Now", exact=True).first.click()
                        await asyncio.sleep(1)
                except Exception as e:
                    pass

            # Step 2: Try exact text-based click first to avoid clicking sidebar "Messages"
            click_success = False
            if browser.backend == "playwright":
                try:
                    # Look specifically for exact "Message" text in a button or link
                    await browser.page.locator("text=\"Message\" >> visible=true").filter(has_text=re.compile(r"^Message$")).first.click(timeout=3000)
                    click_success = True
                except Exception:
                    try:
                        await browser.page.get_by_role("button", name="Message", exact=True).click(timeout=3000)
                        click_success = True
                    except Exception:
                        pass
            
            if not click_success:
                # Fallback to vision coordinates
                x, y = button_analysis.get("x", 0), button_analysis.get("y", 0)
                if x and y:
                    await browser.click_at_coordinates(x, y)
                    click_success = True
                    
            await asyncio.sleep(3)
            
            # Check if we successfully navigated to the direct messages page
            if browser.backend == "playwright":
                current_url = await browser.get_current_url()
                if "/direct/" not in current_url:
                    # Click didn't work, try a direct navigation approach as fallback
                    logger.warning(f"[Instagram] Click failed to open chat. Trying direct navigation to Inbox.")
                    await browser.navigate(f"https://www.instagram.com/direct/new/")
                    await asyncio.sleep(4)
                    
                    # On the new message page, search for the user
                    try:
                        await browser.page.get_by_role("button", name="Send message", exact=True).click(timeout=3000)
                    except:
                        pass
                    await asyncio.sleep(1)
                    
                    try:
                        # Search for user
                        await browser.page.get_by_placeholder("Search...").fill(username)
                        await asyncio.sleep(2)
                        
                        # Click the first user in the list
                        await browser.page.locator("input[type='checkbox']").first.click()
                        await asyncio.sleep(1)
                        
                        # Click Chat button
                        await browser.page.get_by_role("button", name="Chat").click()
                        await asyncio.sleep(3)
                        current_url = await browser.get_current_url()
                    except Exception as e:
                        return f"Failed to open DM chat with @{username} via direct new message fallback. Error: {str(e)}"
                        
                if "/direct/" not in current_url:
                    return f"Failed to open DM chat with @{username}. Navigation did not succeed."

            # Step 3: Wait for DM dialog/chat to open and type message
            screenshot = await browser.capture_screenshot()

            input_prompt = """
            Find the message input field in this Instagram DM chat.
            Return JSON with:
            {
                "chat_opened": true/false,
                "input_selector": "CSS selector for message input",
                "input_placeholder": "placeholder text of the input",
                "x": center X coordinate of input,
                "y": center Y coordinate of input
            }
            Return ONLY valid JSON.
            """

            input_analysis = analyze_screen(input_prompt, screenshot, temperature=0.1)

            if not input_analysis.get("chat_opened", False):
                return f"DM chat with @{username} didn't open properly. They may have DMs restricted."

            # Click on input field
            input_x, input_y = input_analysis.get("x", 0), input_analysis.get("y", 0)
            if input_x and input_y:
                await browser.click_at_coordinates(input_x, input_y)
                await asyncio.sleep(0.5)

            # Type the message
            # Try common Instagram DM input selectors
            selectors_to_try = [
                "textarea[placeholder*='Message']",
                "div[contenteditable='true']",
                "input[placeholder*='Message']",
                "textarea",
            ]

            typed = False
            for selector in selectors_to_try:
                try:
                    # Fail fast if element doesn't exist (avoid 30s timeout)
                    if browser.backend == "playwright":
                        count = await browser.page.locator(selector).count()
                        if count == 0:
                            continue
                            
                    result = await browser.type_text(selector, message, clear_first=True, press_enter=False)
                    if result.get("success"):
                        typed = True
                        break
                except:
                    continue

            if not typed:
                # Fallback: just type after clicking
                if browser.backend == "playwright":
                    await browser.page.keyboard.type(message, delay=30)
                    typed = True

            await asyncio.sleep(0.5)

            # Step 4: Send the message (press Enter or click Send)
            if browser.backend == "playwright":
                await browser.page.keyboard.press("Enter")

            await asyncio.sleep(1)

            # Verify message was sent
            screenshot = await browser.capture_screenshot()
            verify_prompt = f"""
            Check if the message "{message[:50]}..." was sent successfully.
            Look for the message in the chat window.
            Return JSON with:
            {{
                "message_sent": true/false,
                "message_visible": true/false,
                "error": "any error message visible"
            }}
            Return ONLY valid JSON.
            """

            verify = analyze_screen(verify_prompt, screenshot, temperature=0.1)

            if verify.get("message_sent", False) or verify.get("message_visible", False):
                return f"Message sent to @{username}: \"{message}\""
            else:
                error = verify.get("error", "Unknown")
                return f"Message may not have been sent. Error: {error}"

    except Exception as e:
        logger.error(f"[Instagram] DM error: {e}", exc_info=True)
        return f"Failed to send Instagram DM: {e}"


@function_tool()
async def instagram_search_and_dm(
    context: RunContext,
    search_query: Annotated[str, "Name or username to search for"],
    message: Annotated[str, "Message to send"],
) -> str:
    """
    Search for a user on Instagram and send them a DM.
    Useful when you don't know the exact username.

    Examples:
    - instagram_search_and_dm("John Smith NYC", "Hey John! It was great meeting you.")
    - instagram_search_and_dm("Tesla official", "Interested in partnership")
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        logger.info(f"[Instagram] Searching for: {search_query}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            # Go to Instagram
            await browser.navigate("https://www.instagram.com/")
            await asyncio.sleep(3)

            # Click search icon/bar
            screenshot = await browser.capture_screenshot()

            search_prompt = """
            Find the search bar or search icon on this Instagram page.
            Return JSON with:
            {
                "found": true/false,
                "x": center X coordinate,
                "y": center Y coordinate,
                "type": "icon" or "input"
            }
            Return ONLY valid JSON.
            """

            search_result = analyze_screen(search_prompt, screenshot, temperature=0.1)

            if not search_result.get("found"):
                return "Could not find Instagram search. Make sure you're logged in."

            # Click search
            await browser.click_at_coordinates(search_result["x"], search_result["y"])
            await asyncio.sleep(1)

            # Type search query
            if browser.backend == "playwright":
                await browser.page.keyboard.type(search_query, delay=50)

            await asyncio.sleep(2)

            # Find and click first result
            screenshot = await browser.capture_screenshot()

            result_prompt = f"""
            Find the first user search result for "{search_query}" in the search dropdown.
            Return JSON with:
            {{
                "found": true/false,
                "username": "the username shown",
                "display_name": "the display name",
                "x": center X coordinate,
                "y": center Y coordinate
            }}
            Return ONLY valid JSON.
            """

            result_analysis = analyze_screen(result_prompt, screenshot, temperature=0.1)

            if not result_analysis.get("found"):
                return f"No results found for '{search_query}'"

            found_username = result_analysis.get("username", search_query)

            # Click the result
            await browser.click_at_coordinates(result_analysis["x"], result_analysis["y"])
            await asyncio.sleep(2)

            # Now we're on the profile - find and click Message button
            screenshot = await browser.capture_screenshot()

            msg_button_prompt = """
            Find the "Message" button on this Instagram profile.
            Return JSON with:
            {
                "found": true/false,
                "x": center X coordinate,
                "y": center Y coordinate
            }
            Return ONLY valid JSON.
            """

            msg_button = analyze_screen(msg_button_prompt, screenshot, temperature=0.1)

            if not msg_button.get("found"):
                return f"Found @{found_username} but couldn't find Message button. They may have DMs restricted."

            # Click Message
            await browser.click_at_coordinates(msg_button["x"], msg_button["y"])
            await asyncio.sleep(2)

            # Type and send message
            if browser.backend == "playwright":
                await browser.page.keyboard.type(message, delay=30)
                await asyncio.sleep(0.5)
                await browser.page.keyboard.press("Enter")

            await asyncio.sleep(1)

            return f"Message sent to @{found_username}: \"{message}\""

    except Exception as e:
        logger.error(f"[Instagram] Search and DM error: {e}")
        return f"Failed to search and DM: {e}"


@function_tool()
async def instagram_like_recent_posts(
    context: RunContext,
    username: Annotated[str, "Instagram username (without @)"],
    count: Annotated[int, "Number of posts to like (1-10)"] = 3,
) -> str:
    """
    Like the most recent posts from an Instagram user.

    Examples:
    - instagram_like_recent_posts("friend_username", 3) - Like their 3 most recent posts
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        username = username.strip().lstrip("@")
        count = max(1, min(10, count))  # Limit 1-10

        logger.info(f"[Instagram] Liking {count} posts from @{username}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            # Go to profile
            await browser.navigate(f"https://www.instagram.com/{username}/")
            await asyncio.sleep(3)

            liked_count = 0

            for i in range(count):
                # Find posts grid
                screenshot = await browser.capture_screenshot()

                post_prompt = f"""
                Find post #{i+1} in the Instagram posts grid (reading left to right, top to bottom).
                Return JSON with:
                {{
                    "found": true/false,
                    "x": center X coordinate of the post thumbnail,
                    "y": center Y coordinate of the post thumbnail
                }}
                Return ONLY valid JSON.
                """

                post_result = analyze_screen(post_prompt, screenshot, temperature=0.1)

                if not post_result.get("found"):
                    break

                # Click post to open it
                await browser.click_at_coordinates(post_result["x"], post_result["y"])
                await asyncio.sleep(1.5)

                # Find and click like button (heart)
                screenshot = await browser.capture_screenshot()

                like_prompt = """
                Find the like button (heart icon) for this Instagram post.
                The heart should be below the image, near comment and share icons.
                Check if it's already liked (filled red heart).
                Return JSON with:
                {
                    "found": true/false,
                    "already_liked": true/false,
                    "x": center X coordinate,
                    "y": center Y coordinate
                }
                Return ONLY valid JSON.
                """

                like_result = analyze_screen(like_prompt, screenshot, temperature=0.1)

                if like_result.get("found") and not like_result.get("already_liked"):
                    await browser.click_at_coordinates(like_result["x"], like_result["y"])
                    liked_count += 1
                    await asyncio.sleep(0.5)

                # Close post (click X or press Escape)
                if browser.backend == "playwright":
                    await browser.page.keyboard.press("Escape")

                await asyncio.sleep(1)

            return f"Liked {liked_count} posts from @{username}"

    except Exception as e:
        logger.error(f"[Instagram] Like posts error: {e}")
        return f"Failed to like posts: {e}"


@function_tool()
async def instagram_follow_user(
    context: RunContext,
    username: Annotated[str, "Instagram username to follow (without @)"],
) -> str:
    """
    Follow an Instagram user.

    Examples:
    - instagram_follow_user("nasa") - Follow NASA's account
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        username = username.strip().lstrip("@")

        logger.info(f"[Instagram] Following @{username}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            await browser.navigate(f"https://www.instagram.com/{username}/")
            await asyncio.sleep(3)

            screenshot = await browser.capture_screenshot()

            follow_prompt = """
            Find the Follow button on this Instagram profile.
            Check if already following (button says "Following" or "Requested").
            Return JSON with:
            {
                "found": true/false,
                "button_text": "Follow" or "Following" or "Requested",
                "already_following": true/false,
                "x": center X coordinate,
                "y": center Y coordinate
            }
            Return ONLY valid JSON.
            """

            follow_result = analyze_screen(follow_prompt, screenshot, temperature=0.1)

            if follow_result.get("already_following"):
                return f"You're already following @{username}"

            if not follow_result.get("found"):
                return f"Could not find Follow button for @{username}"

            await browser.click_at_coordinates(follow_result["x"], follow_result["y"])
            await asyncio.sleep(1)

            return f"Now following @{username}!"

    except Exception as e:
        logger.error(f"[Instagram] Follow error: {e}")
        return f"Failed to follow: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# TWITTER/X AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════

@function_tool()
async def twitter_send_dm(
    context: RunContext,
    username: Annotated[str, "Twitter/X username (without @)"],
    message: Annotated[str, "Message to send"],
) -> str:
    """
    Send a Direct Message on Twitter/X using browser automation.

    IMPORTANT: Requires you to be logged into Twitter/X in your browser.

    Examples:
    - twitter_send_dm("elonmusk", "Great thread on AI!")
    - twitter_send_dm("friend_handle", "Hey, let's catch up!")
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        username = username.strip().lstrip("@")

        logger.info(f"[Twitter] Sending DM to: @{username}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            # Go directly to messages with this user
            dm_url = f"https://twitter.com/messages/compose?recipient_id={username}"
            # Alternative: Go to profile first
            profile_url = f"https://twitter.com/{username}"

            await browser.navigate(profile_url)
            await asyncio.sleep(3)

            screenshot = await browser.capture_screenshot()

            # Find Message button on profile
            msg_prompt = """
            Find the Message button/icon on this Twitter profile.
            It's usually an envelope icon near the Follow button.
            Return JSON with:
            {
                "found": true/false,
                "x": center X coordinate,
                "y": center Y coordinate,
                "login_required": true/false
            }
            Return ONLY valid JSON.
            """

            msg_result = analyze_screen(msg_prompt, screenshot, temperature=0.1)

            if msg_result.get("login_required"):
                return "Please log into Twitter/X first to send DMs."

            if not msg_result.get("found"):
                return f"Could not find Message option for @{username}. They may have DMs closed."

            await browser.click_at_coordinates(msg_result["x"], msg_result["y"])
            await asyncio.sleep(2)

            # Type message
            screenshot = await browser.capture_screenshot()

            input_prompt = """
            Find the message input field in this Twitter DM conversation.
            Return JSON with:
            {
                "found": true/false,
                "x": center X coordinate,
                "y": center Y coordinate
            }
            Return ONLY valid JSON.
            """

            input_result = analyze_screen(input_prompt, screenshot, temperature=0.1)

            if input_result.get("found"):
                await browser.click_at_coordinates(input_result["x"], input_result["y"])
                await asyncio.sleep(0.3)

            if browser.backend == "playwright":
                await browser.page.keyboard.type(message, delay=30)
                await asyncio.sleep(0.5)

                # Find and click Send button or press Enter
                await browser.page.keyboard.press("Enter")

            await asyncio.sleep(1)

            return f"DM sent to @{username}: \"{message}\""

    except Exception as e:
        logger.error(f"[Twitter] DM error: {e}")
        return f"Failed to send Twitter DM: {e}"


@function_tool()
async def twitter_post_tweet(
    context: RunContext,
    tweet_text: Annotated[str, "The tweet content (max 280 characters)"],
) -> str:
    """
    Post a tweet on Twitter/X.

    Examples:
    - twitter_post_tweet("Just discovered something amazing!")
    - twitter_post_tweet("Check out my new project: example.com")
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        if len(tweet_text) > 280:
            return f"Tweet too long ({len(tweet_text)} chars). Max is 280."

        logger.info(f"[Twitter] Posting tweet: {tweet_text[:50]}...")

        async with use_global_browser(backend="auto", headless=False) as browser:
            await browser.navigate("https://twitter.com/compose/tweet")
            await asyncio.sleep(3)

            # Type the tweet
            if browser.backend == "playwright":
                await browser.page.keyboard.type(tweet_text, delay=20)

            await asyncio.sleep(1)

            # Find and click Post button
            screenshot = await browser.capture_screenshot()

            post_prompt = """
            Find the "Post" button to publish this tweet.
            Return JSON with:
            {
                "found": true/false,
                "x": center X coordinate,
                "y": center Y coordinate
            }
            Return ONLY valid JSON.
            """

            post_result = analyze_screen(post_prompt, screenshot, temperature=0.1)

            if post_result.get("found"):
                await browser.click_at_coordinates(post_result["x"], post_result["y"])
                await asyncio.sleep(2)
                return f"Tweet posted: \"{tweet_text}\""
            else:
                return "Could not find Post button. Tweet may not have been posted."

    except Exception as e:
        logger.error(f"[Twitter] Tweet error: {e}")
        return f"Failed to post tweet: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# WHATSAPP WEB AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════

@function_tool()
async def whatsapp_send_message(
    context: RunContext,
    contact_name: Annotated[str, "Contact name as it appears in WhatsApp"],
    message: Annotated[str, "Message to send"],
) -> str:
    """
    Send a WhatsApp message using WhatsApp Web.

    IMPORTANT: Requires WhatsApp Web to be linked to your phone.

    Examples:
    - whatsapp_send_message("Mom", "I'll be home for dinner!")
    - whatsapp_send_message("Work Group", "Meeting at 3pm")
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        logger.info(f"[WhatsApp] Sending to: {contact_name}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            await browser.navigate("https://web.whatsapp.com/")
            await asyncio.sleep(5)  # WhatsApp Web loads slowly

            screenshot = await browser.capture_screenshot()

            # Check if logged in
            login_check_prompt = """
            Check if WhatsApp Web is logged in and showing the chat list.
            Return JSON with:
            {
                "logged_in": true/false,
                "qr_code_visible": true/false,
                "search_visible": true/false
            }
            Return ONLY valid JSON.
            """

            login_status = analyze_screen(login_check_prompt, screenshot, temperature=0.1)

            if login_status.get("qr_code_visible"):
                return "Please scan the QR code with your phone to log into WhatsApp Web."

            if not login_status.get("logged_in"):
                return "WhatsApp Web not logged in. Please scan QR code first."

            # Search for contact
            search_prompt = """
            Find the search bar to search for contacts in WhatsApp Web.
            Return JSON with:
            {
                "found": true/false,
                "x": center X coordinate,
                "y": center Y coordinate
            }
            Return ONLY valid JSON.
            """

            search_result = analyze_screen(search_prompt, screenshot, temperature=0.1)

            if search_result.get("found"):
                await browser.click_at_coordinates(search_result["x"], search_result["y"])
                await asyncio.sleep(0.5)

                if browser.backend == "playwright":
                    await browser.page.keyboard.type(contact_name, delay=50)

                await asyncio.sleep(2)

                # Click on the contact
                screenshot = await browser.capture_screenshot()

                contact_prompt = f"""
                Find the contact "{contact_name}" in the search results.
                Return JSON with:
                {{
                    "found": true/false,
                    "x": center X coordinate,
                    "y": center Y coordinate
                }}
                Return ONLY valid JSON.
                """

                contact_result = analyze_screen(contact_prompt, screenshot, temperature=0.1)

                if contact_result.get("found"):
                    await browser.click_at_coordinates(contact_result["x"], contact_result["y"])
                    await asyncio.sleep(1)
                else:
                    return f"Could not find contact: {contact_name}"

            # Type message
            if browser.backend == "playwright":
                await browser.page.keyboard.type(message, delay=30)
                await asyncio.sleep(0.5)
                await browser.page.keyboard.press("Enter")

            await asyncio.sleep(1)

            return f"WhatsApp message sent to {contact_name}: \"{message}\""

    except Exception as e:
        logger.error(f"[WhatsApp] Error: {e}")
        return f"Failed to send WhatsApp message: {e}"


@function_tool()
async def whatsapp_send_to_number(
    context: RunContext,
    phone_number: Annotated[str, "Phone number with country code (e.g., +1234567890)"],
    message: Annotated[str, "Message to send"],
) -> str:
    """
    Send a WhatsApp message to a phone number (even if not in contacts).

    Examples:
    - whatsapp_send_to_number("+14155551234", "Hello from Nivora!")
    """
    try:
        import webbrowser

        # Clean phone number
        phone = re.sub(r'[^\d+]', '', phone_number)
        if not phone.startswith('+'):
            phone = '+' + phone

        # Remove the + for the URL
        phone_clean = phone.lstrip('+')

        # URL encode the message
        encoded_message = urllib.parse.quote(message)

        # WhatsApp Click-to-Chat URL
        url = f"https://wa.me/{phone_clean}?text={encoded_message}"

        logger.info(f"[WhatsApp] Opening chat with: {phone}")
        webbrowser.open(url)

        return f"Opened WhatsApp chat with {phone_number}. Click 'Send' to deliver the message."

    except Exception as e:
        logger.error(f"[WhatsApp] Error: {e}")
        return f"Failed to open WhatsApp: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# LINKEDIN AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════

@function_tool()
async def linkedin_send_message(
    context: RunContext,
    profile_url: Annotated[str, "LinkedIn profile URL or search name"],
    message: Annotated[str, "Message to send"],
) -> str:
    """
    Send a LinkedIn message to a connection.

    IMPORTANT: Must be logged into LinkedIn and connected with the person.

    Examples:
    - linkedin_send_message("https://linkedin.com/in/johndoe", "Hi John, great connecting!")
    - linkedin_send_message("John Doe CEO TechCorp", "Interested in discussing partnership")
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen

        logger.info(f"[LinkedIn] Messaging: {profile_url}")

        async with use_global_browser(backend="auto", headless=False) as browser:
            # Navigate to profile
            if profile_url.startswith("http"):
                await browser.navigate(profile_url)
            else:
                # Search for the person
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(profile_url)}"
                await browser.navigate(search_url)
                await asyncio.sleep(3)

                # Click first result
                screenshot = await browser.capture_screenshot()

                result_prompt = """
                Find the first person result in this LinkedIn search.
                Return JSON with:
                {
                    "found": true/false,
                    "name": "person's name",
                    "x": center X coordinate to click,
                    "y": center Y coordinate to click
                }
                Return ONLY valid JSON.
                """

                result = analyze_screen(result_prompt, screenshot, temperature=0.1)

                if result.get("found"):
                    await browser.click_at_coordinates(result["x"], result["y"])
                else:
                    return f"Could not find person: {profile_url}"

            await asyncio.sleep(3)

            # Find Message button
            screenshot = await browser.capture_screenshot()

            msg_prompt = """
            Find the "Message" button on this LinkedIn profile.
            Return JSON with:
            {
                "found": true/false,
                "x": center X coordinate,
                "y": center Y coordinate,
                "not_connected": true/false
            }
            Return ONLY valid JSON.
            """

            msg_result = analyze_screen(msg_prompt, screenshot, temperature=0.1)

            if msg_result.get("not_connected"):
                return "You're not connected with this person. Send a connection request first."

            if not msg_result.get("found"):
                return "Could not find Message button."

            await browser.click_at_coordinates(msg_result["x"], msg_result["y"])
            await asyncio.sleep(2)

            # Type and send message
            if browser.backend == "playwright":
                await browser.page.keyboard.type(message, delay=30)
                await asyncio.sleep(0.5)

                # Find Send button
                screenshot = await browser.capture_screenshot()

                send_prompt = """
                Find the "Send" button in this LinkedIn message dialog.
                Return JSON with:
                {
                    "found": true/false,
                    "x": center X coordinate,
                    "y": center Y coordinate
                }
                Return ONLY valid JSON.
                """

                send_result = analyze_screen(send_prompt, screenshot, temperature=0.1)

                if send_result.get("found"):
                    await browser.click_at_coordinates(send_result["x"], send_result["y"])

            await asyncio.sleep(1)

            return f"LinkedIn message sent: \"{message}\""

    except Exception as e:
        logger.error(f"[LinkedIn] Error: {e}")
        return f"Failed to send LinkedIn message: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# UNIVERSAL SOCIAL TOOL
# ═══════════════════════════════════════════════════════════════════════════════

@function_tool()
async def social_dm(
    context: RunContext,
    platform: Annotated[Literal["instagram", "twitter", "whatsapp", "linkedin"], "Social media platform"],
    recipient: Annotated[str, "Username, contact name, or phone number"],
    message: Annotated[str, "Message to send"],
) -> str:
    """
    Universal social media DM tool. Routes to the appropriate platform.

    Platforms: instagram, twitter, whatsapp, linkedin

    Examples:
    - social_dm("instagram", "friend_username", "Hey!")
    - social_dm("twitter", "elonmusk", "Great tweet!")
    - social_dm("whatsapp", "Mom", "Coming home soon")
    - social_dm("linkedin", "recruiter_name", "Thanks for reaching out")
    """
    platform = platform.lower()

    if platform == "instagram":
        return await instagram_send_dm(context, recipient, message)
    elif platform == "twitter":
        return await twitter_send_dm(context, recipient, message)
    elif platform == "whatsapp":
        if recipient.startswith("+") or recipient[0].isdigit():
            return await whatsapp_send_to_number(context, recipient, message)
        else:
            return await whatsapp_send_message(context, recipient, message)
    elif platform == "linkedin":
        return await linkedin_send_message(context, recipient, message)
    else:
        return f"Unknown platform: {platform}. Use: instagram, twitter, whatsapp, linkedin"


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT ALL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════





@function_tool()
async def instagram_comment_on_recent_post(
    context: RunContext,
    username: Annotated[str, "Instagram username (without @)"],
    comment_text: Annotated[str, "The comment to post"],
) -> str:
    """
    Comment on the most recent post of an Instagram user.
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen
        
        username = username.strip().lstrip("@")
        logger.info(f"[Instagram] Commenting on {username}'s recent post")
        
        async with use_global_browser(backend="auto") as browser:
            await browser.navigate(f"https://www.instagram.com/{username}/")
            await asyncio.sleep(3)
            
            screenshot = await browser.capture_screenshot()
            post_prompt = """
            Find the first (most recent) post in the Instagram posts grid.
            Return JSON with: {"found": true/false, "x": center X, "y": center Y}
            Return ONLY valid JSON.
            """
            post_result = analyze_screen(post_prompt, screenshot, temperature=0.1)
            
            if not post_result.get("found"):
                return f"Could not find any posts for @{username}"
                
            await browser.click_at_coordinates(post_result["x"], post_result["y"])
            await asyncio.sleep(2)
            
            screenshot = await browser.capture_screenshot()
            comment_prompt = """
            Find the "Add a comment..." input field on this Instagram post.
            Return JSON with: {"found": true/false, "x": center X, "y": center Y}
            Return ONLY valid JSON.
            """
            comment_result = analyze_screen(comment_prompt, screenshot, temperature=0.1)
            
            if not comment_result.get("found"):
                return "Could not find comment input field. Comments may be disabled."
                
            await browser.click_at_coordinates(comment_result["x"], comment_result["y"])
            await asyncio.sleep(0.5)
            
            if browser.backend == "playwright":
                await browser.page.keyboard.type(comment_text, delay=30)
                await asyncio.sleep(0.5)
                await browser.page.keyboard.press("Enter")
                
            await asyncio.sleep(2)
            
            if browser.backend == "playwright":
                await browser.page.keyboard.press("Escape")
                
            return f"Commented on @{username}'s recent post: '{comment_text}'"
            
    except Exception as e:
        logger.error(f"[Instagram] Comment error: {e}")
        return f"Failed to comment on post: {e}"


@function_tool()
async def instagram_view_and_summarize_stories(
    context: RunContext,
    username: Annotated[str, "Instagram username (without @)"],
) -> str:
    """
    View a user's active Instagram stories and summarize their content using Vision AI.
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen
        
        username = username.strip().lstrip("@")
        logger.info(f"[Instagram] Viewing stories for {username}")
        
        async with use_global_browser(backend="auto") as browser:
            await browser.navigate(f"https://www.instagram.com/{username}/")
            await asyncio.sleep(3)
            
            screenshot = await browser.capture_screenshot()
            story_prompt = """
            Find the user's profile picture avatar. Check if it has a colorful ring around it indicating an active story.
            Return JSON with: {"has_story": true/false, "x": center X, "y": center Y}
            Return ONLY valid JSON.
            """
            story_result = analyze_screen(story_prompt, screenshot, temperature=0.1)
            
            if not story_result.get("has_story"):
                return f"@{username} has no active stories right now."
                
            await browser.click_at_coordinates(story_result["x"], story_result["y"])
            await asyncio.sleep(2)
            
            screenshot = await browser.capture_screenshot()
            summary_prompt = """
            Analyze this Instagram story. Describe what you see in detail. 
            Read any text visible on the screen. Describe the visual content, people, objects, and overall context.
            Return JSON with: {"summary": "detailed summary of the story"}
            Return ONLY valid JSON.
            """
            summary_result = analyze_screen(summary_prompt, screenshot, temperature=0.1)
            
            if browser.backend == "playwright":
                await browser.page.keyboard.press("Escape")
                
            return f"Story Summary for @{username}:\n{summary_result.get('summary', 'Could not analyze story content.')}"
            
    except Exception as e:
        logger.error(f"[Instagram] Story viewer error: {e}")
        return f"Failed to view stories: {e}"


@function_tool()
async def twitter_reply_to_recent_tweet(
    context: RunContext,
    username: Annotated[str, "Twitter username (without @)"],
    reply_text: Annotated[str, "The reply text"],
) -> str:
    """
    Reply to the most recent tweet of a Twitter/X user.
    """
    try:
        from global_browser import use_global_browser
        from computer_use import analyze_screen
        
        username = username.strip().lstrip("@")
        logger.info(f"[Twitter] Replying to {username}'s recent tweet")
        
        async with use_global_browser(backend="auto") as browser:
            await browser.navigate(f"https://twitter.com/{username}")
            await asyncio.sleep(4)
            
            screenshot = await browser.capture_screenshot()
            reply_prompt = """
            Find the 'Reply' button (speech bubble icon) on the first tweet in the user's timeline.
            Skip pinned tweets if possible, or just click the first reply button you see under a tweet.
            Return JSON with: {"found": true/false, "x": center X, "y": center Y}
            Return ONLY valid JSON.
            """
            reply_result = analyze_screen(reply_prompt, screenshot, temperature=0.1)
            
            if not reply_result.get("found"):
                return f"Could not find a tweet to reply to for @{username}"
                
            await browser.click_at_coordinates(reply_result["x"], reply_result["y"])
            await asyncio.sleep(2)
            
            if browser.backend == "playwright":
                await browser.page.keyboard.type(reply_text, delay=30)
                await asyncio.sleep(0.5)
                
                screenshot = await browser.capture_screenshot()
                post_prompt = """
                Find the 'Reply' or 'Post' button to submit the reply.
                Return JSON with: {"found": true/false, "x": center X, "y": center Y}
                Return ONLY valid JSON.
                """
                post_result = analyze_screen(post_prompt, screenshot, temperature=0.1)
                
                if post_result.get("found"):
                    await browser.click_at_coordinates(post_result["x"], post_result["y"])
                    await asyncio.sleep(2)
                    return f"Replied to @{username}'s tweet: '{reply_text}'"
                else:
                    return "Could not find the button to submit the reply."
                    
    except Exception as e:
        logger.error(f"[Twitter] Reply error: {e}")
        return f"Failed to reply to tweet: {e}"


SOCIAL_TOOLS = [
    # Instagram
    instagram_login,
    instagram_comment_on_recent_post,
    instagram_view_and_summarize_stories,
    instagram_open_profile,

    instagram_send_dm,
    instagram_search_and_dm,
    instagram_like_recent_posts,
    instagram_follow_user,
    # Twitter/X
    twitter_reply_to_recent_tweet,
    twitter_send_dm,
    twitter_post_tweet,
    # WhatsApp
    whatsapp_send_message,
    whatsapp_send_to_number,
    # LinkedIn
    linkedin_send_message,
    # Universal
    social_dm,
]
