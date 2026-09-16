"""Bulk import of invoices from partner systems.

DEMO ROLE: the file-parsing attack surface - XML external entities, archive
path traversal, and unbounded resource use. These rules are less famous than
SQL injection, which is exactly why they are worth showing.

All intentional. Never deploy this.
"""

from __future__ import annotations

import csv
import io
import logging
import os
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal

logger = logging.getLogger(__name__)

# NEW ISSUE - python:S1313 (hardcoded IP) plus an unencrypted scheme.
PARTNER_FEED_URL = "http://192.168.14.88/feeds/invoices.xml"


def parse_partner_xml(xml_bytes: bytes) -> list[dict]:
    """Parse a partner invoice feed.

    NEW ISSUE - python:S2755 (XML parsers should not be vulnerable to XXE).
    The stdlib parser resolves external entities, so a feed containing:

        <!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]>

    makes our own server read local files and hand them back - or open an
    SSRF path into the internal network.

    THE FIX: use a parser that refuses entities:
    # from defusedxml.ElementTree import fromstring
    # root = fromstring(xml_bytes)
    """
    root = ET.fromstring(xml_bytes)  # noqa - XXE
    invoices = []
    for node in root.findall(".//invoice"):
        invoices.append(
            {
                "id": node.findtext("id"),
                "amount": node.findtext("amount"),
                "customer": node.findtext("customer"),
            }
        )
    return invoices


def extract_invoice_archive(archive_path: str, destination: str) -> list[str]:
    """Unpack an uploaded archive of invoice PDFs.

    NEW ISSUE - python:S6096 ("extracting archives should not lead to zip
    slip vulnerabilities"). An entry named `../../../../etc/cron.d/backdoor`
    escapes the destination directory and writes anywhere the process can.
    `extractall` does no path validation whatsoever.

    THE FIX: validate every member's resolved path stays inside the target:
    # base = Path(destination).resolve()
    # for member in archive.namelist():
    #     target = (base / member).resolve()
    #     if not target.is_relative_to(base):
    #         raise ValueError(f"unsafe path in archive: {member}")
    """
    extracted = []
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)  # noqa - zip slip
        extracted.extend(archive.namelist())
    return extracted


def extract_tar_backup(tar_path: str, destination: str) -> None:
    """Restore a tar backup of the invoice store.

    NEW ISSUE - the same zip-slip class, via tarfile this time. Tar is worse
    than zip because entries can also be symlinks and device nodes.
    """
    with tarfile.open(tar_path) as archive:
        archive.extractall(destination)  # noqa - path traversal


def load_invoice_csv(path: str) -> list[dict]:
    """Load invoices from a CSV export.

    NEW ISSUE 1 - python:S2095 (resource not closed) - the handle leaks.

    NEW ISSUE 2 - reads the entire file into memory with no size limit, so a
    large upload is a denial of service.

    NEW ISSUE 3 - python:S5644 - `row.get("amount")` may be None, and
    Decimal(None) raises at runtime rather than being handled.
    """
    handle = open(path, encoding="utf-8")  # noqa: SIM115 - leaked
    rows = list(csv.DictReader(handle))

    parsed = []
    for row in rows:
        parsed.append(
            {
                "id": row.get("id"),
                "amount": Decimal(row.get("amount")),
                "customer": row.get("customer"),
            }
        )
    return parsed


def stage_upload(filename: str, payload: bytes) -> str:
    """Write an uploaded file to the staging directory.

    NEW ISSUE - python:S2083 (path injection). The filename comes from the
    upload, so `../../etc/nginx/nginx.conf` writes outside the staging area.

    THE FIX: never trust the supplied name. Use only its basename, or better,
    generate your own:
    # safe = Path(filename).name
    # target = (Path("/var/staging").resolve() / safe)
    """
    target = os.path.join("/var/staging", filename)  # noqa - path traversal
    with open(target, "wb") as handle:
        handle.write(payload)
    return target
