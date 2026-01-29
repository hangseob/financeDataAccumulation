# FinanceDataReader 데이터 종류 및 가용 기간 정리

## 📊 데이터 카테고리 요약

FinanceDataReader는 다음 8가지 주요 카테고리의 금융 데이터를 제공합니다:

---

## 1. 한국 주식 시장 🇰🇷

### 이용 가능한 데이터:
- **전체 종목 수**: 2,901개 (KRX 전체)
- **시장 구분**: KOSPI, KOSDAQ, KONEX
- **제공 정보**: 
  - 종목코드, 종목명, 시장구분
  - 시가, 고가, 저가, 종가
  - 거래량, 거래대금
  - 시가총액, 상장주식수

### 과거 데이터 범위:
- **삼성전자(005930) 예시**: 
  - 시작일: **2013-10-22**
  - 약 **3,000일** 이상의 데이터 (약 12년)
  
### 사용 예시:
```python
import FinanceDataReader as fdr

# 전체 KRX 종목 리스트
krx_stocks = fdr.StockListing('KRX')

# 특정 종목 데이터
samsung = fdr.DataReader('005930', '2020-01-01')
```

---

## 2. 미국 주식 시장 🇺🇸

### 이용 가능한 데이터:
- **NASDAQ**: 3,773개 종목
- **NYSE**: 상장 종목 전체
- **AMEX**: 상장 종목 전체
- **S&P 500**: 구성 종목

### 과거 데이터 범위:
- **Apple(AAPL) 예시**:
  - 시작일: **1980-12-12**
  - 약 **11,361일** 이상의 데이터 (약 45년!)

### 사용 예시:
```python
# NASDAQ 종목 리스트
nasdaq = fdr.StockListing('NASDAQ')

# Apple 주식 데이터
aapl = fdr.DataReader('AAPL', '2020-01-01')
```

---

## 3. 주요 지수 📈

### 이용 가능한 지수 및 과거 데이터:

| 지수 코드 | 지수명 | 시작일 | 데이터 기간 |
|---------|--------|--------|------------|
| **KS11** | KOSPI | 1980-01-04 | ~12,229일 (46년) |
| **KQ11** | KOSDAQ | 1996-07-01 | ~7,395일 (29년) |
| **DJI** | 다우존스 | 1992-01-02 | ~8,567일 (34년) |
| **IXIC** | NASDAQ Composite | 1979-12-31 | ~11,602일 (46년) |
| **US500** | S&P 500 | 1979-12-31 | ~11,602일 (46년) |

### 사용 예시:
```python
# KOSPI 지수
kospi = fdr.DataReader('KS11', '2020-01-01')

# S&P 500 지수
sp500 = fdr.DataReader('US500', '2020-01-01')
```

---

## 4. 환율 💱

### 이용 가능한 환율 데이터:

| 통화쌍 | 시작일 | 데이터 기간 |
|--------|--------|------------|
| **USD/KRW** | 2003-12-01 | ~5,771일 (22년) |
| **EUR/USD** | 2003-12-01 | ~5,770일 (22년) |
| **JPY/KRW** | 2003-12-01 | ~5,770일 (22년) |

### 제공 정보:
- Open, High, Low, Close
- Volume, Adj Close

### 사용 예시:
```python
# 달러/원 환율
usd_krw = fdr.DataReader('USD/KRW', '2020-01-01')

# 유로/달러 환율
eur_usd = fdr.DataReader('EUR/USD', '2020-01-01')
```

---

## 5. 암호화폐 ₿

### 이용 가능한 암호화폐:

| 코드 | 암호화폐 | 시작일 | 데이터 기간 |
|------|---------|--------|------------|
| **BTC/USD** | 비트코인 | 2014-09-17 | ~4,134일 (11년) |
| **ETH/USD** | 이더리움 | 2017-11-09 | ~2,985일 (8년) |

### 사용 예시:
```python
# 비트코인 가격
btc = fdr.DataReader('BTC/USD', '2020-01-01')

# 이더리움 가격
eth = fdr.DataReader('ETH/USD', '2020-01-01')
```

---

## 6. 경제 지표 (FRED) 📊

### 이용 가능한 주요 경제 지표:

| 코드 | 지표명 | 시작일 | 데이터 기간 | 빈도 |
|------|--------|--------|------------|------|
| **FRED:GDP** | 미국 GDP | 1950-01-01 | ~303개 (75년) | 분기별 |
| **FRED:UNRATE** | 미국 실업률 | 1950-01-01 | ~912개 (75년) | 월별 |
| **FRED:DEXKOUS** | 원/달러 환율 | 1981-04-13 | ~11,670일 (44년) | 일별 |
| **FRED:DGS10** | 미국 10년물 국채 수익률 | 가용 | - | 일별 |

### 사용 예시:
```python
# 미국 GDP 데이터
gdp = fdr.DataReader('FRED:GDP', '2000-01-01')

# 미국 실업률
unemployment = fdr.DataReader('FRED:UNRATE', '2000-01-01')

# 원/달러 환율 (FRED 버전)
usd_krw = fdr.DataReader('FRED:DEXKOUS', '2000-01-01')
```

**참고**: FRED 데이터는 `FRED:코드` 형식으로 사용해야 합니다.

---

## 7. ETF 💼

### 이용 가능한 주요 ETF:

| 코드 | ETF명 | 시작일 | 데이터 기간 |
|------|-------|--------|------------|
| **SPY** | SPDR S&P 500 | 1993-01-29 | ~8,294일 (33년) |
| **QQQ** | Invesco QQQ | 1999-03-10 | ~6,752일 (26년) |
| **069500** | KODEX 200 | 2013-10-22 | ~3,000일 (12년) |

### 사용 예시:
```python
# SPY ETF
spy = fdr.DataReader('SPY', '2020-01-01')

# KODEX 200
kodex200 = fdr.DataReader('069500', '2020-01-01')
```

---

## 8. 상품 선물 🏆

### 이용 가능한 주요 상품:

| 코드 | 상품명 | 시작일 | 데이터 기간 |
|------|--------|--------|------------|
| **GC=F** | 금 선물 | 2000-08-30 | ~6,448일 (25년) |
| **CL=F** | 원유 선물 | 2000-08-23 | ~6,453일 (25년) |
| **SI=F** | 은 선물 | 2000-08-30 | ~6,448일 (25년) |

### 사용 예시:
```python
# 금 선물 가격
gold = fdr.DataReader('GC=F', '2020-01-01')

# 원유 선물 가격
oil = fdr.DataReader('CL=F', '2020-01-01')
```

---

## 📝 공통 제공 데이터 컬럼

대부분의 시계열 데이터는 다음 컬럼을 포함합니다:

- **Open**: 시가
- **High**: 고가
- **Low**: 저가
- **Close**: 종가
- **Volume**: 거래량
- **Change**: 변화율 (일부 데이터)
- **Adj Close**: 조정 종가 (일부 데이터)

---

## 💡 사용 팁

### 1. 종목 리스트 조회
```python
# 한국 주식
krx = fdr.StockListing('KRX')          # KRX 전체
kospi = fdr.StockListing('KOSPI')       # KOSPI만
kosdaq = fdr.StockListing('KOSDAQ')     # KOSDAQ만

# 미국 주식
nasdaq = fdr.StockListing('NASDAQ')     # NASDAQ
nyse = fdr.StockListing('NYSE')         # NYSE
sp500 = fdr.StockListing('SP500')       # S&P 500
```

### 2. 날짜 범위 지정
```python
# 특정 기간
df = fdr.DataReader('005930', '2020-01-01', '2023-12-31')

# 시작일만 지정 (오늘까지)
df = fdr.DataReader('005930', '2020-01-01')

# 최근 1년 데이터
from datetime import datetime, timedelta
start_date = datetime.now() - timedelta(days=365)
df = fdr.DataReader('005930', start_date)
```

### 3. 여러 종목 한번에 조회
```python
symbols = ['005930', '000660', '035420']  # 삼성전자, SK하이닉스, NAVER
data_dict = {}

for symbol in symbols:
    data_dict[symbol] = fdr.DataReader(symbol, '2020-01-01')
```

### 4. 데이터 가공 예시
```python
import pandas as pd

# 데이터 조회
df = fdr.DataReader('005930', '2020-01-01')

# 일간 수익률 계산
df['Returns'] = df['Close'].pct_change()

# 이동평균선 추가
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA60'] = df['Close'].rolling(window=60).mean()

# 데이터 저장
df.to_csv('samsung_stock_data.csv')
```

---

## ⚠️ 주의사항

1. **데이터 범위**: 각 종목/지표마다 데이터 시작일이 다릅니다. 과거 데이터를 조회할 때는 실제 데이터 시작일을 확인하세요.

2. **거래일 기준**: 주식 데이터는 거래일 기준이므로 주말과 공휴일 데이터는 없습니다.

3. **실시간 데이터**: FinanceDataReader는 일반적으로 종가 데이터를 제공하며, 실시간 데이터는 제공하지 않습니다.

4. **데이터 소스**: 데이터는 여러 소스(Yahoo Finance, KRX, FRED 등)에서 수집되므로, 소스별로 제공 범위가 다를 수 있습니다.

5. **API 제한**: 대량의 데이터를 빠르게 조회할 경우 데이터 소스의 API 제한에 걸릴 수 있습니다.

---

## 📚 참고 자료

- **공식 문서**: https://financedata.github.io/
- **GitHub**: https://github.com/FinanceData/FinanceDataReader
- **설치 방법**: `pip install finance-datareader`

---

## 🎯 주요 활용 사례

1. **포트폴리오 분석**: 여러 자산의 역사적 수익률 분석
2. **백테스팅**: 투자 전략의 과거 성과 테스트
3. **상관관계 분석**: 자산 간 상관관계 연구
4. **기술적 분석**: 이동평균선, RSI 등 기술적 지표 계산
5. **거시경제 분석**: 경제 지표와 주가의 관계 분석
6. **머신러닝**: 주가 예측 모델 학습 데이터로 활용

---

**생성일**: 2026-01-10  
**FinanceDataReader 버전**: 0.9.101
