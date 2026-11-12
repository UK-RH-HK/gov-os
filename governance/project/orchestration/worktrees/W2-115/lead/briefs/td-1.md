# Brief: independent test designer, DAEO-emq1 (W2-115), FULL, class C3 — the smart close's acceptance tests (build run 2, td-1)

Budget: projection 6 USD. Keep your context short: read only what the tests need; cut long outputs to head and tail.

You are a fresh independent test designer (MR-3) for ticket DAEO-emq1 (W2-115). You work only in
`/home/usain/gov-os-worktrees/W2-115-tests` on branch `w2/W2-115-tests` (DEC-963). The engineer builds in parallel in
another worktree, which you never read or write. You write to the KPI lines and the Interface below, never to the
implementation: do not read `src/gov/close/` (you may run `PYTHONPATH=<your tree>/src python3 -m gov.cli.main close --help`
and read the existing acceptance suites `tests/acceptance/W1-30/`, `W2-07/`, `W2-57/`, `W2-66/` to see how planted
projects are built and how today's close is driven).

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-emq1`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-emq1','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it (its test-designer
paragraph applies; where it names the heavy slot or `select_tests.py`, use neither unless the sandbox allows it).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-emq1`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-115-tests`, `w2/W2-115-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md` (KPI lines, the Interface section and
  the "Delegated" paragraph at its end). The context packet (`gov context`, built by the lead):
  `/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/brief/context-td.json`. The register
  (`docs/DECISION_REGISTER.md`, 1.6 MB): grep only by id (e.g. `### DEC-1083`); the sources are the ticket's `sources:`.
  `governance/project/briefs/JUDGEMENT.md` defines the reviewer's fenced `verdict` block (S11).
- **Writes:** only `tests/acceptance/W2-115/**`. Scripts, if any, as files under your sandbox `TMPDIR`.
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-115-tests/src`. No `gov retrieve` or `gov context`; search
  with Read and Grep, and search again once in other words if the first search does not answer (DEC-1065). No `$(…)`
  or variable as a write target, no here-document, no `bash -c`. Foreground only. No reset, checkout, clean, amend,
  rebase, push, merge or install.
- No test starts a real embedder, reranker or model; stand-ins only. Planted projects live under pytest's `tmp_path`;
  no test writes into this repository's tree. Keep the whole suite fast: planted test suites of a few trivial cases,
  each scoped close in a planted project a few seconds at most.
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## What to write: `tests/acceptance/W2-115/`

Tests for the KPI lines **S1 to S11, S13 and F1 to F4** of the ticket (the brief's numbering: S12 is the trailers
switch, a kernel check file that waits for its CIT-P, review and the owner's approval: **write no test for it**, and
say so in the README). Each line from its `Verify:` text, through the public surface: `gov close <ticket>`,
`gov close --select <ticket>`, `gov close --verify <ticket>` (run as `python3 -m gov.cli.main close ...` with your
tree's `PYTHONPATH`), the close record, the files the close writes, and the modules the Interface names
(`gov.close.batch`, `gov.close.nightly`) where a line has no CLI form. Plant what the ticket's `acceptance_tests`
names: repositories with a caused red, an unowned red, a test a ticket added, a batch with one culprit and one with an
unexplained red. Where a line's `Verify:` checks "no list read or written" (S5, F2) or "no clone built" (S4), check
it by file times or absence after the run, as the line says. F4: a project with `close: strict` and a project with
no `close.yaml` give the same verdicts and refusals as today's close on the same planted cases (the existing W1-30 and
W2-07 suites stay the strict close's own tests; name them in the README for F4 and add your own comparison).
S9: read `docs/research/W2-115-smart-close.md` of the tree under test and check three recorded batches (one clean,
one caused red, one unowned red) with both verdicts side by side and equal.

Write the README (`tests/acceptance/W2-115/README.md`) mapping every line to its tests **with full node ids**
(`test_<file>.py::test_<name>`, every item; the runner fails a line whose map names a test it cannot collect).

## The interface both sides build to (the ticket's Interface, DEC-1112 (3), plus the lead's naming for what it leaves open)

From the ticket (`.tickets/DAEO-emq1.md`, section "Interface"), binding:
- The switch: `governance/project/close.yaml` holding `close: scoped` or `close: strict`. The template's copy
  `template/governance/project/close.yaml` holds `close: scoped`, and so does this repository's. **A project with no
  file runs strict** (today's close, unchanged; F4). An unreadable file or another value is refused (fail closed).
- Refusal codes: `SELECTION_REFUSED` (a selection that cannot be made, S2; and `--verify`'s exit 2, S13),
  `BATCH_UNEXPLAINED` and `CANDIDATE_NOT_ISOLATED` (S6), `VERDICT_MALFORMED`, `VERDICT_NOT_REVIEWER` and
  `FINDING_BLOCKS` (S11). Each refusal prints its code and its reason.
- The close record at the existing place `docs/close/<ticket>/CL-<ticket>.md` (YAML front matter, then text).
- The warm clone at `.gov-runtime/close/clone/` in the project (S10).

The lead's naming for what the Interface leaves open (both the tests and the code use exactly these; the CTO is told):
- `gov close --select <ticket>` prints one JSON object on stdout:
  `{"ticket": "<id>", "suites": [<test paths or node ids, sorted>], "pytest_options": [<strings>]}`, exit 0;
  a refused selection prints `SELECTION_REFUSED: <reason>` on stderr, prints no set, and exits 2.
- `gov close --verify <ticket> [--out <dir>]` (default `<dir>` = `.gov-runtime/close/verify/<ticket>/`), modelled on
  the CTO's `lead_verify.sh`: it writes in `<dir>` `select.json` (the `--select` object), `parallel.xml` and
  `serial.xml` (JUnit; an empty suite when no serial entry is selected), `summary.txt` (one summary line) and
  `verify.exit` (the code, written last). Exit 0 green; 1 a red (a failure or error in either JUnit file); 2 the
  selection refused; 3 a run that did not complete (pytest's exit not 0 or 1, a JUnit file missing, a killed run).
  The serial phase is today's (`gov.close.serial.phase`, W2-57), restricted to entries inside the selection; each
  phase runs in a heavy-job slot (`gov.resources`' slots).
- The close record's front matter, scoped close, carries these keys (strict close: unchanged, it may add `close: strict`):
  - `close: scoped`
  - `commit: <full sha of the commit closed>`
  - `selection: {suites: [...], pytest_options: [...]}`: equal to what `--select` prints for the same ticket
  - `runs: [{name: <str>, passed: <int>, failed: <int>, errors: <int>, skipped: <int>}]` (never a full-suite run)
  - `review: {verdict: READY|<refusal code>, record: <probe record path or null>}`
  - `reds: [{test: <node id>, failure_type: <e.g. AssertionError, timeout, unknown>, caused: true|false, reason: <text>, repair_ticket: <id or null>}]`
  - `culprits: [<ticket or candidate id>, ...]` (an empty list when none)
  - `clone: {path: .gov-runtime/close/clone, reused: true|false, replaced: <reason text or null>}`
  - `nightly: {read: true|false, record: <path or null>}` (S4: the nightly's recorded result read first)
  A missing key is a failed check (S7).
- A red not caused by the change opens a repair ticket in `.tickets/` (the project's ticket form, `assignee:
  orchestrator`, the red's node id and failure type in its text) and the record's `repair_ticket` names its id (S5).
- The structured reviewer verdict (S11) is the probe record's fenced `verdict` block as `governance/project/briefs/JUDGEMENT.md`
  defines it (read it whole); per KPI line: pass or fail; per finding: scope in|out, ordinary work yes|no, consequence
  fails open|loses work|other. Who wrote it is judged from the commit that wrote the probe record (its `Role:` trailer
  `independent-auditor`; a record whose verdict block a commit with `Role: orchestrator` wrote or changed after the
  reviewer's is `VERDICT_NOT_REVIEWER`).
- The test map: only its existing keys (`shared_core`, `record_only`, `record_reading`, `every_close`, `couplings`,
  `test_inputs`); a shared-core path selects the suites its `couplings` entries and the import graph name, never the
  full suite; a changed path that nothing maps is `SELECTION_REFUSED`.
- The nightly (S8): `gov.close.nightly` rebuilds the worktree's stores with `GOV_SECRETS_FULL_SCAN=1` in the rebuild's
  environment, whatever the caller's, before its run; its record (under `docs/close/nightly/`) says
  `secrets_full_scan: true`.
- Batches (S6): `gov.close.batch` builds the merged result without each candidate in turn (a fresh merge of the
  others onto the base, never a revert of merged code); only the culprits go back, the rest land on the same run.

## Check and commit

1. Run your suite on this branch (today's integrated code, before the engineer's change):
   `env HOME=/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-115-tests/src python3 -m pytest tests/acceptance/W2-115 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
   The new lines should be red there (no `close.yaml`, no `--select`, no `--verify`); F4's strict comparison should be
   green. Quote the last line and each failure's one-line reason, grouped by KPI line; a line green on today's code
   is a test that checks nothing new: fix it or say why.
2. Commit only your paths:

       git commit -m "W2-115 acceptance: the smart close (S1-S11, S13, F1-F4; S12 waits for its CIT-P)" --trailer "Task: DAEO-emq1" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-983, DEC-982, DEC-979, DEC-968, DEC-966, DEC-953, DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1050, DEC-1083, DEC-988, DEC-989, DEC-1125, DEC-1052" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-115

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `ps` check (EMG-d4b-launched.md), the run's last line, the commit hash with its
trailers, `du -sh` of your TMPDIR. In `tests`: the case count per KPI line and the TESTS-READY text (the merge commit is
the lead's). Also the refusals met. Where the Interface is silent on something a test needs, choose the narrowest
reading, name it in `discoveries`, and never invent a refusal code.
