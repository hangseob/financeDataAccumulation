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

target_table = "HANGSEOB.DATA_FROM_INFOMAX"

def query_random_rows():
    conn = None
    try:
        # DB 접속
        conn = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"],
            config_dir=config["wallet_path"],
            wallet_location=config["wallet_path"],
            wallet_password=config["wallet_password"]
        )
        cursor = conn.cursor()

        # 랜덤하게 10개 행 조회 SQL
        # Oracle에서는 DBMS_RANDOM.VALUE를 사용하여 정렬 후 상위 N개를 가져옵니다.
        sql = f"""
            SELECT * FROM (
                SELECT ID, TDATE, CODE, VAL, CREATED_AT 
                FROM {target_table} 
                ORDER BY DBMS_RANDOM.VALUE
            ) WHERE ROWNUM <= 10
        """
        
        print(f"Fetching 10 random rows from {target_table}...\n")
        cursor.execute(sql)
        
        # 결과 출력 (헤더 포함)
        headers = [col[0] for col in cursor.description]
        print(f"{headers[0]:<10} | {headers[1]:<12} | {headers[2]:<15} | {headers[3]:<10} | {headers[4]}")
        print("-" * 80)
        
        for row in cursor:
            print(f"{str(row[0]):<10} | {str(row[1]):<12} | {str(row[2]):<15} | {str(row[3]):<10} | {str(row[4])}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # 터미널 출력 인코딩 설정
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    
    query_random_rows()
