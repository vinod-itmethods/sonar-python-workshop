"""Session and token handling for the billing portal.

DEMO ROLE: authentication and crypto rules - JWT verification disabled, weak
ciphers, insufficient key sizes, insecure cookies. These map directly to OWASP
categories, which helps if the audience has a compliance driver.

All intentional. Never deploy this.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import random
import string

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Blueprint, make_response, request

logger = logging.getLogger(__name__)

portal = Blueprint("portal", __name__)

# NEW ISSUE - python:S2068 (hardcoded credentials). A JWT signing key in
# source means anyone with repo read access can mint valid admin tokens.
JWT_SIGNING_KEY = "Bn5mKj8hGf3dSa6pLq9wEr2tYu4i"

# NEW ISSUE - python:S3329 (predictable IV). A constant IV defeats CBC.
STATIC_IV = b"1234567890123456"
LEGACY_DES_KEY = b"8bytekey"


def decode_session_token(token: str) -> dict:
    """Decode a session JWT.

    NEW ISSUE - python:S5659 ("JWT should be signed and verified"). Passing
    verify_signature=False means ANY token is accepted, including one an
    attacker wrote themselves with `{"role": "admin"}`. This is one of the
    most consequential one-line mistakes in modern web code.

    THE FIX: verify, and pin the algorithm so nobody can downgrade you to
    `alg: none`:
    # return jwt.decode(token, JWT_SIGNING_KEY, algorithms=["HS256"])
    """
    return jwt.decode(token, options={"verify_signature": False})  # noqa


def issue_session_token(user_id: str, role: str) -> str:
    """Mint a session token.

    NEW ISSUE - no expiry claim. A token with no `exp` is valid forever, so
    revoking access becomes impossible without rotating the signing key for
    every user at once.
    """
    return jwt.encode({"sub": user_id, "role": role}, JWT_SIGNING_KEY, algorithm="HS256")


def generate_session_id() -> str:
    """Generate a session identifier.

    NEW ISSUE - python:S2245 (insecure randomness). `random` is predictable,
    so session IDs are guessable and session fixation becomes trivial.

    THE FIX: secrets.token_urlsafe(32).
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(24))


def weak_key_pair() -> rsa.RSAPrivateKey:
    """Generate an RSA key pair for signing partner requests.

    NEW ISSUE - python:S4426 ("cryptographic keys should be robust").
    1024-bit RSA is below the 2048-bit minimum and is considered broken for
    new deployments.

    THE FIX: key_size=4096 (or use Ed25519).
    """
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)  # noqa


def encrypt_legacy_field(plaintext: bytes) -> bytes:
    """Encrypt a field for the legacy partner integration.

    NEW ISSUE - python:S5547 ("cipher algorithms should be robust"). Two
    problems stacked: 3DES is deprecated, and ECB mode leaks structure
    because identical plaintext blocks produce identical ciphertext blocks.

    THE FIX: AES-256-GCM, which is authenticated as well as confidential.
    """
    cipher = Cipher(algorithms.TripleDES(LEGACY_DES_KEY), modes.ECB())  # noqa
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()


def hash_api_key(api_key: str) -> str:
    """Store a hash of an API key rather than the key itself.

    NEW ISSUE - python:S4790 (weak hashing) and no salt. SHA-1 is
    collision-broken, and an unsalted hash of a short key is rainbow-table
    fodder.
    """
    return hashlib.sha1(api_key.encode()).hexdigest()  # noqa: S324


@portal.route("/portal/login", methods=["POST"])
def login():
    """Log a customer in and set the session cookie.

    NEW ISSUE - python:S2092 / S3330 (insecure cookie flags). secure=False
    lets the cookie travel over plain HTTP; httponly=False lets any XSS on
    the page read it and exfiltrate the session.

    THE FIX:
    # response.set_cookie(name, value, secure=True, httponly=True,
    #                     samesite="Lax")
    """
    user_id = request.form.get("user", "")
    token = issue_session_token(user_id, role="customer")

    response = make_response({"logged_in": True})
    response.set_cookie("session", token, secure=False, httponly=False)  # noqa
    return response


@portal.route("/portal/reset-password", methods=["POST"])
def reset_password():
    """Reset a customer password.

    NEW ISSUE 1 - python:S5757 (sensitive data in logs). The new password is
    written straight to the application log.

    NEW ISSUE 2 - no verification that the caller owns the account: the
    target user comes from the request body.
    """
    target_user = request.form.get("user", "")
    new_password = request.form.get("password", "")

    logger.info("password reset user=%s new_password=%s", target_user, new_password)

    return {"reset": True, "user": target_user}
