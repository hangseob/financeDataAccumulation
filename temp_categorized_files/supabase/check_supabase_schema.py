from supabase import create_client, Client
from supabase.client import ClientOptions
import json

SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def check_supabase_table():
    # Try different schemas
    schemas = ["spt", "public", "financial_data"]
    tables_to_check = ["mmkt_infomax_fields", "mmkt_infomax_fields_supabase"]
    
    for schema in schemas:
        print(f"\n--- Schema: {schema} ---")
        try:
            opts = ClientOptions(schema=schema)
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
            
            for table in tables_to_check:
                try:
                    # Using a simple query to check existence
                    response = supabase.table(table).select("count", count="exact").limit(1).execute()
                    print(f"✅ Found '{table}' (Rows: {response.count})")
                except Exception:
                    print(f"❌ '{table}' not found")
        except Exception as e:
            print(f"Error connecting to schema {schema}: {e}")

if __name__ == "__main__":
    check_supabase_table()
