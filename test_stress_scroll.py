import asyncio
from playwright.async_api import async_playwright
import sys
import random

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

async def stress_test_scroll():
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

        async def get_scroll():
            js = """
                (() => {
                    const el = document.querySelector('section[data-testid="stMain"]');
                    return el ? el.scrollTop : 0;
                })()
            """
            return await page.evaluate(js)

        async def set_scroll_and_save(pos):
            """스크롤 설정 + sessionStorage 직접 저장"""
            js = f"""
                (() => {{
                    const el = document.querySelector('section[data-testid="stMain"]');
                    if (el) {{
                        el.scrollTop = {pos};
                        sessionStorage.setItem('st_scroll_y', '{pos}');
                    }}
                }})()
            """
            await page.evaluate(js)
            await asyncio.sleep(1)

        async def find_slider():
            selectors = [
                "div[data-testid='stSlider']",
                "div[data-testid='stSelectSlider']", 
            ]
            for sel in selectors:
                elem = page.locator(sel).first
                if await elem.count() > 0 and await elem.is_visible():
                    return elem
            return None

        async def click_slider_random(slider, times=20):
            """슬라이더를 랜덤 위치에서 여러 번 클릭"""
            box = await slider.bounding_box()
            if not box:
                return times  # 전부 실패로 처리
            
            failures = 0
            for i in range(times):
                x_ratio = 0.1 + random.random() * 0.8
                click_x = box['x'] + box['width'] * x_ratio
                click_y = box['y'] + box['height'] / 2
                
                await page.mouse.click(click_x, click_y)
                await asyncio.sleep(0.7)  # 리렌더링 대기
                
                scroll_now = await get_scroll()
                if scroll_now < 50:
                    failures += 1
                    print(f"    클릭 {i+1}: 🚨 스크롤 {scroll_now}으로 튐!")
                    # 스크롤 재설정 (테스트 계속 위해)
                    await set_scroll_and_save(500)
                else:
                    print(f"    클릭 {i+1}: ✅ 스크롤 {scroll_now} 유지")
            
            return failures

        results = []

        # ============================================
        # TEST 1: 스크롤 다운 후 슬라이더 20회 클릭
        # ============================================
        print("=" * 60)
        print("TEST 1: 스크롤 다운 후 슬라이더 20회 클릭")
        print("=" * 60)
        
        await set_scroll_and_save(500)
        scroll_before = await get_scroll()
        print(f"  시작 스크롤 위치: {scroll_before}\n")

        slider = await find_slider()
        if slider:
            failures = await click_slider_random(slider, 20)
            print(f"\n  실패 횟수: {failures}/20")
            if failures == 0:
                print("  ✅ TEST 1 PASSED\n")
            else:
                print(f"  🚨 TEST 1 FAILED\n")
            results.append(("TEST 1", failures))
        else:
            print("  ⚠️ 슬라이더 없음")
            results.append(("TEST 1", -1))

        # ============================================
        # TEST 2: Curve ID 변경 후 슬라이더 20회 클릭
        # ============================================
        print("=" * 60)
        print("TEST 2: Curve ID 변경 후 슬라이더 20회 클릭")
        print("=" * 60)
        
        selectbox = page.locator("section[data-testid='stSidebar'] div[data-testid='stSelectbox']").first
        if await selectbox.is_visible():
            await selectbox.click()
            await asyncio.sleep(0.5)
            await page.keyboard.press("ArrowDown")
            await page.keyboard.press("Enter")
            print("  Curve ID 변경됨")
            await asyncio.sleep(3)
        
        await set_scroll_and_save(500)
        scroll_before = await get_scroll()
        print(f"  시작 스크롤 위치: {scroll_before}\n")

        slider = await find_slider()
        if slider:
            failures = await click_slider_random(slider, 20)
            print(f"\n  실패 횟수: {failures}/20")
            if failures == 0:
                print("  ✅ TEST 2 PASSED\n")
            else:
                print(f"  🚨 TEST 2 FAILED\n")
            results.append(("TEST 2", failures))
        else:
            print("  ⚠️ 슬라이더 없음")
            results.append(("TEST 2", -1))

        # ============================================
        # TEST 3: 체크박스 토글 후 슬라이더 20회 클릭
        # ============================================
        print("=" * 60)
        print("TEST 3: 체크박스 토글 후 슬라이더 20회 클릭")
        print("=" * 60)
        
        checkbox = page.locator("label:has-text('Tenor Collapse')").first
        if await checkbox.is_visible():
            await checkbox.click()
            print("  체크박스 토글됨")
            await asyncio.sleep(2)
        
        await set_scroll_and_save(500)
        scroll_before = await get_scroll()
        print(f"  시작 스크롤 위치: {scroll_before}\n")

        slider = await find_slider()
        if slider:
            failures = await click_slider_random(slider, 20)
            print(f"\n  실패 횟수: {failures}/20")
            if failures == 0:
                print("  ✅ TEST 3 PASSED\n")
            else:
                print(f"  🚨 TEST 3 FAILED\n")
            results.append(("TEST 3", failures))
        else:
            print("  ⚠️ 슬라이더 없음")
            results.append(("TEST 3", -1))

        # ============================================
        # 최종 결과
        # ============================================
        print("=" * 60)
        print("📊 최종 테스트 결과 (각 20회 클릭)")
        print("=" * 60)
        total_failures = 0
        for name, failures in results:
            if failures == -1:
                print(f"  {name}: ⚠️ SKIPPED")
            elif failures == 0:
                print(f"  {name}: ✅ PASSED (0회 튐)")
            else:
                print(f"  {name}: 🚨 FAILED ({failures}회 튐)")
                total_failures += failures

        await browser.close()

if __name__ == "__main__":
    asyncio.run(stress_test_scroll())
