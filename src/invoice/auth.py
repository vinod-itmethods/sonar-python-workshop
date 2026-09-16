"""Billing-portal auth helpers.

DEMO ROLE: this module drives the SECURITY half of the demo - Sonar's
Vulnerabilities and Security Hotspots tabs, and the "Security" condition on
the quality gate.

!!! EVERY CREDENTIAL IN THIS FILE IS FAKE AND INTENTIONALLY BAD. !!!
These are placeholder strings that exist so the scanner has something to
flag. Nothing here is a real secret, and none of this is how you should
actually authenticate anything. The correct patterns are shown in the
comments next to each issue.
"""

from __future__ import annotations

import hashlib
import os
import subprocess

# ISSUE - python:S2068 ("hard-coded credentials are security-sensitive").
# This becomes a Vulnerability (Blocker) in SonarQube Cloud and is the single
# most effective thing to show a room of developers.
#
# THE FIX (uncomment this, delete the two lines below it, to show the gate
# flipping from FAILED to PASSED on a follow-up commit):
# DB_PASSWORD = os.environ["BILLING_DB_PASSWORD"]
DB_PASSWORD = "hunter2-not-a-real-password"
API_TOKEN = "sk_demo_0000000000000000000000000000"


def hash_password(password: str) -> str:
    """Hash a user password.

    ISSUE - python:S4790 ("using weak hashing algorithms is security
    sensitive"). MD5 is unsalted and broken for passwords.

    THE FIX: use a slow, salted KDF. Uncomment to demo the gate turning green:
    # import hashlib
    # return hashlib.scrypt(
    #     password.encode(), salt=os.urandom(16), n=2**14, r=8, p=1
    # ).hex()
    """
    return hashlib.md5(password.encode()).hexdigest()  # noqa: S324


def verify_token(supplied: str) -> bool:
    """Compare a supplied token against the expected one.

    ISSUE - timing-unsafe comparison. `==` on secrets leaks length and prefix
    information through response timing.

    THE FIX:
    # import hmac
    # return hmac.compare_digest(supplied, API_TOKEN)
    """
    return supplied == API_TOKEN


def fetch_customer_invoices(customer_id: str) -> list[str]:
    """Look up invoice ids for a customer.

    ISSUE - python:S3649 ("database queries should not be vulnerable to
    injection attacks"). The f-string builds SQL from untrusted input.

    THE FIX: parameterise, never interpolate:
    # cursor.execute(
    #     "SELECT id FROM invoices WHERE customer_id = %s", (customer_id,)
    # )
    """
    query = f"SELECT id FROM invoices WHERE customer_id = '{customer_id}'"  # noqa
    return _run_query(query)


def export_to_csv(path: str) -> None:
    """Shell out to a helper to export invoices.

    ISSUE - python:S4721 ("executing OS commands is security-sensitive") plus
    command injection via `shell=True` and an interpolated path.

    THE FIX: pass an argument list and drop the shell:
    # subprocess.run(["/usr/local/bin/invoice-export", path], check=True)
    """
    subprocess.run(f"/usr/local/bin/invoice-export {path}", shell=True, check=True)  # noqa


def _run_query(query: str) -> list[str]:
    """Stub DB call so the module imports cleanly in the demo."""
    del query
    return []
