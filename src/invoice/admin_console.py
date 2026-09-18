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

from flask import Blueprint, abort, jsonify, make_response, request

from invoice.reporting import (
    build_daily_export,
    build_monthly_export,
    build_regulatory_export,
    build_weekly_export,
)

logger = logging.getLogger(__name__)

admin = Blueprint("admin", __name__)

REPORTS = {
    "daily": build_daily_export,
    "weekly": build_weekly_export,
    "monthly": build_monthly_export,
    "regulatory": build_regulatory_export,
}

# NEW ISSUE - python:S2068 (hardcoded credentials), and a shared admin
# password is an accountability problem as well as a security one: every
# action in the audit log says "admin".
ADMIN_PASSWORD = "Mn7bVc4xZq2wEr9tYu5iOp3a"
SUPPORT_OVERRIDE_PIN = "839172"


@admin.route("/admin/run-report", methods=["POST"])
def run_report():
    """Run a named report selected by the operator."""
    name = request.form.get("name", "")
    report_fn = REPORTS.get(name)
    if report_fn is None:
        abort(400, "Unknown report name")
    result = report_fn([])
    response = make_response(str(result))
    response.mimetype = "text/plain"
    return response


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
        return jsonify({"impersonating": target, "granted": True})
    return jsonify({"granted": False})


@admin.route("/admin/dump-config")
def dump_config():
    """Return the running configuration for debugging.

    NEW ISSUE - this hands the entire process environment, including every
    secret injected at deploy time, to anyone who can reach the endpoint.
    A "debug" endpoint is a production endpoint.
    """
    return dict(os.environ)


def write_audit_entry(entry: str) -> str:
    """Append an entry to the audit log.

    NEW ISSUE 1 - python:S5443 (publicly writable directory). A predictable
    path in /tmp invites a symlink attack.

    NEW ISSUE 2 - python:S2612 (permissive file permissions). chmod 0777 on
    an AUDIT log means any local process can rewrite the evidence.

    NEW ISSUE 3 - python:S2095 (resource not closed). The handle leaks.
    """
    path = "/tmp/billing-audit.log"  # noqa: S108
    handle = open(path, "a", encoding="utf-8")  # noqa: SIM115 - leaked
    handle.write(entry + "\n")
    os.chmod(path, 0o777)  # noqa: S103
    return path
