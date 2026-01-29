import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def debug_slider_alternating():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        
        page = await context.new_page()
        url = "http://localhost:8501"
        print(f"Connecting to {url}...")
        
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        print("Page loaded.")

        try:
            await page.wait_for_selector("div[data-testid='stSlider']", timeout=10000)
            
            for i in range(10):
                slider = page.locator("div[data-testid='stSlider']")
                # 현재 슬라이더에 표시된 날짜 (thumb value) 확인
                thumb = page.locator("div[data-testid='stThumbValue']")
                current_text = await thumb.inner_text()
                print(f"Attempt {i}: Current Thumb Text = {current_text}")
                
                box = await slider.bounding_box()
                if box:
                    # 매번 조금씩 오른쪽으로 클릭
                    offset = 100 + (i * 50)
                    if offset > box['width'] - 10: offset = 100
                    
                    await page.mouse.click(box['x'] + offset, box['y'] + box['height'] / 2)
                    print(f"Clicked at offset {offset}")
                    
                    # Rerun 및 Sync 대기
                    await asyncio.sleep(2)
                    
                    new_text = await thumb.inner_text()
                    print(f"Attempt {i}: New Thumb Text = {new_text}")
                    
                    if new_text == current_text and i > 0:
                        print("⚠️ Thumb text did not change after click!")
                else:
                    print("Slider box not found.")
                    break
        except Exception as e:
            print(f"Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_slider_alternating())
