
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
