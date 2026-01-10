
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
