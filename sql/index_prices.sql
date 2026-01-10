
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
