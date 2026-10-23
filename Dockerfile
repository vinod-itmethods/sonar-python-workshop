# Container image for the invoice billing demo.
#
# DEMO ROLE: gives SonarQube Cloud's CONTAINER SCANNING something real to find.
#
# The base image is pinned to an OLD Debian 11 (bullseye) Python release ON
# PURPOSE. A current base image would report almost nothing, which makes for a
# dull demo. This one carries a genuine backlog of OS-level CVEs.
#
# Talking point: this is the part of your attack surface that code analysis
# CANNOT see. Your Python might be spotless and your image still ships a
# vulnerable OpenSSL. Container scanning and code scanning answer different
# questions.
#
# Base OS support at the time of writing (beta): RHEL, Debian 11+, Ubuntu,
# Alpine. Distroless, Wolfi/Chainguard and BusyBox images are NOT yet covered.
FROM python:3.9-slim-bullseye

# Deliberately NOT running as root would be the correct practice. We stay root
# so the image also demonstrates a Dockerfile-level finding.
WORKDIR /app

# Install the app's runtime dependencies. Pinning is loose on purpose so the
# SBOM contains a realistic spread of packages for Sonar to match against.
COPY requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt

COPY src/ /app/src/
COPY pyproject.toml /app/pyproject.toml

ENV PYTHONPATH=/app/src

# The Flask app in src/invoice/web.py is intentionally vulnerable and must
# never actually be served. This CMD exists so the image has an entrypoint;
# it prints a refusal rather than starting anything.
CMD ["python", "-c", "print('This demo image is not meant to be run. See README.')"]
