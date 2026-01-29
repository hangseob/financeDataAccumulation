"""
메트라이프 변액보험 기준가 크롤러

무배당 My Fund 변액유니버셜보험의 혼합성장형 기준가 데이터를 수집합니다.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime


def setup_driver():
    """Chrome 드라이버 설정"""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 브라우저 창 숨기기 (필요시 주석 해제)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--lang=ko-KR')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # webdriver-manager를 사용하여 자동으로 ChromeDriver 관리
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def crawl_metlife_data():
    """메트라이프 변액보험 기준가 데이터 크롤링"""
    
    url = "https://brand.metlife.co.kr/pn/paReal/retrieveVrinsPaBprcPcndList.do"
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    
    try:
        print("="*80)
        print("메트라이프 변액보험 기준가 크롤러 시작")
        print("="*80)
        
        # 1. 페이지 접속
        print("\n[1/7] 페이지 접속 중...")
        driver.get(url)
        time.sleep(2)
        
        # 2. "판매중지상품" 탭 클릭
        print("[2/7] 판매중지상품 탭 클릭...")
        discontinued_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '판매중지상품')]"))
        )
        discontinued_tab.click()
        time.sleep(2)
        
        # 3. 상품 선택 (무배당 My Fund 변액유니버셜보험)
        print("[3/7] 상품 선택: 무배당 My Fund 변액유니버셜보험...")
        
        # 상품 드롭다운 찾기
        selects = driver.find_elements(By.TAG_NAME, "select")
        
        # "무배당 My Fund 변액유니버셜보험" 선택 (정확한 상품명)
        product_found = False
        for select_elem in selects:
            try:
                options = select_elem.find_elements(By.TAG_NAME, "option")
                for option in options:
                    # "My Fund"와 "유니버셜" 둘 다 포함된 상품만 선택
                    if ("My Fund" in option.text or "My fund" in option.text) and "유니버셜" in option.text:
                        option.click()
                        print(f"   선택된 상품: {option.text}")
                        product_found = True
                        break
                if product_found:
                    break
            except:
                continue
        
        time.sleep(1)
        
        # 4. 검색 버튼 클릭
        print("[4/7] 검색 버튼 클릭...")
        search_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '검색')]")
        if search_buttons:
            search_buttons[0].click()
            time.sleep(2)
        
        # 5. 기준가현황 "보기" 클릭
        print("[5/7] 기준가현황 보기 클릭...")
        view_button = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "보기"))
        )
        view_button.click()
        time.sleep(2)
        
        # 새 창으로 전환
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        
        # 6. 혼합성장형 체크박스 선택
        print("[6/7] 혼합성장형 선택...")
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        
        for cb in checkboxes:
            try:
                parent = cb.find_element(By.XPATH, "..")
                if "혼합성장형" in parent.text:
                    if not cb.is_selected():
                        cb.click()
                        print("   ✓ 혼합성장형 선택 완료")
                    break
            except:
                continue
        
        time.sleep(1)
        
        # 7. 검색기간 3개월 선택
        print("[7/7] 검색기간 3개월 선택 후 검색...")
        three_months_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "3개월"))
        )
        three_months_link.click()
        time.sleep(1)
        
        # 검색 버튼 클릭
        search_button2 = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '검색')]"))
        )
        search_button2.click()
        time.sleep(3)
        
        # 8. 데이터 수집
        print("\n데이터 수집 중...")
        
        # 테이블 찾기
        table = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # 테이블 데이터 파싱
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        data = []
        headers = []
        
        for idx, row in enumerate(rows):
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                # 헤더 행
                cells = row.find_elements(By.TAG_NAME, "th")
                headers = [cell.text.strip() for cell in cells]
            else:
                # 데이터 행
                row_data = [cell.text.strip() for cell in cells]
                if row_data:
                    data.append(row_data)
        
        print(f"✓ {len(data)}개 레코드 수집 완료")
        
        # DataFrame 생성
        if headers:
            df = pd.DataFrame(data, columns=headers)
        else:
            df = pd.DataFrame(data, columns=['날짜', '기준가(원)'])
        
        # 데이터 정리
        if '기준가(원)' in df.columns:
            # 쉼표 제거 및 숫자 변환
            df['기준가(원)'] = df['기준가(원)'].str.replace(',', '').astype(float)
        
        # 날짜 형식 변환
        if '날짜' in df.columns:
            df['날짜'] = pd.to_datetime(df['날짜'])
        
        return df
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        print(f"현재 페이지 제목: {driver.title}")
        print(f"현재 URL: {driver.current_url}")
        
        # 스크린샷 저장
        screenshot_name = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_name)
        print(f"스크린샷 저장: {screenshot_name}")
        
        return None
        
    finally:
        driver.quit()


def save_to_excel(df, filename='메트라이프_혼합성장형_기준가.xlsx'):
    """데이터를 엑셀로 저장"""
    if df is None or df.empty:
        print("저장할 데이터가 없습니다.")
        return
    
    try:
        # 엑셀 저장
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n✓ 엑셀 파일 저장 완료: {filename}")
        
        # 통계 정보 출력
        print("\n" + "="*80)
        print("수집 데이터 요약")
        print("="*80)
        print(f"총 데이터 개수: {len(df)}개")
        if '날짜' in df.columns:
            print(f"기간: {df['날짜'].min()} ~ {df['날짜'].max()}")
        if '기준가(원)' in df.columns:
            print(f"최고 기준가: {df['기준가(원)'].max():,.2f}원")
            print(f"최저 기준가: {df['기준가(원)'].min():,.2f}원")
            print(f"평균 기준가: {df['기준가(원)'].mean():,.2f}원")
        
        print("\n데이터 미리보기 (상위 5개):")
        print(df.head())
        
    except ImportError:
        print("\n⚠ openpyxl이 설치되지 않았습니다.")
        print("설치: pip install openpyxl")
        
        # CSV로 대신 저장
        csv_filename = filename.replace('.xlsx', '.csv')
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"✓ CSV 파일 저장 완료: {csv_filename}")
        
    except Exception as e:
        print(f"✗ 저장 오류: {e}")


def main():
    """메인 실행 함수"""
    print("\n" + "="*80)
    print("메트라이프 변액보험 기준가 자동 수집")
    print("="*80)
    print("\n대상 상품: 무배당 My Fund 변액유니버셜보험")
    print("펀드 유형: 혼합성장형")
    print("조회 기간: 최근 3개월")
    print("\n" + "="*80)
    
    # 필요한 라이브러리 확인
    try:
        import selenium
        print("✓ Selenium 설치 확인")
    except ImportError:
        print("✗ Selenium이 설치되지 않았습니다.")
        print("설치: pip install selenium")
        return
    
    try:
        import openpyxl
        print("✓ openpyxl 설치 확인")
    except ImportError:
        print("⚠ openpyxl이 설치되지 않았습니다. CSV로 저장됩니다.")
        print("설치: pip install openpyxl")
    
    print("\n크롤링을 시작합니다...")
    print("(Chrome 브라우저가 자동으로 열립니다)")
    time.sleep(2)
    
    # 데이터 수집
    df = crawl_metlife_data()
    
    # 엑셀 저장
    if df is not None:
        save_to_excel(df)
        
        print("\n" + "="*80)
        print("✓ 작업 완료!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ 데이터 수집 실패")
        print("="*80)


if __name__ == "__main__":
    main()
