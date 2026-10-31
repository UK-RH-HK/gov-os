---
id: W2-11-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-10-31
branch: w2/W2-11
base: 4c064bab
ticket: DAEO-k7hz (W2-11), round 1 of two declared rounds (DEC-916)
author: product-spec (W2-11)
review: a fresh independent reviewer of the combined K3 CIT-P (DEC-954 Q7), with the judgement rules
decisions_carried: [DEC-957, DEC-959, DEC-866, DEC-820, DEC-861, DEC-862, DEC-847, DEC-837, DEC-838, DEC-808, DEC-791, DEC-430, DEC-943, DEC-951, DEC-889, DEC-968, DEC-832, DEC-981]
list_rows: [W2-L097, W2-L256, W2-L257, W2-L258, W2-L259, W2-L268, W2-M313, W2-M346, W2-M356]
state_class: EVIDENCE
---

# W2-11: change-impact proposal (CIT-P) on the brief templates and the kernel skills

This round brings the kernel's five brief templates, its orchestration, audit and test-design skills and a new
qa-review skill to the roles specification the owner approved (DEC-957), and to the rules in force since the
supersessions DEC-866 swept. It adds one skill template and gives every kernel skill but adopt a version its
generated copy states. It is a kernel change (CAP-33) and one part of the combined K3 CIT-P (DEC-954 Q7): the
branch merges only after the owner approves that proposal.

## 1. Evidence

| # | Evidence | Source |
|---|---|---|
| E1 | Templates, skill and role file still teach superseded rules: the lead's checkpoint status and context-limit stop, listing refusals over the governance folder, the held-out list's names refused, a fixed number of tickets in flight, owner commits | SWEEP-2026-10-20 §4; DEC-866; DEC-837, DEC-838, DEC-820, DEC-847, DEC-861 |
| E2 | No return rule in the briefs: the twelve fields, the payload after, the two-refusal stop | AR-5, AR-6; CAP-37.d |
| E3 | The work order changed: test designer and implementer in parallel from the spec; tests run once per level | DEC-959 items 1 and 7 (its Swept line), DEC-963, DEC-968 |
| E4 | G13: no generated skill copy carries a version | roles specification §6.1 (DEC-957); DEC-832 item 2; DEC-981 |
| E5 | G14: the kernel lead brief lags the common lead brief and has no `brief_gaps:` | DEC-943 item 1 |
| E6 | G15: the judgement rules are not in the kernel | DEC-801, DEC-808 (row W2-M377) |
| E7 | The skill template and qa-review; test-design's proportion, kinds and cost; orchestration's three reference files | DEC-959 items 3 and 5; DEC-951 item 5; DEC-889 item 11 c |
| E8 | The list rows taken in | W2-L097, W2-L256 to W2-L259, W2-L268, W2-M313, W2-M346, W2-M356 |

Corroboration: the sweep's findings were re-read against the files on this branch's base; each changed rule was
read in the register before it was cited.

## 2. The change

| File | What changed, and why | Version |
|---|---|---|
| `templates/brief-engineer.md`, `brief-test-designer.md`, `brief-product-spec.md`, `brief-reviewer.md`, `brief-lead.md` | Record frontmatter (W2-L258); checklist C1 to C12; the twelve-field block, payload after, two-refusal stop, `AUTH_REQUIRED`; Policy 2 with rule (c) per role (DEC-820); the guard's five rules; the decision-record rule (DEC-861, DEC-862); the work order in parallel; the escalation rubric (DEC-957); supersession (DEC-866); the DEC-791 (ii) decisions that apply. Lead: brought to the common brief's role-independent rules, the launch as a command not a code span (W2-L257), `brief_gaps:` (G14). Reviewer: the judgement rules (G15) | template 2.0.0 (none before) |
| `skills/orchestration/SKILL.md` and four new reference files | The same rules for the method; DEC-791 (ii) decisions with their ids; DEC-430 (W2-L268); loose citations fixed (W2-L256); `briefs-and-returns.md`, `integration-queue.md`, `nightly-sheriff.md`, `incident-response.md` | 1.0.0 → 1.1.0 |
| `skills/audit/SKILL.md` | The judgement rules (G15); the reviewer's part; Policy 2 for reviewers; DEC-430 under the parallel work order; the return | 1.1.0 → 1.2.0 |
| `skills/test-design/SKILL.md`, new `test-kinds.md` | The work order in parallel, red against the base, the black-box techniques, proportion with the measured example, test kinds and their cost, no whole-tree copies, repository-state tests declared, the README map in the acceptance runner's form | 1.0.0 → 1.1.0 |
| `skills/qa-review/` (new: `scenarios.md`, then `SKILL.md`) | The QA engineer's method: trace, tests and code against the spec, probes in proportion, findings in the two lines, severity tied to P3/P2/P1, re-runs nothing | new, 1.0.0 |
| `templates/skill.md` (new; its scenarios committed first) | The skill template: front matter, When / not when, Inputs, Steps, Done when, Output and handover, Escalation, Never, Sources; three scenarios first; imports licence-checked | new |
| `roles/orchestrator.md` | DEC-866's sentences only: the lead's statuses, DEC-162's held-out refusal replaced by DEC-820, the checkpoint at every handover | unchanged (role files carry no version yet) |
| `skills/change`, `checkpoint`, `discovery`, `planning`, `retrieval` | `metadata.version` added, equal to `version`; nothing else (G13) | unchanged: 1.0.0, 1.1.0, 1.0.0, 1.0.0, 1.0.0 |
| `.rulesync/skills/<name>/`, `template/.rulesync/skills/<name>/`, both `subagents/orchestrator.md` | Made to match the kernel: a skill file byte for byte, the role by body | follows the kernel |
| `.claude/skills/<name>/**`, `.claude/agents/orchestrator.md` | Generated by rulesync 24.0.0 from the sources; not yet written (§6) | follows the kernel |

Every skill copy carries its version as `metadata.version`: the adapter writes no top-level `version` into a Claude
Code skill, and it keeps the `metadata` block.

## 3. Options (DEC-105)

1. **Apply now** (recommended): the rules in force reach every adopted repository's briefs and skills, and the
   launcher can read a skill's version from its copy.
2. **Defer to round 2:** the kernel keeps teaching superseded rules (E1) meanwhile, and W2-60a cannot rely on the
   versions.
3. **Re-baseline:** none; the specification stands (DEC-957).

## 4. Tests

- **Acceptance:** `tests/acceptance/W2-11/` by the independent test designer (632e708b), and W1-35's revised cases.
  The KPI map is its README, which the author did not read (DEC-820 (c)); the author's one run after this commit is
  reported in its return.
- **The skill validator** (`gov.check.skill_validator --both-layouts`): no finding on the nine kernel skills this
  round touches, nor on the skill template read as a skill.
- **The adapter check** (`gov.adapters.portability`): green once the generated copies are written (§6). Before them,
  it reports exactly the 16 copies this round regenerates as `GENERATED_DIFFERS`, and nothing else.

## 5. Impact and rollback

- **Impact:** briefs filled from the templates now carry the twelve fields, Policy 2 and the parallel work order;
  W1-35's cases that required the old sentences were revised by the test designer (DEC-866); a project fills new
  placeholders (threat-model record, QA findings path, skill-import record, tests-ready marker, per-kind limits).
  No code changes.
- **Rollback:** revert this round's commits on the integration branch and regenerate the copies; no data or record
  depends on them.

## 6. Not in this round, and outside the paths

- **Round 2** (declared): the orchestration skill split into three (the orchestrator's, the Senior Engineer's, the
  lead's); the Senior Engineer's brief template; the checkpoint skill's stream checkpoint and morning handover
  (G7 to G9).
- **The generated copies** could not be written by the author's session (`.claude/` is read-only to it): the lead
  regenerates and copies the 16 files of §4.
- **The launcher's skill reader** (another ticket) must read a copy's version from `metadata.version`.
- **The role file's lead section** still says "tests first" and has `gov launch` in code spans (W2-L257): W2-33.
- **P-1:** mark DEC-430 "Changed by DEC-959 item 7" for the order of writing.
- **P-2:** add `probe.schema.json` and `audit-report.schema.json` to W2-11's paths (the card's DEC-808 line), or move
  W2-M377's schema half to W2-33.
- **P-3:** the validator's refusal of a brief without the twelve fields, and W2-L097, need `src/gov/check/skill_validator.py`.
- **P-4:** a schema for `type: brief` needs the schemas folder and core-schema's map (W2-L258's second half).
- **P-5:** the scenario form `scenarios.md` (situation, expected behaviour, pass line), for the skill harness (decided).
- **P-6:** a record type and path for the QA findings report, with the QA engineer's role file (W2-33 r2).
- **P-7:** the per-kind run-time limits are defaults a project may set otherwise (decided).
- **Rows still open:** W2-L259 (the project prompt), W2-M313 (placeholders filled or checked at adoption), W2-M346
  (a recorded session), W2-M356 (rules mechanised).
