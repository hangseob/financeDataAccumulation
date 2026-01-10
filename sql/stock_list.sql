
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
