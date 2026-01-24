from supabase import create_client, Client
from supabase.client import ClientOptions

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def get_status():
    try:
        opts = ClientOptions(schema="financial_data")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
        
        response = supabase.table('ficc_data_sample').select("*", count='exact').limit(1).execute()
        count = response.count if hasattr(response, 'count') else 0
        
        avg_row_size = 120 
        estimated_size_kb = (count * avg_row_size) / 1024
        
        print("=" * 60)
        print(f"Table Name : financial_data.ficc_data_sample")
        print("-" * 60)
        print(f"Total Rows : {count:,} records")
        print(f"Est. Size  : {estimated_size_kb:.2f} KB (approx {estimated_size_kb/1024:.2f} MB)")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    get_status()
