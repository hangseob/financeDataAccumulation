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

md_file_path = 'mmkt_infomax_fields_parsed.md'
target_schema = "HANGSEOB"
target_table = "RATE_ID_PARSED"
full_table_name = f"{target_schema}.{target_table}"

def upload_md_to_oracle_distinct():
    conn = None
    try:
        # 1. 마크다운 파일 파싱 (중복 제거)
        print(f"Reading markdown file: {md_file_path}")
        with open(md_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        seen_rate_ids = set()
        data_rows = []
        for line in lines:
            if line.strip().startswith('|') and 'RATE_ID' not in line and '---' not in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) == 3:
                    rate_id = parts[0]
                    if rate_id not in seen_rate_ids:
                        data_rows.append(tuple(parts))
                        seen_rate_ids.add(rate_id)
        
        print(f"Parsed {len(data_rows)} unique rows from markdown.")

        # 2. DB 접속
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

        # 3. 테이블 초기화
        cursor.execute(f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {full_table_name}'; EXCEPTION WHEN OTHERS THEN NULL; END;")
        cursor.execute(f"""
            CREATE TABLE {full_table_name} (
                RATE_ID VARCHAR2(100) PRIMARY KEY,
                TENOR_NAME VARCHAR2(50),
                CURVE_ID VARCHAR2(100),
                LOAD_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. 데이터 삽입
        sql = f"INSERT INTO {full_table_name} (RATE_ID, TENOR_NAME, CURVE_ID) VALUES (:1, :2, :3)"
        cursor.executemany(sql, data_rows)
        conn.commit()
        
        print(f"✅ Successfully uploaded {len(data_rows)} unique rows to {full_table_name}!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    upload_md_to_oracle_distinct()
