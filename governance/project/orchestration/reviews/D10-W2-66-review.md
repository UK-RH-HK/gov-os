# D-10's red-fix list: the review of W2-66's DEC-891 record case leaving out files code reads (W2-66c, DAEO-btcs)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-66-review.md`; branch `w2/W2-66c-d10-tests at dc5c0fd87`; reviewer log `/home/usain/gov-os-worktrees/W2-66c-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-66-review.json`.
- verdict.py: READY (no blocking finding).

## Review of W2-66c (DAEO-btcs): the DEC-891 record case stops counting files that code reads (`dc5c0fd87`)

**Result:** the revision passes. It has 4 findings, and none of them blocks: none is in scope, reachable in ordinary work, and failing open or losing work. The rule leaves out exactly the 6 files the designer named, and every error it can make by leaving a file out fails closed.

**Sandbox check (Step 0):** passed.
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-66c` was refused: `OSError: [Errno 30] Read-only file system`.
- (b) `git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing, both at the start and before returning. I started no embedder, reranker or model.

---

**task:** W2-66c (DAEO-btcs): review of `dc5c0fd87`, W2-66's DEC-891 record case no longer counting files that code reads (D-10's red-fix list, DEC-1112 (3), the CTO's delegated (a)).

**decisions:** DEC-891; DEC-1112 (3), whose delegated record is at `governance/project/orchestration/DECISIONS-IN-FORCE.md:428-431`; DEC-1027 B; DEC-1084 (3); DEC-1061 (D-4's `d3d757f3b`); DEC-889 item 2; DEC-1100 (1); DEC-801; DEC-1010; DEC-1014; DEC-1073.

**status:** DONE

**work_completed:**
- Identity: HEAD is `dc5c0fd872782deccec278e1b52bda8ee2752d1a`, the reviewed commit.
- Read the diff, the whole test file, the live test map, the selector (`src/gov/close/select.py`), the merge queue's record check, the two readers (`indep_launch.py`, `deadman.py`), tickets DAEO-btcs and DAEO-zuiy (W2-66b), DEC-1112, and the CTO's delegated record.
- Ran the live-map test file twice, read-only, through the heavy slot.
- Ran the file's own `_string_literals` and `_read_by_code` on the real tree and on 14 planted cases. I extracted them with `ast` (the test module was not imported) and held the planted cases in memory.

**files_changed:** none.
- `git status --porcelain` is empty.
- The ignored `tests/acceptance/W2-66/__pycache__/` is the designer's: all its files date from 10:05 to 10:11 UTC, before the commit at 10:14:55. My runs did not rewrite it.

**evidence:**
- **Environment for both runs:** `PYTHONPATH=<worktree>/src`, my own TMPDIR folder, an empty HOME, `PYTHONUSERBASE=/home/usain/.local`, and `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
- **Run 1 (default):** 36 passed, 53 deselected. The breadth list keeps only one row of 7 functions in this file, `test_paths_dec_891_does_not_name_are_not_record_only` among them. All 7 rows of the record case ran, since it has no `rep:` line.
- **Run 2 (`--optin=breadth`):** 80 passed, 9 deselected.
- **Real-tree probe:** the rule leaves out 6 files, the 5 `tools/indep-schemas/*.schema.json` and `tools/win_toast.ps1`. Today `tools/` has two subfolders, `dispatch` and `indep-schemas`. The 7 `.py` files directly in `tools/` hold about 700 bare word-like literals between them (`log`, `state`, `decision`, even `a`).
- **Planted probe:** 14 cases, in memory; results are under check 1.
- **Scratch:** 20K and 5 inodes (`du -sh`, `du -s --inodes`), then removed.
- **Refusal:** the Write tool was refused for a probe script in my TMPDIR. I took the refusal: I wrote no file and ran the probes in memory instead.

**tests:**
- The live-map file: 80 passed with every row opted in.
- The exclusion left out 9 rows, confirmed by a collection-only run of its inverse:
  - 6 green-here rows of `test_the_record_reading_set_holds_each_reader_of_a_record_path` (W2-02's file and W2-54's five cases);
  - the 3 rows of `test_a_fixture_input_change_does_not_reach_the_real_model_suites`.
- None of the 9 belongs to the record case or to the cases check 3 names.

**discoveries:**
1. The ticket on disk does not hold this revision (F3).
2. A default run of this file shows only 36 of its 89 rows. Seeing every row of `test_paths_dec_891_does_not_name_are_not_record_only` needs `--optin=breadth`.
3. The premise that record-only fails open for the schemas holds for the merge queue's rerun after `w2/integrate` moves, which reruns only the record-reading tests.
   - It does not hold in `gov.close.select.plan`. There, W2-149's `allowed_paths` (`indep-schemas/**`) select its suite through the ticket overlap (`_tickets` reads every ticket, of any wave), and `tests/unit` always runs.
   - (a) remains the sound choice; this only bounds what (c) would have cost.
4. W2-66b's KPI ("so it is green on `w2/integrate`") is now true without W2-66b's own change.

**risks:**
- W2-66b could be closed as satisfied without its `.ps1` suffix ever being built, which would leave the `win_toast.ps1` record-only entry flagged by nothing (F2).
- When W2-66b builds the suffix, `test_the_record_only_list_hides_no_code_path` goes red until the map's `win_toast.ps1` line is dropped. That is the intended catch, but it collides with W2-66b's own clause "every other case … unchanged".
- W2-66b's README line may hit a trivial textual conflict with this one. No work is lost.

**lessons:** for a completeness case, ask which way each error of its filter fails. Here, leaving too much out fails closed (the selector widens to the full regression), while leaving too little out pushes the map toward a fail-open entry.

**proposed_decisions:** none. One bookkeeping act is needed (F3).

**unresolved:** nothing blocking.

**recommended_next_action:** READY per `verdict.py`.
- F1 and F4 go together as one hardening row for the case.
- F2: keep W2-66b in D-10, and drop the map's `win_toast.ps1` line with it.
- F3: amend DAEO-btcs before its close: add the KPI line `w2-66-records-read-by-code`, its `allowed_paths`, and the failure-line exception, citing `DECISIONS-IN-FORCE.md:428`.

---

### Answers to the checks

**1. No fail-open.** The rule can take a real record out of the case, but only in the fail-closed direction. Once a file leaves the case, the map may leave it unplaced, and the selector then runs the full regression for any change to it (`select.py:371-375`, UNPLACED). That never runs fewer tests.

- **A `.json` or `.yaml` that a tool merely names:** it is left out whenever the whole literal equals its name, even when the code joins that name to another folder. Probe C: `indep_launch.py`'s `"kinds.yaml"` belongs to `governance/project/indep-walls/`, yet a `tools/kinds.yaml` would be left out.
- **A log message:** counts only when the whole literal is the name. Probe F: a sentence that contains `win_toast.ps1` does not count.
- **A folder-level literal:** every non-`.md` file under a folder of that name is left out. Probe A: `deadman.py`'s channel literal `"log"` would take a JSON record under a future `tools/log/` out of the case. No reader directly in `tools/` holds `"dispatch"`, so `tools/dispatch/` is untouched today.
- **A `tools/` folder anywhere under a DEC-891 place:** the nearest one counts (probe K: `docs/close/tools/` behaves the same). Only `.md` files are spared. `docs/plan/` is unaffected because its filter keeps only `docs/plan/*.md`.
- **Is "a literal equals the path" a sound proxy for "code reads it"?**
  - As evidence that code reads a file, it is strong but over-matches (probes A, C, M). Those errors fail closed (F4).
  - As a test of reading, it is incomplete (probes B, D, E, J, L): a file read through a route the rule cannot see still counts as a record and must be listed record-only (F1). That is the old behaviour, narrowed; the revision adds no new fail-open.
  - Probes G, F, H and I behave as intended: a planted record stays a record, and a reader that cannot be parsed keeps the file a record, which fails closed for the case.

**2. `win_toast.ps1`.** This is F2, out of scope.
- The revised case does not hide a fail-open. The old case *demanded* the record-only entry, because it counted the script as a record (D-4 added it to green this case, `d3d757f3b`). The new case neither demands nor flags it.
- A case should catch it, and one is already decided: W2-66b's `.ps1` code suffix (DEC-1027 B) turns `test_the_record_only_list_hides_no_code_path` red on the entry.
- This revision makes that fix conflict-free, because dropping the map line no longer turns the record case red.

**3. The other cases are unchanged and pass.**
- The diff touches only the record case (one added filter clause and its docstring) and adds two module-private helpers. `ast` was already imported.
- `test_paths_dec_891_does_not_name_are_not_record_only` passes all 4 rows, `test_the_record_only_list_hides_no_code_path` passes, and `test_the_record_only_paths_are_dec_891_s_places_and_nothing_else` passes.

**4. Trailers and paths.**
- `dc5c0fd87` carries all five required trailers: `Task: DAEO-btcs`, `Implements: DEC-1109, DEC-1112`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-891, DEC-1112 (3): …` and `Co-Authored-By: Claude Opus 5.5`.
- It changes only `tests/acceptance/W2-66/README.md` (+1 line) and `test_w2_66_live_test_map.py` (+37/−1).
- `25d72380f` changes only the status line of `.tickets/DAEO-btcs.md` (`Task: DAEO-sdxk`, `Role: orchestrator`).
- Note: D-4b's launch brief asks for `Implements: DEC-1065`. The commit instead follows the CTO's ticket commit. This is traceability only, not a finding.
- The ticket's own frontmatter is out of step with the change (F3).

---

### Findings

Classification: F1 in/yes/other; F2 out/yes/other; F3 in/yes/other; F4 in/yes/other. None is in scope, reachable in ordinary work, and failing open or losing work, so no round is proposed.

**F1. The rule misses files read by code through other routes, so the case still demands record-only for them** (scope: in)
- **What happens:** a file is left out only when a tracked `.py` directly in the nearest `tools/` folder holds its exact name or one of its folders. The case still counts as a record, and stays red until the map lists record-only, any file read:
  - by a tool in a subfolder (probe B: a `weights.json` beside `tools/dispatch/balancer.py`; the tree already has `.py` tools there);
  - by a shell script (probe J);
  - through a name built at run time (probe L, the style `indep_launch.py` already uses for `"indep-" + "walls"`);
  - by code outside any `tools/` folder (probe E);
  - as an `.md` file, by design (probe D).
- **What should happen:** the readers would cover the `tools/` subtree and `.sh` files, or the red message would name the other answer.
- **Today:** none exists. No other non-code file in a DEC-891 place is named by code: the four ACT package files are named by no code, and `sentinel-brief.md` is named only by the operator's protected-path lists and W2-148's unit tests.
- Ordinary work: yes, because adding a data file beside a dispatch or shell tool is ordinary, and the red message points at the record-only list, which is the answer D-4 gave for `win_toast.ps1`.
- Consequence: other. The case itself fails closed. A fail-open needs a later map edit, and in `gov.close.select.plan` that edit is mostly covered by the ticket overlap and by `tests/unit` always running.
- **Reversed by:** evidence that tools read data files only through a `.py` directly in `tools/`, or that the merge queue's rerun after `w2/integrate` moves also runs the overlap suites.

**F2. The test map lists `tools/win_toast.ps1` record-only while `deadman.py` runs it, and no case flags it** (scope: out)
- **What happens:** `deadman.py` runs the script through PowerShell. The selector and the merge queue treat a change to it as a record change.
- **What should happen:** the owner's DEC-1027 B says the script is code. D-4's entry under DEC-1061 contradicts that; both ids are named here per DEC-1073.
- No tracked test reads or runs the script. The merge-queue unit test only names it, and asserts that it is code.
- Ordinary work: yes, because an honest agent who edits the toast script lands on a record-only selection, and an honest closer can read W2-66b as already satisfied.
- Consequence: other. The entry is a fail-open classification in kind, but no test is skipped today.
- **Reversed by:** a tracked test that reads or runs the script, which would make the consequence fail open (still out of scope); or the entry being dropped together with W2-66b's suffix.

**F3. Ticket DAEO-btcs on disk does not authorize this revision** (scope: in)
- **What was done:** W2-66c's designer changed `test_w2_66_live_test_map.py` and its README, and narrowed another W2-66 case.
- **What the ticket says:**
  - Its `allowed_paths` hold only `test_w2_66_select_fixes.py`.
  - Its failure lines include "Any file changed outside `tests/acceptance/W2-66/test_w2_66_select_fixes.py`; any other case of the W2-66 suite changed, skipped, xfailed or loosened."
  - Its notes say the changed file belongs to W2-66b.
- `25d72380f` only changed the status. The KPI `w2-66-records-read-by-code` exists only in this brief. The authority is real, though: `DECISIONS-IN-FORCE.md:428-431` says "(a) … a test designer revises the case".
- Ordinary work: yes, because reusing an open ticket for a delegated revision without amending its frontmatter is an ordinary bookkeeping slip.
- Consequence: other. No work is lost: W2-66b has no built work, and its planned change sits on a different line. A close that judges W2-66c against its own failure lines would refuse it, which fails closed.
- **Reversed by:** an amended DAEO-btcs on the branch, or a standing rule that a recorded delegated decision widens a ticket's paths.

**F4. A literal that equals a bare name or folder name counts as "read" whatever the code does with it** (scope: in)
- **What happens:** probes A and C, above. Also, the case's docstring says "prose names nothing", but a docstring that exactly equals a file name does count (probe M, contrived).
- **What should happen:** a real record would stay in the case.
- Ordinary work: yes, because a tracked folder under `tools/` named with a common word is ordinary, and the readers already hold about 700 such words.
- Consequence: other. It fails closed: an unplaced record runs the full regression.
- **Reversed by:** any path through which leaving a record out of this case selects fewer tests. The UNPLACED rule in `select.py` rules that out today.

### Probed and found sound
- The rule leaves out exactly the 6 files the designer named, over `git ls-files`.
- `.md` files, tickets, probes, checkpoints, close records (including `docs/close/nightly/*.json`), the decision register and the plan's documents are untouched.
- All 7 rows of the record case run and pass, and each still asserts that its place holds at least one record.
- The case runs on every close (it is in `record_reading`) and now reads the literals of the `.py` files in `tools/`. A change that drops `"indep-schemas"` turns it red in the same close, which fails closed.
- The motive is real: W2-149's `test_w2_149_results.py` and its unit tests read the schemas.

```verdict
{"kpis": [{"kpi": "w2-66-records-read-by-code", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
