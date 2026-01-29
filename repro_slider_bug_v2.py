import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def reproduce_slider_bug_with_config():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        url = "http://localhost:8501"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector("div[data-testid='stAppViewContainer']")
            
            # 1. 사이드바 기간 변경 (2019-01-17로 설정)
            print("Changing Start Date to 2019-01-17...")
            # 사이드바의 첫 번째 date_input (Start Date)
            date_inputs = page.locator("div[data-testid='stSidebar'] div[data-testid='stDateInput'] input")
            start_date_input = date_inputs.nth(0)
            await start_date_input.click()
            await start_date_input.fill("2019/01/17")
            await start_date_input.press("Enter")
            
            # Apply 버튼 클릭
            apply_btn = page.locator("button:has-text('Apply Period Settings')")
            await apply_btn.click()
            print("Applied new period. Waiting for refresh...")
            await asyncio.sleep(5)
            
            # 2. 메인 슬라이더 조작 테스트
            await page.wait_for_selector("div[data-testid='stSlider']")
            slider = page.locator("div[data-testid='stSlider']")
            thumb = page.locator("div[data-testid='stThumbValue']")
            
            history = []
            print("\n--- Starting Slider Click Test (After Config Change) ---")
            for i in range(10):
                box = await slider.bounding_box()
                # 30% -> 60% -> 40% -> 70% ... 이런식으로 왔다갔다 클릭
                offsets = [0.3, 0.6, 0.4, 0.7, 0.5, 0.8, 0.2, 0.9, 0.1, 0.5]
                click_x = box['x'] + (box['width'] * offsets[i])
                await page.mouse.click(click_x, box['y'] + box['height'] / 2)
                
                await asyncio.sleep(2) # 렌더링 대기
                
                current_val = await thumb.inner_text()
                history.append(current_val)
                print(f"Click {i+1}: Offset {int(offsets[i]*100)}% -> Value: {current_val}")
                
                if len(history) >= 2 and history[-1] == history[-2]:
                    print("  🚨 BUG DETECTED: Value did not change after click!")
                if len(history) >= 3 and history[-1] == history[-3]:
                    print("  🚨 BUG DETECTED: Value snapped back to previous state!")

            print("\n--- Summary of Values ---")
            print(" -> ".join(history))
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(reproduce_slider_bug_with_config())
