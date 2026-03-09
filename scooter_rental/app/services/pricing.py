from decimal import Decimal, ROUND_HALF_UP

BASE_FEE_CHF = Decimal("1.00")
PER_MINUTE_CHF = Decimal("0.35")


def calculate_price_minutes(minutes: int) -> Decimal:
    if minutes < 0:
        raise ValueError("minutes must be >= 0")
    price = BASE_FEE_CHF + (PER_MINUTE_CHF * Decimal(minutes))
    return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
