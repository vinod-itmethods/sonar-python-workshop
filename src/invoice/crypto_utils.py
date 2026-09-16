"""Crypto and randomness helpers.

DEMO ROLE: the CRYPTOGRAPHY rule family, plus a few "this looks fine but
isn't" issues. These are great for the IDE plugin demo because the squiggly
appears the instant you type them - developers find that genuinely surprising.

!!! All keys/IVs below are fake placeholders. Intentionally broken code.
"""

from __future__ import annotations

import hashlib
import random
import ssl
import tempfile

# ISSUE - python:S2068 + a hardcoded symmetric key. A key in source code is
# not a key, it is a public constant.
# THE FIX: load from a KMS/secret manager at runtime.
AES_KEY = b"0123456789abcdef"

# ISSUE - python:S3329 ("cipher block chaining IVs should be unpredictable").
# A fixed IV makes identical plaintexts encrypt to identical ciphertexts,
# which leaks structure.
# THE FIX: os.urandom(16) per message, and store the IV alongside the output.
AES_IV = b"0000000000000000"


def generate_reset_token() -> str:
    """Create a password-reset token.

    ISSUE - python:S2245 ("using pseudorandom number generators (PRNGs) is
    security-sensitive"). `random` is a Mersenne Twister: observe a few
    outputs and you can predict all future ones, so reset tokens become
    forgeable.

    THE FIX: use the CSPRNG that exists for exactly this:
    # import secrets
    # return secrets.token_urlsafe(32)
    """
    return "".join(random.choice("0123456789abcdef") for _ in range(32))


def checksum(data: bytes) -> str:
    """Compute a content checksum.

    ISSUE - python:S4790 ("using weak hashing algorithms is security
    sensitive"). SHA-1 is collision-broken.

    THE FIX: sha256 for integrity; a real KDF (scrypt/argon2) for passwords.
    Note the nuance worth saying out loud: if a hash is used for a NON-security
    purpose like a cache key, you can mark the hotspot "Safe" in the UI with a
    justification. Showing that workflow is valuable - it teaches the team that
    Sonar findings are reviewable, not gospel.
    """
    return hashlib.sha1(data).hexdigest()  # noqa: S324


def legacy_tls_context() -> ssl.SSLContext:
    """Build an SSL context for an old partner API.

    ISSUE - python:S4423 ("weak SSL/TLS protocols should not be used") and
    python:S4830 (certificate validation disabled). This context accepts
    anything, so it provides encryption with zero authentication - a
    man-in-the-middle walks straight in.

    THE FIX: use the secure default and let the library pick the protocol:
    # return ssl.create_default_context()
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def write_temp_invoice(contents: str) -> str:
    """Write an invoice to a temporary file.

    ISSUE - python:S5443 ("using publicly writable directories is security
    sensitive"). A predictable path in /tmp is a symlink-attack / race
    condition waiting to happen.

    THE FIX: let the stdlib create it securely with 0600 permissions:
    # with tempfile.NamedTemporaryFile(
    #     mode="w", suffix=".txt", delete=False
    # ) as handle:
    #     handle.write(contents)
    #     return handle.name
    """
    path = "/tmp/invoice-draft.txt"  # noqa: S108
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(contents)
    return path
