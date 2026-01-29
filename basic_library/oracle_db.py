import oracledb
import pandas as pd
from datetime import datetime

# Oracle Cloud DB 접속 정보
CONFIG = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}

def get_connection():
    """Oracle DB 연결 객체 반환"""
    return oracledb.connect(
        user=CONFIG["user"],
        password=CONFIG["password"],
        dsn=CONFIG["dsn"],
        config_dir=CONFIG["wallet_path"],
        wallet_location=CONFIG["wallet_path"],
        wallet_password=CONFIG["wallet_password"]
    )

def get_available_curves():
    """사용 가능한 모든 CURVE_ID 리스트 조회"""
    conn = get_connection()
    try:
        query = "SELECT DISTINCT CURVE_ID FROM SPT.MMKT_RATE ORDER BY CURVE_ID"
        df = pd.read_sql(query, conn)
        return df['CURVE_ID'].tolist()
    finally:
        conn.close()

def get_curve_data(curve_id, tdate):
    """특정 곡선과 날짜의 데이터를 조회 (DataFrame 반환)"""
    conn = get_connection()
    try:
        query = f"""
            SELECT TDATE, CURVE_ID, RATE_ID, TENOR_NAME, MID, BID, ASK
            FROM SPT.MMKT_RATE
            WHERE CURVE_ID = :curve_id AND TDATE = :tdate
            ORDER BY TDATE, RATE_ID
        """
        return pd.read_sql(query, conn, params={"curve_id": curve_id, "tdate": tdate})
    finally:
        conn.close()

def find_nearest_date(curve_id, target_date):
    """지정한 날짜에 데이터가 없을 경우, 그 이후의 가장 가까운 날짜를 반환"""
    conn = get_connection()
    try:
        query = """
            SELECT MIN(TDATE) as NEAREST_DATE
            FROM SPT.MMKT_RATE
            WHERE CURVE_ID = :curve_id AND TDATE >= :target_date
        """
        cursor = conn.cursor()
        cursor.execute(query, curve_id=curve_id, target_date=target_date)
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def get_available_dates(curve_id):
    """특정 곡선에 대해 데이터가 존재하는 모든 날짜 리스트 조회"""
    conn = get_connection()
    try:
        query = """
            SELECT DISTINCT TDATE 
            FROM SPT.MMKT_RATE 
            WHERE CURVE_ID = :curve_id 
            ORDER BY TDATE
        """
        df = pd.read_sql(query, conn, params={"curve_id": curve_id})
        return df['TDATE'].tolist()
    finally:
        conn.close()

def get_all_curve_data(curve_id, start_date, end_date):
    """특정 기간 동안의 모든 곡선 데이터를 한 번에 가져옴"""
    conn = get_connection()
    try:
        query = f"""
            SELECT TDATE, CURVE_ID, RATE_ID, TENOR_NAME, MID, BID, ASK
            FROM SPT.MMKT_RATE
            WHERE CURVE_ID = :curve_id AND TDATE BETWEEN :start_date AND :end_date
            ORDER BY TDATE, RATE_ID
        """
        return pd.read_sql(query, conn, params={
            "curve_id": curve_id, 
            "start_date": start_date, 
            "end_date": end_date
        })
    finally:
        conn.close()

if __name__ == "__main__":
    # 테스트 코드
    curves = get_available_curves()
    print(f"Available curves: {curves[:5]}...")
    
    test_date = "20260123"
    if curves:
        data = get_curve_data(curves[0], test_date)
        print(f"Data for {curves[0]} on {test_date}:")
        print(data.head())
