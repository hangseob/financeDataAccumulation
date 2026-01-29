import asyncio
from playwright.async_api import async_playwright
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

async def check_scroll_visually():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        
        url = "http://localhost:8503"
        print(f"Connecting to {url}...")
        await page.goto(url, wait_until="networkidle")

        # 앱 로드 대기
        await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        print("App loaded.")

        # 스크롤 가능한 요소 찾기
        scroll_selector = "section[data-testid='stMain']"
        
        # 1. 스크롤 수행 (800px)
        print("Scrolling down 800px...")
        await page.evaluate("selector => { const el = document.querySelector(selector); if (el) el.scrollTop = 800; }", scroll_selector)
        await asyncio.sleep(2)
        
        scroll_before = await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : 0; }", scroll_selector)
        print(f"Scroll position BEFORE: {scroll_before}")
        
        if scroll_before < 100:
            print("Trying mouse wheel scroll...")
            await page.mouse.move(640, 600)
            await page.mouse.wheel(0, 800)
            await asyncio.sleep(2)
            scroll_before = await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : 0; }", scroll_selector)
            print(f"Scroll position after wheel: {scroll_before}")

        # 2. "Tenor Collapse" 클릭
        checkbox = page.locator("label:has-text('Tenor Collapse')").first
        if await checkbox.is_visible():
            print("Clicking 'Tenor Collapse'...")
            await checkbox.click()
            
            print("Waiting for rerender (5s)...")
            await asyncio.sleep(5)
            
            # 3. 위치 확인
            scroll_after = await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : 0; }", scroll_selector)
            print(f"Scroll position AFTER: {scroll_after}")
            
            if scroll_after < scroll_before - 50:
                print(f"🚨 [BUG CONFIRMED] Scroll jumped from {scroll_before} to {scroll_after}!")
            else:
                print(f"✅ [SUCCESS] Scroll position {scroll_after} is maintained!")
        else:
            print("Widget not found.")
            await page.screenshot(path="debug_final.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_scroll_visually())
