"""
E-Box Course Automation Tool - REVISED FOR PROJECT-BASED LEARNING
Automates course completion on https://pro.e-box.co.in

ACTUAL E-BOX STRUCTURE (based on screenshots):
- Course Page: Shows Topics (left sidebar) and Sections (tabs: i-Learn, i-Explore, i-Analyse, i-Design)
- Topics = Unit names (e.g., "Solution Of Ordinary Differential...", "Vector Calculus")
- Sections = Tabs (i-Learn, i-Explore, i-Analyse, i-Design)
- Each Section has a Project with problems to solve
- Projects require code solutions with command line arguments
"""

import logging
import asyncio
import re
from typing import Annotated, Dict, List, Any
from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

# Hardcoded credentials
EBOX_USERNAME = "SIT25CS170"
EBOX_PASSWORD = "SIT25CS170"
EBOX_LOGIN_URL = "https://pro.e-box.co.in/login"

# Course name mappings
COURSE_MAPPINGS = {
    "differential": "Differential Equations And Complex Analysis",
    "diff eq": "Differential Equations And Complex Analysis",
    "differential equations": "Differential Equations And Complex Analysis",
    "biology": "Biology for Engineers",
    "bio": "Biology for Engineers",
    "chemistry": "Principles of Chemistry in Engineering",
    "chem": "Principles of Chemistry in Engineering",
    "digital electronics": "Digital Electronics",
    "digital logic": "Digital Logic and Design",
    "python": "Programming Fundamentals using Python",
    "programming": "Programming Fundamentals using Python",
}

# Section/Phase names
SECTIONS = ["i-Learn", "i-Explore", "i-Analyse", "i-Design"]


def extract_course_and_topic(user_input: str) -> Dict[str, Any]:
    """
    Extract course name and topic from natural language input.
    """
    input_lower = user_input.lower().strip()

    result = {
        "course": None,
        "topic": None,
        "section": None,  # i-Learn, i-Explore, i-Analyse, i-Design
        "all": False,
    }

    # Check if requesting all courses/topics
    if any(phrase in input_lower for phrase in ["finish course", "complete course", "do course", "finish my course", "complete all"]):
        result["all"] = True

    # Extract section/phase
    section_patterns = {
        "learn": "i-Learn",
        "explore": "i-Explore",
        "analyse": "i-Analyse",
        "analyze": "i-Analyse",
        "design": "i-Design",
    }
    for key, value in section_patterns.items():
        if key in input_lower:
            result["section"] = value
            break

    # Extract course name
    for key, value in COURSE_MAPPINGS.items():
        if key in input_lower:
            result["course"] = value
            break

    # Extract specific topic (if mentioned)
    topic_keywords = [
        "solution of ordinary differential equations",
        "vector calculus",
        "analytic functions",
        "complex integration",
        "partial differential equation"
    ]
    for topic in topic_keywords:
        if topic in input_lower:
            result["topic"] = topic.title()
            break

    return result


async def login_to_ebox(browser) -> Dict[str, Any]:
    """
    Login to E-Box using hardcoded credentials.
    E-Box always requires login - this auto-fills the form every time.
    """
    try:
        logger.info("[EBox] Navigating to login page...")

        # Navigate to login page
        nav_result = await browser.navigate(EBOX_LOGIN_URL)
        if not nav_result.get("success"):
            return {"success": False, "error": f"Failed to load page: {nav_result.get('error')}"}

        await asyncio.sleep(2)

        # Check if already on dashboard (rare but possible)
        current_url = await browser.get_current_url()
        if "login" not in current_url.lower():
            logger.info("[EBox] Already logged in!")
            return {"success": True, "message": "Already logged in"}

        logger.info(f"[EBox] Filling login form with username: {EBOX_USERNAME}")

        page = browser.page

        try:
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Fill username
            username_selectors = ['input[name="username"]', 'input[type="text"]', '#username']
            for selector in username_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.fill(EBOX_USERNAME)
                        logger.info(f"[EBox] Filled username using: {selector}")
                        break
                except:
                    continue

            # Fill password
            password_selectors = ['input[name="password"]', 'input[type="password"]', '#password']
            for selector in password_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.fill(EBOX_PASSWORD)
                        logger.info(f"[EBox] Filled password using: {selector}")
                        break
                except:
                    continue

            await asyncio.sleep(0.5)

            # Click submit
            submit_selectors = ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("Login")']
            for selector in submit_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        logger.info(f"[EBox] Clicked submit using: {selector}")
                        break
                except:
                    continue

            await asyncio.sleep(3)

            current_url = await browser.get_current_url()
            if "login" not in current_url.lower():
                logger.info("[EBox] Login successful!")
                return {"success": True, "message": "Logged in successfully!"}
            else:
                return {"success": False, "error": "Login failed - still on login page"}

        except Exception as form_error:
            logger.error(f"[EBox] Form fill error: {form_error}")
            return {"success": False, "error": f"Could not fill login form: {form_error}"}

    except Exception as e:
        logger.error(f"[EBox] Login error: {e}")
        return {"success": False, "error": str(e)}


async def navigate_to_course(browser, course_name: str) -> Dict[str, Any]:
    """Navigate to a specific course from the dashboard."""
    try:
        logger.info(f"[EBox] Navigating to course: {course_name}")

        page = browser.page
        await asyncio.sleep(2)

        # Find course links
        course_links = await page.query_selector_all('a[href*="course"]')
        logger.info(f"[EBox] Found {len(course_links)} course links")

        search_terms = [course_name, course_name.split()[0]]

        for term in search_terms:
            for link in course_links:
                try:
                    text = await link.text_content()
                    if text and term.lower() in text.lower():
                        logger.info(f"[EBox] Clicking course: {text[:60]}...")
                        await link.click()
                        await asyncio.sleep(3)
                        return {"success": True, "course": course_name}
                except:
                    continue

        return {"success": False, "error": f"Course '{course_name}' not found"}

    except Exception as e:
        logger.error(f"[EBox] Course navigation error: {e}")
        return {"success": False, "error": str(e)}


async def get_topics_list(browser) -> Dict[str, Any]:
    """Get list of topics from the left sidebar."""
    try:
        page = browser.page
        await asyncio.sleep(1)

        # Topics are in the left sidebar - look for the Topics section
        topics = []

        # Try to find topic elements in sidebar
        topic_selectors = [
            '.topic-item',
            '[class*="topic"]',
            '.sidebar a',
            'a:has-text("Solution")',
            'a:has-text("Vector")',
            'a:has-text("Analytic")',
            'a:has-text("Complex")',
            'a:has-text("Partial")',
        ]

        # Get all text that looks like topic names
        body_text = await page.inner_text('body')

        # Known topic patterns for Differential Equations course
        known_topics = [
            "Solution Of Ordinary Differential",
            "Vector Calculus",
            "Analytic Functions",
            "Complex Integration",
            "Partial Differential Equation"
        ]

        for topic in known_topics:
            if topic.lower() in body_text.lower():
                topics.append(topic)

        logger.info(f"[EBox] Found topics: {topics}")
        return {"success": True, "topics": topics}

    except Exception as e:
        logger.error(f"[EBox] Error getting topics: {e}")
        return {"success": False, "error": str(e)}


async def click_topic(browser, topic_name: str) -> Dict[str, Any]:
    """Click on a topic in the left sidebar."""
    try:
        page = browser.page
        logger.info(f"[EBox] Clicking topic: {topic_name}")

        # Try to find and click the topic
        search_terms = [topic_name, topic_name.split()[0], topic_name[:20]]

        for term in search_terms:
            try:
                # Try clicking by text
                locator = page.get_by_text(re.compile(term, re.IGNORECASE)).first
                await locator.click()
                logger.info(f"[EBox] Clicked topic: {term}")
                await asyncio.sleep(2)
                return {"success": True, "topic": topic_name}
            except:
                continue

        return {"success": False, "error": f"Could not find topic: {topic_name}"}

    except Exception as e:
        logger.error(f"[EBox] Topic click error: {e}")
        return {"success": False, "error": str(e)}


async def click_section(browser, section_name: str) -> Dict[str, Any]:
    """Click on a section tab (i-Learn, i-Explore, i-Analyse, i-Design, i-Assess)."""
    try:
        page = browser.page
        logger.info(f"[EBox] Clicking section: {section_name}")

        # Based on exploration: sections are <a> tags with class "item" in a ".ui.pointing.secondary.menu"
        # Selector: a.item with text matching section name

        # Method 1: Click using the specific menu item selector
        try:
            section_link = await page.query_selector(f'a.item:has-text("{section_name}")')
            if section_link:
                await section_link.click()
                logger.info(f"[EBox] Clicked section using a.item selector: {section_name}")
                await asyncio.sleep(2)
                return {"success": True, "section": section_name}
        except Exception as e:
            logger.warning(f"[EBox] Method 1 failed: {e}")

        # Method 2: Find the menu and click the link inside it
        try:
            menu = await page.query_selector('.ui.pointing.secondary.menu')
            if menu:
                links = await menu.query_selector_all('a.item')
                for link in links:
                    text = await link.inner_text()
                    if section_name.lower() in text.lower():
                        await link.click()
                        logger.info(f"[EBox] Clicked section from menu: {section_name}")
                        await asyncio.sleep(2)
                        return {"success": True, "section": section_name}
        except Exception as e:
            logger.warning(f"[EBox] Method 2 failed: {e}")

        # Method 3: Direct text match
        try:
            await page.get_by_text(section_name, exact=True).first.click()
            logger.info(f"[EBox] Clicked section by text: {section_name}")
            await asyncio.sleep(2)
            return {"success": True, "section": section_name}
        except Exception as e:
            logger.warning(f"[EBox] Method 3 failed: {e}")

        # Method 4: Locator with text
        try:
            await page.locator(f'a:has-text("{section_name}")').first.click()
            logger.info(f"[EBox] Clicked section using locator: {section_name}")
            await asyncio.sleep(2)
            return {"success": True, "section": section_name}
        except Exception as e:
            logger.warning(f"[EBox] Method 4 failed: {e}")

        return {"success": False, "error": f"Could not find section: {section_name}"}

    except Exception as e:
        logger.error(f"[EBox] Section click error: {e}")
        return {"success": False, "error": str(e)}


async def click_project(browser) -> Dict[str, Any]:
    """Click on the project link to enter the problem page."""
    try:
        page = browser.page
        logger.info("[EBox] Looking for project to click...")

        # Wait a moment for content to load after section click
        await asyncio.sleep(1)

        # Based on exploration: Project links are <a> tags with href containing "attempt"
        # Example: <a href="/attempt/233693">Solution Of Ordinary Differential Equations / iLearn</a>

        # Method 1: Click link with href containing "attempt" (MOST RELIABLE)
        try:
            attempt_link = await page.query_selector('a[href*="attempt"]')
            if attempt_link:
                href = await attempt_link.get_attribute('href')
                text = await attempt_link.inner_text()
                logger.info(f"[EBox] Found attempt link: {text[:50]}... -> {href}")
                await attempt_link.click()
                await asyncio.sleep(3)
                return {"success": True, "href": href}
        except Exception as e:
            logger.warning(f"[EBox] Method 1 (attempt link) failed: {e}")

        # Method 2: Click link with href containing "project"
        try:
            project_link = await page.query_selector('a[href*="project"]')
            if project_link:
                await project_link.click()
                logger.info("[EBox] Clicked project link")
                await asyncio.sleep(3)
                return {"success": True}
        except Exception as e:
            logger.warning(f"[EBox] Method 2 failed: {e}")

        # Method 3: Click element containing "Completed" percentage
        try:
            # Look for the session content div and click it
            session_content = await page.query_selector('[class*="session_list_tab_content"]')
            if session_content:
                # Find the link inside
                link = await session_content.query_selector('a')
                if link:
                    await link.click()
                    logger.info("[EBox] Clicked link inside session content")
                    await asyncio.sleep(3)
                    return {"success": True}
        except Exception as e:
            logger.warning(f"[EBox] Method 3 failed: {e}")

        # Method 4: Click by text containing topic name and section
        try:
            await page.get_by_text(re.compile(r".*/(i-Learn|iLearn|i-Design|iDesign|i-Explore|i-Analyse)", re.IGNORECASE)).first.click()
            logger.info("[EBox] Clicked project by text pattern")
            await asyncio.sleep(3)
            return {"success": True}
        except Exception as e:
            logger.warning(f"[EBox] Method 4 failed: {e}")

        return {"success": False, "error": "Could not find project to click"}

    except Exception as e:
        logger.error(f"[EBox] Project click error: {e}")
        return {"success": False, "error": str(e)}
        logger.error(f"[EBox] Project click error: {e}")
        return {"success": False, "error": str(e)}


async def analyze_problem_page(browser) -> Dict[str, Any]:
    """Analyze the current problem page and extract problem details from DOM."""
    try:
        page = browser.page
        logger.info("[EBox] Analyzing problem page...")

        await asyncio.sleep(2)

        # Get page content - this is more reliable than vision
        body_text = await page.inner_text('body')

        # Extract problem details from the text
        problem_data = {
            "problem_title": "",
            "description": "",
            "context": "",
            "task": "",
            "input_format": "",
            "output_format": "",
            "sample_input": "",
            "sample_output": "",
            "programming_language": "Python"  # Default to Python
        }

        # Parse the body text to extract sections
        lines = body_text.split('\n')
        current_section = ""
        section_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            if line in ["Context", "Problem Description", "Input Format", "Output Format",
                       "Sample Input", "Sample Output", "Model Definition", "Your task is to:",
                       "Learning Outcomes", "Sample Output Explanation"]:
                # Save previous section
                if current_section and section_content:
                    content = ' '.join(section_content)
                    if "context" in current_section.lower():
                        problem_data["context"] = content
                    elif "problem description" in current_section.lower():
                        problem_data["description"] = content
                    elif "input format" in current_section.lower():
                        problem_data["input_format"] = content
                    elif "output format" in current_section.lower():
                        problem_data["output_format"] = content
                    elif "sample input" in current_section.lower():
                        problem_data["sample_input"] = content
                    elif "sample output" in current_section.lower() and "explanation" not in current_section.lower():
                        problem_data["sample_output"] = content

                current_section = line
                section_content = []
            else:
                section_content.append(line)

        # Try to find the problem title (usually at the top)
        for line in lines[:20]:
            line = line.strip()
            if len(line) > 20 and len(line) < 150 and line[0].isupper():
                # Skip common non-title lines
                if line not in ["Context", "Problem Description", "Review", "Submit", "Next"]:
                    if not any(x in line.lower() for x in ["are widely", "one common", "you are given", "your task"]):
                        problem_data["problem_title"] = line
                        break

        # Build task description from what we found
        task_parts = []
        if problem_data["description"]:
            task_parts.append(problem_data["description"])
        if problem_data["context"]:
            task_parts.append(f"Context: {problem_data['context']}")

        problem_data["task"] = ' '.join(task_parts) if task_parts else body_text[:500]

        # Detect programming language from content
        if "python" in body_text.lower() or "matplotlib" in body_text.lower() or "numpy" in body_text.lower():
            problem_data["programming_language"] = "Python"
        elif "java" in body_text.lower():
            problem_data["programming_language"] = "Java"
        elif "#include" in body_text or "printf" in body_text:
            problem_data["programming_language"] = "C"

        logger.info(f"[EBox] Extracted problem: {problem_data['problem_title'][:50]}...")
        logger.info(f"[EBox] Language: {problem_data['programming_language']}")

        return {"success": True, "problem": problem_data}

    except Exception as e:
        logger.error(f"[EBox] Problem analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def generate_solution_code(problem_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate solution code using AI."""
    try:
        import boto3
        import json

        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

        prompt = f"""
You are solving an E-Box programming problem that requires command line arguments.

PROBLEM: {problem_data.get('problem_title', 'Unknown')}

DESCRIPTION: {problem_data.get('description', '')}

TASK: {problem_data.get('task', '')}

INPUT FORMAT: {problem_data.get('input_format', 'Command line arguments')}

OUTPUT FORMAT: {problem_data.get('output_format', 'Print to stdout')}

SAMPLE INPUT: {problem_data.get('sample_input', '')}

SAMPLE OUTPUT: {problem_data.get('sample_output', '')}

LANGUAGE: {problem_data.get('programming_language', 'Python')}

CRITICAL E-BOX REQUIREMENTS:
1. The code MUST accept command line arguments using sys.argv (for Python) or equivalent
2. Parse the input format to determine what arguments are expected
3. E-Box provides a "Command line argument" textbox where test arguments are entered
4. E-Box will execute your code with these arguments: python script.py arg1 arg2 arg3
5. Generate realistic test arguments based on the sample input (these will be entered in the textbox)
6. Include import statements for required libraries (matplotlib, numpy, scipy, etc.)
7. Handle plotting/visualization if required by the problem

Generate complete, working code that E-Box can execute with command line arguments.

Return JSON:
{{
    "code": "complete working code with proper command line argument handling",
    "command_args": "space-separated arguments to test with (e.g. '100 0.4 10')",
    "explanation": "brief explanation of the solution approach"
}}

Return ONLY valid JSON.
"""

        response = bedrock.invoke_model(
            modelId='amazon.nova-pro-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "temperature": 0.3,
                    "max_new_tokens": 2000
                }
            })
        )

        response_body = json.loads(response['body'].read())
        result_text = response_body['output']['message']['content'][0]['text']

        # Strip markdown
        result_text = re.sub(r'^```json?\s*', '', result_text.strip())
        result_text = re.sub(r'\s*```$', '', result_text.strip())

        result = json.loads(result_text)

        return {
            "success": True,
            "code": result.get("code", ""),
            "command_args": result.get("command_args", ""),
            "explanation": result.get("explanation", "")
        }

    except Exception as e:
        logger.error(f"[EBox] Code generation error: {e}")
        return {"success": False, "error": str(e)}


async def submit_code(browser, code: str, command_args: str = "") -> Dict[str, Any]:
    """Submit code to E-Box code editor (ACE/Monaco editor)."""
    try:
        page = browser.page
        logger.info("[EBox] Submitting code...")

        # E-Box uses ACE editor - we need to click on the editor area first
        # The editor is inside a container with class containing "editor_project" or "editor_container"

        editor_clicked = False
        editor_selectors = [
            '[class*="editor_project"]',
            '[class*="editor_container"]',
            '.ace_editor',
            '.monaco-editor',
            '.CodeMirror',
        ]

        for selector in editor_selectors:
            try:
                editor = await page.query_selector(selector)
                if editor:
                    await editor.click()
                    await asyncio.sleep(0.3)
                    logger.info(f"[EBox] Clicked on editor: {selector}")
                    editor_clicked = True
                    break
            except:
                continue

        if not editor_clicked:
            logger.warning("[EBox] Could not click on editor container, trying direct keyboard input")

        # Now type the code using keyboard (this works with ACE/Monaco editors)
        # First select all existing code and delete it
        await page.keyboard.press("Control+a")
        await asyncio.sleep(0.1)
        await page.keyboard.press("Delete")
        await asyncio.sleep(0.1)

        # Type the code line by line (more reliable than pasting all at once)
        code_lines = code.split('\n')
        for i, line in enumerate(code_lines):
            await page.keyboard.type(line, delay=5)  # Small delay for each character
            if i < len(code_lines) - 1:
                await page.keyboard.press("Enter")
            # Log progress for long code
            if i % 10 == 0 and i > 0:
                logger.info(f"[EBox] Typed {i}/{len(code_lines)} lines...")

        logger.info(f"[EBox] Code entered ({len(code_lines)} lines)")
        await asyncio.sleep(0.5)

        # Fill command line arguments field if provided
        # Based on Playwright exploration: There IS a textbox labeled "Command line argument"
        # Located below the code editor - it loads dynamically after a delay
        if command_args:
            logger.info(f"[EBox] Filling command line arguments: {command_args}")
            try:
                # Wait for the Submit button to appear (indicates page is fully loaded)
                try:
                    await page.wait_for_selector('button:has-text("Submit")', timeout=5000)
                    logger.info("[EBox] Submit button found - page fully loaded")
                except:
                    logger.warning("[EBox] Submit button not found, continuing anyway")

                # Additional wait for dynamic content
                await asyncio.sleep(3)

                # Method 1: Use getByRole to find textbox (most reliable based on Playwright plugin test)
                try:
                    # In the Playwright plugin test, I used .first() which worked!
                    # Try the FIRST textbox instead of the last
                    textboxes = page.get_by_role('textbox')
                    count = await textboxes.count()
                    if count > 0:
                        # Try first textbox (the working one based on Playwright plugin test)
                        try:
                            await textboxes.first.fill(command_args)
                            logger.info(f"[EBox] ✅ Filled command args using first textbox: {command_args}")
                            return {"success": True}
                        except Exception as e1:
                            logger.warning(f"[EBox] First textbox failed: {e1}, trying last...")
                            # Fallback: try last textbox
                            try:
                                await textboxes.nth(count - 1).fill(command_args)
                                logger.info(f"[EBox] ✅ Filled command args using last textbox: {command_args}")
                                return {"success": True}
                            except Exception as e2:
                                logger.warning(f"[EBox] Last textbox also failed: {e2}")
                except Exception as e:
                    logger.warning(f"[EBox] getByRole method failed: {e}")

                # Method 2: Search through all inputs with broader selectors
                input_selectors = [
                    'input[type="text"]',
                    'input:not([type="password"]):not([type="hidden"])',
                    'input',
                    'textarea'
                ]

                for selector in input_selectors:
                    all_inputs = await page.query_selector_all(selector)
                    for inp in all_inputs:
                        try:
                            # Check parent, siblings, and grandparent for "command" + "argument"
                            parent_text = await inp.evaluate('el => el.parentElement ? el.parentElement.textContent : ""')
                            prev_sibling = await inp.evaluate('el => el.previousElementSibling ? el.previousElementSibling.textContent : ""')
                            grandparent = await inp.evaluate('el => el.parentElement && el.parentElement.parentElement ? el.parentElement.parentElement.textContent : ""')

                            combined = f"{parent_text} {prev_sibling} {grandparent}".lower()

                            if 'command' in combined and 'argument' in combined:
                                await inp.fill(command_args)
                                logger.info(f"[EBox] ✅ Filled command args: {command_args}")
                                return {"success": True}
                        except:
                            continue

                logger.warning("[EBox] Could not find command line argument input field")
            except Exception as e:
                logger.warning(f"[EBox] Error filling command args: {e}")

        await asyncio.sleep(1)

        # Click submit button
        logger.info("[EBox] Looking for submit button...")
        submit_clicked = False
        submit_selectors = [
            'button:has-text("Submit")',
            'button:has-text("Run")',
            'button:has-text("Execute")',
            'button:has-text("Check")',
        ]

        for selector in submit_selectors:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    await btn.click()
                    logger.info(f"[EBox] Clicked submit button: {selector}")
                    submit_clicked = True
                    break
            except:
                continue

        if not submit_clicked:
            # Try clicking by text directly
            try:
                await page.get_by_text("Submit", exact=True).click()
                logger.info("[EBox] Clicked Submit by text")
                submit_clicked = True
            except:
                pass

        if not submit_clicked:
            return {"success": False, "error": "Could not find submit button"}

        await asyncio.sleep(3)  # Wait for submission processing
        return {"success": True, "message": "Code submitted"}

    except Exception as e:
        logger.error(f"[EBox] Submit error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def solve_mcq_question(browser) -> Dict[str, Any]:
    """
    Solve a single MCQ question using vision AI.
    Returns the selected answer and whether it was correct.
    """
    try:
        page = browser.page

        # Take screenshot of the question
        screenshot_bytes = await page.screenshot()
        import base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        # Use vision AI to analyze the question and select answer
        import boto3
        import json

        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

        prompt = """
Analyze this E-Box MCQ question and select the CORRECT answer.

Look at the question text and all the radio button options.
Return ONLY the option number (1, 2, 3, or 4) that is the correct answer, AND the exact text of that answer.

Return JSON:
{
    "answer_number": 2,
    "answer_text": "exponential growth",
    "reasoning": "brief explanation why this is correct"
}
"""

        response = bedrock.invoke_model(
            modelId='amazon.nova-pro-v1:0',
            body=json.dumps({
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "image": {
                                "format": "png",
                                "source": {"bytes": screenshot_b64}
                            }
                        },
                        {"text": prompt}
                    ]
                }],
                "inferenceConfig": {
                    "temperature": 0.1,
                    "max_new_tokens": 500
                }
            })
        )

        response_body = json.loads(response['body'].read())
        result_text = response_body['output']['message']['content'][0]['text']

        # Strip markdown
        import re
        result_text = re.sub(r'^```json?\s*', '', result_text.strip())
        result_text = re.sub(r'\s*```$', '', result_text.strip())

        result = json.loads(result_text)
        answer_num = result.get("answer_number", 1)
        answer_text = result.get("answer_text", "")

        logger.info(f"[EBox MCQ] AI selected answer {answer_num} ('{answer_text}'): {result.get('reasoning', '')}")

        # Click the radio button for the selected answer
        # Try multiple methods to click the correct radio button
        clicked = False

        # Method 0: Click by exact text (Highly reliable for custom UI where radios are hidden)
        if answer_text:
            try:
                # EBox seems to wrap the text in a div or span next to the radio button.
                # We can find elements containing the text and click them.
                # Try clicking via evaluate to bypass "element not visible" errors if it's covered by a pseudo-element
                clicked_by_js = await page.evaluate(f'''(textToFind) => {{
                    const elements = Array.from(document.querySelectorAll('div, span, label, p, td, li'));
                    // Find the deepest element containing the text (to avoid clicking the whole page wrapper)
                    const target = elements.reverse().find(el =>
                        el.textContent &&
                        el.textContent.trim().toLowerCase() === textToFind.trim().toLowerCase() &&
                        el.children.length === 0 // ensure it's a leaf node
                    );

                    if (target) {{
                        target.click();
                        return true;
                    }}

                    // Fallback to partial match if exact match fails
                    const partialTarget = elements.reverse().find(el =>
                        el.textContent &&
                        el.textContent.toLowerCase().includes(textToFind.trim().toLowerCase()) &&
                        el.children.length === 0
                    );

                    if(partialTarget) {{
                        partialTarget.click();
                        return true;
                    }}

                    return false;
                }}''', answer_text)

                if clicked_by_js:
                    clicked = True
                    logger.info(f"[EBox MCQ] Clicked answer using JS text search: {answer_text}")
                else:
                    # Fallback to Playwright's locator if JS fails
                    locators = page.get_by_text(answer_text)
                    count = await locators.count()
                    if count > 0:
                        await locators.first.click(force=True)
                        clicked = True
                        logger.info(f"[EBox MCQ] Clicked answer using Playwright text locator: {answer_text}")
            except Exception as e:
                logger.warning(f"[EBox MCQ] Method 0 (text match) failed: {e}")

        # Method 1: Force click the hidden radio input directly (useful if styled with opacity 0)
        if not clicked:
            try:
                radios = await page.query_selector_all('input[type="radio"]')
                if 0 < answer_num <= len(radios):
                    await radios[answer_num - 1].click(force=True)
                    clicked = True
                    logger.info(f"[EBox MCQ] Clicked answer {answer_num} using forced click on radio")
            except Exception as e:
                logger.warning(f"[EBox MCQ] Method 1 (force click radio) failed: {e}")

        # Method 2: Click the parent container of the radio button
        if not clicked:
            try:
                # Find the Nth radio button and click its parent element (which is usually the visible label/row)
                radios = await page.query_selector_all('input[type="radio"]')
                if 0 < answer_num <= len(radios):
                    # Use javascript to click the parent node since it's the visible part
                    await page.evaluate('(element) => element.parentElement.click()', radios[answer_num - 1])
                    clicked = True
                    logger.info(f"[EBox MCQ] Clicked answer {answer_num} using parentElement JS click")
            except Exception as e:
                logger.warning(f"[EBox MCQ] Method 2 (parent JS click) failed: {e}")

        # Method 3: Use pure JS to set the radio to checked
        if not clicked:
            try:
                radios = await page.query_selector_all('input[type="radio"]')
                if 0 < answer_num <= len(radios):
                    await page.evaluate('(element) => { element.checked = true; const event = new Event("change", { bubbles: true }); element.dispatchEvent(event); }', radios[answer_num - 1])
                    clicked = True
                    logger.info(f"[EBox MCQ] Selected answer {answer_num} using JS property set")
            except Exception as e:
                logger.warning(f"[EBox MCQ] Method 3 (JS property set) failed: {e}")

        return {
            "success": clicked,
            "answer": answer_num,
            "reasoning": result.get("reasoning", "")
        }

    except Exception as e:
        logger.error(f"[EBox MCQ] Error solving question: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def complete_mcq_section(browser, topic_name: str, section_name: str) -> Dict[str, Any]:
    """
    Complete ALL MCQ questions in i-Learn or similar quiz-based sections.
    Clicks through questions, selects answers, clicks Review Answer, then Next.
    """
    results = []
    questions_completed = 0
    max_questions = 50  # Safety limit

    try:
        page = browser.page
        logger.info(f"[EBox MCQ] Starting MCQ section: {topic_name}/{section_name}")

        # Click on section tab
        section_result = await click_section(browser, section_name)
        if not section_result.get("success"):
            return {"success": False, "error": f"Could not click section {section_name}"}

        await asyncio.sleep(2)

        # Click the first question/project link
        attempt_links = await page.query_selector_all('a[href*="attempt"]')
        if attempt_links and len(attempt_links) > 0:
            await attempt_links[0].click()
            await asyncio.sleep(3)
        else:
            return {"success": False, "error": "No MCQ questions found"}

        # Loop through all questions
        for question_num in range(1, max_questions + 1):
            logger.info(f"[EBox MCQ] Question #{question_num}")

            # Solve the MCQ question
            solve_result = await solve_mcq_question(browser)

            if not solve_result.get("success"):
                results.append(f"❌ Q{question_num}: Could not solve")
                break

            # Click "Review Answer" button
            await asyncio.sleep(1)
            review_clicked = False
            review_selectors = [
                'button:has-text("Review Answer")',
                'button:has-text("Review")',
                'input[value="Review Answer"]',
            ]

            for selector in review_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click(force=True)
                        logger.info("[EBox MCQ] Clicked Review Answer")
                        review_clicked = True
                        break
                except:
                    continue

            # Fallback for Review Answer
            if not review_clicked:
                try:
                    await page.evaluate('''() => {
                        const buttons = Array.from(document.querySelectorAll('button, input[type="button"], a.btn'));
                        const reviewBtn = buttons.find(b => b.textContent.includes('Review Answer') || b.value === 'Review Answer');
                        if(reviewBtn) reviewBtn.click();
                    }''')
                    logger.info("[EBox MCQ] Clicked Review Answer via JS eval")
                except:
                    pass

            await asyncio.sleep(2)

            # Click "Next" or "Save & Close" button
            next_clicked = False
            next_selectors = [
                'button:has-text("Next")',
                'input[value="Next"]',
                'a:has-text("Next")',
                'button:has-text("Save And Close")',
                'button:has-text("Save & Close")',
                'button:has-text("Finish")',
                'a:has-text("Save")',
            ]

            for selector in next_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        btn_text = await btn.text_content()
                        await btn.click(force=True)
                        logger.info(f"[EBox MCQ] Clicked '{btn_text.strip()}' button")
                        next_clicked = True
                        questions_completed += 1
                        results.append(f"✅ Q{question_num}: Answer {solve_result.get('answer')} (Selected text: '{solve_result.get('answer_text', '')}')")

                        # If the button was Save & Close, we are done with the MCQ section
                        if "save" in btn_text.lower() or "close" in btn_text.lower():
                            logger.info("[EBox MCQ] End of quiz detected ('Save & Close' clicked). Exiting section loop.")
                            return {
                                "success": True,
                                "problems_completed": questions_completed,
                                "results": results
                            }
                        break
                except:
                    continue

            # Fallback for Next button
            if not next_clicked:
                try:
                    await page.evaluate('''() => {
                        const buttons = Array.from(document.querySelectorAll('button, input[type="button"], a.btn, a'));
                        const nextBtn = buttons.find(b =>
                            b.textContent.includes('Next') || b.value === 'Next' ||
                            b.textContent.includes('Save') || b.value === 'Save'
                        );
                        if(nextBtn) nextBtn.click();
                    }''')
                    logger.info("[EBox MCQ] Clicked Next/Save via JS eval")
                    next_clicked = True
                    questions_completed += 1
                    results.append(f"✅ Q{question_num}: Answer {solve_result.get('answer')}")
                except:
                    pass

            if not next_clicked:
                # Might be the last question - check if we're done
                logger.info("[EBox MCQ] No Next or Save button found - section might be finished")
                break

            await asyncio.sleep(2)

        logger.info(f"[EBox MCQ] Section complete: {questions_completed} questions answered")

        return {
            "success": True,
            "problems_completed": questions_completed,
            "results": results
        }

    except Exception as e:
        logger.error(f"[EBox MCQ] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "problems_completed": questions_completed,
            "results": results
        }


async def complete_section(browser, topic_name: str, section_name: str) -> Dict[str, Any]:
    """
    Complete ALL problems/projects within a specific section.
    Returns results for all problems attempted.
    """
    results = []
    problems_completed = 0
    max_problems = 20  # Safety limit to prevent infinite loops

    try:
        page = browser.page
        logger.info(f"[EBox] Starting section: {topic_name}/{section_name}")

        # Click on section tab
        section_result = await click_section(browser, section_name)
        if not section_result.get("success"):
            return {"success": False, "error": f"Could not click section {section_name}"}

        await asyncio.sleep(2)

        # Loop through all problems in this section
        for problem_num in range(1, max_problems + 1):
            logger.info(f"[EBox] Problem #{problem_num} in {section_name}")

            # Get all project/attempt links on the current page
            attempt_links = await page.query_selector_all('a[href*="attempt"]')

            if not attempt_links or len(attempt_links) == 0:
                logger.info(f"[EBox] No more problems found in {section_name}")
                break

            # Click the first unfinished problem
            first_link = attempt_links[0]
            link_text = await first_link.inner_text()
            href = await first_link.get_attribute('href')

            logger.info(f"[EBox] Clicking problem: {link_text[:50]}... ({href})")
            await first_link.click()
            await asyncio.sleep(3)

            # Analyze the problem
            problem_result = await analyze_problem_page(browser)
            if not problem_result.get("success"):
                results.append(f"❌ Problem {problem_num}: Could not analyze")
                # Go back and try next problem
                await page.go_back()
                await asyncio.sleep(2)
                continue

            problem = problem_result["problem"]

            # Generate solution
            solution_result = await generate_solution_code(problem)
            if not solution_result.get("success"):
                results.append(f"❌ Problem {problem_num}: Could not generate solution")
                await page.go_back()
                await asyncio.sleep(2)
                continue

            # Submit code
            submit_result = await submit_code(
                browser,
                solution_result["code"],
                solution_result.get("command_args", "")
            )

            if submit_result.get("success"):
                results.append(f"✅ Problem {problem_num}: {problem.get('problem_title', 'Unknown')[:40]}...")
                problems_completed += 1
            else:
                results.append(f"⚠️ Problem {problem_num}: Submit failed")

            # Wait for submission to process
            await asyncio.sleep(3)

            # Go back to section page to get next problem
            await page.go_back()
            await asyncio.sleep(2)

            # Check if we're still on the section page
            current_url = await browser.get_current_url()
            if 'attempt' in current_url:
                # Still on a problem page, go back again
                await page.go_back()
                await asyncio.sleep(2)

        logger.info(f"[EBox] Section {section_name} complete: {problems_completed} problems solved")

        return {
            "success": True,
            "problems_completed": problems_completed,
            "results": results
        }

    except Exception as e:
        logger.error(f"[EBox] Error completing section: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "problems_completed": problems_completed,
            "results": results
        }


@function_tool()
async def complete_ebox_course(
    context: RunContext,
    request: Annotated[str, "Natural language request like 'finish differential equations', 'complete biology course', 'do i-Design section'"]
) -> str:
    """
    Automatically complete E-Box course projects/problems.

    E-Box Structure:
    - Course → Topics (left sidebar) → Sections (i-Learn, i-Explore, i-Analyse, i-Design) → Projects → Problems

    Supports:
    - "finish differential equations" - complete all topics and sections
    - "do i-Design section" - complete ALL problems in i-Design across all topics
    - "solve vector calculus" - complete all sections in vector calculus topic
    - "finish i-Learn" - complete i-Learn section in all topics
    """
    browser = None
    try:
        from browser_automation import BrowserAutomationEngine

        parsed = extract_course_and_topic(request)
        logger.info(f"[EBox] Parsed request: {parsed}")

        # Start browser
        browser = BrowserAutomationEngine(backend="playwright", headless=False)
        await browser.start()
        logger.info("[EBox] Browser started")

        # Login
        login_result = await login_to_ebox(browser)
        if not login_result.get("success"):
            return f"Login failed: {login_result.get('error')}. Browser left open for manual login."

        # Navigate to course
        if parsed["course"]:
            course_result = await navigate_to_course(browser, parsed["course"])
            if not course_result.get("success"):
                return f"Could not find course: {parsed['course']}. Browser left open."

        await asyncio.sleep(2)

        # Get list of topics
        topics_result = await get_topics_list(browser)
        topics = topics_result.get("topics", [])

        if not topics:
            return "No topics found on the course page. Please navigate manually. Browser left open."

        all_results = []
        total_problems = 0

        # Process each topic
        for topic in topics:
            logger.info(f"[EBox] ========== TOPIC: {topic} ==========")

            # Click on the topic
            topic_result = await click_topic(browser, topic)
            if not topic_result.get("success"):
                all_results.append(f"❌ {topic}: Could not select topic")
                continue

            # Process each section
            sections_to_do = [parsed["section"]] if parsed["section"] else SECTIONS

            for section in sections_to_do:
                logger.info(f"[EBox] ----- SECTION: {section} -----")

                # Route based on section type
                # i-Learn usually contains MCQs/Quizzes
                if section.lower() in ["i-learn", "ilearn", "i-explore", "iexplore"]:
                    logger.info(f"[EBox] Detected MCQ/Quiz section: {section}")
                    section_result = await complete_mcq_section(browser, topic, section)
                else:
                    logger.info(f"[EBox] Detected Coding/Project section: {section}")
                    section_result = await complete_section(browser, topic, section)

                if section_result.get("success"):
                    problems_count = section_result.get("problems_completed", 0)
                    total_problems += problems_count
                    all_results.append(f"✅ {topic}/{section}: {problems_count} problems completed")

                    # Add individual problem results
                    for result in section_result.get("results", []):
                        all_results.append(f"  {result}")
                else:
                    all_results.append(f"❌ {topic}/{section}: {section_result.get('error', 'Unknown error')}")

        # Build response
        response = f"**E-Box Course Automation Complete!**\n\n"
        response += f"**Total Problems Solved: {total_problems}**\n\n"
        response += f"**Results:**\n"
        for r in all_results:
            response += f"{r}\n"

        response += f"\n**Browser left open for verification.**"

        return response

    except Exception as e:
        logger.error(f"[EBox] Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Automation error: {str(e)}. Browser left open for manual recovery."


@function_tool()
async def ebox_help_with_problem(
    context: RunContext,
    problem_description: Annotated[str, "Describe the problem or paste the problem statement"]
) -> str:
    """
    Get AI help with understanding and solving an E-Box problem.
    Returns solution approach, code, and explanation.
    """
    try:
        import boto3
        import json

        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

        prompt = f"""
You are an expert programmer helping with an E-Box course problem.

PROBLEM:
{problem_description}

Provide:
1. Understanding of what the problem is asking
2. Solution approach (step-by-step)
3. Complete code solution (if applicable)
4. Explanation of key concepts

Return JSON:
{{
    "understanding": "what the problem is asking for",
    "approach": ["step 1", "step 2", ...],
    "code": "complete code solution (if applicable)",
    "key_concepts": ["concept 1", "concept 2", ...],
    "tips": "helpful tips for solving similar problems"
}}

Return ONLY valid JSON.
"""

        response = bedrock.invoke_model(
            modelId='amazon.nova-pro-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                "inferenceConfig": {
                    "temperature": 0.4,
                    "max_new_tokens": 2000
                }
            })
        )

        response_body = json.loads(response['body'].read())
        result_text = response_body['output']['message']['content'][0]['text']

        # Strip markdown
        result_text = re.sub(r'^```json?\s*', '', result_text.strip())
        result_text = re.sub(r'\s*```$', '', result_text.strip())

        result = json.loads(result_text)

        # Format response
        output = f"**Understanding:** {result.get('understanding', '')}\n\n"
        output += f"**Solution Approach:**\n"
        for i, step in enumerate(result.get('approach', []), 1):
            output += f"{i}. {step}\n"

        if result.get('code'):
            output += f"\n**Code Solution:**\n```\n{result['code']}\n```\n"

        output += f"\n**Key Concepts:** {', '.join(result.get('key_concepts', []))}\n"
        output += f"\n**Tips:** {result.get('tips', '')}"

        return output

    except Exception as e:
        logger.error(f"[EBox] Help error: {e}")
        return f"Could not generate help: {str(e)}"
