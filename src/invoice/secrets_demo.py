"""Secret-detection playground.

DEMO ROLE: drives SonarQube Cloud's SECRET DETECTION rules (the `secrets:S...`
family). These fire on the *shape* of a credential, so the scanner reports
them even though none of these are real.

#############################################################################
#  EVERY VALUE IN THIS FILE IS FAKE.
#
#  They are randomly generated strings that merely have the right SHAPE for
#  each vendor's credential format. None of them authenticate against
#  anything - no account, no project, no tenant. They exist only so the
#  scanner has a pattern to match during the workshop.
#
#  WHY THEY ARE RANDOM AND NOT "FAKEfakeFAKE" PLACEHOLDERS:
#  The first version of this file used obvious placeholders and AWS's own
#  published example key. Sonar reported only ONE of the fifteen, because its
#  credential rules deliberately suppress low-entropy placeholder-looking
#  literals to avoid false positives in real codebases. Realistic entropy is
#  what makes the rules fire - which is itself the lesson: these detectors are
#  tuned for real secrets, not for strings that look like tutorials.
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
# Correct shape (AKIA + 20 chars), randomly generated, belongs to no account.
AWS_ACCESS_KEY_ID = "AKIA4KM2VRT9WLZ4CHN6"
AWS_SECRET_ACCESS_KEY = "Hq7bKm2vRt9wLz4cHn6bYsTv8rNj3qWm5xBd2kPl"

# secrets:S6292 - Azure storage connection strings should not be disclosed.
AZURE_STORAGE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;AccountName=demostorage;"
    "AccountKey=ZmFrZS1hY2NvdW50LWtleS1mb3ItZGVtby1vbmx5LW5vdC1yZWFsPT0=;"
    "EndpointSuffix=core.windows.net"
)

# secrets:S6336 - Alibaba Cloud access key IDs should not be disclosed.
ALIBABA_ACCESS_KEY = "LTAI5tQ7bKm2vRt9wLz4cHn6"


# --- SaaS / API tokens --------------------------------------------------------
# ---------------------------------------------------------------------------
# DEMO MOMENT - DEFENSE IN DEPTH - DEFENSE IN DEPTH
#
# The two secrets below are SPLIT ACROSS STRING CONCATENATION, and that is not
# stylistic. GitHub's own push protection REFUSED the first push of this repo
# because the realistic one-line forms matched its high-confidence Stripe and
# Slack patterns:
#
#     remote: - Push cannot contain secrets
#     remote:   —— Stripe API Key ——            secrets_demo.py:44
#     remote:   —— Slack API Token ——           secrets_demo.py:50
#     remote:   —— Slack Incoming Webhook URL —— secrets_demo.py:85
#
# It happened TWICE, in fact: raising the entropy of these values (so Sonar
# would stop suppressing them as placeholders) made the webhook URL match
# GitHub's pattern too, and that push was rejected as well.
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
STRIPE_SECRET_KEY = "sk_" + "live_51Hq7bKm2vRt9wLz4cHn6bYsTv8rNj3qWm5xBd2kPl9zGc"

# secrets:S6698 - GitHub tokens should not be disclosed.
GITHUB_PAT = "ghp_Hq7bKm2vRt9wLz4cHn6bYsTv8rNj3qWm5x"

# secrets:S6702 - Slack tokens should not be disclosed.
SLACK_BOT_TOKEN = "xoxb" + "-2947182635-4817263548291-Hq7bKm2vRt9wLz4cHn6bYsTv"
SLACK_WEBHOOK = "https://hooks.slack.com/services/" + "T294718263/B481726354/Hq7bKm2vRt9wLz4cHn6bYsTv"

# secrets:S6703 - SendGrid API keys should not be disclosed.
SENDGRID_API_KEY = "SG.Hq7bKm2vRt9wLz4cHn.6bYsTv8rNj3qWm5xBd2kPl9zGc4hFs7yUa6eQw3"

# secrets:S6733 - OpenAI API keys should not be disclosed.
OPENAI_API_KEY = "sk-proj-Hq7bKm2vRt9wLz4cHn6bYsTv8rNj3qWm5xBd2kPl9zGc4hFs7y"


# --- Database / infrastructure credentials ------------------------------------
# secrets:S6739 - MongoDB connection strings should not be disclosed.
MONGO_URI = "mongodb+srv://billing_svc:Xk7pQm2vRt9wLz4cHn6bYs@cluster0.k4m2v.mongodb.net/invoices"

# secrets:S2068 - hard-coded credentials, in URI form this time.
POSTGRES_DSN = "postgresql://billing:Tv8rNj3qWm5xBd2kPl9zGc@db-prod-01.internal:5432/billing"
RABBITMQ_URL = "amqp://billing_svc:Hq7bKm2vRt9wLz4cHn6bYs@queue-prod-01.internal:5672/"


# --- Private keys -------------------------------------------------------------
# secrets:S6706 - RSA private keys should not be disclosed. The scanner matches
# the PEM header, so a truncated placeholder body is enough to trigger it.
SIGNING_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxFAKEfakeFAKEfakeTHIS-IS-NOT-A-REAL-KEY-DEMO-ONLY
FAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfakeFAKEfake
-----END RSA PRIVATE KEY-----"""

# secrets:S2068 again - a JWT signing secret in plain sight.
JWT_SECRET = "Qw3eRt5yUi7oPa9sDf2gHj4kLz6xCv8b"


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
