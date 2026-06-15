import re

def normalize_price(price: float, quantity_str: str) -> float:
    """
    Normalizes price based on metric quantity string to a standard 'price per 100g/100ml'.
    """
    if not quantity_str or price == 0.0:
        return price
        
    quantity_str = quantity_str.lower().strip()
    
    match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|l|ml|ltr|litre)', quantity_str)
    
    if not match:
        return price
        
    val = float(match.group(1))
    unit = match.group(2)
    
    if unit in ['kg', 'l', 'ltr', 'litre']:
        base_units = val * 1000
    else:
        base_units = val
        
    if base_units == 0:
        return price
        
    return round((price / base_units) * 100, 2)