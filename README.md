# FinanceDataReader → Supabase 데이터 수집 시스템

FinanceDataReader로 금융 데이터를 수집하고 Supabase에 자동으로 저장하는 완전한 솔루션입니다.

## 📁 프로젝트 구조

```
financeDataAccumulation/
├── supabase_finance_uploader.py    # 데이터 수집 및 업로드 메인 스크립트
├── create_supabase_tables.py       # 테이블 생성 SQL 스크립트 생성 도구
├── supabase_tables.sql             # Supabase 테이블 생성 SQL (통합)
├── check_finance_data.py           # 데이터 종류 및 가용 기간 확인 도구
├── sql/                            # 개별 테이블 SQL 파일
│   ├── stock_prices.sql
│   ├── index_prices.sql
│   ├── exchange_rates.sql
│   ├── crypto_prices.sql
│   └── stock_list.sql
├── FinanceDataReader_데이터_정리.md  # 데이터 상세 가이드
└── FinanceDataReader_요약표.md       # 빠른 참조 요약
```

## 🚀 빠른 시작 가이드

### 1단계: 필요한 라이브러리 설치

```bash
pip install finance-datareader supabase
```

### 2단계: Supabase 테이블 생성

#### 방법 A: Python 스크립트로 SQL 파일 생성 (권장)

```bash
python create_supabase_tables.py
```

이 스크립트는 `supabase_tables.sql` 파일을 생성합니다.

#### 방법 B: Supabase 대시보드에서 직접 실행

1. **Supabase 대시보드 접속**
   - https://supabase.com/dashboard
   - 프로젝트 선택: `jvyqmtklymxndtapkqez`

2. **SQL Editor 열기**
   - 왼쪽 메뉴에서 `SQL Editor` 클릭

3. **SQL 스크립트 실행**
   - `supabase_tables.sql` 파일 내용 복사
   - SQL Editor에 붙여넣기
   - `Run` 버튼 클릭

4. **테이블 확인**
   - 왼쪽 메뉴에서 `Table Editor` 클릭
   - 5개 테이블 생성 확인:
     - `stock_prices` (주식 가격)
     - `index_prices` (지수)
     - `exchange_rates` (환율)
     - `crypto_prices` (암호화폐)
     - `stock_list` (종목 리스트)

### 3단계: 데이터 수집 및 업로드

```python
from supabase_finance_uploader import FinanceDataUploader, supabase

# 업로더 인스턴스 생성
uploader = FinanceDataUploader(supabase)

# 예시 1: 삼성전자 최근 1년 데이터 업로드
uploader.upload_stock_data(
    symbol='005930',
    start_date='2024-01-01',
    table_name='stock_prices'
)

# 예시 2: 여러 종목 한번에 업로드
uploader.upload_multiple_stocks(
    symbols=['005930', '000660', '035420'],  # 삼성전자, SK하이닉스, NAVER
    start_date='2024-01-01'
)

# 예시 3: KOSPI 지수 업로드
uploader.upload_index_data(
    index_code='KS11',
    start_date='2024-01-01'
)

# 예시 4: 환율 업로드
uploader.upload_exchange_rate(
    currency_pair='USD/KRW',
    start_date='2024-01-01'
)

# 예시 5: 암호화폐 업로드
uploader.upload_crypto_data(
    crypto_pair='BTC/USD',
    start_date='2024-01-01'
)

# 예시 6: 종목 리스트 업로드
uploader.upload_stock_list(market='KRX')
```

### 간단 실행 (메인 함수)

```bash
python supabase_finance_uploader.py
```

이 명령은 자동으로 다음을 실행합니다:
- 한국 대표 주식 3종목 최근 1년 데이터
- KOSPI 지수 최근 1년 데이터
- USD/KRW 환율 최근 1년 데이터
- KRX 전체 종목 리스트

## 📊 생성되는 테이블 구조

### 1. stock_prices (주식 가격)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGSERIAL | 자동 증가 ID |
| symbol | VARCHAR(20) | 종목 코드 |
| date | DATE | 날짜 |
| open | DECIMAL(20,4) | 시가 |
| high | DECIMAL(20,4) | 고가 |
| low | DECIMAL(20,4) | 저가 |
| close | DECIMAL(20,4) | 종가 |
| volume | BIGINT | 거래량 |
| change | DECIMAL(10,6) | 변화율 |
| created_at | TIMESTAMP | 생성 시간 |
| updated_at | TIMESTAMP | 수정 시간 |

**제약조건**: `UNIQUE(symbol, date)` - 같은 종목의 같은 날짜 데이터는 중복 불가

**인덱스**:
- `idx_stock_prices_symbol` - 종목별 조회 최적화
- `idx_stock_prices_date` - 날짜별 조회 최적화
- `idx_stock_prices_symbol_date` - 복합 조회 최적화

### 2. index_prices (지수 가격)

stock_prices와 동일한 구조

### 3. exchange_rates (환율)

stock_prices와 동일한 구조 (소수점 자리 6자리로 더 정밀)

### 4. crypto_prices (암호화폐)

stock_prices와 동일한 구조 (소수점 자리 6자리로 더 정밀)

### 5. stock_list (종목 리스트)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGSERIAL | 자동 증가 ID |
| code | VARCHAR(20) | 종목 코드 (고유) |
| name | VARCHAR(200) | 종목명 |
| market | VARCHAR(50) | 시장 (KRX, KOSPI, NASDAQ 등) |
| close | DECIMAL(20,4) | 현재가 |
| volume | BIGINT | 거래량 |
| market_cap | DECIMAL(30,2) | 시가총액 |
| updated_at | TIMESTAMP | 수정 시간 |
| created_at | TIMESTAMP | 생성 시간 |

## 🔐 보안 (RLS - Row Level Security)

모든 테이블에 RLS가 적용되어 있습니다:

- **읽기**: 모든 사용자가 조회 가능
- **쓰기/수정**: 인증된 사용자만 가능

필요시 Supabase 대시보드에서 정책 수정 가능

## 💡 주요 기능

### 1. 자동 중복 제거 (Upsert)

같은 종목의 같은 날짜 데이터는 자동으로 업데이트됩니다.

```python
# 이미 존재하는 데이터를 다시 업로드해도 에러 없이 업데이트됨
uploader.upload_stock_data('005930', '2024-01-01')  # 첫 번째 실행
uploader.upload_stock_data('005930', '2024-01-01')  # 중복 업로드 - 자동 업데이트
```

### 2. 배치 처리

대량 데이터를 1000개씩 나눠서 업로드하여 API 제한 방지

```python
# 10년치 데이터도 안전하게 업로드
uploader.upload_stock_data('005930', '2015-01-01', '2024-12-31')
```

### 3. 진행 상황 표시

```
================================================================================
종목 005930 데이터 수집 시작...
기간: 2024-01-01 ~ 현재
================================================================================
✓ 데이터 수집 완료: 245개 레코드
  업로드 진행: 245/245 (100.0%)
✓ 업로드 완료: 245개 레코드
```

### 4. 여러 종목 일괄 처리

```python
# 10개 종목을 한번에 업로드
symbols = ['005930', '000660', '035420', '005380', '051910',
           '035720', '006400', '000270', '068270', '207940']

results = uploader.upload_multiple_stocks(
    symbols=symbols,
    start_date='2024-01-01'
)

# 결과 확인
for result in results:
    if result['success']:
        print(f"✓ {result['symbol']}: {result['records_uploaded']}개 업로드 완료")
    else:
        print(f"✗ {result['symbol']}: {result['error']}")
```

## 📈 사용 가능한 데이터

### 한국 시장
- **주식**: KRX 2,901개 종목 (~12년)
- **지수**: KOSPI (~46년), KOSDAQ (~29년)

### 미국 시장
- **주식**: NASDAQ 3,773개 종목 (~45년)
- **지수**: S&P 500, Dow Jones, NASDAQ Composite

### 기타
- **환율**: USD/KRW, EUR/USD 등 (~22년)
- **암호화폐**: BTC, ETH (~11년)
- **경제지표**: FRED 데이터 (~75년)

자세한 내용은 `FinanceDataReader_데이터_정리.md` 참고

## 🔍 데이터 조회 예시

### Supabase Python Client로 조회

```python
from supabase import create_client

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "your_key_here"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. 삼성전자 최근 30일 데이터
result = supabase.table('stock_prices') \
    .select('*') \
    .eq('symbol', '005930') \
    .order('date', desc=True) \
    .limit(30) \
    .execute()

# 2. 2024년 1월 모든 주식 종가
result = supabase.table('stock_prices') \
    .select('symbol, date, close') \
    .gte('date', '2024-01-01') \
    .lte('date', '2024-01-31') \
    .execute()

# 3. 거래량 상위 10개 종목
result = supabase.table('stock_prices') \
    .select('*') \
    .eq('date', '2024-01-10') \
    .order('volume', desc=True) \
    .limit(10) \
    .execute()

# 4. 가격 상승률 계산
result = supabase.table('stock_prices') \
    .select('symbol, date, close, change') \
    .eq('symbol', '005930') \
    .gte('date', '2024-01-01') \
    .order('date') \
    .execute()
```

### SQL로 직접 조회 (Supabase SQL Editor)

```sql
-- 1. 삼성전자 최근 30일 평균 종가
SELECT AVG(close) as avg_price
FROM stock_prices
WHERE symbol = '005930'
  AND date >= CURRENT_DATE - INTERVAL '30 days';

-- 2. 일별 거래량 순위
SELECT symbol, date, volume, close,
       RANK() OVER (PARTITION BY date ORDER BY volume DESC) as volume_rank
FROM stock_prices
WHERE date = '2024-01-10';

-- 3. 월별 평균 종가
SELECT symbol,
       DATE_TRUNC('month', date) as month,
       AVG(close) as avg_close,
       MAX(high) as max_high,
       MIN(low) as min_low
FROM stock_prices
WHERE symbol = '005930'
  AND date >= '2024-01-01'
GROUP BY symbol, DATE_TRUNC('month', date)
ORDER BY month;

-- 4. 이동평균선 (20일)
SELECT symbol, date, close,
       AVG(close) OVER (
           PARTITION BY symbol
           ORDER BY date
           ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
       ) as ma20
FROM stock_prices
WHERE symbol = '005930'
ORDER BY date DESC
LIMIT 100;
```

## ⚡ 성능 최적화

1. **배치 크기 조정**
```python
# 기본값: 1000개
uploader.upload_stock_data('005930', '2020-01-01', batch_size=500)
```

2. **인덱스 활용**
   - symbol, date로 조회 시 자동으로 인덱스 사용
   - 복합 조회도 최적화됨

3. **API 제한 방지**
   - 배치 사이에 자동 대기 (0.1초)
   - 여러 종목 업로드 시 0.5초 대기

## 🛠 문제 해결

### 문제 1: 테이블 생성 실패

**증상**: Python으로 테이블 생성 시 권한 오류

**해결방법**: Supabase 대시보드에서 직접 SQL 실행
1. `supabase_tables.sql` 파일 내용 복사
2. Supabase 대시보드 > SQL Editor
3. 붙여넣기 후 Run

### 문제 2: 업로드 시 속도 느림

**해결방법**: 배치 크기 조정
```python
uploader.upload_stock_data('005930', '2020-01-01', batch_size=500)
```

### 문제 3: 데이터 중복

**해결방법**: 이미 upsert로 처리됨 - 걱정 없음!

### 문제 4: API Rate Limit

**해결방법**: 
```python
import time

for symbol in symbols:
    uploader.upload_stock_data(symbol, '2024-01-01')
    time.sleep(1)  # 대기 시간 증가
```

## 📚 관련 문서

- `FinanceDataReader_데이터_정리.md` - 데이터 종류 상세 가이드
- `FinanceDataReader_요약표.md` - 빠른 참조 테이블
- `check_finance_data.py` - 실시간 데이터 확인 도구

## 🔗 유용한 링크

- **FinanceDataReader**: https://github.com/FinanceData/FinanceDataReader
- **Supabase**: https://supabase.com/docs
- **PostgreSQL**: https://www.postgresql.org/docs/

## 📝 라이센스

이 프로젝트는 자유롭게 사용 가능합니다.

## 👨‍💻 기여

개선 사항이나 버그 리포트는 언제든 환영합니다!

---

**마지막 업데이트**: 2026-01-10
