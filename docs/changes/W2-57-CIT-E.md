---
id: W2-57-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-27
branch: w2/W2-57
base: d835cf51bbea
ticket: DAEO-cy5o (W2-57)
author: engineer (W2-57, run 1, batch 1)
decisions_recorded: []
decisions_carried: [DEC-892, DEC-871, DEC-886, DEC-915, DEC-500, DEC-186, DEC-595, DEC-135]
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
