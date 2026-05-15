"""
Universal Web Agent Tools for Nivora Voice Assistant
===================================================

Voice commands to trigger the Universal Web Agent:
- "Search for laptops on Amazon under $1000"
- "Book a flight to Paris next month"
- "Order coffee from Starbucks"
- "Fill out this job application form"
- "Compare prices for iPhone 15 across different stores"
- "Check my email and reply to John"
- "Create a new Notion page for this project"
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from livekit.agents import function_tool

# Import our universal agent
from universal_web_agent import UniversalWebAgent, WebAgentConfig

logger = logging.getLogger(__name__)

# Global agent instance for reuse
_universal_agent: Optional[UniversalWebAgent] = None


def get_universal_agent() -> UniversalWebAgent:
    """Get or create the universal web agent instance"""
    global _universal_agent
    if _universal_agent is None:
        config = WebAgentConfig(
            headless=False,  # Run visibly so the user can see the automation
            max_steps=50,
            timeout_seconds=300,  # 5 minute timeout
            memory_enabled=True,  # Enable learning
            deep_analysis_mode=True,
            planning_depth=5,
            adaptive_waiting=True,
            error_recovery_mode=True
        )
        _universal_agent = UniversalWebAgent(config)
    return _universal_agent


@function_tool
async def automate_website_task(
    task_description: str,
    website_url: str = "",
    context: str = ""
) -> str:
    """
    Automate ANY task on ANY website using advanced AI reasoning.

    This is a powerful universal web automation tool that can:
    - Navigate and interact with any website
    - Handle complex multi-step workflows
    - Fill forms, make purchases, search, login, etc.
    - Learn from patterns and improve over time
    - Handle errors and adapt to website changes

    CRITICAL INSTRUCTION: DO NOT use this tool for Notion, Gmail, or Google Sheets.
    Use their dedicated native API tools (e.g. search_notion, send_email, google_sheets_read) instead.

    Args:
        task_description: Natural language description of what to do
                         Examples:
                         - "Search for wireless headphones under $200 on Amazon"
                         - "Book a table for 2 at Italian restaurants tonight"
                         - "Apply for software engineer jobs on LinkedIn"
                         - "Order my usual coffee from Starbucks delivery"
        website_url: Optional starting website URL (can be auto-determined)
        context: Additional context like preferences, credentials info, etc.

    Returns:
        Description of what was accomplished and any results found
    """
    try:
        logger.info(f"[WebAgent] Automating task: {task_description}")

        agent = get_universal_agent()

        # Parse context if provided
        context_dict = {}
        if context:
            # Simple parsing - in production you might want more sophisticated parsing
            for line in context.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    context_dict[key.strip()] = value.strip()

        # Execute the task
        result = await agent.execute_universal_task(
            task_description=task_description,
            website_url=website_url,
            context=context_dict
        )

        if result['success']:
            response = f"""✅ **Task Completed Successfully!**

🎯 **Task**: {task_description}
🌐 **Website**: {result.get('website_domain', 'Multiple sites')}
⏱️ **Completion Time**: {result.get('completion_time', 0):.1f} seconds
🎬 **Actions Taken**: {result.get('actions_taken', 0)} steps
🧠 **Learned Patterns**: {result.get('learned_patterns', 0)}

📋 **Result**: {result.get('result', 'Task completed')}

The web agent has successfully automated your request and learned from this interaction to improve future performance."""

        else:
            response = f"""❌ **Task Failed**

🎯 **Task**: {task_description}
🌐 **Website**: {result.get('website_domain', 'Unknown')}
⏱️ **Attempt Duration**: {result.get('completion_time', 0):.1f} seconds
🎬 **Actions Attempted**: {result.get('actions_taken', 0)} steps

❌ **Error**: {result.get('error', 'Unknown error')}

The web agent encountered an issue. This failure has been recorded to improve future attempts. You might want to try with more specific instructions or check if the website is accessible."""

        return response

    except Exception as e:
        logger.error(f"[WebAgent] Failed to execute task: {e}")
        return f"❌ **Web automation failed**: {str(e)}\n\nPlease try again with a more specific task description or check your internet connection."


@function_tool
async def search_and_compare_prices(
    product: str,
    max_price: str = "",
    websites: str = "amazon.com,ebay.com,bestbuy.com"
) -> str:
    """
    Search for a product across multiple websites and compare prices.

    Args:
        product: Product name to search for
        max_price: Maximum price limit (optional)
        websites: Comma-separated list of websites to search

    Returns:
        Price comparison results across websites
    """
    try:
        agent = get_universal_agent()
        website_list = [w.strip() for w in websites.split(',')]

        price_filter = f" under {max_price}" if max_price else ""
        task = f"Search for '{product}'{price_filter} and find the best deals with prices"

        results = []
        for website in website_list:
            if not website.startswith('http'):
                website = f"https://{website}"

            try:
                result = await agent.execute_universal_task(
                    task_description=task,
                    website_url=website
                )
                if result['success']:
                    results.append(f"✅ **{website}**: {result.get('result', 'Found results')}")
                else:
                    results.append(f"❌ **{website}**: Failed to search")
            except:
                results.append(f"⚠️ **{website}**: Website unavailable")

        response = f"""🛒 **Price Comparison Results for '{product}'**

{chr(10).join(results)}

💡 **Tip**: The agent has learned from these searches and will be faster next time!"""

        return response

    except Exception as e:
        return f"❌ **Price comparison failed**: {str(e)}"


@function_tool
async def automate_shopping_cart(
    items_to_buy: str,
    website: str = "amazon.com",
    budget_limit: str = ""
) -> str:
    """
    Automate adding items to shopping cart and managing purchases.

    Args:
        items_to_buy: Comma-separated list of items to add to cart
        website: Shopping website to use
        budget_limit: Maximum total budget for purchases

    Returns:
        Shopping cart automation results
    """
    try:
        agent = get_universal_agent()

        if not website.startswith('http'):
            website = f"https://{website}"

        budget_text = f" with a budget limit of {budget_limit}" if budget_limit else ""
        task = f"Add these items to cart: {items_to_buy}{budget_text}. Find the best deals and show total cost."

        result = await agent.execute_universal_task(
            task_description=task,
            website_url=website
        )

        if result['success']:
            return f"""🛒 **Shopping Cart Automated**

🎯 **Items**: {items_to_buy}
🌐 **Website**: {website}
⏱️ **Time**: {result.get('completion_time', 0):.1f} seconds

📋 **Result**: {result.get('result', 'Items processed')}

The shopping cart has been prepared. You can review and complete the purchase manually."""
        else:
            return f"❌ **Shopping automation failed**: {result.get('error', 'Unknown error')}"

    except Exception as e:
        return f"❌ **Shopping cart automation failed**: {str(e)}"


@function_tool
async def automate_form_filling(
    form_url: str,
    form_data: str,
    submit: str = "no"
) -> str:
    """
    Automatically fill out web forms with provided data.

    Args:
        form_url: URL of the form to fill
        form_data: Form data in format "field1:value1,field2:value2"
        submit: Whether to submit the form ("yes" or "no")

    Returns:
        Form filling results
    """
    try:
        agent = get_universal_agent()

        # Parse form data
        form_fields = {}
        for item in form_data.split(','):
            if ':' in item:
                field, value = item.split(':', 1)
                form_fields[field.strip()] = value.strip()

        submit_action = "and submit the form" if submit.lower() == "yes" else "but do not submit"
        task = f"Fill out the form at this page with the provided data {submit_action}. Form data: {form_data}"

        result = await agent.execute_universal_task(
            task_description=task,
            website_url=form_url,
            context=form_fields
        )

        if result['success']:
            return f"""📝 **Form Filling Completed**

🔗 **Form URL**: {form_url}
⏱️ **Time**: {result.get('completion_time', 0):.1f} seconds
✅ **Submitted**: {submit.lower() == 'yes'}

📋 **Result**: {result.get('result', 'Form filled successfully')}"""
        else:
            return f"❌ **Form filling failed**: {result.get('error', 'Unknown error')}"

    except Exception as e:
        return f"❌ **Form automation failed**: {str(e)}"


@function_tool
async def monitor_website_changes(
    website_url: str,
    check_for: str,
    check_interval: str = "5 minutes"
) -> str:
    """
    Monitor a website for specific changes or content.

    Args:
        website_url: URL to monitor
        check_for: What to look for (prices, new posts, availability, etc.)
        check_interval: How often to check (not implemented in demo)

    Returns:
        Current status of what's being monitored
    """
    try:
        agent = get_universal_agent()

        task = f"Check the website for: {check_for}. Report current status and any relevant information found."

        result = await agent.execute_universal_task(
            task_description=task,
            website_url=website_url
        )

        if result['success']:
            return f"""👁️ **Website Monitoring Results**

🔗 **URL**: {website_url}
🔍 **Looking for**: {check_for}
⏱️ **Check Time**: {result.get('completion_time', 0):.1f} seconds

📊 **Current Status**: {result.get('result', 'Information gathered')}

💡 **Note**: This was a one-time check. For continuous monitoring, this tool would need to be set up as a recurring task."""
        else:
            return f"❌ **Website monitoring failed**: {result.get('error', 'Website inaccessible')}"

    except Exception as e:
        return f"❌ **Website monitoring failed**: {str(e)}"


@function_tool
async def get_web_agent_performance() -> str:
    """
    Get performance statistics and capabilities of the Universal Web Agent.

    Returns:
        Detailed performance report and learned patterns
    """
    try:
        agent = get_universal_agent()
        report = await agent.get_performance_report()

        metrics = report['performance_metrics']
        memory_stats = report['memory_statistics']

        return f"""📊 **Universal Web Agent Performance Report**

🎯 **Task Statistics**:
  - ✅ Successful Tasks: {metrics.get('successful_tasks', 0)}
  - ❌ Failed Tasks: {metrics.get('failed_tasks', 0)}
  - ⏱️ Average Completion: {metrics.get('average_completion_time', 0):.1f} seconds

🧠 **Learning Statistics**:
  - 💾 Total Task Memories: {memory_stats.get('total_task_memories', 0)}
  - 🌐 Learned Domains: {len(memory_stats.get('learned_domains', []))}
  - 🎯 Successful Actions: {memory_stats.get('total_successful_actions', 0)}
  - 📈 Learned Patterns: {metrics.get('learned_patterns', 0)}

🚀 **Capabilities**:
  - ✅ Universal Website Support
  - ✅ Advanced AI Reasoning
  - ✅ Adaptive Learning
  - ✅ Error Recovery
  - ✅ Multi-step Planning
  - ✅ Form Automation
  - ✅ E-commerce Support

**Learned Domains**: {', '.join(memory_stats.get('learned_domains', ['None yet']))}

The agent continuously improves its performance by learning from each interaction."""

    except Exception as e:
        return f"❌ **Performance report failed**: {str(e)}"


# Add these tools to the appropriate agent tool lists
UNIVERSAL_WEB_TOOLS = [
    automate_website_task,
    search_and_compare_prices,
    automate_shopping_cart,
    automate_form_filling,
    monitor_website_changes,
    get_web_agent_performance
]


async def test_universal_tools():
    """Test the universal web tools"""
    print("🚀 Testing Universal Web Agent Tools...")

    # Test basic web automation
    result = await automate_website_task(
        task_description="Go to Google and search for 'python web scraping tutorials'",
        website_url="https://google.com"
    )
    print(f"✅ Basic automation result:\n{result}\n")

    # Test performance report
    performance = await get_web_agent_performance()
    print(f"📊 Performance report:\n{performance}")


if __name__ == "__main__":
    asyncio.run(test_universal_tools())