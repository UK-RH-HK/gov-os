task: Judgement-only re-probe (owner, DEC-895 item 2) of DAEO-cy5o (W2-57) at `bd418982e6c0`, after the merge of W2-68 changed `src/gov/close/command.py`; return the probe record's content.
status: DONE. Verdict pass: no finding, two observations (A yes / other; B no / other, feature-gated), and review 2's F1 to F4 and run 3's O1 stand.
work_completed: Did step 0 and the identity checks. Checked the judged-and-changed intersection myself: it matches the lead's two files. Read the `command.py` diff, W2-68's `batch.py` and `fingerprint.py`, and the `repo.py` change. Counted the reuse candidates in the main tree, read-only. Built one temporary project with W2-68's builder (on W2-66's fixture) and its own routed serial-only list, and closed planted cases there: a full close then a close that reuses its run, a route change, faulted commit gates beside junk run records, a pre-close refusal, and a red batch record on HEAD's code. Ran the close's probe gate read-only at this head, and W2-57's route acceptance file.
files_changed: none
evidence: `gov.__file__` is `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`. Step 0: (a) failed with Errno 30; (b) wrote blob `1ae28402a109`, and the refresh exited 0. Planted probe: 1 passed in 15.9 s, then 30.9 s with two checks added; its observations are in the record below. Read-only probe gate at this head: PASS, measuring `27f290a2beef`, `848f5ab366b9`, `4904a60f420d` and `b52e3a9615c1` as git's own merge. Scratch: 8 inodes / 24 KB at start, 17 / 92 KB before the planted closes, 23 / 140 KB at the end.
tests: `tests/acceptance/W2-57/test_w2_57_nightly_route.py` 3 passed (33.3 s). The planted probe file (temporary, outside the repository) passed both times. Nothing else was run.
discoveries: Reuse already works in a plain `gov close` at this head, not only in the batch: committed full close records are candidates. In the main tree, two full close records (W2-68's and W2-75's) already meet every reuse condition except "same code". Separately, a red batch record on HEAD's code refuses the close before the commit gates and hides their findings; this only matters once the batch is switched on.
risks: Once the batch is on, the batch's governance check stands in for `gov check` over records-only commits made after the batch's head. That is W2-68's documented design and is feature-gated; it touches nothing W2-57 governs.
lessons: To probe reuse, close one ticket with `--full`, then another on the same code; W2-68's builder does it in about 30 s. Run 3's O1 still holds: the close's own probe gate does not see a behaviour change carried in by a clean merge.
proposed_decisions: none
unresolved: Nothing for this ticket. Observation B can go to W2-68's owners as an optional entry criterion for switching on the batch.
recommended_next_action: Commit this record as the ticket's probe record, with `probed_commit` set to the full id of `bd418982e6c0` and reviewer session `2d310c50-9b13-496f-b973-32c91ba8b57a`, then continue W2-57's close.

---

Verdict: pass

**Head probed:** `bd418982e6c0` on `w2/W2-57`; its code is identical to the merge `27f290a2beef`. Since `8d9d78d93529` the branch has gained run 3's record, the lead's merge of `w2/integrate` at `848f5ab366b9` (W2-68), and the lead's checkpoint `CP-DAEO-cy5o-0015`.

**Step 0:**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o` failed: `OSError: [Errno 30] Read-only file system`, exit 1.
- (b) `git hash-object -w --stdin` worked (exit 0, blob `1ae28402a109`), and so did `git update-index --refresh` (exit 0).
- Identity:
  - `GOV_ROLE` is `independent-auditor` and `GOV_TICKET` is `DAEO-cy5o`.
  - The toplevel is `/home/usain/gov-os-worktrees/W2-57`, on `w2/W2-57`, and HEAD is `bd418982e6c0`.
  - `git status` showed the 11 placeholder mounts and nothing else, at the start and at the end.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`. The planted closes ran through W1-07's launcher on this worktree's `src/`.

**Classification (DEC-809):** no finding; observation A yes / other, observation B no / other (feature-gated, DEC-803); review 2's F1 to F4 and run 3's O1 stand; nothing is both "yes" and "fails open or loses work".

**Intersection of judged and changed files:**
- The judged files are those of the ticket's own commits up to `8d9d78d93529`: 27 commits, 50 paths.
- `git diff --name-only 8d9d78d93529 HEAD` names 51 paths.
- They share two files: `src/gov/close/command.py` and `docs/plan/WAVE_2_WBS.md`.
- **`WAVE_2_WBS.md`:** 14 lines added and none removed. They are the new W2-75 card, at line 1253. W2-57's card, at line 913, is untouched.
- **`command.py`:** only W2-68's hunks changed. These parts are byte-identical to `8d9d78d93529`:
  - `_run_tests`, with the serial phase's call to `serial.phase`;
  - every commit gate;
  - gate (h)'s `recorded` line.
- **Unchanged since `8d9d78d93529`:**
  - `serial.py`, the plugin folder and `tests/acceptance/serial-only.txt`;
  - `nightly.py`, `gates.py`, `select.py` and `evidence.py`;
  - `src/gov/doctor/command.py` and `src/gov/adapters/portability.py`.
- **`repo.py`:** its `store_is_of_head` changed, and it only got stricter. The old condition must still hold, and then also the store's fingerprint row. It can turn a pass into `STORE_STALE`, never the reverse.

**Can reuse happen in ordinary work at this head? Yes, without the batch.**
- No nightly or batch record exists: there is no `docs/close/nightly/` in the main tree or in this worktree. So the red-run hold never fires, and the reused check never stands in.
- But reuse's candidates include committed full close records (W2-68's design note, section 4).
- Read-only, in the main tree at `w2/integrate` `d808292d88e1`, there are 4 full close records:
  - `CL-DAEO-2gc7` (head `94e7115cd59a`) and `CL-DAEO-ebmh` (head `2f2fb03e5076`) meet every condition except the same code;
  - `CL-DAEO-c1uz` and `CL-DAEO-uzme` are marked failed.
- So the first close that lands on the code of a full close will reuse that close's run (observation A).

## Probed and found sound

**The planted project.** One temporary project, built with W2-68's builder on W2-66's fixture. Its serial-only list has six entries:
- a `serial:` entry outside C's suite and outside the record-reading set (W1-bb);
- a `nightly:` entry (W1-dd);
- a `serial:` entry in C's own suite (W2-cc);
- a `serial:` entry on the record-reading case (W1-rr);
- an entry with an unknown route word, `overnight:` (W1-gg);
- a `serial:` entry that skips (W1-hh).

It also has W2-zz's planted skip, and tickets A, C and F (STANDARD) and E (FULL).

**1. The serial phase's entries.**
- **A's close with `--full`:** its scope was full.
  - Its serial-afterwards run's `cases` were exactly the five entries not routed to the nightly, in the list's order: W1-bb, W2-cc, W1-rr, W1-gg, W1-hh. 4 passed and 1 skipped.
  - Each of the five ran once, alone, in no worker.
  - W1-dd's entry ran nowhere. Its sibling case in another file of W1-dd ran in a worker.
- **C's close, after record-only commits on the same code:** its scope was `reused`, citing A's record.
  - **Acceptance:** the parallel run passed 1. The serial-afterwards run had `cases: [W2-cc's entry]` and passed 1, alone. So the ticket's own acceptance folder and its serial entry still run; the reused run does not stand in for them.
  - **Regression:** the record-reading set alone. The parallel run passed 0, because its one case is a serial entry. The serial-afterwards run had `cases: [W1-rr's entry]` and passed 1, alone.
  - **Nothing else ran.** W1-bb's, W1-gg's and W1-hh's entries did not run in C's close. The reused run had run them alone, and A's record names them in its serial-afterwards `cases`. C's `reused` block names A's record and its three JUnit files, `03-regression-serial-afterwards.xml` among them.
  - So in both closes, `test_runs` and `cases` state what ran.
- **An unreadable route stays serial** in both forms (W1-gg's `overnight:`).
- **A route change is a code change.**
  - Then W1-dd's entry was re-routed to `serial:`. The code fingerprint changed, and F's close ran full instead of reusing A's run.
  - In F's close, W1-dd's entry ran alone in the serial phase, in the list's order.
  - At this head, none of W2-57's governed paths is on the record-only list: the list, `serial.py`, the plugin, `command.py`, doctor, portability and W2-57's tests are all code. Only the ticket file is a record. So a reused run can never carry a change to the serial phase, the route, the rulesync probe or the doctor probes.

**2. The nightly route, and a reused run's skips.**
- **The nightly route is not widened.** W1-dd's nightly entry ran neither in A's full close nor in C's reusing close. That is the same as before (W2-68's F3, and review 2's F1 and O2).
- **Skips are stated.**
  - C's `reused` block states `skip_count: 2`, and its `skips` name W2-zz's planted skip and W1-hh's serial skip, each with its reason. C's own `skip_count` is 0.
  - The count is the number of `<skipped>` cases across every JUnit file of the reused run: acceptance and regression, both forms. It must equal the reused record's stated skip count (condition 5).
  - Deselected and nightly-routed cases are not skips, and the block does not claim them.
- **Nothing outside the route drops a serial entry.**
  - The reused form's only drop is a serial entry outside the record-reading set and outside the ticket's suite. It is not run again because the reused run ran it alone on byte-identical code.
  - A full close ignores only its own suite, which its acceptance run runs, and its plan deselects nothing.
  - A stale entry that names no case cannot pass through reuse. On the same code, the reused run's serial phase would have refused it, so that record would not exist.

**3. The order of the commit gates before any test.**
- **The order is unchanged.** Probe gate, trailers, accepted history, gate (h) and the ratchet lists all run before `_scope`, and their refusal is uncounted. The red-run hold runs earlier, beside the tree check and the store check.
- **E's close with faulted commit gates.** E (FULL) had no probe record, and a commit naming no task changed `src/gov/eel/e.py`. The nightly folder held junk run records: unparsable JSON, a JSON list, a batch record whose head is no commit, and a red batch record on another code fingerprint.
  - E's close was refused `CHECK_FAILED` with exactly the two findings: no probe record, and a commit naming no task that changes `src/gov/eel/e.py`.
  - The refusal reads `counted: false` and `test_runs: []`, and no test ran.
  - No JUnit folder was made for E, so `_scope` was not reached.
  - The tree was clean afterwards.
- **A's close without a checkpoint.** This is the pre-close gate, which now runs after `_scope`.
  - It was refused `CHECKPOINT_MISSING`, with `counted: false` and `test_runs: []`, and no test ran.
  - `_scope` had already made an empty JUnit folder under `.gov-runtime/close/PROJ-aaaa/`, which git ignores.
  - `git status` showed nothing afterwards, and A's next close passed.
- **Raises in the new calls.**
  - A fingerprint that cannot be computed comes back as "none", and every caller then runs fresh.
  - Unreadable run records are skipped, and a malformed close record reads as no frontmatter.
  - A missing, empty, truncated or failing JUnit file is never reused.
  - None of the new calls raises a finding of the close's gates, so none can count an attempt. An error they raise ends the close uncounted, before any test.
- **One change of behaviour,** feature-gated: observation B.

**4. The reused check.**
- **In ordinary work at this head, the reused check never stands in.**
  - Only a batch record names a check result. W2-66's night record has no such key, and close records give none.
  - C's reusing close ran its own `gov check`: the project's declared check counted one run.
  - C's record states `check_commit` (its head, `e557363bd605`) and no `governance_checks_reused`.
- **With the batch switched on (feature-gated, DEC-803):**
  - The batch's check at its head stands in for the close's own. So records-only commits after the batch's head get no fresh `gov check` in a reusing close; the design note gives them to the record-reading set (section 11, point A).
  - This does not touch what W2-57 governs. Every governed path is code, and any change to it ends reuse, so the close runs its own check again.
  - The commits list the close hands its check only decides whether the check runs. The batch's check is the same check, at the batch's head.

**W2-57's own tests at this head:** `tests/acceptance/W2-57/test_w2_57_nightly_route.py`, 3 passed.

**F1 to F4 and O1 stand.**
- None of the files behind F1 to F4 changed, so they stand with their classification.
- **O1** stands as written. Run read-only at this head, with run 3's record as the latest, the close's probe gate passes. It measures merges `27f290a2beef`, `848f5ab366b9`, `4904a60f420d` and `b52e3a9615c1` as git's own merge on the probed paths.
- So the close itself still does not flag run 3's record as stale after W2-68's merge. The fresh probe is required by DEC-895 item 2, and this record answers it. Once committed with the head's full id as `probed_commit`, it makes run 3's record an earlier round (W2-M209).

## Findings

None.

## Observations (no round)

**Observation A. A plain `gov close` now reuses a run, not only the batch.**
- **Done:** I closed A with `--full`, committed records only, then closed C with a plain `gov close` and no batch. I also listed the main tree's candidates, read-only.
- **Happened:**
  - C's close reused A's run, and its regression was the record-reading set alone.
  - In the main tree, two full close records already meet every condition except the same code.
- **Should have:**
  - This is the design: DEC-883 item 3, and the design note's section 4 lists committed full close records first among the candidates.
  - The merge's note, "the batch is not switched on until row W2-M406's fix", covers the batch, not reuse.
  - Under reuse, W2-57's serial phase, its route and the commit gates behave as required (questions 1 to 3 above).
  - A reader of a close record should know that `scope: reused` can now appear without any batch.
- **Severity:** none.

  Ordinary work: yes, because the first close on the code of a full close reuses that close's run (for example, two tickets merged before the close queue runs).
  Consequence: other

**Observation B. A red batch record on HEAD's code refuses the close before the commit gates, so their findings go unreported.**
- **Done:** I committed a red batch record on HEAD's code and closed E again.
- **Happened:**
  - E's close was refused `RED_RUN_ON_CODE`, exit 1, not counted.
  - It opened no repair ticket, ran no test and left the tree clean.
  - The probe gate's and gate (h)'s findings, which E's earlier refusal had reported, were not reported.
- **Should have:**
  - The refusal fails closed and spends no attempt, like the tree and store checks beside it.
  - But DEC-492 ("every gate is asked") holds for the commit gates, so the hold could report after them.
  - If wanted, this is an entry criterion for switching the close queue to the batch (DEC-803), for W2-68's owners.
- **Severity:** none.

  Ordinary work: no, because only the batch writes a batch record and the batch is not switched on (there is no nightly folder in the main tree or in this worktree).
  Consequence: other

## Scratch, refusals, retrieval

- **Scratch:**
  - 8 inodes / 24 KB at the start, 17 / 92 KB before the planted closes, and 23 / 140 KB at the end.
  - pytest's retention removed each passing run's project, and at most one fixture project existed at a time. I did not measure the peak during the runs.
  - All of this is far inside my share of 6 GB and 300,000 files and folders.
- **Machine:**
  - `CLOSE-RUNNING` was present from 00:07, and `NIGHTLY-RUNNING` was absent. The 1-minute load was 24 to 40.
  - I ran single test files only: the planted probe (one case, run twice) and the route file (3 cases).
  - Every run was at nice 19, and each fixture close used 2 workers.
- **Read refusals (DEC-849):** 0.
- **Guard refusals:** 0.
- **Sandbox:** the proxy twice denied `gov retrieve`'s outbound call to `ollama.com:443`. The retrieve still completed, with exit 0.
- **`gov retrieve`:** used once.
  - The question: does a close reuse a full close record's run before the batch is switched on?
  - Both facets were available, not stale, and the bundle ended with its budget used and gaps listed.
  - It returned the design note's sections 3 and 4, with the candidates list. I confirmed that list in `batch.py` and by running it.
  - The call ran past the tool's 120 s foreground limit, so the harness moved it to the background. I waited for it to finish (exit 0) and then read its answer.
- **Code-graph tool:** not used.
  - The call sites I needed are named in the `command.py` diff and in `batch.py`.
  - Targeted searches of named files were enough: `command.py`, `select.py`, `nightly.py` and `src/gov/check/`.
  - The tool's folder is also read-only in this sandbox until W2-56.