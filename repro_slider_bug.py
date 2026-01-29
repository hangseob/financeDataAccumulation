import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def reproduce_slider_bug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        
        page = await context.new_page()
        url = "http://localhost:8501"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("Page loaded.")
            await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
            
            # 슬라이더 대기
            await page.wait_for_selector("div[data-testid='stSlider']", timeout=10000)
            slider = page.locator("div[data-testid='stSlider']")
            thumb = page.locator("div[data-testid='stThumbValue']")
            
            history = []
            
            print("\n--- Starting Slider Click Test ---")
            for i in range(10):
                box = await slider.bounding_box()
                if not box: break
                
                # 매번 다른 위치 클릭 (10%, 20%, 30% ... 지점)
                click_x = box['x'] + (box['width'] * (0.1 + (i * 0.08)))
                await page.mouse.click(click_x, box['y'] + box['height'] / 2)
                
                # 결과 반영 대기 (Streamlit 리렌더링 시간 고려)
                await asyncio.sleep(1.5)
                
                current_val = await thumb.inner_text()
                history.append(current_val)
                print(f"Click {i+1}: Position ~{int((0.1 + (i * 0.08))*100)}% -> Value: {current_val}")
                
                if len(history) >= 2:
                    if history[-1] == history[-2]:
                        print("  ⚠️ Warning: Value did not change!")
                    elif len(history) >= 3 and history[-1] == history[-3]:
                        print("  🚨 BUG DETECTED: Value snapped back to previous state!")

            print("\n--- Summary of Values ---")
            print(" -> ".join(history))
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(reproduce_slider_bug())
