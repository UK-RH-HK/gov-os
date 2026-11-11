---
type: probe
task: DAEO-9nys
reviewer_session: 75a5fb44-6607-4386-ab23-4b87f0fa174b
implementer_session: 8a693c0b-3078-481b-ad80-99104401fbb7
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 90d41204d412b09f348c422fce9cdce95870bd4e
---

# Probe record: W2-67 (DAEO-9nys), run 6: the merge of w2/integrate (DEC-954) and its one repair batch

- **What was probed.** Run 6 merged `w2/integrate` (`c07a1115577f`) into `w2/W2-67` (merge `0568d91baf56`, 2026-10-31). The merge had to resolve one conflict, in `tests/acceptance/W1-30/test_w1_30_close.py` (the KPI S1 case `test_task_trailer_exact_match_not_substring`: W2-64's schema-valid ids against this ticket's PF15 revision). A fresh independent test designer resolved it (td-9, session `4e4a6cce-c3a2-492e-b120-e905a6f27271`). Under DEC-953 (its lifted DEC-895: a new review only where a merge resolved conflicts in files a review judged), two reviews ran on that change only, each a fresh read-only reviewer (role `independent-auditor`, through `gov launch` under its OS sandbox, reading tools only, effort max), commissioned and judged by the ticket lead:
  - **rev-5** (session `29477cee-8ee8-442a-9ee4-e3872ad1fcad`), on head `3a2f2a1f0497` (the merge plus checkpoint CP-DAEO-9nys-0022): the resolution. **Pass**, with F1 (medium; with W2-64's ids the close's fixed-string search hides AB's commit, so the case no longer turned red under PF15, seen under the plant) and F2 (low; the README-W2-67 row stale). Both "Ordinary work: yes", "Consequence: other".
  - **The one repair batch** (DEC-136: the finding given as behaviour): a fresh independent test designer (td-10, session `8a693c0b-3078-481b-ad80-99104401fbb7`), commit `a8c0920abead` (`Rewrite-Reason: DEC-954 merge of W2-64: the merged ids hid PF15 behind the close's search, so the case no longer caught its plant`): a near-miss commit `Task: PROJ-tkaab` (A's id plus one character, naming no ticket) in the same case, and the README-W2-67 row and a run-6 section.
  - **rev-6** (session `75a5fb44-6607-4386-ab23-4b87f0fa174b`), on head `90d41204d412` (the repair plus checkpoint CP-DAEO-9nys-0025): the repair's change, `3a2f2a1f0497..a8c0920abead`. **Pass**: F1 and F2 fixed (under PF15 1 failed for PF15's own reason, marker "matched by substring: 1, of them exactly: 0"; without it 1 passed); nothing lowered; scope as stated. Two low findings on README-W2-67's wording (G1, G2), both "Ordinary work: yes", "Consequence: other".
- **Which review this is.** These are reviews of the run-6 merge resolution and its repair, not new rounds (DEC-916); rev-6 is the second and last review of this change (DEC-413). The three declared rounds keep their passed records (`PR-DAEO-9nys.md`, `PR-DAEO-9nys-run3.md`).
- **The tripwire.** Before and after each reviewer: no change in this worktree or the main tree (other worktrees moved by their own leads and the store refresh only).
- **The lead's verification on `90d41204d412`** (this worktree's `src/`; `gov.__file__` = `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`):
  - rebuild (under the rebuild lock, never `--no-embeddings`): exit 0, `store.invalid: []`;
  - the selection (`select_tests.py`): scope `scoped`, `core_changed` [], `unplaced` [], 36 targets; no "serial"-route entry reached, so no serial phase;
  - the scoped run in the close's form (`-n auto`, `-p gov_close_serial_only`, `--timeout=900 --timeout_method=signal`, `-o tmp_path_retention_policy=failed`, the selection's `--ignore`/`--deselect`): **1 failed, 4965 passed, 1 skipped in 1570.68 s**. The red: `tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure`, red alone too. Cause: the merge's clean auto-merge of that file kept W2-64's fixture ids (`DEC-9003`, `DEC-9004`) beside this ticket's revised assertion on the old ids (`DEC-cyc1`, `DEC-cyc2`); git reported no conflict there, and neither review judged that file. It is this ticket's to fix (a two-line test-design change); the one repair batch being spent, it is returned to the orchestrator as a package (P-W2-67-R6-DISP);
  - KPI 4's count: four base folders right after the run (pytest's three retained nested-session folders and the outer run's own, kept for the one red's `tmp_path`); the next pytest session pruned them to three;
  - TD1C-A's case, run by the lead outside the sandbox: 5 passed in 48.29 s; daemon folders under `/tmp/gov-cbm-<uid>` 17,691 before and after;
  - collect-only over `tests`: "17475/17477 tests collected (2 deselected)", exit 0; `gov check`: core-mutation RED for W2-76's ticket file (the same on `w2/integrate`), two YELLOW, the rest GREEN.
- **Threat model (DEC-801, DEC-808).** Every finding is judged by ADR-0001's two questions; only "yes" with "fails open" or "loses work" fails a probe. **The lead's judgement: pass.** F1 and F2 (rev-5) are fixed by the repair; G1 and G2 (rev-6) are "Ordinary work: yes", "Consequence: other": residual rows on README-W2-67's wording. The verification red is not a review finding: it is the package above.

## rev-5's record

task: Review, at effort max, only the one conflict the merge of `w2/integrate` (`0568d91baf56`) resolved in a file the earlier review judged: `tests/acceptance/W1-30/test_w1_30_close.py`, the KPI S1 "Task: AB" case. Head probed: `3a2f2a1f0497`; nothing written.
status: DONE. Verdict pass. The resolution keeps every assertion of both sides, but on the merged head the case no longer catches the recorded PF15 (seen in my probe). That finding's consequence is "other", so it does not fail the probe.
work_completed: Step 0 and the identity checks. Read the merge against both parents and the merge base, recomputed it with `git merge-tree` and compared the file lists and changed lines of each side. Read how the close matches a ticket's commits and td-6's PF15 plant of record. Wrote my own PF15 plant in my temporary folder and ran the single case twice: once without the plant, once under it. Checked the ticket-id grammar by proof and by enumeration. Searched W1-30 and the unit suite for cases that catch a start-only match. Read td-9's return.
files_changed: none in the repository. My temporary folder holds the plant, its marker and a copy of the merged file. Step 0's blob and `git merge-tree`'s unreferenced objects went to the object store; no ref changed.
evidence: Merge `0568d91baf56` has parents `bdc1bb3e1d43` and `c07a1115577f` (Task: DAEO-9nys, Implements: DEC-954, DEC-941, Role: orchestrator, Rewrite-Reason: DEC-954 merge of W2-64; its message says "Nothing lowered"). The head `3a2f2a1f0497` adds only `docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0022.md`. W2-64's commit `be76f9a39ef7` (Task: DAEO-0uhh, Role: independent-test-designer, Rewrite-Reason: DEC-872 item 2). `git merge-tree --write-tree` gives one conflict, in this file (tree `4d0c4988525f`), and differs from the merge only in this file's conflict region. The close's matching is at `src/gov/close/repo.py:70-73`; td-6's plant at `.gov-runtime/scratch/td-6/plant/site/sitecustomize.py:95-105`. My marker: under the plant the close of `PROJ-tkaa` (pid 53, code loaded from the worktree's `src/gov/close/command.py`) got 0 commits; a substring match without git's search would have got 2 (`9e645064a037`, `cee74b82aa34`, both `Task: XPROJ-tkaa`). Round 1 with the old ids (td-6's `after-PF15.xml` and its marker): 2 commits matched by substring, `gov close PROJ-tska` exited 0, and the case failed with "gov close was not refused".
tests: Every run used `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src`, `-o tmp_path_retention_policy=failed`, `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`. The resolved case alone without a plant: 1 passed in 10.04 s. The same case alone under my PF15 plant (td-6's form): 1 passed in 10.87 s, so it did not catch the plant. No suite was re-run.
discoveries: The close first asks git for commits whose message contains the text `Task: <ticket>`, and only then checks the trailer value exactly. With W2-64's ids, AB's id is A's with one character in front, so git's search never returns AB's commits. A fault that loosens only the exact check is therefore invisible to this case, and td-6's PF15 of record is that fault. td-9's return says the case "still catches `id in value`"; that is true only if the fault also widens git's search, and td-9 ran no plant. Under the ticket schema no valid id is another valid id plus trailing characters, so no fixture with two valid tickets can show the recorded PF15.
risks: On the head, the recorded PF15 is caught by one unit case only (`tests/unit/close/test_gates.py:72-78`). That is the state lens I2 flagged (`I2-close-checks-ratchet.md:605`, regression evidence, not acceptance, DEC-042). A close record that counts this case as red under its plant (KPI 5) would not be true of the head. The outcome under a broader substring fault is inferred, not run.
lessons: When a merge changes a case's fixture, re-run that case's plant of record once before writing "nothing lowered". When reasoning about which match faults a fixture can show, read the code's own pre-filter (here git's `--grep`), not only its final check.
proposed_decisions: On td-9's P-W2-67-PF15-PREFIX I recommend option (2): an acceptance commit whose `Task:` value is A's id plus one character and names no ticket; the close must still refuse with the trailer gate and must not name that commit. It restores the catch of the recorded PF15 itself, not of a variant beside it. It rides along in any resume of W2-67 (DEC-802), otherwise it is a row for a test-designer follow-up. Until then the probe record and README-W2-67 should say that on the head the unit case alone holds it. Confidence: high on the facts, medium on the choice of option.
unresolved: Whether this ticket's fifth KPI line counts as met for this case on the head is for the lead or the owner to read. The lead's scoped run was not awaited. The broader-fault outcome was not run (one plant run allowed).
recommended_next_action: The lead commits this record (Verdict: pass, F1 and F2), corrects "nothing lowered" for PF15, and decides P-W2-67-PF15-PREFIX on these facts.

---

Verdict: pass

**Head probed:** `3a2f2a1f0497`, the lead's checkpoint CP-DAEO-9nys-0022 on top of the merge `0568d91baf56`; it adds only that checkpoint record.

**Step 0:**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys` failed with OSError Errno 30, read-only file system. No file was made.
- (b) `git hash-object -w --stdin` worked (`1ae28402a109`) and `git update-index --refresh` exited 0.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"` gives `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`.

**Classification (DEC-809):** 2 findings, F1 and F2, both "Ordinary work: yes" and "Consequence: other". Neither fails open or loses work, so neither justifies a round.

## What was probed and found sound

### 1. Both sides' intent: kept on the page, with one loss (F1)

- **Every assertion of this ticket's revision is kept:**
  - A's checkpoint;
  - the fixture guard (A has no commit);
  - the refusal with exit 3, which includes W2-64's only check, that the close is refused;
  - the trailer gate's text, `Task: PROJ-tkaa` exactly;
  - AB's commit not named;
  - A not closed.
- **W2-64's schema-valid ids are everywhere in the file:**
  - `TICKET` PROJ-aaaa and `WBS` W1-946;
  - the case's PROJ-tkaa, XPROJ-tkaa, W1-947 and W1-9471;
  - `other_wbs` W1-923 and the planted folder `tests/acceptance/W1-923/`.
  - Every ticket and wbs id in the file passes `common.schema.json`. The pair W1-947 / W1-9471 keeps the old wbs prefix relation, as W2-64 says ("prefixes kept").
- **The docstring and W2-64's comment are true of the ids:** both are valid ticket ids, AB is A's id with one character in front, and AB is never closed.
- **What is lowered** is not any assertion but the case's power against its plant of record (F1). The case's record row is now stale (F2).

### 2. PF15 on the merged close: the recorded plant is no longer caught

- **My plant** lives in my temporary folder. A pytest plugin wraps `w1_30_support.sandbox_env` so each `gov` process the case starts has my `site/` folder first on its `PYTHONPATH`. That folder's `sitecustomize` applies td-6's PF15 as `gov.close.command` loads, and writes a marker line each time the plant runs. td-6's PF15: the commits of a ticket are those git's fixed-string search for `Task: <ticket>` finds and whose `Task:` values contain the ticket id anywhere.
- **Without the plant:** 1 passed in 10.04 s.
- **Under the plant:** 1 passed in 10.87 s.
  - The marker shows the plant loaded from the worktree's `src`.
  - In the case's own close it returned 0 commits for PROJ-tkaa: git's search had already left out AB's two commits.
  - A substring match without that search would have counted both.
- **Round 1, old ids, same plant:** 2 commits counted by substring, A closed with exit 0, and the case was red.
- **So the merged case fails only under a substring fault that also widens or drops git's search.** That is inferred from the marker and from round 1's close of A, not run.

### 3. td-9's note, judged by the two questions

- **Can a real ticket id be another valid id plus trailing characters? No.**
  - `ticket_id` is a prefix without hyphens, one hyphen, then exactly four characters (`common.schema.json:9`). Any trailing characters push the part after the hyphen past four.
  - Enumeration agrees: 0 such pairs among 1,920 ids over a four-character alphabet. Pairs with A at the end of AB, like W2-64's, do exist.
  - So a start-only match cannot count another real ticket's commits as A's. That bounds the consequence.
- **Does another case catch a match with no end anchor? One unit case only:** `tests/unit/close/test_gates.py:72-78`.
  - Its commit carrying the ticket's id plus one character, and its commit with the trailer text outside the trailers, must not count as the ticket's.
  - No W1-30 case does after the merge.
- **The note understates the gap.** As the close is built, its start-only form is the recorded PF15 itself.

### 4. Scope: nothing of either side is dropped

- **`git merge-tree`** of the two parents reports exactly one conflict, in this file. The merge's tree differs from merge-tree's result only in that file's conflict region.
- **Against each parent:** the merge differs from the first parent in exactly the 141 files `w2/integrate` changed since the merge base `f21ede6ef198`, and from the second parent in exactly the 26 files this ticket changed.
- **Shared files:** seven files changed on both sides; six auto-merged, identical to merge-tree's result.
- **Line by line:** outside the conflict region, every changed line of each side is in the merge.

## Findings

### F1: the merged case no longer catches the recorded PF15

- **What was done:** the resolution took W2-64's pair, where AB's id is A's with one character in front, and kept this ticket's assertions. The merge message says nothing was lowered.
- **What happened:**
  - The close first asks git for commits whose message holds "Task: " followed by the ticket's id, and only then requires that id as a whole trailer value.
  - With the new pair, git's search never returns AB's commits. A fault that loosens only the exact step, which is td-6's PF15 of record, therefore never sees them.
  - The close refuses for the missing trailer exactly as it does on the head, and the case passes under the plant (observed).
  - Before the merge, under the same plant, the close closed A on AB's commits and the case was red.
  - td-9 reasoned that the case still catches a match anywhere inside the trailer, but ran no plant.
- **What should have happened:** the case on the head should still turn red under its plant of record, as this ticket's fifth KPI line and the round-1 review record (`PR-DAEO-9nys-run3.md:67`).
  - Two schema-valid tickets cannot show it.
  - It needs a commit whose `Task:` value is A's id plus a character, naming no ticket (td-9's option 2).
  - Failing that, the record should say plainly that on the head the unit case alone holds it.
- **Severity:** medium. At acceptance level it undoes the PF15 item of lens I2's Finding 2, one of the findings this ticket was opened to fix; the gate itself is still held.
- Ordinary work: yes, because an honest engineer simplifying the close's commit matching (trusting git's search and loosening the exact step) is ordinary work, and this case would stay green.
- Consequence: other, because the unit case `test_gates.py:72-78` still fails under that fault in every regression run, and under the schema a start-only match cannot count another real ticket's commits as A's.

### F2: the README-W2-67 row for the case is not true of the head

- **What was done:** the merge changed the case's ids. `tests/acceptance/W1-30/README-W2-67.md` merged cleanly and was not touched.
- **What happened:** line 45 still says A is PROJ-tska and records the case red under PF15. On the head, A is PROJ-tkaa and the case is green under PF15.
- **What should have happened:** the row should give the head's ids and the case's state under PF15, or the fix if F1 is fixed.
- **Severity:** low.
- Ordinary work: yes, because the next auditor or test designer reads this row to learn which plant each revised case catches.
- Consequence: other, because it misleads a reader; it opens no gate and loses no work.

## Scratch, refusals, retrieval

- **Scratch:** `TMPDIR` is `/tmp/gov-launch-independent-auditor-714v6mfh/claude-1000`.
  - At the start: 8 inodes, 24K.
  - Before the two runs: 12 inodes, 40K.
  - After them: 15 inodes, 92K. pytest's own folder kept nothing.
- **Refusals:**
  - Read refusals: 0.
  - One hook refusal (DEC-953 item 2), not a read: a command that wrote file lists into my temporary folder through a shell variable, which was my error under the brief's command rules. I did not retry that form; I made the same comparison read-only, writing nothing.
- **`gov retrieve`:** used once, for how `gov close` matches a ticket's commits by its `Task:` trailer. It returned no evidence (FACET_UNAVAILABLE, both facets "stale"), so I read named files instead.
- **Code-graph tool:** not available in this session; not used.
- **Load:** the load average was 87 to 108 during my runs.

## rev-6's record

task: Last review (DEC-413, DEC-953, effort max) of DAEO-9nys's repair change, `git diff 3a2f2a1f0497 a8c0920abead` (2 files), on head 90d41204d412: are rev-5's F1 and F2 fixed, is nothing lowered, and is the scope right?
status: DONE. Verdict pass: F1 and F2 are fixed, nothing is lowered and the scope is as stated. There are two low findings, both in README-W2-67's wording; neither fails open or loses work, so they are rows, not a round.
work_completed: Ran step 0 and the identity checks. Read the diff, the case at the base and at the head, and its helpers in `w1_30_support.py`. Read how the close matches commits and the order of its gates (`src/gov/close/command.py`, `repo.py`, `history.py`), and the ticket id grammar in `common.schema.json`. Read td-6's plant tooling (`PLANTS.md`, `td6_plant_plugin.py`, `site/sitecustomize.py`) and td-6's and td-10's run records. Ran the single case twice, once under PF15 and once without. Checked the README-W2-67 row, its new "Run 6" section, W1-30's `README.md`, both commits' trailers and the files they touch.
files_changed: none. Step 0 (b) wrote one loose object, 1ae28402a109 ("sandbox-trial"), to the object store, as the brief requires. Probe leftovers are only in my temporary folder: one marker file and pytest's kept folder of the failed run.
evidence: Step 0 (a) refused with "Read-only file system"; (b) wrote 1ae28402a109 and `update-index --refresh` exited 0. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`. Under PF15 the close (08:00:01 UTC) exited 3 with CONTAINMENT_FINDING alone: "commit 1c4426ae8962: src/example/feature_after.py: committed path(s) outside allowed paths". Marker: "commits of PROJ-tkaa matched by substring: 1, of them exactly: 0". Commit a8c0920abead (parent 3a2f2a1f0497) touches only the two files and carries Task: DAEO-9nys, Role: independent-test-designer, Implements: DEC-954, DEC-907 (both in the register) and a Rewrite-Reason. Commit 90d41204d412 adds only `CP-DAEO-9nys-0025.md`. td-10's records: marker 0/0 before the change, 1/0 after; whole file 33 tests with 0 failures before and after. My temporary folder went from 8 files and folders (24K) to 3,165 (34M).
tests: Two runs of `test_w1_30_close.py::test_task_trailer_exact_match_not_substring` on 90d41204d412, both with `-o tmp_path_retention_policy=failed`: under PF15, 1 failed (18.15 s); without the plant, 1 passed (5.74 s). The suite was not run (DEC-959 item 1).
discoveries: (1) The close's search, git's fixed-string search for "Task: <ticket>", reads the whole commit message, subject included, not only the trailers. (2) Under PF15 the refusal also names the near-miss commit, so the new assertion would turn red on its own. (3) The near-miss commit also catches a "starts with" matching fault, which AB's id (one character in front) cannot. (4) td-10's whole-file "after" run used exactly the committed file: the file was last written at 07:49:13 UTC, the run started at 07:50:51 and the commit is from 07:53:06. (5) `gov retrieve`'s two index facets were stale when I asked.
risks: The near-miss commit writes `src/example/feature_after.py`, which is inside A's allowed paths. Today nothing reaches it, because A has no commit and so no range. If the case ever gives A an earlier commit, the close's rule against commits that name no task and touch the ticket's work would name it, and the new assertion's message ("substring match bug") would give the wrong cause. The lead's rebuild and scoped run on the head are still pending.
lessons: When a substring fault sits behind a fixed-string pre-search, only values that survive that search can show it. Read the plant's marker count before trusting a red or a green.
proposed_decisions: none
unresolved: The lead's rebuild and scoped-run results, which go into the probe record. Where the two low README findings go: as rows that ride along with a resume (DEC-802), not as a round.
recommended_next_action: Commit this probe record (pass) beside the lead's scoped-run results, record the two low README findings as rows, and return to the orchestrator.

---

Verdict: pass

**Head probed:** 90d41204d412 on branch `w2/W2-67`. The change reviewed is `git diff 3a2f2a1f0497 a8c0920abead` (2 files). Identity checks matched: GOV_ROLE independent-auditor, GOV_TICKET DAEO-9nys, top level `/home/usain/gov-os-worktrees/W2-67`, branch `w2/W2-67`.

**Step 0:**
- (a) Failed with "Read-only file system", as required.
- (b) `hash-object` wrote 1ae28402a109 and `update-index --refresh` exited 0, as required.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`.

**Classification (DEC-809):** 2 findings, both low, both "Ordinary work: yes" and "Consequence: other"; none fails open or loses work; no round.

**1. F1 is fixed.**
- **Run under PF15.** I used td-6's tooling: its plugin loaded into pytest, its plant folder on PYTHONPATH after this worktree's `src/`, `GOV_TD6_PLANT=PF15`, `PYTHONDONTWRITEBYTECODE=1`, and the marker file in my own temporary folder.
  - Result: 1 failed, at "the refusal does not say that no commit carries Task: PROJ-tkaa".
  - The close exited 3 with CONTAINMENT_FINDING alone, naming `src/example/feature_after.py`. Both test runs were made (acceptance 1 passed, regression 1 passed).
  - The marker, from the `gov close PROJ-tkaa` process: "commits of PROJ-tkaa matched by substring: 1, of them exactly: 0".
- **The red has PF15's own cause.** The plant keeps the close's search and changes only the exact filter on `Task:` values into a substring one.
  - The search returns the near-miss commit (`Task: PROJ-tkaab`) and the plant counts it as A's.
  - The trailer gate refuses only when a ticket has no commit, so it passes.
  - W1-50's containment check then refuses that commit, because its `Task:` names no ticket. The refusal names the commit too, so the new assertion would also have turned red.
- **Run without the plant:** 1 passed.
- Both runs agree with td-10's records.

**2. Nothing is lowered.**
- The five checks the case had at 3a2f2a1f0497 are all unchanged:
  - the fixture check that A has no commit (the support's own exact matching, which now also has to leave `PROJ-tkaab` out);
  - refused with exit 3;
  - `Task: PROJ-tkaa` named exactly;
  - AB's commit not named;
  - A not closed.
- One assertion is added. The only other edit to existing lines moves the docstring's closing quotes.
- W2-64's ids are kept: A `PROJ-tkaa` (W1-947), AB `XPROJ-tkaa` (W1-9471). W1-30 is unchanged between the merge 0568d91baf56 and the base.
- **The near-miss commit reaches the close only through the matching.**
  - On the head the exact filter drops it, so A has no commits and no range. The commit gates (trailers, accepted history, unmeasured work, the known-reds lists) refuse with TRAILER_MISSING alone, and the close stops there (DEC-868 item 3).
  - The governance checks, the checkpoint watchdog, containment and the test runs are never reached. The 5.7 s head run against the 18 s PF15 run fits that.
  - Under PF15 every gate before containment passed, the checkpoint included.
  - So no gate refuses for this commit on the head, and none can hide a fault.
- Under the ticket id grammar (`common.schema.json`: a project prefix, a hyphen, exactly four characters), `PROJ-tkaab` names no ticket.

**3. F2 is fixed.**
- The row now names A `PROJ-tkaa`, AB `XPROJ-tkaa` and the near-miss `PROJ-tkaab`, and records run 6's red and the head green. That is true of the head and of the runs.
- The "Run 6" section matches my runs, td-10's records and the code, except for one sentence (finding 1).
- The whole-file count of 33 holds: there are 33 test functions at both commits, and td-10's "after" run used the committed file.
- W1-30's `README.md` is untouched by the repair, and its line for this case ("close | substring match") stays true.

**4. Scope:** as stated in the evidence line above. Commit a8c0920abead touches only the two files and carries all four required trailers. Commit 90d41204d412 adds only the checkpoint record, which is a plain checkpoint (trigger ticket-transition).

**Finding 1 (low): README-W2-67 "Run 6" states a general rule that does not hold.**
- What was done: the section concludes that because no valid ticket id is another valid id with characters after it, no pair of tickets can show PF15.
- What happens: the premise is true, but the close's search reads the whole commit message, subject and body included. On this repository, a search for "Task: of A's id" finds a8c0920abead by its subject alone; that commit's only Task trailer is DAEO-9nys. PF15 loosens only the filter on the `Task:` values of the commits found. So a commit of the valid ticket AB whose subject or body also holds A's trailer text is found and counted as A's under PF15, but not under the exact match. A pair of tickets can show PF15 that way.
- What should be: the sentence should say what holds, that no pair of tickets shows PF15 through their `Task:` trailers alone. The case itself is unaffected; its near-miss form is sound.
- Ordinary work: yes, because a later designer revising PF15's coverage reads this README as settled reasoning.
- Consequence: other

**Finding 2 (low): README-W2-67's "Runs" line no longer matches the PF15 row.**
- What was done: run 6 replaced the row's "After" cell. The batch-6 red (the close was not refused: it closed `PROJ-tska` with exit 0, marker 2 by substring and 0 exactly) became run 6's red (CONTAINMENT_FINDING, marker 1 and 0).
- What happens:
  - The "Runs" section still says every revised case "failed as in the table", pointing to td-6's run files. td-6's PF15 files hold the batch-6 red, not the one the table now states.
  - The batch-6 red is no longer recorded in the table.
  - The run-6 section names td-10's folder only for the marker of the run before the change, not for the red run.
- What should be: the row keeps both reds, each with its record (td-6's for batch 6, td-10's for run 6), or the "Runs" line sends the PF15 row to td-10's records.
- Ordinary work: yes, because an auditor tracing a table's red to its named run file meets a different failure and a different ticket id.
- Consequence: other

**Scratch:** my temporary folder went from 8 files and folders (24K) before the runs to 3,165 (34M) after; that is pytest's kept folder of the failed run plus one marker, within my 2 GB and 50,000 share. No bytecode was written into the worktree or td-6's folder; every bytecode file there predates my runs. The worktree's `.gov-runtime/store.db` and `query-vector-cache.db` changed at 08:01:27 UTC, during none of my commands, which fits the lead's rebuild.

**Refusals:**
- Read refusals (DEC-849): none.
- Guard refusals: one. A compound shell command that read td-10's markers (a `cd` plus a loop variable) was refused under DEC-953 item 2: "a reviewer or auditor runs only commands whose writes can be read". I did not retry it in any shell form and read the same named files with the plain read tools.

**gov retrieve:** used twice before reading any file, on how the close matches `Task:` trailers and on the ticket id grammar. Both answers were FACET_UNAVAILABLE (both facets "stale") with no evidence, so I read the named files. No code-graph tool is attached to this session, so none was used.
