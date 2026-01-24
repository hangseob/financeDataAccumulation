from supabase import create_client, Client
from supabase.client import ClientOptions
import sys
import io

# 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def get_distinct_codes_efficiently():
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    print("🔍 'KRWQ3L%' 패턴 고유 코드 조회 중 (타임아웃 우회)...")
    
    unique_codes = set()
    
    # 전체 데이터를 가져오는 대신, 개별 종목을 하나씩 확인하거나
    # 데이터가 많은 경우 rpc가 없으므로 limit/offset을 사용하여 조금씩 가져옵니다.
    # 하지만 종목 코드는 전체 행 수에 비해 적을 것이므로, 
    # select 시 중복을 줄일 수 있는 방법이 제한적이라 fetch_all 방식을 사용합니다.
    
    try:
        page_size = 1000
        current_page = 0
        
        while True:
            start = current_page * page_size
            end = start + page_size - 1
            
            # value는 빼고 code만 가져와서 부하를 줄임
            response = supabase.table('data_from_infomax') \
                .select("code") \
                .like("code", "KRWQ3L%") \
                .range(start, end) \
                .execute()
            
            data = response.data
            if not data:
                break
                
            for row in data:
                unique_codes.add(row['code'])
            
            if len(data) < page_size:
                break
                
            current_page += 1
            # 너무 오래 걸릴 수 있으므로 중간 보고
            if current_page % 10 == 0:
                print(f"  ... {current_page * page_size}행 처리 중 (현재 발견된 고유 코드: {len(unique_codes)}개)")

        print(f"\n✅ 완료! 'KRWQ3L%' 패턴 고유 코드 개수: {len(unique_codes)}")
        print(f"📋 고유 코드 목록: {sorted(list(unique_codes))}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    get_distinct_codes_efficiently()
