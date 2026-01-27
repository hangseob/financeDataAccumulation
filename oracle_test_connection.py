import oracledb
import sys
import os

# Oracle Cloud DB 접속 정보
# 지갑(Wallet)을 사용하는 접속 방식으로 변경합니다.
wallet_path = r'C:\oracle\Wallet'
wallet_password = '0458seob.wallet'

config = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high" # 지갑 내 tnsnames.ora에 정의된 서비스 명 (보통 소문자_high)
}

def create_sample_table():
    conn = None
    try:
        # 1. DB 접속 (Wallet 사용)
        print(f"Connecting to Oracle Cloud DB as {config['user']} using Wallet...")
        
        # oracledb.init_oracle_client() 가 필요할 수 있으나, 
        # 최근 버전의 oracledb는 thin 모드에서도 지갑 연동을 지원합니다.
        # 지갑 경로가 올바른지 확인
        if not os.path.exists(wallet_path):
            print(f"❌ Error: Wallet path not found at {wallet_path}")
            return

        conn = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"],
            config_dir=wallet_path,
            wallet_location=wallet_path,
            wallet_password=wallet_password
        )
        cursor = conn.cursor()
        print("✅ Successfully connected to Oracle Cloud DB!")

        # 2. 기존 테이블 삭제 (존재할 경우)
        print("Dropping existing SAMPLE01 table if exists...")
        try:
            cursor.execute("DROP TABLE ADMIN.SAMPLE01")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code != 942: # ORA-00942: table or view does not exist
                raise

        # 3. 테이블 생성
        print("Creating table ADMIN.SAMPLE01...")
        cursor.execute("""
            CREATE TABLE ADMIN.SAMPLE01 (
                COL1 VARCHAR2(100),
                COL2 NUMBER,
                CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. 샘플 데이터 삽입
        print("Inserting sample data...")
        sample_data = [
            ("First Sample Data", 10.5),
            ("Second Sample Data", 2500),
            ("Oracle 23ai Wallet Test", 777.7),
            ("Financial Data Accumulation", 123456)
        ]
        
        cursor.executemany("INSERT INTO ADMIN.SAMPLE01 (COL1, COL2) VALUES (:1, :2)", sample_data)
        conn.commit()
        print(f"✅ Successfully inserted {len(sample_data)} rows.")

        # 5. 데이터 조회 확인
        print("\n--- [조회 결과 확인] ---")
        cursor.execute("SELECT COL1, COL2, TO_CHAR(CREATED_AT, 'YYYY-MM-DD HH24:MI:SS') FROM ADMIN.SAMPLE01")
        for row in cursor:
            print(f"COL1: {row[0]:<30} | COL2: {row[1]:>10} | Created: {row[2]}")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\n[HINT] 만약 서비스 명을 못 찾는다면 dsn 값을 'S9LBMRNW3ZCT3J80_high'로 바꿔보세요.")
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    # 터미널 출력 인코딩 설정
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    
    create_sample_table()
