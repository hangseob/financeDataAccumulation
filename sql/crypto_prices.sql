
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
