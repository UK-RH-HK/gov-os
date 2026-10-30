---
type: probe
task: DAEO-2gc7
reviewer_session: 7c28b0d3-a218-47a8-ae88-043c99b67f4b
implementer_session: "0959d62f-294a-4664-8baf-a3a5941301f1, fec0320a-a8ef-4b38-a0bd-e607d45429e7, ef0d7c9f-042d-44b4-9347-8bc1f38f0ae0"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: fd88e61072ebbe9f591c288e139481b58f5f5cf0
---

# PR-DAEO-2gc7: probe of W2-68 (batched closes, reuse on the same code, two fingerprints)

## The lead's note

- **Commissioned and judged** by the ticket lead (an orchestrator-role session in this ticket's worktree, DEC-137). The reviewer was a fresh `independent-auditor` session (`7c28b0d3-a218-47a8-ae88-043c99b67f4b`, 2026-10-29), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max. It wrote nothing: the lead's tripwire before and after its session shows no change in this worktree or any other tree.
- **The implementer sessions** (engineer, each through `gov launch`, sandboxed): `0959d62f-294a-4664-8baf-a3a5941301f1` (the fingerprints, the store, the store check, `refresh`), `fec0320a-a8ef-4b38-a0bd-e607d45429e7` (the batch's run, reuse, the close's lines, the red-run hold), `ef0d7c9f-042d-44b4-9347-8bc1f38f0ae0` (the trial). The design note's first two commits were `3d9cc8b7-1915-44f8-96fa-82adf82f338b`; the acceptance tests `d10b6078-8dd1-46ad-8e5d-576e2eff5727` (independent test designer).
- **The lead's verification at the probed head** (`fd88e61072eb`, after a full rebuild, exit 0): `gov.__file__` in this worktree; collection 16,747 of 16,749 tests (2 deselected), no error; `gov check` exit 0 (23 checks, two YELLOW: `core-decision-citations` on older commits' citations, `openspec-validate` with `openspec` not on the check's PATH; no red); the full parallel run in the close's form 16,536 passed, 31 skipped, 0 failed (44:02); the serial-only list's 63 entries alone 180 passed, 0 failed (18:30); the trailer gate 15 commits, 0 lacking.
- **Verdict: pass.** Classification (DEC-809): 0 findings "yes" with "fails open" or "loses work". F1 no / loses work (a row, and package P-W2-68-PRUNE: the batch's regression reaches W2-66's nightly run, which DEC-915 item 4 keeps out of use until row W2-M406's fix; recommended as an entry criterion of switching the close queue to the batch, DEC-803); F2 to F5 yes / other (rows); F6 no / other (feature-gated, DEC-803). The lead's judgement agrees with the reviewer's.

## Head probed

`w2/W2-68` at `fd88e61072eb`, branched from `w2/integrate` at `966b9f6b5596`. Every run used the worktree's own `src/` (`gov.__file__` = `/home/usain/gov-os-worktrees/W2-68/src/gov/__init__.py`). The reviewer session id is taken from the session's scratchpad path.

## Method

- **Read:**
  - the ticket file: its KPI lines and its allowed paths;
  - the design note (sections 11 and 12 hold over the earlier ones);
  - DEC-883, DEC-889 items 2 and 4, DEC-890, DEC-803, DEC-915 item 4 and DEC-932 item 7;
  - the change against `w2/integrate` (the batch, the fingerprints, the close's calls and record lines, the store check, the store's row and record load), with its builder tests and the acceptance tests and README;
  - W2-66's selection, evidence and nightly, W2-57's serial routes, the test map and the path map.
  - `gov retrieve` was used once. It found row W2-M406 and W2-66's probe R8.
- **Ran:**
  - the builder tests: 35 passed;
  - `tests/acceptance/W2-68`: 22 passed in 189 s;
  - W1-30's re-read case: 1 passed.
- **Probed** on temporary repositories built from scratch in the session's temporary folder (W2-68's acceptance support imported for the whole-batch cases), each removed at its end:
  1. The fingerprints of record-only, code, path-map, test-map and invalid-map commits, and their cost on this repository: 0.05 to 0.1 s for 2,360 entries.
  2. Reuse and the red-run hold against planted run records: a newer red night; a newer green full close after a red batch; a truncated JUnit file; a suite-level error; an xfail; an empty check result.
  3. The store: its row after a rebuild; after a record-only commit; after a record load whose index refresh fails; the record load's digest against a full load's; after a code commit; in a project with no test map.
  4. Whole batches:
     - the first ticket's close refused;
     - one ticket named twice;
     - a code commit landing during the batch's regression;
     - serial-only entries routed to the nightly;
     - a second worktree of the project's repository, holding a staged change, out of the batch process's view while the batch ran (its folder moved aside), with a control run without the batch.
  5. On this repository, read only:
     - its registered worktrees: 20, none locked, none prunable from this session;
     - its serial-only routes: 15 of 63 entries go to the nightly, all 24 load-sensitive entries among them.

## Found sound

- **The fingerprints.**
  - A record-only commit keeps the code fingerprint and changes the records fingerprint.
  - The path map, the test map and its schema count as code even when the record-only list names them.
  - A map that does not parse or fails its schema gives no fingerprint. Every caller then runs fresh.
- **Reuse.** A run is never reused when it:
  - is red, or failed;
  - names no JUnit file, or one that is missing;
  - has a JUnit file cut short, truncated, or holding a failure;
  - states a skip count its files contradict;
  - is on another code fingerprint.

  An xfail is counted and stated as a skip. An empty check result makes the close run its own `gov check`.
- **The red-run hold.** After a red batch, a later close on that code is held, even when a newer green full close record exists. Only a green night or batch on that code lifts the hold.
- **The store.**
  - It is stale after a record-only commit until the record load.
  - A record load whose index refresh fails leaves it stale.
  - The record load leaves the same digest as a full load.
  - A code commit makes the record load refuse `STORE_CODE_CHANGED` and the close refuse `STORE_STALE`.
  - With no test map, only a rebuild of HEAD itself is fresh.
- **The batch.**
  - A refused close ends it with exit 3, and the tickets after it are not closed.
  - The green run record stays committed. The close committed its own repair ticket, so the tree was clean.
  - A red batch closes nothing (acceptance).
  - A code merge during the batch is refused.

## Findings

### F1: The batch's regression drops the registration of any worktree of the repository that its process cannot see (medium)

- **What was done.**
  - A fixture project with ticket A ready.
  - A second worktree of the project's repository, holding a staged change.
  - Its folder moved aside for the duration of `python3 -m gov.close.batch run PROJ-aaaa`, standing for a folder outside the batch process's view, then put back.
  - Control: the same hidden folder, three commits and git's automatic garbage collection, with no batch.
- **What happened.**
  - The batch passed (exit 0) and closed A.
  - The second worktree's registration and admin folder were gone, and with them the index holding its staged change. Git answered "not a git repository" in its folder.
  - The control kept its registration.
  - The batch's full regression is W2-66's nightly run, which ends by pruning every worktree record of the repository. The owner keeps that run out of use until row W2-M406's fix (DEC-915 item 4, restated in DEC-932 item 7). The fix has not landed, and the design note does not name it.
- **What should have happened.** The batch's regression removes only the worktree it added, or runs on a clone of its own. Otherwise the batch waits for W2-M406's fix, as the owner ordered for the nightly command.
- `Ordinary work: no, because it needs a worktree folder that is hidden or missing from the batch's process when its regression ends; from this session all 20 registered folders of this repository were visible and none was prunable, as W2-66's probe R8 found for the same mechanism.`
- `Consequence: loses work` (the hidden worktree's index and its link to the repository).
- **Routing.** This is a row by the rules. It still conflicts with a standing owner order, so it goes as package P-W2-68-PRUNE: W2-M406's fix becomes an entry criterion of switching the close queue to the batch (DEC-803).

### F2: A red night on the same code does not hold a later close, which reuses an older green batch run (low)

- **What was done.** A green batch record on head H, with its JUnit file. Then a record-only commit, and a red night record on the same code. The close's hold and reuse were then asked.
- **What happened.** Nothing held the close, and reuse chose the older green batch run.
- **What should have happened.** This is the residual the design note's section 9 names. DEC-883 item 3 allows "the last fully passing run", and no rule in force holds a close on a red night. Today no night reaches the judge at all: the nightly is `tools/nightly.sh`, whose records the judge does not read.
- `Ordinary work: yes, because a night runs between batches and a red night on unchanged code (a flaky case, a change of the machine, a miss of the record-reading set) is routine.`
- `Consequence: other` (the close cites a green full run on byte-identical code. A W2-66 scoped close would not be held either, though it would also run the unit suite and the every-close targets.)

### F3: The batch's full regression leaves out the serial-only entries routed to the nightly, and its record says nothing of them (low)

- **What was done.** The fixture's two serial-only entries routed to the nightly in a base commit, then a batch of ticket A.
- **What happened.**
  - The batch was green.
  - The two routed cases did not run and are not in its JUnit file.
  - The record states 17 passed, 0 skipped, skip count 0.
  - A's close reused that run.
- **What should have happened.** The serial-only list's header says every entry runs in the nightly. W2-66's nightly runs the close's two phases, which leave routed entries out of both. A full close leaves them out in the same way.
- `Ordinary work: yes, because this repository's list routes 15 entries to the nightly.`
- `Consequence: other` (the batch's run equals a full close in the close's form; this is inherited from W2-66's nightly and W2-57's routes, a row for their owners.)

### F4: A code merge during the batch leaves the batch's run record uncommitted and unstated (low)

- **What was done.** A code commit landed in the project right after the batch's regression.
- **What happened.**
  - The batch refused `BATCH_CODE_CHANGED` (exit 1).
  - Its green run record stayed untracked in the nightly folder.
  - The answer names the record's path but not its verdict.
  - The next `gov close` refused `TREE_NOT_COMMITTED`.
- **What should have happened.** The refusal states the run's verdict, and says that the record is left for the orchestrator to commit or remove.
- `Ordinary work: yes, because a merge landing during a batch is a plausible slip against DEC-883 item 1 c's wait.`
- `Consequence: other` (it fails closed and loses nothing.)

### F5: A ticket named twice is accepted at the batch's first step (low)

- **What was done.** `run PROJ-aaaa PROJ-aaaa`.
- **What happened.** The ticket closed once, and the commit stands. The batch then ended `BATCH_CLOSE_REFUSED`, exit 3, on `STALE_EVIDENCE` "already closed".
- **What should have happened.** A repeated ticket is refused, or named once, before anything runs.
- `Ordinary work: yes, because a repeated id in a queue list is an ordinary slip.`
- `Consequence: other` (it fails closed; nothing is lost.)

### F6: Every close of a batch is handed the batch's check result, also when it runs fresh (low; not reproduced)

- **What was done.**
  - Read how the batch calls each close, and how the close hands its check result to its test runs.
  - Searched the suites for a reader of that variable.
  - No run was possible, because no reader exists.
- **What happened.** Each close's test runs are given the result made at H, even when the close does not reuse and runs its own `gov check`. That happens when the fingerprints cannot be computed or the code changed during the batch. No test of this repository reads the variable today.
- **What should have happened.** A close that runs its own check hands its tests that check's result.
- `Ordinary work: no, because no test of this repository reads the check result the close hands its runs.`
- `Consequence: other` (once a record-reading case reads it in place of running `gov check`, it would judge another commit's result: an entry criterion of the ticket that adds such a reader, DEC-803.)

## Classification

- F1: ordinary work no, loses work. A row, with package P-W2-68-PRUNE as an entry criterion before the batch is switched on.
- F2 to F5: ordinary work yes, other. Rows.
- F6: ordinary work no, other. Feature-gated.

No finding is both ordinary work and fails open or loses work, so the probe passes.

## Notes for the lead and the auditor

- **KPI line 6.** It asks for a Rewrite-Reason. No Rewrite-Reason commit was made: the README's "W1-30's case re-read" explains that no expectation changed. The case passes at this head.
- **The design note.** Sections 3 and 11 E say a refused close's repair ticket is left uncommitted. In the run, the close committed it itself.
- **The reused regression drops the every-close targets.** These are W1-07's three contract files; one of them is also in the record-reading set. This is consistent with DEC-883 item 1 b, and the acceptance fixture leaves the targets out on purpose.
- **Machine and session.**
  - The probe runs were made with the 1-minute load below 3. It rose to 36 afterwards, from outside this session, and no test ran after that.
  - The untracked dot-files `git status` shows at the worktree's root are the sandbox's placeholder devices, not files of this session.
