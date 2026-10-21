
## W1-30 follow-up: `gov close` after its two independent reviews (DEC-487, DEC-490, DEC-492, DEC-498, DEC-500; 2026-10-07)

The follow-up to the merge at `2c71bc64`: rounds 8 to 10 on `w1/W1-30` (290 cases; `src/gov/close/` is
`command.py`, `repo.py`, `state.py`, `tool.py`). One run of `gov close` now reports every finding in one
refusal, counted once, with one repair ticket; it finds the ticket tool at the kernel's place and, where
that holds nothing, on PATH; it measures the commit and not the tree; it reads every probe record. The first
review (reviewer session `350cc2a3-27ae-4888-834a-c6df2fc31b79`, at `6f2130c8`) returned thirteen findings
and the second and last (session `35e6015b-375b-4173-87df-7d5abfc1e07b`, at `b59d7244`) sixteen; the last
round (designer `1fac7f2a`, engineer `fa5180ed`) came after the second review and was read by the
orchestrator only (DEC-498: no third review). **Deviation (DEC-498):** the ticket was merged before any
independent probe of its final code.

What `gov close` still does not measure, or can be made to pass, each known and none fixed here:

- **From the last review (DEC-500), by its finding number.** (2) A commit without a task that adds a test
  configuration file outside the ticket's folder (`tests/conftest.py`, a root `conftest.py`, `pytest.ini`,
  `pyproject.toml`) decides what the acceptance run measures and refuses nothing: a gap in DEC-490's own
  rule. (4) The range of commits follows git's date order, not ancestry: a backdated commit plus a merge
  hides a task-less commit. (5) "By the orchestrator" on a probe record is a self-written `Role:` trailer;
  whether such a commit can be made is the guard's matter. (9) Any owner decision recorded after an
  escalation lifts it, whatever it is about. (10) Removing both state files resets an escalation, and
  removing the counter before the third refusal resets the count. (11) The close record lists no skills in
  a project with an installed kernel (it reads the template's place only): for W1-41's adoption. (12) An
  interruption while the ticket tool closes leaves the close record and the checkpoint; the next close
  refuses for them. (14) Template kernel folders outside the six listed prefixes do not run the governance
  checks. (15) A ticket argument that is a path is taken as a ticket and writes a counter outside the
  iterations folder; nothing closes. (16) In a project that does not ignore compiled files, a refused
  close's own test run makes the next close answer "tree not committed". (3, other side) A probe record of
  an earlier round refuses beside a passing one: the orchestrator keeps only the record of the final code.
- **Files the commit's own ignore rules ignore** are in the tree the tests run in and not in the commit
  (the ordinary form of finding 6); closing it means running the tests in a clean checkout of the commit.
- **Left open by the last round, by the engineer's own account.** Only the git that `gov close` itself asks
  is cut off from the caller's environment and from replacement refs: containment, the check runner, the
  store, the context and the watchdog call git themselves. The repository's and the caller's git
  configuration files still reach every call (an excludes file they name is caught). Of the interpreter's
  variables three still reach the test runs (`PYTHONUSERBASE`, `PYTHONPYCACHEPREFIX`,
  `PYTHONDONTWRITEBYTECODE`); the rest of the caller's environment reaches them too.
- **From the engineers' lists of rounds 8 and 9.** A regression run that collects or passes nothing counts
  as passed. An acceptance run with one passing test counts as measured whatever was skipped (skips are now
  counted in the record and refuse nothing). The governance checks run only when a commit in the range
  touches a governance prefix; otherwise the close record carries no check result. The tree and `HEAD` are
  checked once at the start, not again before the ticket is closed. A committed `conftest.py` inside the
  ticket's own folder runs. A merge commit without a task that brings ticket work refuses even where the
  merged commits were measured (it over-refuses). `deviations` is always "not measured", and the watchdog
  is given no context utilisation. The status read-back after a ticket tool on PATH checks only the ticket
  file's `status` field. `_work_of` imports a private function of the guard
  (`gov.guard.decide._match_pattern`). `src/gov/close/traceability.py:101` keeps an `except Exception`
  from before these rounds.
- **DEC-487's four residuals** stand: the owner's decision is read from decision files only (DEC-483, for
  W1-41); the escalation state is in files the caller can write; the probe record's sessions are not
  checked against a launch record (Wave 2, DEC-470); the time limit covers each test run, not the whole
  close.
- **The governance share is not yet in the close record:** the call to the counter is a follow-up once
  W1-31 is merged (DEC-495); until then `gov telemetry` is run beside each close.
- **Process notes.** The round-9 test designer edited the suite's support file with a script instead of the
  Edit tool (inside its folder). Rounds 9 and 10 each outlasted the tool's ten-minute limit in the workers'
  foreground runs and finished in the background; each worker waited for the end before committing.
- **KPI disputes:** none raised as disputes. **Acceptance tests rewritten after implementation began:**
  rounds 8 to 10 rewrote none by their designers' accounts (round 8's rewrites carry their reasons in the
  README; the `Rewrite-Reason:` trailer began with DEC-491).
