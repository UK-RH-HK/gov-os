I've finished the probe: **judgement pass**. No finding is both something an honest agent hits in ordinary work and one that fails open or loses work. There is one package the orchestrator needs to decide before the batch is used on the real repository: the batch's regression ends with a repo-wide `git worktree prune`, the code path DEC-915 item 4 keeps out of use.

task: Probe the W2-68 head (DAEO-2gc7, `fd88e61072eb`) for behaviour its acceptance tests miss, as brief A3's reviewer, writing nothing.
status: DONE. The probe passes. One package (P-W2-68-PRUNE) must be decided before `close_queue.sh` calls the batch.
work_completed: I read the ticket, the design note, the decisions, the change and W2-66's selection, evidence and nightly code. I ran the builder tests, the W2-68 acceptance suite and W1-30's re-read case. I probed the fingerprints, reuse, the red-run hold, the store and complete batches on temporary repositories built from scratch, using W2-68's acceptance support by import. The six findings are judged by the two questions.
files_changed: none in the repository. My probe scripts are still in `$TMPDIR/w268probe` because the permission system refused their removal; the temporary repositories were already removed.
evidence: identity checks returned `independent-auditor` / `DAEO-2gc7`, `/home/usain/gov-os-worktrees/W2-68`, `w2/W2-68`, `fd88e61072eb`. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-68/src/gov/__init__.py`. I used `gov retrieve` once ("W2-M406 nightly worktree prune fix"); it found row W2-M406 in `docs/plan/WAVE_2_LIST.md` and W2-66's probe R8. I met no read refusals. Refusals I met: one Bash call (removing my own probe folder, permission not granted, not retried), and the sandbox denied outbound access to ollama.com during the retrieve. F1's batch output: exit 0, the second worktree's registration and admin folder gone, `git status` there "fatal: not a git repository", and the control kept its registration. The only prune in `src/gov` is `src/gov/close/nightly.py:327`, reached from `src/gov/close/batch.py:346`. `nightly.py` was last changed at `c96866061ec0` (W2-66) and is unchanged on this branch and on `w2/integrate` (`b52e3a9615c1`). DEC-915 item 4 and DEC-932 item 7 say `gov.close.nightly` is not run until W2-M406's fix. The other probes' outputs are in the record below.
tests: builder tests (`tests/unit/close/test_batch_reuse.py`, `test_batch_refresh.py`, `test_fingerprint.py`, `tests/unit/store/test_fingerprint_store.py`) 35 passed in 1.02 s. `tests/acceptance/W2-68` (`-n auto`, `-o tmp_path_retention_policy=failed`) 22 passed in 188.57 s. W1-30's `test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later` 1 passed.
discoveries: (1) The batch brings `nightly.night`, which the owner ordered out of use, into every close queue. Its cleanup prunes every registration whose folder the process cannot see (W2-M406), and neither the design note nor the batch mentions it. (2) `gov.close.nightly.night` runs the close's two phases, so none of the 15 entries the serial-only list routes to the nightly runs in it. The list's header says every entry runs in the nightly. (3) The real nightly is `tools/nightly.sh`, whose records the judge does not read (DEC-932 item 7). So today neither reuse nor the red-run hold sees any night. (4) All 24 `load_sensitive` entries are nightly-routed, so the batch never meets them. (5) A refused close commits its own repair ticket (AR-9). The design note's "left uncommitted" is inaccurate, and harmlessly so.
risks: F1's "ordinary work: no" rests on what this session can see (all 20 registered folders, none prunable) and on W2-66's R8. A session that cannot see some worktree folder makes F1 an ordinary loss of work. All behaviour was probed on fixtures, not on the real programme.
lessons: The batch reuses W2-66's nightly as it stands, so it inherits that nightly's open rows (W2-M406, and the routed entries left out). Check the rows and owner orders that stand on a function before building a new caller of it. The acceptance fixture leaves out `every_close`, so the reused form's dropping of it is untested by design.
proposed_decisions: P-W2-68-PRUNE. Classification: F1 ordinary work no, loses work; no round proposed. Options: (a) apply now: the batch runs its regression without the repo-wide prune, for example in a clone of its own as `tools/nightly.sh` does (a W2-68 round and a fresh probe); (b) defer as an entry criterion (DEC-803): W2-M406's fix ("the cleanup prunes only the nightly's own clone, by its exact path") lands before `close_queue.sh` calls the batch or the third re-pin carries it (no round now; one small engineer row in `nightly.py`); (c) re-baseline: the owner lifts DEC-915 item 4 for the batch. I recommend (b), confidence medium-high: merging W2-68 runs nothing on the real repository, and one fix serves both callers. Rows F2 to F6 go to the list.
unresolved: whether the orchestrator's session can see every worktree folder at batch time; whether `tools/nightly.sh` runs the routed entries (I could not read it from here); removal of my probe folder in `$TMPDIR`.
recommended_next_action: The orchestrator records W2-M406's fix as an entry criterion of switching `close_queue.sh` to the batch, files rows F2 to F6, and sends W2-68 on to its audit.

---

```markdown
---
type: probe
task: DAEO-2gc7
reviewer_session: 7c28b0d3-a218-47a8-ae88-043c99b67f4b
implementer_session: see the lead's note
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: fd88e61072ebbe9f591c288e139481b58f5f5cf0
---

# PR-DAEO-2gc7: probe of W2-68 (batched closes, reuse on the same code, two fingerprints)

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
```