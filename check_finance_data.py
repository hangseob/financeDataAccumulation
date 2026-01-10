"""
FinanceDataReader로 받아올 수 있는 데이터의 종류와 과거 데이터 가용 기간 확인
"""
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import pandas as pd

print("=" * 80)
print("FinanceDataReader 데이터 종류 및 가용 기간 분석")
print("=" * 80)

# 1. 한국 주식 종목 리스트
print("\n[1] 한국 주식 시장")
print("-" * 80)
try:
    krx_list = fdr.StockListing('KRX')
    print(f"KRX 전체 종목 수: {len(krx_list)}")
    print(f"컬럼: {list(krx_list.columns)}")
    print(f"\n샘플 (상위 5개):")
    print(krx_list.head())
    
    # 삼성전자 예시로 과거 데이터 확인
    print("\n[삼성전자(005930) 과거 데이터 확인]")
    samsung = fdr.DataReader('005930', '1990-01-01')
    print(f"최초 데이터 시작일: {samsung.index[0]}")
    print(f"최근 데이터 날짜: {samsung.index[-1]}")
    print(f"전체 데이터 기간: {len(samsung)}일")
    print(f"제공 컬럼: {list(samsung.columns)}")
    print(f"\n최초 5일 데이터:")
    print(samsung.head())
except Exception as e:
    print(f"오류: {e}")

# 2. 미국 주식
print("\n" + "=" * 80)
print("[2] 미국 주식 시장")
print("-" * 80)
try:
    nasdaq = fdr.StockListing('NASDAQ')
    print(f"NASDAQ 종목 수: {len(nasdaq)}")
    
    # Apple 예시
    print("\n[Apple(AAPL) 과거 데이터 확인]")
    aapl = fdr.DataReader('AAPL', '1980-01-01')
    print(f"최초 데이터 시작일: {aapl.index[0]}")
    print(f"최근 데이터 날짜: {aapl.index[-1]}")
    print(f"전체 데이터 기간: {len(aapl)}일")
except Exception as e:
    print(f"오류: {e}")

# 3. 주요 지수
print("\n" + "=" * 80)
print("[3] 주요 지수 데이터")
print("-" * 80)
indices = {
    'KS11': 'KOSPI',
    'KQ11': 'KOSDAQ',
    'DJI': 'Dow Jones Industrial Average',
    'IXIC': 'NASDAQ Composite',
    'US500': 'S&P 500',
}

for symbol, name in indices.items():
    try:
        data = fdr.DataReader(symbol, '1980-01-01')
        print(f"\n{name} ({symbol}):")
        print(f"  최초 데이터: {data.index[0]}")
        print(f"  최근 데이터: {data.index[-1]}")
        print(f"  데이터 기간: {len(data)}일")
    except Exception as e:
        print(f"\n{name} ({symbol}): 오류 - {e}")

# 4. 환율
print("\n" + "=" * 80)
print("[4] 환율 데이터")
print("-" * 80)
currencies = ['USD/KRW', 'EUR/USD', 'JPY/KRW']

for curr in currencies:
    try:
        data = fdr.DataReader(curr, '2000-01-01')
        print(f"\n{curr}:")
        print(f"  최초 데이터: {data.index[0]}")
        print(f"  최근 데이터: {data.index[-1]}")
        print(f"  데이터 기간: {len(data)}일")
        print(f"  제공 컬럼: {list(data.columns)}")
    except Exception as e:
        print(f"\n{curr}: 오류 - {e}")

# 5. 암호화폐
print("\n" + "=" * 80)
print("[5] 암호화폐 데이터")
print("-" * 80)
cryptos = ['BTC/USD', 'ETH/USD']

for crypto in cryptos:
    try:
        data = fdr.DataReader(crypto, '2010-01-01')
        print(f"\n{crypto}:")
        print(f"  최초 데이터: {data.index[0]}")
        print(f"  최근 데이터: {data.index[-1]}")
        print(f"  데이터 기간: {len(data)}일")
    except Exception as e:
        print(f"\n{crypto}: 오류 - {e}")

# 6. 경제 지표 (FRED) - 업데이트된 형식 사용
print("\n" + "=" * 80)
print("[6] 경제 지표 (FRED)")
print("-" * 80)
fred_indicators = {
    'FRED:GDP': '미국 GDP',
    'FRED:UNRATE': '미국 실업률',
    'FRED:CPIAUCSL': '미국 소비자물가지수',
    'FRED:DGS10': '미국 10년물 국채 수익률',
    'FRED:DEXKOUS': '원/달러 환율',
}

for code, name in fred_indicators.items():
    try:
        data = fdr.DataReader(code, '1950-01-01')
        print(f"\n{name} ({code}):")
        print(f"  최초 데이터: {data.index[0]}")
        print(f"  최근 데이터: {data.index[-1]}")
        print(f"  데이터 포인트: {len(data)}개")
    except Exception as e:
        print(f"\n{name} ({code}): 오류 - {e}")

# 7. ETF
print("\n" + "=" * 80)
print("[7] ETF 데이터")
print("-" * 80)
etfs = ['SPY', 'QQQ', '069500']  # SPY, QQQ, KODEX 200

for etf in etfs:
    try:
        data = fdr.DataReader(etf, '1990-01-01')
        print(f"\n{etf}:")
        print(f"  최초 데이터: {data.index[0]}")
        print(f"  최근 데이터: {data.index[-1]}")
        print(f"  데이터 기간: {len(data)}일")
    except Exception as e:
        print(f"\n{etf}: 오류 - {e}")

# 8. 상품 선물
print("\n" + "=" * 80)
print("[8] 상품 선물")
print("-" * 80)
commodities = ['GC=F', 'CL=F', 'SI=F']  # 금, 원유, 은

for comm in commodities:
    try:
        data = fdr.DataReader(comm, '1980-01-01')
        print(f"\n{comm}:")
        print(f"  최초 데이터: {data.index[0]}")
        print(f"  최근 데이터: {data.index[-1]}")
        print(f"  데이터 기간: {len(data)}일")
    except Exception as e:
        print(f"\n{comm}: 오류 - {e}")

print("\n" + "=" * 80)
print("데이터 확인 완료")
print("=" * 80)
