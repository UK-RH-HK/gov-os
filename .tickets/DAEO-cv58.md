---
id: DAEO-cv58
status: in_progress
deps: []
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: engineer
external-ref: W2-60a
tags: [wave-2, implementation, full, launch, roles, keystone-3]
wbs_id: W2-60a
title: 'The role, its skills and its model and effort loaded at launch; the launch record'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/launch/launcher.py
- src/gov/launch/role.py
- src/gov/launch/record.py
- src/gov/launch/criticality.py
- governance/project/criticality.yaml
- tests/unit/launch/test_role*
- tests/unit/launch/test_launch_record*
- tests/unit/launch/test_runs.py
- tests/unit/launch/test_w1_28.py
- tests/unit/launch/test_w1_32.py
- docs/changes/W2-60a-CIT-E.md
- docs/research/W2-60-rules-probe.md
kpis:
  success:
  - 'gov launch <role> <ticket> starts the session as its role: the role''s text (its generated agent, or the role file''s text appended) is in the session''s context at its start, shown by a launched session''s log; the launch record holds the role file''s path, version and content hash [DEC-826 Q1, lens E F2]'
  - 'The skills the session can load are in the launch record, each with its name, version and content hash, taken from the copy the session loads; a role file that names its skills gets those, so the engineer''s skill packs load with no code change once W2-33 writes them; a named skill that is missing refuses the launch [DEC-826 Q1, DEC-832 item 1, lens E F15]'
  - 'The session''s model and effort are RUBRIC-2''s for its role and criticality: read from the role file''s `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket''s criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket''s `class`, which is its kind); applied on the launch line (--model, --effort) and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses the launch; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3), CAP-35.c lite, lens F R1] (folds W2-21 S4) [changed, DEC-1120 (5), DEC-1126 (3)]'
  - 'A model after -- that is not the resolved tier''s is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session''s tier model (CLAUDE_CODE_SUBAGENT_MODEL in the settings'' env), as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after -- with no trial: refused naming both [DEC-1120 (3), lens E F14] (folds W2-21 S4) [changed, DEC-1120 (5), DEC-1126 (3)]'
  - 'No launch sets a compaction threshold: no --autocompact on the line, no CLAUDE_CODE_AUTO_COMPACT_WINDOW in the settings or the session''s environment, one given after -- refused; the launch record states the threshold as none [DEC-838 items 1 and 2]'
  - 'A launched session loads no connectors, no user-level agents or skills and no model-side memory: a test home planted with one of each shows none in the session''s start; what the CLI gives no switch for is a package naming it, never passed silently [DEC-826 Q5, lens E R6] (folds W2-21 S4)'
  - 'The arguments the launcher now sets itself are refused after --: --agent, --append-system-prompt and its file form, --session-id [lens E R6, DEC-826 Q5]'
  - 'Every launch writes one launch record, keyed by the session id the launcher gives with --session-id, before the session starts: role, ticket, the ticket''s class, model, effort, subagent model, threshold none, the role text''s and each skill''s version and hash, the CLI''s version and the start time, and `tier`, `criticality`, `model_source`, the trial id and the promotion reason (each null when not given); in one folder every worktree of the repository shares, stated in the CIT-E; a record that cannot be written refuses the launch [DEC-826 Q1, CAP-36.a lite, lens F R6, DEC-1120 (3)] (folds W2-21 S3, its launch record) [changed, DEC-1120 (5), DEC-1126 (3)]'
  - 'Research first, by the lead before the engineer starts: whether a paths:-scoped .claude/rules/ file loads in a headless worker started by gov launch, its token cost, and whether the worker can change it; recorded in docs/research/W2-60-rules-probe.md [lens G Q4]'
  - 'On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [changed, DEC-1120 (5), DEC-1126 (3)]'
  - 'A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table''s effort, recorded as `promotion` with the reason and the record''s path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [changed, DEC-1120 (5), DEC-1126 (3)]'
  failure:
  - A launch that starts with no role text, an unrecorded skill, a model not the role's, a compaction threshold, a user-level agent, skill or connector, or model-side memory.
  - A role file without its default line that still launches; a launch with no record, or a record naming another session.
  - A refusal the launcher makes today that no longer refuses.
  - A model below its tier with no trial; a promotion not applied; an effort below the floor. [changed, DEC-1120 (5), DEC-1126 (3)]
profile: FULL
sources:
- DEC-826
- DEC-838
- DEC-839
- DEC-832
- DEC-801
- DEC-786
- DEC-941
- CAP-35.c
- CAP-36.a
- DEC-1014
- DEC-1015
- DEC-1119
- DEC-1120
- DEC-1126
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-60a/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: []
---
# W2-60a The role, its skills and its model and effort loaded at launch; the launch record

Card: the draft card `W2-60` (W2-60a part), from the accepted plan (`docs/plan/WAVE_2_REVISED_PLAN.md` §4.3, §2 row 5 and the CAP-35.c and CAP-36.a lite rows; DEC-826 Q1 and Q5, DEC-838, DEC-839); keystone 3, agents know what to do. Started now by the re-plan the owner accepted on 2026-10-29 (DEC-941), beside the memory work.

- **Why:** a launched session loads none of its role's text (lens E F2). No launch sets effort, and the compaction threshold was a user-level value (lens F F1). The model a subagent runs on is not the one recorded (lens E F14), and the loaded skill copy has no version (lens E F15). Until this lands, the prompt's launch forms carry the values by hand (prompt v3 §6, DEC-839 item 5).
- **Profile FULL (the plan said STANDARD):** this ticket rewrites the CLI line and the settings that carry the sandbox. It also keeps connectors out, and connectors run outside the sandbox with network. A mistake here fails open in ordinary work (DEC-801).
- **Place:** starts as soon as filed (DEC-941), stacked on `w2/integrate` (DEC-786), where W2-58's launcher is merged (`af5d1a25`). It runs beside W2-56 on `launcher.py`: each keeps its work in modules of its own and touches `launcher.py` at its call sites and argument checks only, and the second to merge merges the first back first. W2-05 (`DAEO-0z8c`) holds `src/gov/**/*.py` for git-environment lines only, so those lines are left alone. W2-21 follows. W2-60b follows it.
- **Merges after the role files carry their default line** (model and effort, no threshold), which W2-33's widening writes through CIT-P (DEC-839 item 5). It is built and tested against fixture role files until then.
- **Paths:** `launcher.py` for the CLI line, the settings' env lines it sets, its argument checks and the calls only. The probe record is the lead's. The role files, generated agents and skills are not in the paths (W2-11, W2-33).
- **The test designer's files** (MR-3): `tests/acceptance/W2-60a/**`.
