import oracledb
import sys
import time

# Oracle Cloud DB 접속 정보
config = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}

target_schema = "HANGSEOB"
table_name = "DATA_FROM_INFOMAX"
backup_table = f"{table_name}_OLD"

def transform_table_types():
    conn = None
    try:
        # DB 접속
        print(f"Connecting to Oracle Cloud DB...")
        conn = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"],
            config_dir=config["wallet_path"],
            wallet_location=config["wallet_path"],
            wallet_password=config["wallet_password"]
        )
        cursor = conn.cursor()
        print("✅ Connected!")

        # 1. 기존 테이블 이름 변경 (백업)
        print(f"1. Renaming current table to {backup_table}...")
        cursor.execute(f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {target_schema}.{backup_table}'; EXCEPTION WHEN OTHERS THEN NULL; END;")
        cursor.execute(f"ALTER TABLE {target_schema}.{table_name} RENAME TO {backup_table}")

        # 2. 새로운 타입으로 정식 테이블 생성
        print(f"2. Creating new {table_name} with proper data types...")
        create_sql = f"""
            CREATE TABLE {target_schema}.{table_name} (
                ID NUMBER PRIMARY KEY,
                TDATE DATE,
                CODE VARCHAR2(100),
                VAL NUMBER,
                CREATED_AT TIMESTAMP WITH TIME ZONE,
                LOAD_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        cursor.execute(create_sql)

        # 3. 데이터 이관 및 타입 변환 (CTAS 스타일 인서트)
        print(f"3. Migrating data with type conversion (this may take a minute)...")
        start_time = time.time()
        
        # TO_TIMESTAMP_TZ를 사용하여 '+00' 형식을 처리합니다.
        insert_sql = f"""
            INSERT /*+ APPEND */ INTO {target_schema}.{table_name} (ID, TDATE, CODE, VAL, CREATED_AT)
            SELECT 
                TO_NUMBER(ID),
                TO_DATE(TDATE, 'YYYY-MM-DD'),
                CODE,
                TO_NUMBER(VAL),
                TO_TIMESTAMP_TZ(CREATED_AT, 'YYYY-MM-DD HH24:MI:SS.FF6 TZH:TZM')
            FROM {target_schema}.{backup_table}
        """
        cursor.execute(insert_sql)
        conn.commit()
        
        elapsed = time.time() - start_time
        print(f"✅ Migration completed in {elapsed:.2f}s.")

        # 4. 결과 확인
        cursor.execute(f"SELECT COUNT(*) FROM {target_schema}.{table_name}")
        count = cursor.fetchone()[0]
        print(f"   - Total rows in new table: {count:,}")

        # 5. 샘플 조회로 타입 확인
        print("\n--- [New Table Sample Check] ---")
        cursor.execute(f"SELECT ID, TDATE, VAL, CREATED_AT FROM {target_schema}.{table_name} WHERE ROWNUM <= 3")
        for row in cursor:
            print(f"ID: {row[0]} (Type: {type(row[0])})")
            print(f"TDATE: {row[1]} (Type: {type(row[1])})")
            print(f"VAL: {row[2]} (Type: {type(row[2])})")
            print(f"CREATED_AT: {row[3]} (Type: {type(row[3])})")
            print("-" * 30)

        print(f"\n🚀 All set! The original data is still in {target_schema}.{backup_table} just in case.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    transform_table_types()
