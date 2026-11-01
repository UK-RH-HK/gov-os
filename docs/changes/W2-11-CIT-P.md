---
id: W2-11-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-10-31
revised: 2026-11-01
branch: w2/W2-11
base: 4c064bab
ticket: DAEO-k7hz (W2-11), round 1 of two declared rounds (DEC-916), with its resume under DEC-992
author: product-spec (W2-11)
review: a fresh independent reviewer of the combined K3 CIT-P (DEC-954 Q7), with the judgement rules; round 1's review record `docs/probes/DAEO-k7hz/CITP-REVIEW-r1.md` (pass, F1 to F7)
decisions_carried: [DEC-957, DEC-959, DEC-866, DEC-820, DEC-861, DEC-862, DEC-847, DEC-837, DEC-838, DEC-808, DEC-791, DEC-430, DEC-943, DEC-951, DEC-889, DEC-968, DEC-832, DEC-981, DEC-992, DEC-802, DEC-536, DEC-534, DEC-539]
list_rows: [W2-L097, W2-L256, W2-L257, W2-L258, W2-L259, W2-L268, W2-M313, W2-M346, W2-M356]
state_class: EVIDENCE
---

# W2-11: change-impact proposal (CIT-P) on the brief templates and the kernel skills

This round brings the kernel's five brief templates, its orchestration, audit and test-design skills and a new
qa-review skill to the roles specification the owner approved (DEC-957), and to the rules in force since the
supersessions DEC-866 swept. It adds one skill template and gives every kernel skill but adopt and the vendored
skills (§6) a version its generated copy states. It is a kernel change (CAP-33) and one part of the combined K3
CIT-P (DEC-954 Q7): the branch merges only after the owner approves that proposal.

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
| E9 | The opaque acceptance runner has merged: `gov accept` is the engineer's only way to run the acceptance tests, and reads one README-map form | W2-96's KPI lines 3 and 6; DEC-959 items 6 and 7; DEC-820 (c) |
| E10 | Round 1's review: F1 to F6 ride along in the resume, F7 is a row | `CITP-REVIEW-r1.md`; DEC-802; DEC-992 |

Corroboration: the sweep's findings were re-read against the files on this branch's base; each changed rule was
read in the register before it was cited. The README-map form was read from `gov accept`'s map reader as merged.

## 2. The change

| File | What changed, and why | Version |
|---|---|---|
| `templates/brief-engineer.md`, `brief-test-designer.md`, `brief-product-spec.md`, `brief-reviewer.md`, `brief-lead.md` | Record frontmatter (W2-L258); checklist C1 to C12; the twelve-field block, payload after, two-refusal stop, `AUTH_REQUIRED`; Policy 2 with rule (c) per role (DEC-820); the guard's five rules; the decision-record rule (DEC-861, DEC-862); the work order in parallel; the escalation rubric (DEC-957); supersession (DEC-866); the DEC-791 (ii) decisions that apply. Lead: brought to the common brief's role-independent rules, the launch as a command not a code span (W2-L257), `brief_gaps:` (G14). Reviewer: the judgement rules (G15). Resume: the engineer's, the product-spec worker's and the lead's briefs name `gov accept <ticket id>` as the only way an implementer runs the acceptance tests (§2.2) | `<brief version>`, the project's placeholder (none before); not "template 2.0.0", which repair 2 replaced |
| `skills/orchestration/SKILL.md` and four new reference files | The same rules for the method; DEC-791 (ii) decisions with their ids; DEC-430 (W2-L268); loose citations fixed (W2-L256); `briefs-and-returns.md`, `integration-queue.md`, `nightly-sheriff.md`, `incident-response.md`. Resume: F4's formatting and the close step (§2.2) | 1.0.0 → 1.1.0 |
| `skills/audit/SKILL.md` | The judgement rules (G15); the reviewer's part; Policy 2 for reviewers; DEC-430 under the parallel work order; the return | 1.1.0 → 1.2.0 |
| `skills/test-design/SKILL.md`, new `test-kinds.md` | The work order in parallel, red against the base, the black-box techniques, proportion with the measured example, test kinds and their cost, no whole-tree copies, repository-state tests declared, the README map. Resume: the map in exactly the form `gov accept` reads (§2.2) | 1.0.0 → 1.1.0 |
| `skills/qa-review/` (new: `scenarios.md`, then `SKILL.md`) | The QA engineer's method: trace, tests and code against the spec, probes in proportion, findings in the two lines, severity tied to P3/P2/P1, re-runs nothing. Resume: one pointer to where the twelve fields and the two questions stand (§2.2) | new, 1.0.0 |
| `templates/skill.md` (new; its scenarios committed first) | The skill template: front matter, When / not when, Inputs, Steps, Done when, Output and handover, Escalation, Never, Sources; three scenarios first; imports licence-checked | new; unchanged in the resume |
| `roles/orchestrator.md` | DEC-866's sentences only: the lead's statuses, DEC-162's held-out refusal replaced by DEC-820, the checkpoint at every handover. Resume: F2, the lead's return (§2.2) | unchanged (role files carry no version yet) |
| `skills/change`, `checkpoint`, `discovery`, `planning`, `retrieval` | `metadata.version` added, equal to `version`; nothing else (G13) | unchanged: 1.0.0, 1.1.0, 1.0.0, 1.0.0, 1.0.0 |
| `.rulesync/skills/<name>/`, `template/.rulesync/skills/<name>/`, both `subagents/orchestrator.md` | Made to match the kernel: a skill file byte for byte, the role by body | follows the kernel |
| `.claude/skills/<name>/**`, `.claude/agents/orchestrator.md` | Generated by rulesync 24.0.0 from the sources; the CTO's step (§6) | follows the kernel |

Every skill copy carries its version as `metadata.version`: the adapter writes no top-level `version` into a Claude
Code skill, and it keeps the `metadata` block.

### 2.1 Repairs in round 1

**Repair 1 (DEC-537, DEC-539, DEC-541):** the five brief templates and the orchestration skill had dropped
standing sentences of W1-35's delivery that no newer decision supersedes. They are restored word for word from the
base (`4c064bab`) and changed only where a newer decision changes them: DEC-820 (reads open; no listing or search
refusal; the held-out file names readable), DEC-847 (no fixed number of tickets in flight), DEC-837 and DEC-838 (no
lead checkpoint status, no context-limit stop, a checkpoint at every handover), DEC-861 and DEC-862 (decision-record
commits), DEC-959 items 1 and 7 and DEC-968 (the work order in parallel; tests run once per level; the full suite
only in the nightly), CAP-37 (the twelve fields first, so `AUTH_REQUIRED` is the status, not the first line). The
stop's short block cites DEC-537 and DEC-948; DEC-486 covers the closed count only. The escalation rubric's delay
thresholds are the project's placeholders (DEC-539). To keep the skill's body within the validator's 2,500 tokens,
the work order's detail moved to `briefs-and-returns.md`. Test-design states the work order in parallel, red
against the ticket's base, the 2,980 test lines for 713 code lines and the README map in its own body; qa-review
ties severity to P3/P2/P1.

**Repair 2 (`fe21fcb2`; DEC-371, DEC-536, DEC-539, DEC-732, DEC-968):** the lead brief's launch rule names the
launcher and points to the launch command below instead of repeating `gov launch` in a code span (W2-L257); the
settings identity cites DEC-371, not DEC-183; the orchestration skill links `incident-response.md` beside the other
two reference files; the close step's base sentence "a full regression runs (DEC-536)" is restored and read under
DEC-968 as the nightly's run, replacing repair 1's "the regression runs on the merged result (DEC-536): the scoped
set"; the lead brief's code-under-test bullet states the per-command setting as
`<the setting that selects the code under test>=<worktree path>/src` (DEC-732); and the five briefs' `version` became `<brief version>`, the
project's placeholder, because a fixed "2.0.0" was this repository's number in a kernel text (DEC-539).

**Repair 3 (`095167b8`; DEC-534):** the lead brief's code-under-test bullet lost its example for one language
("for a Python project, …"): the setting stays a placeholder, and the kernel names no language or runner.

### 2.2 The resume under DEC-992

The orchestrator's packages P-W2-11-1 to 8 (DEC-992); the review's F1 to F6 ride along (DEC-802).

- **The test designer's three revisions** (merged `7a2baf50`): P-W2-11-7 (A), W2-11's code-under-test case
  accepts the placeholder form, `Rewrite-Reason: DEC-992 (P-W2-11-7), DEC-534` (`bdae4e45`); P-W2-11-6 (a), W1-35's
  record-frontmatter case accepts a brief's own record type, `Rewrite-Reason: W2-L258 (DEC-729, DEC-866)`
  (`668b0ad5`); P-W2-11-8 (a), W1-35's discovery work-order case reads the skill's body only,
  `Rewrite-Reason: DEC-981, DEC-832 item 2` (`38887d51`). With them, the README's KPI map was rewritten as the
  table `gov accept` reads, by the ticket's line numbers, `Rewrite-Reason: DEC-959 item 6` (`647f2f44`). Nothing
  else is lowered.
- **W2-96's KPI 6, the briefs** (DEC-959 items 6 and 7, DEC-820 (c)): `brief-engineer.md` and
  `brief-product-spec.md` name `gov accept <ticket id>` as the only way to run the ticket's acceptance tests; it
  reports pass or fail per KPI line and the counts, never a test's source, assertion text or traceback. Their own
  unit, builder and other suites still run with `<the project's test command>`. `brief-lead.md`'s step 2 tells the
  lead the implementer runs them so. The test-designer and reviewer briefs give an implementer no such
  instruction and are unchanged. The role file names no way an engineer runs the acceptance tests, so it gains
  nothing for this.
- **F2, the role file's lead return** (CAP-37): the summary starts with the twelve labelled fields, the status
  field carrying DONE, PACKAGES, ESCALATION or `AUTH_REQUIRED`, any payload after; `AUTH_REQUIRED` is the status,
  no longer "its first line". Nothing else in the role file changes (W2-33 holds the rest, DEC-981).
- **F4, the orchestration skill:** the Sessions bullet run onto the one before it is split; the next heading gets
  its blank line; "Temp hygiene and protected files" now holds its protected-files rule, Policy 2's bullet (moved
  word for word from Briefs; it is what replaced the base's DEC-508 and DEC-525 refusals there); the close step
  reads "a full regression runs (DEC-536), which since DEC-968 is the next nightly's; a close runs the scoped
  set." Every rule's text survives; the body is 2,500 tokens, the validator's limit.
- **F5, test-design's README map:** the form is exactly the one `gov accept` reads: a table with a KPI column and a
  test or file column whose items are code spans, or a table under a heading that names its line; the line names
  `success-N` / `failure-N` and their accepted spellings; a README with no map refused, a row naming no line
  refused, an unmapped test counted, never named. The tie to "code in progress" is gone; the example names no
  language.
- **The qa-review skill** (RESULTS.md's observations): a session loaded with qa-review alone found neither the
  twelve fields nor the two questions; one input line now says where they stand (the audit skill's "Judgement
  rules"; the orchestration skill's `briefs-and-returns.md`, "The return"). RESULTS.md names no gap in the skill
  template (§4), so it is unchanged.
- **Versions:** orchestration 1.1.0, test-design 1.1.0 and qa-review 1.0.0 are this round's own and unmerged; the
  resume's edits fall inside the same unmerged round and keep them. Before-and-after against the base stand as in
  the table above.
- **The generated copies** under `.claude/` are the CTO's step (DEC-992 P-W2-11-5 (b)): regenerated and committed
  in this worktree, with `Task: DAEO-k7hz`, while no worker runs here.

## 3. Options (DEC-105)

1. **Apply now** (recommended): the rules in force reach every adopted repository's briefs and skills, and the
   launcher can read a skill's version from its copy.
2. **Defer to round 2:** the kernel keeps teaching superseded rules (E1) meanwhile, and W2-60a cannot rely on the
   versions.
3. **Re-baseline:** none; the specification stands (DEC-957).

## 4. Tests

- **Acceptance:** `tests/acceptance/W2-11/` by the independent test designer (632e708b), and W1-35's revised cases,
  with the resume's revisions (§2.2). The KPI map is its README, which the author did not read (DEC-820 (c)); the
  author runs the tests only through `gov accept`, once after its commit, and reports its per-line result in its
  return.
- **The skill validator** (`gov.check.skill_validator --both-layouts`): no finding on the nine kernel skills this
  round touches, nor on the skill template read as a skill.
- **The adapter check** (`gov.adapters.portability`): green once the generated copies are written (§6). Before them,
  it reports exactly the 16 copies this round regenerates as `GENERATED_DIFFERS`, and nothing else.
- **The six scenarios** (qa-review's three, the skill template's three; F6): run on 2026-11-01 as dry runs, each
  by a fresh in-session session that read only the skill or the template under test (not its `scenarios.md`),
  was given the scenario's inputs as fictional facts and wrote nothing; the lead judged each by its pass line, and
  ran the skill validator on the returned texts. All six pass. The deviation from "run on a fresh session": with no
  file written and no commit made, the commit order and "only the report written" were judged from the stated
  order and file list. Observations: qa-review alone did not lead to the twelve fields or the two questions (now
  pointed to, §2.2); the template does not give the skill-import record's form (that record is
  `<the project's skill-import record>`, the project's; no change).
- **Not yet in the template's form:** the revised orchestration, audit and test-design skills were written before
  the skill template and have no `scenarios.md`; bringing them to its sections and scenarios is round 2.

## 5. Impact and rollback

- **Impact:** briefs filled from the templates now carry the twelve fields, Policy 2, the parallel work order and
  `gov accept` as the implementer's only run of the acceptance tests; W1-35's cases that required the old sentences
  were revised by the test designer (DEC-866, DEC-992); a project fills new placeholders (brief version,
  threat-model record, QA findings path, skill-import record, tests-ready marker, per-kind limits). No code changes.
- **Rollback:** revert this round's commits on the integration branch and regenerate the copies; no data or record
  depends on them.

## 6. Not in this round, and outside the paths

- **Round 2** (declared): the orchestration skill split into three (the orchestrator's, the Senior Engineer's, the
  lead's); the Senior Engineer's brief template; the checkpoint skill's stream checkpoint and morning handover
  (G7 to G9); the orchestration, audit and test-design skills in the skill template's form (§4).
- **The vendored skills carry no version** (F3): `superpowers/test-driven-development`, `systematic-debugging` and
  `verification-before-completion`, and the openspec skills, with their copies, state none. Owner: round 2 of
  this ticket, under their vendoring record (DEC-992 P-W2-11-4).
- **The generated copies** (`.claude/`): the CTO generates and commits them (DEC-992 P-W2-11-5 (b)).
- **The validator's refusal of a brief without the twelve-field rule** (a failure KPI line) and row W2-L097, on
  `src/gov/check/skill_validator.py` (DEC-992 P-W2-11-2): the engineer could not be started. `gov launch` refused
  it: `LAUNCH_REFUSED: ticket 'DAEO-k7hz' is a ticket of another role ('product-spec'), not of 'engineer'`. The
  line and the row stay open, returned as a package.
- **The launcher's skill reader** reads a copy's version from `metadata.version`: W2-60a's next round (DEC-992
  P-W2-11-1).
- **DEC-808's schema fields** (`probe.schema.json`, `audit-report.schema.json`): W2-33 (DEC-992 P-W2-11-3).
- **The register's marks:** DEC-430 "Changed by DEC-959 item 7" (the order of writing) and DEC-536 "Changed by
  DEC-968" (the full regression is the nightly's): the orchestrator's.
- **The role file's lead section** still says "tests first" and has `gov launch` in code spans (W2-L257): W2-33.
- **Policy 2 (c) in the briefs** keeps DEC-820's words ("names, results and failure messages"); `gov accept` shows
  less (pass or fail per line and counts). Bringing that bullet to the runner needs DEC-820 (c) marked by DEC-959
  item 6 in the register first: the orchestrator's.
- **The common lead brief** (the project's, not the kernel's) names `gov accept` with W2-96's merge: the
  orchestrator's (W2-96's KPI 6).
- **Still open:** a schema for `type: brief` (the schemas folder and core-schema's map, W2-L258's second half); a
  record type and path for the QA findings report, with the QA engineer's role file (W2-33 r2); F7, the lead
  brief's code-under-test bullet fixing `src/` beside a placeholder (a row).
- **Decided earlier:** the scenario form `scenarios.md` (situation, expected behaviour, pass line); the per-kind
  run-time limits as defaults a project may set otherwise.
- **Rows still open:** W2-L097 (above), W2-L259 (the project prompt), W2-M313 (placeholders filled or checked at
  adoption), W2-M346 (a recorded session), W2-M356 (rules mechanised).
