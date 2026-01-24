import xlwings as xw
import pandas as pd
import time
import os
import sys
from supabase import create_client, Client
from supabase.client import ClientOptions

# 터미널 한글 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# Supabase 설정
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def log(msg, end='\n'):
    print(msg, end=end, flush=True)

def upsert_to_supabase(supabase, table_name, data):
    """중복 방지(Upsert)를 사용하여 데이터를 업로드하는 함수"""
    if not data:
        return 0
    try:
        # on_conflict를 사용하여 중복 발생 시 업데이트 처리
        response = supabase.table(table_name).upsert(
            data, 
            on_conflict='date,code'
        ).execute()
        return len(data)
    except Exception as e:
        log(f" [DB 업로드 오류] {e}")
        return 0

def process_historical_infomax_to_supabase():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fields_path = os.path.join(current_dir, 'mmkt_infomax_fields.xlsx')
    infomax_xlam = r"C:\Infomax\bin\excel\infomaxexcel.xlam"
    
    # 장기 날짜 범위
    start_date = "20160101"
    end_date = "20260123"
    
    log(f"\n[시작] 인포맥스 장기 데이터 -> Supabase Upsert 업로드")
    log(f"- 기간: {start_date} ~ {end_date}")
    
    # 1. Supabase 클라이언트 (financial_data 스키마)
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    table_name = "data_from_infomax"

    # 2. 필드 정보 로드 (Sheet2, header=1 적용 - 진단 결과 반영)
    try:
        df_fields = pd.read_excel(fields_path, sheet_name='Sheet2', header=1)
        df_fields = df_fields.dropna(subset=['RATE_ID', 'DATA_TYPE', 'DATA_ID', 'FIELD_ID'])
        log(f"- 대상 종목 수: {len(df_fields)}개")
    except Exception as e:
        log(f"[에러] 필드 로드 실패: {e}")
        return

    # 3. 엑셀 실행
    app = None
    try:
        log("- 엑셀 및 인포맥스 로딩...")
        app = xw.App(visible=True, add_book=False)
        if os.path.exists(infomax_xlam):
            app.books.open(infomax_xlam)
            time.sleep(5)
            
        wb = app.books.add()
        scratch = wb.sheets[0]
        scratch.name = "Scratch"
        
        # 4. 순환 루프
        total_upserted = 0
        to_process = df_fields.to_dict('records')
        
        for i, row in enumerate(to_process):
            rate_id = row['RATE_ID']
            scale = row['SCALE_FACTOR'] if not pd.isna(row['SCALE_FACTOR']) else 1.0
            
            log(f"[{i+1}/{len(to_process)}] {rate_id} 수집 및 업로드 중", end='')
            
            # IMDH 함수 (데이터 개수 제한 5000으로 상향)
            formula = f'=IMDH("{row["DATA_TYPE"]}", "{row["DATA_ID"]}", "일자,{row["FIELD_ID"]}", "{start_date}", "{end_date}", 5000, "Headers=0,Orient=V,Per=D,Bizday=0")'
            scratch.range("A1").formula = formula
            
            # 수신 대기 (장기 데이터이므로 넉넉하게 대기)
            fetched_data = None
            for _ in range(20): 
                time.sleep(3)
                log(".", end='')
                val = scratch.range("A1:C5000").value
                if val and (val[0][0] or val[0][1]) and "#WAITING" not in str(val[0][0] or "").upper():
                    fetched_data = val
                    break
            
            if fetched_data:
                records = []
                for r in fetched_data:
                    if r is None or (r[1] is None and r[2] is None): continue
                    if r[1] is not None:
                        # 데이터 정제
                        d_str = str(int(r[1]))
                        formatted_date = f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}"
                        val_num = r[2] * scale if isinstance(r[2], (int, float)) else r[2]
                        
                        # 중복 방지를 위해 리스트에 담기
                        records.append({
                            "date": formatted_date,
                            "code": rate_id,
                            "value": val_num
                        })
                
                # DB Upsert 실행
                if records:
                    # 1000건씩 끊어서 업로드 (Supabase 제한 고려)
                    batch_size = 1000
                    for j in range(0, len(records), batch_size):
                        batch = records[j:j + batch_size]
                        count = upsert_to_supabase(supabase, table_name, batch)
                        total_upserted += count
                    
                    log(f" 완료! ({len(records)}건 처리)")
                else:
                    log(" 데이터 없음")
                
                # 영역 정리
                scratch.range("A1:C5000").clear_contents()
            else:
                log(" 실패 (타임아웃)")

        log(f"\n[종료] 장기 수집 완료. 총 {total_upserted}건이 처리되었습니다.")

    except Exception as e:
        log(f"\n[치명적 오류] {e}")
    finally:
        if app:
            try: app.quit()
            except: pass

if __name__ == "__main__":
    process_historical_infomax_to_supabase()
