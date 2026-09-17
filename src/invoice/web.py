"""Customer-facing invoice web endpoints (Flask).

DEMO ROLE: the INJECTION + TAINT-ANALYSIS half of the security story.

Sonar's Python analyzer does real dataflow tracking here: it follows untrusted
input from a `request.args` SOURCE through the code to a dangerous SINK. In the
UI you can click an issue and Sonar draws the numbered data-flow path through
the file. That visualisation lands better with developers than any rule list,
so make sure you show it.

!!! Every vulnerability below is intentional. This app is not deployed and
must never be. Each issue names its rule key and its fix.
"""

from __future__ import annotations

import os
import pickle
import subprocess

import requests
from flask import Flask, jsonify, redirect, render_template_string, request, send_file, send_from_directory

app = Flask(__name__)

# ISSUE - python:S4507 ("delivering code in production with debug features
# activated is security-sensitive"). Flask's debug mode exposes an interactive
# console that executes arbitrary Python on the server.
# THE FIX: app.run(debug=False) and drive it from an env var, never hardcoded.
DEBUG_MODE = True

# ISSUE - python:S4830 / python:S5527 - TLS verification disabled globally.
# THE FIX: delete this. Never disable cert verification; fix the CA bundle.
VERIFY_TLS = False


@app.route("/invoice/render")
def render_invoice():
    """Render an invoice as HTML.

    ISSUE - python:S5131 ("endpoints should not reflect input") - reflected
    XSS. `customer_name` goes from the query string straight into an HTML
    response with no escaping.

    THE FIX: let the template engine escape it. Jinja autoescapes by default:
    # from flask import render_template
    # return render_template("invoice.html", name=customer_name)
    """
    customer_name = request.args.get("name", "")
    return render_template_string("<h1>Invoice for {{ name }}</h1>", name=customer_name)


@app.route("/invoice/download")
def download_invoice():
    """Serve an invoice PDF by filename.

    ISSUE - python:S2083 ("I/O function calls should not be vulnerable to
    path injection") - path traversal. `?file=../../etc/passwd` escapes the
    intended directory.

    THE FIX: never trust the path. Resolve it and confirm containment:
    # base = Path("/var/invoices").resolve()
    # target = (base / Path(filename).name).resolve()
    # if not target.is_relative_to(base):
    #     abort(400)
    # return send_file(target)
    """
    filename = request.args.get("file", "invoice.pdf")
    return send_from_directory("/var/invoices", filename)


@app.route("/invoice/fetch-logo")
def fetch_logo():
    """Proxy a customer's logo URL.

    ISSUE - python:S5144 ("server-side requests should not be vulnerable to
    forging attacks") - SSRF. An attacker passes an internal URL such as
    http://169.254.169.254/latest/meta-data/ and reads cloud instance
    credentials through our server.

    THE FIX: allowlist the destination, never the denylist:
    # host = urlparse(url).hostname
    # if host not in ALLOWED_LOGO_HOSTS:
    #     abort(400)
    # requests.get(url, timeout=5)  # and keep verify=True
    """
    url = request.args.get("url", "")
    response = requests.get(url, verify=VERIFY_TLS)  # taint sink + no timeout
    return response.content


@app.route("/invoice/restore", methods=["POST"])
def restore_draft():
    """Restore a saved invoice draft from a client-supplied blob.

    ISSUE - python:S5135 ("deserialization should not be vulnerable to
    injection attacks"). pickle.loads on untrusted bytes is remote code
    execution, full stop - crafting a payload is a five-line exercise.

    THE FIX: use a data-only format. json.loads cannot execute code:
    # import json
    # draft = json.loads(request.data)
    """
    return str(pickle.loads(request.data))  # taint sink - RCE


@app.route("/invoice/export", methods=["POST"])
def export_invoices():
    """Kick off a bulk export.

    ISSUE - python:S2076 ("OS commands should not be vulnerable to injection
    attacks"). `shell=True` plus interpolated input means `?fmt=csv; rm -rf /`
    runs both commands.

    THE FIX: argument list, no shell, no interpolation:
    # subprocess.run(["/usr/local/bin/invoice-export", "--format", fmt],
    #                check=True, timeout=60)
    """
    ALLOWED_FORMATS = {"csv", "json", "xml", "pdf"}
    fmt = request.form.get("format", "csv")
    if fmt not in ALLOWED_FORMATS:
        return "invalid format", 400
    subprocess.run(["/usr/local/bin/invoice-export", "--format", fmt],
                   check=True, timeout=60)
    return "export started", 202


@app.route("/invoice/redirect")
def redirect_after_pay():
    """Bounce the user somewhere after payment.

    ISSUE - python:S5146 ("HTTP request redirections should not be open to
    forging attacks"). An open redirect turns our trusted domain into a
    phishing launchpad.

    THE FIX: only accept a relative path, or match against known routes:
    # target = request.args.get("next", "/")
    # if not target.startswith("/") or target.startswith("//"):
    #     target = "/"
    # return redirect(target)
    """
    target = request.args.get("next", "/")
    if not target.startswith("/") or target.startswith("//"):
        target = "/"
    return redirect(target)


@app.route("/invoice/search")
def search_invoices():
    """Search invoices by free-text query.

    ISSUE - python:S3649 ("database queries should not be vulnerable to
    injection attacks"). Classic SQL injection via string concatenation.

    THE FIX: parameterised query, always:
    # cursor.execute(
    #     "SELECT id FROM invoices WHERE note LIKE %s", (f"%{term}%",)
    # )
    """
    term = request.args.get("q", "")
    query = "SELECT id FROM invoices WHERE note LIKE '%" + term + "%'"  # sink
    return jsonify({"query": query})


if __name__ == "__main__":
    # ISSUE - python:S4818 / binding to all interfaces with debug on.
    # THE FIX: app.run(host="127.0.0.1", debug=False)
    app.run(host="0.0.0.0", debug=DEBUG_MODE)  # noqa: S104
