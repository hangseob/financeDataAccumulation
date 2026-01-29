import re
import sys

def convert_to_markdown():
    input_file = "kospi200 list"
    
    try:
        # 파일 내용을 바이너리로 읽어서 앞부분 확인
        with open(input_file, "rb") as f:
            raw_data = f.read(100)
            print(f"Raw data (first 100 bytes): {raw_data}")
            
        # 다양한 인코딩 시도
        encodings = ['utf-8', 'cp949', 'utf-16']
        content = None
        for enc in encodings:
            try:
                with open(input_file, "r", encoding=enc) as f:
                    content = f.read()
                    print(f"Successfully read with {enc}")
                    break
            except:
                continue
        
        if content:
            lines = content.splitlines()
            print(f"Total lines: {len(lines)}")
            for i, line in enumerate(lines[:5]):
                print(f"Line {i}: {repr(line)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    convert_to_markdown()
