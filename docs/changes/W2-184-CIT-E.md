---
id: W2-184-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-11-13
branch: w2/W2-184
base: w2/W2-184 @ b624fa3c1
ticket: DAEO-6f0s
author: engineer (W2-184)
decisions_carried: [DEC-1120, DEC-1119, DEC-1167, DEC-1157, DEC-1126, DEC-839, DEC-1010, DEC-1014]
state_class: EVIDENCE
---

# W2-184 (DAEO-6f0s): RUBRIC-2 at launch — change-execution record

What the ticket built, against the interface of `.gov-runtime/scratch/briefs/INTERFACE.md` (W2-60a run 4d's proposal, adopted at
claim, DEC-1157, with the points the ticket lead settled). `gov launch --plan`, a lead launch and W2-60a's refusals and
record fields are unchanged.

## 1. What changed

| File | Change |
|---|---|
| `governance/project/criticality.yaml` (new) | The project's rules from DEC-1120 (1): C3 guard, hooks, settings, path map, held-out, operator agent, kernel, Contract; C2 `src/*`, test map, schemas, FULL tickets; C1 `docs/*`, orchestration; default C2; `opus: claude-opus-5-5`. This ticket resolves to C2. |
| `src/gov/launch/criticality.py` (new) | `ticket_criticality(root, ticket)`, `opus_model(root)`, `load`, `exists`: the file's form checked whole (a key twice, a wrong key, a class or profile not listed refuse, naming the file); the highest class among the rules that match; an allowed path loses its `  # comment` tail; a glob and a path match when either, as an fnmatch pattern, matches the other. The ticket's `class` is never read. |
| `src/gov/launch/role.py` | `Launch by criticality` line (optional, once, four entries C3, C2, C1, C0, plain or "on FULL ... otherwise" form): `read_role()["by_criticality"]`, `read_by_criticality`. `launch_default` (the plan) reads the default line alone, as before. |
| `src/gov/launch/launcher.py` | `launch(..., *, reason, trial, owner_named)`; `_rubric` resolves model and effort (table, floor, max and `--reason`, after `--`, trial, promotion, FULL ticket's probe, same setting twice) before the gate and before any record, temp folder or session; the record's nine new keys; `_worker_plan` and `_launch_line` carry them. |
| `src/gov/launch/record.py` | Not changed: the record's keys are written by `_launch_line` through `record.write`; `record.folder` is the folder the auditor launches are counted in. |
| `tests/unit/launch/test_w2_184_*.py` (new) | Builder tests, below. |

## 2. Settled points built as written

1.2 matching (comment tail dropped, either-way fnmatch, `*` crosses `/`); 1.4 the file read only when needed, else read if there
(malformed refuses) and `criticality` null if absent; 3.1 floor judged on the table's effort, none where the table is low or
medium; 3.2 a max the table or the probe sets needs no reason, a launch's own max does; 4.3 a trial's effort below the floor
is accepted, a trial's max needs `--reason`; 5.2 a fail-open finding is checked before two failed reviews; 6.2 `probe` is a
sixth `model_source` value, set only when the probe changed the model; 7.2 `command.py` is not edited here.

## 3. The `command.py` package (outside the ticket's paths)

`src/gov/launch/command.py` is not in `allowed_paths` (interface 7.2). The patch the lead applies is
`.gov-runtime/scratch/eng/command.py.diff` (three `add_argument` lines for `--reason`, `--trial`, `--owner-named`, the usage
line and the three keywords passed to `launcher.launch`); it applies cleanly to b624fa3c1 (`git apply --check`).

## 4. Evidence

| Item | Result |
|---|---|
| Builder tests (`tests/unit/launch/test_w2_184_*.py`) | 197: criticality 61, role line 35 (each kernel role file's real line parses), launch 101 |
| `tests/unit/launch` whole folder, after | 537 passed (86 deselected: local_only, real, green_here, time_limit) |
| Regression set on the base (clean clone at b624fa3c1) | 1207 passed, 19 skipped, 1425 deselected, 0 failed |
| Regression set after | 1402 passed, 19 skipped, 1425 deselected, **1 failed** (below) |
| Mutation spot checks (12 mutants of the floor, max, model after `--`, promotion, same setting, probe, class order, comment tail, trial class, fail-open order, other tickets' records) | 11 killed on the first run; the survivor (comment tail kept) got its own case, `test_the_comment_tail_matters_where_the_rule_names_the_path_exactly` |

Left out of every run: the cases named `real`, `green_here` and `time_limit`, and the `local_only` mark (DEC-1012).

## 5. The one red, and why it is not fixed here

`tests/acceptance/W2-60a/test_w2_60a_user_permissions.py::test_the_user_s_ask_and_deny_rules_reach_the_session_beside_the_launcher_s_own[independent-auditor]`
launches the auditor twice on the same FULL ticket (DAEO-zz6a) in a fixture with no `criticality.yaml`, an auditor default
of Opus max and no probe records. Under the interface the second launch is review round 2: the probe applies (6.2), so the
file is needed (1.4) and its absence refuses; and with a file the probe's setting (Opus max) would equal the first
review's (6.3). The interface (and the brief) assumed "at most one auditor launch per ticket" in the existing fixtures. This
test is W2-60a's and is not edited here. The choice is the lead's: re-baseline that case (launch the second time as another
ticket, or plant a record), or settle that a project with no `criticality.yaml` counts no review round and applies no
probe (1.4's absent-file case widened to section 6).
