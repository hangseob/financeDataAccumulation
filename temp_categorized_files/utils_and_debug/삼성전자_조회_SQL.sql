-- ================================================================================
-- 삼성전자 주가 조회 SQL 모음
-- ================================================================================

-- ------------------------------------------------------------
-- 1. 최근 한 달 데이터 (최신순)
-- ------------------------------------------------------------
SELECT 
    date as 날짜,
    symbol as 종목코드,
    close as 종가,
    open as 시가,
    high as 고가,
    low as 저가,
    volume as 거래량,
    change as 변화율
FROM stock_prices
WHERE symbol = '005930'
  AND date >= CURRENT_DATE - INTERVAL '1 month'
ORDER BY date DESC;


-- ------------------------------------------------------------
-- 2. 최근 한 달 데이터 (포맷팅 버전)
-- ------------------------------------------------------------
SELECT 
    TO_CHAR(date, 'YYYY-MM-DD') as 날짜,
    TO_CHAR(close, '999,999,999') as 종가,
    TO_CHAR(volume, '999,999,999,999') as 거래량,
    CASE 
        WHEN change > 0 THEN CONCAT('+', ROUND(change * 100, 2), '%')
        WHEN change < 0 THEN CONCAT(ROUND(change * 100, 2), '%')
        ELSE '0%'
    END as 등락률
FROM stock_prices
WHERE symbol = '005930'
  AND date >= CURRENT_DATE - INTERVAL '1 month'
ORDER BY date DESC;


-- ------------------------------------------------------------
-- 3. 정확히 30일치 데이터
-- ------------------------------------------------------------
SELECT 
    date as 날짜,
    close as 종가,
    open as 시가,
    high as 고가,
    low as 저가,
    volume as 거래량,
    ROUND((change * 100)::numeric, 2) as 등락률
FROM stock_prices
WHERE symbol = '005930'
  AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;


-- ------------------------------------------------------------
-- 4. 최근 한 달 + 통계 정보
-- ------------------------------------------------------------
SELECT 
    date as 날짜,
    close as 종가,
    volume as 거래량,
    -- 20일 이동평균
    AVG(close) OVER (
        ORDER BY date 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as 이동평균_20일,
    -- 최고가 대비 현재가
    ROUND(((close - MAX(high) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)) / 
           MAX(high) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) * 100)::numeric, 2) as 최고가대비
FROM stock_prices
WHERE symbol = '005930'
  AND date >= CURRENT_DATE - INTERVAL '1 month'
ORDER BY date DESC;


-- ------------------------------------------------------------
-- 5. 최근 한 달 요약 통계
-- ------------------------------------------------------------
SELECT 
    '삼성전자' as 종목명,
    '005930' as 종목코드,
    COUNT(*) as 거래일수,
    MIN(date) as 시작일,
    MAX(date) as 마지막일,
    ROUND(AVG(close)::numeric, 0) as 평균종가,
    MAX(high) as 최고가,
    MIN(low) as 최저가,
    ROUND(AVG(volume)::numeric, 0) as 평균거래량,
    ROUND((
        (MAX(CASE WHEN date = (SELECT MAX(date) FROM stock_prices WHERE symbol = '005930' AND date >= CURRENT_DATE - INTERVAL '1 month') THEN close END) - 
         MIN(CASE WHEN date = (SELECT MIN(date) FROM stock_prices WHERE symbol = '005930' AND date >= CURRENT_DATE - INTERVAL '1 month') THEN close END)) /
        MIN(CASE WHEN date = (SELECT MIN(date) FROM stock_prices WHERE symbol = '005930' AND date >= CURRENT_DATE - INTERVAL '1 month') THEN close END) * 100
    )::numeric, 2) as 기간수익률
FROM stock_prices
WHERE symbol = '005930'
  AND date >= CURRENT_DATE - INTERVAL '1 month';


-- ------------------------------------------------------------
-- 6. 최근 20거래일 (영업일 기준)
-- ------------------------------------------------------------
SELECT 
    date as 날짜,
    close as 종가,
    volume as 거래량,
    ROUND((change * 100)::numeric, 2) as 등락률,
    -- 전일 대비 가격 변동
    close - LAG(close) OVER (ORDER BY date DESC) as 전일대비,
    -- 거래량 증감
    volume - LAG(volume) OVER (ORDER BY date DESC) as 거래량증감
FROM stock_prices
WHERE symbol = '005930'
ORDER BY date DESC
LIMIT 20;


-- ------------------------------------------------------------
-- 7. 간단 버전 (가장 많이 사용)
-- ------------------------------------------------------------
SELECT 
    date,
    close,
    volume,
    ROUND((change * 100)::numeric, 2) as change_pct
FROM stock_prices
WHERE symbol = '005930'
  AND date >= CURRENT_DATE - INTERVAL '1 month'
ORDER BY date DESC;


-- ================================================================================
-- Python으로 조회하는 방법
-- ================================================================================

/*
from supabase import create_client

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "your_key_here"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 방법 1: 최근 한 달
from datetime import datetime, timedelta

one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

result = supabase.table('stock_prices') \
    .select('date, close, open, high, low, volume, change') \
    .eq('symbol', '005930') \
    .gte('date', one_month_ago) \
    .order('date', desc=True) \
    .execute()

# 데이터프레임으로 변환
import pandas as pd
df = pd.DataFrame(result.data)
print(df)


# 방법 2: 최근 20거래일
result = supabase.table('stock_prices') \
    .select('*') \
    .eq('symbol', '005930') \
    .order('date', desc=True) \
    .limit(20) \
    .execute()

df = pd.DataFrame(result.data)
print(df)
*/
