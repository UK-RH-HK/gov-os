---
id: DAEO-xm6l
status: closed
deps: [DAEO-g0ip, DAEO-a3m2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-22
tags: [wave-2, implementation, standard, wave-3, deferred]
wbs_id: W2-22
title: gov doctor green
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-a3m2
allowed_paths:
- src/gov/doctor/**
- governance/project/tool-registry.yaml
- tests/unit/doctor/**
kpis:
  success:
  - Doctor reads the installed pytest-xdist version [W2-M287, W2-L336].
  - It does not judge citations inside adoption records or evidence snapshots [W2-M288].
  - After a model-less rebuild it says "semantic index not built", not a canary miss [W2-M289, W2-L206].
  - 'CLI and extension drift is reported by the owner''s policy: a warning below a set gap, a failure above it [W2-M139, W2-M264].'
  - It checks that the hook time limit exceeds the guard's deadline [W2-M201, W2-L215].
  - Model hashes are cached by size and mtime [W2-L101].
  - gov doctor exits 0 on this repository [F-M2, W2-M290].
  failure:
  - A tool at the wrong version still fails; a real canary miss still fails.
profile: STANDARD
sources:
- DEC-729
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-22/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- F-M2
list_rows:
- W2-L009
- W2-L011
- W2-L062
- W2-L101
- W2-L121
- W2-L206
- W2-L215
- W2-L336
- W2-M124
- W2-M139
- W2-M140
- W2-M201
- W2-M264
- W2-M287
- W2-M288
- W2-M289
- W2-M290
- W2-M308
---
# W2-22 gov doctor green

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** K8 (DEC-941 item 3); `gov doctor` green on EXAMIN's copy is W2-27's KPI.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-22), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/doctor/**`, `governance/project/tool-registry.yaml`, `tests/unit/doctor/**`.
- **KPIs, success:**
  - Doctor reads the installed pytest-xdist version [W2-M287, W2-L336].
  - It does not judge citations inside adoption records or evidence snapshots [W2-M288].
  - After a model-less rebuild it says "semantic index not built", not a canary miss [W2-M289, W2-L206].
  - CLI and extension drift is reported by the owner's policy: a warning below a set gap, a failure above it [W2-M139, W2-M264].
  - It checks that the hook time limit exceeds the guard's deadline [W2-M201, W2-L215].
  - Model hashes are cached by size and mtime [W2-L101].
  - `gov doctor` exits 0 on this repository [F-M2, W2-M290].
- **KPIs, failure:** a tool at the wrong version still fails; a real canary miss still fails.

**D9-FATES (DEC-1083):** Retired by DEC-1083 (D9-FATES): B1-24 ("`gov doctor` green" lives in W2-27 and W2-46).

## Fix: the patch-only Claude Code CLI/extension gap (DEC-1227 D6 (a))

Found 2026-11-20 by W2-81's proving run on release 0.1.4 (`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` rows P1,
A1): `gov doctor` exited 3 (`DOCTOR_UNHEALTHY`) in every adopted repository on CLI 2.1.329 against extension 2.1.328,
because any difference of the two strings was `drift` and `drift` counted as unhealthy; the extension auto-updates, so a
patch gap is the normal state. No test caught it (`tests/acceptance/W2-22/` did not exist). The owner chose D6 (a): a
patch-only gap (same major and minor) is drift, reported, exit 0; a minor or major gap, a CLI below the minimum and a CLI
sha256 mismatch at the recorded version still exit 3; drift against the registry's recorded version still exits 3. Kind:
a fix, no new ticket; the ticket stays closed. Failing tests first (`tests/acceptance/W2-22/`, A1; A2 guards the edges);
code `src/gov/doctor/command.py` (`_is_patch_only_gap`, `_blocks_health`). Lead `d6-doctor-drift` (Sonnet), branch
`e2/d6-doctor-drift` (`7db019b2f` tests, `fffebea78` code), merged as `9a4adb350`; on the merged tree `gov accept W2-22`
green and 192 passed (W2-22, doctor units, W1-27, W1-48, W2-57, optin). The Contract's CAP-25 acceptance and CAP-61.e
still read "exits non-zero on drift" and "aligned": their replacement wording goes to the owner with 0.1.5.

## Fix: `gov doctor` checks a tool installed in its own folder (audit 3, M-04; DEC-1232, DEC-1233)

Found 2026-11-22 by the E2 audit 3 (`docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md`, M-04): the registry entries
`node-22.23.5` and `rea-agents` read `ok: false` in doctor's `tools` part, because doctor found a binary only by
`TOOL_BINARIES` or a `PATH=<prefix>:$PATH` in the install line. No test caught it. Required: both found and versioned with
no schema change; a `PATH=` prefix from one tool's install line never answers for another tool of the same binary at
another version (v22.23.5 never for `node` v22.23.3, nor the reverse). Kind: a fix, no new ticket; the ticket stays
closed. Failing tests first: `tests/acceptance/W2-22/test_w2_22_tool_in_own_folder.py` (README ids success-3 to
success-7; 17 red, 13 guards on the base), `1015d60e8`; code `src/gov/doctor/command.py` (a `<binary>-<version>` name maps
to its binary; a tool's places are its own `PATH=` prefix, a local install's `<cd folder>/node_modules/.bin` and a Node's
nvm folder for its pinned version; a folder owned by an entry of the same binary at another pinned version is skipped;
the install line's `~` and `$HOME` read the process's HOME), `d21973e3c`; units `tests/unit/doctor/test_w2_22_own_folder.py`.
Lead `fixes-015b` (Sonnet), branch `e2/fixes-015b`. `gov accept W2-22` green (success-1 to success-7, 46 passed) on the
first run after the engineer's commit; `tests/unit/doctor`, W1-27, W1-06, W1-48, W2-22: 229 passed. On the real machine
`gov doctor --json` now reads `node` v22.23.3, `node-22.23.5` v22.23.5 and `rea-agents` 6.10.1, all `ok: true`; the
`pytest-xdist`, `pytest-timeout` and `pytest-testmon` entries (Python packages with no binary, not in `NO_BINARY_TOOLS`)
still read `ok: false`, as on the base: not this fix's.
