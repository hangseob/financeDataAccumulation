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

def recreate_mmkt_rate_table_clean():
    conn = None
    try:
        print(f"Connecting to Oracle Cloud DB as {config['user']}...")
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

        target_table = "SPT.MMKT_RATE"
        
        # 1. 테이블 재생성 (제약 조건 없이)
        print(f"1. Recreating table {target_table} with NULLABLE columns...")
        cursor.execute(f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {target_table}'; EXCEPTION WHEN OTHERS THEN NULL; END;")
        
        create_sql = f"""
        CREATE TABLE {target_table} (
            TDATE VARCHAR2(8) NOT NULL,
            CCY VARCHAR2(3),
            CCY2 VARCHAR2(3),
            RATE_TYPE VARCHAR2(12),
            CURVE_ID VARCHAR2(24) NOT NULL,
            RATE_ID VARCHAR2(24) NOT NULL,
            TENOR_NAME VARCHAR2(3),
            REL_TENOR_NAME VARCHAR2(3),
            MID NUMBER NOT NULL,
            BID NUMBER,
            ASK NUMBER
        )
        """
        cursor.execute(create_sql)
        print("   - Table created.")

        # 2. 데이터 다시 마이그레이션 (비울 컬럼은 NULL로)
        print("2. Migrating data again (CCY, CCY2, RATE_TYPE, REL_TENOR_NAME, BID, ASK as NULL)...")
        start_time = time.time()
        
        insert_sql = """
        INSERT INTO SPT.MMKT_RATE (
            TDATE, CCY, CCY2, RATE_TYPE, CURVE_ID, RATE_ID, 
            TENOR_NAME, REL_TENOR_NAME, MID, BID, ASK
        )
        SELECT 
            TO_CHAR(D.TDATE, 'YYYYMMDD'),
            NULL, -- CCY
            NULL, -- CCY2
            NULL, -- RATE_TYPE
            NVL(P.CURVE_ID, 'UNKNOWN'),
            D.CODE,
            NVL(P.TENOR_NAME, 'N'),
            NULL, -- REL_TENOR_NAME
            D.VAL,
            NULL, -- BID
            NULL  -- ASK
        FROM HANGSEOB.DATA_FROM_INFOMAX D
        LEFT JOIN HANGSEOB.RATE_ID_PARSED P ON D.CODE = P.RATE_ID
        """
        
        cursor.execute(insert_sql)
        row_count = cursor.rowcount
        conn.commit()
        
        elapsed = time.time() - start_time
        print(f"✅ Re-migration completed! {row_count:,} rows inserted in {elapsed:.2f}s.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    recreate_mmkt_rate_table_clean()
