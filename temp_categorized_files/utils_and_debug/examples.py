"""
FinanceDataReader → Supabase 업로드 예시 스크립트

이 스크립트는 다양한 사용 사례를 보여줍니다.
"""
from supabase_finance_uploader import FinanceDataUploader, supabase
from datetime import datetime, timedelta
import time


def example_1_single_stock():
    """예시 1: 단일 종목 업로드"""
    print("\n" + "="*80)
    print("예시 1: 삼성전자 최근 1년 데이터 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    result = uploader.upload_stock_data(
        symbol='005930',
        start_date=start_date,
        table_name='stock_prices'
    )
    
    print(f"\n결과: {result}")


def example_2_multiple_stocks():
    """예시 2: 여러 종목 일괄 업로드"""
    print("\n" + "="*80)
    print("예시 2: 한국 대표 주식 10종목 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    
    # 한국 대표 주식 10종목
    symbols = [
        '005930',  # 삼성전자
        '000660',  # SK하이닉스
        '035420',  # NAVER
        '005380',  # 현대차
        '051910',  # LG화학
        '035720',  # 카카오
        '006400',  # 삼성SDI
        '000270',  # 기아
        '068270',  # 셀트리온
        '207940',  # 삼성바이오로직스
    ]
    
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    results = uploader.upload_multiple_stocks(
        symbols=symbols,
        start_date=start_date,
        table_name='stock_prices'
    )
    
    # 결과 요약
    print("\n" + "="*80)
    print("업로드 결과 요약:")
    print("="*80)
    for result in results:
        if result['success']:
            print(f"✓ {result['symbol']}: {result['records_uploaded']}개 업로드")
        else:
            print(f"✗ {result['symbol']}: {result['error']}")


def example_3_indices():
    """예시 3: 주요 지수 업로드"""
    print("\n" + "="*80)
    print("예시 3: 한국 및 미국 주요 지수 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    indices = {
        'KS11': 'KOSPI',
        'KQ11': 'KOSDAQ',
        'DJI': 'Dow Jones',
        'IXIC': 'NASDAQ',
        'US500': 'S&P 500',
    }
    
    for code, name in indices.items():
        print(f"\n{name} ({code}) 업로드 중...")
        result = uploader.upload_index_data(
            index_code=code,
            start_date=start_date,
            table_name='index_prices'
        )
        time.sleep(1)


def example_4_exchange_rates():
    """예시 4: 환율 데이터 업로드"""
    print("\n" + "="*80)
    print("예시 4: 주요 환율 데이터 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    currencies = ['USD/KRW', 'EUR/USD', 'JPY/KRW', 'CNY/KRW']
    
    for currency in currencies:
        print(f"\n{currency} 업로드 중...")
        result = uploader.upload_exchange_rate(
            currency_pair=currency,
            start_date=start_date,
            table_name='exchange_rates'
        )
        time.sleep(1)


def example_5_crypto():
    """예시 5: 암호화폐 데이터 업로드"""
    print("\n" + "="*80)
    print("예시 5: 주요 암호화폐 데이터 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    cryptos = ['BTC/USD', 'ETH/USD']
    
    for crypto in cryptos:
        print(f"\n{crypto} 업로드 중...")
        result = uploader.upload_crypto_data(
            crypto_pair=crypto,
            start_date=start_date,
            table_name='crypto_prices'
        )
        time.sleep(1)


def example_6_stock_lists():
    """예시 6: 종목 리스트 업로드"""
    print("\n" + "="*80)
    print("예시 6: 종목 리스트 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    
    markets = ['KRX', 'NASDAQ']
    
    for market in markets:
        print(f"\n{market} 종목 리스트 업로드 중...")
        result = uploader.upload_stock_list(
            market=market,
            table_name='stock_list'
        )
        time.sleep(2)


def example_7_historical_data():
    """예시 7: 과거 10년 데이터 업로드"""
    print("\n" + "="*80)
    print("예시 7: 삼성전자 과거 10년 데이터 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    
    # 10년 전부터
    start_date = (datetime.now() - timedelta(days=365*10)).strftime('%Y-%m-%d')
    
    result = uploader.upload_stock_data(
        symbol='005930',
        start_date=start_date,
        table_name='stock_prices',
        batch_size=1000
    )


def example_8_us_stocks():
    """예시 8: 미국 주식 업로드"""
    print("\n" + "="*80)
    print("예시 8: 미국 대표 주식 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    us_stocks = [
        'AAPL',   # Apple
        'MSFT',   # Microsoft
        'GOOGL',  # Google
        'AMZN',   # Amazon
        'TSLA',   # Tesla
        'NVDA',   # NVIDIA
        'META',   # Meta (Facebook)
    ]
    
    results = uploader.upload_multiple_stocks(
        symbols=us_stocks,
        start_date=start_date,
        table_name='stock_prices'
    )


def example_9_custom_date_range():
    """예시 9: 특정 기간 데이터 업로드"""
    print("\n" + "="*80)
    print("예시 9: 2024년 데이터만 업로드")
    print("="*80)
    
    uploader = FinanceDataUploader(supabase)
    
    result = uploader.upload_stock_data(
        symbol='005930',
        start_date='2024-01-01',
        end_date='2024-12-31',
        table_name='stock_prices'
    )


def example_10_all_kospi():
    """예시 10: KOSPI 전체 종목 업로드 (주의: 시간 오래 걸림)"""
    print("\n" + "="*80)
    print("예시 10: KOSPI 전체 종목 업로드")
    print("="*80)
    print("\n⚠ 주의: 이 작업은 매우 오래 걸립니다 (수 시간)")
    
    uploader = FinanceDataUploader(supabase)
    
    # KOSPI 종목 리스트 조회
    import FinanceDataReader as fdr
    kospi_list = fdr.StockListing('KOSPI')
    
    print(f"총 {len(kospi_list)}개 종목")
    
    # 상위 20개만 샘플로 업로드
    symbols = kospi_list['Code'].head(20).tolist()
    
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    results = uploader.upload_multiple_stocks(
        symbols=symbols,
        start_date=start_date,
        table_name='stock_prices'
    )


def main():
    """메인 메뉴"""
    print("\n" + "="*80)
    print("FinanceDataReader → Supabase 업로드 예시")
    print("="*80)
    
    print("\n실행할 예시를 선택하세요:")
    print("  1. 단일 종목 (삼성전자 1년)")
    print("  2. 여러 종목 (한국 대표 10종목)")
    print("  3. 주요 지수 (KOSPI, NASDAQ 등)")
    print("  4. 환율 (USD/KRW 등)")
    print("  5. 암호화폐 (BTC, ETH)")
    print("  6. 종목 리스트 (KRX, NASDAQ)")
    print("  7. 과거 10년 데이터")
    print("  8. 미국 주식 (AAPL, MSFT 등)")
    print("  9. 특정 기간 (2024년만)")
    print(" 10. KOSPI 전체 (샘플 20개)")
    print("  0. 전체 실행 (예시 1-6)")
    
    try:
        choice = input("\n선택 (0-10): ").strip()
        
        examples = {
            '1': example_1_single_stock,
            '2': example_2_multiple_stocks,
            '3': example_3_indices,
            '4': example_4_exchange_rates,
            '5': example_5_crypto,
            '6': example_6_stock_lists,
            '7': example_7_historical_data,
            '8': example_8_us_stocks,
            '9': example_9_custom_date_range,
            '10': example_10_all_kospi,
        }
        
        if choice == '0':
            # 전체 실행
            for i in range(1, 7):
                examples[str(i)]()
        elif choice in examples:
            examples[choice]()
        else:
            print("잘못된 선택입니다.")
            return
        
        print("\n" + "="*80)
        print("✓ 작업 완료!")
        print("="*80)
        print("\nSupabase 대시보드에서 데이터를 확인하세요:")
        print("https://supabase.com/dashboard")
        
    except KeyboardInterrupt:
        print("\n\n작업이 취소되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    main()
