import re
import sys

def convert_to_markdown():
    input_file = "kospi200 list"
    output_file = "kospi200_list.md"
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        md_lines = []
        # 헤더는 데이터 구조(6열)에 맞춰 명시적으로 작성
        header = ["종목명", "현재가", "구분", "전일대비", "등락률(%)", "시총(억)"]
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        count = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith("종목명"):
                continue
            
            # 탭(\t)을 기준으로만 분리하고 각 항목의 앞뒤 공백 제거
            parts = [p.strip() for p in line.split('\t') if p.strip()]
            
            # 데이터 개수 보정
            if len(parts) == 6:
                md_lines.append("| " + " | ".join(parts) + " |")
                count += 1
            elif len(parts) == 5:
                # 구분이 없는 경우 인덱스 2번에 빈 값 삽입
                parts.insert(2, "")
                md_lines.append("| " + " | ".join(parts) + " |")
                count += 1
            elif len(parts) > 6:
                md_lines.append("| " + " | ".join(parts[:6]) + " |")
                count += 1
            elif len(parts) > 0:
                while len(parts) < 6:
                    parts.append("")
                md_lines.append("| " + " | ".join(parts[:6]) + " |")
                count += 1

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        
        print(f"Successfully saved {output_file} with {count} rows.")
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    convert_to_markdown()
