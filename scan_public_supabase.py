from supabase import create_client, Client
from supabase.client import ClientOptions

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def scan_public_schema():
    opts = ClientOptions(schema="public")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    print("--- Searching in 'public' schema ---")
    # public 스키마에 있을 가능성이 높은 이름들 확인
    tables = ["mmkt_infomax_fields", "mmkt_infomax_fields_supabase", "data_from_infomax"]
    for t in tables:
        try:
            res = supabase.table(t).select("*").limit(1).execute()
            print(f"✅ Found in public: {t}")
            if res.data:
                print(f"   Columns: {list(res.data[0].keys())}")
        except Exception as e:
            # relation does not exist와 permission denied 구분
            err_msg = str(e)
            if "relation" in err_msg and "does not exist" in err_msg:
                print(f"❌ '{t}' does not exist in public.")
            else:
                print(f"⚠️ '{t}' exists but error: {err_msg}")

if __name__ == "__main__":
    scan_public_schema()
