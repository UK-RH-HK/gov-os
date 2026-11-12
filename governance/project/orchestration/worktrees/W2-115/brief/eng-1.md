# Brief: engineer, DAEO-emq1 (W2-115), FULL, class C3 — gov close, the smart close (build run 2, eng-1)

Budget: projection 12 USD. Keep your context short: read only what this change needs; cut long outputs to head and
tail. `src/gov/close/command.py` is 1,466 lines: read it by the functions you change (Grep `^def `), not whole.

You are a fresh engineer for ticket DAEO-emq1 (W2-115). You work only in `/home/usain/gov-os-worktrees/W2-115` on
branch `w2/W2-115` (DEC-963). An independent test designer writes the acceptance tests in parallel in another worktree;
the lead merges them later. `gov close` is the judge's core (class C3): the reviewer will probe above all for a caused
red that closes.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-emq1`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-emq1','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read that file (its Engineer paragraph applies, except
that the evidence goes in `docs/research/W2-115-smart-close.md`, your allowed path) and `EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-emq1`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-115`, `w2/W2-115`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md` (KPI lines, the Interface section and
  the "Delegated" paragraph at its end; "Why" names today's contradictions: `select.py` widens to the full suite,
  `ratchet.py` judges by owner-accepted lists, `load_sensitive`, `batch.py` closes nothing on a red run). The context
  packet (`gov context`, built by the lead): `/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/context-eng.json`.
  The register (`docs/DECISION_REGISTER.md`, 1.6 MB): grep only by id (`### DEC-1083`); read at least DEC-953, DEC-983,
  DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1083, DEC-1125. The CTO's working smart close, the model this one
  follows: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_build.py`,
  `select_tests.py` and `lead_verify.sh` (read; do not change them).
- **Writes:** only the ticket's `allowed_paths`: `src/gov/close/command.py`, `select.py`, `batch.py`, `nightly.py`,
  `tool.py`, `attribution.py` (new), `governance/project/close.yaml` (new, `close: scoped`),
  `template/governance/project/close.yaml` (new, `close: scoped`), `template/governance/project/test-map.yaml`,
  `tests/unit/close/test_w2_115*`, `docs/research/W2-115-smart-close.md`. **Not** `src/gov/close/traceability.py` or
  `template/governance/kernel/checks/product-traceability-trailers.yaml`: S12 (the trailers switch) is not built in
  this run (P4: it waits for its CIT-P, review and the owner's approval). A change you need outside these paths
  (`serial.py`, `ratchet.py`, the test-map schema, `governance/project/test-map.yaml`): stop and return PACKAGES with
  the question, options with cost, your recommendation and confidence. Never `git add -A`.
- **Never read `tests/acceptance/W2-115/**`** (DEC-820, DEC-1063); every Grep/Glob that could reach it carries
  `!tests/acceptance/W2-115/**`, every recursive grep `--exclude-dir=W2-115`.
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src`. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src python3 -c "import gov; print(gov.__file__)"`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). Command forms: no `$(…)` or variable as a write target, no here-document, no
  `bash -c`; scripts as files under your sandbox `TMPDIR`. Foreground only. No reset, checkout, clean, amend, rebase,
  push, merge or install. No real embedder or model in any test (stand-ins only).
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## The change

Build KPI lines **S1 to S11, S13 and F1 to F4** (the brief's numbering; the ticket's "S17" in the Delegated paragraph
is this brief's S12, its "S18" is S13). In short:

- **S1** the switch (Interface); no file = strict, today's close byte for byte in its verdicts (F4): keep every
  strict path and every lifted gate built and reached only when `close: strict` or no file.
- **S2/S3** the scoped selection: the ticket's own suite (`acceptance_tests.path`) plus every suite the change can reach
  (import graph, `couplings`), a shared-core change selecting its mapped suites, never the full; record places and
  the governance overlay select nothing by themselves; records alone select `record_reading` only; an unmappable
  change refuses `SELECTION_REFUSED` with its reason, never widened. `--select` prints exactly the set the close runs.
- **S4/S5/F1** red attribution (`attribution.py`): every failing test run again alone; a red is not the change's only if
  the head without the batch (the tested code, in the warm clone) has it red with the same failure type, one run each
  way, 3 rounds only for load-sensitive cases; the nightly's recorded result read first; no nightly-baseline clone;
  timeout or no record never matches. An unowned red is named in the record and opens a repair ticket; the scoped
  close reads and writes no accepted-reds or load-sensitive list (`ratchet.py` stays the strict close's).
- **S6/F3** batches (`batch.py`): the culprit found by building the merged result without each candidate before
  anything lands; only culprits go back, the rest land on the same run; `BATCH_UNEXPLAINED`, `CANDIDATE_NOT_ISOLATED`.
- **S7** the close record's keys (below). **S8** the nightly's full secrets scan. **S10** the warm clone (reset, stores
  kept; a clone that cannot be reset replaced, the record says so).
- **S11** READY computed from the probe record's fenced `verdict` block (JUDGEMENT.md, line 23):
  `VERDICT_MALFORMED`, `VERDICT_NOT_REVIEWER`, `FINDING_BLOCKS`.
- **S13** `gov close --verify` (below), on today's serial phase (`serial.py`, P5 (a)).
- **S9** measure in `docs/research/W2-115-smart-close.md`: `close_build.py`'s verdict and this close's side by side on
  three of this repository's recorded batches (one clean, one caused red, one unowned red), equal on all three. If
  `close_build.py` cannot run in your sandbox, find its recorded verdicts (its logs/records under the orchestrator's
  scratch), cite them by path, run this close's side, and say which in the document and your return.
- This repository's `governance/project/close.yaml` reads `close: scoped`.

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

## Tests and done

Your own unit tests in `tests/unit/close/test_w2_115_*.py` (planted projects under `tmp_path`, stand-ins), one or more
per KPI line. Stop when they pass and the close's existing unit and acceptance suites you can reach still pass:
`env HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src python3 -m pytest tests/unit/close tests/acceptance/W1-30 tests/acceptance/W2-07 tests/acceptance/W2-57 tests/acceptance/W2-66 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(the strict close's suites: F4). Quote the last line. A red you did not cause: re-run it alone, then name it.

Commit in batches as you go (the lead merges the tests between your batches), each:

    git commit -m "<subject>" --trailer "Task: DAEO-emq1" --trailer "Role: engineer" --trailer "Implements: DEC-983, DEC-982, DEC-979, DEC-968, DEC-966, DEC-953, DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1050, DEC-1083, DEC-988, DEC-989, DEC-1125, DEC-1052, DEC-1079" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Then quote `git log --oneline -5` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `ps` check, the `gov.__file__` line, the runs' last lines, each commit hash with
its trailers, `du -sh` of your TMPDIR. In `tests`: the counts per KPI line. Also the refusals met. Where the Interface
is silent, choose the narrowest reading that keeps the close fail-closed and name it in `discoveries`.
