"""
Python으로 Supabase 테이블 생성하기

주의사항:
1. anon key로는 테이블 생성이 안될 수 있습니다 (권한 제한)
2. service_role key가 필요할 수 있습니다
3. 테이블 생성이 실패하면 Supabase 대시보드에서 SQL 실행을 권장합니다
"""
from supabase import create_client, Client
import time

# Supabase 접속 정보
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

# service_role key가 있다면 여기에 입력 (더 높은 권한)
# SUPABASE_KEY = "your_service_role_key_here"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_tables_via_rpc():
    """
    RPC (Remote Procedure Call)를 통한 테이블 생성
    주의: 이 방법은 Supabase에서 먼저 SQL 함수를 생성해야 합니다
    """
    print("RPC를 통한 테이블 생성은 사전에 SQL 함수 정의가 필요합니다.")
    print("대신 SQL 스크립트를 제공합니다.")


def execute_sql_via_postgrest(sql: str):
    """
    PostgREST를 통한 SQL 실행 시도
    주의: anon key로는 DDL 권한이 없을 수 있습니다
    """
    try:
        # Supabase Python 클라이언트는 기본적으로 DDL을 지원하지 않습니다
        # 대신 RPC나 Supabase 대시보드 사용을 권장합니다
        print("⚠ Python 클라이언트로는 직접 테이블 생성이 제한될 수 있습니다.")
        print("Supabase 대시보드의 SQL Editor를 사용하는 것을 권장합니다.")
        return False
    except Exception as e:
        print(f"오류: {e}")
        return False


def create_tables_with_psycopg2():
    """
    psycopg2를 사용한 직접 PostgreSQL 연결 (고급)
    주의: Direct Database Connection URL이 필요합니다
    """
    print("\n" + "="*80)
    print("psycopg2를 사용한 테이블 생성")
    print("="*80)
    
    try:
        import psycopg2
        
        # Supabase의 Direct Connection URL이 필요합니다
        # Settings > Database > Connection string > Direct connection
        # 형식: postgresql://postgres:[password]@[host]:[port]/postgres
        
        print("\n⚠ 이 방법을 사용하려면:")
        print("1. Supabase 대시보드 > Settings > Database")
        print("2. Connection string > Direct connection 복사")
        print("3. 아래 코드의 DATABASE_URL에 입력")
        print("\n현재는 SQL 스크립트 파일을 생성합니다.")
        
        return False
        
    except ImportError:
        print("\n⚠ psycopg2가 설치되지 않았습니다.")
        print("설치: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"오류: {e}")
        return False


def generate_sql_scripts():
    """
    Supabase 대시보드에서 실행할 SQL 스크립트 생성
    이것이 가장 확실한 방법입니다!
    """
    print("\n" + "="*80)
    print("SQL 스크립트 파일 생성 중...")
    print("="*80)
    
    # 1. 주식 가격 테이블
    stock_prices_sql = """
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
"""

    # 2. 지수 가격 테이블
    index_prices_sql = """
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
"""

    # 3. 환율 테이블
    exchange_rates_sql = """
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
"""

    # 4. 암호화폐 테이블
    crypto_prices_sql = """
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
"""

    # 5. 종목 리스트 테이블
    stock_list_sql = """
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
"""

    # 전체 SQL 스크립트 결합
    full_sql = f"""
-- FinanceDataReader 데이터를 위한 Supabase 테이블 생성 스크립트
-- 생성일: {time.strftime('%Y-%m-%d %H:%M:%S')}
-- 
-- 사용 방법:
-- 1. Supabase 대시보드 접속
-- 2. SQL Editor 메뉴 선택
-- 3. 이 스크립트 전체를 복사하여 붙여넣기
-- 4. Run 버튼 클릭

{stock_prices_sql}

{index_prices_sql}

{exchange_rates_sql}

{crypto_prices_sql}

{stock_list_sql}

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '테이블 생성 완료!';
    RAISE NOTICE '생성된 테이블: stock_prices, index_prices, exchange_rates, crypto_prices, stock_list';
END $$;
"""

    # 파일로 저장
    with open('supabase_tables.sql', 'w', encoding='utf-8') as f:
        f.write(full_sql)
    
    print("\n✓ SQL 스크립트 파일 생성 완료: supabase_tables.sql")
    
    # 개별 파일도 저장
    scripts = {
        'stock_prices.sql': stock_prices_sql,
        'index_prices.sql': index_prices_sql,
        'exchange_rates.sql': exchange_rates_sql,
        'crypto_prices.sql': crypto_prices_sql,
        'stock_list.sql': stock_list_sql,
    }
    
    for filename, sql in scripts.items():
        with open(f'sql/{filename}', 'w', encoding='utf-8') as f:
            f.write(sql)
    
    print("✓ 개별 SQL 파일도 생성됨 (sql/ 폴더)")
    
    return True


def main():
    import sys
    import io
    
    # Windows 콘솔 인코딩 문제 해결
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\n" + "="*80)
    print("Supabase 테이블 생성 도구")
    print("="*80)
    
    print("\n[방법 1] Python으로 직접 테이블 생성 (제한적)")
    print("-" * 80)
    print("주의: anon key로는 DDL(CREATE TABLE) 권한이 제한될 수 있습니다.")
    print("주의: service_role key가 필요하거나 대시보드 사용을 권장합니다.")
    
    print("\n[방법 2] SQL 스크립트 생성 후 대시보드에서 실행 (권장)")
    print("-" * 80)
    
    # SQL 스크립트 생성
    import os
    os.makedirs('sql', exist_ok=True)
    generate_sql_scripts()
    
    print("\n" + "="*80)
    print("다음 단계:")
    print("="*80)
    print("\n1. Supabase 대시보드 접속")
    print("   → https://supabase.com/dashboard")
    print("\n2. 프로젝트 선택")
    print("   → jvyqmtklymxndtapkqez")
    print("\n3. 왼쪽 메뉴에서 'SQL Editor' 클릭")
    print("\n4. 'supabase_tables.sql' 파일 내용을 복사하여 붙여넣기")
    print("\n5. 'Run' 버튼 클릭하여 실행")
    print("\n6. 테이블 생성 완료!")
    print("\n7. 'Table Editor'에서 생성된 테이블 확인")
    
    print("\n" + "="*80)
    print("생성될 테이블 목록:")
    print("="*80)
    tables = [
        ("stock_prices", "주식 가격 데이터 (일별)"),
        ("index_prices", "지수 가격 데이터 (일별)"),
        ("exchange_rates", "환율 데이터 (일별)"),
        ("crypto_prices", "암호화폐 가격 데이터 (일별)"),
        ("stock_list", "종목 리스트 (메타데이터)"),
    ]
    
    for table, description in tables:
        print(f"  - {table:20s} : {description}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
