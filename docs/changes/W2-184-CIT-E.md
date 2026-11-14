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

1.2 matching (comment tail dropped, either-way fnmatch, `*` crosses `/`); 1.4 as amended 2026-11-14 (section 6 below: a file
present is read on every worker launch and a malformed one refuses; no file, the launch as before W2-184); 3.1 floor judged on the table's effort, none where the table is low or
medium; 3.2 a max the table or the probe sets needs no reason, a launch's own max does; 4.3 a trial's effort below the floor
is accepted, a trial's max needs `--reason`; 5.2 a fail-open finding is checked before two failed reviews; 6.2 `probe` is a
sixth `model_source` value, set only when the probe changed the model; 7.2 `command.py` is not edited here.

3.2a (the lead's amendment, batch eng-2): a max after `--` equal to the effort already resolved (the table's max, or the probe's max on a FULL ticket's round 2+) needs no `--reason`, and its `effort_source` is `probe` when it equals the probe's, `after --` when it equals the table's; only a max that differs from the resolved effort, or a trial's max, needs `--reason` (`_rubric` in `launcher.py`).

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

## 5. Interface 1.4, amended on 2026-11-14 (batch eng-3)

The earlier 1.4 refused every launch of a role whose file carries a `Launch by criticality` line (the kernel engineer's and
test designer's do) in a project with no `criticality.yaml`. The full run at d858e409b showed 77 reds from that: 50 of W1-46's
suite, 12 of W1-32's, 8 of W1-28's, 6 of W1-50's (fixtures that copy the kernel role files and have no such file), and 1 of
W2-60a's (the auditor launched twice on a FULL fixture ticket, which the earlier 1.4 made a probe that needs the file). It also
went against DEC-1167 (2): an adopted repository with no file, such as EXAMIN's copy, has to launch on each role's `Launch
default` line. The lead replaced 1.4. `_rubric` (`launcher.py`) now tests `criticality.exists(root)` once: **with no file** the
launch is as before W2-184 (the role's `Launch default` for every role and class, source `role default`; no promotion and no
probe records read; no review count, so no probe and no same-setting refusal; `criticality`, `promotion` and `review_round`
null; a `Launch by criticality` line is still read and a malformed one still refuses, but is not applied); a model after `--`
other than the default, the floor (judged on the default line's effort), max and `--reason` (3.2a included), the forms of
`--reason` and `--owner-named` still apply; `--trial` is refused naming `governance/project/criticality.yaml` before any trial
file is read. **With the file** it is read on every worker launch (an unreadable or malformed one refuses, naming it) and
sections 2.3, 4.3, 5 and 6 apply as written. `criticality.py` is unchanged but for its docstring. The W2-60a red of the
earlier section 5 is gone: its fixture has no file, so the second auditor launch is a plain launch.


## 6. Review round 1 (batch eng-4, after `docs/probes/DAEO-6f0s/PR-DAEO-6f0s-round-1.md`)

The FULL review's round 1 failed S1 on F1 (blocking, fails open): the project's `criticality.yaml` had no rule for DEC-1120 (1)'s
hidden sets, so a ticket on `fixtures/evaluation/<set>/hidden/**` resolved to C2, or C1 beside a probe-record path, and launched
below C3. The C3 rule now holds `fixtures/evaluation/*/hidden/*` (the path map's hidden halves; interface 1.5 as amended), and,
riding along (DEC-802), F8's permission paths `.claude/settings.local.json`, `governance/project/secrets.yaml` and
`governance/project/indep-walls/*` beside `.claude/settings.json` and `governance/project/held-out.yaml` (stricter only; a
visible half stays at the default). F2 (fails open, rides along): `_rubric` (`launcher.py`) refuses an auditor launch on a FULL
ticket whose `review_round` is 3 or more, naming the round and DEC-1010, unless `--owner-named` is given, whatever its setting
(interface 6.3 as amended), so a round 2 on another effort (e.g. `--effort xhigh`) no longer opens a third round; the
same-setting rule stays for round 2, and where a round 3 also repeats a counted setting the one refusal names both (the round
and DEC-1010, and the repeated record's session, model and effort). Builder cases: each hidden-set and permission path at C3 in the project's own file, the same
beside a `docs/probes/<id>/**  # ...` path on each profile; round 3 after a round 2 at xhigh refused, and accepted with
`owner_named`; the same-setting case moved to round 2. Left for the CTO as rows: F3 (resuming round 1 after round 2 refused),
F4 (a trial replaces the probe), F5 (five closed tickets' legacy verdict blocks refused), F6 (promotion on any fail-open finding,
rows included; this record's F2 promotes W2-184's next round), F7 (no file, a launch off the table, recorded only as
`criticality: null`), F9 (a probe-record path lowers an unlisted-area ticket to C1) and F10 (out of scope: an adopted repository
with no file does not route by RUBRIC-2).
