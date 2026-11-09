# W2-141 acceptance tests: the guard refuses an engineer's search into its own acceptance folder unless excluded

Ticket DAEO-xwro (W2-141), profile STANDARD, DEC-1093 (2). Written by the independent test designer (MR-3) from the
ticket's KPI lines S1 to S3 and its three failure lines, before any implementation, reading only the integrated code
(`w2/integrate` at `8bb10a683` on this branch's base, DEC-963). No implementation of this ticket was read (G-14).

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
