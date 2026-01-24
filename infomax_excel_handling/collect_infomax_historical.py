import xlwings as xw
import pandas as pd
import time
from datetime import datetime
import os
import sys

# 터미널 한글 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def log(msg, end='\n'):
    print(msg, end=end, flush=True)

def collect_historical_data():
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file_name = 'infomax_ficc_data_historical_long.xlsx'
    output_file = os.path.join(current_dir, output_file_name)
    fields_path = os.path.join(current_dir, 'mmkt_infomax_fields.xlsx')
    infomax_xlam = r"C:\Infomax\bin\excel\infomaxexcel.xlam"
    
    # 날짜 설정
    start_date = "20160101"
    end_date = "20260123"
    
    log(f"\n[시작] 인포맥스 장기 데이터 수집 ({start_date} ~ {end_date})")
    log(f"- 대상 파일: {output_file_name}")

    # 1. 필드 정보 로드 (Sheet2, header=2)
    try:
        df_raw = pd.read_excel(fields_path, sheet_name='Sheet2', header=2)
        # 컬럼 이름 정제
        df_raw.columns = [str(c).strip() for c in df_raw.columns]
        # 필수 컬럼 존재 여부 확인 후 필터링
        required_cols = ['RATE_ID', 'DATA_TYPE', 'DATA_ID', 'FIELD_ID']
        df_fields = df_raw.dropna(subset=required_cols)
        total_codes = len(df_fields)
        log(f"- 필드 정보 확인 완료 ({total_codes}개 종목)")
    except Exception as e:
        log(f"[에러] 필드 로드 실패: {e}")
        return

    # 2. 엑셀 및 인포맥스 실행
    app = None
    wb = None
    try:
        log("- 엑셀 앱 실행 중...")
        app = xw.App(visible=True, add_book=False)
        
        if os.path.exists(infomax_xlam):
            log(f"- 인포맥스 애드인 로드")
            app.books.open(infomax_xlam)
            time.sleep(5)
            
        wb = app.books.add()
        
        # 시트 설정
        final_sheet = wb.sheets.add("FinalTable")
        final_sheet.range("A1").value = ["날짜", "코드", "값"]
        final_row = 2

        scratch_sheet = wb.sheets.add("Scratch")
        
    except Exception as e:
        log(f"[에러] 엑셀 초기화 실패: {e}")
        if app: app.quit()
        return

    # 3. 데이터 수집 루프
    to_process_list = df_fields.to_dict('records')
    
    for i, row in enumerate(to_process_list):
        rate_id = row['RATE_ID']
        scale = row['SCALE_FACTOR'] if not pd.isna(row['SCALE_FACTOR']) else 1.0
        
        log(f"[{i+1}/{total_codes}] {rate_id} 요청 중", end='')
        
        # 장기 데이터이므로 개수 제한을 5000으로 늘림
        formula = f'=IMDH("{row["DATA_TYPE"]}", "{row["DATA_ID"]}", "일자,{row["FIELD_ID"]}", "{start_date}", "{end_date}", 5000, "Headers=0,Orient=V,Per=D,Bizday=0")'
        
        try:
            scratch_sheet.clear_contents()
            scratch_sheet.range("A1").formula = formula
            
            success = False
            # 데이터 수신 대기 (최대 60초로 상향)
            for _ in range(30):
                time.sleep(2)
                log(".", end='')
                
                data = scratch_sheet.range("A1:C5001").value
                if data and (data[0][0] or data[0][1]) and "#WAITING" not in str(data[0][0] or "").upper():
                    records = []
                    for r in data:
                        if r is None or (r[1] is None and r[2] is None): continue
                        if r[1] is not None:
                            val = r[2] * scale if isinstance(r[2], (int, float)) else r[2]
                            records.append([r[1], rate_id, val])
                    
                    if records:
                        final_sheet.range(f"A{final_row}").value = records
                        final_row += len(records)
                        log(f" 완료! ({len(records)}행)")
                        wb.save(output_file)
                    else:
                        log(" 데이터 없음")
                    success = True
                    break
            
            if not success:
                log(" 타임아웃/실패")
                
        except Exception as e:
            log(f" 오류 발생: {e}")

    log(f"\n[종료] 장기 데이터 수집 완료. (총 행: {final_row-1})")
    try:
        final_sheet.autofit()
        wb.save(output_file)
        log(f"- 파일 저장됨: {output_file}")
    except: pass

if __name__ == "__main__":
    collect_historical_data()
