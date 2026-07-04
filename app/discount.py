from statistics import mean, median
from typing import Iterable


def detect_rare_discount(
    current_price: float,
    historical_prices: Iterable[float],
    threshold: float = 0.20,
    min_points: int = 10,
    use_median: bool = True,
) -> dict:
    """Detect whether current price is unusually low vs recent history."""
    prices = [float(p) for p in historical_prices if p is not None and float(p) > 0]

    if current_price <= 0:
        return {"is_rare_discount": False, "reason": "invalid_current_price"}

    if len(prices) < min_points:
        return {
            "is_rare_discount": False,
            "reason": "not_enough_history",
            "points": len(prices),
        }

    baseline_price = median(prices) if use_median else mean(prices)
    if baseline_price <= 0:
        return {"is_rare_discount": False, "reason": "invalid_baseline_price"}

    discount_rate = (baseline_price - current_price) / baseline_price

    return {
        "is_rare_discount": discount_rate >= threshold,
        "current_price": round(current_price, 2),
        "baseline_price": round(baseline_price, 2),
        "discount_rate": round(discount_rate, 4),
        "discount_percent": round(discount_rate * 100, 2),
        "points": len(prices),
    }
