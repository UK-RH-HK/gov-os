# Brief: independent test designer, W2-66c (DAEO-btcs), one round

Hand-written from the role template `role-test-designer@1.0.0` and the ticket by the ticket lead: `gov context DAEO-btcs --role independent-test-designer` answered `STORE_MISSING` in the lead's tree (no store there), so this brief is written by hand.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-btcs','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

## Who and where
- Role `independent-test-designer`, ticket `DAEO-btcs` (WBS `W2-66c`), profile LITE, class test-revision.
- Check: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-btcs`) and `git -C /home/usain/gov-os-worktrees/W2-66c-tests rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66c-tests`, `w2/W2-66c-tests`).
- You work and commit only in `/home/usain/gov-os-worktrees/W2-66c-tests` on branch `w2/W2-66c-tests`. Its base is `4193812cbf93` (= `w2/integrate`'s head).
- **The one path you may write:** `tests/acceptance/W2-66/test_w2_66_select_fixes.py` (a new file). Nothing else: not the README, not `test_w2_66_live_test_map.py` (W2-66b's, DAEO-zuiy), not the W2-66 `conftest.py` or `w2_66_support.py`, not `governance/project/test-map.yaml`, not `tests/optin-lifted-breadth.txt`, not `src/`. Any other case of the W2-66 suite stays exactly as it is (no change, skip, xfail or loosening).
- The README's KPI map is outside your path: do not edit it. Instead give the map in your return (below, `readme_map_gap:`).

## The KPI lines (word for word from the ticket file `.tickets/DAEO-btcs.md`; the `Verify:` text is the design's measure)
Success:
- S1 Settings and hook wiring are coupled: on the live test map, a change of `.claude/settings.json`, `.rulesync/hooks.jsonc` or `.rulesync/permissions.jsonc` reaches W1-33's `test_w1_33_guard_and_launcher.py`, W1-46's `test_w1_46_research_installs.py` and W2-54's `test_w2_54_sandboxed_worker.py`, through a coupling the map declares. Verify: a case per path, reading `governance/project/test-map.yaml` with the product's own loader (`gov.close.select.load_map`) and matching with `gov.close.select.match`, asserts the three suites are among the targets of the couplings that path matches [DEC-1100 (1), DEC-1098 (2)(b), DEC-896 item 2]
- S2 The declared checks are coupled to W2-54's no-weakening case alone: a change of any file under `template/governance/kernel/checks/` reaches `tests/acceptance/W2-54/test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened` through a coupling, and no coupling that path matches names the whole file `test_w2_54_time_limit.py` or another of its cases. Verify: a case per tracked file of that folder (`git ls-files`), on the live map with the product's loader and matcher [DEC-1100 (1), DEC-1045]
- S3 The history rule and the fixture scans are coupled: a change of any path under `tests/acceptance/` reaches `tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass`, and a change of an acceptance `.py` also reaches `tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found` beside W1-28's `test_w1_28_fixture_copies.py`. Verify: cases on planted paths (an acceptance `.py`, an acceptance `.md`, a conftest) on the live map with the product's loader and matcher; the `.md` reaches W1-01's case and not W1-50's [DEC-1100 (1), DEC-253, DEC-912 item 3]
- S4 W2-66's record-only case is always run: the live map's `record_reading` holds `tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only`, so a scoped selection of a change that holds only a record under `governance/project/orchestration/` selects it, and a run that names no node id collects every row of the case (no opt-in list leaves a row out: `tests/optin-lifted-breadth.txt` holds no `rep:` line for it), the `governance/project/orchestration/` row included. Verify: a case reading `record_reading`; a case reading the opt-in lists with tests/conftest.py's own reader (`optin_entries`) asserting none names the function; a case running the product's `gov.close.select.plan` on a temporary copy of the repository's test map and tickets folder in a planted git repository with one records-only commit, asserting the case is among the selected targets [DEC-1100 (1), DEC-889 item 2, DEC-891, DEC-1061]
- S5 Every coupling's target exists: each target of every coupling in the live map names a tracked file or folder, or a node id whose file is tracked and whose function (with its class, when named) is defined in that file, so a renamed case reds here, not as an `UNRESOLVED_TARGET` refusal at a later selection. Verify: a case over every coupling target, the node ids checked by reading the file's `def` and `class` lines (no collection, no run); a planted map with a misspelt node id reds the same helper [DEC-1100 (1), DEC-968]
- S6 Tests first: the cases were written from these lines, not from the patch; each case of S1 to S4 is red on the test map and breadth list of ACT-SELECT-FIXES-1's parent commit and green on those after it, and the file's cases are green on `w2/integrate`. Verify: the test designer's record (in the commit body) of a run of the file with the ACT's parent's `governance/project/test-map.yaml` and `tests/optin-lifted-breadth.txt` (`git show` of each copied over in a scratch clone): every S1-S4 case red; then green on the ACT's commit and on `w2/integrate` [DEC-1100 (1), DEC-906]

Failure (each must not happen):
- F1 A case that passes on the map before ACT-SELECT-FIXES-1 (it pins nothing).
- F2 Any file changed outside `tests/acceptance/W2-66/test_w2_66_select_fixes.py`; any other case of the W2-66 suite changed, skipped, xfailed or loosened.
- F3 A case that runs a pytest selection, starts a gov command, or reads anything outside this repository's tracked files and its own temporary folders.

The ticket's sources: DEC-1109, DEC-1112, DEC-1100, DEC-1098, DEC-889, DEC-891, DEC-253, DEC-968, DEC-1061, DEC-896, DEC-912, DEC-1045, DEC-906. Read them by id in `docs/DECISION_REGISTER.md` as you need.

## Method (tests first, MR-3, DEC-906, DEC-462)
- Write from the lines and the interfaces, **never from the patch**. ACT-SELECT-FIXES-1 is the owner's operator commit `8038e0ee648c` (its parent `795d97c7cd44`). **Do not read** `governance/project/orchestration/packages/ACT-SELECT-FIXES-1.md`, the ACT's patch files, or `git show 8038e0ee648c` as a diff: the lines say what to pin. You may read the two data files your cases read (`governance/project/test-map.yaml`, `tests/optin-lifted-breadth.txt`) as they stand, and copy the parent's and the ACT's versions into your scratch clone for S6's run (as whole files, `git show <commit>:<path>`; you need not study their difference).
- **Never read the bodies of `src/gov/close/select.py` or any implementation code.** The calls' forms are in `tests/acceptance/W2-66/README.md`, section "Interface", and in how the existing W2-66 tests call them: `tests/acceptance/W2-66/test_w2_66_live_test_map.py` (its `test_map` fixture, `RECORD_READERS`, `COUPLINGS`, `test_every_record_reading_target_exists` near line 349), `tests/acceptance/W2-66/w2_66_support.py` and `conftest.py`, and `tests/conftest.py`'s `optin_entries(folder)` (line 222). As the README says: `gov.close.select.load_map(root)` returns `(map, error)`, `gov.close.select.match(path, pattern)` matches a path against a map pattern, `gov.close.select.plan(root, wbs, ...)` makes the selection. Confirm the forms from the README, not the source.
- Memory: use `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` (the integration branch's store; at most two searches: if a bundle does not answer or may be incomplete, search once more in your own, different words, then answer from both bundles with path and lines, or say "not found"; DEC-1092 (1)). Never one giant query (DEC-860); for code questions small targeted traversals (DEC-859). **Drop unread any retrieve result under `src/`** and name in your return any such result you were served (P-R1, DEC-820 (c)). Say in your return whether you used it.
- Reads (DEC-820): reads are open except (a) secrets and keys, never printed; (b) the held-out qualification material's contents; (c) the counterpart's work: here, the implementation (`src/`, and the ACT's patch); (d) the hidden half of any evaluation set. None of (b) or (d) is involved. Until W2-58 lands the guard still refuses some reads (searches from the repository root, `governance/project/` or `.claude/`): take a refusal, never another spelling; search named folders; count the refusals in your return (DEC-849).

## The cases' form
- pytest; LITE profile, but every line needs its cases as its `Verify:` says. Import `gov.close.select` as the product; the helper reads the live map with `load_map` and matches with `match`. A helper that gives, for a path, the union of targets of every coupling whose patterns the path matches.
- **S1:** one parametrised case per path of the three; asserts the three suites (by file; a node id inside that file does not count as the whole suite unless the line allows it: read it as "the suite file is among the targets") are among the targets.
- **S2:** one parametrised case per tracked file of `template/governance/kernel/checks/` (list it with `git ls-files` at collection or in a fixture, inside the repository); each asserts the node id is a target and no matched coupling names the whole `test_w2_54_time_limit.py` or another of its cases.
- **S3:** planted paths (an acceptance `.py`, an acceptance `.md`, an acceptance `conftest.py`; names you choose, they need not exist): W1-01's case reached by all three; W1-50's case and W1-28's file reached by the `.py` (and the conftest if it is a `.py`); the `.md` reaches W1-01's case and **not** W1-50's.
- **S4:** three cases: `record_reading` holds the node id; no opt-in list (read with `optin_entries` from `tests/conftest.py`) holds an entry naming the function; a planted git repository in `tmp_path` (git `init`, a copy of the live `governance/project/test-map.yaml` and the `.tickets/` folder, a base commit, then one commit adding only a record under `governance/project/orchestration/`), with `gov.close.select.plan` called as a function on it, asserting the case is among the selected targets.
- **S5:** a case over every coupling target of the live map (files and folders tracked: `git ls-files`; node ids: the file tracked and its `def` (and `class`, when named) lines read as text: no collection, no run); and a case with a planted map (a dict or a file in `tmp_path`) holding a misspelt node id, asserting the same helper reports it.
- **F3:** no case runs pytest (no `pytest.main`, no `python -m pytest`), starts a `gov` command (no `gov` CLI, no `python -m gov...` subprocess), or reads outside the repository's tracked files and `tmp_path`. `git` subprocess calls are allowed for `git ls-files` in the repository and for building the planted repository in `tmp_path` (S2, S4 need them); nothing else through `subprocess`. No network. Deterministic.
- No `skip`, `xfail` or `skipif` anywhere in the file. Name each case so its S line is clear (e.g. `test_s1_...`).

## S6: the procedure you carry out and record in the commit body
Commit the file first (below), then:
(a) **Parent run:** one scratch clone of your tests branch under `/tmp/gov-os-lead-W2-66c/td-clone` (e.g. `git clone --quiet /home/usain/gov-os-worktrees/W2-66c-tests /tmp/gov-os-lead-W2-66c/td-clone` then check out `w2/W2-66c-tests` there; put commands longer than one line in a script file under `/home/usain/gov-os-worktrees/W2-66c-tests/.gov-runtime/scratch/` and run it with `bash`). Overwrite in the clone `governance/project/test-map.yaml` and `tests/optin-lifted-breadth.txt` with `git show 795d97c7cd44:<path>` of each. Run the new file there:
`env HOME=/tmp/gov-os-lead-W2-66c/empty-home TMPDIR=/tmp/gov-os-lead-W2-66c PYTHONPATH=/tmp/gov-os-lead-W2-66c/td-clone/src python3 -m pytest tests/acceptance/W2-66/test_w2_66_select_fixes.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"` (run from the clone's root).
**Every S1 to S4 case must be red there.** S5's cases are exempt from the red rule: say what they do on the parent. A case green on the parent pins nothing (F1): rewrite it until it reds for the line's reason, or drop it and name it in your return.
(b) **ACT run:** the same, with the two files from `8038e0ee648c`: all green. (c) **Head run:** the same file in your worktree as it stands (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-66c-tests/src`): all green.
If (a) made you change the file, commit the revision as a new commit (never amend) and repeat (a)-(c). Remove the clone afterwards (`rm -rf /tmp/gov-os-lead-W2-66c/td-clone`); if you cannot, name it.
Record in the last commit's body: the three counts (red on the parent, green on the ACT, green on the head), the exact pytest line, and which cases are red on the parent with each one's reason in a few words.

## Rules
- **DEC-732, word for word:** "in this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=<this worktree>/src` set per command (never in a session's `--settings` env)." Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66c-tests/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Commit (your path only; never amend, rebase or reset):**
  `git commit -m "W2-66c: <subject>" -m "<body: the S6 record>" --trailer "Task: DAEO-btcs" --trailer "Implements: DEC-1100, DEC-1098, DEC-1109, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-66/test_w2_66_select_fixes.py`
  (a new file: `git add` it first; no `Rewrite-Reason`). Before each commit: `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` (if one is there, stop and return); never `--no-verify`.
- Command forms the guard reads: one simple command per Bash call; no `cd ... &&` chains (use `git -C` and absolute paths); no here-documents, backticks, `$(...)` as a write target, shell variables as write targets, or long inline `python3 -c` with braces; anything longer in a script file under your scratch, run with `bash` or `python3`. A refused form is never retried in another disguise. **Refused twice for the same call: stop and say so; no third try.**
- No installs (only the CTO may ask the owner). Never read the held-out material or the hidden half of an evaluation set. Never print a secret. Never write in `~/gov-os-workbench`. No copying of the tree other than the one S6 clone this brief names, under `/tmp/gov-os-lead-W2-66c/`; nothing under any `.gov-runtime/` but your scratch notes, and no clone there.
- **Scratch budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-66c` for every run; keep pytest's own retention (no `--basetemp`); clean as you go.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never the keywords of the secrets rule that takes a bare 40-hex string.
- On an authentication or access error (401, 403), stop and return with status AUTH_REQUIRED.
- An ambiguous KPI line is never guessed: give it in `proposed_decisions` with options, recommendation and confidence; write the cases for the reading you recommend and say so.

## Your return (your last message; the twelve fields first, each a labelled line, "none" where nothing)
After the twelve fields add:
- `sandbox_check:` the results of step 0 (a) and (b);
- `cases_per_line:` the file's case count per S line (S1..S5) and the case ids (full node ids);
- `s6_record:` red on the parent / green on the ACT / green on the head, counts, and any case dropped or rewritten for F1;
- `readme_map_gap:` a table `| KPI id | tests | expected red reason |` the CTO can paste into the README, and whether every line maps to cases you can name;
- `retrieve:` whether you used `gov retrieve`, how many times, and any result under `src/` you were served and dropped;
- `read_refusals:` the guard's read refusals you met (count and form);
- `imports:` the new file's imports.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
Refused twice for the same call: stop and say so.
