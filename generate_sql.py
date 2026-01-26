import pandas as pd
import re
import os

file_path = 'infomax_excel_handling/mmkt_infomax_fields_edited.xlsx'
output_sql = 'create_spt_infomax_fields.sql'

try:
    # 엑셀 데이터 읽기
    df_excel = pd.read_excel(file_path, sheet_name='Sheet2', skiprows=1)
    df_excel = df_excel.rename(columns={'Unnamed: 1': 'RATE_ID'})
    
    special_tenors = ['ON', 'TN', 'SN']
    
    def parse_tenor(rate_id):
        if not isinstance(rate_id, str): return 'N', rate_id
        for st in special_tenors:
            if rate_id.endswith(st):
                return st, rate_id[:-len(st)]
        match = re.search(r'(\d+[DWMY])$', rate_id)
        if match:
            tenor = match.group(1)
            curve_id = rate_id[:-len(tenor)]
            return tenor, curve_id
        return 'N', rate_id

    # 전체 데이터 파싱 및 리스트 생성
    rows = []
    for _, row in df_excel.dropna(subset=['RATE_ID']).iterrows():
        rid = row['RATE_ID']
        tenor_name, curve_id = parse_tenor(rid)
        rows.append({
            'RATE_ID': rid,
            'TENOR_NAME': tenor_name,
            'CURVE_ID': curve_id
        })

    # SQL 생성
    sql = []
    sql.append('CREATE SCHEMA IF NOT EXISTS spt;')
    sql.append('')
    sql.append('CREATE TABLE IF NOT EXISTS spt.mmkt_infomax_fields_supabase (')
    sql.append('    rate_id VARCHAR(50) PRIMARY KEY,')
    sql.append('    tenor_name VARCHAR(10),')
    sql.append('    curve_id VARCHAR(40)')
    sql.append(');')
    sql.append('')
    sql.append('-- 데이터 삽입 (UPSERT 방식)')
    
    for r in rows:
        rid = str(r['RATE_ID']).replace("'", "''")
        tn = str(r['TENOR_NAME']).replace("'", "''")
        cid = str(r['CURVE_ID']).replace("'", "''")
        sql.append(f"INSERT INTO spt.mmkt_infomax_fields_supabase (rate_id, tenor_name, curve_id) VALUES ('{rid}', '{tn}', '{cid}') ON CONFLICT (rate_id) DO UPDATE SET tenor_name = EXCLUDED.tenor_name, curve_id = EXCLUDED.curve_id;")

    with open(output_sql, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql))
    
    print(f'Successfully created {output_sql} with {len(rows)} insert statements.')
except Exception as e:
    print(f'Error: {e}')
