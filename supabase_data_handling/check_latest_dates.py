from supabase import create_client, Client
from supabase.client import ClientOptions
import pandas as pd
import sys
import io

# 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def check_latest_data():
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    symbols = ['KRWQ3L1Y', 'KRWQ3L10Y']
    
    print("🔍 [data_from_infomax] 최신 데이터 확인 중...")
    
    for symbol in symbols:
        response = supabase.table('data_from_infomax') \
            .select("date, value") \
            .eq("code", symbol) \
            .order("date", desc=True) \
            .limit(5) \
            .execute()
        
        if response.data:
            print(f"\n✅ {symbol} 최신 5건:")
            for row in response.data:
                print(f"  - {row['date']}: {row['value']}")
        else:
            print(f"❌ {symbol} 데이터가 없습니다.")

if __name__ == "__main__":
    check_latest_data()
