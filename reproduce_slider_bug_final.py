import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def reproduce_slider_bug_final():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        url = "http://localhost:8501"
        print(f"Connecting to {url}...")
        
        try:
            # 타임아웃 넉넉하게 설정
            await page.goto(url, wait_until="load", timeout=90000)
            print("Initial load done. Waiting for content...")
            
            # 본문 로딩 확인
            await page.wait_for_selector("h1", timeout=60000)
            print("Title found.")
            
            # 1. 사이드바 날짜 변경 (직접 JS로 조작 시도)
            print("Attempting to change Start Date via UI...")
            # st.date_input은 보통 aria-label="Start Date" 또는 placeholder="YYYY/MM/DD" 를 가짐
            try:
                date_input = page.locator("input[aria-label='Start Date']").first
                await date_input.wait_for(state="visible", timeout=30000)
                await date_input.click()
                await date_input.fill("2019/01/17")
                await date_input.press("Enter")
                print("Filled date.")
                
                # Apply 버튼
                apply_btn = page.locator("button:has-text('Apply Period Settings')")
                await apply_btn.click()
                print("Clicked Apply.")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"UI interaction failed: {e}. Trying to proceed with default dates.")

            # 2. 슬라이더 테스트
            print("\n--- Starting Slider Clicks ---")
            await page.wait_for_selector("div[data-testid='stSlider']", timeout=30000)
            slider = page.locator("div[data-testid='stSlider']")
            thumb = page.locator("div[data-testid='stThumbValue']")
            
            box = await slider.bounding_box()
            if not box:
                print("Slider not visible.")
                return

            history = []
            # 30% -> 70% 반복 클릭하여 Alternating 현상 확인
            for i in range(10):
                target_offset = 0.3 if i % 2 == 0 else 0.7
                await page.mouse.click(box['x'] + (box['width'] * target_offset), box['y'] + box['height'] / 2)
                await asyncio.sleep(2)
                
                val = await thumb.inner_text()
                history.append(val)
                print(f"Click {i+1}: Offset {int(target_offset*100)}% -> Value: {val}")
                
                if i >= 2:
                    if history[i] == history[i-2] and history[i] != history[i-1]:
                        print("  🚨 BUG CONFIRMED: Values are alternating/snapping back!")

            print("\nFull History:", " -> ".join(history))
            
        except Exception as e:
            print(f"Error during script: {e}")
            await page.screenshot(path="debug_screenshot.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(reproduce_slider_bug_final())
