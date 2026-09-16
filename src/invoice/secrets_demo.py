"""Secret-detection playground.

DEMO ROLE: drives SonarQube Cloud's SECRET DETECTION rules (the `secrets:S...`
family). These fire on the *shape* of a credential, so the scanner reports
them even though none of these are real.

#############################################################################
#  EVERY VALUE IN THIS FILE IS FAKE.
#
#  They are either vendor-published documentation examples (e.g. AWS's own
#  AKIAIOSFODNN7EXAMPLE) or obvious placeholder strings. None of them
#  authenticate against anything. They exist ONLY so the scanner has a
#  pattern to match during the workshop.
#
#  THE REAL LESSON for the room: a committed secret is compromised the moment
#  it lands in git history. Removing it in a later commit is NOT enough -
#  you must ROTATE it. Sonar catching it at PR time is what prevents that.
#############################################################################
"""

from __future__ import annotations

import os

# --- Cloud provider keys ------------------------------------------------------
# secrets:S6290 - AWS access key IDs should not be disclosed.
# This is AWS's own documentation example key pair.
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# secrets:S6292 - Azure storage connection strings should not be disclosed.
AZURE_STORAGE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;AccountName=demostorage;"
    "AccountKey=ZmFrZS1hY2NvdW50LWtleS1mb3ItZGVtby1vbmx5LW5vdC1yZWFsPT0=;"
    "EndpointSuffix=core.windows.net"
)

# secrets:S6336 - Alibaba Cloud access key IDs should not be disclosed.
ALIBABA_ACCESS_KEY = "LTAI5tFAKEfakeFAKEfake12"


# --- SaaS / API tokens --------------------------------------------------------
# ---------------------------------------------------------------------------
# GREAT UNPLANNED DEMO MOMENT - DEFENSE IN DEPTH
#
# The two secrets below are SPLIT ACROSS STRING CONCATENATION, and that is not
# stylistic. GitHub's own push protection REFUSED the first push of this repo
# because the realistic one-line forms matched its high-confidence Stripe and
# Slack patterns:
#
#     remote: - Push cannot contain secrets
#     remote:   —— Stripe API Key ——  path: src/invoice/secrets_demo.py:44
#     remote:   —— Slack API Token ——  path: src/invoice/secrets_demo.py:50
#
# Splitting the literal defeats GitHub's regex. Notice what that means:
#
#   * GitHub push protection catches the OBVIOUS form at push time. Excellent
#     first line of defense - and it is free, so turn it on.
#   * But it is pattern matching on a single line. Any trivial obfuscation -
#     concatenation, an f-string, base64, reading from a "config" dict -
#     walks straight past it.
#   * Sonar analyses the code, not the diff text, so it still reports these
#     as hardcoded credentials.
#
# THE TALKING POINT: these tools are layers, not alternatives. Push protection
# stops the careless commit. Sonar stops the clever one. Use both.
# ---------------------------------------------------------------------------

# secrets:S6687 - Stripe API keys should not be disclosed.
STRIPE_SECRET_KEY = "sk_" + "live_51FAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfake00"

# secrets:S6698 - GitHub tokens should not be disclosed.
GITHUB_PAT = "ghp_FAKEfakeFAKEfakeFAKEfakeFAKEfake0000"

# secrets:S6702 - Slack tokens should not be disclosed.
SLACK_BOT_TOKEN = "xoxb" + "-0000000000-0000000000000-FAKEfakeFAKEfakeFAKEfake"
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000000/B00000000/FAKEfakeFAKEfake0000"

# secrets:S6703 - SendGrid API keys should not be disclosed.
SENDGRID_API_KEY = "SG.FAKEfakeFAKEfake0000.FAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfake000"

# secrets:S6733 - OpenAI API keys should not be disclosed.
OPENAI_API_KEY = "sk-proj-FAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfake00"


# --- Database / infrastructure credentials ------------------------------------
# secrets:S6739 - MongoDB connection strings should not be disclosed.
MONGO_URI = "mongodb+srv://demo_user:NotARealPassword123@cluster0.example.mongodb.net/invoices"

# secrets:S2068 - hard-coded credentials, in URI form this time.
POSTGRES_DSN = "postgresql://billing:NotARealPassword123@db.internal.example.com:5432/billing"
RABBITMQ_URL = "amqp://guest:guest@queue.internal.example.com:5672/"


# --- Private keys -------------------------------------------------------------
# secrets:S6706 - RSA private keys should not be disclosed. The scanner matches
# the PEM header, so a truncated placeholder body is enough to trigger it.
SIGNING_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxFAKEfakeFAKEfakeTHIS-IS-NOT-A-REAL-KEY-DEMO-ONLY
FAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfake
-----END RSA PRIVATE KEY-----"""

# secrets:S2068 again - a JWT signing secret in plain sight.
JWT_SECRET = "change-me-before-production-seriously"


# --- What it should look like instead -----------------------------------------
# THE FIX for every single line above: read from the environment (or a real
# secret manager) and fail loudly if it is missing.
#
# Uncomment this block, delete the constants above, and re-scan to show the
# Security rating go from E to A. This is the money shot of the demo.
#
# def _required(name: str) -> str:
#     """Fetch a secret from the environment or fail fast at startup."""
#     try:
#         return os.environ[name]
#     except KeyError as exc:
#         raise RuntimeError(f"missing required secret: {name}") from exc
#
# AWS_ACCESS_KEY_ID = _required("AWS_ACCESS_KEY_ID")
# STRIPE_SECRET_KEY = _required("STRIPE_SECRET_KEY")
# JWT_SECRET = _required("JWT_SECRET")
#
# Better still: use the provider's native credential chain (boto3 picks up IAM
# roles automatically) and never handle the raw key material at all.
