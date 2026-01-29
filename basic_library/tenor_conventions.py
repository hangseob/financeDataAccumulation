import re

def tenor_name_to_year_fraction(tenor_name: str) -> float:
    """
    30/360 Convention 기반 테너명을 Year Fraction으로 변환
    - 1D = 1/360
    - 1W = 7/360
    - 1M = 30/360 = 1/12
    - 1Y = 360/360 = 1
    """
    if not tenor_name:
        return 0.0
    
    tenor_name = tenor_name.upper().strip()
    
    # 1. 특수 테너 처리 (일 단위로 취급)
    special_tenors = {
        'ON': 1/360,  # Overnight
        'TN': 1/360,  # Tomorrow Next
        'SN': 1/360,  # Spot Next
        'N': 0.0      # Spot/Unknown (필요 시 0 또는 특정값 설정)
    }
    
    if tenor_name in special_tenors:
        return special_tenors[tenor_name]
    
    # 2. 정규표현식으로 숫자와 단위 분리 (예: '10Y' -> 10, 'Y')
    match = re.match(r'^(\d+)([DWMY])$', tenor_name)
    if not match:
        return 0.0
    
    value = float(match.group(1))
    unit = match.group(2)
    
    # 3. 단위별 계산
    if unit == 'D':      # Day
        return value / 360.0
    elif unit == 'W':    # Week
        return (value * 7.0) / 360.0
    elif unit == 'M':    # Month (30/360에 의해 1개월은 항상 1/12)
        return value / 12.0
    elif unit == 'Y':    # Year
        return value
    
    return 0.0

def year_fraction_to_label(fraction: float) -> str:
    """
    Year Fraction을 읽기 쉬운 라벨(6M, 1Y, 1.5Y 등)로 변환
    """
    if fraction <= 0:
        return "N"
    
    if fraction < 1.0:
        # 1년 미만은 개월(M)로 표시
        months = round(fraction * 12, 1)
        if months == int(months):
            return f"{int(months)}M"
        return f"{months}M"
    else:
        # 1년 이상은 년(Y)으로 표시
        years = round(fraction, 2)
        if years == int(years):
            return f"{int(years)}Y"
        return f"{years}Y"

if __name__ == "__main__":
    # 간단한 테스트
    test_cases = ["1D", "1W", "1M", "3M", "6M", "1Y", "10Y", "ON", "SN", "N"]
    for t in test_cases:
        frac = tenor_name_to_year_fraction(t)
        label = year_fraction_to_label(frac)
        print(f"Tenor: {t:<4} | Fraction: {frac:.6f} | Label: {label}")
