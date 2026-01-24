from supabase import create_client, Client
from supabase.client import ClientOptions
import sys
import io

# 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def count_daily_codes(target_date="2026-01-23"):
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    print(f"🔍 {target_date} 기준 고유 코드 개수 조회 중...")
    
    unique_codes = set()
    page_size = 1000
    current_page = 0
    
    try:
        while True:
            start = current_page * page_size
            end = start + page_size - 1
            
            # 특정 날짜 데이터만 필터링하여 code 목록 가져오기
            response = supabase.table('data_from_infomax') \
                .select("code") \
                .eq("date", target_date) \
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

        print(f"\n✅ 완료! {target_date} 기준 고유 코드 개수: {len(unique_codes)}")
        if unique_codes:
            print(f"📋 코드 목록: {sorted(list(unique_codes))}")
        else:
            print(f"⚠️ {target_date}에 해당하는 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    count_daily_codes("2026-01-23")
