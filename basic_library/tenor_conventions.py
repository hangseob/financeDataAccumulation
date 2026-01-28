import re

def tenor_name_to_year_fraction(tenor_name):
    """
    Converts a tenor name (e.g., '1Y', '6M', '3M', 'ON', 'TN') to a year fraction.
    """
    if not tenor_name:
        return 0.0
    
    tenor_name = tenor_name.upper().strip()
    
    # Special cases
    if tenor_name == 'ON': return 1.0 / 365.0
    if tenor_name == 'TN': return 2.0 / 365.0
    if tenor_name == 'SN': return 3.0 / 365.0
    
    # Regular patterns
    match = re.match(r'^(\d+)([DYMWY])$', tenor_name)
    if not match:
        # Try to handle cases like '12M' as '1Y' etc if needed, 
        # but the regex above should handle '12M' as 12 * (1/12)
        match = re.match(r'^(\d+)([A-Z]+)$', tenor_name)
        if not match:
            return 0.0
            
    value = float(match.group(1))
    unit = match.group(2)
    
    if unit == 'D':
        return value / 365.0
    elif unit == 'W':
        return value * 7.0 / 365.0
    elif unit == 'M':
        return value / 12.0
    elif unit == 'Y':
        return value
    else:
        # Fallback for unexpected units
        return value
