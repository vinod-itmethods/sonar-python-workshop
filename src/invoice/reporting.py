"""Regulatory and finance export builders.

DEMO ROLE: NEW-CODE DUPLICATION. Four near-identical exporters, each ~45
lines, so this file alone pushes duplication on new code over the 3% gate
threshold.

The refactor is obvious - one `_build_export(rows, label, region)` helper -
which makes this the best file to hand to Claude at the end of the session and
say "collapse this". All intentional.
"""

from __future__ import annotations

from decimal import Decimal


def build_daily_export(rows: list[dict], region: str = "US") -> dict:
    """Build the daily export block.

    DUPLICATE of the other exporters in this file - same 40-line body, only
    the report label differs. Deliberately over Sonar's ~100-token minimum
    block size so it registers as duplication on NEW code.
    """
    total = Decimal("0")
    tax_total = Decimal("0")
    fee_total = Decimal("0")
    count = 0
    skipped = 0
    largest = Decimal("0")
    customers = set()
    currencies = set()
    for row in rows:
        if row.get("status") != "settled":
            skipped += 1
            continue
        amount = row.get("amount")
        if amount is None:
            skipped += 1
            continue
        value = Decimal(str(amount))
        if value <= 0:
            skipped += 1
            continue
        total += value
        tax_total += value * Decimal("0.13")
        fee_total += value * Decimal("0.029") + Decimal("0.30")
        count += 1
        if value > largest:
            largest = value
        customer = row.get("customer_id")
        if customer is not None:
            customers.add(customer)
        currency = row.get("currency")
        if currency is not None:
            currencies.add(currency)
    average = total / count if count else Decimal("0")
    return {
        "report": "daily",
        "region": region,
        "total": total,
        "tax_total": tax_total,
        "fee_total": fee_total,
        "count": count,
        "skipped": skipped,
        "largest": largest,
        "unique_customers": len(customers),
        "currencies": sorted(currencies),
        "average": average,
    }

def build_weekly_export(rows: list[dict], region: str = "US") -> dict:
    """Build the weekly export block.

    DUPLICATE of the other exporters in this file - same 40-line body, only
    the report label differs. Deliberately over Sonar's ~100-token minimum
    block size so it registers as duplication on NEW code.
    """
    total = Decimal("0")
    tax_total = Decimal("0")
    fee_total = Decimal("0")
    count = 0
    skipped = 0
    largest = Decimal("0")
    customers = set()
    currencies = set()
    for row in rows:
        if row.get("status") != "settled":
            skipped += 1
            continue
        amount = row.get("amount")
        if amount is None:
            skipped += 1
            continue
        value = Decimal(str(amount))
        if value <= 0:
            skipped += 1
            continue
        total += value
        tax_total += value * Decimal("0.13")
        fee_total += value * Decimal("0.029") + Decimal("0.30")
        count += 1
        if value > largest:
            largest = value
        customer = row.get("customer_id")
        if customer is not None:
            customers.add(customer)
        currency = row.get("currency")
        if currency is not None:
            currencies.add(currency)
    average = total / count if count else Decimal("0")
    return {
        "report": "weekly",
        "region": region,
        "total": total,
        "tax_total": tax_total,
        "fee_total": fee_total,
        "count": count,
        "skipped": skipped,
        "largest": largest,
        "unique_customers": len(customers),
        "currencies": sorted(currencies),
        "average": average,
    }

def build_monthly_export(rows: list[dict], region: str = "CA") -> dict:
    """Build the monthly export block.

    DUPLICATE of the other exporters in this file - same 40-line body, only
    the report label differs. Deliberately over Sonar's ~100-token minimum
    block size so it registers as duplication on NEW code.
    """
    total = Decimal("0")
    tax_total = Decimal("0")
    fee_total = Decimal("0")
    count = 0
    skipped = 0
    largest = Decimal("0")
    customers = set()
    currencies = set()
    for row in rows:
        if row.get("status") != "settled":
            skipped += 1
            continue
        amount = row.get("amount")
        if amount is None:
            skipped += 1
            continue
        value = Decimal(str(amount))
        if value <= 0:
            skipped += 1
            continue
        total += value
        tax_total += value * Decimal("0.13")
        fee_total += value * Decimal("0.029") + Decimal("0.30")
        count += 1
        if value > largest:
            largest = value
        customer = row.get("customer_id")
        if customer is not None:
            customers.add(customer)
        currency = row.get("currency")
        if currency is not None:
            currencies.add(currency)
    average = total / count if count else Decimal("0")
    return {
        "report": "monthly",
        "region": region,
        "total": total,
        "tax_total": tax_total,
        "fee_total": fee_total,
        "count": count,
        "skipped": skipped,
        "largest": largest,
        "unique_customers": len(customers),
        "currencies": sorted(currencies),
        "average": average,
    }

def build_regulatory_export(rows: list[dict], region: str = "EU") -> dict:
    """Build the regulatory export block.

    DUPLICATE of the other exporters in this file - same 40-line body, only
    the report label differs. Deliberately over Sonar's ~100-token minimum
    block size so it registers as duplication on NEW code.
    """
    total = Decimal("0")
    tax_total = Decimal("0")
    fee_total = Decimal("0")
    count = 0
    skipped = 0
    largest = Decimal("0")
    customers = set()
    currencies = set()
    for row in rows:
        if row.get("status") != "settled":
            skipped += 1
            continue
        amount = row.get("amount")
        if amount is None:
            skipped += 1
            continue
        value = Decimal(str(amount))
        if value <= 0:
            skipped += 1
            continue
        total += value
        tax_total += value * Decimal("0.13")
        fee_total += value * Decimal("0.029") + Decimal("0.30")
        count += 1
        if value > largest:
            largest = value
        customer = row.get("customer_id")
        if customer is not None:
            customers.add(customer)
        currency = row.get("currency")
        if currency is not None:
            currencies.add(currency)
    average = total / count if count else Decimal("0")
    return {
        "report": "regulatory",
        "region": region,
        "total": total,
        "tax_total": tax_total,
        "fee_total": fee_total,
        "count": count,
        "skipped": skipped,
        "largest": largest,
        "unique_customers": len(customers),
        "currencies": sorted(currencies),
        "average": average,
    }
