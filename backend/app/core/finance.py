"""Shared financial helpers.

The MVP keeps all finance math in Decimal and rounds at the edges. This is a
tradeoff in favor of predictable logic over implementation brevity.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


TWOPLACES = Decimal("0.01")


def money(value: object) -> Decimal:
    """Normalize numeric input into a two-decimal-place Decimal."""
    if isinstance(value, Decimal):
        amount = value
    else:
        amount = Decimal(str(value))
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def clamp_non_negative(value: Decimal) -> Decimal:
    return value if value > Decimal("0.00") else Decimal("0.00")


def monthly_multiplier(frequency: str) -> Decimal:
    """Convert supported recurring frequencies into monthly multipliers."""
    mapping = {
        "weekly": Decimal("52") / Decimal("12"),
        "biweekly": Decimal("26") / Decimal("12"),
        "semimonthly": Decimal("2"),
        "monthly": Decimal("1"),
        "quarterly": Decimal("1") / Decimal("3"),
        "annual": Decimal("1") / Decimal("12"),
    }
    if frequency not in mapping:
        raise ValueError(f"Unsupported frequency: {frequency}")
    return mapping[frequency]


def to_monthly(amount: object, frequency: str) -> Decimal:
    return money(money(amount) * monthly_multiplier(frequency))


def sum_money(values: Iterable[Decimal]) -> Decimal:
    total = Decimal("0.00")
    for value in values:
        total += money(value)
    return money(total)


def decimal_to_float(value: Decimal) -> float:
    return float(money(value))

