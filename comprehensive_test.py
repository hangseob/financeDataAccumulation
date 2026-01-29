import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def run_comprehensive_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        
        url = "http://localhost:8505"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=90000)
            await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
            print("Page loaded.")

            async def get_scroll_top():
                return await page.evaluate("() => { const el = (document.querySelector('section[data-testid=\"stMain\"]') || document.querySelector('section.main')); return el ? el.scrollTop : 0; }")

            # --- BUG 1 TEST: Scroll top on slider change ---
            print("\n[Test 1] Testing scroll stability on slider click...")
            # Wait for main content to have height
            await asyncio.sleep(2)
            # Scroll down first
            await page.evaluate("() => { const el = (document.querySelector('section[data-testid=\"stMain\"]') || document.querySelector('section.main')); if(el) el.scrollTo(0, 500); }")
            await asyncio.sleep(1)
            initial_scroll = await get_scroll_top()
            print(f"  Initial Scroll: {initial_scroll}")

            slider = page.locator("div[data-testid='stSlider']")
            box = await slider.bounding_box()
            # Click slider at 50%
            await page.mouse.click(box['x'] + box['width']*0.5, box['y'] + box['height']/2)
            # Wait for rerender and scroll restoration
            await asyncio.sleep(3)
            
            final_scroll = await get_scroll_top()
            print(f"  Final Scroll: {final_scroll}")
            if final_scroll < initial_scroll - 100:
                print("  [FAIL] BUG 1 FAILED: Scroll jumped up!")
            else:
                print("  [PASS] BUG 1 FIXED: Scroll maintained.")

            # --- BUG 2 TEST: Scroll top on Start Date change ---
            print("\n[Test 2] Testing scroll stability on Start Date change...")
            # Wait for skeletons to disappear and date inputs to appear
            await page.wait_for_selector("div[data-testid='stDateInput']", timeout=60000)
            start_date_input = page.locator("div[data-testid='stDateInput'] input").nth(0)
            await start_date_input.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.keyboard.type("2019/01/17")
            await page.keyboard.press("Enter")
            # Wait for rerun
            await asyncio.sleep(5)
            
            current_scroll = await get_scroll_top()
            print(f"  Scroll after Start Date change: {current_scroll}")
            if current_scroll < 100:
                 print("  [FAIL] BUG 2 FAILED: Scroll jumped to top after date change!")
            else:
                 print("  [PASS] BUG 2 FIXED: Scroll maintained after date change.")

            # --- BUG 3 TEST: Slider ignores new Start Date ---
            print("\n[Test 3] Testing slider respects new Start Date (2019-01-17)...")
            thumb = page.locator("div[data-testid='stThumbValue']")
            # Click near the start of the slider (10%)
            await page.mouse.click(box['x'] + box['width']*0.1, box['y'] + box['height']/2)
            await asyncio.sleep(2)
            val = await thumb.inner_text()
            print(f"  Value after click: {val}")
            if "2016" in val:
                print("  [FAIL] BUG 3 FAILED: Slider reverted to 2016 range!")
            else:
                print("  [PASS] BUG 3 FIXED: Slider respects new 2019 range.")

            # --- BUG 4 TEST: Alternating/Snap-back values ---
            print("\n[Test 4] Testing alternating/snap-back (10 wide clicks)...")
            history = []
            for i in range(10):
                offsets = [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6, 0.5, 0.1]
                target = offsets[i]
                # Use locator.click with position for better reliability
                slider_el = page.locator("div[data-testid='stSlider']")
                box = await slider_el.bounding_box()
                await slider_el.click(position={'x': box['width']*target, 'y': box['height']/2})
                await asyncio.sleep(3.0) 
                val = await thumb.inner_text()
                history.append(val)
                print(f"  Click {i+1} (Target {int(target*100)}%): {val}")
                
                if i >= 2:
                    if history[i] == history[i-2] and history[i] != history[i-1]:
                        print(f"  [FAIL] BUG 4 DETECTED: Snap-back from {history[i-1]} to {val}!")
            else:
                unique_count = len(set(history))
                if unique_count >= 8:
                    print(f"  [PASS] BUG 4 FIXED: {unique_count} unique values, no snap-back pattern.")
                else:
                    print(f"  [FAIL] BUG 4 FAILED: Too few unique values ({unique_count}/10).")

        except Exception as e:
            print(f"Error during test: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
