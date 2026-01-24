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

def resume_infomax_extraction():
    # 현재 스크립트가 위치한 디렉토리를 기준으로 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    existing_file_name = 'infomax_ficc_data_sample_04.xlsx'
    existing_file = os.path.join(current_dir, existing_file_name)
    fields_path = os.path.join(current_dir, 'mmkt_infomax_fields.xlsx')
    infomax_xlam = r"C:\Infomax\bin\excel\infomaxexcel.xlam"
    
    log(f"\n[시작] 인포맥스 데이터 수집 재개 (대상: {existing_file_name})")
    log(f"- 작업 디렉토리: {current_dir}")
    
    # 1. 기존 작업 내용 확인 (pandas)
    processed_codes = set()
    if os.path.exists(existing_file):
        try:
            df_existing = pd.read_excel(existing_file, sheet_name='FinalTable', engine='openpyxl')
            if not df_existing.empty:
                processed_codes = set(df_existing.iloc[:, 1].dropna().unique().tolist())
            log(f"- 기존 파일 확인: {len(processed_codes)}개 종목 완료")
        except Exception as e:
            log(f"- 파일 확인 중 경고: {e}")

    # 2. 필드 정보 로드 및 필터링
    try:
        # mmkt_infomax_fields.xlsx는 Sheet2의 2번째 줄(header=1)에 정보가 있음
        df_fields = pd.read_excel(fields_path, sheet_name='Sheet2', header=1) 
        df_fields = df_fields.dropna(subset=['RATE_ID', 'DATA_TYPE', 'DATA_ID', 'FIELD_ID'])
        df_to_process = df_fields[~df_fields['RATE_ID'].isin(processed_codes)]
        log(f"- 상태: 전체 {len(df_fields)}개 중 {len(processed_codes)}개 완료, 남은 {len(df_to_process)}개 시작")
    except Exception as e:
        log(f"[에러] 필드 로드 실패: {e}")
        return

    if len(df_to_process) == 0:
        log("[완료] 모든 종목이 처리되었습니다.")
        return

    # 3. 엑셀 및 인포맥스 실행 (테스트 성공 로직 반영)
    app = None
    wb = None
    try:
        log("- 엑셀 앱 실행 중 (새 인스턴스)...")
        app = xw.App(visible=True, add_book=False)
        
        if os.path.exists(infomax_xlam):
            log(f"- 인포맥스 애드인 로드: {infomax_xlam}")
            app.books.open(infomax_xlam)
            time.sleep(5) # 초기화 대기
            
        if os.path.exists(existing_file):
            log(f"- 기존 파일 열기: {existing_file_name}")
            wb = app.books.open(existing_file)
        else:
            log("- 새 파일 생성...")
            wb = app.books.add()
            wb.save(existing_file)

        # 시트 설정
        if "FinalTable" not in [s.name for s in wb.sheets]:
            final_sheet = wb.sheets.add("FinalTable")
            final_sheet.range("A1").value = ["날짜", "코드", "값"]
            final_row = 2
        else:
            final_sheet = wb.sheets["FinalTable"]
            last_cell = final_sheet.range("A" + str(final_sheet.cells.last_cell.row)).end('up')
            final_row = last_cell.row + 1 if last_cell.value != "날짜" else 2

        if "Scratch" not in [s.name for s in wb.sheets]:
            scratch_sheet = wb.sheets.add("Scratch")
        else:
            scratch_sheet = wb.sheets["Scratch"]
            
        log(f"- 준비 완료. {final_row}행부터 기록 시작.")

    except Exception as e:
        log(f"[에러] 엑셀 초기화 실패: {e}")
        if app: app.quit()
        return

    # 4. 데이터 수집 루프
    start_date = "20260101"
    end_date = datetime.now().strftime("%Y%m%d")
    to_process_list = df_to_process.to_dict('records')
    total = len(to_process_list)
    
    log(f"\n[데이터 수집 진행]")
    for i, row in enumerate(to_process_list):
        rate_id = row['RATE_ID']
        scale = row['SCALE_FACTOR'] if not pd.isna(row['SCALE_FACTOR']) else 1.0
        
        log(f"[{i+1}/{total}] {rate_id} 요청 중", end='')
        
        formula = f'=IMDH("{row["DATA_TYPE"]}", "{row["DATA_ID"]}", "일자,{row["FIELD_ID"]}", "{start_date}", "{end_date}", 100, "Headers=0,Orient=V,Per=D,Bizday=0")'
        
        try:
            # Busy(0x800ac472) 에러 대응을 위한 재시도 로직
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    scratch_sheet.clear_contents()
                    scratch_sheet.range("A1").formula = formula
                    break
                except Exception as ex:
                    if "0x800ac472" in str(ex) and attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    raise ex

            success = False
            # 데이터 수신 대기 (30초)
            for _ in range(15):
                time.sleep(2)
                log(".", end='')
                
                try:
                    data = scratch_sheet.range("A1:C101").value
                    if data and (data[0][0] or data[0][1]) and "#WAITING" not in str(data[0][0] or "").upper():
                        records = []
                        for r in data:
                            if r[1] is None and r[2] is None: continue
                            if r[1] is not None:
                                val = r[2] * scale if isinstance(r[2], (int, float)) else r[2]
                                records.append([r[1], rate_id, val])
                        
                        if records:
                            final_sheet.range(f"A{final_row}").value = records
                            final_row += len(records)
                            sample_date = int(records[0][0]) if isinstance(records[0][0], float) else records[0][0]
                            log(f" 완료! ({len(records)}행, {sample_date})")
                            try: wb.save()
                            except: pass
                        else:
                            log(" 데이터 없음")
                        success = True
                        break
                except Exception as ex:
                    if "0x800ac472" in str(ex):
                        continue # 바쁘면 다음 루프에서 재시도
                    raise ex
            
            if not success:
                log(" 타임아웃/실패")
                
        except Exception as e:
            log(f" 오류 발생: {e}")
            # 치명적인 오류(예: 엑셀 꺼짐) 발생 시 중단
            if "0x80010108" in str(e) or "0x800706be" in str(e):
                log("엑셀과의 연결이 끊겼습니다. 작업을 중단합니다.")
                break

    log(f"\n[종료] 작업 완료. (최종 행: {final_row-1})")
    try:
        final_sheet.autofit()
        wb.save()
    except: pass

if __name__ == "__main__":
    resume_infomax_extraction()
