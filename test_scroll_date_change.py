import asyncio
from playwright.async_api import async_playwright
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

async def test_scroll_after_date_change():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        
        url = "http://localhost:8503"
        print(f"Connecting to {url}...")
        await page.goto(url, wait_until="networkidle")

        await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        print("App loaded.")

        scroll_selector = "section[data-testid='stMain']"
        
        # 1. 스크롤 다운
        print("Scrolling down 600px...")
        await page.evaluate("selector => { const el = document.querySelector(selector); if (el) el.scrollTop = 600; }", scroll_selector)
        await asyncio.sleep(2)
        
        scroll_before = await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : 0; }", scroll_selector)
        print(f"Scroll position BEFORE date change: {scroll_before}")

        # 2. Start Date 변경 (사이드바의 date_input 클릭)
        # 사이드바에서 Start Date 입력 필드를 찾아서 클릭
        date_input = page.locator("input[aria-label='Start Date']").first
        if await date_input.is_visible():
            print("Clicking Start Date input...")
            await date_input.click()
            await asyncio.sleep(1)
            
            # 날짜 선택 (이전 달의 첫 날 선택 시도)
            prev_month_btn = page.locator("button[aria-label='Previous month']").first
            if await prev_month_btn.is_visible():
                await prev_month_btn.click()
                await asyncio.sleep(0.5)
                
                # 1일 클릭
                day_btn = page.locator("button:has-text('1')").first
                if await day_btn.is_visible():
                    await day_btn.click()
                    print("Date changed.")
                    
                    # 페이지 리런 대기
                    await asyncio.sleep(5)
                    
                    # 3. 스크롤 위치 확인
                    scroll_after = await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : 0; }", scroll_selector)
                    print(f"Scroll position AFTER date change: {scroll_after}")
                    
                    if scroll_after < scroll_before - 100:
                        print(f"🚨 [BUG] Scroll jumped from {scroll_before} to {scroll_after}!")
                    else:
                        print(f"✅ [SUCCESS] Scroll position maintained at {scroll_after}!")
                else:
                    print("Day button not found.")
            else:
                print("Previous month button not found.")
        else:
            print("Start Date input not found. Testing checkbox instead...")
            # 대안: 체크박스 테스트
            checkbox = page.locator("label:has-text('Tenor Collapse')").first
            if await checkbox.is_visible():
                await checkbox.click()
                await asyncio.sleep(5)
                scroll_after = await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : 0; }", scroll_selector)
                print(f"Scroll position AFTER checkbox click: {scroll_after}")
                if scroll_after < scroll_before - 100:
                    print(f"🚨 [BUG] Scroll jumped!")
                else:
                    print(f"✅ [SUCCESS] Scroll maintained!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_scroll_after_date_change())
