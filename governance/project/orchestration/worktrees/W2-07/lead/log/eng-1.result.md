task: Implement W2-07 (DAEO-r9ss) in `/home/usain/gov-os-worktrees/W2-07`, branch `w2/W2-07`: `gov close` judges by ticket class, runs its gates before any test, writes tracked repair tickets and carries a share on every close, until the acceptance tests pass.

status: PACKAGES. All 40 W2-07 cases pass, but running `gov check` on every close (A6/KPI 5) turns many W1-30 cases red because their test projects are RED at `gov check`; the test designer or owner has to decide how to handle that. Not finished: the list rows were not re-checked, and W1-30 was not re-run on the final code.

work_completed:
- New module `src/gov/close/gates.py`:
  - judging by class (research, audit, integration, coordination on `acceptance_tests.evidence`; specification on `gov readiness`);
  - the acceptance folder a ticket declares in `acceptance_tests.path`;
  - decision-record commits measured by an ACCEPTED owner decision;
  - the ratchet's reading of both lists before any test;
  - the collection of each suite, one process per suite, run exactly as the close runs it;
  - the disk floors (`close_free_gib_floor`, `close_free_inodes_floor`; refusal code `DISK_BELOW_FLOOR`, exit 3, no attempt spent);
  - a failed probe accepted when an ACCEPTED owner decision names the record, the probed commit and each finding with its row;
  - taking back what an interrupted close left.
- `command.py` `run()`, in the new order:
  - commit gates first, then the pre-close gate (collection, `gov check` on every close, checkpoint), then the disk floor, then the tests;
  - refusals from the commit gates and the pre-close gate are not counted, keep exit 3 and keep their repair ticket;
  - the record and the answer now state `ticket_class`, `disk`, `evidence` and `probe_accepted_by`.
- `tool.py`, repair tickets:
  - each carries `role`, `allowed_paths` and `kpis` taken from the ticket being closed, plus a fingerprint of its findings;
  - a repeated identical refusal reuses the open repair ticket;
  - the refusal commits the new repair ticket alone (`Task: <repair id>`, `Role: orchestrator`, `Implements: AR-9`). It cannot just be left in the working tree: the test project's next `git add -A` commit by a worker role swept it in, and the containment check refused that commit. If the commit fails, the ticket stays untracked, which the tree check already allows.
- KPI 12: `test_a_collection_error_is_a_finding` revised in its own commits, with no expectation lowered.

files_changed: `src/gov/close/gates.py` (new), `src/gov/close/command.py`, `src/gov/close/tool.py`, `tests/unit/close/test_run_and_record.py`

evidence:
- Sandbox check:
  - (1) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r9ss` failed (`OSError: [Errno 30] Read-only file system`);
  - (2) `git hash-object -w` gave `1ae28402…` with exit 0, and `git update-index --refresh` exited 0;
  - `GOV_ROLE=engineer`, `GOV_TICKET=DAEO-r9ss`; toplevel `/home/usain/gov-os-worktrees/W2-07`, branch `w2/W2-07`.
- `gov.__file__` = `/home/usain/gov-os-worktrees/W2-07/src/gov/__init__.py`.
- Commits:

  | Commit | Content | Extra trailer |
  |---|---|---|
  | `f00e9d39` | main implementation | — |
  | `c0e9d677` | `gov check` call kept compatible with the existing unit tests' mocks | — |
  | `57d3f4e4` | unit-test revision | `Rewrite-Reason: DEC-868 item 3` |
  | `aa33c62d` | collection per suite, as the close runs it | — |
  | `e1101f12` | unit-test follow-up | `Rewrite-Reason: DEC-868 item 3` |

  Every commit carries `Task: DAEO-r9ss`, `Role: engineer`, `Implements: DEC-896, DEC-868, DEC-892, DEC-898, DEC-790` and `Co-Authored-By: Claude Opus 5.5`.
- Size: +437/−35 lines over 4 files, against an estimate of 220 (about 2× over).
- No `pre-commit` hook was present (only `pre-commit.sample`). `git status` shows nothing of mine left over; the untracked dotfiles and `docs/source` in the worktree are not mine.
- Scratch: `TMPDIR` holds 137,914 inodes and 1.7 GB, within my 6 GB / 300,000 share. I did not measure the worktree's ignored files (`__pycache__`, `.gov-runtime/`).
- Read refusals: 1 guard refusal, my own mistake (an `ls` that included `tests/acceptance/W2-07`; not retried). Separately, one `rm -rf` of my temp folder `…/claude-1000/ita` waited for a permission I don't have, so that tiny folder is still there.
- `gov retrieve`: used once; it returned `FACET_UNAVAILABLE` because the index is stale. After that I used Grep and Read on named files.

tests:
- On the final code:
  - `tests/acceptance/W2-07`: 40 passed.
  - `tests/acceptance/W2-01`: all pass. These were red until I split the collection per suite.
  - `tests/acceptance/W2-53`: 1 red (below).
  - `test_w1_30_close.py::test_collection_error_refuses_close`: passes.
  - `tests/unit/close` and `tests/unit/telemetry`: 18 red (below).
  - The combined run of these suites: 19 failed, 618 passed.
- `tests/acceptance/W1-30`, run before the per-suite collection fix: 193 failed, 316 passed, 3 errors. With `gov check` back to only-when-governance-files-change, as a temporary diagnostic, it was 27 failed, 485 passed. So about 166 of those reds come from `gov check` running on every close. Not re-run on the final code.
- `test_w1_30_no_acceptance_tests.py` (revised by the test designer): 6 cases red, refused on a RED `gov check` in the test project (adapter-portability `KERNEL_EMPTY`, index-freshness "lexical index missing", retrieval-regression "GOV_DEV_TIERS is not configured").
- `pytest tests --collect-only`: 15,802 tests collected, no collection error.
- Serial-only cases were not run separately.

discoveries:
- Earlier cases I turned red, by cause:
  - **KPI 5 / A6 (DEC-868 item 1(b)): `gov check` on every close.** W1-30's test projects copy the whole kernel's check set and are RED at `gov check`. About 166 W1-30 cases go red this way, including all 6 cases of the revised `test_w1_30_no_acceptance_tests.py`.
  - **KPI 4/5 (DEC-868 item 3, P-IS-4 (a)): the gates now stop before any test, and their refusals are not counted.**
    - W1-30 (27 cases): every case in `test_w1_30_r9_every_finding.py`, `test_w1_30_r13_refused_runs.py`, `test_w1_30_iteration.py::test_mixed_causes_reach_escalation` and `::test_each_refusal_opens_repair_ticket`, `test_w1_30_check_blocks.py::test_a_refusal_where_gov_check_blocks_is_counted`, `test_w1_30_governance_checks.py::test_a_refusal_for_a_red_check_is_counted`, `test_w1_30_time_limit.py` (3 cases), and the others in the 27 listed.
    - W2-53: `test_w2_53_load_sensitive.py::test_an_entry_the_owner_did_not_add_is_refused_naming_it_and_its_test_is_not_run_again`. The entry is now refused before any test runs.
    - Unit (17 cases): `test_every_finding.py` (12), `test_governance_checks.py` (3, which hold that a red check is counted or shares one refusal with a failing test), `test_measured.py::test_a_finding_and_could_not_measure_are_two_ways_out`.
  - **KPI 8 / A7: the committed repair ticket moves HEAD.** `test_state.py::test_the_third_refusal_records_where_the_escalation_began` expects `escalated_at` to equal HEAD from before the refusals.
- Later decision over earlier one: DEC-868 item 3 and DEC-896 item 3 change DEC-492 ("every gate is asked; one counted refusal") for the gates that now run before the tests. Code: `command.py` `run()`; test: `test_every_finding.py`.

risks:
- A refused close now makes a commit (the repair ticket). The record store is then stale until the next rebuild, so a close straight after a refusal without `gov rebuild` gets `STORE_STALE`.
- `gov check` on every close blocks any project whose check set is RED for reasons unrelated to the ticket.
- The probe acceptance requires the finding id and a row id (a `W<n>-<letter><n>` pattern) on the same line of the decision text.

lessons:
- W2-07's test-project helper commits with `git add -A` for a test-designer role, so anything the close leaves uncommitted ends up inside a worker's commit.
- Collect each suite the way the close runs it. Collecting `tests/` in one go raised a basename clash (`test_pass.py` in two folders) that the real runs never meet.

proposed_decisions:
- **P-1: the W1-30 test projects and `gov check` on every close.** Recommend (a): the test designer gives the W1-30 test projects a check set that is green, as W2-07's projects evidently have, with `Rewrite-Reason: DEC-868 item 1`. Confidence: medium-high.
  - Alternatives: (b) re-baseline A6 so `gov check` runs only when governance files change, which turns W2-07's `test_a_red_gov_check_refuses_before_any_test` red; (c) defer.
- **P-2: the repair-ticket commit.** Recommend accepting the commit made by the refusal. Confidence: medium.
  - Alternative: leave the repair ticket uncommitted and change W2-07's test helper.
- **P-3: the unit tests in the KPI 4/5 and KPI 8 groups above.** These sit inside my paths, but revising them changes what they assert. Recommend that one builder pass revises them with `Rewrite-Reason: DEC-868 item 3`, or `KPI 8 / A7` for the `test_state` case. Confidence: medium.

unresolved:
- The list rows were not re-checked against the code (DEC-718), and none of the telemetry rows were taken. W2-M348, W2-M349 and W2-M354 are reported only, as the brief asks.
- W1-30 not re-run on the final code.
- The 18 unit reds are not revised.
- The worktree's ignored files were not measured.
- The temp folder `ita` is still there.

recommended_next_action: The lead takes P-1 to the test designer, then re-runs W1-30 and the serial-only cases on `e1101f12`.