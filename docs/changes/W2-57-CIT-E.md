---
id: W2-57-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-27
branch: w2/W2-57
base: d835cf51bbea
ticket: DAEO-cy5o (W2-57)
author: engineer (W2-57, run 1, batch 1; run 2)
decisions_recorded: []
decisions_carried: [DEC-892, DEC-871, DEC-886, DEC-915, DEC-500, DEC-186, DEC-595, DEC-135, DEC-925, DEC-924, DEC-889, DEC-527, DEC-549, DEC-555, DEC-802]
state_class: EVIDENCE
---

# W2-57: change-execution record (CIT-E), batch 1: the rulesync probe and the doctor probes

This records the first batch of W2-57 (DAEO-cy5o): KPI lines 1 and 2, the code half. DEC-892 item 2 makes the rulesync
probe W2-57's first item; DEC-871 and DEC-886 hold W1-38's three cases and W1-07's `[doctor]` on `load_sensitive`
until W2-57. The sources are I4 finding 2 (the probe), finding 5 (the exception `gov doctor` does not catch) and P-I4-5,
and I-SYNTHESIS §3.1 C and P-IS-6. The serial-only list, its route to the nightly and the `load_sensitive` removals are
not in this batch.

## 1. The changes

| # | File | Change | Evidence |
|---|---|---|---|
| 1 | `src/gov/adapters/portability.py` | `TIME_LIMIT`, the limit of each of the check's two rulesync calls (`--version`, `generate`), goes from 10 to 25 seconds, set from the measurement in §2. Nothing else changes: a call that answers late but within the limit is waited for and compared as a prompt one; a call that gives no answer in time is `RULESYNC_FAILED` "rulesync --version: no answer within 25 seconds" (or `generate`), a finding, so the check is red and exits 1; a rulesync that is absent keeps `RULESYNC_ABSENT`. | acceptance `tests/acceptance/W2-57/test_w2_57_rulesync_probe.py` (7 passed); `tests/unit/adapters/test_portability.py::TestVersion::test_both_calls_at_their_limit_end_inside_the_runners_limit` (new: holds the arithmetic of §3) |
| 2 | `src/gov/doctor/command.py`, the probes | Every timed probe runs through `_probe`: the tools' version probes (5 s before) and Claude Code's version probe (3 s before) get `VERSION_LIMIT` = 30 s; the reranker venv's `uv pip freeze` (10 s before) gets `FREEZE_LIMIT` = 40 s. All the timed probes of one `run` share `PROBE_BUDGET` = 90 s: a probe gets its own limit or what is left of the budget, whichever is less, and none once it is spent. A probe that gives no answer raises `TimeoutExpired`, which its caller already reads as not answering (no version read, no hash): never a pass. | acceptance `tests/acceptance/W2-57/test_w2_57_doctor_probes.py` (6 passed: four probes that answer after 15 s, or 25 s for the freeze, are read; a probe that never answers is read as not answering and doctor still ends) |
| 3 | `src/gov/doctor/command.py`, `run` | Each part of doctor runs through `_part(name, check, …)`. An exception a part raises (I4 finding 5's routes: a decode error from `_git`'s `text=True`, an unguarded read, the lock comparison) is raised again as `GovError("DOCTOR_PART_FAILED", …)`, with the part, the exception's type and its text in the message and in `details`. `gov doctor` then prints the API-0002 envelope with `ok: false` and exits 1 (`main.py` catches `GovError`), never a bare traceback. The exception is not swallowed: no part becomes a pass or a quiet "not read". `gov status`'s `_doctor` re-raises a `GovError` without `healthy` in its details, so its own `_part` shows the same text as the reason doctor was not read. | acceptance `test_w2_57_doctor_probes.py::test_a_probe_exception_ends_doctor_with_the_envelope_and_its_text`; the envelope in §4 |
| 4 | `tests/unit/adapters/test_portability.py` | One case: twice `TIME_LIMIT` plus 10 s for the check's own work is no more than `gov check`'s `TIMEOUT_S`. | 139 passed in `tests/unit/adapters` and `tests/unit/doctor` |

## 2. The measurement

Method: `measure.py` (a script in the session's scratch folder) starts a pytest run with `-n 40` in its own process group,
then times each probe in a loop until the run ends: `rulesync --version`, and `rulesync generate --targets
claudecode,agentsmd --features rules,hooks,permissions,subagents,commands,skills --input-roots <this worktree>/.rulesync`
in an empty temporary folder (the check's own `generate`, from the same sources), and doctor's probes: `node --version`,
`gitleaks --version`, `claude --version` and `uv pip freeze --python <reranker venv>`. Each sample records the 1-minute
load average from `/proc/loadavg`. The machine has 20 logical CPUs. rulesync 24.0.0, Node 22.23.3.

| Run | Load (1 min) | `rulesync --version` (s) | `rulesync generate` (s) | doctor's version probes (s) | `uv pip freeze` (s) |
|---|---|---|---|---|---|
| Idle, 5 rounds | 0.18 to 0.25 | 0.30 to 0.32 | 0.41 to 0.42 | at most 0.20 | (uv's cache refused by the sandbox; see below) |
| Beside `tests/acceptance/W1-38`, `-n auto`, 17 rounds | 1.4 to 6.2 | 0.32 to 0.58, median 0.53 | 0.43 to 0.81, median 0.77 | at most 0.32 | at most 0.08 |
| Beside W1-38, W1-26, W1-27 and `tests/unit`, `-n 40`, 45 rounds | 9.9 to 48.2 | 0.31 to 2.26, median 0.78 | 0.42 to 4.22, median 1.06 | at most 1.77 (gitleaks) | at most 0.05 |

I4 measured `--version` at 0.33 to 2.81 s at loads of 6.6 to 47.1 (42 samples). Yet two closes saw a call pass 10 s
(W2-53's of 2026-10-20 and W2-63's of 2026-10-22). So a close's spikes go past what a sampled loop reaches, by a factor
of at least 2.4 over `generate`'s measured worst and 3.5 over I4's `--version` worst. The limits chosen: 25 s for each
rulesync call (6x `generate`'s measured worst, 11x `--version`'s); 30 s for a version probe (17x the measured worst);
40 s for the freeze. `uv pip freeze` needs a writable uv cache. The sandbox refuses `~/.cache/uv`, so the loaded runs
gave uv a temporary cache.

## 3. The arithmetic against the limits that hold these

- **`gov check`:** the declaration `template/governance/kernel/checks/adapter-portability.yaml` states no `timeout`,
  so `gov check` gives the check 60 s (`src/gov/check/runner.py`, `TIMEOUT_S`). The check makes its calls one after
  the other, and `generate` runs only when `--version` gave the expected answer. Worst case, the check ends by itself
  with its `RULESYNC_FAILED` timeout finding: `--version` answers just inside 25 s and `generate` reaches its 25 s,
  so 50 s. That leaves 10 s for the interpreter's start, the registry read, the kernel comparison and the held-out step
  (the whole check, both calls included, took 0.8 s on this worktree at load 2, its calls about 0.7 s of that). The
  runner never cuts it. If `--version` itself gives no answer, the check ends
  after about 25 s. The new unit case holds `2 × 25 + 10 ≤ 60`.
- **`gov doctor`:** one probe that never answers costs 30 s (40 s for the freeze). However many never answer, the
  timed probes together stop at 90 s. Doctor's other parts took 4.6 s and 0.6 s at load 19 (I4 finding 5), so
  `gov doctor` ends near 100 s at worst, well inside the 180 s W1-07 gives the whole command. A probe the budget no
  longer reaches is read as not answering, so it is a failure, never a pass.

## 4. How a doctor exception now reads

A git repository with `core.quotePath false` and a committed rename of a file whose name is not UTF-8 (`caf\xe9.txt`),
then `gov doctor --json` (exit 1):

```json
{"ok": false, "command": "doctor", "result": {}, "session": "", "error": {"code": "DOCTOR_PART_FAILED", "message": "gov doctor's path_compliance part raised UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 8: invalid continuation byte", "details": {"part": "path_compliance", "exception": "UnicodeDecodeError", "text": "'utf-8' codec can't decode byte 0xe9 in position 8: invalid continuation byte"}}}
```

Before this change the same command printed a traceback ending in that `UnicodeDecodeError`, with no envelope.

## 5. The runs

All with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`,
Node 22 on the PATH, after commit `5ec92077f8fd`:

| Suite | Result |
|---|---|
| `tests/acceptance/W2-57/test_w2_57_rulesync_probe.py`, `test_w2_57_doctor_probes.py` (`-n auto`) | 13 passed (8 of them failed before the change) |
| `tests/acceptance/W2-57/` as a whole (`-n auto`) | 18 passed, 1 failed: `test_w2_57_nightly_route.py`'s route case, the serial-only list's route, which is not this batch's |
| `tests/acceptance/W1-38` (`-n auto`) | 201 passed, 0 skipped, 0 failed |
| `tests/acceptance/W1-33` | 113 passed |
| `tests/acceptance/W1-07` (`-n auto`) | 223 passed |
| `tests/acceptance/W1-27` (`-n auto`) | 174 passed, 2 failed: `test_w1_27_rebuild_r4.py::test_rebuild_codeintel_reason_is_measured` and `::test_rebuild_codeintel_is_recreated_when_tool_answers` ("rebuild did not ask the code index's tool to index"). Both are `gov rebuild`'s, not doctor's, and both were already red in the loaded measurement run, before any edit. |
| `tests/acceptance/W1-26` (`-n auto`) | 415 passed, 1 skipped (`test_w1_26_command.py:44`, the full project does not pass gov check yet) |
| `tests/unit/adapters`, `tests/unit/doctor` | 139 passed |
| `tests/unit` (`-n auto`) | 2644 passed, 1 skipped (`tests/unit/retrieval/test_lexical.py:54`, no `govbridge`) |

# Run 2: the close's route to the nightly (B1) and the doctor budget (R1)

Run 2 (owner, DEC-925 item 3) does two things. The first is P-W2-57-B B1 (a), KPI line "Run 2": W2-57 is widened to the
serial-phase call in `src/gov/close/command.py`, and gate (h)'s line stays W2-07's round 2's (DEC-924 item 3). The
second is R1, a ride-along (DEC-802): reviewer F1 of run 1, an unread Claude Code version read as a pass. The
acceptance cases are the test designer's run 2 files, `tests/acceptance/W2-57/test_w2_57_nightly_route.py` and
`test_w2_57_doctor_claude_code_unread.py`. Before this change 3 of their 5 cases failed: the route case, because the
nightly entries ran in the serial phase, and both doctor cases, which read `claude_code` as `pass` with
`cli_version: None`.

## 6. The changes

| # | File | Change | Evidence |
|---|---|---|---|
| 5 | `src/gov/close/serial.py` (new) | `nightly(root)` reads the list (`gov_close_serial_only.LIST_REL`, its entry as the plugin takes it: the text before ` #`). An entry's route is its comment's first word, before the first `:`. It gives the entries that every line naming them routes to `nightly`. `phase(root, declared)` gives the entries of `declared` that are not routed there, in their order. Fail closed: an entry with no comment, an unknown first word (`weekly`, `Nightly`, `nightly` without its colon) or a second line that keeps it serial stays in the serial phase. A list that is not UTF-8 text raises `UnicodeDecodeError`, never "no list". | `tests/unit/close/test_serial.py` (new, 11 passed) |
| 6 | `src/gov/close/command.py`, `_run_tests`, the serial phase's call only | Unchanged: `declared` is still the list's entries in scope, and while one is in scope the parallel run carries the plugin. The plugin deselects every listed entry from the parallel run, either route, so a nightly entry is collected and left out there even when every entry in scope is a nightly one. Then `declared = serial.phase(root, declared)`, and the run afterwards is made only when an entry is left. It is given exactly those entries (the plugin's DEC-549 check holds for them), and the close's evidence names them as its `cases`. The list is still read first by `serial_only.entries`, inside the existing `SERIAL_ONLY_LIST_UNREADABLE` refusal, so an unreadable list refuses the close as before. Nothing else in the file changes (7 lines added, 4 removed: one import and the call). | `test_w2_57_nightly_route.py` (passes; red before) |
| 7 | `src/gov/doctor/command.py`, `_probe` and `_check_claude_code` | Both routes. (a) `_probe(..., shared=False)` keeps a probe out of the shared `PROBE_BUDGET`: Claude Code's version probe has its own `VERSION_LIMIT` (30 s), so the tools' probes that run before it can no longer leave it no time. (b) A CLI that is found but whose version is not read (no answer within the limit, a failed call, or `--version` gave no version) makes the part `unmeasured` where it would be `pass`. Its `reason` reads "the Claude Code CLI's version was not read: …" with the cause. A `fail` or `drift` found otherwise stays. No CLI at all keeps today's reading. Why both: (a) alone leaves a timeout or a missing version a pass, and (b) alone would leave a machine whose other tools hang unable to read a CLI that answers at once. The bound: the shared probes stop at 90 s and Claude Code's probe at 30 s, so with doctor's other parts (4.6 s and 0.6 s at load 19) `gov doctor` ends near 125 s at worst, inside W1-07's 180 s. | `test_w2_57_doctor_claude_code_unread.py` (2 passed; red before: a CLI that never answers, and three hanging tools before a CLI that answers 2.0.0 at once, now read `fail` below the minimum) |

## 7. The runs of run 2

All with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` (`gov.__file__` is
`/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`), `-p no:cacheprovider -o tmp_path_retention_policy=failed`,
Node 22 on the PATH, after commit `8d34ea94ba5a`:

| Suite | Result |
|---|---|
| `tests/acceptance/W2-57` (`-n auto`) | 21 passed |
| `tests/acceptance/W1-30` (`-n auto`) | 537 passed |
| `tests/acceptance/W2-66` (`-n auto`) | 168 passed, 1 skipped (`test_w2_66_live_test_map.py:466`, the path map no longer holds `test_inputs`), 1 failed: `test_w2_66_lead_verification.py::test_no_file_a_plain_run_reads_for_its_configuration_or_collection_changes`. This is the known red of DEC-919: the branch changes `serial-only.txt` and two `conftest.py` files. |
| `tests/acceptance/W1-27` (`-n auto`) | 174 passed, 2 failed: `test_w1_27_rebuild_r4.py::test_rebuild_codeintel_reason_is_measured` and `::test_rebuild_codeintel_is_recreated_when_tool_answers`. Both are `gov rebuild`'s, the same two as run 1 (`Read-only file system: '/tmp/gov-cbm-1000/…'`, the sandbox), not doctor's. |
| `tests/acceptance/W1-07` (`-n auto`) | 223 passed |
| `tests/unit/close` (`-n auto`) | 428 passed |
| `tests/unit` (`-n auto`) | 2655 passed, 1 skipped (`tests/unit/retrieval/test_lexical.py:54`, no `govbridge`) |
