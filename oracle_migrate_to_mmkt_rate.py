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

def migrate_to_mmkt_rate():
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

        # 1. 기존 데이터 삭제 (중복 방지)
        print("SPT.MMKT_RATE 테이블 초기화 중...")
        cursor.execute("TRUNCATE TABLE SPT.MMKT_RATE")

        # 2. Migration SQL 작성
        # - TDATE: DATE 형식을 'YYYYMMDD' 문자열로 변환 (TO_CHAR)
        # - RATE_ID: CODE 컬럼 그대로 사용
        # - TENOR_NAME, CURVE_ID: HANGSEOB.RATE_ID_PARSED 테이블과 JOIN하여 가져옴
        # - MID: VAL 컬럼 사용 (이미 NUMBER 타입으로 변환됨)
        # - CCY, CCY2, RATE_TYPE, BID, ASK 등은 이미지에서 NOT NULL이었으나 
        #   현재 소스 데이터(DATA_FROM_INFOMAX)에는 없으므로 임시 값(N/A 또는 0)으로 채움
        
        insert_sql = """
        INSERT INTO SPT.MMKT_RATE (
            TDATE, CCY, CCY2, RATE_TYPE, CURVE_ID, RATE_ID, 
            TENOR_NAME, REL_TENOR_NAME, MID, BID, ASK
        )
        SELECT 
            TO_CHAR(D.TDATE, 'YYYYMMDD'),  -- DATE -> TDATE (YYYYMMDD)
            'UNK',                         -- CCY (임시)
            'UNK',                         -- CCY2 (임시)
            'FIXED',                       -- RATE_TYPE (임시)
            NVL(P.CURVE_ID, 'UNKNOWN'),    -- CURVE_ID (PARSED 참조)
            D.CODE,                        -- RATE_ID (CODE)
            NVL(P.TENOR_NAME, 'N'),        -- TENOR_NAME (PARSED 참조)
            'N',                           -- REL_TENOR_NAME
            D.VAL,                         -- MID (VALUE)
            D.VAL,                         -- BID (MID와 동일하게 임시)
            D.VAL                          -- ASK (MID와 동일하게 임시)
        FROM HANGSEOB.DATA_FROM_INFOMAX D
        LEFT JOIN HANGSEOB.RATE_ID_PARSED P ON D.CODE = P.RATE_ID
        """

        print("데이터 마이그레이션 시작 (JOIN 연산 포함)...")
        start_time = time.time()
        
        cursor.execute(insert_sql)
        row_count = cursor.rowcount
        conn.commit()
        
        elapsed = time.time() - start_time
        print(f"✅ 마이그레이션 완료! 총 {row_count:,} 행 이관됨 (소요시간: {elapsed:.2f}초)")

        # 샘플 확인
        print("\n--- [이관 데이터 샘플 확인] ---")
        cursor.execute("SELECT * FROM SPT.MMKT_RATE WHERE ROWNUM <= 5")
        for row in cursor:
            print(row)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    migrate_to_mmkt_rate()
