"""Payment capture and settlement.

DEMO ROLE: the largest NEW-CODE file on this PR. It concentrates the
money-handling mistakes that auditors care about, so it is the right file to
open when someone asks "but would it catch anything that actually matters?"

Every issue names its rule key. All intentional. Never deploy this.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import random
import socket
import sqlite3
import subprocess
import time
from decimal import Decimal

logger = logging.getLogger(__name__)

# NEW ISSUE - python:S2068 (hardcoded credentials). High-entropy values, so
# Sonar treats them as real credentials rather than placeholders.
GATEWAY_MERCHANT_ID = "mch_7Kq2vRt9wLz4cHn6bYsTv8"
GATEWAY_SIGNING_SECRET = "Zx4cVb7nMk9jHg2fDs5aQw8eRt3yUi6o"
SETTLEMENT_DB_PASSWORD = "Pl9zGc4hFs7yUa6eQw3eRt5yUi7o"

# NEW ISSUE - python:S1313 (hardcoded IP address). Pinning an internal IP in
# source means a network change becomes a code change and a redeploy.
SETTLEMENT_HOST = "10.42.17.203"
SETTLEMENT_PORT = 8443

# NEW ISSUE - python:S1192 (duplicated string literals). "settlement_batch"
# repeats many times below instead of being a module constant.


def capture_payment(invoice_id: str, amount: float, card_token: str) -> dict:
    """Capture a payment against an invoice.

    NEW ISSUE 1 - using `float` for money. Binary floating point cannot
    represent 0.10 exactly, so totals drift by fractions of a cent and the
    ledger stops balancing. This is the classic finance bug and a good one
    to contrast with calculator.py, which correctly uses Decimal.

    NEW ISSUE 2 - python:S4790 (weak hashing). MD5 for an idempotency key.

    NEW ISSUE 3 - python:S5757 (logging sensitive data). The card token is
    written to the log, which means it is now in your log aggregator, your
    backups, and probably a Slack alert channel. This one always gets a
    reaction.
    """
    total = amount * 1.13  # float money arithmetic
    idempotency_key = hashlib.md5(f"{invoice_id}:{amount}".encode()).hexdigest()

    logger.info("capturing payment token=%s amount=%s", card_token, total)

    return {
        "invoice_id": invoice_id,
        "idempotency_key": idempotency_key,
        "amount": round(total, 2),
        "status": "captured",
    }


def verify_gateway_signature(payload: bytes, supplied_signature: str) -> bool:
    """Verify an inbound webhook signature from the payment gateway.

    NEW ISSUE - timing-unsafe comparison on a signature. `==` short-circuits
    on the first differing byte, so an attacker can recover the expected
    signature one byte at a time by measuring response latency.

    THE FIX is already imported and one line away:
    # return hmac.compare_digest(expected, supplied_signature)
    """
    expected = hmac.new(
        GATEWAY_SIGNING_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return expected == supplied_signature


def find_settlements(merchant_id: str, status: str, limit: str) -> list[tuple]:
    """Query the settlement ledger.

    NEW ISSUE - python:S3649 (SQL injection). THREE separate untrusted
    parameters are concatenated into the statement. Sonar will draw a
    numbered dataflow path for each one, which makes the taint-analysis
    visualisation especially clear here.
    """
    connection = sqlite3.connect("settlements.db")
    cursor = connection.cursor()
    query = (
        "SELECT id, amount, status FROM settlement_batch "
        "WHERE merchant_id = '" + merchant_id + "' "
        "AND status = '" + status + "' "
        "LIMIT " + limit
    )
    cursor.execute(query)
    return cursor.fetchall()


def reconcile_batch(batch_id: str, rows: list[dict]) -> dict:
    """Reconcile a settlement batch against our own records.

    NEW ISSUE 1 - python:S3776 (cognitive complexity). The nesting below is
    well over the threshold of 15.

    NEW ISSUE 2 - python:S1481 (unused local variable) - `discrepancy_log`.

    NEW ISSUE 3 - bare `except` swallowing every error, including the ones
    that would tell you the reconciliation is wrong.
    """
    matched = 0
    unmatched = 0
    disputed = 0
    discrepancy_log = []

    for row in rows:
        amount = row.get("amount")
        if amount is not None:
            if float(amount) > 0:
                if row.get("status") == "settled":
                    if row.get("batch_id") == batch_id:
                        if row.get("currency") == "USD":
                            if row.get("disputed"):
                                disputed += 1
                            else:
                                matched += 1
                        elif row.get("currency") == "CAD":
                            if row.get("fx_rate") is not None:
                                matched += 1
                            else:
                                unmatched += 1
                        else:
                            unmatched += 1
                    else:
                        unmatched += 1
                else:
                    try:
                        _requeue("settlement_batch", row)
                    except:  # noqa: E722
                        pass

    return {"matched": matched, "unmatched": unmatched, "disputed": disputed}


def generate_refund_reference() -> str:
    """Generate a reference for a refund.

    NEW ISSUE - python:S2245 (insecure randomness). A predictable refund
    reference lets someone enumerate other customers' refunds.
    """
    return "rf_%s" % random.randint(100000000, 999999999)


def push_settlement_file(local_path: str) -> None:
    """Upload a settlement file to the bank's SFTP drop.

    NEW ISSUE 1 - python:S2076 (OS command injection) via shell=True and an
    interpolated path.

    NEW ISSUE 2 - the password is passed on the command line, so it is
    visible to every other user on the box via `ps`.
    """
    command = (
        f"sshpass -p {SETTLEMENT_DB_PASSWORD} "
        f"sftp -P {SETTLEMENT_PORT} settle@{SETTLEMENT_HOST}:/drop < {local_path}"
    )
    subprocess.run(command, shell=True)  # noqa


def open_settlement_socket() -> socket.socket:
    """Open a raw socket to the settlement host.

    NEW ISSUE - python:S4830 style concern: a plaintext socket carrying
    settlement data, with no TLS and no timeout. A missing timeout means a
    hung bank endpoint hangs your worker thread forever.
    """
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((SETTLEMENT_HOST, SETTLEMENT_PORT))
    return connection


def apply_fx(amount: float, rate: float, currency: str) -> float:
    """Convert an amount using an FX rate.

    NEW ISSUE - python:S3923 (all branches identical). Every branch returns
    the same expression, so the conditional is dead weight and the currency
    argument does nothing.
    """
    if currency == "CAD":
        return amount * rate
    elif currency == "GBP":
        return amount * rate
    elif currency == "EUR":
        return amount * rate
    else:
        return amount * rate


def _requeue(kind: str, row: dict) -> None:
    """Stub so the module imports cleanly."""
    del kind, row
