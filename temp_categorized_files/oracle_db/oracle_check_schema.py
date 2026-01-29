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

target_schema = "HANGSEOB"
target_table = "DATA_FROM_INFOMAX"

def check_table_schema():
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

        # 테이블 스키마 조회 SQL (데이터 타입, 길이, 정밀도 등)
        sql = """
            SELECT 
                column_name, 
                data_type, 
                data_length, 
                data_precision, 
                data_scale, 
                nullable
            FROM all_tab_columns
            WHERE owner = :owner AND table_name = :table_name
            ORDER BY column_id
        """
        
        print(f"--- Schema for {target_schema}.{target_table} ---\n")
        cursor.execute(sql, owner=target_schema, table_name=target_table)
        
        # 헤더 출력
        print(f"{'COLUMN_NAME':<20} | {'TYPE':<12} | {'LEN':<6} | {'PREC':<6} | {'SCALE':<6} | {'NULL?'}")
        print("-" * 75)
        
        columns = cursor.fetchall()
        if not columns:
            print("Table not found or no access permission.")
        else:
            for col in columns:
                name, dtype, length, prec, scale, nulls = col
                prec = prec if prec is not None else ""
                scale = scale if scale is not None else ""
                print(f"{name:<20} | {dtype:<12} | {length:<6} | {str(prec):<6} | {str(scale):<6} | {nulls}")

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
    
    check_table_schema()
