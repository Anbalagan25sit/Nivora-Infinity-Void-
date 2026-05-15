"""
🚀 UNIVERSAL WEB AGENT DEMONSTRATION
====================================

This demo showcases the powerful Universal Web Agent integrated into Nivora.
The agent can now handle ANY website and ANY task with advanced AI reasoning.

🎯 CAPABILITIES DEMONSTRATED:
- E-commerce automation (Amazon product search)
- Price comparison across multiple sites
- Form filling automation
- Social media automation
- Travel booking assistance
- Website monitoring
- General web task automation

🗣️ VOICE COMMANDS TO TRY:
- "Search for gaming laptops under $1500 on Amazon"
- "Compare iPhone 15 prices across Amazon, eBay, and Best Buy"
- "Fill out the contact form on that website with my information"
- "Book a table for 2 at Italian restaurants tonight on OpenTable"
- "Order my usual coffee from Starbucks delivery"
- "Apply for software engineer jobs on LinkedIn"
- "Create a new Notion page for this project"
- "Monitor Tesla stock price and alert when it drops"

🔧 TECHNICAL FEATURES:
- AWS Bedrock Nova Pro powered reasoning
- Multi-step planning and execution
- Adaptive learning from website patterns
- Robust error handling and recovery
- Memory persistence across sessions
- Self-correcting behavior
"""

import asyncio
import logging
from universal_web_agent import UniversalWebAgent, WebAgentConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_amazon_search():
    """Demo 1: Amazon product search with intelligent filtering"""
    print("\n🛒 DEMO 1: Amazon Product Search")
    print("="*60)

    config = WebAgentConfig(
        headless=False,  # Show browser for demo
        max_steps=30,
        memory_enabled=True,
        deep_analysis_mode=True
    )

    agent = UniversalWebAgent(config)

    result = await agent.execute_universal_task(
        task_description="Search for 'wireless gaming headset under $100' on Amazon and show me the top 3 results with prices and ratings",
        website_url="https://amazon.com"
    )

    print(f"✅ Result: {result}")
    return result


async def demo_price_comparison():
    """Demo 2: Price comparison across multiple websites"""
    print("\n💰 DEMO 2: Multi-Site Price Comparison")
    print("="*60)

    config = WebAgentConfig(headless=False, max_steps=50)
    agent = UniversalWebAgent(config)

    # Search on multiple sites
    websites = ["amazon.com", "ebay.com", "bestbuy.com"]
    results = []

    for site in websites:
        print(f"🔍 Searching {site}...")
        result = await agent.execute_universal_task(
            task_description="Search for 'iPhone 15 Pro' and find the best price with shipping info",
            website_url=f"https://{site}"
        )
        results.append({
            "site": site,
            "success": result.get("success"),
            "result": result.get("result")
        })

    print("\n📊 PRICE COMPARISON RESULTS:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"{status} {r['site']}: {r['result']}")

    return results


async def demo_form_automation():
    """Demo 3: Intelligent form filling"""
    print("\n📝 DEMO 3: Smart Form Filling")
    print("="*60)

    config = WebAgentConfig(headless=False, form_auto_fill=True)
    agent = UniversalWebAgent(config)

    # Demo form data
    form_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "555-0123",
        "company": "Tech Innovations Inc",
        "message": "Interested in your services"
    }

    result = await agent.execute_universal_task(
        task_description="Find the contact form on this website and fill it out with the provided information. Do not submit yet, just fill the fields.",
        website_url="https://example-contact-form.com",
        context=form_data
    )

    print(f"✅ Form filling result: {result}")
    return result


async def demo_social_automation():
    """Demo 4: Social media automation (read-only for safety)"""
    print("\n📱 DEMO 4: Social Media Analysis")
    print("="*60)

    config = WebAgentConfig(headless=False)
    agent = UniversalWebAgent(config)

    result = await agent.execute_universal_task(
        task_description="Go to Hacker News and summarize the top 3 trending technology stories with titles and brief descriptions",
        website_url="https://news.ycombinator.com"
    )

    print(f"✅ Social media analysis: {result}")
    return result


async def demo_travel_search():
    """Demo 5: Travel booking assistance"""
    print("\n✈️ DEMO 5: Travel Search Assistance")
    print("="*60)

    config = WebAgentConfig(headless=False, max_steps=40)
    agent = UniversalWebAgent(config)

    result = await agent.execute_universal_task(
        task_description="Search for flights from New York to Los Angeles for next Friday, show me the cheapest options with times and airlines",
        website_url="https://google.com/flights"
    )

    print(f"✅ Travel search result: {result}")
    return result


async def demo_learning_capabilities():
    """Demo 6: Show learning and memory capabilities"""
    print("\n🧠 DEMO 6: Learning and Memory Capabilities")
    print("="*60)

    agent = UniversalWebAgent()
    performance = await agent.get_performance_report()

    print("📊 PERFORMANCE METRICS:")
    print(f"  - Successful Tasks: {performance['performance_metrics'].get('successful_tasks', 0)}")
    print(f"  - Failed Tasks: {performance['performance_metrics'].get('failed_tasks', 0)}")
    print(f"  - Average Completion Time: {performance['performance_metrics'].get('average_completion_time', 0):.1f}s")
    print(f"  - Learned Patterns: {performance['performance_metrics'].get('learned_patterns', 0)}")

    print("\n🌐 LEARNED DOMAINS:")
    for domain in performance['memory_statistics'].get('learned_domains', []):
        print(f"  - {domain}")

    print("\n🚀 CAPABILITIES:")
    for capability, enabled in performance['capabilities'].items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {capability.replace('_', ' ').title()}")

    return performance


async def run_comprehensive_demo():
    """Run all demonstrations"""
    print("🚀 UNIVERSAL WEB AGENT - COMPREHENSIVE DEMONSTRATION")
    print("="*80)
    print("This demo showcases the powerful web automation capabilities")
    print("integrated into Nivora voice assistant.")
    print("="*80)

    demos = [
        ("Amazon Product Search", demo_amazon_search),
        ("Multi-Site Price Comparison", demo_price_comparison),
        ("Smart Form Filling", demo_form_automation),
        ("Social Media Analysis", demo_social_automation),
        ("Travel Search", demo_travel_search),
        ("Learning Capabilities", demo_learning_capabilities)
    ]

    results = {}

    for demo_name, demo_func in demos:
        try:
            print(f"\n🎯 Starting: {demo_name}")
            result = await demo_func()
            results[demo_name] = {"success": True, "result": result}
            print(f"✅ Completed: {demo_name}")
        except Exception as e:
            print(f"❌ Failed: {demo_name} - {e}")
            results[demo_name] = {"success": False, "error": str(e)}

        # Short pause between demos
        await asyncio.sleep(2)

    # Final summary
    print("\n📊 DEMONSTRATION SUMMARY")
    print("="*80)
    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)

    print(f"✅ Successful Demos: {successful}/{total}")
    print(f"🎯 Success Rate: {successful/total*100:.1f}%")

    print("\n🎉 VOICE ASSISTANT READY!")
    print("You can now use these voice commands with Nivora:")
    print("- 'Search for laptops under $1000 on Amazon'")
    print("- 'Compare iPhone prices across different sites'")
    print("- 'Fill out that contact form with my information'")
    print("- 'Book a restaurant for tonight'")
    print("- 'Apply for jobs on LinkedIn'")
    print("- 'Monitor stock prices for me'")

    return results


async def quick_test():
    """Quick test to verify everything works"""
    print("🔧 QUICK INTEGRATION TEST")
    print("="*40)

    from universal_web_tools import automate_website_task, get_web_agent_performance

    # Test performance report
    print("📊 Testing performance report...")
    performance = await get_web_agent_performance()
    print(f"✅ Performance report: {len(performance)} characters")

    # Test basic automation (safe Google search)
    print("🔍 Testing basic web automation...")
    result = await automate_website_task(
        task_description="Go to Google and search for 'Universal Web Agent demo'",
        website_url="https://google.com"
    )
    print(f"✅ Automation test: {'SUCCESS' if 'success' in result.lower() else 'PARTIAL'}")

    print("🎉 Integration test completed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test mode
        asyncio.run(quick_test())
    else:
        # Full demo mode
        asyncio.run(run_comprehensive_demo())