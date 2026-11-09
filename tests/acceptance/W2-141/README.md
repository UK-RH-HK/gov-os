# W2-141 acceptance tests: the guard refuses an engineer's search into its own acceptance folder unless excluded

Ticket DAEO-xwro (W2-141), profile STANDARD, DEC-1093 (2). Written by the independent test designer (MR-3) from the
ticket's KPI lines S1 to S3 and its three failure lines, before any implementation, reading only the integrated code
(`w2/integrate` at `8bb10a683` on this branch's base, DEC-963). No implementation of this ticket was read (G-14).

Two rounds: round 1 (`c3e0e16bc`) drives the guard's decide function; round 2 (the ticket's "The hook side",
DEC-1102) drives the live G-14 hook module `role_reads`, where W2-138's search went through (section "Round 2" below).

## How they run

    env PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-141 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

In process, under 1 s; no hook process, no git, no network, no model. The tests use the tree `PYTHONPATH` names,
else the worktree's own `src`. `HOME` is a temporary folder for the module; `GOV_ROLE`, `GOV_TICKET` and
`CLAUDE_PROJECT_DIR` are cleared.

- **The planted project** (`w2_141_support.make_project`, once per module): `.tickets/DAEO-zz41.md` (an engineer
  ticket, WBS id **W2-941**, the session's ticket) and `.tickets/DAEO-zz42.md` (W2-942); `tests/acceptance/W2-941/`
  (`test_feature.py`, `README.md`: the folder the engineer may not search), `tests/acceptance/W2-942/test_other.py`
  (another ticket's, readable), `tests/unit/`, `src/app/main.py`, `docs/notes.md`, `README.md`; the path map with the
  `role_paths:` block as the main tree holds it (G-14); a held-out list naming a path outside the project. Not a git
  repository. Every file holds the word `zqxw141`.
- **The oracle:** the KPI lines alone. Which planted commands really reach the folder, and which exclusion forms
  really keep it out, was checked by running the grep and find commands in a copy of the planted project (every
  "reaching" command printed the folder's lines; every excluded one printed none); rg, ag and ack are not installed
  here and were not run (N-5).

## The interface the tests assume

- **The decide function:** `gov.guard.decide.decide(tool_name, tool_input, project_root, role, ticket_id,
  subagent_type=None, cwd=None)` returns `("allow", "")` or `("deny", reason)`. Called with `cwd` the project root,
  `ticket_id` the ticket's id (`DAEO-zz41`) or its WBS id (`W2-941`), `tool_input` as the harness sends it (a Grep
  `glob` is one string; `{root}` in a case is the project's absolute path).
- **The refusal** (S1, S2; the second failure line) holds the folder `tests/acceptance/<WBS>` (here
  `tests/acceptance/W2-941`, with or without the trailing slash) and at least one exclusion form for its tool
  (`w2_141_support.HOW`):

  | Call | The reason holds one of |
  |---|---|
  | Grep tool | `!tests/acceptance/<WBS>/**` (the glob to add) |
  | Glob tool | `path` or `pattern` (it has no exclusion field: narrow the path or the pattern) |
  | grep -r / -R | `--exclude-dir=<WBS>` (the base-name form, the one GNU grep honours; D-1) |
  | rg | `-g` or `--glob` |
  | find | `-prune`, `-not -path` or `! -path` |
  | ag, ack | any of `--ignore-dir`, `--ignore`, `-g`, `--exclude-dir`, `-prune`, `-not -path` |

- **The exclusion forms that are allowed** (S1, S2): Grep with `glob: "!tests/acceptance/<WBS>/**"` and no path,
  `.` or the absolute root (also with `output_mode: files_with_matches`); `grep -rn <text> --exclude-dir=<WBS> .` and
  `grep -rn --exclude-dir=<WBS> <text> tests/`; `rg -n <text> -g '!tests/acceptance/<WBS>/**'` (no path: from the
  root); `find . -path ./tests/acceptance/<WBS> -prune -o -type f -exec grep … {} +`,
  `find . -type f -not -path './tests/acceptance/<WBS>/*' -exec grep … {} +`, and the prune form `-print | xargs
  grep …`. A Glob call is "excluded" by a path or pattern that cannot reach the folder (`src`, `src/**/*.py`,
  another ticket's folder).
- **Still refused** (the first failure line): an exclusion that does not keep the folder out: another ticket's
  folder excluded (`!tests/acceptance/W2-942/**`, `--exclude-dir=W2-942`, `-g '!tests/acceptance/W2-942/**'`) and
  grep's path form `--exclude-dir=tests/acceptance/W2-941`; and a call aimed inside the folder, with or without the
  exclusion glob.

## KPI lines, tests, and the outcome on `w2/integrate`

Run in the launch sandbox through the heavy slot on this branch (base `8bb10a683`): **88 tests, 50 failed, 38
passed** (0.42 s). Every red fails on the line it names: a refusal that names neither the folder nor the exclusion
(today's reason is `TESTS_REFUSAL`, "run them with pytest…"), a call allowed today (Glob with `**`, ag, ack), or an
excluded call refused today. Node ids are relative to the repository root; each row covers every parameter of the
function. `gov accept W2-141` (the same tree, heavy slot) reads the map: success-1 4 passed 22 failed, success-2 0
and 28, success-3 30 and 0, failure-1 5 and 34, failure-2 0 and 34, failure-3 33 and 0; none unmapped; 38 passed,
50 failed.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_a_call_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (13) | 8 Grep calls (no path, `.`, the absolute root, `tests/`, `tests/acceptance/`, glob `**/*.py`, type py, another ticket excluded) refused without the folder or the glob; 5 Glob calls (`**/*.py` with no path and from the absolute root, `**/*` from `tests/`, `**/test_*.py` from `tests/acceptance/`, `tests/**`) allowed |
| S1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_the_same_when_the_ticket_is_named_by_its_wbs_id` | red (2) | as above with `GOV_TICKET` W2-941: the Grep refused without the folder, the Glob allowed |
| S1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_the_same_for_an_engineer_subagent_of_an_orchestrator_session` | red (2) | as above for an engineer subagent of an orchestrator session |
| S1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_the_grep_call_with_the_exclusion_is_allowed` | red (4) | the Grep calls with `!tests/acceptance/W2-941/**` are refused today (a negated glob keeps nothing out in `reads._Judge.above`) |
| S1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_the_exclusion_is_taken_when_the_ticket_is_named_by_its_wbs_id` | red | the same, `GOV_TICKET` W2-941 |
| S1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_guard_a_glob_call_that_cannot_reach_the_folder_is_allowed` | green (guard, 3) | Glob `**/*.py` from `src`, `src/**/*.py`, `**/*` from another ticket's folder: allowed |
| S1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_guard_the_exclusion_does_not_open_a_call_aimed_inside_the_folder` | green (guard) | Grep from `tests/acceptance/W2-941/` with the exclusion glob: refused |
| S2 | `tests/acceptance/W2-141/test_w2_141_bash.py::test_s2_a_recursive_search_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (21) | 17 refused without the folder or a form (grep -r/-R from `.`, none, `tests/`, `tests/acceptance`, the absolute root, `--include=*.py`, `--exclude-dir=W2-942`, `--exclude-dir=tests/acceptance/W2-941`; rg with no path, `tests`, `-g '*.py'`, `-g '!…W2-942/**'`; find `-exec cat`, `-exec grep`, from `tests`, piped into `xargs grep`, `-print0` piped into `xargs -0 cat`); 4 allowed (ag and ack, with and without `.`) |
| S2 | `tests/acceptance/W2-141/test_w2_141_bash.py::test_s2_the_search_with_the_exclusion_is_allowed` | red (6) | grep `--exclude-dir=W2-941` (two orders), rg `-g '!tests/acceptance/W2-941/**'`, find `-prune -exec`, `-not -path -exec`, `-prune -print` piped into `xargs grep`: refused today |
| S2 | `tests/acceptance/W2-141/test_w2_141_bash.py::test_s2_the_same_when_the_ticket_is_named_by_its_wbs_id` | red | `GOV_TICKET` W2-941: `grep -rn … .` refused without the folder |
| S3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_an_engineer_search_that_cannot_reach_its_folder_is_allowed` | green (guard, 19) | Grep from `src`, glob `src/**/*.py`, from W2-942, the folder's name as the pattern from `src`; Glob from `src`, `src/**/*.py`, from W2-942; grep -rn for the folder's name in `src/app/` (G-14); grep -rn / rg / find in `src`; grep -rn in W2-942; `find . -name '*.py'` (names, no reader); `ls tests/acceptance`; a plain grep of `README.md`; pytest on the folder; Read of W2-942's test and `README.md` |
| S3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_other_roles_are_unaffected` | green (guard, 6) | orchestrator, independent-auditor (a reviewer), independent-test-designer (same ticket), product-spec, ticket-lead, research: the broad Grep, Glob, grep -r, rg, ag, find searches and a Read of the folder all allowed |
| S3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_another_ticket_s_engineer_reads_this_ticket_s_tests` | green (guard) | W2-942's engineer: `grep -rn … tests/acceptance/W2-941` allowed (DEC-963) |
| S3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_g14_cases_answer_as_before` | green (guard, 4) | guard4_check's G-14 cases 1, 3, 4 and 5 through the decide function: own README denied, another ticket's allowed, the grep by pattern only allowed, the orchestrator's Read allowed (N-3) |
| F1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_a_call_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (13) | the Glob calls are allowed without an exclusion |
| F1 | `tests/acceptance/W2-141/test_w2_141_bash.py::test_s2_a_recursive_search_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (21) | ag and ack are allowed without an exclusion |
| F1 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_guard_the_exclusion_does_not_open_a_call_aimed_inside_the_folder` | green (guard) | a call aimed inside the folder stays refused |
| F1 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_a_read_aimed_at_the_own_folder_stays_refused` | green (guard, 4) | Read, Grep, cat and grep -rn aimed at the folder: refused |
| F2 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_a_call_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (13) | the Grep refusals name neither the folder nor the glob |
| F2 | `tests/acceptance/W2-141/test_w2_141_bash.py::test_s2_a_recursive_search_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (21) | the grep, rg and find refusals name neither the folder nor a form |
| F3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_an_engineer_search_that_cannot_reach_its_folder_is_allowed` | green (guard, 19) | as S3 |
| F3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_other_roles_are_unaffected` | green (guard, 6) | as S3 |
| F3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_another_ticket_s_engineer_reads_this_ticket_s_tests` | green (guard) | as S3 |
| F3 | `tests/acceptance/W2-141/test_w2_141_unchanged.py::test_s3_guard_g14_cases_answer_as_before` | green (guard, 4) | as S3 |
| F3 | `tests/acceptance/W2-141/test_w2_141_grep_glob.py::test_s1_guard_a_glob_call_that_cannot_reach_the_folder_is_allowed` | green (guard, 3) | as S1 |

## Round 2: the hook side (DEC-1093 (2), DEC-1102)

Written by a fresh independent test designer on `w2/W2-141-tests` with integrate merged (`2a49d031b`), from the KPI
lines, round 1's cases and today's integrate code (`.claude/hooks/role_reads.py`, `pretooluse.py`, `bash_writes.py`,
`src/gov/guard/`); no implementation of this ticket was read, and `docs/changes/W2-141-hook/` does not exist in this
tree.

    env HOME=<empty scratch> PYTHONUSERBASE=$HOME/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-141/test_w2_141_hook.py -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed

In process, under 1 s; no hook process, no network, no model; one `git init` of the planted project.
(`PYTHONUSERBASE` only where pytest is installed in the user's site and `HOME` is emptied.)

### Which hook the cases load

`w2_141_hook_support.hook_file`: **`docs/changes/W2-141-hook/role_reads.py` when it exists in the tree under test,
else `.claude/hooks/role_reads.py`**, loaded by file path (importlib) under the module name
`w2_141_role_reads_under_test`. The tree under test is the parent of the first `src` folder `PYTHONPATH` names when it
holds either file, else the worktree that holds the tests. Every failure message starts with `[hook <path>]`, naming
the file the case ran on. **The outcome below ran on `.claude/hooks/role_reads.py`** (integrate's live hook; no staged
copy here). `bash_writes` is imported from the tree's `.claude/hooks/`.

### The interface the hook cases assume

- **The call, as `.claude/hooks/pretooluse.py` makes it (lines 566-573):**
  `role_reads.refusal(main, os.path.realpath(root), tool, seen, cwd, roles, ticket, trees, expand_token)` returns the
  refusal's reason (a string) or None. The cases pass `main` and `root` the planted project (a git repository with no
  commits, its own path map with the `role_paths:` section round 1 plants: never the main tree's), `cwd` its root,
  `seen` the tool input (for Bash, `bash_writes.reads_view(command)`), `roles` the session's role and
  `gov.guard.reads.acting_role(role, agent_type)` deduplicated, `ticket` `DAEO-zz41` or `W2-941`,
  `trees` `lambda: [root]`, `expand_token` `gov.guard.decide._expand_token`. `HOME` is the module's temporary folder
  when the module loads, so `~/gov-os-worktrees` names nothing real. The staged copy keeps this signature.
- **Glob is passed to `refusal` too** (tool `Glob`, input `pattern` and `path`): S1 names Glob. Today's
  `pretooluse.py` sends only Read, NotebookRead, Grep and Bash to `role_reads` (D-2).
- **The refusal** holds the folder `tests/acceptance/W2-941` and one of its kind's exclusion forms (round 1's `HOW`),
  matched as a whole word: a hook reason also names `role_paths` and the path map, so `path` inside `role_paths` or
  `path-map` does not count as saying how. A G-14 true read keeps its reason (`role_paths.engineer.reads_denied`,
  `DEC-1052 G-14`).
- **Allowed exclusion forms, refused near-exclusions and still-refused calls:** round 1's list, with three more
  allowed forms (`grep -rn --exclude-dir W2-941 …`, the option's value as its own word; `--exclude-dir=W2-941` from
  the absolute root; `find . -type f ! -path './tests/acceptance/W2-941/*' -exec cat {} +`), and three more reaching
  forms (`grep -rn … . | head -n 50`, `cd tests && grep -rn … .`, `find tests -type f -exec grep -Hn … {} \;`).
- **The oracle:** each grep and find command was run for real in a copy of the planted project (GNU grep 3.11,
  findutils): every reaching command printed lines from `tests/acceptance/W2-941/`, every excluded and every S3 one
  printed none, the names-only listings printed no content. rg, ag and ack are not installed (N-5).

### KPI lines, hook cases, and the outcome on `w2/integrate`

Run in the launch sandbox through the heavy slot on `2a49d031b`, hook `.claude/hooks/role_reads.py`: **94 tests, 42
failed, 52 passed** (0.31 s). Every red fails on "was not refused: decision=allow": today's hook lets the search
through, from the root, `tests/`, `tests/acceptance/`, a `cd`, or as a Glob (which it never judges). The whole
folder (rounds 1 and 2): 182 tests, 92 failed, 90 passed; round 1's outcome is unchanged. `gov accept W2-141` (the same
tree, heavy slot, `HOME` an empty folder with only the user's site-packages linked in): success-1 9 passed 40 failed,
success-2 9 and 52, success-3 81 and 0, failure-1 11 and 71, failure-2 0 and 71, failure-3 79 and 0; none unmapped;
90 passed, 92 failed.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1, F1, F2 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s1_hook_a_grep_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (9) | Grep with no path, `.`, the absolute root, `tests/`, `tests/acceptance`, the absolute `tests/acceptance/`, glob `**/*.py`, type py, another ticket excluded: allowed by the hook |
| S1, F1, F2 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s1_hook_a_glob_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (5) | Glob `**/*.py` (no path, absolute root), `**/*` from `tests`, `**/test_*.py` from `tests/acceptance`, `tests/**`: allowed (the hook reads no Glob) |
| S1 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s1_hook_the_same_when_the_ticket_is_named_by_its_wbs_id` | red (2) | `GOV_TICKET` W2-941: the Grep and the Glob allowed |
| S1 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s1_hook_the_same_for_an_engineer_subagent_of_an_orchestrator_session` | red (2) | an engineer subagent of an orchestrator session: allowed |
| S1, S3, F3 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s1_hook_guard_the_grep_with_the_exclusion_is_allowed` | green (guard, 4) | Grep with `!tests/acceptance/W2-941/**` (no path, `.`, the absolute root, names only), by id and by WBS id: allowed |
| S1, F1 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s1_hook_guard_the_exclusion_does_not_open_a_call_aimed_inside_the_folder` | green (guard) | Grep from the own folder with the exclusion glob: refused |
| S2, F1, F2 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s2_hook_a_recursive_search_reaching_the_own_acceptance_folder_is_refused_saying_how` | red (23) | grep -r/-R from `.`, none, `tests/`, `tests/acceptance`, the absolute root, `--include=*.py`, `--exclude-dir=W2-942`, the path form `--exclude-dir=tests/acceptance/W2-941`, piped into head, after `cd tests`; rg with no path, `tests`, `-g '*.py'`, another ticket excluded; ag and ack with and without `.`; find `-exec cat`, `-exec grep` (from `.` and `tests`), piped into `xargs grep`, `-print0` into `xargs -0 cat`: allowed |
| S2 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s2_hook_the_same_when_the_ticket_is_named_by_its_wbs_id` | red | `GOV_TICKET` W2-941: `grep -rn … .` allowed |
| S2, S3, F3 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s2_hook_guard_the_search_with_the_exclusion_is_allowed` | green (guard, 9) | grep `--exclude-dir=W2-941` (two orders, the value as its own word, from the absolute root), rg `-g '!tests/acceptance/W2-941/**'`, find `-prune -exec`, `-not -path -exec`, `! -path -exec cat`, `-prune -print \| xargs grep`: allowed |
| S3, F3 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s3_hook_guard_an_engineer_search_that_cannot_reach_its_folder_is_allowed` | green (guard, 22) | Grep from `src`, glob `src/**/*.py`, from W2-942, the folder's name as the pattern from `src`; Glob from `src`, `src/**/*.py`, from W2-942; grep -rn for the folder's name and for `test_feature` in `src/` (by pattern, G-14); grep/rg/find in `src`, grep in W2-942; names-only listings (`find . -name '*.py'`, `find tests -type f`, `ls -R tests`, `git log --stat`); `ls` and pytest on the folder; a plain grep of `README.md`; Read and cat of W2-942's test; Read of `README.md` |
| S3, F3 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s3_hook_guard_other_roles_are_unaffected` | green (guard, 6) | orchestrator, independent-auditor, independent-test-designer (same ticket), product-spec, ticket-lead, research: the broad Grep, Glob, grep -r, rg, ag, find searches and a Read and cat of the folder allowed |
| S3, F3 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s3_hook_guard_another_ticket_s_engineer_reads_this_ticket_s_tests` | green (guard) | W2-942's engineer: grep -rn, Grep and Read of W2-941's folder allowed (DEC-963) |
| S3, F1 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s3_hook_guard_g14_true_reads_stay_refused_as_before` | green (guard, 5) | G-14's true reads (`test_live_hook.py`'s G14_REFUSED for the engineer): Read, cat, Grep of the folder, `cd tests/acceptance && sed …`, grep -rn of the folder: refused with the G-14 reason, also for an engineer subagent |
| S3, F3 | `tests/acceptance/W2-141/test_w2_141_hook.py::test_s3_hook_guard_g14_near_misses_still_pass` | green (guard, 4) | G-14's near misses (G14_PASSED for the engineer): another ticket's test, `ls` and pytest on the folder, grep by pattern from `src/`, inline Python: allowed |

### Round 2's notes

- **D-2. `pretooluse.py` never sends a Glob call to `role_reads`.** Its line 566 calls `role_reads.refusal` only for
  Read, NotebookRead, Grep and Bash. The Glob cases call `refusal` directly, so a staged copy can pass them while the
  live hook still lets every Glob through: the Glob half of S1 is live only when that line also names `Glob`. That
  file is not in the ticket's paths (a proposal to the CTO; the return's P-1).
- **D-3. One existing G-14 near miss contradicts S2.** `tests/unit/hooks/test_live_hook.py` (`G14_PASSED`, "a pattern
  naming the tests, a search from above") expects `grep -r foo tests/` allowed in a planted project whose
  `tests/acceptance/W2-G14T/` holds a test: S2 refuses it. These cases keep that row's first command (the grep by
  pattern from `src/`) and refuse the second. The unit case runs the live hook, so it turns red at the operator's
  copy; it is outside the ticket's paths (the return's P-2).
- **D-4. The hook's note lists Glob as a names-only listing let through;** S1 names Glob among the calls refused.
  The cases follow S1; the other names-only listings (`ls`, `find` without a reader, `git log --stat`) stay allowed.
  Its note also lets through names a command gets at run time (xargs); S2 names find "piped into a reader", so
  `find … | xargs grep` and `find … -print0 | xargs -0 cat` are refused unless the find prunes the folder.
- **N-7. Not reproduced here:** G-14's case of another folder's case revised for the ticket (linked by a designer's
  `Task:` trailer, it needs commits) and the `git show w2/<T>-tests:…` read (it needs the branch); both are in
  `test_live_hook.py`, which the CTO runs on the live hook after the re-pin with `guard4_check.py`.

## D-6 part 2: S4, the suites' own call-log folder (DEC-1108 (5), DEC-1109 (2))

Written by the independent test designer on `w2/W2-141-d6-tests` (from `w2/integrate`), from S4 and its failure line.
The owner's DEC-1108 (5) asked for "the suites that run the live hook pointed at a temporary folder" as a follow-up
to ACT-GUARD-CALLLOG-1 (DEC-1106 (2)); DEC-1109 (2) restarted it within D-6 part 2 (DECIDED-NOT-DONE row 60). Tests
only: no engineer, no product code (the hook already reads `GOV_GUARD_CALLS_DIR`, its `CALLS_ENV`).

- **`tests/conftest.py`:** the autouse fixture `_own_guard_calls`, beside `_own_vector_cache`, sets
  `GOV_GUARD_CALLS_DIR` for every test to `<base temp>/guard-calls/<16 hex of the test's node id>` (made only when a
  hook writes). A suite whose hook runs inherit the environment (`tests/unit/hooks/test_live_hook.py`) needs nothing
  more.
- **The suites that build a hook's environment themselves** carry the variable from the test's environment, one line
  each (`Rewrite-Reason: DEC-1108 (5)`, a note in each README): W1-02, W1-03, W1-04, W1-05 (its builder serves W1-38,
  W1-46 and W1-47 too; W1-46's hook runs are the live hook's), W1-49, W2-50, W2-58, W2-59 (the live hook's copy),
  W2-61, W2-65, W2-84, W2-106. The template's hook (`template/governance/kernel/hooks/pretooluse.py`) keeps no call
  log today; those suites carry the variable as S4 names the template's copy too.
- **Not changed:** the operator suites (`tests/unit/operator/`, `tests/acceptance/W2-148/`) run planted stand-in
  guards, and the operator's replay sets its own `GOV_GUARD_CALLS_DIR`; W1-28 and W1-50's freeze lift run `gov`, not
  the hook; W2-72's own builder is the PostToolUse hook's (its guard runs go through W1-03's). Unit files outside
  W2-141's paths that build a template hook's environment are the return's discoveries, not edited.

    env HOME=<empty scratch> PYTHONUSERBASE=$HOME/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-141/test_w2_141_calls_dir.py -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed

One hook process, one `git init`; under 1 s.

| KPI line | Test (node id) | Without the fixture | Why |
|---|---|---|---|
| S4, F4 | `tests/acceptance/W2-141/test_w2_141_calls_dir.py::test_s4_a_live_hook_call_s_line_lands_in_the_test_s_own_folder` | red | the tree's live hook, run once (a Read, as the orchestrator) on a planted project with a planted `HOME` and the test's own environment: the line went to `<planted HOME>/.gov-os/guard-calls`; with the fixture, one line in the test's own folder and no `.gov-os/guard-calls` under the planted `HOME` |
| S4 | `tests/acceptance/W2-141/test_w2_141_calls_dir.py::test_s4_guard_the_conftest_gives_each_test_an_absolute_folder_under_the_base_temp` | red | `GOV_GUARD_CALLS_DIR` unset; with the fixture, an absolute path under the base temp, never the real log folder |

"Without the fixture" is `--confcutdir=tests/acceptance/W2-141` (only this folder's conftest loaded), integrate's
state. The scoped runs (scratch `HOME`, heavy slot) and the scratch `HOME` before and after are in the return of
this round; the verification is S4's own: no `<scratch HOME>/.gov-os/guard-calls` after the run.

- **N-8. Two reds of a scratch `HOME` under `/tmp`.** `tests/unit/hooks/test_live_hook.py`'s
  `test_a_catastrophic_rm_is_refused[outside the project]` and `test_the_reason_is_plain` expect `rm -f ~/.bashrc`
  refused as outside the project; with `HOME` under `/tmp` the hook takes `~` as scratch and allows it. They fail
  the same with no conftest at all (`--noconftest`): the run's `HOME`, not S4.
- **N-9. A fixture's hook run.** A hook run made in a module- or session-scoped fixture runs before the autouse
  fixture sets the variable. Such a run with an inherited environment would show as a `.gov-os/guard-calls`
  folder under the scratch `HOME` (S4's verification); one with a built environment writes under that suite's own
  temporary `HOME`, never the real one, as before this round.

## Notes and limits

- **D-1. grep's `--exclude-dir` takes a base name.** GNU grep 3.11 (here) skips a subfolder when its *base name*
  matches `--exclude-dir`; `--exclude-dir=tests/acceptance/W2-941` (and `./tests/…`) keeps nothing out when it
  recurses from `.` (run for real on the planted project). So the tests take `--exclude-dir=W2-941` as an exclusion
  and refuse the path form (allowing it would fail open, the first failure line), and the grep refusal must name the
  base-name form. The emergency rules' line "`grep -r --exclude-dir=<that folder>`" (`EMG-common.md`) and the
  briefs' exclusion line, read as a path, do not exclude.
- **N-1. A folder that holds files.** The planted folder holds two files. Whether a search is refused when the
  ticket's folder is absent or empty (today's guard takes a part in only where files exist) is not tested: either
  reading passes.
- **N-2. The Glob tool has no exclusion field.** S1 asks a Glob call to be refused "unless the call excludes" the
  folder; a Glob call can only keep it out by its path or pattern, so its refusal must say to narrow them (the
  reason holds `path` or `pattern`). Glob patterns without `**` that match only names one level down (such as
  `tests/acceptance/*`) are not tested.
- **N-3. G-14's second case is the role_reads hook's.** guard4_check's case "W2-126's engineer reads W2-123's case
  revised for it" (linked by a test designer's `Task:` trailer) is judged by `.claude/hooks/role_reads.py`, not by
  the decide function, which allows it today; it is not reproduced. guard4_check.py itself runs the main tree's live
  hook under the pinned interpreter: it is the CTO's check after the re-pin (S3), not run here.
- **N-4. One Grep glob.** The Grep tool's `glob` is tested as one glob. A field holding the exclusion beside other
  globs (space- or comma-separated) is not tested.
- **N-5. rg, ag and ack were not run.** They are not installed in the sandbox. rg's exclusion is tested from the root
  with no path, where `-g '!tests/acceptance/<WBS>/**'` is relative to the folder searched; rg from a subfolder with
  that glob, and ag's or ack's own exclusions (`--ignore-dir`), are not tested either way.
- **N-6. The refusal names a path.** `reads.py`'s module note says "No message carries a path"; S1 asks the refusal
  to name the folder. The tests ask only for the project-relative folder built from the ticket's WBS id.

## Files

- `w2_141_support.py`: the planted project, the calls, the decide wrapper, the refusal checks (`HOW`).
- `conftest.py`: the module's planted project and guard, with a temporary `HOME`.
- `test_w2_141_grep_glob.py` (S1), `test_w2_141_bash.py` (S2), `test_w2_141_unchanged.py` (S3, the failure lines).
- Round 2: `w2_141_hook_support.py` (which hook file, its loader, the call as `pretooluse.py` makes it) and
  `test_w2_141_hook.py` (S1, S2, S3 and the failure lines through the hook).
- D-6 part 2: `test_w2_141_calls_dir.py` (S4 and its failure line; DEC-1108 (5), DEC-1109 (2)).
