"""Tests for invoice.calculator.

DEMO ROLE: this file gives calculator.py 100% coverage. Together with
test_discounts.py it produces the coverage.xml that the scanner imports, and
the JUnit XML that populates the "Unit Tests" widget (test count + duration)
in SonarQube Cloud.

Talking point: Sonar does NOT run your tests. pytest runs them, writes the
reports, and the scanner reads those files. If the reports are missing you get
0% coverage and no test count - which is the #1 support question.
"""

from decimal import Decimal

import pytest

from invoice.calculator import LineItem, apply_tax, line_total, subtotal


def test_line_total_multiplies_and_rounds():
    item = LineItem(sku="WIDGET", quantity=3, unit_price=Decimal("19.995"))
    assert line_total(item) == Decimal("59.99")


def test_line_total_zero_quantity():
    item = LineItem(sku="WIDGET", quantity=0, unit_price=Decimal("19.99"))
    assert line_total(item) == Decimal("0.00")


def test_line_total_rejects_negative_quantity():
    item = LineItem(sku="WIDGET", quantity=-1, unit_price=Decimal("10.00"))
    with pytest.raises(ValueError, match="negative"):
        line_total(item)


def test_subtotal_sums_all_lines():
    items = [
        LineItem(sku="A", quantity=2, unit_price=Decimal("10.00")),
        LineItem(sku="B", quantity=1, unit_price=Decimal("5.50")),
    ]
    assert subtotal(items) == Decimal("25.50")


def test_subtotal_of_empty_invoice_is_zero():
    assert subtotal([]) == Decimal("0.00")


def test_apply_tax_adds_percentage():
    assert apply_tax(Decimal("100.00"), Decimal("0.13")) == Decimal("113.00")


def test_apply_tax_zero_rate_is_identity():
    assert apply_tax(Decimal("100.00"), Decimal("0")) == Decimal("100.00")


def test_apply_tax_rejects_negative_rate():
    with pytest.raises(ValueError, match="negative"):
        apply_tax(Decimal("100.00"), Decimal("-0.1"))
