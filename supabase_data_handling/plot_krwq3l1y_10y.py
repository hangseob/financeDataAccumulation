import matplotlib.pyplot as plt
import pandas as pd
from supabase import create_client, Client
from supabase.client import ClientOptions
import sys
import io
import os

# Set encoding for Windows terminal
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase Connection Info
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def plot_historical_graph(symbol='KRWQ3L1Y'):
    print(f"📊 Fetching data for {symbol} from Supabase...")
    
    # 1. Initialize Supabase Client with financial_data schema
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    try:
        # 2. Query data for the specific symbol, ordered by date
        response = supabase.table('data_from_infomax') \
            .select("date, value") \
            .eq("code", symbol) \
            .order("date", desc=False) \
            .execute()
        
        data = response.data
        if not data:
            print(f"❌ No data found for symbol: {symbol}")
            return

        # 3. Convert to Pandas DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'])
        
        print(f"✅ Loaded {len(df)} records. Plotting graph...")

        # 4. Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], df['value'], linestyle='-', color='#1f77b4', linewidth=1.5)
        
        # Formatting
        plt.title(f'{symbol} - 10Y Historical Trend', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        
        # Dynamic Y-axis padding
        y_min, y_max = df['value'].min(), df['value'].max()
        padding = (y_max - y_min) * 0.1
        plt.ylim(y_min - padding, y_max + padding)

        plt.tight_layout()
        
        # Save the plot
        output_path = os.path.join(os.path.dirname(__file__), f"{symbol}_10y_graph.png")
        plt.savefig(output_path)
        print(f"🎉 Graph saved successfully to: {output_path}")
        
        # Show the plot
        plt.show()

    except Exception as e:
        print(f"❌ Error during data processing or plotting: {e}")

if __name__ == "__main__":
    plot_historical_graph('KRWQ3L1Y')
