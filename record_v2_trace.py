import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def record_v2_trace():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = await context.new_page()
        url = "http://localhost:8504"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("V2 Page loaded successfully.")
            await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
            await asyncio.sleep(3)
            
            # 1. 슬라이더 조작
            print("Finding V2 slider...")
            try:
                await page.wait_for_selector("div[data-testid='stSlider']", timeout=10000)
                slider = page.locator("div[data-testid='stSlider']")
                box = await slider.bounding_box()
                if box:
                    print("Moving slider...")
                    for i in range(5):
                        offset = 100 + (i * 100)
                        await page.mouse.click(box['x'] + offset, box['y'] + box['height'] / 2)
                        print(f"Clicked slider at offset {offset}")
                        await asyncio.sleep(2)
                else:
                    print("Slider box not found.")
            except Exception as e:
                print(f"Slider interaction failed: {e}")

            # 2. Go to Date 입력
            print("Testing Go to Date...")
            goto_input = page.locator("input[aria-label='Go to Date']")
            if await goto_input.count() > 0:
                await goto_input.fill("20200101")
                await goto_input.press("Enter")
                await asyncio.sleep(3)
                print("Entered 20200101 in Go to Date")

        except Exception as e:
            print(f"Error during V2 trace: {e}")

        await context.tracing.stop(path="v2_app_trace.zip")
        print("Trace saved to v2_app_trace.zip")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(record_v2_trace())
