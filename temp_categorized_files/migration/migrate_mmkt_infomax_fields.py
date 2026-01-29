import oracledb
import sys
import os
from supabase import create_client, Client
from supabase.client import ClientOptions

# --- Configuration ---
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"
SUPABASE_SCHEMA = "spt"
TARGET_TABLE_NAME = "mmkt_infomax_fields"

ORACLE_CONFIG = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}
ORACLE_SCHEMA = "SPT"

def migrate_correct_table():
    conn_oracle = None
    try:
        # 1. Supabase에서 명시된 테이블(mmkt_infomax_fields) 읽기 시도
        print(f"1. Supabase '{SUPABASE_SCHEMA}.{TARGET_TABLE_NAME}' 읽기 시도 중...")
        opts = ClientOptions(schema=SUPABASE_SCHEMA)
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
        
        # 명시된 테이블 외에 다른 테이블은 시도하지 않음
        response = supabase.table(TARGET_TABLE_NAME).select("*").execute()
        data = response.data

        if not data:
            print(f"⚠️ '{TARGET_TABLE_NAME}' 테이블에 데이터가 없거나 접근할 수 없습니다.")
            return

        print(f"✅ 데이터 읽기 성공! 총 {len(data)} 건")
        columns = list(data[0].keys())
        print(f"   컬럼: {columns}")

        # 2. Oracle 접속
        print(f"\n2. Oracle Cloud DB ({ORACLE_SCHEMA}) 접속 중...")
        conn_oracle = oracledb.connect(
            user=ORACLE_CONFIG["user"],
            password=ORACLE_CONFIG["password"],
            dsn=ORACLE_CONFIG["dsn"],
            config_dir=ORACLE_CONFIG["wallet_path"],
            wallet_location=ORACLE_CONFIG["wallet_path"],
            wallet_password=ORACLE_CONFIG["wallet_password"]
        )
        cursor = conn_oracle.cursor()

        # 3. Oracle 테이블 생성 (명시된 이름 그대로 사용)
        oracle_table_full = f"{ORACLE_SCHEMA}.{TARGET_TABLE_NAME.upper()}"
        print(f"\n3. Oracle 테이블 생성 및 초기화: {oracle_table_full}")
        
        # 기존 테이블 삭제
        cursor.execute(f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {oracle_table_full}'; EXCEPTION WHEN OTHERS THEN NULL; END;")
        
        # 컬럼 정의 (모든 컬럼을 VARCHAR2(4000)으로 생성하여 데이터 손실 방지)
        col_defs = []
        for col in columns:
            col_defs.append(f"{col.upper()} VARCHAR2(4000)")
        
        create_sql = f"CREATE TABLE {oracle_table_full} (\n    " + ",\n    ".join(col_defs) + "\n)"
        cursor.execute(create_sql)
        print("   테이블 생성 완료.")

        # 4. 데이터 업로드
        print(f"\n4. {len(data)}건 데이터 업로드 중...")
        placeholders = ", ".join([f":{i+1}" for i in range(len(columns))])
        insert_sql = f"INSERT INTO {oracle_table_full} ({', '.join([c.upper() for c in columns])}) VALUES ({placeholders})"
        
        rows = [tuple(item[col] for col in columns) for item in data]
        
        cursor.executemany(insert_sql, rows)
        
        conn_oracle.commit()
        print(f"✅ 이관 완료: {oracle_table_full} 에 {len(rows)} 행 저장됨.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        if conn_oracle:
            conn_oracle.rollback()
    finally:
        if conn_oracle:
            conn_oracle.close()
            print("\nOracle 연결 종료.")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    migrate_correct_table()
