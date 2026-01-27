import oracledb
import sys
import os
import time
from supabase import create_client, Client
from supabase.client import ClientOptions

# --- Configuration ---
# Supabase
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"
SUPABASE_SCHEMA = "spt"
SUPABASE_TABLE = "mmkt_infomax_fields" # Will also try mmkt_infomax_fields_supabase if this fails

# Oracle
ORACLE_CONFIG = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}
TARGET_SCHEMA = "SPT"
TARGET_TABLE = "MMKT_INFOMAX_FIELDS" # Will match whatever is found in Supabase

def migrate_data():
    conn_oracle = None
    try:
        # 1. Connect to Supabase and fetch data
        print(f"1. Supabase에서 데이터 가져오는 중 (Schema: {SUPABASE_SCHEMA})...")
        opts = ClientOptions(schema=SUPABASE_SCHEMA)
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
        
        data = []
        actual_table_name = SUPABASE_TABLE
        try:
            response = supabase.table(actual_table_name).select("*").execute()
            data = response.data
        except Exception:
            actual_table_name = "mmkt_infomax_fields_supabase"
            print(f"   - '{SUPABASE_TABLE}' 테이블을 찾을 수 없어 '{actual_table_name}' 시도 중...")
            response = supabase.table(actual_table_name).select("*").execute()
            data = response.data

        if not data:
            print("❌ 옮길 데이터가 없습니다.")
            return

        print(f"   - 총 {len(data)} 건의 데이터를 가져왔습니다.")
        columns = list(data[0].keys())
        print(f"   - 컬럼 구조: {columns}")

        # 2. Connect to Oracle
        print("\n2. Oracle Cloud DB 접속 중 (ADMIN)...")
        conn_oracle = oracledb.connect(
            user=ORACLE_CONFIG["user"],
            password=ORACLE_CONFIG["password"],
            dsn=ORACLE_CONFIG["dsn"],
            config_dir=ORACLE_CONFIG["wallet_path"],
            wallet_location=ORACLE_CONFIG["wallet_path"],
            wallet_password=ORACLE_CONFIG["wallet_password"]
        )
        cursor = conn_oracle.cursor()
        print("   - 접속 성공!")

        # 3. Create Table in Oracle (SPT Schema)
        # Use the same table name as found in Supabase (all caps for Oracle convention)
        oracle_table_name = f"{TARGET_SCHEMA}.{actual_table_name.upper()}"
        
        print(f"\n3. Oracle 테이블 생성 및 초기화 중 ({oracle_table_name})...")
        cursor.execute(f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {oracle_table_name}'; EXCEPTION WHEN OTHERS THEN NULL; END;")
        
        # Build CREATE TABLE SQL dynamically based on columns
        col_defs = []
        for col in columns:
            # Simple mapping: all as VARCHAR2(4000) for safety, except known keys
            if col.lower() == 'rate_id':
                col_defs.append(f"{col.upper()} VARCHAR2(100) PRIMARY KEY")
            else:
                col_defs.append(f"{col.upper()} VARCHAR2(4000)")
        
        create_sql = f"CREATE TABLE {oracle_table_name} (\n    " + ",\n    ".join(col_defs) + "\n)"
        cursor.execute(create_sql)
        print("   - 테이블 생성 완료.")

        # 4. Insert Data
        print(f"\n4. 데이터 업로드 시작...")
        placeholders = ", ".join([f":{i+1}" for i in range(len(columns))])
        insert_sql = f"INSERT INTO {oracle_table_name} ({', '.join([c.upper() for c in columns])}) VALUES ({placeholders})"
        
        # Prepare data rows
        rows_to_insert = []
        for item in data:
            rows_to_insert.append(tuple(item[col] for col in columns))
        
        cursor.executemany(insert_sql, rows_to_insert)
        conn_oracle.commit()
        print(f"   - 완료! {len(rows_to_insert)} 행이 {oracle_table_name}에 저장되었습니다.")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
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
    migrate_data()
