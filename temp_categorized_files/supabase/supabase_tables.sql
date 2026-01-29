
-- FinanceDataReader 데이터를 위한 Supabase 테이블 생성 스크립트
-- 생성일: 2026-01-10 22:32:21
-- 
-- 사용 방법:
-- 1. Supabase 대시보드 접속
-- 2. SQL Editor 메뉴 선택
-- 3. 이 스크립트 전체를 복사하여 붙여넣기
-- 4. Run 버튼 클릭


-- 주식 가격 데이터 테이블
CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(20, 4),
    high DECIMAL(20, 4),
    low DECIMAL(20, 4),
    close DECIMAL(20, 4),
    volume BIGINT,
    change DECIMAL(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, date)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices(symbol, date);

-- RLS (Row Level Security) 활성화
ALTER TABLE stock_prices ENABLE ROW LEVEL SECURITY;

-- 읽기 정책: 모든 사용자가 조회 가능
CREATE POLICY "Enable read access for all users" ON stock_prices
    FOR SELECT USING (true);

-- 쓰기 정책: 인증된 사용자만 삽입/수정 가능
CREATE POLICY "Enable insert for authenticated users only" ON stock_prices
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users only" ON stock_prices
    FOR UPDATE USING (true);

COMMENT ON TABLE stock_prices IS '주식 가격 데이터 (일별)';



-- 지수 가격 데이터 테이블
CREATE TABLE IF NOT EXISTS index_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(20, 4),
    high DECIMAL(20, 4),
    low DECIMAL(20, 4),
    close DECIMAL(20, 4),
    volume BIGINT,
    change DECIMAL(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_index_prices_symbol ON index_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_index_prices_date ON index_prices(date);
CREATE INDEX IF NOT EXISTS idx_index_prices_symbol_date ON index_prices(symbol, date);

ALTER TABLE index_prices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON index_prices
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON index_prices
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users only" ON index_prices
    FOR UPDATE USING (true);

COMMENT ON TABLE index_prices IS '지수 가격 데이터 (일별)';



-- 환율 데이터 테이블
CREATE TABLE IF NOT EXISTS exchange_rates (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(20, 6),
    high DECIMAL(20, 6),
    low DECIMAL(20, 6),
    close DECIMAL(20, 6),
    volume BIGINT,
    change DECIMAL(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_exchange_rates_symbol ON exchange_rates(symbol);
CREATE INDEX IF NOT EXISTS idx_exchange_rates_date ON exchange_rates(date);
CREATE INDEX IF NOT EXISTS idx_exchange_rates_symbol_date ON exchange_rates(symbol, date);

ALTER TABLE exchange_rates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON exchange_rates
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON exchange_rates
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users only" ON exchange_rates
    FOR UPDATE USING (true);

COMMENT ON TABLE exchange_rates IS '환율 데이터 (일별)';



-- 암호화폐 가격 데이터 테이블
CREATE TABLE IF NOT EXISTS crypto_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(20, 6),
    high DECIMAL(20, 6),
    low DECIMAL(20, 6),
    close DECIMAL(20, 6),
    volume BIGINT,
    change DECIMAL(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_crypto_prices_symbol ON crypto_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_prices_date ON crypto_prices(date);
CREATE INDEX IF NOT EXISTS idx_crypto_prices_symbol_date ON crypto_prices(symbol, date);

ALTER TABLE crypto_prices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON crypto_prices
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON crypto_prices
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users only" ON crypto_prices
    FOR UPDATE USING (true);

COMMENT ON TABLE crypto_prices IS '암호화폐 가격 데이터 (일별)';



-- 종목 리스트 테이블
CREATE TABLE IF NOT EXISTS stock_list (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200),
    market VARCHAR(50),
    close DECIMAL(20, 4),
    volume BIGINT,
    market_cap DECIMAL(30, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stock_list_code ON stock_list(code);
CREATE INDEX IF NOT EXISTS idx_stock_list_market ON stock_list(market);
CREATE INDEX IF NOT EXISTS idx_stock_list_name ON stock_list(name);

ALTER TABLE stock_list ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON stock_list
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON stock_list
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users only" ON stock_list
    FOR UPDATE USING (true);

COMMENT ON TABLE stock_list IS '종목 리스트 (메타데이터)';


-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '테이블 생성 완료!';
    RAISE NOTICE '생성된 테이블: stock_prices, index_prices, exchange_rates, crypto_prices, stock_list';
END $$;
