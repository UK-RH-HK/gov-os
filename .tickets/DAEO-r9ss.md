---
id: DAEO-r9ss
status: open
deps: [DAEO-g0ip, DAEO-zflj, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-07
tags: [wave-2, implementation, standard, close, keystone-1]
wbs_id: W2-07
title: gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-zflj
- DAEO-7rr2
allowed_paths:
- src/gov/close/**
- src/gov/telemetry/**
- tests/unit/close/**
- tests/unit/telemetry/**
kpis:
  success:
  - 'gov close judges a ticket by its class [W2-H045]: an implementation ticket on its acceptance tests; a specification ticket on its closed readiness record and its acceptance tests; an audit ticket on its report and the audit validator; a research ticket on its evidence record; an integration or coordination ticket on its named evidence files'
  - 'A test-revision ticket is judged on the acceptance tests its ticket file names in acceptance_tests.path (another ticket''s folder), not on a folder of its own [DEC-892, DEC-896 item 3]'
  - 'A decision-record commit that changes only governance records (the register, the plan files, the prompts, the briefs, governance/project/orchestration/, the path map) and names an ACCEPTED decision counts as measured for the work-without-a-task gate; a decision-record commit that names no ACCEPTED decision, or changes code, tests or the kernel, still counts as unmeasured [DEC-896 item 1]'
  - 'The commit gates run first, before any test: the trailers, work without a task, accepted history, the probe gate (a stale probe named before the run, W2-M403), and the ratchet''s own reading of both lists'' entries (an entry the ratchet would not count is named); when one refuses, the close stops at once, names its cause and spends no ratchet attempt [DEC-868 item 3, DEC-896 item 3, P-IS-4 (a), I2 F13, I4 F14, F17]'
  - 'The pre-close gate inside gov close: it collects every suite it will run, in one process, as it runs them; it runs gov check with no commit since the rebuild; and it checks that the ticket''s checkpoint is fresh. Any failure refuses at once, before any test runs [DEC-868]'
  - 'Before its regression, gov close reads the shared disk''s free space and free inodes (W2-20''s reading once it lands; until then the floors 100 GiB and 10,000,000 inodes from the configuration) and refuses below either floor, naming the reading [DEC-898]'
  - 'The probe gate accepts a failed probe record whose every finding is named, with its row, in an ACCEPTED owner decision that names the record and its probed commit; any finding not so named still refuses [W2-M371, DEC-790]'
  - A refused close writes a complete repair ticket (role, allowed paths, KPIs) that stays tracked in .tickets/ [F-m8, W2-L209, W2-L236, AR-9].
  - The close record carries the measured governance share [W2-M166, W2-M286].
  - Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal reuses its repair ticket [W2-H038, W2-M249, W2-M252].
  - An interrupted close leaves nothing that blocks the next close [W2-M158].
  - 'The cases this ticket turns red are revised by its test designer, each with a Rewrite-Reason: W1-30''s test_w1_30_no_acceptance_tests.py (3 functions, 6 cases) and test_collection_error_refuses_close; its engineer revises the unit test_a_collection_error_is_a_finding [I2 F9]'
  failure:
  - A research ticket without an evidence record closes; an audit ticket whose report fails the validator closes.
  - A collection error, a RED gov check, a stale checkpoint, a stale probe, an unmeasured commit, a ratchet entry the ratchet would not count, or a disk below the floor refused only after the regression.
  - A decision-record commit outside an ACCEPTED decision counted as measured.
profile: STANDARD
sources:
- DEC-729
- DEC-738
- DEC-790
- DEC-868
- DEC-892
- DEC-896
- DEC-898
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-07/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-9 (claims)
- F-m8
- W2-H045
list_rows:
- W2-H038
- W2-H045
- W2-L107
- W2-L108
- W2-L123
- W2-L124
- W2-L165
- W2-L196
- W2-L197
- W2-L208
- W2-L209
- W2-L210
- W2-L236
- W2-M149
- W2-M157
- W2-M158
- W2-M166
- W2-M178
- W2-M248
- W2-M249
- W2-M252
- W2-M263
- W2-M276
- W2-M286
- W2-M348
- W2-M349
- W2-M354
- W2-M403
---
# W2-07 gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-07), as approved (DEC-729), with DEC-868, DEC-892, DEC-896 item 3, DEC-898 and lens I's P-IS-4.

- **Place (DEC-896 item 3):** it comes forward to sit with W2-66, before the first re-pin, and rides in it.
  - It shares `src/gov/close/command.py` with W2-66: W2-66 writes the record's evidence lines, W2-07 the gates.
  - **The merge order (owner, DEC-899 item 2):** the two are built in parallel, and **W2-07 merges first.** Then W2-66 merges `w2/integrate` back, re-verifies and gets a fresh FULL probe before the re-pin.
- **Allowed paths:** `src/gov/close/**`, except W2-66's and W2-68's new modules (`select.py`, `nightly.py`, `evidence.py`, `batch.py`, `fingerprint.py`). Also `src/gov/telemetry/**`, `tests/unit/close/**` and `tests/unit/telemetry/**`, and, for its test designer only, the W1-30 cases named above.
- **It unblocks** the test-revision tickets: W2-63, W2-67's revisions and W2-70 close on its class once it is pinned.
- **Row W2-M263 (DEC-738 item 4):** RED stays when nothing comes after the base (DEC-479; W1-30's test); this ticket owns how the close reports it.
- **The test designer's files (MR-3: named here, never in the implementer's `allowed_paths`; DEC-899):** `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py`, `tests/acceptance/W1-30/test_w1_30_collection*`. Each change carries a `Rewrite-Reason:`; no expectation is lowered.
