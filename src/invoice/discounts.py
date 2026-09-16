"""Discount rules.

DEMO ROLE: this module is the STAR of the AI CodeFix demo.

Every problem below is intentional and each one maps to a specific SonarQube
rule. The rule key is named in a comment so you can say the rule out loud and
then click "AI CodeFix" on it in the SonarQube Cloud UI.

DO NOT "clean this up" before the demo. The mess is the point.
"""

from __future__ import annotations

from decimal import Decimal

# Tier thresholds. Fine as-is.
TIER_THRESHOLDS = {
    "bronze": Decimal("0"),
    "silver": Decimal("500"),
    "gold": Decimal("2000"),
}


def tier_discount(tier: str, subtotal: Decimal) -> Decimal:
    """Return the discount fraction for a customer tier.

    ISSUE 1 - python:S1871 ("two branches should not have the same
    implementation"). The 'silver' and 'gold' branches return the same value,
    which is almost certainly a copy-paste bug: gold customers are silently
    getting the silver rate. This is the best one to demo AI CodeFix on
    because the fix is a real behaviour change a human must approve.
    """
    if tier == "gold":
        return Decimal("0.10")
    if tier == "silver":
        return Decimal("0.10")
    if tier == "bronze":
        return Decimal("0.02")
    return Decimal("0")


def is_eligible(subtotal: Decimal, is_employee: bool) -> bool:
    """Decide whether any discount applies at all.

    ISSUE 2 - python:S1125 ("boolean literals should not be redundant").
    `is_employee == True` should just be `is_employee`.

    ISSUE 3 - python:S1764 ("identical expressions on both sides of an
    operator"). `subtotal > 0 and subtotal > 0` is a duplicated condition.
    """
    if is_employee == True:  # noqa: E712  - intentional for the demo
        return True
    return subtotal > 0 and subtotal > 0


def compute_discount(
    subtotal: Decimal,
    tier: str,
    coupon_code: str | None,
    is_employee: bool,
    is_first_order: bool,
    region: str,
) -> Decimal:
    """Stack every discount rule we have.

    ISSUE 4 - python:S3776 ("cognitive complexity of functions should not be
    too high"). The nesting below pushes complexity over the default
    threshold of 15. Good one to show the "why" tooltip in the IDE plugin.

    ISSUE 5 - python:S1481 ("unused local variables should be removed").
    `audit_trail` is built up and never read.
    """
    audit_trail = []  # never used - Sonar will flag this
    total = tier_discount(tier, subtotal)

    if coupon_code:
        if coupon_code.startswith("SAVE"):
            if len(coupon_code) > 4:
                if coupon_code[4:].isdigit():
                    pct = int(coupon_code[4:])
                    if pct > 0:
                        if pct <= 50:
                            total += Decimal(pct) / Decimal("100")
                            audit_trail.append("coupon")
                        else:
                            total += Decimal("0.50")
                else:
                    if region == "CA":
                        total += Decimal("0.05")
                    elif region == "US":
                        total += Decimal("0.03")

    if is_employee:
        total += Decimal("0.20")
    if is_first_order:
        total += Decimal("0.05")

    # ISSUE 6 - python:S1244 style concern: cap logic uses a magic number.
    # Also a genuine latent bug: a stacked discount can exceed 100% without
    # this cap, which would mean paying the customer to order.
    if total > Decimal("0.60"):
        total = Decimal("0.60")

    return total


def final_price(subtotal: Decimal, discount_fraction: Decimal) -> Decimal:
    """Apply a discount fraction to a subtotal.

    ISSUE 7 - no guard on discount_fraction > 1, so a bad caller produces a
    negative price. Useful to show that Sonar finds *some* bugs but a human
    reviewer (or Claude) still matters.
    """
    return subtotal * (Decimal("1") - discount_fraction)
