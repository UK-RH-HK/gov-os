# W2-172 (DAEO-p8tv) evidence: the memory audit's driver and schedule

Engineer's record. Branch `w2/W2-172`, base `80da3fbcca0d`. Profile FULL, class C2.

## What was built

- `src/gov/memaudit/schedule.py`: the clock seam (`GOV_MEMAUDIT_NOW`), the runs folder rule, the store link and its head,
  the churn of a commit, the active-and-stable rule (`decide`), and the subcommands `due`, `status` and `baseline`.
- `src/gov/memaudit/driver.py`: `run` (items 2 to 5): the refusals of item 3, the lock, `STARTS.log`, the twelve steps as
  child processes, the canary retry, the USED boundary, the gate wait, `HISTORY.jsonl`, `COUNTS.json`.
- `src/gov/memaudit/digest.py`: the `figures` reader (item 6) and the digest block's twelve lines (item 7).
- `src/gov/memaudit/__main__.py`: the five new subcommands joined to the parser; the existing subcommands' code is
  unchanged.
- `governance/project/orchestration/tools/memaudit_cron.sh`: the cron wrapper (item 8); `grep -c crontab` is 0.
- `tests/unit/memaudit/test_driver.py`: 11 unit cases (churn, mode rule, `due` at 5/6/27/28 days, the USED boundary,
  the digest's twelve lines and the "not reached" forms, the figures reader).

## Per KPI line

The acceptance files are named for the KPI line they serve; the engineer reads their names and results only.

| KPI | acceptance file | result |
|---|---|---|
| S1 | `test_w2_172_s1_cycle.py` | passes |
| S2, S4 | `test_w2_172_s2_s4_refusals.py` | passes, except `test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there`: awaiting the test designer's revision (it plants the folder and no `STARTS.log` line; TD-2 (b) judges RN-NAME by `STARTS.log`) |
| S3 | `test_w2_172_s3_stops.py` | passes |
| S5 | `test_w2_172_s5_due.py` | passes |
| S6 | `test_w2_172_s6_baseline.py` | passes |
| S7 | `test_w2_172_s7_digest.py` | passes |
| S8 | `test_w2_172_s8_status.py` | passes |
| S9 | `test_w2_172_s9_cron_gate.py` | passes |
| F1, F4 | `test_w2_172_f1_f4_access.py` | passes |
| F5 | `test_w2_172_f5_paths.py` | passes |

## Pytest summary lines (run through `heavy_slot.sh`, HOME an empty scratch folder, `-m "not local_only" -k "not real and not green_here and not time_limit"`)

- `tests/acceptance/W2-172`: `1 failed, 160 passed` (the one red is the RN-NAME case above).
- `tests/unit/memaudit`: `230 passed`.
- `tests/acceptance/W2-170 tests/acceptance/W2-171`: `1 failed, 317 passed, 2 skipped`. The red is
  `test_w2_171_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows`: it lists every path this branch
  changes (this ticket's own and the designer's tests) as outside W2-171's allowed paths; it would be red on any later
  branch and is outside this ticket (the base-red rule). No W2-170 or W2-171 behaviour case failed.

The exclusion left out the `local_only` cases and those named `real`, `green_here` or `time_limit`.

## Readings of the Interface (item numbers)

- **Item 3, TD-2 (b).** `RN-NAME` is a `STARTS.log` line naming `<A>`; the audit's folder is not consulted. A refused run
  writes `COUNTS.json` and the digest only where `<R>/<A>/` is absent.
- **Item 3 / item 7.** A refusal prints no separate `REFUSED` line: the digest's line 11 is `REFUSED <code>` and the
  digest is printed (the F3 case counts the lines that start with `REFUSED`). A stop prints `STOPPED <step> <exit>` and
  then the digest.
- **Item 1, TD-1 (b).** The digest holds no `--force`; `COUNTS.json` and `STARTS.log` do.
- **Items 9 and 11 without a link.** `due` and `status` use the store link when it resolves (`--store-link`, else
  `rebuild.yaml`), and the main line's tip when it does not. `status` accepts `--store-link` (the Interface lists it for
  `run` and `due`); `run` refuses with usage (exit 4) when the link cannot be read.
- **Item 9, "the last audit commit".** The last `HISTORY.jsonl` line's commit, else the last `AUDITS.log` line's, read
  before the cycle starts (the auditor's delivery appends to `AUDITS.log` during it). A commit the repository does not
  hold names no retrieval path.
- **Item 9, reason codes.** Fewer than 3 measured audits: `start`. Otherwise a back-to-weekly trigger (`churn`,
  `retrieval`, `verdict`, `pool`, in that order), else `stable` (monthly) when the last three were calm, else `active`.
  `next` is `last start + 6 d` (weekly) or `+ 28 d` (monthly), never before today.
- **Item 8, gate busy.** The wait is counted by `GOV_MEMAUDIT_GATE_POLL_S` steps and by the real clock. When
  `GOV_MEMAUDIT_NOW` is set the polls are counted and not slept (a fixed clock never advances). The stop prints
  `STOPPED <step> gate busy`; `COUNTS.json` holds `stop {step, exit: 2, used, reason: "gate busy"}`, and the digest line
  reads `STOP <step> exit 2` to keep its form. The gate command is split with `shlex.split` (GATE-1 (a)) and its output is
  discarded.
- **Item 2.** A canary retry prints the `STEP` line once (the step's one line); `COUNTS.json` records `retried: true`.
  A brief missing at the audit commit stops that step with the launch script's own code, 10, and runs no child.
- **Item 7.** `COST` names the steps that cost (the launch steps by the counts' `session.cost_usd`, `judge` by its
  `spent <usd> USD` line) and reads `COST not reached` when none ran. `QUESTIONS`, `VERDICT`, `HIT5`, `MISSES` and `POOL`
  come from the `figures` step only, so a stop before it prints their `not reached` forms.
- **Guard.** The engineer's read of `tests/acceptance/W2-172/README.md` was refused by the guard (the role file bars the
  ticket's acceptance folder); the helpers there were not read either. The work follows the Interface alone.
