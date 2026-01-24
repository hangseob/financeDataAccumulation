import pandas as pd
from supabase import create_client, Client
from supabase.client import ClientOptions
import sys
import io

# 인코딩 설정 (한글 깨짐 방지)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase 연결 정보
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def upload_excel_to_supabase():
    file_path = "C:/git_repository/infomax_supabase_bot/infomax_ficc_data_sample_02.xlsx"
    sheet_name = "FinalTable"
    
    print(f"📖 엑셀 파일 읽는 중: {file_path}")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # 1. 컬럼명 변경 (한글 -> 영어)
    # 엑셀 데이터의 실제 컬럼 순서에 따라 매핑 (날짜, 코드, 값)
    df.columns = ['date', 'code', 'value']
    
    # 2. 날짜 형식 변환 (20260124 -> 2026-01-24)
    def format_date(d):
        try:
            if pd.isna(d): return None
            s = str(int(float(d)))
            if len(s) == 8:
                return f"{s[:4]}-{s[4:6]}-{s[6:]}"
            return s
        except:
            return None
    
    df['date'] = df['date'].apply(format_date)
    
    # 3. 데이터 정제: 결측치(NaN, inf)를 모두 None으로 변환
    import numpy as np
    df = df.replace([np.inf, -np.inf], np.nan)
    # df = df.where(pd.notnull(df), None) # 이 방식보다 아래 방식이 더 확실함
    records = df.to_dict('records')
    
    # JSON 직렬화가 불가능한 nan 값을 None으로 최종 변환
    clean_records = []
    for row in records:
        clean_row = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        # 날짜나 코드가 없는 데이터는 제외
        if clean_row['date'] and clean_row['code']:
            clean_records.append(clean_row)
    
    print(f"✅ 데이터 정제 완료: 총 {len(clean_records)} 건 준비됨")

    # 4. Supabase 클라이언트 생성
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)

    # 5. 데이터 업로드
    table_name = "ficc_data_sample" 
    
    # 기존 데이터 삭제 (중복 방지)
    print(f"\n🗑️ 기존 데이터 삭제 중...")
    try:
        # 주주의: RLS가 꺼져있어야 delete가 작동함
        supabase.table(table_name).delete().neq("id", -1).execute()
    except:
        pass

    print(f"🚀 financial_data.{table_name} 테이블로 데이터 업로드 중...")
    
    try:
        batch_size = 200 # 속도를 위해 배치 사이즈 상향
        total_uploaded = 0
        for i in range(0, len(clean_records), batch_size):
            batch = clean_records[i:i + batch_size]
            supabase.table(table_name).insert(batch).execute()
            total_uploaded += len(batch)
            if total_uploaded % 1000 == 0 or total_uploaded == len(clean_records):
                print(f"   - {total_uploaded} / {len(clean_records)} 건 완료")
            
        print(f"\n🎉 총 {total_uploaded}개의 데이터가 성공적으로 업로드되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    upload_excel_to_supabase()
