# W2-170 evidence: the memory audit's set record (DAEO-61vm; DEC-1101 (1)-(2), DEC-1125 (2))

- **Who:** the engineer (launched worker, sandboxed), 2026-11-11, build run 1. Branch `w2/W2-170`.
- **Built to:** the ticket's KPI lines S1-S6 and F1-F5 and its `## Interface` sections 1-10 (the CTO's readings 1-8
  included), generalising the fresh 80's `preflight.py` and `f80lib.py`. The acceptance cases
  (`tests/acceptance/W2-170/`) were never read; only their run's pass and failure lines.

## What was built

| Path | What |
|---|---|
| `src/gov/memaudit/__main__.py` | `python3 -m gov.memaudit preflight\|void\|declare`: a thin wrapper; exit 0/1/2/3/4; argparse errors 4, `--help` 0; any unexpected error the one line `ERROR: <class>` on stdout and stderr. |
| `src/gov/memaudit/layout.py` | `paths(sets_root, audit)`: every path of section 2 derived from the two flags and checked inside the root; `is_used`; the notes of the highest round; the set's entries. |
| `src/gov/memaudit/say.py` | `say(line, sets_root)`: the only printer; refuses a line holding the root's path and a slash, `fixtures/`, `runs/`, `indep-walls/` or `hidden` (prints the refusal, exits 4); returns `("ok", {"printed": 1})`. |
| `src/gov/memaudit/ledger.py` | `append(run_dir, event, **fields)`: `ledger.jsonl`, one object per line with `seq`, `at`, `event`, synced. |
| `src/gov/memaudit/preflight.py` | `run(...)`: the ten checks of section 3, `PREFLIGHT.json` (whole or nothing) and the `preflight` ledger line; the selection lists from `selection.json` or the launch script's stage B4 rule. |
| `src/gov/memaudit/drops.py` | `apply(...)`: the drop and void rule of section 5 (`os.rename` into `hidden/dropped/`, never overwriting), `DROPS.json`, the `drop` and `void` ledger lines. |
| `src/gov/memaudit/declare.py` | `declare(...)`: the refusals first, then the map entry, `DECLARATION.json`, the `declaration` line, `USED` (`O_EXCL`, after a probe file's own mtime passes the declaration's), the `used` line. |
| `src/gov/memaudit/tables.py`, `common.py` | The domain and subsystem tables and the quotas as data; git at a commit, whole-file JSON, the set's digest. |
| `tests/unit/memaudit/` | 65 unit tests on planted roots under `tmp_path` (a repository with two commits, a sets root with its own map, a runs dir, a pool, a store, a gov link into `pin-<12 hex>`). |
| `governance/project/test-map.yaml` | One coupling: `src/gov/memaudit/**` → `tests/unit/memaudit/` (S6). |

## The counts

- **Acceptance** (`pytest tests/acceptance/W2-170` with this worktree's `src/`, the run's required filter, an empty
  `HOME`): **165 passed, 0 failed, 0 deselected** (head `564c397b2`). The first run had 6 failures, each fixed to the
  Interface's words: `say` exits 4 on a refused line (section 1), and a fitting line whose verdict is not exactly
  `accept` is counted by its codes, `UNFIT` only for a line that does not fit (section 5).
- **Unit tests:** 65 passed (same filter; nothing deselected).
- `gov accept W2-170` ends `error_kind: crash` in the launch sandbox with no line counts (twice); the per-line counts
  are for the CTO's run outside the sandbox.

## One row per KPI line

| Line | Evidence |
|---|---|
| S1 | Unit: a clean planted set ends `PRE-FLIGHT: every check as expected`, exit 0, `runs/<A>/` mode 700; one planted defect per check, each refused with its own code and the other nine ok: PF-COUNT (35 files; a stray entry), PF-FORM (five forms), PF-COMMIT, PF-QUOTA (names and counts, no ids; 36-39 read as at most), PF-SPREAD (a thin domain; a heavy subsystem), PF-DRAWN (planted `selection.json`; derived from `AUDITS.log`/`SEEDS.log`; lists that cannot be had name every drawn question), PF-SOURCE (missing path; heading lost with lines outside; re-anchored counted), PF-EVALNS, PF-DUPPOOL, PF-IDEXISTS (whole token; `no_token` counted); an unreadable map at the commit is `ERROR: <class>`, exit 4. Acceptance S1 cases pass. |
| S2 | Unit: 3 drops go on (kept 37, scales recomputed, files under `dropped/`); 5 drops `VOID VOID-COUNT kept 35 dropped 5`, exit 2, no `USED`, no `DECLARATION.json`; a drop leaving plan at 3 `VOID-DOMAIN`; `DR-NOTES`, `DR-DONE`, the highest round read, `UNFIT`/`NOLINE`, a subsystem over recorded not void, an existing dropped file never overwritten. Acceptance S2 cases pass. |
| S3 | Unit: `DECLARATION.json` then `USED` (mtime strictly later in ns), ledger `preflight, drop, declaration, used`; every key and the bar for n = 39 (34, 1, 38); a second declare exits 3 and changes no file; pool off: `DC-DECISION pool`, `ok: false`, no `USED`, no map entry; with `--decision DEC-1234` ok and `USED`; `USED` refused when the file time never passes. Acceptance S3 cases pass. |
| S4 | Unit: the sets root's map gains exactly one entry, every other byte kept; `git status --porcelain` of the planted repository empty before and after; the entry passes `set_fault`, its hidden glob covers `hidden/`, its five roles leave out the orchestrator (the measure's own acceptance); an equal entry is left as is, a different one or no block is `DC-MAP`. Acceptance S4 cases pass. |
| S5 | Unit: a planted question with unique words in its question, gold answer, path and heading: none of them, nor `docs/`, in stdout, stderr or any file of the run folder; no `fixtures/`, `runs/` or the root's path printed; `say` refuses each folder word and the root's path. Acceptance S5 cases pass. |
| S6 | Unit: the live test map's couplings map `src/gov/memaudit/preflight.py` to `tests/unit/memaudit/` (by `gov.close.select`'s own `match`) and it is not shared core; `--help` of each subcommand exits 0. Acceptance S6 cases pass. |
| F1 | As S5, and an unexpected error prints only `ERROR: <class>` on stdout and stderr (a planted exception's text is absent). |
| F2 | As S3: the order by file times and the ledger; a second run exits 3 and writes nothing; `void` and `preflight` exit 3 too once `USED` exists. |
| F3 | Every test plants its roots under `tmp_path` and gives child processes a planted empty `HOME` and an explicit `--runs-dir` or `selection.json`; the repository is read only through `git` at the commit (`GIT_OPTIONAL_LOCKS=0`); its status stays empty. |
| F4 | As S2: the 3 dropped files are under `dropped/`; a void audit has no `USED` and no `DECLARATION.json`, and `declare` refuses it. |
| F5 | `git diff --name-only 79a8fb87f HEAD` lists only `src/gov/memaudit/**`, `tests/unit/memaudit/**`, `governance/project/test-map.yaml`, this file, and the merge's `.tickets/DAEO-61vm.md` and `DECIDED-NOT-DONE.md`. |
