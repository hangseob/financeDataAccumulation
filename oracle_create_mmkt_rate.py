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

def create_mmkt_rate_table():
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
        print(f"Creating table {target_table}...")

        # 기존 테이블 삭제 (존재하는 경우)
        cursor.execute(f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {target_table}'; EXCEPTION WHEN OTHERS THEN NULL; END;")

        # 이미지 스키마를 그대로 반영한 CREATE TABLE 문
        create_sql = f"""
        CREATE TABLE {target_table} (
            TDATE VARCHAR2(8) NOT NULL,
            CCY VARCHAR2(3) NOT NULL,
            CCY2 VARCHAR2(3) NOT NULL,
            RATE_TYPE VARCHAR2(12) NOT NULL,
            CURVE_ID VARCHAR2(24) NOT NULL,
            RATE_ID VARCHAR2(24) NOT NULL,
            TENOR_NAME VARCHAR2(3),
            REL_TENOR_NAME VARCHAR2(3),
            MID NUMBER NOT NULL,
            BID NUMBER NOT NULL,
            ASK NUMBER NOT NULL
        )
        """
        cursor.execute(create_sql)
        print(f"✅ Table {target_table} created successfully.")

        conn.commit()

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
    create_mmkt_rate_table()
