from supabase import create_client, Client
from supabase.client import ClientOptions

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def find_exact_table():
    # spt 스키마를 명시적으로 확인
    opts = ClientOptions(schema="spt")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    print("--- Searching in 'spt' schema ---")
    tables = ["mmkt_infomax_fields", "mmkt_infomax_fields_supabase"]
    for t in tables:
        try:
            # rpc가 없으므로 직접 조회를 통해 확인
            res = supabase.table(t).select("*").limit(1).execute()
            print(f"✅ Found table: {t}")
            if res.data:
                print(f"   Columns: {list(res.data[0].keys())}")
        except Exception as e:
            print(f"❌ Table {t} error: {e}")

if __name__ == "__main__":
    find_exact_table()
