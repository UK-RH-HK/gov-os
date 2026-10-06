# W1-30 acceptance tests: `gov close`

Ticket `DAEO-2lwj`, profile FULL (DEC-221). Written before implementation by the Independent Test Designer (MR-3).
75 cases in 8 files (49 first-start + 2 fail-open probe-gate + 24 second-start).

```
python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider
```

## How the tests run

- Through public interfaces only: the `gov close` command line (W1-07's console-script stand-in), its API-0002
  envelope and exit code; `gov check` for the product-traceability family check (S3).
- Every project is a temporary git repository (DEC-322): its own `.tickets/`, its own commits, its own
  acceptance tests. No test creates a file in this repository. The code under test is this worktree's `src/`.
- Before `gov close` runs, the project is committed.
- Deterministic, no network.

## Red before implementation

Expected: `1 skipped, 48 errors`.

- The 47 errors stop at the `built` fixture: `gov close is not built yet: it returns NOT_IMPLEMENTED`.
- The 1 skip, in `test_w1_30_close.py::test_close_returns_api_0002_envelope`: uses the
  `raw_project` fixture (no `built` gate) and skips because `NOT_IMPLEMENTED` is in the output.

## KPI lines and covers ids

| KPI line | Tests | Red reason |
|---|---|---|
| **S1** "Runs tests/acceptance/<ticket>/ and the regression tests, requires Implements: and Task: trailers, runs the containment check, writes a checkpoint and the close record with skill versions" [CAP-13.a, CAP-24.a, CAP-38.a, CAP-38.c] | `test_w1_30_close.py` (18), `test_w1_30_watchdog.py` (3) | `NOT_IMPLEMENTED` |
| **S2** "Holds the iteration count … after three consecutive non-converging iterations it stops the loop and puts an escalation package in chat … a failure opens a dependent repair ticket" [CAP-31.b, CAP-59.a] | `test_w1_30_iteration.py` (14) | `NOT_IMPLEMENTED` |
| **S3** "Registers the product-traceability family check: the commits of every closed ticket carry Implements: and Task: trailers that resolve" [CAP-38.b] | `test_w1_30_traceability.py` (5) | Product-traceability trailer check not registered |
| **S4** "A ticket that changes governance files cannot close on check results recorded for another commit or inputs hash" [CAP-38.d] | `test_w1_30_stale.py` (5) | `NOT_IMPLEMENTED` |
| **S5** "The close record is a consumption receipt: the input ids and hashes supplied (packet hash) and used, outputs produced, requirements implemented, decisions applied, tests produced, and deviations" [CAP-50.c] | `test_w1_30_receipt.py` (9) | `NOT_IMPLEMENTED` |
| **S6** "A finding raised at close is classed into exactly one disposition … with whole-system context from gov context before any code change, and the repair ticket records it" [CAP-59.c] | `test_w1_30_disposition.py` (9) | `NOT_IMPLEMENTED` |
| **S7** "A FULL-profile ticket closes only with a post-green probe record made by a fresh reviewer session other than the implementer" [CAP-38.f] | `test_w1_30_probe.py` (12) | `NOT_IMPLEMENTED` |
| **F1** "A ticket closes with a failing acceptance test" | `test_w1_30_close.py::test_close_refuses_when_acceptance_tests_fail` | `NOT_IMPLEMENTED` |
| **F2** "A fourth consecutive non-converging iteration starts without an owner decision" | `test_w1_30_iteration.py::test_fourth_non_converging_blocked_without_owner` | `NOT_IMPLEMENTED` |
| **F3** "The iteration count or budget appears in any output seen by the looping session" [CAP-59.b] | `test_w1_30_iteration.py` (3 tests) | `NOT_IMPLEMENTED` |
| **MWA-04** "A commit outside allowed_paths is caught by containment" | `test_w1_30_close.py::test_containment_blocks_close_for_out_of_scope_commit` | `NOT_IMPLEMENTED` |

## Covers ids

| Covers id | Tests |
|---|---|
| CAP-13.a (closure process) | `test_w1_30_close.py` (envelope, success, checkpoint, containment) |
| CAP-24.a (skill versions) | `test_w1_30_close.py` (skill versions in close record) |
| CAP-31.b (iteration count) | `test_w1_30_iteration.py` (persistence, convergence) |
| CAP-38.a (runs acceptance tests) | `test_w1_30_close.py` (runs tests, refuses on failure) |
| CAP-38.b (product-traceability check) | `test_w1_30_traceability.py` (5 tests) |
| CAP-38.c (trailers required) | `test_w1_30_close.py` (Implements:, Task:) |
| CAP-38.d (stale evidence) | `test_w1_30_stale.py` (5 tests) |
| CAP-38.f (probe record) | `test_w1_30_probe.py` (12 tests) |
| CAP-50.c (consumption receipt) | `test_w1_30_receipt.py` (9 tests) |
| CAP-59.a (escalation) | `test_w1_30_iteration.py` (escalation, options, repair ticket, distinct outcomes) |
| CAP-59.b (count hidden) | `test_w1_30_iteration.py` (count/budget not in output) |
| CAP-59.c (disposition) | `test_w1_30_disposition.py` (9 tests) |
| DEC-416 (checkpoint watchdog) | `test_w1_30_watchdog.py` (3 tests) |

## Files

| File | Cases | KPI |
|---|---|---|
| `test_w1_30_close.py` | 18 | S1, F1, MWA-04 |
| `test_w1_30_iteration.py` | 14 | S2, F2, F3 |
| `test_w1_30_traceability.py` | 5 | S3 |
| `test_w1_30_stale.py` | 5 | S4 |
| `test_w1_30_receipt.py` | 9 | S5 |
| `test_w1_30_disposition.py` | 9 | S6 |
| `test_w1_30_probe.py` | 12 | S7 |
| `test_w1_30_watchdog.py` | 3 | S1 (DEC-416) |

## The interface the tests fix

| What | Value | From |
|---|---|---|
| Module | `src/gov/close/command.py` | DEC-317, `gov.cli.main` |
| Class | act | DEC-317 |
| Arguments | `<ticket>` (positional); `--json` (standard) | DEC-317 |
| Passes | `ok: true`, exit 0, result includes ticket and close record info | API-0002 |
| Acceptance test failure | `ok: false`, exit 3 | API-0002 code 3 |
| Missing trailer | `ok: false`, exit 1 | API-0002 code 1 |
| Containment finding | `ok: false`, exit 1 | API-0002 code 1 |
| Missing probe (FULL) | `ok: false`, exit 1 or 4 | API-0002 code 1/4 |
| Escalation (blocked) | `ok: false`, exit 4 | API-0002 code 4 |
| Stale evidence | `ok: false`, exit 1 or 3 | API-0002 code 1/3 |

## Design decisions

### Close record path
Recommendation: `docs/close/<ticket>/CL-<ticket>.md`, following the checkpoint pattern
(`docs/checkpoints/<ticket>/CP-<ticket>-NNNN.md`). Confidence: 75%.

The tests use `find_close_record()` which scans new files for `type: close` frontmatter,
so the exact path is not hard-coded in assertions.

### Probe record path
Recommendation: `docs/probes/<ticket>/PR-<ticket>.md`. Confidence: 70%.

The probe record has YAML frontmatter with: `type: probe`, `task`, `reviewer_session`,
`implementer_session`, `reviewer_wrote_nothing`, `commissioned_by`, `judged_by`.

### Iteration count storage
The iteration count is stored under `.gov-runtime/` (which the guard denies to workers).
This ensures CAP-59.b: the looping session cannot read its own iteration count.
Recommendation: `.gov-runtime/iterations/<ticket>.json`. Confidence: 70%.

### Non-converging definition
An iteration is "non-converging" when the same set of failing tests or findings repeats
as the previous iteration. After 3 consecutive non-converging iterations, the 4th attempt
is blocked and an escalation package is produced.

### Product-traceability check
The engineer registers a check declaration in `template/governance/kernel/checks/product-traceability*.yaml`
that runs a command verifying closed tickets' commits carry Implements: and Task: trailers that resolve
to records in the store.

## Earlier tests revised

`tests/acceptance/W1-07/`: `close` joins `BUILT_LATER` in `w1_07_support.py`, with
`REQUIRED_ARGUMENTS["close"]` for the ticket argument.

`tests/unit/launch/test_command_modules.py`: `close` on line 119 must be replaced by
`rebuild` as the not-yet-built stand-in in `test_a_faulty_module_fails_its_own_command_and_no_other`.
**The test designer's paths do not cover `tests/unit/`; this edit belongs to the engineer
or orchestrator** (following the pattern of commit `9c8fec02`, which was `Role: orchestrator`).

## Second-start tests (24 new cases)

Added by a second Independent Test Designer pass (11 points).

| Point | File | New cases | Red reason |
|---|---|---|---|
| 2 | `test_w1_30_close.py` | 2 (no acceptance dir, empty dir) | Missing acceptance tests not checked |
| 3 | `test_w1_30_close.py` | 1 (regression test failure) | Regression test failure not checked |
| 4 | `test_w1_30_probe.py` | 5 (commissioned_by, judged_by, judgement, malformed YAML, unreadable) | Probe validation fields not checked |
| 5 | `test_w1_30_receipt.py` | 3 (packet_hash matches, context failure, input hash of content) | Hash is invented fallback, not from context |
| 6 | `test_w1_30_disposition.py` | 4 (no class, two classes, six valid names, repair records class) | Code assigns DISPOSITIONS[0] to everything |
| 7 | `test_w1_30_iteration.py` | 2 (distinct outcomes, reason not converging) | Outcomes are duplicated copies |
| 8 | `test_w1_30_close.py` | 2 (trailer exact match, ticket tool interface) | Substring match bug; string replacement |
| 9 | `test_w1_30_stale.py` | 1 (stale evidence without prior close) | Existing test closes first, masking stale check |
| 10 | `test_w1_30_watchdog.py` | 3 (stale checkpoint, missing checkpoint, closing checkpoint written) | No call to gov.checkpoint.record.watch() |
| 11 | `test_w1_30_iteration.py` | 1 (outcomes list reveals count to looping session) | Outcomes list length IS the count (CAP-59.b) |

### Packages (not testable without new code)

- **Point 1** (containment commit-range check): `check_containment` in `src/gov/guard/containment.py` is snapshot-based. Checking that a ticket's commits stay within `allowed_paths` requires a commit-range function that does not exist yet. **Package**: add `check_commit_range(root, ticket, allowed_paths)` to containment.py.
- **Point 4 sub-item** (reviewer "wrote nothing" verification): `reviewer_wrote_nothing` in the probe record is a claim by the reviewer session. Verifying it against the repository (no commits with `Role: independent-test-designer` trailers for this ticket) requires comparing commit trailers, which `_check_probe` does not do. **Package**: add verification of `reviewer_wrote_nothing` against commit history.
- **Point 6 sub-item** (disposition source): Who provides the disposition is unclear — the code assigns `DISPOSITIONS[0]` unconditionally. The tests check that each finding has exactly one valid disposition, but the mechanism (argument, file, or orchestrator-provided) is a design decision. **Package**: decide and implement the disposition assignment mechanism.

## Residuals

- Source **S0a-G-12** is among the ticket's sources but its text is not in the tree.
  No test is derived from unread text.
- **W1-29** (session hooks, stale-checkpoint watchdog) is being built on another branch.
  If `gov close` must call a W1-29 function (e.g. to trigger the stale-checkpoint
  watchdog after writing a checkpoint), that is a cross-ticket dependency not covered
  here.

## Not tested

- Latency or timeout of `gov close` (not a test concern beyond determinism).
- The orchestrator's judgment of the probe record (that is the orchestrator's role,
  not a `gov close` responsibility).
- Running `gov close` against this repository (DEC-322: always a throwaway project).
