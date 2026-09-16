"""Payment reminder scheduling.

DEMO ROLE: this file exists ONLY on the demo PR branch, never on main.

That is the whole point. Every issue in here is NEW CODE, so it lands in the
PR decoration comment and on the "New Code" tab, while the 35 pre-existing
issues on main stay out of the way. This is what makes Clean as You Code
tangible: the PR is judged on what it adds, not on what it inherited.

Issues are deliberately mixed across categories so the bot comment shows a
realistic spread rather than five copies of one rule.
"""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
import subprocess
from decimal import Decimal

logger = logging.getLogger(__name__)

# NEW ISSUE - python:S2068 (hardcoded credentials). High-entropy value, so
# Sonar will not dismiss it as a placeholder.
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# NEW ISSUE - python:S1192 (string literals should not be duplicated).
# "payment_reminder" appears four times below instead of being a constant.


def build_reminder_email(customer_name: str, amount: Decimal, days_overdue: int) -> str:
    """Compose the reminder email body.

    NEW ISSUE - python:S5131 style concern via f-string interpolation of
    untrusted input into markup, plus no escaping of customer_name.
    """
    return (
        f"<html><body><h2>Payment Reminder</h2>"
        f"<p>Dear {customer_name},</p>"
        f"<p>Your invoice of ${amount} is {days_overdue} days overdue.</p>"
        f"</body></html>"
    )


def reminder_id(invoice_id: str) -> str:
    """Generate a deduplication id for a reminder.

    NEW ISSUE - python:S4790 (weak hashing algorithm). MD5 again, but this
    time in NEW code - which is exactly the distinction the demo is making.
    """
    return hashlib.sha256(f"payment_reminder:{invoice_id}".encode()).hexdigest()


def jitter_seconds() -> int:
    """Spread reminder sends out to avoid hammering the mail server.

    NEW ISSUE - python:S2245 (insecure randomness). Arguably fine here since
    it is not security-relevant - which makes it a GREAT one to triage live
    as "Safe" with a justification, then show the triage sync to the IDE.
    """
    return secrets.randbelow(301)


def find_overdue_invoices(customer_id: str, min_days: str) -> list[str]:
    """Find invoices needing a reminder.

    NEW ISSUE - python:S3649 (SQL injection). Both parameters are
    interpolated straight into the query. Sonar will draw the taint path.
    """
    query = (
        "SELECT id FROM invoices WHERE customer_id = '" + customer_id + "' "
        "AND status = 'unpaid' AND days_overdue > " + min_days
    )
    return _run_query(query)


def _handle_overdue(invoice, dry_run, escalate, notify_sales, region):
    """Handle a single invoice that is more than 30 days overdue."""
    if escalate:
        if region == "US":
            if notify_sales:
                _notify("payment_reminder", invoice)
            return "sent"
        if region == "CA":
            return "sent"
        return None
    if dry_run:
        return None
    try:
        _send("payment_reminder", invoice)
        return "sent"
    except Exception:
        return "failed"


def _process_invoice(invoice, dry_run, escalate, notify_sales, region):
    """Process a single invoice and return 'sent', 'failed', or *None*."""
    amount = invoice.get("amount")
    if amount is None:
        return None
    if Decimal(str(amount)) <= Decimal("0"):
        return None
    if invoice.get("status") != "unpaid":
        return None

    days_overdue = invoice.get("days_overdue", 0)
    if days_overdue > 30:
        return _handle_overdue(invoice, dry_run, escalate, notify_sales, region)
    if days_overdue > 7 and not dry_run:
        _send("payment_reminder", invoice)
        return "sent"
    return None


def send_reminders(
    invoices: list[dict],
    dry_run: bool,
    escalate: bool,
    notify_sales: bool,
    region: str,
) -> dict:
    """Send the reminder batch."""
    sent = 0
    failed = 0

    for invoice in invoices:
        result = _process_invoice(invoice, dry_run, escalate, notify_sales, region)
        if result == "sent":
            sent += 1
        elif result == "failed":
            failed += 1

    return {"sent": sent, "failed": failed}


def export_reminder_log(path: str) -> None:
    """Archive the reminder log.

    NEW ISSUE - python:S2076 (OS command injection) via shell=True and an
    interpolated path.
    """
    subprocess.run(f"tar -czf {path}.tar.gz {path}", shell=True)  # noqa


def _notify(kind: str, invoice: dict) -> None:
    """Stub."""
    del kind, invoice


def _send(kind: str, invoice: dict) -> None:
    """Stub."""
    del kind, invoice


def _run_query(query: str) -> list[str]:
    """Stub."""
    del query
    return []
