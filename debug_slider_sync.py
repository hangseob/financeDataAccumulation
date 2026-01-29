import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def debug_slider_sync():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = await context.new_page()
        url = "http://localhost:8501"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await context.tracing.stop(path="trace_failed_load.zip")
            await browser.close()
            return

        await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        print("Page loaded.")

        # 1. 사이드바에서 날짜 변경
        print("Looking for Start Date input...")
        date_inputs = page.locator("div[data-testid='stDateInput'] input")
        if await date_inputs.count() >= 1:
            start_date_input = date_inputs.nth(0)
            print("Found Start Date input.")
            await start_date_input.click()
            # 2024.01.01로 변경
            await start_date_input.fill("2024.01.01")
            await start_date_input.press("Enter")
            print("Changed Start Date to 2024.01.01")
            await asyncio.sleep(5) 
        else:
            print("Start Date input not found.")

        # 2. 슬라이더 클릭 5번
        print("Interacting with slider...")
        try:
            for i in range(5):
                await page.wait_for_selector("div[data-testid='stSelectSlider']", timeout=10000)
                slider = page.locator("div[data-testid='stSelectSlider']")
                box = await slider.bounding_box()
                if box:
                    offset = (i + 1) * (box['width'] / 6)
                    await page.mouse.click(box['x'] + offset, box['y'] + box['height'] / 2)
                    print(f"Clicked slider at {offset} px.")
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"Slider interaction failed: {e}")

        await context.tracing.stop(path="slider_debug_trace.zip")
        print("Trace saved to slider_debug_trace.zip")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_slider_sync())
