# W2-57 acceptance tests: load out of the close

Ticket `DAEO-cy5o` (W2-57), profile FULL. Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-57). Sources: DEC-892 item 2,
DEC-889 item 5, DEC-899 items 3 and 7, DEC-813, DEC-823, DEC-871, DEC-883 item 5, DEC-886, DEC-890, DEC-784, DEC-915;
lens I's P-IS-6 (`docs/assessment/2026-10/I-SYNTHESIS.md`), I4 findings 2 and 5 and P-I4-5, I2 F12.

Written by the independent test designer (MR-3) from the KPI lines and their sources, before any implementation,
in two batches of one session. **Batch A (this commit): KPI line 1, the rulesync probe, and KPI line 2, the doctor
probes.** Batch B adds KPI lines 3 to 7 (the serial-only list as P-IS-6's two tables, W1-30's r11 and r13, W1-50's
`CLAUDE*` removal, a p95 case for a test designer's read, W2-M332's timing, the resource gate and the network check)
to this folder and to the earlier files the ticket names; its sections below are marked "batch B".

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

Batch A today: 13 cases, 8 red and 5 green (the guards), in 13 s under `-n auto`.

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

## Batch B (to come in this folder)

KPI line 3 (the serial-only list as P-IS-6's two tables; every kept entry with its reason; the moves to the parallel
phase and to the nightly; latency cases alone), line 4 (W1-30's r11 test reads the reworked list), line 5 (W1-30's
r13 limit, W1-50's `CLAUDE*` removal, a p95 case for a designer's read, W2-M332), line 6 (the resource gate) and line
7 (the network check). Line 8 (the removal of `load_sensitive` entries) is the orchestrator's commit, not a test here.
