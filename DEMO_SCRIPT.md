# Demo Runbook — SonarQube Cloud for Python Developers

Target: **45–60 minutes**, single call, developer audience.

Repo: `vinod-itmethods/sonar-python-workshop` · Sonar project: `vinod-itmethods_sonar-python-workshop`

---

## Pre-flight (do this 15 minutes before the call)

- [x] `SONAR_TOKEN` is in GitHub Actions secrets — **done**
- [x] Automatic Analysis is **OFF** in Sonar project settings — **done**
- [x] `main` analysed (baseline exists: 25 vulns, 11% duplication, 17 tests) — **done**
- [x] GitHub App permissions granted, PR decoration verified posting — **done**
- [x] PR #1 open and analysed, gate FAILED / pipeline GREEN — **done**
- [ ] VS Code open on the repo, connected mode active, Sonar panel visible
- [ ] Browser tabs pre-opened: Sonar project overview · Sonar Security tab ·
      GitHub Actions · the demo PR (created but *not* yet discussed)
- [ ] Zoom to ~120% in both editor and browser
- [ ] Have the fix branch ready but unpushed (see Act 4)

---

## Act 1 — The problem, not the tool (5 min)

Don't open Sonar yet. Open `src/invoice/secrets_demo.py` in VS Code.

> "This is a normal-looking Python module. Someone committed it six months ago.
> Count the credentials."

Scroll slowly. Let them react.

> "Here's the thing about a committed secret: it's compromised the moment it
> lands in git history. Deleting it in a later commit does nothing — you have to
> rotate it. So the only fix that actually works is catching it *before* merge."

That frames everything that follows as prevention, not reporting.

**Bonus — a true story, and it's worth telling.** GitHub's push protection
actually *refused* the first push of this repo. It caught the Stripe key and
the Slack token. So we split those two literals across string concatenation
(see the comment block in `secrets_demo.py`) and the push went straight
through.

> "Push protection caught the obvious form. One concatenation defeated it —
> because it's matching patterns on diff text. Sonar analyses the *code*, so it
> still reports both. These are layers, not alternatives: push protection stops
> the careless commit, Sonar stops the clever one."

This lands well because it's real, it happened during setup, and it pre-empts
the "we already have GitHub secret scanning" objection before anyone raises it.

---

## Act 2 — Sonar for IDE, connected mode (10 min)

Still in VS Code. **Open `src/invoice/web.py`.**

Point at the squiggles in the **Problems** panel.

> "These aren't flake8. This is the same analyzer that runs in CI — same rules,
> same quality profile, pulled down from the server."

Click the SSRF finding in `fetch_logo()`. Show the rule description panel.

> "Note what it's telling me: an attacker passes `169.254.169.254` — the cloud
> metadata endpoint — and my own server hands back its IAM credentials."

**Now the key moment.** Explain taint analysis:

> "This finding is special. Sonar traced untrusted input from `request.args`
> all the way to the `requests.get` call. That's dataflow analysis, and it's a
> *server-side* rule — I only see it locally because I'm in connected mode.
> Standalone SonarLint would not show me this."

Live-type something to show real-time feedback:

```python
password = "admin123"
```

Squiggle appears immediately.

> "No save, no commit, no CI. That's the shortest feedback loop you can get."

Delete the line.

---

## Act 3 — AI CodeFix in the IDE (8 min)

Open `src/invoice/discounts.py`, go to `tier_discount()`.

> "Two branches, identical bodies. Sonar rule S1871. Read what it actually
> means: gold customers are getting the silver discount. That's a revenue bug
> that's been in production for months and no test caught it."

Click the lightbulb → **AI CodeFix**.

Show the suggested diff. **Do not accept it instantly.** Read it aloud.

> "It's proposing gold goes to 15%. Now — is 15% right? Sonar doesn't know our
> pricing. It found the bug correctly and it's guessing at the business rule.
> This is the part that still needs me."

Accept the fix. Then run the tests in the terminal:

```bash
pytest tests/test_discounts.py -v
```

`test_gold_tier_discount` **fails**.

> "And there's the real lesson. The test suite was *asserting the bug*. Someone
> wrote a test against the broken behaviour, it went green, everyone moved on.
> Sonar found what the tests were actively protecting."

Fix the test to expect `0.15`. This is a great unscripted moment — let them
watch you update the assertion.

---

## Act 4 — CI, PR decoration, and the bot (12 min)

**PR #1 is already open and analysed:**
<https://github.com/vinod-itmethods/sonar-python-workshop/pull/1>

It adds `src/invoice/reminders.py` plus a `late_fee_for()` function in the
previously-clean `calculator.py`. Open it in the browser, then switch to the
**Actions** tab and open the completed job.

**VERIFIED NUMBERS (measured, not estimated) — what the bot comment says:**

| Condition | Actual | Required | |
|---|---|---|---|
| Coverage on New Code | **21.5%** | ≥ 80% | FAILED |
| Reliability Rating on New Code | **C** | A | FAILED |
| Security Rating on New Code | **E** | A | FAILED |
| Maintainability Rating on New Code | A | A | ok |
| Duplication on New Code | 0.0% | ≤ 3% | ok |

**Quality Gate: FAILED. GitHub Actions job: GREEN.**

Lead with that contradiction — it is the most important slide of the demo:

> "The gate failed. Three conditions red. And the pipeline is green, the merge
> button works, nothing is stopping me. Right now Sonar is *advice*."

Then, if you want to reopen the branch story live instead:

```bash
git checkout -b fix/gold-tier-discount
git add -A && git commit -m "fix: gold tier was getting the silver rate"
git push -u origin fix/gold-tier-discount && gh pr create --fill
```


Walk the workflow while it runs — `.github/workflows/ci.yml` is commented for
exactly this:

1. **Checkout with `fetch-depth: 0`** —
   > "Full history. The scanner reads git blame to decide what counts as *new
   > code* and who wrote it. Shallow clone breaks new-code detection and PR
   > decoration silently. This is the number one misconfiguration I see."
2. **pytest writes the reports** —
   > "Sonar does not run your tests. pytest writes `coverage.xml` and
   > `junit.xml`, and the scanner imports them. Order is mandatory."
3. **`sonarqube-scan-action@v6` reads them**

When the job finishes, refresh the PR. Show all THREE surfaces it posts to:

1. the **SonarCloud Code Analysis** check run — "Quality Gate failed" with each
   failed condition linked straight to the offending measure
2. the **bot comment** from `sonarqubecloud` listing new issues, coverage on new
   code and gate status
3. **GitHub's own Security tab** — Sonar also exports SARIF into GitHub Code
   Scanning, so findings show up as native GitHub alerts with inline PR
   annotations. There are currently **4** on this PR (`S2068` hardcoded
   credential, `S2245` insecure random, `S4790` weak hash, `secrets:S7552`).

That third one is worth pausing on for a security-minded audience:

> "These are also landing in GitHub's native Security tab as code scanning
> alerts. So if your team already lives in that tab, Sonar meets them there —
> you don't have to send everyone to a second dashboard."

> "Nobody had to go look at a dashboard. The analysis came to the code review."

Click through to Sonar. Show the **Pull Request** view — new code only.

> "This is Clean as You Code. It's not asking me to fix the 200 issues already
> in this repo. It's asking: *is the code you just wrote clean?* That's a
> standard a team can actually hold."

**Then show the gate as a blocker.** Point at the `sonar.qualitygate.wait`
toggle in `ci.yml`:

> "Flip this to `true` and add a branch protection rule, and a failed gate stops
> the merge. That's the difference between a dashboard and a control."

---

## Act 4b — The big PR: volume, duplication, and the Remediation Agent (8 min)

**PR #3** — <https://github.com/vinod-itmethods/sonar-python-workshop/pull/3>

858 new lines across 5 new modules. Use this one when you want scale, and when
you want new code to explore in the IDE **after merging**.

**VERIFIED gate result — four conditions failing:**

| Condition | Actual | Required |
|---|---|---|
| Coverage on New Code | **7.7%** | ≥ 80% |
| Duplication on New Code | **15.9%** | ≤ 3% |
| Reliability Rating on New Code | **C** | A |
| Security Rating on New Code | **E** | A |

**Pipeline: still GREEN.**

This PR trips **duplication**, which PR #1 could not — the four 45-line
exporters in `reporting.py` are what do it. So show duplication here, not on
PR #1.

The file to open for maximum effect is `src/invoice/admin_console.py`:

> "Three separate routes to remote code execution in one 125-line file.
> `eval` on request data. `pickle.loads` on request data. `os.system` with
> string interpolation. Sonar rates all three Blocker."

### The Remediation Agent — check whether you want to show this

The bot comment on this PR carries a **"Fix automatically"** checkbox:

> 🛠️ **Remediation Agent ready** — Fix automatically
> *Creates a separate PR with fixes for eligible issues*

Ticking it makes Sonar open a **new PR containing the fixes**. That is a
stronger story than per-issue AI CodeFix, because it is agentic remediation at
PR scale rather than one lightbulb at a time.

**Decide in advance whether to tick it live.** Two risks worth knowing:

- It generates a real PR against this repo. Fine here, but do not tick it by
  reflex if you have reset the repo to a known state for the session.
- Many issues in this PR are *architecturally* wrong, not typo-wrong. `eval`
  on user input has no local fix — the endpoint should not exist. Expect the
  agent to fix the mechanical ones (MD5, `hmac.compare_digest`, cookie flags,
  bare `except`) and leave the hard ones. **That is a good outcome to narrate
  honestly** rather than hide:

> "It fixed the mechanical ones. It did not rewrite the admin console, because
> the fix there isn't a line change — the endpoint shouldn't exist. That's the
> real boundary: agents are very good at the known-pattern fixes, and the
> judgement calls still come back to you."

If you would rather not generate PRs live, just point at the checkbox and
describe it.

### Merging, for the IDE segment

Merge PR #3 before the IDE portion if you want a large body of freshly-merged
code to explore in connected mode:

```bash
gh pr merge 3 --squash
git checkout main && git pull
```

After merging, `main` carries all 5 new modules, so opening any of them in VS
Code shows real findings immediately — including the taint-analysis issues that
only appear in connected mode.

---

## Act 5 — The full picture in the UI (10 min)

Go to the project overview, `main` branch.

**Security tab** — the headline numbers.

> "Blockers: hardcoded credentials, pickle deserialization, SQL injection."

Open the pickle RCE in `web.py`. Show the taint path visualisation.

**Security Hotspots tab** — heads up: **this tab is currently EMPTY (0 hotspots).**

Under SonarQube Cloud's current Clean Code taxonomy, the rules that used to be
hotspots here — weak hash (`S4790`), insecure PRNG (`S2245`), debug mode
(`S4507`), publicly writable tmp dir (`S5443`) — are all reported as
**Vulnerabilities** instead. They *are* being found; they're just on the
Security tab, not this one.

So **do not open this tab expecting content.** Either skip it, or open it
deliberately and explain the distinction, which is still worth teaching:

> "Sonar used to split these out as *hotspots* — security-sensitive code
> needing a human judgement call rather than a definite bug. That taxonomy has
> been folded into the main issue list. The judgement call still exists though:
> the SHA-1 checksum in `crypto_utils.py` is a disaster if it's hashing
> passwords, and completely fine if it's a cache key."

Then demo the triage workflow on any **Vulnerability** instead — set one to
**Won't Fix** / **Safe** with a justification and show it disappear.

> "And because I'm in connected mode, that triage syncs down to my IDE. I won't
> see it locally again. Triage once, not once per developer."

**Coverage tab** — sort ascending. `legacy_report.py` at 0%.

> "27% overall. Nobody's fixing that this quarter and the gate isn't asking them
> to — it only enforces coverage *on new code*."

**Duplications tab** — `legacy_report.py`, three near-identical functions.

**AI CodeFix in the UI** — pick an issue and run it from the browser.

> "Same capability, different entry point. Fix it here, or fix it in the IDE."

---

## Act 6 — Live toggles, if there's time (5 min)

Pick one. Each takes a commit and a CI run.

| Toggle | Where | What they see |
|---|---|---|
| Comment out `sonar.exclusions` | `sonar-project.properties` | Issue count jumps — generated protobuf floods in |
| Blank out `sonar.python.coverage.reportPaths` | same file | Coverage collapses to 0% |
| Uncomment `sonar.inclusions` | same file | `auth.py` vulnerabilities *vanish* — cautionary tale |
| `qualitygate.wait=true` | `ci.yml` | Job fails on gate failure |

The exclusions one lands best — it makes the config feel consequential.

---

## Act 7 — Close: Claude + Vortex (5 min)

> "Sonar tells me *what's* wrong, precisely, with a rule and a dataflow path.
> The next question is who does the work."

Open `legacy_report.py`, hand Claude the duplication finding, let it collapse
the three functions into one helper and write the missing tests.

> "Sonar is the ground truth. The agent is the labour. And because the gate runs
> on every PR, agent-written code is held to exactly the same standard as
> human-written code — which is the only way you can safely let an agent write
> at volume."

Then transition to Vortex.

---

## Questions you will get

**"Does it run our tests?"**
No. Your test runner writes coverage and JUnit XML; Sonar imports them.

**"Will it flood us with issues on our existing codebase?"**
It'll *report* them, but the quality gate only enforces new code. That's the
whole point of Clean as You Code.

**"Can we turn rules off?"**
Yes — quality profiles, server-side, per-project. And issues can be triaged as
*Won't Fix* / *Safe*, which syncs to every developer's IDE.

**"Is AI CodeFix sending our code to a model?"**
Yes — it's a cloud service. Point them at Sonar's data-handling docs; it's an
org-level setting you can leave off.

**"How is this different from GitHub Advanced Security / Snyk?"**
Sonar covers quality *and* security in one gate, with the IDE loop and the
new-code model. Don't oversell — if they already have SAST, the differentiator
is Clean as You Code and the IDE feedback loop, not raw rule count.

**"What about monorepos?"**
`sonar.inclusions` / multiple projects per repo. Show the inclusions toggle.

---

## Reset between demos

```bash
git checkout main && git reset --hard origin/main
git branch -D fix/gold-tier-discount
git push origin --delete fix/gold-tier-discount
```

Close the PR without merging so `main` stays dirty for the next run.
