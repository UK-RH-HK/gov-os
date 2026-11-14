---
id: DAEO-6f0s
wbs_id: W2-184
external-ref: W2-184
title: "RUBRIC-2 at launch: criticality from criticality.yaml, the Launch by criticality line, the effort floor, trials, the second review's setting, promotion (from W2-60a)"
type: task
class: implementation
role: engineer
profile: FULL
status: closed
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-13
deps: [DAEO-cv58]
allowed_paths:
- src/gov/launch/launcher.py
- src/gov/launch/role.py
- src/gov/launch/record.py
- src/gov/launch/criticality.py
- governance/project/criticality.yaml
- tests/unit/launch/test_w2_184_*.py
- docs/changes/W2-184-CIT-E.md
- docs/probes/DAEO-6f0s/**  # the probe record
- src/gov/launch/command.py
reads:
- .tickets/DAEO-cv58.md
- governance/project/orchestration/packages/P1-W2-60a-P5.md
- governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md
- template/governance/kernel/roles/**
needs: []
waits_on: []
kpis:
  success:
  - 'The session''s model and effort are RUBRIC-2''s for its role and criticality: read from the role file''s `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket''s criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket''s `class`, which is its kind); applied on the launch line (--model, --effort) and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses the launch; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3), CAP-35.c lite, lens F R1] (folds W2-21 S4) [from W2-60a S3, DEC-1167]'
  - 'A model after -- that is not the resolved tier''s is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session''s tier model (CLAUDE_CODE_SUBAGENT_MODEL in the settings'' env), as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after -- with no trial: refused naming both [DEC-1120 (3), lens E F14] (folds W2-21 S4) [from W2-60a S4, DEC-1167]'
  - 'The launch record also holds `tier`, `criticality`, `model_source` (role default, by criticality, after --, trial, promotion), the trial id and the promotion reason, each null when not given. Verify: a planted launch by criticality, one with a trial and one promoted each record their fields; a plain launch records them null [DEC-1120 (3)] [from W2-60a S8, DEC-1167]'
  - 'On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [from W2-60a S10, DEC-1167]'
  - 'A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table''s effort, recorded as `promotion` with the reason and the record''s path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [from W2-60a S11, DEC-1167]'
  - 'R1 (F1, 2026-11-14): a lead launch (`gov launch orchestrator <ticket>`) given `--reason`, `--trial` or `--owner-named` is refused with exit 2 and a message saying a lead takes none of them; nothing starts and no record is written; a lead launch without them is unchanged [rv-f1 F1, interface 7.1/7.2a, DEC-1180 (4)] Verify: the `test_r1_*` cases in tests/unit/launch/ pass (each option alone and together refused for a lead; the worker cases unchanged)'
  - 'R2 (F2, 2026-11-14): a launch record is written atomically: its bytes go to a temporary file in the same folder that no reader takes as a record, then it is linked or renamed to its final name without overwriting; a launch killed at any point leaves either no record or a whole one under the final name; the reader still refuses a final-name record that is not JSON [rv-f1 F2, DEC-1180 (4)] Verify: the `test_r2_*` cases pass (a write interrupted after the create and before the bytes leaves no final-name file; a leftover temporary file does not refuse a launch; a planted non-JSON final-name record still refuses, naming it; two writers of the same name: one wins, the other is refused as today)'
  - 'R3 (F3, 2026-11-14): the same probe-record path found under more than one root with different contents is read from every root, and a promotion any copy shows applies; identical copies count once [rv-f1 F3, P-td5-2 revised, DEC-1180 (4)] Verify: the `test_r3_*` cases pass (a stale launch-root copy without the fail-open finding and a newer ticket-branch copy with it: promoted; two identical copies: counted once); `test_f1_a_path_under_both_roots_is_read_from_the_launch_root_s_copy` is revised to this rule by the test designer'
  failure:
  - 'A model below its tier with no trial; a promotion not applied; an effort below the floor. Verify: S3 and S4''s planted cases: a model below its tier with no trial is refused; a promotion is recorded and applied; an effort below high for a judgement role is refused [from W2-60a F4, DEC-1167]'
non_goals:
- 'not W2-60a''s reviewed core (role text, skills, the record''s base fields, no compaction, the refused arguments): W2-60a lands it first'
- 'not a gate for W2-27 (EXAMIN''s copy): launches during the copy use each role''s `Launch default` line (P1-W2-60a-P5 (B), DEC-1167)'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1180, DEC-1167, DEC-1126, DEC-1120, DEC-1119, DEC-839, DEC-1010, CAP-35.c, DEC-1014, DEC-1015, DAEO-cv58]
acceptance_tests: {path: tests/acceptance/W2-184/}
---

# W2-184 RUBRIC-2 at launch (from W2-60a)

The owner's P1-W2-60a-P5 (B) (DEC-1167): RUBRIC-2's lines, added to W2-60a by DEC-1126 (3) after its three review
rounds and never built, move here, so W2-60a lands its reviewed core and EXAMIN's copy runs on each role's
`Launch default` line. The interface is the CTO's at claim, from W2-60a run 4d's proposal (`log/W2-60a-A5-run4d.json`):
`criticality.yaml` and `ticket_criticality(root, ticket)`, the `Launch by criticality` line with its "on FULL ... otherwise"
form, the effort floor and `--reason`, `--trial` reading `governance/project/trials/<id>.yaml`, promotion from the probe
records, S10 counting the auditor's launch records with `--owner-named <DEC-id>`. Starts after W2-60a merges; its own
review rounds (new scope).

**The CTO, 2026-11-14:** P-W2-184-2 (a), `src/gov/launch/command.py` added (the interface at claim puts `--trial`, `--reason` and `--owner-named` before `--`). P-W2-184-3 confirmed: 1.4 (no `criticality.yaml`: a launch behaves as before W2-184, DEC-1167 (2)); 3.2a (a max after `--` equal to the resolved effort needs no `--reason`); `probe` as a sixth `model_source`/`effort_source`; the lead's matching rule. P-W2-184-1 (round 2's F1) is the owner's (DEC-1010).

**The owner, 2026-11-14 (chat, ~11:40): P-W2-184-1 (a), with (c) as the stop-gap until it lands (DEC-1010; round 2's F1).** (a): `_probe_files` (`src/gov/launch/launcher.py`) also reads `docs/probes/<id>/` under each worktree root that the ticket's launch records name, so a test designer launched from its tests worktree sees the ticket's probe records; a root that no longer exists is skipped. (c): until (a) lands, a lead brings the ticket branch's probe-record commit into its tests branch before it launches a test designer. The fix is followed by a narrow independent check of that change only (DEC-1154).

**Reopened 2026-11-14 by the CTO (DEC-1180 (4): a defect spotted is fixed in the same flow; DEC-1157 (12), within the ticket's purpose; listed for the owner's reading): R1-R3 for the narrow check's F1-F3** (`docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`, landed at d79c8c939). F1: a lead launch drops the three options silently (`command.py:41-45`, `launcher.py:938-950`). F2: `record.write` (`record.py:91-110`) creates then writes, so a killed launch leaves an empty record that refuses every worker launch (`launcher.py:494-500`). F3: a stale launch-root copy of a probe record wins over a newer copy elsewhere (`launcher.py:521-534`; fails open in that case). Order: a fresh test designer (R1-R3 as described behaviour, the one F3 case revised with `Rewrite-Reason: DEC-1180 (4), rv-f1 F3`), a fresh engineer, gov accept, a narrow independent check of this change only (DEC-1156 (7)).
