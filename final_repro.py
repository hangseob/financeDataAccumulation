import asyncio
from playwright.async_api import async_playwright
import time

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8501')
        await page.wait_for_selector('div[data-testid="stSlider"]')
        
        slider = page.locator('div[data-testid="stSlider"]')
        thumb = page.locator('div[data-testid="stThumbValue"]')
        box = await slider.bounding_box()
        
        history = []
        print("--- Testing 20 clicks ---")
        for i in range(20):
            # 10% -> 15% -> 20% ... 지점 클릭
            off = 0.1 + (i * 0.04)
            await page.mouse.click(box['x'] + (box['width'] * off), box['y'] + box['height'] / 2)
            await asyncio.sleep(1.2) # 조금 더 빠르게 클릭
            
            val = await thumb.inner_text()
            history.append(val)
            print(f"Click {i+1}: {val}")
            
            if i >= 1 and history[i] == history[i-1]:
                print("  🚨 SNAP BACK / NO CHANGE DETECTED!")
        
        print("\nFull Sequence:", " -> ".join(history))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
