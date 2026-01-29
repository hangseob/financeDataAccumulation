import asyncio
from playwright.async_api import async_playwright
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

async def comprehensive_scroll_test():
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
        results = []

        # Helper: 스크롤 위치 가져오기
        async def get_scroll():
            return await page.evaluate("selector => { const el = document.querySelector(selector); return el ? el.scrollTop : 0; }", scroll_selector)

        # Helper: 스크롤 설정 및 저장 트리거
        async def set_scroll(pos):
            await page.evaluate(f"""selector => {{ 
                const el = document.querySelector(selector); 
                if (el) {{ 
                    el.scrollTop = {pos}; 
                    // 스크롤 이벤트 강제 발생
                    el.dispatchEvent(new Event('scroll'));
                }}
            }}""", scroll_selector)
            await asyncio.sleep(2)

        # Helper: 슬라이더 찾기 (여러 셀렉터 시도)
        async def find_slider():
            selectors = [
                "div[data-testid='stSlider']",
                "div[data-testid='stSelectSlider']", 
                "div[role='slider']",
                "input[type='range']",
                "div.stSlider",
            ]
            for sel in selectors:
                elem = page.locator(sel).first
                if await elem.count() > 0 and await elem.is_visible():
                    return elem
            return None

        # ============================================
        # 테스트 1: 스크롤 다운 후 날짜 슬라이더 움직임
        # ============================================
        print("=" * 50)
        print("TEST 1: 스크롤 다운 후 날짜 슬라이더 움직임")
        print("=" * 50)
        
        await set_scroll(500)
        scroll_before = await get_scroll()
        print(f"  스크롤 위치 BEFORE: {scroll_before}")

        slider = await find_slider()
        if slider:
            box = await slider.bounding_box()
            if box:
                await page.mouse.click(box['x'] + box['width'] * 0.8, box['y'] + box['height'] / 2)
                print("  날짜 슬라이더 클릭됨")
                await asyncio.sleep(4)
                
                scroll_after = await get_scroll()
                print(f"  스크롤 위치 AFTER: {scroll_after}")
                
                if scroll_after >= scroll_before - 50:
                    print("  ✅ TEST 1 PASSED: 스크롤 유지됨\n")
                    results.append(("TEST 1", True))
                else:
                    print(f"  🚨 TEST 1 FAILED: 스크롤이 {scroll_before} -> {scroll_after}로 튐\n")
                    results.append(("TEST 1", False))
            else:
                print("  ⚠️ 슬라이더 박스 찾기 실패, 체크박스로 대체")
                checkbox = page.locator("label:has-text('Tenor Collapse')").first
                if await checkbox.is_visible():
                    await checkbox.click()
                    await asyncio.sleep(4)
                    scroll_after = await get_scroll()
                    print(f"  스크롤 위치 AFTER (체크박스): {scroll_after}")
                    if scroll_after >= scroll_before - 50:
                        print("  ✅ TEST 1 PASSED (체크박스)\n")
                        results.append(("TEST 1", True))
                    else:
                        print(f"  🚨 TEST 1 FAILED\n")
                        results.append(("TEST 1", False))
                else:
                    results.append(("TEST 1", None))
        else:
            # 슬라이더 없으면 체크박스로 테스트
            print("  슬라이더 없음, 체크박스로 테스트...")
            checkbox = page.locator("label:has-text('Tenor Collapse')").first
            if await checkbox.is_visible():
                await checkbox.click()
                await asyncio.sleep(4)
                scroll_after = await get_scroll()
                print(f"  스크롤 위치 AFTER (체크박스): {scroll_after}")
                if scroll_after >= scroll_before - 50:
                    print("  ✅ TEST 1 PASSED (체크박스)\n")
                    results.append(("TEST 1", True))
                else:
                    print(f"  🚨 TEST 1 FAILED: {scroll_before} -> {scroll_after}\n")
                    results.append(("TEST 1", False))
            else:
                results.append(("TEST 1", None))

        # ============================================
        # 테스트 2: Curve ID 변경 (전체 리런 트리거)
        # ============================================
        print("=" * 50)
        print("TEST 2: Curve ID 변경 후 스크롤 유지")
        print("=" * 50)
        
        await set_scroll(400)
        scroll_before = await get_scroll()
        print(f"  스크롤 위치 BEFORE: {scroll_before}")

        # 사이드바의 selectbox 찾기
        selectbox = page.locator("section[data-testid='stSidebar'] div[data-testid='stSelectbox']").first
        if await selectbox.is_visible():
            await selectbox.click()
            await asyncio.sleep(1)
            # 다음 옵션 선택
            await page.keyboard.press("ArrowDown")
            await page.keyboard.press("Enter")
            print("  Curve ID 변경됨")
            await asyncio.sleep(5)
            
            scroll_after = await get_scroll()
            print(f"  스크롤 위치 AFTER: {scroll_after}")
            
            if scroll_after >= scroll_before - 50:
                print("  ✅ TEST 2 PASSED: 스크롤 유지됨\n")
                results.append(("TEST 2", True))
            else:
                print(f"  🚨 TEST 2 FAILED: {scroll_before} -> {scroll_after}\n")
                results.append(("TEST 2", False))
        else:
            print("  ⚠️ Selectbox 찾기 실패")
            results.append(("TEST 2", None))

        # ============================================
        # 테스트 3: 설정 변경 후 위젯 조작
        # ============================================
        print("=" * 50)
        print("TEST 3: 설정 변경 후 위젯 조작")
        print("=" * 50)
        
        await set_scroll(450)
        scroll_before = await get_scroll()
        print(f"  스크롤 위치 BEFORE: {scroll_before}")

        checkbox = page.locator("label:has-text('Tenor Collapse')").first
        if await checkbox.is_visible():
            await checkbox.click()
            await asyncio.sleep(4)
            
            scroll_after = await get_scroll()
            print(f"  스크롤 위치 AFTER: {scroll_after}")
            
            if scroll_after >= scroll_before - 50:
                print("  ✅ TEST 3 PASSED: 스크롤 유지됨\n")
                results.append(("TEST 3", True))
            else:
                print(f"  🚨 TEST 3 FAILED: {scroll_before} -> {scroll_after}\n")
                results.append(("TEST 3", False))
        else:
            print("  ⚠️ 체크박스 찾기 실패")
            results.append(("TEST 3", None))

        # ============================================
        # 최종 결과 요약
        # ============================================
        print("=" * 50)
        print("📊 최종 테스트 결과")
        print("=" * 50)
        passed = 0
        failed = 0
        for name, result in results:
            if result is True:
                print(f"  {name}: ✅ PASSED")
                passed += 1
            elif result is False:
                print(f"  {name}: 🚨 FAILED")
                failed += 1
            else:
                print(f"  {name}: ⚠️ SKIPPED")
        
        print(f"\n  총 {passed}/{len(results)} 테스트 통과")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(comprehensive_scroll_test())
