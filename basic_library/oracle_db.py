import oracledb
import pandas as pd
import os
import sys

# Oracle Cloud DB 접속 정보
# 주의: 이 정보는 보안을 위해 환경변수나 별도 설정 파일로 관리하는 것이 좋습니다.
ORACLE_CONFIG = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "S9LBMRNW3ZCT3J80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}

def get_connection():
    """Oracle DB 연결 객체를 반환합니다."""
    # 리눅스 환경 등에서 경로가 다를 경우를 대비해 환경변수 확인
    # 1. 환경변수 확인 2. 현재 작업 디렉토리 내 wallet 폴더 확인 3. 기본 설정값 확인
    workspace_wallet = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wallet')
    wallet_path = os.environ.get("ORACLE_WALLET_PATH")
    
    if not wallet_path:
        if os.path.exists(workspace_wallet):
            wallet_path = workspace_wallet
        else:
            wallet_path = ORACLE_CONFIG["wallet_path"]
    
    try:
        conn = oracledb.connect(
            user=ORACLE_CONFIG["user"],
            password=ORACLE_CONFIG["password"],
            dsn=ORACLE_CONFIG["dsn"],
            config_dir=wallet_path,
            wallet_location=wallet_path,
            wallet_password=ORACLE_CONFIG["wallet_password"]
        )
        return conn
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return None

def get_available_curves():
    """사용 가능한 모든 CURVE_ID 리스트를 가져옵니다."""
    conn = get_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT CURVE_ID FROM SPT.MMKT_RATE ORDER BY CURVE_ID")
        curves = [row[0] for row in cursor.fetchall()]
        return curves
    finally:
        conn.close()

def get_available_dates(curve_id):
    """특정 CURVE_ID에 대해 데이터가 존재하는 모든 TDATE 리스트를 가져옵니다."""
    conn = get_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT TDATE FROM SPT.MMKT_RATE WHERE CURVE_ID = :1 ORDER BY TDATE", [curve_id])
        dates = [row[0] for row in cursor.fetchall()]
        return dates
    finally:
        conn.close()

def get_all_curve_data(curve_id, start_date, end_date):
    """특정 기간 동안의 특정 CURVE_ID 데이터를 DataFrame으로 가져옵니다."""
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        sql = """
            SELECT TDATE, TENOR_NAME, MID, BID, ASK, CCY, RATE_TYPE
            FROM SPT.MMKT_RATE
            WHERE CURVE_ID = :1 
              AND TDATE >= :2 
              AND TDATE <= :3
            ORDER BY TDATE, TENOR_NAME
        """
        cursor.execute(sql, [curve_id, start_date, end_date])
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        return df
    finally:
        conn.close()
