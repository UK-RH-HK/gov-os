task: Second and last FULL probe of DAEO-c1uz (W2-66) at `5634d430` on `w2/W2-66`, read-only: are the first review's F1 to F6 answered, and what does the new code do that the tests miss?
status: DONE. Verdict **fail**: F1 to F6 are answered at this head, but two new findings are "yes" and "fails open" (P1 medium, P2 low).
work_completed: The sandbox check passed and the identity matched. I read the ticket, the code and test map since `9174e358`, the README's interface, the first review's draft, DEC-385, DEC-899 and lens I's W2-66 block. I ran the real selection on the live tree, with the base and the change put in memory, for F1 to F6 and for new paths. I ran W1-28's own scan on a scratch folder. I made eight real `gov close` runs and one nightly in fixture projects built with W2-66's own support module, reproduced F7, and rechecked the report's selection figures.
files_changed: none
evidence: Sandbox (a) refused: "OSError: [Errno 30] Read-only file system", exit 1. Sandbox (b) worked: object `1ae28402a109c3397a44b19239a00adfa9472eb0`, refresh exit 0. `printenv` gave `independent-auditor` and `DAEO-c1uz`. The worktree is `/home/usain/gov-os-worktrees/W2-66` on `w2/W2-66` at `5634d4305a7c4f9b677bed6a6cea26ea53c96c94`. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py`. Commits since `9174e358`: six by the test designer (`39b875bc`, `ee98e24a`, `cc7fb17f`, `7dc63f67`, `98c4be2f`, `6d17109b`; Role: independent-test-designer; only under `tests/acceptance/W2-66/`); five by the engineer (`45763156`, `16e98848`, `1ad4db0d`, `b3e60cbc`, `d3650169`; Role: engineer, Implements: DEC-880; none under `tests/acceptance/`); and the orchestrator's checkpoint `5634d430`. Probe outputs: case A exit 0, the old node id under `selected`, the case red at the closed head (1 failed); case B exit 0, red (1 failed); case C exit 0 for a conftest change, exit 3 for a support-module change; case D exit 0, red (1 failed), and its module-level variant was refused `COLLECTION_FAILED`; case E gave `first_bad` = the nightly record's commit `195e62e`, while the culprit was `561732c`; case F gave exit 1 `CHECK_RESULT_UNREADABLE` with the count 0→0, then exit 3 `CONTAINMENT_FINDING` with the count at 1. Scratch: 8 files and folders and 24K at the start; 23 and 116K at the end. Guard refusals: 2 (a Bash heredoc whose `>` was read as a write to an unresolvable path; a Bash grep with backticks, refused as an unreadable command under DEC-409); neither call was retried. Read refusals: 0. `gov retrieve`: used once, on the status of W1-28's check (DEC-385, P-I1-4); it returned lens I1's P-I1-4, which says the check "reads every file under `tests/acceptance/`".
tests: W2-66's four new acceptance files (moved files, declared folders, suiteless tickets, deselected cases): 7 passed. W2-66's live-map file and the unit tests `test_select.py`, `test_evidence.py`, `test_nightly.py`: 90 passed. My probe module in the scratchpad, over four runs: 6, 2, 1 and 1 passed, where a pass means the behaviour was reproduced. Every run used `-o tmp_path_retention_policy=failed`. No full suite was run.
discoveries: P1: a test-map target (record-reading, every-close or coupling) whose file or test function was renamed is still named `selected` and runs nothing, and nothing widens the run. P2: W1-28's held-out copy check reads every Python file under `tests/acceptance/`, but the map couples only `**_support.py` files to it; the line dates from `388d5892`, before the first review. Rows: R1, a renamed helper is not followed to a suite that imports it inside a function; R2, `pyproject.toml` (pytest's root marker) is placed by W1-07 alone; R3, F7 now reproduced; R4, an unreadable `--check-result` holds back a counted containment refusal by one run.
risks: The live selections come from the real code with the base and the change put in memory, not from a close of this worktree. The fixture cases model the live map's lines rather than closing this repository. W1-28's check is under review (P-I1-4 in P-IS-15); if the owner retires it, P2 goes away. The record-reading set was not searched again beyond what changed since the first review. The report's times were not re-run.
lessons: A W2-66 fixture close takes seconds, so end-to-end probes are cheap. Write probe files with the Write tool in the scratchpad: the guard refuses Bash heredocs with `>` and greps with backticks. All 59 live map targets exist today, checked down to the case; staleness only arrives with a rename.
proposed_decisions: Classification: 2 findings yes and fails open (P1 medium, P2 low); 2 rows no and fails open (R1, R2); 2 rows yes and other (R3, which is F7 reproduced, and R4); 1 feature-gated row (unchanged); the W1-01 merge item not found again. Recommendation for the owner (DEC-105): (a) apply now, riding along with the resume the merge package needs anyway (DEC-802). Test-designer cases come first (MR-4): a target that names no file or no case at the head widens to the full regression and is named; W1-28's coupling reaches every Python file its scan reads. Cost: about 2 fixture cases, about 30 lines, one map line. Option (b), defer to W2-68's entry criteria, leaves P1 silent for function renames. Option (c), re-baseline P2 by retiring W1-28's check through P-IS-15 (P-I1-4). Confidence: high for P1; medium for P2, which depends on P-IS-15.
unresolved: Whether the owner retires W1-28's check under P-IS-15 (P-I1-4), which decides P2. The W1-01 merge package stays the lead's to take to the orchestrator.
recommended_next_action: The lead commits this record and takes P1 and P2 to the owner with the classification line (this was the last review, DEC-413), proposing the fixes ride along with the merge package's resume.

PROBE_RECORD:

# Probe record: DAEO-c1uz (W2-66), path-scoped regression at close: the second and last FULL review

## What was probed
- **Head:** `5634d4305a7c4f9b677bed6a6cea26ea53c96c94` on `w2/W2-66`, worktree `/home/usain/gov-os-worktrees/W2-66`.
- **The change since the first review** (head `9174e358`, failed on F1 to F3):
  - Six test-designer commits under `tests/acceptance/W2-66/`: the moved-file, declared-folder, suiteless-ticket and deselected-case cases, the live-map cases, and the README's "Interface" items 1, 2, 3 and 6.
  - Five engineer commits:
    - `select.py`: rename detection off; a ticket's suite is its declared folder; a path only suiteless tickets hold is not placed; deselected cases named; a folder outside `tests/` is no suite.
    - One line of `command.py`.
    - The live map: the two conftests in the shared core, the coupling to `test_w2_67_copies.py`, the corrected note.
  - The lead's checkpoint.
- **The merge:** `03f470a5` (`w2/integrate`: W2-07's gates, W2-70, W2-67 round 1), unchanged since the first review. W2-07's judged paths stay under `class_evidence`.
- **Method:** the code was run, not only read:
  - the real selection on the live test map and tickets for chosen changed paths, with the base and the change put in memory and nothing written;
  - W1-28's own scan module on a scratch folder;
  - eight real `gov close` runs and one nightly in fixture projects built with W2-66's support module;
  - W2-66's new acceptance files, its live-map file and its unit tests.

## Who probed
A fresh independent-auditor session (`GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-c1uz`), read-only on the repository and sandboxed: the write outside the worktree was refused, git object writes worked. Effort max. Two guard refusals, neither retried: a Bash heredoc, and a grep with backticks. No read refusals. `gov retrieve` was used once, on W1-28's check and DEC-385.

## Threat model
ADR-0001: the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Every finding is judged by the two questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?". Only "yes" with "fails open" or "loses work" fails the probe.

## The first review's findings at this head
- **F1, answered.**
  - The change is read with rename detection off: a moved file is in `changed` at both its paths.
  - The three moved-file cases pass: a move out of the shared core runs full; a move away from a ticket's paths selects its suite.
- **F2, answered.**
  - On the live map, `tests/conftest.py` and `tests/acceptance/conftest.py` run full (`SHARED_CORE`).
  - Paths that only suiteless tickets hold run full (`UNPLACED`): `governance/project/orchestration/sync_context.py`, `docs/contract/contract.yaml`, `docs/audit/wave-1/context-pack-DAEO-03pw.json` and `docs/plan/tools/validate_s1.py`.
  - The overlap rule reads each ticket's declared acceptance folder.
- **F3, answered.** W1-07's and W1-25's conftests reach `tests/acceptance/W1-27/test_w2_67_copies.py` through a coupling, and W1-27's own through its suite folder. That file loads exactly those three conftests.
- **F4, answered.** Each deselected case is named in `left_out` by its node id with `NOT_REACHED`. For W1-32's typical change: 43 suites, 142 files and 31 cases.
- **F5, answered.** W2-67's close names `tests/acceptance/W1-27/` with `OWN`, and none of its files is left out. The same holds for W2-63 (W1-49) and W2-70 (W1-05).
- **F6, answered.** The map's note matches the selection: `sync_context.py` and `validate_s1.py` run full; W1-42's two scripts are placed by W1-42.
- **F7:** reproduced at this head; see row R3.

## Findings

### P1: A test-map target that no longer exists is still named "selected", and the run selects nothing for it (medium)
- **What was done:** two fixture projects, each with a real `gov close`.
  - **Case A:** the map's record-reading set names W1-rr's register-reading case by its node id.
    - W1-rr's test designer renames that test function.
    - A green night after the rename is the base.
    - Then an orchestrator's record-only commit breaks the register, and the ticket makes its one-module change.
  - **Case B:** W1-ec's every-close file is renamed by its test designer, with a green night after it as the base.
    - The renamed file checks the ticket's module.
    - The ticket's change breaks that module.
- **What happened:** both closes passed (exit 0) with `scope: scoped`.
  - **A:** the evidence names the old node id under `selected` with `RECORD_READING`. The renamed case is in `left_out` (`NOT_REACHED`), deselected with the file's other cases. Run at the closed head, the file has 1 failed.
  - **B:** the evidence names the old file under `selected` with `EVERY_CLOSE`. Every file of W1-ec, the renamed one included, is in `left_out`. Run at the closed head, the renamed file has 1 failed.
- **Cause:**
  - Only the own suite is checked for existence. A record-reading, every-close or coupling target is taken as given.
    - A file target that is gone leaves its suite's other files ignored.
    - A case target that is gone leaves every top-level case of its file deselected.
  - No rule widens the run.
  - On the live map:
    - W2-66's live-map case checks only the file part of each record-reading target, and runs only when W2-66's suite is selected.
    - Every-close and coupling targets are compared as strings only.
  - All 59 live targets exist at this head, checked down to their top-level case.
- **What should have happened:**
  - The README's "Interface" item 3: "Every target `selected` names exists in the tree closed."
  - Its rule that anything unknown or unreadable fails safe: the full regression, never less.
  - So a target that names no file or no case at the head widens to the full regression and is named. The record never states as selected a target that ran nothing.
- `Ordinary work: yes, because renaming a test function or test file is ordinary test-design work (W2-67's planned renames and revisions of W1-27, the pending P-IS-15 retirements), the designer does not hold the test map (shared core, W2-66's and W2-68's), and nothing at the rename's own close flags the stale entry.`
- `Consequence: fails open` (a record-only commit that turns a renamed record-reading case red, or a change a renamed every-close file would catch, passes a scoped close; KPI failure lines 1 and 3)

### P2: W1-28's held-out copy check reads every Python file of the acceptance suites, but the map couples it to support modules only (low)
- **What was done:**
  - The live selection for a change to `tests/acceptance/W2-54/conftest.py`, and for a new test file in W2-54.
  - W1-28's own scan module, run on a scratch folder whose conftest copies the repository whole.
  - A fixture project whose map couples `tests/acceptance/**_support.py` to a scanning suite, with a real `gov close`. The same marker was added once to a conftest and once, as the contrast, to a support module.
- **What happened:**
  - **Live:** both changes run scoped, and `tests/acceptance/W1-28/` is left out as `NOT_REACHED`.
  - **W1-28's scan:** it reads every `*.py` under `tests/acceptance/`, conftests and test files included. It flagged the planted conftest fixture as a whole-tree copier it cannot run, which is exactly what its case `test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs` refuses.
  - **Fixture:**
    - The conftest change: the close passed (exit 0), the scanning suite was left out, and it is red at the closed head.
    - The support-module change: the coupling selected the scanner, and the close was refused (exit 3).
- **Cause:**
  - The line follows lens I1's summary ("every suite's support modules"). W1-28's code, and I1's own K-8, read every file under `tests/acceptance/`.
  - The line has been in the map since `388d5892`. No acceptance case covers it.
- **What should have happened:**
  - A change to any Python file W1-28's scan reads selects W1-28. Lens I's synthesis §4 says "W1-28's file scan, which runs every suite's whole-tree copier".
  - This holds until the owner retires the check (P-I1-4 in P-IS-15, not yet decided: DEC-899 item 8).
- `Ordinary work: yes, because a test designer putting a copying fixture in a conftest or test file is the very mistake DEC-385's check, still in force, exists to catch.`
- `Consequence: fails open` (the scoped close passes with W1-28's check red until the nightly)

## Rows

### R1: A renamed or deleted helper module is not followed to a suite that imports it inside a function
- **What was done:** W2-ii imports W1-hh's helper inside its test. W1-hh's designer renames the helper and updates W1-hh. Then the ticket's change, and a close.
- **What happened:**
  - Both paths are in `changed`, and W1-hh is selected as `TEST_CHANGED`.
  - W2-ii is left out. The close passed, and W2-ii is red at the closed head.
  - With a module-level import instead, the pre-close gate refused the close (`COLLECTION_FAILED`).
- **What should have happened:** a suite whose imports name a helper that the change removed or moved is selected.
- `Ordinary work: no, because no acceptance helper module has been renamed or deleted in this repository's history, only three files import another suite's helper inside a function (W1-27's copies case, W1-28's support, W1-44's lessons), and module-level imports are refused at collection.`
- `Consequence: fails open`

### R2: `pyproject.toml`, the repository's pytest root marker, is placed by W1-07 alone
- **What was done:** the live selection for a change to `pyproject.toml`.
- **What happened:**
  - Scoped: W1-07 is selected by `OVERLAP` (DAEO-drvn), plus the always-run set.
  - There is no `pytest.ini`, `setup.cfg` or `tox.ini`. pytest reads a `[tool.pytest.ini_options]` section from this file when one exists; none exists today.
- **What should have happened:** a settings file every pytest run reads is in the shared core, like the two conftests now are.
- `Ordinary work: no, because no ticket open at this head holds the file, it has not changed since W1-07 (2026-10-03), and the project keeps its pytest settings in tests/conftest.py, now shared core.`
- `Consequence: fails open` (once a pytest section is added)

### R3: F7 reproduced: the nightly's bisect names the range's first commit when the red test is new
- **What was done:** a green night at G (its record committed after G), two harmless commits, a commit adding a red test, one more harmless commit, then the nightly on `main`.
- **What happened:** the night is red, and the red failed again when run alone. The P1 bisect package has the range G..HEAD, with `first_bad` = the nightly record's commit rather than the culprit.
- **Cause:** at commits before the test existed, pytest exits with "file or node not found", which the bisect step counts as bad.
- **What should have happened:** such a commit is skipped, and the culprit is named.
- `Ordinary work: yes, because a newly added red test is an ordinary red.`
- `Consequence: other` (the P1 package points at the wrong commit; the red itself is reported)

### R4: An uncounted stop after the counted gates holds back a counted refusal
- **What was done:** the ticket committed a file outside its allowed paths (a containment finding), and the close was given an unreadable `--check-result`.
- **What happened:**
  - Exit 1 `CHECK_RESULT_UNREADABLE`, the count stayed 0, and no repair ticket was opened. The containment finding is not stated.
  - Without the option, the same close gave exit 3 `CONTAINMENT_FINDING`, counted (count 1).
  - An absent pytest-timeout stops the close at the same point, as an absent test runner already does on `w2/integrate`.
- **What should have happened:** the findings of the gates already asked are stated and counted, or the option is read before those gates.
- `Ordinary work: yes, because a mistyped path is ordinary.`
- `Consequence: other` (nothing passes; the count comes one run later)

### Row (feature-gated, DEC-803): the check result is taken as given
- Unchanged since the first review: no test outside W2-66's own fixture reads `GOV_CLOSE_CHECK_RESULT`.
- `Ordinary work: no, because no live test reads the variable at this head.`
- `Consequence: fails open` (once a reader exists, a stale file could pass those cases)

### Known item, not found again: W1-01's two reds on the merge `03f470a5`
- This is the lead's package for the orchestrator.

## Found sound
- **The new rules only widen.** The declared folder, the suiteless rule, rename detection off and the conftests in the shared core each only add suites or widen to the full run.
- **A folder outside `tests/` is no suite.**
- **The full list of declared-folder tickets is W2-67, W2-63 and W2-70.** None is an orphaned suite or an orphaned WBS folder.
- **No ticket with a suite holds a broad pattern.** The ones that reach test infrastructure are `pyproject.toml` (R2), `tests/conftest.py` (now shared core), `.rulesync/**` and `schemas/**`; `schemas/` does not exist.
- **The base:**
  - Only a passed close writes a close record, and only `scope: full` evidence counts.
  - Nightly records count only when `verdict: green`.
  - Ids must be full commit ids and ancestors of HEAD.
  - The change is a tree diff, so the shape of the history does not matter.
- **The deselection:**
  - It honours a beginning at a `/`, `::` or `[` boundary.
  - pytest's prefix deselection never removes a selected case.
  - The serial-only cases follow the same ignore and deselect lists.
- **The merge with W2-07:**
  - No gate was removed or reordered.
  - The commit gates and the pre-close gate refuse, uncounted, before the selection runs.
  - No finding carries an `evidence` key, and the close schema admits both `evidence` and `class_evidence`.
  - W2-07's interface names no record key for the judged paths.
- **The per-test limit and the retention option** are on every run:
  - the close's acceptance run, its parallel run, the serial cases afterwards and the runs alone of the ratchet;
  - the nightly's full run, its runs alone and its bisect steps.
- **The nightly:**
  - A flaky candidate is never bisected.
  - A selection miss carries the map's correction.
  - Its writes are its record, its JUnit XML under `.gov-runtime/nightly/`, and a temporary worktree it removes afterwards.
- **The report:**
  - §1's figures hold at this head: 43 whole suites and 142 files left out, 31 deselections (now also named in `left_out`), and 26 record-reading targets in 14 suites.
  - It is dated `c9686606`. Under the new rules, which only add, its catch rate cannot fall.
- **Acceptance tests:** since `9174e358`, only test-designer commits change files under `tests/acceptance/`.

## Verdict
**fail.**
- P1 and P2 are each "yes" and "fails open".
- P1 breaks the README's own interface ("Every target `selected` names exists in the tree closed") and KPI failure line 3.
- P2 leaves DEC-385's live check unreached for changes to conftests and test files.