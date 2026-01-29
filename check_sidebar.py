import asyncio
from playwright.async_api import async_playwright

async def check_sidebar():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:8505")
        await page.wait_for_selector("div[data-testid='stSidebar']")
        content = await page.content()
        with open("sidebar_structure.html", "w", encoding="utf-8") as f:
            f.write(content)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_sidebar())
