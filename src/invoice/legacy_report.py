"""Legacy invoice reporting.

DEMO ROLE: two things at once.

1. DUPLICATION. The three functions below are near-identical copy-paste, so
   this file lights up the "Duplications" metric (>3% density). Use it to show
   the Duplications tab and the duplicated-block viewer side by side.

2. ZERO COVERAGE. There is deliberately NO test file for this module. It is
   the worst offender on the Coverage tab, which is what makes the
   "Coverage on New Code" quality-gate condition meaningful.

This is also the realistic "we inherited this" module - handy when someone
asks how Clean as You Code handles an existing mess (answer: it doesn't make
you fix it, it just stops you adding more).
"""

from __future__ import annotations

from decimal import Decimal


def monthly_summary(rows: list[dict], tax_rate: Decimal = Decimal("0.13")) -> dict:
    """Aggregate invoice rows for a month."""
    total = Decimal("0")
    tax_total = Decimal("0")
    count = 0
    skipped = 0
    largest = Decimal("0")
    smallest = Decimal("999999")
    currencies = set()
    customers = set()
    for row in rows:
        if row.get("status") != "paid":
            skipped += 1
            continue
        amount = row.get("amount")
        if amount is None:
            skipped += 1
            continue
        value = Decimal(str(amount))
        if value < 0:
            skipped += 1
            continue
        total += value
        tax_total += value * tax_rate
        count += 1
        if value > largest:
            largest = value
        if value < smallest:
            smallest = value
        currency = row.get("currency")
        if currency is not None:
            currencies.add(currency)
        customer = row.get("customer_id")
        if customer is not None:
            customers.add(customer)
    average = total / count if count else Decimal("0")
    return {
        "period": "month",
        "total": total,
        "tax_total": tax_total,
        "count": count,
        "skipped": skipped,
        "largest": largest,
        "smallest": smallest if count else Decimal("0"),
        "currencies": sorted(currencies),
        "unique_customers": len(customers),
        "average": average,
    }


def quarterly_summary(rows: list[dict], tax_rate: Decimal = Decimal("0.13")) -> dict:
    """Aggregate invoice rows for a quarter.

    DUPLICATE of monthly_summary - only the period literal differs. Now well
    over Sonar's ~100-token minimum duplicated-block size, so it registers."""
    total = Decimal("0")
    tax_total = Decimal("0")
    count = 0
    skipped = 0
    largest = Decimal("0")
    smallest = Decimal("999999")
    currencies = set()
    customers = set()
    for row in rows:
        if row.get("status") != "paid":
            skipped += 1
            continue
        amount = row.get("amount")
        if amount is None:
            skipped += 1
            continue
        value = Decimal(str(amount))
        if value < 0:
            skipped += 1
            continue
        total += value
        tax_total += value * tax_rate
        count += 1
        if value > largest:
            largest = value
        if value < smallest:
            smallest = value
        currency = row.get("currency")
        if currency is not None:
            currencies.add(currency)
        customer = row.get("customer_id")
        if customer is not None:
            customers.add(customer)
    average = total / count if count else Decimal("0")
    return {
        "period": "quarter",
        "total": total,
        "tax_total": tax_total,
        "count": count,
        "skipped": skipped,
        "largest": largest,
        "smallest": smallest if count else Decimal("0"),
        "currencies": sorted(currencies),
        "unique_customers": len(customers),
        "average": average,
    }


def annual_summary(rows: list[dict], tax_rate: Decimal = Decimal("0.13")) -> dict:
    """Aggregate invoice rows for a year.

    DUPLICATE again. The obvious refactor is one _summarize(rows, period)
    helper - a good thing to ask Claude to do live at the end of the session."""
    total = Decimal("0")
    tax_total = Decimal("0")
    count = 0
    skipped = 0
    largest = Decimal("0")
    smallest = Decimal("999999")
    currencies = set()
    customers = set()
    for row in rows:
        if row.get("status") != "paid":
            skipped += 1
            continue
        amount = row.get("amount")
        if amount is None:
            skipped += 1
            continue
        value = Decimal(str(amount))
        if value < 0:
            skipped += 1
            continue
        total += value
        tax_total += value * tax_rate
        count += 1
        if value > largest:
            largest = value
        if value < smallest:
            smallest = value
        currency = row.get("currency")
        if currency is not None:
            currencies.add(currency)
        customer = row.get("customer_id")
        if customer is not None:
            customers.add(customer)
    average = total / count if count else Decimal("0")
    return {
        "period": "year",
        "total": total,
        "tax_total": tax_total,
        "count": count,
        "skipped": skipped,
        "largest": largest,
        "smallest": smallest if count else Decimal("0"),
        "currencies": sorted(currencies),
        "unique_customers": len(customers),
        "average": average,
    }
