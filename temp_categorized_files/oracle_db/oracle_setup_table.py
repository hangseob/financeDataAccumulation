import oracledb
import sys
import os

# Oracle Cloud DB 접속 정보
config = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}

target_schema = "HANGSEOB"
target_table = "DATA_FROM_INFOMAX"
full_table_name = f"{target_schema}.{target_table}"

def setup_table():
    conn = None
    try:
        # 1. DB 접속
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
        print("✅ Successfully connected!")

        # 2. HANGSEOB 스키마 존재 여부 확인 및 생성 (필요 시)
        print(f"Checking if schema {target_schema} exists...")
        cursor.execute(f"SELECT COUNT(*) FROM all_users WHERE username = '{target_schema}'")
        if cursor.fetchone()[0] == 0:
            print(f"   - Schema {target_schema} does not exist. Creating it...")
            # 비밀번호는 임시로 설정 (보안 정책 준수: 대문자, 소문자, 숫자 포함, 사용자명 제외)
            cursor.execute(f"CREATE USER {target_schema} IDENTIFIED BY 'Hangseob#Data123'")
            cursor.execute(f"GRANT CONNECT, RESOURCE TO {target_schema}")
            cursor.execute(f"ALTER USER {target_schema} QUOTA UNLIMITED ON DATA")
            print(f"   - Schema {target_schema} created successfully.")
        else:
            print(f"   - Schema {target_schema} exists.")

        # 3. 기존 테이블 삭제
        print(f"Checking if table {full_table_name} exists...")
        try:
            cursor.execute(f"DROP TABLE {full_table_name}")
            print(f"   - Existing table {full_table_name} dropped.")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code == 942: # ORA-00942: table or view does not exist
                print(f"   - Table {full_table_name} does not exist. Skipping drop.")
            else:
                raise

        # 4. 테이블 생성
        # CSV 헤더: id,date,code,value,created_at
        # 안전을 위해 모두 VARCHAR2로 생성
        print(f"Creating table {full_table_name}...")
        create_sql = f"""
            CREATE TABLE {full_table_name} (
                ID VARCHAR2(100),
                TDATE VARCHAR2(100),
                CODE VARCHAR2(100),
                VAL VARCHAR2(100),
                CREATED_AT VARCHAR2(100)
            )
        """
        cursor.execute(create_sql)
        print(f"✅ Table {full_table_name} created successfully.")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    setup_table()
