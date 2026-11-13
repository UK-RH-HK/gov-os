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
- tests/acceptance/W2-50/w2_50_support.py  # the merge of integrate: conflict resolution by a test designer (DEC-1157 (12))
- tests/acceptance/W2-58/README.md  # the same
- tests/acceptance/W2-58/test_w2_58_launched_sessions.py  # the same
- tests/acceptance/W2-58/w2_58_support.py  # the same
- tests/unit/launch/test_w2_136_plan_check.py  # older fixtures planting no role file (DEC-1156 (7), P-3)
- tests/unit/launch/test_w2_153_template.py  # the same
- tests/unit/launch/test_w2_56.py  # the same
- tests/acceptance/W2-153/test_w2_153_launch.py  # the same; the appended-file value and line asserts (P-3, P-4 (A))
- tests/acceptance/W2-56/test_w2_56_environment.py  # the same
- tests/acceptance/W2-56/test_w2_56_endings.py  # the same
- tests/acceptance/W2-56/test_w2_56_refused_arguments.py  # the same
kpis:
  success:
  - 'gov launch <role> <ticket> starts the session as its role: the role''s text (its generated agent, or the role file''s text appended) is in the session''s context at its start, shown by a launched session''s log; the launch record holds the role file''s path, version and content hash. Verify: a planted role file and a launch of that role: the session''s first context names the role''s text, and the launch record holds the file''s path, version and sha256 [DEC-826 Q1, lens E F2] [Verify clause added, DEC-1157 (12)]'
  - 'The skills the session can load are in the launch record, each with its name, version and content hash, taken from the copy the session loads; a role file that names its skills gets those, so the engineer''s skill packs load with no code change once W2-33 writes them; a named skill that is missing refuses the launch. Verify: a planted role file naming two skills: the launch record lists each with its name, version and sha256 from the loaded copy; the same file naming a missing skill: the launch is refused naming it [DEC-826 Q1, DEC-832 item 1, lens E F15] [Verify clause added, DEC-1157 (12)]'
  - 'The role''s default model and effort, read from its role file''s `Launch default` line, are applied on the launch line (--model, --effort) and recorded with `model_source` (role default, or after --); a missing or malformed default line refuses the launch; an effort given after -- is applied and recorded as the launch''s own. Verify: a planted role file''s default line is applied and recorded; a missing or malformed line is refused naming the file; an effort after -- is recorded as the launch''s own (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1, 2 and 5, CAP-35.c lite, lens F R1] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; RUBRIC-2''s form moved to W2-184]'
  - 'A model given after -- that is not the role''s is refused, naming both; the subagent model is set to the session''s model (CLAUDE_CODE_SUBAGENT_MODEL in the settings'' env) and recorded. Verify: a model after -- that is not the role''s is refused naming both; the planted launch''s settings carry CLAUDE_CODE_SUBAGENT_MODEL equal to its model, recorded (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1 and 3, lens E F14] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; the trial moved to W2-184]'
  - 'No launch sets a compaction threshold: no --autocompact on the line, no CLAUDE_CODE_AUTO_COMPACT_WINDOW in the settings or the session''s environment, one given after -- refused; the launch record states the threshold as none. Verify: the launch line and settings of a planted launch hold no --autocompact and no CLAUDE_CODE_AUTO_COMPACT_WINDOW; one given after -- is refused; the record says none [DEC-838 items 1 and 2] [Verify clause added, DEC-1157 (12)]'
  - 'A launched session loads no connectors, no user-level agents or skills and no model-side memory: a test home planted with one of each shows none in the session''s start; what the CLI gives no switch for is a package naming it, never passed silently. Verify: a test home planted with one connector, one user-level agent, one user-level skill and model-side memory: a launched session''s start shows none of them [DEC-826 Q5, lens E R6] (folds W2-21 S4) [Verify clause added, DEC-1157 (12)]'
  - 'The arguments the launcher now sets itself are refused after --: --agent, --append-system-prompt and its file form, --session-id. Verify: a launch with each of these after --: each is refused, naming the argument [lens E R6, DEC-826 Q5] [Verify clause added, DEC-1157 (12)]'
  - 'Every launch writes one launch record, keyed by the session id the launcher gives with --session-id, before the session starts: role, ticket, the ticket''s class, model, effort, subagent model, threshold none, the role text''s and each skill''s version and hash, the CLI''s version and the start time; in one folder every worktree of the repository shares, stated in the CIT-E; a record that cannot be written refuses the launch. Verify: a planted launch writes exactly one record under its --session-id holding every field named here, before the session starts; with the record folder unwritable the launch is refused (tests/acceptance/W2-60a/test_w2_60a_launch_record.py) [DEC-826 Q1, CAP-36.a lite, lens F R6] (folds W2-21 S3, its launch record) [restored by P1-W2-60a-P5 (B), DEC-1167; tier, criticality, trial and promotion fields moved to W2-184]'
  - 'Research first, by the lead before the engineer starts: whether a paths:-scoped .claude/rules/ file loads in a headless worker started by gov launch, its token cost, and whether the worker can change it; recorded in docs/research/W2-60-rules-probe.md. Verify: the research record exists and answers the three questions, each with its evidence [lens G Q4] [Verify clause added, DEC-1157 (12)]'
  - 'Routed from W2-33 (its S2, DEC-1156 (3)): the launcher''s plan for a planted ticket prints the model and effort of the role file''s `- **Launch default:**` line (W2-33''s line form). Verify: a planted ticket whose role file says `model claude-sonnet-5-5, effort high`: the plan prints that model and effort; a role file without the line fails the plan naming the file [DEC-954, DEC-957, DEC-1156 (3)]'
  failure:
  - 'A launch that starts with no role text, an unrecorded skill, a model not the role''s, a compaction threshold, a user-level agent, skill or connector, or model-side memory. Verify: S1, S2, S3, S5 and S6''s planted cases: none of these launches starts [Verify clause added, DEC-1157 (12)]'
  - 'A role file without its default line that still launches; a launch with no record, or a record naming another session. Verify: a planted role file without its Launch default line is refused; every planted launch has its record, keyed by its own session id [Verify clause added, DEC-1157 (12)]'
  - 'A refusal the launcher makes today that no longer refuses. Verify: the launcher''s existing refusal cases under tests/unit/launch/ pass unchanged on the branch [Verify clause added, DEC-1157 (12)]'
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

## Interface for run 4's additions (the CTO, at claim, DEC-1157 (3), (12); 2026-11-13 01:25)

- **S12, the launcher's plan (P-2 (A)):** `gov launch --plan <role> <ticket>` prints one line `model <id>, effort <e>` read from the role file's `- **Launch default:**` line (W2-33's line form; with `- **Launch by criticality:**` applied for the ticket's class where the file has it) and exits 0, starting nothing; a role file without the line refuses with `LAUNCH_REFUSED` naming the file (exit 2). About 40 lines and one case.
- **The role text and the template in one appended file (P-4 (A), kept):** the role file's text, one blank line, then the template's bytes; W2-153's value and whole-line asserts are revised to that form (P-3).
- **Older cases (P-3, DEC-1156 (7)):** a test designer plants a role file (and, for W2-60a's own suite, the template and an open gate file) in the fixtures of W2-136, W2-153 and W2-56 listed in the paths, and revises W2-153's appended-file asserts to "the one appended file starts with the role text and ends with the template's bytes"; each with its Rewrite-Reason; no case loses its point.
- **The merge's four acceptance conflicts** (W2-50's and W2-58's files in the paths): resolved by a test designer keeping both sides' cases.
- **S10 moved to W2-184 (CTO, 2026-11-13 15:20, DEC-1157 (12), within P1-W2-60a-P5 (B)):** S10 (the second review on a different setting) entered with DEC-1015 after review 3 and was never built or tested; DEC-1167 (2)'s "back to its DEC-839 form" was the CTO's error for it (it never had one). W2-184 carries RUBRIC-2's review-setting line in its place.
