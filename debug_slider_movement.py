import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def debug_slider_movement():
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
            return

        print("Waiting for app container...")
        await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        print("Page loaded.")

        # 슬라이더가 나타날 때까지 대기 (최대 30초)
        print("Waiting for slider...")
        try:
            # Streamlit의 select_slider는 data-testid="stSlider"를 가짐
            await page.wait_for_selector("div[data-testid='stSlider']", timeout=30000)
            print("Slider found!")
            
            for i in range(5):
                slider = page.locator("div[data-testid='stSlider']")
                box = await slider.bounding_box()
                if box:
                    offset = (i + 1) * (box['width'] / 6)
                    await page.mouse.click(box['x'] + offset, box['y'] + box['height'] / 2)
                    print(f"Clicked slider at {offset} px.")
                    # 결과 반영 대기 및 로그 확인을 위해 충분한 시간 부여
                    await asyncio.sleep(3)
                    
                    # 현재 페이지 상태 캡처
                    await page.screenshot(path=f"slider_click_{i}.png")
                else:
                    print(f"Slider box not found at attempt {i}")
                    break
        except Exception as e:
            print(f"Slider failed: {e}")
            await page.screenshot(path="slider_failed_final.png")
            content = await page.content()
            with open("page_content_final.html", "w", encoding="utf-8") as f:
                f.write(content)

        await context.tracing.stop(path="slider_movement_trace.zip")
        print("Trace saved to slider_movement_trace.zip")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_slider_movement())
