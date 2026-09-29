"""Tests for invoice.reminders.

DEMO ROLE: deliberately THIN. It covers one trivial function so that
"Coverage on New Code" comes out low but not zero - which is the realistic
case, and more interesting than a flat 0%.

If your quality gate has a coverage-on-new-code condition (the Sonar way
default is 80%), this is what trips it.
"""

from invoice.reminders import build_reminder_email, reminder_id
from decimal import Decimal


def test_reminder_email_contains_customer_name():
    body = build_reminder_email("Acme Corp", Decimal("500.00"), 45)
    assert "Acme Corp" in body
    assert "45 days overdue" in body


def test_reminder_id_is_stable():
    assert reminder_id("INV-1001") == reminder_id("INV-1001")
