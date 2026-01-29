import re

def tenor_name_to_year_fraction(tenor_name):
    """
    Tenor 명칭(예: '1M', '3Y', '6M', 'ON')을 연 단위 숫자(float)로 변환합니다.
    """
    if not tenor_name:
        return 0.0
    
    tenor_name = str(tenor_name).upper().strip()
    
    # 특수 명칭 처리
    if tenor_name in ['ON', 'TN', 'SN', 'O/N', 'T/N', 'S/N']:
        return 1.0 / 365.0
    
    # 정규표현식으로 숫자와 단위 분리 (Y=Year, M=Month, W=Week, D=Day)
    match = re.match(r'(\d+)([YMWD])', tenor_name)
    if not match:
        return 0.0
    
    value = float(match.group(1))
    unit = match.group(2)
    
    if unit == 'Y':
        return value
    elif unit == 'M':
        return value / 12.0
    elif unit == 'W':
        return value / 52.0
    elif unit == 'D':
        return value / 365.0
    
    return 0.0
