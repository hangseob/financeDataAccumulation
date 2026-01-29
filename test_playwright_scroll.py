import asyncio
from playwright.async_api import async_playwright
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

async def test_scroll_behavior():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        
        url = "http://localhost:8503"
        print(f"Connecting to {url}...")
        await page.goto(url, wait_until="networkidle")

        # 앱 로딩 대기
        await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        
        # 1. 스크롤 가능한 요소 찾기
        scroll_selector = await page.evaluate("""() => {
            const all = document.querySelectorAll('section, div');
            for (let el of all) {
                if (el.scrollHeight > el.clientHeight + 100) {
                    // stMain을 우선순위로
                    if (el.getAttribute('data-testid') === 'stMain') return 'section[data-testid="stMain"]';
                }
            }
            return 'section[data-testid="stMain"]';
        }""")
        print(f"Using selector: {scroll_selector}")

        # 강제 스크롤 및 위치 고정
        await page.evaluate(f"selector => {{ document.querySelector(selector).scrollTop = 600; }}", scroll_selector)
        await asyncio.sleep(2)
        
        scroll_pos_before = await page.evaluate(f"selector => document.querySelector(selector).scrollTop", scroll_selector)
        print(f"Scroll position BEFORE: {scroll_pos_before}")

        if scroll_pos_before < 100:
            print("Trying mouse wheel scroll...")
            await page.mouse.move(640, 600)
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)
            scroll_pos_before = await page.evaluate(f"selector => document.querySelector(selector).scrollTop", scroll_selector)
            print(f"Scroll position after wheel: {scroll_pos_before}")

        # 2. 위젯 클릭
        checkbox = page.locator("label:has-text('Tenor Collapse')").first
        if await checkbox.is_visible():
            print("Clicking Checkbox...")
            await checkbox.click()
            # 복구 로직(50ms)이 작동할 시간을 충분히 줍니다.
            await asyncio.sleep(5) 
            
            scroll_pos_after = await page.evaluate(f"selector => document.querySelector(selector).scrollTop", scroll_selector)
            print(f"Scroll position AFTER: {scroll_pos_after}")
            
            if scroll_pos_after < scroll_pos_before - 50:
                print("🚨 [BUG STILL PRESENT] SCROLL UP OCCURRED!")
            else:
                print("✅ [FIXED] SCROLL POSITION MAINTAINED.")
        else:
            print("Widget not found. Try increasing sleep or checking UI.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_scroll_behavior())
