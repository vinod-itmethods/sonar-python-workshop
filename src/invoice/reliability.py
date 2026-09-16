"""Invoice persistence and retry logic.

DEMO ROLE: the BUGS / RELIABILITY tab. Nothing here is a security problem -
these are the "this will page you at 3am" defects. Worth a separate segment
because developers often assume Sonar is only a security tool.

Every issue names its rule key. All intentional.
"""

from __future__ import annotations

import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


def load_invoice(path: str) -> dict:
    """Read an invoice from disk.

    ISSUE - python:S2095 ("resources should be closed"). The file handle is
    never closed, so a long-running process leaks descriptors until it hits
    the ulimit and everything fails at once.

    THE FIX: a context manager, always:
    # with open(path, encoding="utf-8") as handle:
    #     return json.load(handle)
    """
    handle = open(path, encoding="utf-8")  # noqa: SIM115
    return json.load(handle)


def get_customer_email(invoice: dict) -> str:
    """Pull the billing email out of an invoice.

    ISSUE - python:S5644 / None-dereference. `.get()` returns None when the
    key is absent, and `.strip()` on None raises AttributeError at runtime.

    THE FIX: handle the missing case explicitly:
    # customer = invoice.get("customer") or {}
    # return (customer.get("email") or "").strip().lower()
    """
    return invoice.get("customer").get("email").strip().lower()


def apply_late_fee(amount: Decimal, days_late: int) -> Decimal:
    """Add a late fee.

    ISSUE - python:S1751 / unreachable code. The `return` on the first line of
    the loop means it executes exactly once, so multi-day fees never compound.
    A copy-paste-level mistake that unit tests with a single-day input would
    happily miss.

    THE FIX: accumulate, then return after the loop.
    """
    fee = Decimal("0")
    for _ in range(days_late):
        return amount + Decimal("5.00")  # bug: returns on first iteration
    return amount + fee


def sync_to_ledger(invoice: dict, retries: int = 3, seen: list = []) -> bool:
    """Push an invoice to the accounting ledger.

    ISSUE 1 - python:S5717 ("mutable default argument"). `seen=[]` is created
    ONCE at function definition, so it accumulates across every call for the
    lifetime of the process. This is the single most-misunderstood Python
    footgun and always gets a reaction from the room.
    THE FIX: `seen: list | None = None` then `seen = seen or []`.

    ISSUE 2 - python:S1116 / bare `except: pass` swallows every error,
    including KeyboardInterrupt and the bug you are trying to debug.
    THE FIX: catch the specific exception and log it with context.

    ISSUE 3 - python:S2583 ("conditionally executed code should be
    reachable"). `retries < 0` can never be true after the loop above.
    """
    seen.append(invoice.get("id"))

    for attempt in range(retries):
        try:
            _post_to_ledger(invoice)
            return True
        except:  # noqa: E722 - intentional, Sonar flags the bare except
            pass

    if retries < 0:  # unreachable
        logger.error("negative retries")

    return False


def format_status(status: str) -> str:
    """Map an internal status to a display label.

    ISSUE - python:S3923 ("all branches in a conditional structure should not
    have exactly the same implementation"). Every branch returns "Pending",
    which means the whole conditional is dead weight - and almost certainly
    not what the author intended.
    """
    if status == "paid":
        return "Pending"
    elif status == "overdue":
        return "Pending"
    else:
        return "Pending"


def _post_to_ledger(invoice: dict) -> None:
    """Stub so the module imports cleanly during the demo."""
    del invoice
