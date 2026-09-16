# Sonar Python Workshop

A deliberately flawed Python project for demonstrating **SonarQube Cloud** end to end:
CI analysis, PR decoration, quality gates, coverage import, AI CodeFix, and
Sonar for IDE connected mode.

> ### ⚠️ This repository contains intentional vulnerabilities and fake secrets
>
> Every security issue, hardcoded credential, and bug in `src/` is **deliberate**
> and exists so the scanner has something to find during a workshop.
>
> - **All credentials are fake** — vendor documentation examples (e.g. AWS's own
>   `AKIAIOSFODNN7EXAMPLE`) or obvious placeholders. None authenticate against
>   anything.
> - **Do not deploy this.** The Flask app in `web.py` is remote-code-execution
>   vulnerable by design and is never served.
> - **Do not copy these patterns.** Each issue carries a comment naming its
>   Sonar rule key and showing the correct fix.

---

## Project key facts

| | |
|---|---|
| **GitHub repo** | `vinod-org/sonar-python-workshop` |
| **Sonar organization** | `itmethods-inc` |
| **Sonar project key** | `itmethods-inc_sonar-python-workshop` |
| **Scanner** | `SonarSource/sonarqube-scan-action@v5` |
| **Language** | Python 3.11+ |
| **Tests** | 17 passing, ~27% total coverage (by design) |

---

## What each file is for

Every module exists to light up a specific part of the SonarQube UI.

| File | Demo role | Sonar tab it feeds |
|---|---|---|
| `src/invoice/calculator.py` | The **clean** baseline — 100% covered | Coverage (green) |
| `src/invoice/discounts.py` | Logic bugs + high complexity — **best AI CodeFix target** | Issues / Maintainability |
| `src/invoice/auth.py` | Hardcoded creds, weak hash, SQLi, command injection | **Security** |
| `src/invoice/secrets_demo.py` | ~15 fake secrets of every vendor type | **Security** (secret detection) |
| `src/invoice/web.py` | XSS, SSRF, path traversal, pickle RCE, open redirect | **Security** (taint analysis) |
| `src/invoice/crypto_utils.py` | Weak crypto, insecure PRNG, broken TLS | **Security Hotspots** |
| `src/invoice/reliability.py` | Resource leak, None deref, mutable default, unreachable code | **Bugs / Reliability** |
| `src/invoice/legacy_report.py` | Triplicated code, **zero tests** | **Duplications + Coverage** |
| `src/invoice/generated/models_pb2.py` | Proves `sonar.exclusions` works | *(nothing — it's excluded)* |

The two most important files to read out loud are heavily commented:

- **`sonar-project.properties`** — every setting explained, including the
  coverage/test report paths and `sonar.exclusions` vs `sonar.coverage.exclusions`
- **`.github/workflows/ci.yml`** — the CI flow, why `fetch-depth: 0` is mandatory,
  and how to turn the quality gate into a hard merge blocker

Both contain **DEMO TOGGLE** comments: lines you can comment/uncomment live to
show a metric visibly change.

---

## One-time setup

### 1. Import the project into SonarQube Cloud

1. Go to <https://sonarcloud.io> → **+** → **Analyze new project**
2. Pick the `itmethods-inc` organization, then select `sonar-python-workshop`
3. This installs the **SonarQube Cloud GitHub App** on the repo — required for
   PR decoration. A token alone is not enough.

### 2. Switch off Automatic Analysis ← *don't skip this*

**Project Settings → Analysis Method → disable "Automatic Analysis"**

CI-based analysis and Automatic Analysis are mutually exclusive. Leaving both on
makes the CI scan fail with *"you are running CI analysis while Automatic
Analysis is enabled."* This is the most common first-run failure.

### 3. Add the token to GitHub Actions

1. SonarQube Cloud → **My Account → Security** → generate a token
2. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**
3. Name it exactly **`SONAR_TOKEN`**

### 4. Set the New Code definition

**Project Settings → New Code → "Previous version"** or **"Number of days: 30"**.
This is what Clean as You Code measures against.

### 5. Optional — make the gate block merges

1. In `ci.yml`, change `-Dsonar.qualitygate.wait=false` to `true`
2. GitHub → **Settings → Branches → add rule for `main`** → require the
   **SonarQube Cloud** status check to pass

---

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
pytest --cov=src/invoice --cov-report=xml:coverage.xml --cov-report=term-missing --junitxml=junit.xml
```

**Order matters.** `pytest` *writes* `coverage.xml` and `junit.xml`; the scanner
only *reads* them. Sonar never runs your tests. If the scan runs first, you get
0% coverage and no test count.

To scan from your laptop (CI normally does this):

```bash
SONAR_TOKEN=your_token npx sonarqube-scanner
```

---

## Sonar for IDE — connected mode (VS Code)

`.vscode/` is committed, so this is nearly automatic.

1. Open the repo — VS Code offers to install **SonarQube for IDE**; accept
2. **Command Palette → "SonarQube: Add SonarQube Cloud Connection"**
3. Connection ID must be **`itmethods-inc`** to match `.vscode/settings.json`
4. Paste a user token (VS Code stores it in the OS keychain, never in the repo)
5. Reload — the project binding in `settings.json` picks up automatically

**Why connected mode matters, and what to say:** standalone mode gives you local
rules only. Connected mode pulls the server's quality profile, hides issues
already triaged as *Won't Fix*, surfaces **taint-analysis issues** (the injection
findings in `web.py` — these are server-side rules you cannot get locally), and
enables **AI CodeFix** in the editor.

Open `src/invoice/web.py` in connected mode — the injection findings appearing
locally is the most convincing single moment of the demo.

---

## Demo runbook

See **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** for the full timed walkthrough with
talking points, the exact PR to open, and the AI CodeFix sequence.

---

## The best AI CodeFix targets

Ranked by how well they demo:

1. **`discounts.py` → `tier_discount()`** — `python:S1871`, two branches with
   identical implementations. Gold customers silently get the silver rate. The
   fix is a real behaviour change a human must approve, *and* accepting it turns
   `test_gold_tier_discount` red — which proves the test suite was protecting
   the bug. Best single demo in the repo.
2. **`secrets_demo.py`** — any hardcoded secret. The fix (env var + fail-fast)
   is clean and obviously correct.
3. **`web.py` → `render_invoice()`** — reflected XSS. Sonar draws the numbered
   taint path from `request.args` to the response.
4. **`reliability.py` → `sync_to_ledger()`** — mutable default argument. Always
   gets a reaction from a Python audience.
5. **`legacy_report.py`** — ask Claude (not AI CodeFix) to collapse the three
   duplicated functions into one helper. Good closing act.

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| `Project not found` | `sonar.projectKey` doesn't match the key Sonar created on import |
| Coverage shows 0% | `coverage.xml` missing, or scan ran before pytest |
| No test count shown | `junit.xml` missing — coverage and test reports are separate files |
| "Automatic Analysis is enabled" | Turn it off (setup step 2) |
| No PR comment | GitHub App not installed, or shallow clone (`fetch-depth` not `0`) |
| New Code shows everything | New Code definition unset, or missing git history |
