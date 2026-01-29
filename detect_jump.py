import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def detect_slider_jumping():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        url = "http://localhost:8505"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("Page loaded.")
            await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
            
            # 슬라이더 요소 찾기
            await page.wait_for_selector("div[data-testid='stSlider']", timeout=10000)
            slider = page.locator("div[data-testid='stSlider']")
            thumb = page.locator("div[data-testid='stThumbValue']")
            
            box = await slider.bounding_box()
            if not box:
                print("Could not get slider bounding box.")
                return

            history = []
            print("\n--- Starting Slider Jumping Test (10 clicks) ---")
            
            for i in range(10):
                # 이전 값 확인
                prev_val = await thumb.inner_text()
                
                # 5개 지점 순환 클릭 (20%, 40%, 60%, 80%, 100%)
                target_offset = box['width'] * ((i % 5 + 1) / 5.5)
                await page.mouse.click(box['x'] + target_offset, box['y'] + box['height'] / 2)
                
                # 리렌더링 대기
                await asyncio.sleep(2)
                
                # 새로운 값 확인
                new_val = await thumb.inner_text()
                print(f"Click {i+1}: Offset={target_offset:.1f}, Prev={prev_val}, New={new_val}")
                
                # 점핑 체크
                if i > 0 and new_val == history[-1]['prev']:
                    print(f"  [BUG DETECTED] Value jumped back to previous position!")
                elif new_val == prev_val:
                    print(f"  [WARNING] Value did not change even after click.")
                
                history.append({'prev': prev_val, 'new': new_val})

            print("\n--- Test Finished ---")
            
        except Exception as e:
            print(f"Error during detection: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(detect_slider_jumping())
