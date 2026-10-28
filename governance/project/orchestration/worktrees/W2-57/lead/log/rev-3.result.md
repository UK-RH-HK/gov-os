task: Judgement-only re-probe (owner, DEC-895 item 2) of DAEO-cy5o (W2-57) at head `8d9d78d93529`, after the merge `91f5b19af1af` brought W2-07 round 2's gate (h) line into `src/gov/close/command.py`.
status: DONE. The verdict is pass: the merge leaves W2-57's serial phase and nightly route as they were, and every commit gate still refuses before any test.
work_completed: I ran step 0 and the identity checks, then recomputed the intersection of judged and changed files: one file, `src/gov/close/command.py`. I read its change (only the comment of the `recorded` line changed) and the change in `gates.py` behind that line. On W2-57's real range I compared what gate (h) subtracts under the head's rule and under the rule at `8f61bda0eb5c`, and I ran gate (h), the accepted history and the probe gate read-only on the real head. I planted five closes in temporary projects (`gov close` from this worktree's `src/`) covering questions 1 to 3, and I ran W2-57's route file, its list file and the serial unit test at the head.
files_changed: none. The only write outside my temporary folder is step 0's sandbox-trial blob `1ae28402a109`, a loose object in the shared object store, as step 0 asks.
evidence: `gov.__file__` is `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`. `git show --cc 91f5b19af1af` shows nothing of the merge's own in `command.py` or `gates.py`, and the merge's tree equals `8555aafc0ba6`'s. On the real range: 330 commits besides the ticket's 30; the head's rule subtracts 68, the old rule 23, and none of the 45 added touches W2-57's own paths. Gate (h) finds nothing either with the subtraction or with none at all. The accepted history holds 45 accepted entries and 0 refused. The probe gate passes with review 2's record. Scratch: 10 inodes / 32 KB at start, 18 / 104 KB before the planted closes, 21 / 164 KB after them and at the end. `git status` shows only the 11 placeholder mounts throughout.
tests: All runs used `-o tmp_path_retention_policy=failed`. My planted file: 5 passed (P1 to P3 in 6.75 s, P4 and P4b in 3.77 s). `tests/acceptance/W2-57/test_w2_57_nightly_route.py`: 3 passed. `tests/unit/close/test_serial.py`: 11 passed. `tests/acceptance/W2-57/test_w2_57_serial_list.py`: 2 passed.
discoveries: The close's own probe gate still accepts review 2's record at this head, because it reads the merges as git's own merge (DEC-754). So the fresh probe is required by DEC-895's check, not by the close (O1). Under DEC-923 item 2, gate (h) now leaves alone a decision-record commit that changes W2-57's ticket file. For this FULL ticket the probe gate still refuses such a commit when it comes after the probed commit (P4).
risks: none. Nothing was changed, and the planted projects lived only in my temporary folder.
lessons: The planted projects were built with the suites' own builders, which copy `src/` and the kernel templates into the temporary project, as W2-57's route case does. Both retrieval facets read "stale" at this head, and the code-graph CLI cannot start inside this sandbox.
proposed_decisions: none
unresolved: none
recommended_next_action: The lead commits this record with `Role: orchestrator` alone and `probed_commit` set to the full id of `8d9d78d93529`, so that review 2 becomes an earlier round, then goes on to W2-57's close.

---

Verdict: pass

**Head probed:** `8d9d78d93529` on `w2/W2-57`. Its code is identical to the merge `91f5b19af1af`, whose tree is exactly `w2/integrate` at `8555aafc0ba6` (W2-57 was merged into integrate first, W2-07 second). Since review 2's probed commit `8f61bda0eb5c` the branch has gained only review 2's record (`da0240e0563e`), that merge and the lead's checkpoint.

**Step 0:**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o` failed: `OSError: [Errno 30] Read-only file system`, exit 1.
- (b) `git hash-object -w --stdin` worked (exit 0, blob `1ae28402a109`), and so did `git update-index --refresh` (exit 0).
- Identity: `GOV_ROLE` is `independent-auditor` and `GOV_TICKET` is `DAEO-cy5o`; the toplevel is `/home/usain/gov-os-worktrees/W2-57` on `w2/W2-57`; HEAD is `8d9d78d93529`. `git status` showed the 11 placeholder mounts and nothing else, at the start and after every run.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`. The pytest process of the planted cases printed the same path, and their `gov close` ran through the suite's launcher with `PYTHONPATH` set to this worktree's `src/`.

**Classification (DEC-809):** no new finding, and one observation (O1, other). Review 2's F1 to F4 stand unchanged: F1 yes / fails open, feature-gated (DEC-803); F2 yes / other; F3 no / other; F4 no / fails open (a row). No finding is both "yes" and "fails open or loses work" in code in use at this head.

**Intersection of judged and changed files:**
- The judged files are those of the ticket's own commits up to `8f61bda0eb5c`: 25 commits, 48 paths. `git diff --name-only 8f61bda0eb5c HEAD` names 66 paths. They share one file: `src/gov/close/command.py`.
- In that file one line changed, gate (h)'s `recorded` line, and only its comment. Everything else is byte-identical to `8f61bda0eb5c`: the line's code, `_run_tests`, the serial-phase call, `serial.py`, the plugin and `tests/acceptance/serial-only.txt`.
- The change in behaviour is in W2-07's `src/gov/close/gates.py` (`RECORD_PREFIXES` widened, `owner_listed`, `_ever_accepted`). It is used once, at `command.py:201`, and feeds only gate (h) at line 202. The serial call is at `command.py:917`, in `_run_tests`, which the `recorded` set never reaches.
- The merge adds nothing of its own: `git show --cc` is empty for both files.

## Probed and found sound

**1. The serial phase's entries.**
- **P1:** a temporary project whose list has 8 lines, closed by `gov close`. The lines were:
  - a serial entry;
  - a nightly function whose file holds a sibling case;
  - a nightly whole file;
  - an entry with no comment;
  - an entry whose route word is unknown (`overnight:`);
  - an entry routed `Nightly:` (capital N);
  - one entry listed twice, once nightly and once serial;
  - beside them, a plain case and a decision-record commit that only the head's rule subtracts.
- **P1's result:** the ticket closed. The `serial-afterwards` run's `cases` were exactly the five entries not routed nightly, in the list's order: the serial entry, no comment, unknown word, `Nightly:` and the entry listed twice. That run passed 5, and each of the five ran exactly once, alone. So `test_runs` and `cases` state what ran.
- W2-57's own tests at the head pass: the route file 3, the serial unit test 11, the list file 2.
- The real list reads as at review 2: 63 entries, 15 nightly and 48 in the serial phase, which add up to the whole list.

**2. The nightly route.**
- In P1 the routed function and the routed whole file ran in neither phase. The routed function's sibling ran once in a worker, so the file was collected, not ignored. Every run counted 0 skips.
- Nothing outside the route drops a serial entry. The merge touched none of these: `_run_tests`'s filter, `serial.phase`, the plugin or the list.
- P4b: with a commit in range that only the new rule leaves to its decision, the serial phase still ran its one serial entry alone.

**3. The commit gates before any test, and the widened `recorded` set.**
- **P2, one close of a FULL ticket with every commit gate faulted.** It was refused with 10 findings: `PROBE_MISSING`, `TRAILER_MISSING`, `ACCEPTED_HISTORY_REFUSED`, `WORK_WITHOUT_TASK` (6 commits) and `ACCEPTED_RED_REFUSED`. The refusal shows `test_runs: []` and `counted: false`. No planted test ran, the iteration count stayed 0, and the ticket stayed in progress with no close record.
- **Gate (h) still refuses, under the head's rule, each of the six commits planted in P2:**
  - a commit that names no task and changes the governed code (`src/example/serial.py`, standing in for `src/gov/close/serial.py`);
  - a decision-record commit, under an owner's ACCEPTED decision, that changes that code beside the register;
  - a decision-record commit, under an owner's ACCEPTED decision, that changes `tests/acceptance/serial-only.txt` (placed in the ticket's allowed paths) beside the register;
  - a decision-record commit of records only (the ticket file and the register) that names one owner's ACCEPTED decision and one PROPOSED decision;
  - a commit that the exemption list names by a 12-digit id under an owner's decision;
  - a commit that the exemption list names by its full id under a delegated decision.

  Neither rule subtracted any of the six.
- **The only two ways a commit now leaves gate (h)'s input**, both named by DEC-923 item 2:
  - **(i) A decision-record commit of records only, under decisions each ever ACCEPTED.**
    - Of W2-57's own paths, only `.tickets/DAEO-cy5o.md` is a record. `serial.py`, `command.py` and the serial-only list are not records, so this way never carries them.
    - P4: the ticket file was changed under a delegated decision after the probed commit. The probe gate still refused it with `PROBE_INVALID` "the probe is stale", before any test: `counted: false`, no test ran, the count stayed 0. The head's rule subtracts that commit; the old rule did not.
    - P4b: the same change before the probed commit is one the reviewer sees, and the close passed.
  - **(ii) A commit the owner's lists name by its full id, under the owner's ACCEPTED decision naming it**, whatever it changes. P3: a commit with no task that changes the governed code, listed that way, closed. This needs the owner's own list entry and decision, not an agent's ordinary work.
- **W2-57's real range, read-only at the head:**
  - 330 commits besides the ticket's 30. The head's rule subtracts 68 of them and the rule at `8f61bda0eb5c` subtracted 23: 45 more and none fewer. None of the 45 touches W2-57's own paths (its allowed paths, its ticket file, `tests/acceptance/W2-57/`).
  - Gate (h) finds nothing with the subtraction, and also nothing with no subtraction at all.
  - The accepted history holds 45 accepted entries and 0 refused. The path map gained 39 entries under DEC-927 and no other key changed.
  - The probe gate passes.
- **The `recorded` line still sits outside the gate's catch, as it did at `8f61bda0eb5c`.** `owner_listed` adds no way to raise beyond what `judged_history` already ran earlier. An unreadable register reads as "not accepted", and a malformed exemption entry is skipped.
- **The serial-only list is not one of W2-57's own paths**, so gate (h) never judged changes to it for W2-57's close, before or after the merge alike.

**F1 to F4 stand.** None of these changed since `8f61bda0eb5c`: `nightly.py`, `_run_tests`, `serial.py`, the plugin, the list and `src/gov/doctor/command.py`. Their classification stands.

## Findings

None.

## Observations (other, no round)

- **O1. The close itself does not flag review 2's record as stale at this head.**
  - **Done:** I ran the close's probe gate read-only on the real head with review 2's record.
  - **Happened:** it passed. It measured the merges `57e363c589f4`, `855837aef69b`, `8555aafc0ba6` and `91f5b19af1af` as git's own merge on the probed paths (DEC-754).
  - **Should have:** this is the design. The fresh probe is required by DEC-895 item 2's probe-impact check, and this record answers it. Once committed with the head's full id as `probed_commit`, review 2 becomes an earlier round (W2-M209) and this record decides.
  - **Severity:** none.

  Ordinary work: yes, because every merge of integrate into a merged but not closed FULL ticket meets it.
  Consequence: other

## Scratch, refusals, retrieval

- **Scratch:** 10 inodes / 32 KB at start; 18 / 104 KB before the planted closes; 21 / 164 KB after them and at the end. pytest's retention removed every passing case's folder. I did not measure the peak during the runs; at most five small projects existed (about 3 MB and 350 files each), far inside my share of 6 GB and 300,000 files and folders.
- **How the planted projects were built:** with the suites' own builders (W2-07's, built on W2-01's and W1-30's), as W2-57's route case builds its project. Each builder copies this worktree's `src/` and the kernel templates into the temporary project. Nothing of `governance/project/` was copied, and nothing went under `.gov-runtime/`. Each refused planted close opened a repair ticket inside its own temporary project; the worktree stayed clean.
- **Read refusals (DEC-849):** 0.
- **Other refusals:** 1. The code-graph CLI (`codebase-memory-mcp cli list_projects`) could not start, because `/tmp/cbm-daemon-1000` is read-only in the sandbox (chmod, errno 30). One try, not retried.
- **`gov retrieve`:** used once, to ask how the close routes serial-only entries and what gate (h) subtracts. Both facets answered "stale", so I read the named files instead.
- **Code-graph tool:** not used, for the reason above. The callers were found with one targeted search of `src/`: `decision_records` is used only at `command.py:201`, and `serial.phase` only at `command.py:917`.