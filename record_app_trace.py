import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def record_trace():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = await context.new_page()
        url = "http://localhost:8503"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("Page loaded successfully.")
            await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
            await asyncio.sleep(3)
            
            print("Finding slider...")
            try:
                await page.wait_for_selector("div[data-testid='stSlider']", timeout=10000)
                slider = page.locator("div[data-testid='stSlider']")
                box = await slider.bounding_box()
                if box:
                    print("Moving slider...")
                    for i in range(5):
                        offset = (i + 1) * (box['width'] / 6)
                        await page.mouse.click(box['x'] + offset, box['y'] + box['height'] / 2)
                        print(f"Clicked slider at offset {offset}")
                        await asyncio.sleep(2)
                else:
                    print("Slider box not found.")
            except Exception as e:
                print(f"Slider not found or error: {e}")

        except Exception as e:
            print(f"Error during trace: {e}")

        await context.tracing.stop(path="app_fix_verify_trace.zip")
        print("Trace saved to app_fix_verify_trace.zip")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(record_trace())
