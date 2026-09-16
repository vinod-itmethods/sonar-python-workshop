"""Invoice line-item math.

DEMO ROLE: this is the "good" module. It is clean, fully type-hinted and has
100% test coverage. During the demo it shows what a *passing* file looks like
in SonarQube Cloud, so the audience has a baseline to compare the messy
modules against.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class LineItem:
    """A single billable line on an invoice."""

    sku: str
    quantity: int
    unit_price: Decimal


def _round_money(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker-safe HALF_UP.

    Using Decimal (not float) for money is deliberate: SonarQube's Python
    rules flag float arithmetic on currency, and this is the correct pattern
    to point at when someone asks "what should it look like instead?".
    """
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def line_total(item: LineItem) -> Decimal:
    """Return quantity x unit_price, rounded to cents."""
    if item.quantity < 0:
        raise ValueError("quantity must not be negative")
    return _round_money(item.unit_price * item.quantity)


def subtotal(items: list[LineItem]) -> Decimal:
    """Sum of all line totals."""
    return _round_money(sum((line_total(i) for i in items), Decimal("0")))


def apply_tax(amount: Decimal, tax_rate: Decimal) -> Decimal:
    """Apply a tax rate expressed as a fraction (0.13 == 13%)."""
    if tax_rate < 0:
        raise ValueError("tax_rate must not be negative")
    return _round_money(amount * (Decimal("1") + tax_rate))
