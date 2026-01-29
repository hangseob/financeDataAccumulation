import pandas as pd
from basic_library.oracle_client import OracleClient

def get_available_curves():
    """사용 가능한 모든 CURVE_ID 리스트 조회"""
    db = OracleClient()
    try:
        query = "SELECT DISTINCT CURVE_ID FROM SPT.MMKT_RATE ORDER BY CURVE_ID"
        rows = db.fetch_all(query)
        return [row['CURVE_ID'] for row in rows]
    except Exception as e:
        print(f"Error fetching curves: {e}")
        return []
    finally:
        db.close()

def get_curve_data(curve_id, tdate):
    """특정 곡선과 날짜의 데이터를 조회 (DataFrame 반환)"""
    db = OracleClient()
    try:
        # OracleClient doesn't directly support returning DataFrame, so we use its connection if needed or just convert results
        # However, OracleClient.fetch_all returns list of dicts which pd.DataFrame can consume.
        query = """
            SELECT TDATE, CURVE_ID, RATE_ID, TENOR_NAME, MID, BID, ASK
            FROM SPT.MMKT_RATE
            WHERE CURVE_ID = :curve_id AND TDATE = :tdate
            ORDER BY TDATE, RATE_ID
        """
        rows = db.fetch_all(query, {"curve_id": curve_id, "tdate": tdate})
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Error fetching curve data: {e}")
        return pd.DataFrame()
    finally:
        db.close()

def find_nearest_date(curve_id, target_date):
    """지정한 날짜에 데이터가 없을 경우, 그 이후의 가장 가까운 날짜를 반환"""
    db = OracleClient()
    try:
        query = """
            SELECT MIN(TDATE) as NEAREST_DATE
            FROM SPT.MMKT_RATE
            WHERE CURVE_ID = :curve_id AND TDATE >= :target_date
        """
        rows = db.fetch_all(query, {"curve_id": curve_id, "target_date": target_date})
        return rows[0]['NEAREST_DATE'] if rows and rows[0]['NEAREST_DATE'] else None
    except Exception as e:
        print(f"Error finding nearest date: {e}")
        return None
    finally:
        db.close()

def get_available_dates(curve_id):
    """특정 곡선에 대해 데이터가 존재하는 모든 날짜 리스트 조회"""
    db = OracleClient()
    try:
        query = """
            SELECT DISTINCT TDATE 
            FROM SPT.MMKT_RATE 
            WHERE CURVE_ID = :curve_id 
            ORDER BY TDATE
        """
        rows = db.fetch_all(query, {"curve_id": curve_id})
        return [row['TDATE'] for row in rows]
    except Exception as e:
        print(f"Error fetching dates: {e}")
        return []
    finally:
        db.close()

def get_all_curve_data(curve_id, start_date, end_date):
    """특정 기간 동안의 모든 곡선 데이터를 한 번에 가져옴"""
    db = OracleClient()
    try:
        query = """
            SELECT TDATE, CURVE_ID, RATE_ID, TENOR_NAME, MID, BID, ASK
            FROM SPT.MMKT_RATE
            WHERE CURVE_ID = :curve_id AND TDATE BETWEEN :start_date AND :end_date
            ORDER BY TDATE, RATE_ID
        """
        rows = db.fetch_all(query, {
            "curve_id": curve_id, 
            "start_date": start_date, 
            "end_date": end_date
        })
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Error fetching all curve data: {e}")
        return pd.DataFrame()
    finally:
        db.close()

if __name__ == "__main__":
    # 테스트 코드
    curves = get_available_curves()
    if curves:
        print(f"Available curves: {curves[:5]}...")
        test_date = "20260123"
        data = get_curve_data(curves[0], test_date)
        print(f"Data for {curves[0]} on {test_date}:")
        print(data.head())
