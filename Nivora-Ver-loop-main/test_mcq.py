import asyncio
from browser_automation import BrowserAutomationEngine

async def main():
    browser = BrowserAutomationEngine(backend="playwright", headless=False)
    await browser.start()

    print("Browser started. Please log into E-Box manually and navigate to an MCQ question.")
    print("Waiting 60 seconds for you to navigate...")
    await asyncio.sleep(60)

    print("Testing MCQ logic on current page...")
    from ebox_automation import solve_mcq_question

    result = await solve_mcq_question(browser)
    print("Result:", result)

    print("Waiting 10 seconds before closing...")
    await asyncio.sleep(10)
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())