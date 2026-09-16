# Demo Runbook — SonarQube Cloud for Python Developers

Target: **45–60 minutes**, single call, developer audience.

Repo: `vinod-itmethods/sonar-python-workshop` · Sonar project: `vinod-itmethods_sonar-python-workshop`

---

## Pre-flight (do this 15 minutes before the call)

- [ ] `SONAR_TOKEN` is in GitHub Actions secrets
- [ ] Automatic Analysis is **OFF** in Sonar project settings
- [ ] One CI run has already completed on `main` — **this is essential.** Without
      a main-branch baseline, PR decoration has nothing to compare against
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

Commit the fix on a branch and push:

```bash
git checkout -b fix/gold-tier-discount
git add -A
git commit -m "fix: gold tier was silently getting the silver discount rate"
git push -u origin fix/gold-tier-discount
gh pr create --fill
```

Open the PR in the browser. Switch to the **Actions** tab, open the running job.

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

When the job finishes, refresh the PR. Show:

- the **SonarQube Cloud** check run
- the **bot comment** listing new issues, coverage on new code, and gate status

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
