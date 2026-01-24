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

def upload_to_supabase(supabase, table_name, data):
    """Supabase에 데이터를 업로드하는 함수"""
    if not data:
        return 0
    try:
        response = supabase.table(table_name).insert(data).execute()
        return len(data)
    except Exception as e:
        log(f" [DB 업로드 오류] {e}")
        return 0

def process_infomax_to_supabase():
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fields_path = os.path.join(current_dir, 'mmkt_infomax_fields.xlsx')
    infomax_xlam = r"C:\Infomax\bin\excel\infomaxexcel.xlam"
    
    # 날짜 범위 (2026.01.01 ~ 2026.01.23)
    start_date = "20260101"
    end_date = "20260123"
    
    log(f"\n[시작] 인포맥스 -> Supabase 순환 업로드 테스트")
    
    # 1. Supabase 클라이언트 초기화
    opts = ClientOptions(schema="financial_data")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    table_name = "ficc_data_sample"

    # 2. 필드 정보 로드 (Sheet2, header=2)
    try:
        df_fields = pd.read_excel(fields_path, sheet_name='Sheet2', header=2) 
        df_fields = df_fields.dropna(subset=['RATE_ID', 'DATA_TYPE', 'DATA_ID', 'FIELD_ID'])
        log(f"- 대상 종목 수: {len(df_fields)}개")
    except Exception as e:
        log(f"[에러] 필드 로드 실패: {e}")
        return

    # 3. 엑셀 실행
    app = None
    try:
        log("- 엑셀 및 인포맥스 연결 중...")
        app = xw.App(visible=True, add_book=False)
        if os.path.exists(infomax_xlam):
            app.books.open(infomax_xlam)
            time.sleep(5)
            
        wb = app.books.add()
        scratch = wb.sheets[0]
        scratch.name = "Scratch"
        
        # 4. 순환 루프 실행
        total_uploaded_all = 0
        to_process = df_fields.to_dict('records')
        
        for i, row in enumerate(to_process):
            rate_id = row['RATE_ID']
            scale = row['SCALE_FACTOR'] if not pd.isna(row['SCALE_FACTOR']) else 1.0
            
            log(f"[{i+1}/{len(to_process)}] {rate_id} 처리 시작", end='')
            
            # 인포맥스 함수 입력
            formula = f'=IMDH("{row["DATA_TYPE"]}", "{row["DATA_ID"]}", "일자,{row["FIELD_ID"]}", "{start_date}", "{end_date}", 100, "Headers=0,Orient=V,Per=D,Bizday=0")'
            scratch.range("A1").formula = formula
            
            # 데이터 로딩 대기
            fetched_data = None
            for _ in range(15):
                time.sleep(2)
                log(".", end='')
                val = scratch.range("A1:C100").value
                if val and (val[0][0] or val[0][1]) and "#WAITING" not in str(val[0][0] or "").upper():
                    fetched_data = val
                    break
            
            if fetched_data:
                # 데이터 포맷 변환 (Supabase 맞춤)
                records_to_upload = []
                for r in fetched_data:
                    if r is None or (r[1] is None and r[2] is None): continue
                    if r[1] is not None:
                        # 날짜 형식 변환 (YYYYMMDD -> YYYY-MM-DD)
                        d_str = str(int(r[1]))
                        formatted_date = f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}"
                        val_num = r[2] * scale if isinstance(r[2], (int, float)) else r[2]
                        
                        records_to_upload.append({
                            "date": formatted_date,
                            "code": rate_id,
                            "value": val_num
                        })
                
                # DB 업로드
                uploaded_count = upload_to_supabase(supabase, table_name, records_to_upload)
                total_uploaded_all += uploaded_count
                log(f" 완료! ({uploaded_count}건 업로드)")
                
                # 데이터 지우기 (엑셀 영역 비움)
                scratch.range("A1:C100").clear_contents()
            else:
                log(" 실패 (타임아웃)")

        log(f"\n[종료] 전체 작업 완료. 총 {total_uploaded_all}건이 Supabase에 저장되었습니다.")

    except Exception as e:
        log(f"\n[치명적 오류] {e}")
    finally:
        if app:
            try: app.quit()
            except: pass

if __name__ == "__main__":
    process_infomax_to_supabase()
