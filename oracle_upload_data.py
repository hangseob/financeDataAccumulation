import pandas as pd
import oracledb
import time
import sys

# Oracle Cloud DB 접속 정보
config = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}

csv_file_path = r'oracle_cloud_db_control/data_from_infomax_rows.csv'
target_table = "HANGSEOB.DATA_FROM_INFOMAX"
batch_size = 10000

def upload_data():
    conn = None
    try:
        # 1. CSV 로딩
        print(f"Reading CSV file: {csv_file_path}")
        start_time = time.time()
        # 모든 데이터를 문자열로 로딩하여 형식 에러 방지 (UTF-16 인코딩 적용)
        df = pd.read_csv(csv_file_path, dtype=str, encoding='utf-16')
        total_rows = len(df)
        print(f"Successfully loaded {total_rows:,} rows in {time.time() - start_time:.2f}s")

        # 2. DB 접속
        print("Connecting to Oracle Cloud DB...")
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

        # 3. 데이터 삽입 (Batch)
        # CSV 컬럼: id,date,code,value,created_at
        sql = f"INSERT INTO {target_table} (ID, TDATE, CODE, VAL, CREATED_AT) VALUES (:1, :2, :3, :4, :5)"
        
        # 튜플 리스트로 변환
        print("Preparing data for upload...")
        data_tuples = [tuple(x) for x in df.values]
        
        print(f"Starting upload to {target_table}...")
        for i in range(0, total_rows, batch_size):
            batch = data_tuples[i:i+batch_size]
            cursor.executemany(sql, batch)
            
            if (i + batch_size) % 100000 == 0 or (i + batch_size) >= total_rows:
                current = min(i + batch_size, total_rows)
                print(f"   Progress: {current:,} / {total_rows:,} ({current/total_rows*100:.1f}%)")
        
        conn.commit()
        print(f"✅ Successfully uploaded all {total_rows:,} rows!")
        
        # 4. 건수 확인
        cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
        db_count = cursor.fetchone()[0]
        print(f"Final count in DB: {db_count:,}")

    except Exception as e:
        print(f"❌ Error during upload: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    upload_data()
