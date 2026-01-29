import pandas as pd
from basic_library.oracle_client import OracleClient

def get_available_curves():
    """사용 가능한 CURVE_ID 리스트를 가져옵니다."""
    db = OracleClient()
    try:
        # SPT.MMKT_RATE에서 CURVE_ID 목록 조회
        sql = "SELECT DISTINCT CURVE_ID FROM SPT.MMKT_RATE ORDER BY CURVE_ID"
        rows = db.fetch_all(sql)
        return [row['CURVE_ID'] for row in rows]
    except Exception as e:
        print(f"Error fetching curves: {e}")
        return []
    finally:
        db.close()

def get_available_dates(curve_id):
    """특정 CURVE_ID에 대해 사용 가능한 TDATE 리스트를 가져옵니다."""
    db = OracleClient()
    try:
        sql = "SELECT DISTINCT TDATE FROM SPT.MMKT_RATE WHERE CURVE_ID = :1 ORDER BY TDATE"
        rows = db.fetch_all(sql, [curve_id])
        return [row['TDATE'] for row in rows]
    except Exception as e:
        print(f"Error fetching dates: {e}")
        return []
    finally:
        db.close()

def get_all_curve_data(curve_id, start_date, end_date):
    """특정 기간 동안의 모든 커브 데이터를 가져와 DataFrame으로 반환합니다."""
    db = OracleClient()
    try:
        sql = """
            SELECT TDATE, CURVE_ID, RATE_ID, TENOR_NAME, MID 
            FROM SPT.MMKT_RATE 
            WHERE CURVE_ID = :1 
              AND TDATE BETWEEN :2 AND :3
            ORDER BY TDATE, TENOR_NAME
        """
        rows = db.fetch_all(sql, [curve_id, start_date, end_date])
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Error fetching curve data: {e}")
        return pd.DataFrame()
    finally:
        db.close()
