"""Tests for invoice.discounts.

DEMO ROLE: PARTIAL coverage on purpose (~60%). The deeply-nested coupon
branches in compute_discount are never exercised, so the Coverage tab shows
red uncovered lines right next to the cognitive-complexity issue. That is a
nice one-two punch: "this code is too complex AND untested".

Note test_gold_tier_discount below - it passes today, which is exactly the
problem. It asserts the *buggy* 10% gold rate. When you accept the AI CodeFix
on tier_discount(), this test goes RED, and you get to make the point that
Sonar found a bug the test suite was actively protecting.
"""

from decimal import Decimal

from invoice.discounts import compute_discount, final_price, is_eligible, tier_discount


def test_bronze_tier_discount():
    assert tier_discount("bronze", Decimal("100")) == Decimal("0.02")


def test_silver_tier_discount():
    assert tier_discount("silver", Decimal("1000")) == Decimal("0.10")


def test_gold_tier_discount():
    # Asserts the CURRENT (buggy) behaviour - see module docstring.
    assert tier_discount("gold", Decimal("5000")) == Decimal("0.10")


def test_unknown_tier_gets_nothing():
    assert tier_discount("platinum", Decimal("100")) == Decimal("0")


def test_employee_is_always_eligible():
    assert is_eligible(Decimal("0"), is_employee=True) is True


def test_zero_subtotal_not_eligible():
    assert is_eligible(Decimal("0"), is_employee=False) is False


def test_compute_discount_tier_only():
    result = compute_discount(
        subtotal=Decimal("100"),
        tier="bronze",
        coupon_code=None,
        is_employee=False,
        is_first_order=False,
        region="US",
    )
    assert result == Decimal("0.02")


def test_compute_discount_is_capped():
    result = compute_discount(
        subtotal=Decimal("100"),
        tier="gold",
        coupon_code="SAVE50",
        is_employee=True,
        is_first_order=True,
        region="US",
    )
    assert result == Decimal("0.60")


def test_final_price_applies_fraction():
    assert final_price(Decimal("100"), Decimal("0.25")) == Decimal("75.00")
