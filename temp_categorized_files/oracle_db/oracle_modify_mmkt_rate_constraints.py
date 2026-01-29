import oracledb
import sys

# Oracle Cloud DB 접속 정보
config = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}

def modify_mmkt_rate_table():
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
        
        # 1. NOT NULL 제약 조건 해제 (MODIFY)를 먼저 수행해야 NULL로 업데이트 가능합니다.
        print("1. Modifying column constraints to NULLABLE...")
        modify_sql = f"""
            ALTER TABLE {target_table} MODIFY (
                CCY NULL,
                CCY2 NULL,
                RATE_TYPE NULL,
                REL_TENOR_NAME NULL
            )
        """
        cursor.execute(modify_sql)
        print("   - Column constraints modified.")

        # 2. 데이터 비우기 (NULL로 업데이트)
        print(f"2. Updating columns CCY, CCY2, RATE_TYPE, REL_TENOR_NAME to NULL in {target_table}...")
        update_sql = f"""
            UPDATE {target_table} 
            SET CCY = NULL, CCY2 = NULL, RATE_TYPE = NULL, REL_TENOR_NAME = NULL
        """
        cursor.execute(update_sql)
        print(f"   - Updated {cursor.rowcount:,} rows.")

        conn.commit()
        print("\n✅ All changes applied successfully.")

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
    modify_mmkt_rate_table()
