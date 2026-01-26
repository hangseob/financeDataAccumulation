import pandas as pd
import os

def load_with_header(file_path, sheet_name):
    # 헤더를 찾기 위해 일단 읽음
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    # 'RATE_ID'가 포함된 행 찾기
    for i, row in df.iterrows():
        if 'RATE_ID' in row.values:
            df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=i+1)
            # 만약 skiprows=i+1을 하면 그 다음 행부터 읽히는데, 
            # pandas read_excel의 header 인자를 사용하는 게 더 정확함.
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=i)
            return df
    return df

def compare_excel_files():
    base_path = 'infomax_excel_handling'
    file1 = os.path.join(base_path, 'mmkt_infomax_fields.xlsx')
    file2 = os.path.join(base_path, 'mmkt_infomax_fields_edited.xlsx')

    if not os.path.exists(file1) or not os.path.exists(file2):
        print(f"파일을 찾을 수 없습니다: {file1} 또는 {file2}")
        return

    print("파일 분석 중...")

    df1 = load_with_header(file1, 'Sheet2')
    df2 = load_with_header(file2, 'Sheet2')

    # 컬럼명에서 'Unnamed' 제거 및 정리
    df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
    df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

    target_col = 'RATE_ID'
    if target_col not in df1.columns or target_col not in df2.columns:
        print(f"Error: '{target_col}' 컬럼을 찾을 수 없습니다.")
        print(f"File1 Cols: {df1.columns.tolist()}")
        print(f"File2 Cols: {df2.columns.tolist()}")
        return

    df1 = df1.dropna(subset=[target_col]).set_index(target_col)
    df2 = df2.dropna(subset=[target_col]).set_index(target_col)

    # 차이점 분석
    added_rows = df2.index.difference(df1.index)
    removed_rows = df1.index.difference(df2.index)
    common_idx = df1.index.intersection(df2.index)
    
    df1_common = df1.loc[common_idx]
    df2_common = df2.loc[common_idx]
    common_cols = df1_common.columns.intersection(df2_common.columns)
    
    df1_common = df1_common[common_cols]
    df2_common = df2_common[common_cols]

    # 값 비교 (문자열 변환 후 비교하여 타입 차이 무시)
    diff_mask = (df1_common.astype(str) != df2_common.astype(str)) & ~(df1_common.isna() & df2_common.isna())
    changed_rows_idx = diff_mask.any(axis=1)
    changed_data = df2_common[changed_rows_idx]

    diff_details = []
    for idx in df2_common.index[changed_rows_idx]:
        for col in common_cols:
            val1 = df1_common.loc[idx, col]
            val2 = df2_common.loc[idx, col]
            if str(val1) != str(val2) and not (pd.isna(val1) and pd.isna(val2)):
                diff_details.append({
                    'RATE_ID': idx,
                    'Column': col,
                    'Old': val1,
                    'New': val2
                })

    print(f"\n--- 비교 요약 ---")
    print(f"추가된 행: {len(added_rows)}")
    print(f"삭제된 행: {len(removed_rows)}")
    print(f"내용 수정됨: {len(changed_data)}")

    with open('infomax_comparison_report.md', 'w', encoding='utf-8') as f:
        f.write('# 엑셀 파일 비교 결과 보고서\n\n')
        f.write(f'| 항목 | 개수 |\n| :--- | :--- |\n')
        f.write(f'| 추가된 RATE_ID | {len(added_rows)} |\n')
        f.write(f'| 삭제된 RATE_ID | {len(removed_rows)} |\n')
        f.write(f'| 내용이 변경된 행 | {len(changed_data)} |\n\n')

        if not added_rows.empty:
            f.write('## 추가된 행 (Top 10)\n')
            f.write(df2.loc[added_rows].head(10).to_markdown() + '\n\n')
        if diff_details:
            f.write('## 상세 변경 내용 (Top 50)\n')
            f.write(pd.DataFrame(diff_details).head(50).to_markdown(index=False) + '\n\n')

    print(f"\n보고서가 'infomax_comparison_report.md'에 저장되었습니다.")

if __name__ == "__main__":
    compare_excel_files()
