import matplotlib.pyplot as plt
import pandas as pd
from supabase import create_client, Client
from supabase.client import ClientOptions
import sys
import io
import os
from datetime import datetime

# Set encoding for Windows terminal
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase Connection Info
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def fetch_all_data(supabase, symbol, start_date):
    """서버의 1000개 제한을 우회하여 모든 데이터를 페이지네이션으로 가져옵니다."""
    all_rows = []
    page_size = 1000
    current_page = 0
    
    while True:
        start = current_page * page_size
        end = start + page_size - 1
        
        response = supabase.table('data_from_infomax') \
            .select("date, value") \
            .eq("code", symbol) \
            .gte("date", start_date) \
            .order("date", desc=False) \
            .range(start, end) \
            .execute()
        
        data = response.data
        if not data:
            break
            
        all_rows.extend(data)
        
        # 가져온 데이터가 page_size보다 작으면 마지막 페이지임
        if len(data) < page_size:
            break
            
        current_page += 1
        
    return all_rows

def plot_comparison():
    symbols = ['KRWQ3L1Y', 'KRWQ3L10Y']
    start_date_str = "2016-01-01"
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📊 Fetching comparison data from {start_date_str} to {today_str} (Using Pagination)...")
    
    # 1. Initialize Supabase Client
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    try:
        # 2. Fetch data for both symbols using pagination
        all_data = {}
        for symbol in symbols:
            data = fetch_all_data(supabase, symbol, start_date_str)
            
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = pd.to_numeric(df['value'])
                all_data[symbol] = df
                
                # Print the latest date and total count
                latest_date = df['date'].max().strftime('%Y-%m-%d')
                print(f"✅ Total {len(df)} records for {symbol} (Latest: {latest_date})")
            else:
                print(f"⚠️ No data found for {symbol}")

        if len(all_data) < 2:
            print("❌ Need data for both symbols to plot comparison.")
            return

        # 3. Create the plot
        print("\n📈 Drawing chart...")
        plt.figure(figsize=(15, 8))
        
        # Plot 1Y (Blue)
        plt.plot(all_data['KRWQ3L1Y']['date'], all_data['KRWQ3L1Y']['value'], 
                 label='1Y (KRWQ3L1Y)', color='#1f77b4', linewidth=1.2, alpha=0.7)
        
        # Plot 10Y (Red)
        plt.plot(all_data['KRWQ3L10Y']['date'], all_data['KRWQ3L10Y']['value'], 
                 label='10Y (KRWQ3L10Y)', color='#d62728', linewidth=1.5)
        
        # 4. Set Fixed Time Axis Limits
        plt.xlim(pd.Timestamp(start_date_str), pd.Timestamp(today_str))
        
        # Formatting
        plt.title(f'Comparison: 1Y vs 10Y ({start_date_str} ~ {today_str})', fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(fontsize=12, loc='upper left')
        plt.xticks(rotation=45)

        # Optimization
        plt.tight_layout()
        
        # Save the plot
        output_path = os.path.join(os.path.dirname(__file__), "comparison_all_data.png")
        plt.savefig(output_path)
        print(f"🎉 Complete graph saved to: {output_path}")
        
        # Show the plot
        plt.show()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    plot_comparison()
