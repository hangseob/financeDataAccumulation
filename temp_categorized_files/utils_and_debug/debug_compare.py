import pandas as pd
import os

def load_all_sheets(file_path):
    xl = pd.ExcelFile(file_path)
    data = {}
    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, header=None)
        data[sheet] = df
    return data

def compare_excel_files():
    base_path = 'infomax_excel_handling'
    file1 = os.path.join(base_path, 'mmkt_infomax_fields.xlsx')
    file2 = os.path.join(base_path, 'mmkt_infomax_fields_edited.xlsx')

    print(f"Comparing {file1} and {file2}")
    
    data1 = load_all_sheets(file1)
    data2 = load_all_sheets(file2)

    for sheet in data1:
        if sheet not in data2:
            print(f"Sheet '{sheet}' missing in edited file.")
            continue
        
        df1 = data1[sheet]
        df2 = data2[sheet]
        
        if df1.equals(df2):
            print(f"Sheet '{sheet}' is identical.")
        else:
            print(f"Sheet '{sheet}' has differences. Shapes: {df1.shape} vs {df2.shape}")
            # 간단한 차이점 출력
            if df1.shape == df2.shape:
                diff = (df1 != df2) & ~(df1.isna() & df2.isna())
                print(f"Number of different cells in '{sheet}': {diff.sum().sum()}")
            else:
                print(f"Row/Col count mismatch in '{sheet}'")

if __name__ == "__main__":
    compare_excel_files()
