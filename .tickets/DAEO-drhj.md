---
id: DAEO-drhj
status: in_progress
deps: []
links: []
created: 2026-10-30T23:20:54Z
type: task
priority: 1
assignee: engineer
external-ref: W2-104
tags: [wave-2, implementation, skills, standard]
wbs_id: W2-104
title: 'The skill evaluation harness: each skill''s three scenarios run on a fresh session and recorded, and every imported skill''s licence check recorded before adoption'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- docs/probes/DAEO-drhj/**  # the probe record (run 3's narrow check)
- src/gov/skilleval/**
- tests/unit/skilleval/test_w2_104*
- governance/project/skill-imports.yaml
- src/gov/check/commands.py
kpis:
  success:
  - 'gov skilleval <skill> runs each of the skill''s three committed scenarios on a fresh session with only that skill loaded (the model and effort from the role defaults), judges each against its stated pass line, and writes a scenario record (skill version, scenario, verdict, cost, time) beside the skill; it is the evidence CIT-E reads [DEC-959 item 5, ROLES-RESEARCH-1 §5.3 item 13] Verify: with a stub model in a temporary project, each of a planted skill''s three scenarios runs in a new session folder holding only that skill, with -p, --model and --effort from the role defaults, is judged by a separate process against its pass line, and appends a record with the skill version, scenario, verdict, cost and time beside the skill; a skill that cannot be evaluated ends 5 with nothing run or recorded (tests/acceptance/W2-104/, the README''s Success 1 row)'
  - 'An imported skill (Anthropic''s collection or another source) is adopted only when governance/project/skill-imports.yaml records its source, version, licence and the licence''s verdict for this use, and its three scenarios pass; the harness refuses to mark an import adopted otherwise [DEC-959 item 5] Verify: --adopt with a full allowing record and three passes marks it adopted and leaves other entries unchanged; each gap in the record, no entry, no record file, or fewer than three passes ends 6 with adopted false (tests/acceptance/W2-104/, the README''s Success 2 row)'
  - 'A scenario run that cannot reach a model (no network, no key) is recorded as not run with its cause, never as a pass; the harness reads no secret and prints none [DEC-959 item 5, DEC-820 (a)] Verify: a session that exits non-zero, prints no JSON or reports is_error, a judgement that exits non-zero, no claude on the PATH and a session past --timeout are each recorded not run with a one-line cause and no cost (tests/acceptance/W2-104/, the README''s Success 3 row)'
  - 'Planted skills with a passing and a failing scenario give the expected verdicts, in a temporary project, with a stub model [DEC-959 item 5] Verify: a passing planted skill gives three passes; a FAIL and an unanswered judgement give fail; the last verdict line of the judgement decides and the session''s own verdict line is not read (tests/acceptance/W2-104/, the README''s Success 4 row)'
  failure:
  - 'A scenario reported as passing that did not run, or failed. Verify: every not-run case (the stub''s judgement would say PASS if asked) and every failed case (FAIL, no verdict, PASS then FAIL, a session that says PASS itself) is never recorded pass (tests/acceptance/W2-104/, the README''s F1 row)'
  - 'An import marked adopted with no licence record or a failing scenario. Verify: each of the 7 licence-record gaps, no entry, no record file and each of the 3 not-three-passes variants starts adopted true and ends adopted false (tests/acceptance/W2-104/, the README''s F2 row)'
  - 'A secret read or printed. Verify: two planted values (the environment''s ANTHROPIC_API_KEY and the project''s .env) never appear in gov''s output or records, when the stub prints them on stderr, as non-JSON stdout or in an is_error reply, on a passing run, and with the .env unreadable (tests/acceptance/W2-104/, the README''s F3 row)'
profile: STANDARD
sources:
- DEC-959
- DEC-820
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-104/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-959 item 7); planted skills and a stub model, no network
track: B
list_rows: []
---
# W2-104 The skill evaluation harness

Card: ROLES-RESEARCH-1 §5.3 item 13, approved (DEC-959 items 5 and 8): with or just after W2-11 r1, so the template's scenarios have a runner.

- **Paths:** a new command module `src/gov/skilleval/` (`gov skilleval`), and the import record `governance/project/skill-imports.yaml` (new). No overlap.
- **Re-listed (CTO, 2026-11-13):** run 3 parked by the emergency's freeze on 11-02 and never re-listed; now run 3 merges integrate (W1-07, W1-32 and commands.py conflicts), builds the two gitleaks literals from parts, a narrow check, the land.
