import asyncio
from playwright.async_api import async_playwright
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

async def debug_scroll_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1000})
        page = await context.new_page()
        
        url = "http://localhost:8503"
        print(f"Connecting to {url}...")
        await page.goto(url, wait_until="networkidle")

        await page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        print("App loaded.\n")

        scroll_selector = "section[data-testid='stMain']"

        # Helper 함수들
        async def get_scroll():
            return await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : -1; }", scroll_selector)

        async def get_saved_scroll():
            return await page.evaluate("() => parseInt(sessionStorage.getItem('st_scroll_y') || '0')")

        async def set_scroll(pos):
            await page.evaluate(f"""selector => {{ 
                const el = document.querySelector(selector); 
                if (el) {{ 
                    el.scrollTop = {pos}; 
                    el.dispatchEvent(new Event('scroll'));
                }}
            }}""", scroll_selector)
            await asyncio.sleep(2)

        # 1. 스크롤 설정 및 저장 확인
        print("=" * 50)
        print("DEBUG: 스크롤 설정 및 저장 확인")
        print("=" * 50)
        
        await set_scroll(500)
        current_scroll = await get_scroll()
        saved_scroll = await get_saved_scroll()
        print(f"  현재 스크롤 위치: {current_scroll}")
        print(f"  sessionStorage 저장값: {saved_scroll}")

        # 2. 체크박스 클릭 전후 확인
        print("\n" + "=" * 50)
        print("DEBUG: 체크박스 클릭 전후")
        print("=" * 50)
        
        scroll_before = await get_scroll()
        saved_before = await get_saved_scroll()
        print(f"  클릭 전 스크롤: {scroll_before}")
        print(f"  클릭 전 저장값: {saved_before}")

        checkbox = page.locator("label:has-text('Tenor Collapse')").first
        if await checkbox.is_visible():
            await checkbox.click()
            print("  체크박스 클릭!")
            
            # 0.5초 간격으로 10초간 모니터링
            for i in range(20):
                await asyncio.sleep(0.5)
                current = await get_scroll()
                saved = await get_saved_scroll()
                print(f"  [{i*0.5}s] 스크롤: {current}, 저장값: {saved}")
                
                if current > 100:  # 복구 성공
                    print(f"\n  ✅ 복구 성공! 최종 스크롤: {current}")
                    break
            else:
                final_scroll = await get_scroll()
                final_saved = await get_saved_scroll()
                print(f"\n  🚨 복구 실패. 최종 스크롤: {final_scroll}, 저장값: {final_saved}")
        else:
            print("  체크박스를 찾을 수 없음")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_scroll_test())
