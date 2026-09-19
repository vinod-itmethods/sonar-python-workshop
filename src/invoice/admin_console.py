"""Internal admin console for the billing team.

DEMO ROLE: the "how did this ever get merged" file. These are the highest
severity findings in the whole repo - remote code execution by three separate
routes. Open this one when you want the room to go quiet.

Sonar reports these as BLOCKER severity. All intentional. Never deploy this.
"""

from __future__ import annotations

import base64
import logging
import os
import pickle
import subprocess
import tempfile

from flask import Blueprint, request

logger = logging.getLogger(__name__)

admin = Blueprint("admin", __name__)

# NEW ISSUE - python:S2068 (hardcoded credentials), and a shared admin
# password is an accountability problem as well as a security one: every
# action in the audit log says "admin".
ADMIN_PASSWORD = "Mn7bVc4xZq2wEr9tYu5iOp3a"
SUPPORT_OVERRIDE_PIN = "839172"


@admin.route("/admin/run-report", methods=["POST"])
def run_report():
    """Run an ad-hoc report expression supplied by an operator.

    NEW ISSUE - python:S1523 (dynamic code execution). `eval` on request data
    is unauthenticated remote code execution. The "it's behind our VPN and
    only ops can reach it" defence evaporates the moment anyone phishes an
    ops credential.

    THE FIX: there is no safe way to eval user input. Expose a fixed set of
    named reports and dispatch on the name:
    # REPORTS = {"monthly": monthly_summary, "annual": annual_summary}
    # return REPORTS[request.form["name"]](rows)
    """
    expression = request.form.get("expr", "")
    return str(eval(expression))  # noqa: S307 - RCE


@admin.route("/admin/import-state", methods=["POST"])
def import_state():
    """Import a serialised console state blob.

    NEW ISSUE - python:S5135 (unsafe deserialization). pickle.loads on
    attacker-controlled bytes is RCE. Base64 in front of it changes nothing
    except making it look deliberate.

    THE FIX: json.loads. A data format that cannot execute code.
    """
    blob = base64.b64decode(request.form.get("state", ""))
    return str(pickle.loads(blob))  # noqa - RCE


@admin.route("/admin/exec-maintenance", methods=["POST"])
def exec_maintenance():
    """Run a named maintenance script.

    NEW ISSUE - python:S4721 / S2076 (OS command injection). `os.system`
    with interpolated input is the oldest mistake in the book.

    THE FIX: allowlist the script name, then exec by argument list:
    # if name not in ALLOWED_SCRIPTS: abort(400)
    # subprocess.run(["/opt/maint/" + name], check=True, timeout=300)
    """
    script = request.form.get("script", "vacuum")
    os.system(f"/opt/maint/{script}.sh")  # noqa: S605 - command injection
    return "ok"


@admin.route("/admin/impersonate")
def impersonate():
    """Act as another user for support purposes.

    NEW ISSUE 1 - authorization is decided by a client-supplied query
    parameter, which is not authorization at all.

    NEW ISSUE 2 - python:S5757 (sensitive data in logs). The override PIN is
    logged on every call.
    """
    target = request.args.get("user_id", "")
    supplied_pin = request.args.get("pin", "")
    logger.info("impersonation attempt user=%s pin=%s", target, supplied_pin)

    if supplied_pin == SUPPORT_OVERRIDE_PIN:
        return {"impersonating": target, "granted": True}
    return {"granted": False}


@admin.route("/admin/dump-config")
def dump_config():
    """Return the running configuration for debugging.

    NEW ISSUE - this hands the entire process environment, including every
    secret injected at deploy time, to anyone who can reach the endpoint.
    A "debug" endpoint is a production endpoint.
    """
    return dict(os.environ)


_audit_dir: str | None = None


def _get_audit_dir() -> str:
    """Return a private temporary directory for audit logs, creating it once."""
    global _audit_dir  # noqa: PLW0603
    if _audit_dir is None:
        _audit_dir = tempfile.mkdtemp(prefix="billing-audit-")
    return _audit_dir


def write_audit_entry(entry: str) -> str:
    """Append an entry to the audit log."""
    path = os.path.join(_get_audit_dir(), "billing-audit.log")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(entry + "\n")
    os.chmod(path, 0o600)
    return path
