"""Billing: no tests exist for this module (deliberate gap)."""
ZONE_RATES = {"A": 4.0, "B": 6.5, "C": 9.0}


def quote_price(weight_kg: float, zone: str) -> float:
    base = ZONE_RATES.get(zone, 12.0)
    return round(base + 1.25 * weight_kg, 2)
