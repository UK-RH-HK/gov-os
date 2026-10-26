# W2-57 acceptance tests: load out of the close

Ticket `DAEO-cy5o` (W2-57), profile FULL. Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-57). Sources: DEC-892 item 2,
DEC-889 item 5, DEC-899 items 3 and 7, DEC-813, DEC-823, DEC-871, DEC-883 item 5, DEC-886, DEC-890, DEC-784, DEC-915;
lens I's P-IS-6 (`docs/assessment/2026-10/I-SYNTHESIS.md`), I4 findings 2 and 5 and P-I4-5, I2 F12.

Written by the independent test designer (MR-3) from the KPI lines and their sources, before any implementation,
in two batches of one session. **Batch A: KPI line 1, the rulesync probe, and KPI line 2, the doctor probes.**
**Batch B: KPI lines 3 to 7** (the serial-only list as P-IS-6's first table and the route to the nightly, W1-30's r11
and r13, W1-50's `CLAUDE*` removal, a p95 case for a test designer's read, W2-M332, the wall-clock limits under
load, and the network reason of the live host cases), in this folder and in the earlier files the ticket names.

## Run, and the code under test

    PYTHONPATH=<this worktree>/src python3 -m pytest tests/acceptance/W2-57 -n auto \
        -p no:cacheprovider -o tmp_path_retention_policy=failed

- **This worktree's code, whatever the caller's `PYTHONPATH`.** The declared check (`python3 -m
  gov.adapters.portability`) runs with `PYTHONPATH` set to this worktree's `src/` (W1-38's `run_portability_check`),
  and `gov check` and `gov doctor` run from it (W1-07's `run_gov_with_code`, with this worktree as the code root:
  the launcher an install would write, `PYTHONPATH` set to its `src/`). The session fixture `code_under_test` shows,
  before any case, that `import gov` resolves under this worktree's `src/`, and fails the session otherwise.
- **Nothing is patched or imported from the product.** Every case builds its project under `tmp_path`: an adopted
  project as W1-38's suite builds it (the template's `.rulesync/`, the kernel, the tool registry, the check's
  declaration; `rulesync generate` run and committed), or a small git repository made from scratch. Stand-in tools
  are short shell scripts in the case's `stand-ins/` folder, reached the way a user's are: named by `RULESYNC_BIN`
  and first on the `PATH` for the declared command, first on the `PATH` for `gov` (which builds its environment
  from scratch and passes `RULESYNC_BIN` to no check). Each stand-in records its process id; one still running at
  the end of the case is stopped, so none outlives it. No network; deterministic.
- **Needs** the installed rulesync (skipped only when it is truly absent, "rulesync is not installed"; a rulesync
  that is there and does not answer in time fails, as KPI line 1 (b) asks) and git. The doctor cases need neither.

## KPI line 1: the rulesync probe, with its four effects (DEC-892 item 2, P-I4-5 (a), I4 F2)

| Part | Success, and the failure line it guards | Tests | Red today, and why |
|---|---|---|---|
| (a) a limit a loaded machine meets | either call answering well past the old 10 s (the stand-in: 15 s) is waited for, and the check compares as with a prompt answer | `test_w2_57_rulesync_probe.py::test_a_late_answer_is_waited_for_and_the_check_compares_as_with_a_prompt_one[--version]`, `[generate]` | red: `[{'code': 'RULESYNC_FAILED', 'message': 'rulesync --version: no answer within 10 seconds; the generated files were not compared'}]`, and `'rulesync generate: no answer within 10 seconds'` |
| (a) a real fault is still found by its own finding | both calls 15 s late, CLAUDE.md edited by hand: `gov check` shows the family red with the findings a prompt rulesync gives, and no timeout | `test_a_real_fault_behind_late_answers_is_still_found_by_its_own_finding` | red: "rulesync answered both calls after 15 s, but the check reports a timeout: [{'code': 'RULESYNC_FAILED', 'message': 'rulesync --version: no answer within 10 seconds; …'}]" |
| (a) bounded; a timeout is told apart (failure: a timeout that passes a case) | `rulesync generate` never answers: the check ends by itself, inside the 60 s `gov check` gives it, red, with a finding naming rulesync and saying it gave no answer in time; no finding reads it as absent | `test_a_generate_that_never_answers_ends_the_check_red_with_a_finding_that_says_so`; for `--version`, W1-38's revised `TestToolAbsentOrHanging::test_timeout_handling` (stand-in named by `RULESYNC_BIN`) | green today (a guard): today's 10 s limit ends it with "no answer within 10 seconds". It goes red if the new limit outlasts `gov check`'s, or a timeout reads as absent or green |
| (a) a truly absent rulesync keeps its own finding; a timeout is never "not installed" | not on the `PATH`, or `RULESYNC_BIN` naming no file: the absent finding (`RULESYNC_ABSENT`), as today; a rulesync failing at once: its own reason; none says "no answer in time" | `test_a_rulesync_that_is_absent_or_fails_keeps_its_own_finding_and_is_never_a_timeout[absent-from-the-path]`, `[rulesync-bin-names-no-file]`, `[fails-at-once]`; also W1-38's `test_rulesync_absent_not_green`, `test_rulesync_bin_missing_file` | green today (guards) |
| (b) W1-38's session fixture fails, never skips, on a timeout | `rulesync_bin` skips only when `RULESYNC_BIN` names no file; a rulesync that does not answer `--version` within 60 s fails every case that needs it, naming the timeout; the suite's `generate` waits 180 s (was 30 s), its check wait 180 s (was 60 s), and a timeout in any of them fails, naming it | the revised `tests/acceptance/W1-38/conftest.py` and `w1_38_support.py` (every `needs_rulesync` case of the suite) | shown by a run, not a case of this folder (a nested pytest run would put a 60 s wait into every close): with `RULESYNC_BIN` naming a stand-in whose `--version` answers after 70 s, `TestGenerateCheck::test_check_clean_after_generate` and `TestHookStubs::test_hook_stubs_exist` **errored** "rulesync at … gave no answer to --version within 60 s: a timeout, not an absent tool (DEC-892 item 2)", 0 skipped; with `RULESYNC_BIN` naming no file, skipped "rulesync is not installed". The old helper returned None on a timeout and the fixture skipped (I4's RS-any: 181 cases skipped, exit 0) |
| (c) the 9 masked cases assert their reason | each asserts the finding it expects, so a check that went red on a timeout no longer passes it | W1-38: `TestBrokenHeldOutFile::test_broken_file_is_not_green_and_no_path_is_printed` ×7 (`HELD_OUT_STEP_FAILED` required), `TestFindings::test_one_hand_edit_is_one_finding` (the one finding names AGENTS.md), `TestRegisteredFamilyCheck::test_gov_check_is_red_after_a_hand_edit` (the findings name CLAUDE.md) | green against the installed rulesync (today's behaviour is right there); red 9 of 9 against a check that fails on a timeout (RS-ver and RS-gen below) |
| (d) W1-33's research case fails, not skips, the same way | `w1_33_support.rulesync_version()` returns None only when `RULESYNC_BIN` names no file; a timeout (60 s, was 10 s), a start failure or a failing `--version` fails the case naming it; `generate_definition` waits 180 s (was 60 s) and names a timeout | `tests/acceptance/W1-33/test_w1_33_agent_definitions.py::test_the_research_definition_is_the_generated_one` through the revised support | shown by the same run: **failed** "rulesync at … gave no answer to --version within 60 s: a timeout, not an absent tool"; skipped only with `RULESYNC_BIN` naming no file |
| (e) 0 rulesync skips and 0 timeouts in three closes' worth of parallel runs | **the lead's own verification**, not a case: W1-38's suite three times in the close's parallel form (`-n auto`, as the close runs it), on the implemented head | count, per run: skips whose reason names rulesync (expected 0), and failures or errors whose text names a timeout ("gave no answer", "no answer within", "did not end within"; expected 0). W1-33's research case and W2-57's own cases may be counted with it |

**How the 9 were found** (2026-10-26, on `d54546f00b21`, the suite as it stood, `-n auto`, load under 1): a
stand-in `rulesync` first on the `PATH` (the suite's own helpers call rulesync by absolute path, so only the
check met it). RS-ver, its `--version` answering after 11 s: 29 red, 172 green. RS-gen, its `generate` answering
after 11 s: 28 red, 173 green. Baseline: 201 green. Among the cases that run the check, those green under both
were the 9 above, plus cases a timeout cannot reach (a stand-in of their own named by `RULESYNC_BIN`, or no
rulesync call: `--list`, no tool registry) and the six kernel-comparison cases, which stay green because their real
fault is still found and named (`TestKernelAgainstAdapterSource` ×4, `TestRoleToolsAgainstKernel` ×2). I4 named the
first function; the run named the other two.

## KPI line 2: the doctor probes (I4 F5, I2 F12, row W2-L409)

| Success, and the failure line it guards | Tests | Red today, and why |
|---|---|---|
| a probed tool that answers well past today's limit is still read as answering: a tool's version probe (5 s today; stand-in `gitleaks`, 15 s), a tool with a version command of its own (5 s; `node`, 15 s), a venv's freeze hash (`uv pip freeze`, 10 s; 25 s), Claude Code's version (3 s; `claude`, 15 s) | `test_w2_57_doctor_probes.py::test_a_probed_tool_that_answers_well_past_today_s_limit_is_read_as_answering[tool-version]`, `[tool-own-version-command]`, `[venv-freeze-hash]`, `[claude-code-version]` | red: `'found_version': None, … 'ok': False, 'reason': 'unverified: no version read and hash does not match'` (gitleaks, node); `'sha256_match': False, … 'reason': 'cannot find site-packages in venv'` (the freeze probe gave up); `'cli_version': None` (claude) |
| a tool that never answers is read as not answering, and `gov doctor` still ends (failure: a timeout read as answering) | `test_a_probed_tool_that_never_answers_is_read_as_not_answering_and_doctor_still_ends` | green today (a guard: today's 5 s limit ends it); red if a limit is unbounded (W1-07's 180 s wait passes) or a silent tool is read as the registered version |
| a probe exception `gov doctor` does not catch ends it with an API-0002 envelope: `ok` false, an error code, a message naming the exception and the part of doctor (or the git call) it came from; never a bare traceback | `test_a_probe_exception_ends_doctor_with_the_envelope_and_its_text` (ordinary cause: git's `core.quotePath` off, a Latin-1 file name committed and renamed, so `git log --name-status` returns bytes that are not UTF-8) | red: "standard output is not one JSON document" — `gov doctor --json` exits 1 with an empty standard output and a `UnicodeDecodeError` traceback through `_check_path_compliance` |
| W1-07's `[doctor]` keeps its failure text: its message carries what `gov doctor` printed, trimmed | `tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` (revised; no expectation changed) | green today. Made to fail by the same cause planted only in the case's own temporary copy (a scratch plugin, not in the tree), its message head was `AssertionError: standard output is not one JSON document` / `gov doctor --json, exit code 1` / `stdout (trimmed): (nothing)` / `stderr (trimmed):` and the traceback's end (`_check_path_map` → `_git` → `UnicodeDecodeError`) |

## The failure line of the ticket, batch A's part

"A rulesync or doctor timeout that skips or passes a case": a skip on a timeout is held by (b) and (d); a pass on
a timeout by (c), by the guards above (a timeout is a finding that says so, never green, never "absent"), and by
the doctor guard. "A case weakened, skipped or serialised by marker alone to pass": no case of batch A carries a
marker, a skip other than the absent tool's, or a list entry.

## Slow cases (each waits once; under `-n auto` they run side by side)

| Case | About |
|---|---|
| `test_a_late_answer_is_waited_for…[--version]`, `[generate]` | 17 s each (15 s late, plus a prompt run) |
| `test_a_real_fault_behind_late_answers…` | 45 s (a prompt `gov check`, then one with 2 × 15 s of late answers) |
| `test_a_generate_that_never_answers…` | the check's own limit for `generate` (10 s today), plus `gov check` |
| `test_a_probed_tool_that_answers_well_past…` | 16 s, 16 s, 26 s, 16 s |
| `test_a_probed_tool_that_never_answers…` | doctor's own limit for the probe (5 s today) |
| the rest | 1 to 3 s |

Batch A today: 13 cases, 8 red and 5 green (the guards), in 13 s under `-n auto`. Batch B's cases in this folder
take 0.02 s (the list's two), 3.6 s, 2.2 s and 1.1 s (the route through the close, the broken nightly file, the
nightly's form) and 2.4 s (the designer's p95).

## Earlier tests revised in batch A (each in a commit of its own, with its `Rewrite-Reason:`)

- **W1-38** (`Rewrite-Reason: DEC-892 item 2: a probe timeout is not an absent tool and not the fault under
  test`): the fixture and the suite's waits (limits a loaded machine meets; a timeout fails, naming it); the 9 masked
  cases and `test_timeout_handling` made stricter. No case added or removed. See W1-38's README, "The revision of
  W2-57". W1-30's `test_w1_30_r15_policy_pairs.py` uses W1-38's `rulesync_version()` and `run_rulesync_generate()`,
  so its probe fails on a timeout too, instead of skipping.
- **W1-33** (`w1_33_support.py` only, the same reason): its probe and its `generate` as in (d).
- **W1-07** (`Rewrite-Reason: W2-L409: the failure text is kept`): the envelope case's message head and the timeout
  route of `run_gov_with_code`. See W1-07's README, "Revision (W2-57 …)".

## Reproducing the stand-in runs

The stand-ins are three lines of shell; none is in the tree. RS-ver: `if [[ "$1" == "--version" ]]; then sleep 11;
fi; exec ~/.local/bin/rulesync "$@"`, as `rulesync` in a folder put first on the `PATH`; RS-gen the same with
`generate`. For (b) and (d): `if [[ "$1" == "--version" ]]; then exec sleep 70; fi; exec ~/.local/bin/rulesync "$@"`,
named by `RULESYNC_BIN`. Run with `PYTHONPATH=<worktree>/src`, `-p no:cacheprovider -o
tmp_path_retention_policy=failed`.

## KPI line 3: the serial-only list as P-IS-6's first table, and the route to the nightly (batch B)

**The form** (`tests/acceptance/serial-only.txt`, the test designer's file). Today's readers read it as they are:
one entry on a line, the beginning of a node id, the text after ` #` a comment (`gov close`'s plugin, the
orchestrator's nightly script, W1-30's r11). Within that form every entry's comment is `<route>: <kind>: <reason>`:

- route `serial`: kept in the close, alone after its parallel phase, as before;
- route `nightly`: collected by the close and left out of both its phases (deselected, never ignored, never
  skipped); run alone in the nightly after its parallel run less the list;
- kinds `latency`, `daemon`, `race` take the serial route; `real-model` and `live-session` the nightly route
  (DEC-889 item 5; `real-model-or-daemon` is split in two). The header documents all of it, and that a case is never
  listed merely because it is slow, and that a marker routes nothing.

| Success, and the failure line it guards | Tests | Today, and why |
|---|---|---|
| the header documents the form, the routes, the kinds and the rule on slow cases | `test_w2_57_serial_list.py::test_the_header_documents_the_form_the_routes_the_kinds_and_the_rule_on_slow_cases` | red against the list before this batch ("does not document: the comment's form `<route>: <kind>: <reason>`, the route `serial` …, the route `nightly` …, the kind `daemon` …"); green with the reworked list (the list is this designer's file) |
| every reader takes the same entries; each is a node id's beginning (the route lives in the comment) | `test_w2_57_serial_list.py::test_every_reader_takes_the_same_entries_and_each_is_the_beginning_of_a_node_id` | green before and after (a guard: the rework keeps the list readable by today's readers) |
| **the close**: a nightly entry (a function, and a whole file) runs in neither phase and is counted nowhere as a skip; the sibling of a routed function still runs in parallel (collected, not ignored); the serial entry runs once, alone, and is the serial run's only case; a case with route-like markers and no entry runs in parallel (failure: serialised or skipped by marker alone) | `test_w2_57_nightly_route.py::test_a_nightly_entry_is_collected_and_left_out_of_both_phases_and_a_serial_entry_runs_alone` | **red until the implementation**: "cases the list routes to the nightly ran in the close: {'test_routed': [('none', …)], 'test_routed_file': [('none', …)]} (a run in no worker is the serial phase)": today's close runs every entry in its serial phase |
| collected, never ignored: a nightly file that cannot be imported still refuses the close by name | `test_a_nightly_entry_whose_file_does_not_collect_still_refuses_the_close` | green today (a guard against `--ignore`) |
| **the nightly's form** (the parallel run with the close's plugin, then every entry alone): every entry, nightly or serial, runs alone and passes; no entry runs in the parallel run | `test_the_nightly_form_runs_every_entry_alone_after_its_parallel_run_less_the_list` | green today (a guard: the nightly still runs the routed cases) |
| **this repository's list** (P-IS-6's first table): every entry's route, kind and reason; the live and real-model files and cases routed to the nightly; W1-16's split; W1-50's read-merge case out; W1-09's races and the latency cases kept serial; no entry naming no case (failure: a live or real-model file left in the close; a serial entry without its reason) | W1-30's revised `test_w1_30_r11_declared_here.py` (KPI line 4, below) | red against the list before this batch (r11's 40 red cases and the header case); green with the reworked list |

"The nightly's form" is taken as the lead states it: one parallel run less the list, with the close's own plugin
(the reader `gov close` gives its parallel run), then each entry alone in a run of its own. W2-66's
`python3 -m gov.close.nightly` is not run here (DEC-915 item 4, row W2-M406).

### The list's changes, entry by entry, with what each costs or saves per close

| Entries | Was | Now | Seconds per close (source) |
|---|---|---|---|
| W1-16's 94 cases that start no daemon (19 functions: five of `builtin_allowlist_and_daemon_secrets`, two of `code_answers`, two of `daemon_dir_and_names`, one of `paths_and_roots`, nine of `token_rule`) | serial (six whole-file entries took them in) | not listed: the parallel phase | −35.5 s serial; about +36 case-s in parallel, 8 to 16 s of wall time in I3's parallel trial (I3 F7) |
| W1-50's read-merge latency case | serial | not listed: the parallel phase | −0.3 s serial (I1 §4.2: 10 s bound, at most 1.2 s alone) |
| W1-46's live file; W1-50's two live freeze cases; W1-25's and W1-49's live files | serial `live-session` | `nightly: live-session` | ≈ −270 s serial, with the next row's files (I-SYNTHESIS §2.4: 208.8 s for W1-19, W1-21, W1-49 and W1-25; W1-50's two 37.9 s; W1-46's estimated) |
| W1-19's real-model file; W1-21's dev-tier file | serial `real-model-or-daemon` | `nightly: real-model` | in the row above |
| W2-58's four live functions (5 cases); W2-62's live resume; W2-54's sandboxed worker | on neither list: the parallel phase | **added**, `nightly: live-session` | ≈ −192 case-s from the parallel phase with the next row, and four paid sessions per close (I-SYNTHESIS §2.4; I1 F-2, I3 F6) |
| W1-21's family check; W2-54's real-embedder case | on neither list: the parallel phase | **added**, `nightly: real-model` | in the row above |
| W2-57's p95 case for a test designer's read | (new case) | **added**, `serial: latency` | +2.4 s serial |
| W1-02's and W1-05's p95; W1-07's help; W1-10; W1-15; W1-17; W1-18's two | serial `latency` | `serial: latency`, each with its reason | unchanged |
| W1-16's 67 daemon cases (34 entries); W1-20's file; W2-69's two | serial `real-model-or-daemon` | `serial: daemon` | unchanged (482 s, 116.9 s alone in the rehearsal; I3) |
| W1-09's two race cases | serial `race` | `serial: race`, kept in this run | unchanged (≈ 14 s, I4 §4.2) |

Net: about 303 s less in each close's serial phase, about 156 case-s less in its parallel phase (W1-30's revised r13
case adds about 31 case-s back there), and no paid session in a close. No entry was removed from `load_sensitive` or `accepted_reds` (line 8 is the orchestrator's commit).

**W1-09's two lines, ready for after one green nightly in parallel** (remove both from the list, and move their two
rows of r11's `DECLARED_WITH_THEIR_ROUTE` to its `NOT_DECLARED`):

    tests/acceptance/W1-09/test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder  # serial: race: claims raced from separate processes
    tests/acceptance/W1-09/test_w1_09_review.py::test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim  # serial: race: releases and claims raced from separate processes

## KPI line 4: W1-30's r11 reads the reworked list (batch B, `Rewrite-Reason: DEC-889 item 5`)

`tests/acceptance/W1-30/test_w1_30_r11_declared_here.py` (50 cases): the timed suites' cases with their parameter
sets and routes; every other entry with its route; every live and real-model case of DEC-889 item 5, as collected,
on the nightly route; W1-16's split (the 94 cases of 19 named functions not declared, the 67 others declared serial,
kind `daemon`); W1-50's read-merge case and the cases of no kind not declared; every entry's `<route>: <kind>:
<reason>` with the kind on its route and a reason in words; every entry names a file and a function that exist,
once, and a case the test runner collects. Red against the list before this batch (40 of its 50 cases), green with
the reworked list. It defines the kinds and routes itself (`w1_30_support.py` is not among this ticket's files).

## KPI line 5 (batch B)

| Item | Tests | Today |
|---|---|---|
| W1-30's r13 case gets a limit a loaded start meets (`Rewrite-Reason: W2-M384`) | `tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project`: `--timeout 30` (was 5), the case sleeps 45 s (was 14); nothing asserted changes | green: 1 passed in 48.9 s alone (it was 18 s) |
| W1-50's two live freeze cases remove every `CLAUDE*` variable (`Rewrite-Reason: DEC-784`) | `test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path`, `test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays`: `inherited()` as W1-46's | live: collected, not run here (the lead runs them) |
| one p95 case for a test designer's read on a branch with changes (I1 F-10) | `test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95` (W1-02's fixture world, `w2/integrate` and a ticket branch of 120 changed files; the path shown first: the designer is refused a changed file under DEC-820 (c)) | green today (a guard of DEC-149's budget on a path no case timed: p95 55 ms on a quiet machine); 2.4 s, `serial: latency` |
| W2-M332 times W1-19's warm queries without the memory sampler in the same process (I3 O3 (b)) | none here: the change lies in `tests/acceptance/W1-19/test_w1_19_real_models.py` (its `measured` fixture), not among this ticket's files | returned as a package (below) |

## KPI line 6: the wall-clock limits that went red under load (batch B)

- **W1-02's 5-second bound (168 cases in 29 functions of six files): a limit a loaded machine meets.** The bound
  holds the hook's own time, its CPU time (the hook and the decision process it waits for), still 5 s; the test's
  wait for the process is 18 s of wall time (was 8 s), below the guard's 20-second deadline. 0 s added to the serial
  phase. `Rewrite-Reason: I1 F-14, DEC-823 (b)`; W1-02's README, "Revision of W2-57". The six files: 389 passed in
  7.9 s (`-n auto`). On a quiet machine CPU and wall time agree (0.22 against 0.24 s; 0.17 against 0.16 s).
- **The guard's 20-second deadline (DEC-580, product).** Every W1-50 and W1-03 case that sends a call through the
  guard can meet it (137 functions); running them alone would add minutes to every close for one red seen once, at a
  load of 52 on 20 cores. Not changed here; returned as a package (below). Such a red already names the deadline (the
  guard's reason, "its deadline of 20 seconds was reached, so the call is refused (DEC-580)", is in the message).

## KPI line 7: the live host cases name the network (batch B)

Read as the lead reads it, within this ticket's files: in W1-46's own host cases, at the time a case's session runs,
through the session's own route (the sandbox's proxy), a host that cannot be reached fails the case with a reason
that names the network, never a skip, never a pass, so the next reader does not take it for load
(`Rewrite-Reason: I1 F-1, DEC-892 item 3`; W1-46's README). The probe now keeps curl's exit code, the proxy's CONNECT
answer, the HTTP status and the time. The reasons, shown on sample lines (nothing launched): a timeout through the
proxy gives "the network: through the session's own route (the sandbox's proxy), at 2026-10-27T00:11:05Z,
static.crates.io could not be reached: curl ended with 28 (no answer within curl's 20 s) …; this is the network at the
time the session ran, not load and not the allowlist"; a CONNECT 403 gives "the sandbox's proxy refused … this is the
rule, not the network". `example.com`'s case now passes only on the proxy's refusal (CONNECT 403, how this machine's
sandbox proxy answers a domain off its list, measured 2026-10-27), no longer on a network failure. Live: collected,
not run here. The orchestrator's pre-close network check is a tool outside this repository.

## Packages returned with batch B

- **The route's code is outside the implementer's paths.** The close builds its serial run from the plugin's
  `entries()` in `src/gov/close/command.py`; neither that file nor `src/gov/close/pytest_plugin/` is in the ticket's
  `allowed_paths` (only `src/gov/close/serial.py`, new). KPI line 3's route needs one of them.
- **The guard's 20-second deadline** (line 6): run its 137 functions alone (minutes per close), or leave it to the
  machine's resource gate and the close's quiet window.
- **W2-M332** (line 5): the timing of W1-19's warm queries without the sampler needs `test_w1_19_real_models.py`.

## Runs of batch B that are not mine to make

Live sessions (W1-46, W1-50's two freeze cases, W1-25, W1-49, W2-58's launched sessions, W2-62's live resume, W2-54's
sandboxed worker), real models (W1-19, W1-21's dev-tier file and family check, W2-54's real-embedder case) and the
code-graph daemon's cases (W1-16's 67, W1-20, W2-69's two) are collected only; the lead runs them. W1-16's 94 cases
that start no daemon could not run in this designer's sandbox: W1-16's own fixture makes its folders directly under
`/tmp` (`tempfile.mkdtemp(prefix="w16-", dir="/tmp")`), which the launched sandbox does not let it write (92 errors,
`Read-only file system: '/tmp/w16-…'`; the 8 cases without that fixture passed). The lead runs them in parallel.

Line 8 (the removal of `load_sensitive` entries) is the orchestrator's commit, not a test here.
