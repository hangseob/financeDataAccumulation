import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:8505")
        await page.wait_for_selector("h1")
        
        # Get all elements with data-testid in the sidebar
        sidebar_elements = await page.evaluate("""
            () => Array.from(document.querySelectorAll("section[data-testid='stSidebar'] *[data-testid]"))
                  .map(el => ({
                      testid: el.getAttribute('data-testid'),
                      tag: el.tagName,
                      text: el.innerText
                  }))
        """)
        for el in sidebar_elements:
            print(f"TestID: {el['testid']}, Tag: {el['tag']}, Text: {el['text'][:30]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
