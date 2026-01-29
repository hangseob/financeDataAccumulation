import sys
import os

# basic_library를 임포트하기 위해 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from basic_library import OracleClient

def test_fetch_mmkt_rate():
    # 터미널 출력 인코딩 설정 (한글 깨짐 방지)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    # 클라이언트 생성 (기본 설정 사용)
    # 만약 SPT 유저로 접속해야 한다면 파라미터를 수정해야 할 수 있습니다.
    # 현재는 기존 oracle_test_connection.py 설정을 따릅니다.
    db = OracleClient()
    
    try:
        print("🔍 Connecting to Oracle and fetching data from SPT.MMKT_RATE...")
        
        # SPT.MMKT_RATE 테이블에서 샘플 데이터 5건 조회
        # 테이블명이나 스키마명이 다를 경우를 대비해 예외 처리 포함
        sql = "SELECT * FROM SPT.MMKT_RATE FETCH FIRST 5 ROWS ONLY"
        
        rows = db.fetch_all(sql)
        
        if not rows:
            print("⚠️ No data found or table is empty.")
        else:
            print(f"✅ Successfully fetched {len(rows)} rows:")
            print("-" * 50)
            for i, row in enumerate(rows, 1):
                print(f"Row {i}: {row}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Error occurred during test: {e}")
        print("\n[HINT] 만약 SPT 스키마 접근 권한이 없다면 ADMIN.MMKT_RATE 등을 확인해 보세요.")
    finally:
        db.close()

if __name__ == "__main__":
    test_fetch_mmkt_rate()
