import asyncio
from playwright.async_api import async_playwright
import time

async def run_test():
    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "http://localhost:8503"
        print(f"Connecting to {url}...")
        
        try:
            await page.goto(url, wait_until="load", timeout=60000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return

        # 페이지 로딩 대기 (더 긴 타임아웃과 스크린샷)
        print("Waiting for any element...")
        try:
            await page.wait_for_selector("div.stApp", timeout=30000)
            print("stApp found.")
        except:
            print("stApp not found. Taking screenshot for debug...")
            await page.screenshot(path="debug_screenshot.png")
            print(f"Page content snippet: {(await page.content())[:500]}")
            await browser.close()
            return

        # 1. 스크롤 다운 수행
        # Streamlit의 메인 컨텐츠 영역을 동적으로 찾습니다.
        print("Finding scrollable container...")
        scroll_element_selector = await page.evaluate("""
            () => {
                const selectors = ['section.main', 'div.stAppViewMain', 'div.stMain', '.main'];
                for (const s of selectors) {
                    if (document.querySelector(s)) return s;
                }
                return 'window';
            }
        """)
        print(f"Detected scrollable container: {scroll_element_selector}")
        
        # 현재 스크롤 위치 확인 함수
        async def get_scroll_top():
            if scroll_element_selector == 'window':
                return await page.evaluate("window.pageYOffset")
            return await page.evaluate(f"document.querySelector('{scroll_element_selector}').scrollTop")

        print("Scrolling down...")
        if scroll_element_selector == 'window':
            await page.evaluate("window.scrollTo(0, 1000)")
        else:
            await page.evaluate(f"document.querySelector('{scroll_element_selector}').scrollTop = 1000")
        
        await asyncio.sleep(2) # 스크롤 반영 대기
        
        initial_scroll_pos = await get_scroll_top()
        print(f"Initial scroll position: {initial_scroll_pos}")

        if initial_scroll_pos < 100:
            print("Scroll might not have worked as expected. Trying forced scroll...")
            await page.evaluate(f"document.querySelector('{scroll_element_selector}').scrollTo(0, 1000)")
            await asyncio.sleep(1)
            initial_scroll_pos = await get_scroll_top()
            print(f"Re-checked scroll position: {initial_scroll_pos}")

        # 2. 슬라이드 바(Select Slider) 찾기 및 클릭
        # 'View Curve' 텍스트를 가진 슬라이더 영역을 찾습니다.
        print("Searching for slider...")
        # Streamlit slider는 보통 div[data-testid='stSlider'] 또는 텍스트로 찾을 수 있습니다.
        slider = page.get_by_text("View Curve")
        if await slider.count() > 0:
            print("Slider found. Clicking...")
            # 슬라이더의 특정 지점을 클릭하여 값이 변경되도록 유도
            box = await slider.bounding_box()
            if box:
                # 슬라이더 바의 중간 지점 클릭
                await page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                print("Clicked slider.")
            else:
                await slider.click()
                print("Clicked slider (fallback).")
        else:
            print("Slider 'View Curve' not found.")
            # 다른 방식으로 시도 (모든 slider 찾기)
            sliders = page.locator("div[data-testid='stSlider']")
            if await sliders.count() > 0:
                print(f"Found {await sliders.count()} sliders. Clicking first one...")
                await sliders.first.click()
            else:
                print("No sliders found at all.")
                await browser.close()
                return

        # 3. 리렌더링 및 스크롤 변화 대기
        print("Waiting for potential scroll up...")
        await asyncio.sleep(3) # 리렌더링 및 스크롤 보존 로직 작동 대기

        final_scroll_pos = await get_scroll_top()
        print(f"Final scroll position: {final_scroll_pos}")

        # 4. 결과 판정
        if final_scroll_pos < initial_scroll_pos - 100: # 100px 이상 차이나면 스크롤 업으로 간주
            print("\n[RESULT] BUG DETECTED: Scroll up occurred!")
            print(f"   Pos changed: {initial_scroll_pos} -> {final_scroll_pos}")
        else:
            print("\n[RESULT] NO BUG: Scroll position maintained.")
            print(f"   Pos maintained: {initial_scroll_pos} -> {final_scroll_pos}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
