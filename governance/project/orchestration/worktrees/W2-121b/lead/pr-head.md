---
type: probe
task: DAEO-ifgf
reviewer_session: 6b780fde-de77-42cf-b74a-2e17f98434b3
reviewer_session_round_1: 88a93c93-c2a0-4791-8167-d4eb85b38889
implementer_session: bc2586bf-4089-4ab5-b83c-826f8b6fd3c7
implementer_session_round_1: dcea294b-6e50-4ab3-8bae-aea1673e461a
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: dae1c10e0392360d9d4d2dfe06a8889800cf8c91
decisions_applied: [DEC-801, DEC-802, DEC-808, DEC-809, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1112, DEC-1144]
---

# Probe record: W2-121b (DAEO-ifgf) gov dispatch part b, the landing: reviews 1 and 2 of at most 2 (DEC-1010)

## The lead's judgement

- **Who probed.** Each round had a fresh, read-only reviewer: role `independent-auditor`, Opus 5.5 at effort high, class C2, started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-12.
  - Round 1: session `88a93c93-c2a0-4791-8167-d4eb85b38889`, probing head `951dbcfa5cc7`.
  - Round 2: session `6b780fde-de77-42cf-b74a-2e17f98434b3`, probing head `dae1c10e0392`.
  - In both rounds step 0 held: the write outside the tree failed with a read-only file system, and the index refresh worked. The head was the same at the start and at the end, and `git status --porcelain` was empty.
  - Neither reviewer met a read refusal. Each met one Write refusal for a probe script under its TMPDIR. Neither retried it or worked around it: round 1 probed inline instead, and round 2 used code reading and the S2 file run.
  - The tripwire changes listed were in other sessions' trees.
- **What was probed.** The branch `w2/W2-121b`, from base `1ef597a43909`:
  - the independent test designer's acceptance suite `tests/acceptance/W2-121b/`:
    - `a60ee938c`, the first 48 cases, red 48 on the base;
    - `ed8aa4904`, two cases fixed to the ticket on the engineer's findings (the batch log's count; the midnight-crossing window's outside case);
    - `7143cabd7`, four S2 wrapper-close cases from review round 1's RV1, red on `951dbcfa5`;
  - the engineer's build `ab5799760`: `src/gov/dispatch/landing.py` and `heavy.py`, the changes in `config.py`, `procs.py`, `run.py`, `state.py` and `status.py`, the read helper `slots.runners`, and unit tests;
  - the round 2 fix `dae1c10e0`, by a fresh engineer given the failing output only: `landing.close_arguments` reads a close's tickets from every process matching the close marker, and part a's `procs.find` is unchanged.
  - `git diff --name-only w2/integrate...HEAD` lists only the ticket's `allowed_paths` and the designer's suite.
- **The lead's own results at `dae1c10e0392`.**
  - The store was rebuilt (exit 0).
  - `gov accept W2-121b`: pass, 52 passed, 0 failed: success-1 10, success-2 12, success-3 13, success-4 14. The runner's `gov.__file__` is `/home/usain/.local/share/gov-os/pin-797495bdfc70/lib/python3.12/site-packages/gov/__init__.py`, and the cases import the tree's `src/` (`/home/usain/gov-os-worktrees/W2-121b/src/gov/__init__.py`).
  - Part a's suites, per the engineer: `tests/acceptance/W2-121` 179/179 and `tests/unit/dispatch` 112/112.
  - `lead_verify`: 4,699 tests, 4 failed, 1 error, 7 skipped. None of them is this ticket's:
    - (1) `tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository`. The front matter of `docs/changes/W2-176-CIT-P.md` is not YAML at the branch's base (`e395dd430`). `w2/integrate` fixed it in `5289bec52`, so this red goes when the branch lands on `w2/integrate`.
    - (2) `tests/unit/resources/test_w2_157_backstop.py`: three failures (`test_s1_below_then_above…`, `test_s1_the_limit_and_period…`, `test_l5b_…[last]`) and one error (`test_s3_the_limit_comes_before…`, worker gw2). These are W2-157's load-sensitive cases. The run hung on them for about 30 minutes, so the lead stopped by pid, with `proc.sh`, first three SIGSTOPped `time.sleep(120)` children of the verify's own worker, then the looping worker. Re-run alone, the file gave 94 passed in 6.4 s. `backstop.py` does not use `slots`, and `slots.py` gained only a read function.
- **Judged by the threat model (DEC-801, DEC-808, DEC-1010).**
  - Round 1 found one in-scope finding, RV1, judged ordinary work yes and fails open. On a close started through a shell wrapper (an agent's Bash tool, or cron), only the wrapper was read, so a landing of the same ticket went ahead. That is a fail of S2.
  - Per DEC-136 the fix started with a test-design batch given the finding as described behaviour (td-3, four cases red). A fresh engineer then fixed it, and round 2 confirmed the fix, with both directions covered by the cases.
  - RV2 to RV6 are rows, judged `other` or out of scope, and the round 2 fix leaves them unchanged:
    - RV2: a malformed approval sent beside good ones is named in the claiming pass's status only.
    - RV3: a batch whose wrapper is killed with no exit file holds landings as "still running". The Interface defines finalisation by the exit file, so this is for the CTO.
    - RV4: a re-approval at a failed head is dropped without a word ("never twice").
    - RV5: a heavy step under a shell wrapper is reported outside a slot. It is a false finding, never a missed one.
    - RV6: a landing item with several W2 ids holds no start, because part a's start check compares the whole field. Out of scope.
  - Round 1 also gave one narrow Wave 3 row: finalisation records the claimed file's lines, not the batch actually read. Ordinary work: no.
  - Round 2 found no new finding.
- **Judgement: pass.** S1 to S4 pass at `dae1c10e0392`. This was the last round.

## The reviewer's record, round 2 (as returned)

````
