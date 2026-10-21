
## W1-35 follow-up: the orchestration skill, the ticket lead section and the brief templates (DEC-537, DEC-539, DEC-541, DEC-547, DEC-550; 2026-10-09)

Merged from `w1/W1-35` at `e2797b3b` (54 new cases, 166 in the suite; 675 lines added under `template/`, of
which 127 are the two rulesync copies; the skill is 97 lines, body 2,231 of 2,500 tokens). Delivered:
`template/governance/kernel/skills/orchestration/SKILL.md` (version 1.0.0) with its rulesync source; the
section "The ticket lead" in `template/governance/kernel/roles/orchestrator.md` with its rulesync source;
five brief templates under `template/governance/kernel/templates/` (`brief-test-designer.md`,
`brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md`, `brief-lead.md`); the check
`skill-regression-orchestration`. The skill also states the natural-language route to `gov status --json`
(the half of CAP-28.a moved here from W1-32; the Contract's file names W1-35 as a second provider). Every
row of the orchestrator's report C stands in the skill; none was dropped.

Not covered or not built, by name:

- **Text only.** No case shows a session answering a status question from `gov status --json`, a filled
  brief being followed, or a wave being run this way: each needs a model session and this repository's
  generated `.claude/skills/`. W1-42 runs from the skill and the briefs (its KPI line) and is where this is
  shown.
- **The adapter-portability check at this repository's root has two more findings** (one source missing,
  one source that differs) beside the 43 of DEC-481, until the owner applies the rulesync sources and the
  generated output at the exit (DEC-550). They are in the exit package.
- **Followed by hand, not enforced by a mechanism (Wave 2, DEC-537):** the resource gate, a launch without
  a model, `AUTH_REQUIRED`, leads started through the launcher. The skill says so in its last section.
- **Citations.** Rules that only this repository's orchestrator prompt held are cited with DEC-537. Loose
  citations the lead noticed: "never into the main branch" under DEC-235 and DEC-416; the rule against two
  writing sessions under DEC-254, which records misattributions; "against the last known state" under
  DEC-236 and DEC-449; DEC-183 for identity through the settings argument although DEC-371 superseded it
  for launched roles; DEC-486 for the stop's block although it covers the closed count only.
- **A project's own values are placeholders** (integration branch, ceiling, free memory, model, the CLI's
  path, the decision trailer): nothing fills them or checks that they were filled.
- **The launcher command stands in a code span** in `brief-lead.md` and the role file's lead section; the
  skill validator would flag that inside a skill and does not read templates or role files.
- **The five briefs have no record frontmatter** and no schema; the templates folder's other files do.
- **The orchestrator prompt of this repository is unchanged** and still holds the same rules; from W1-42 on
  the skill and the briefs are the source.
- **Sandbox:** a worker's Write under `.gov-runtime/scratch/` was denied by its permission settings and a
  `mkdir` under `template/.rulesync/skills/` by the guard (it used the Write tool); the containment hook
  twice attributed the test designer's files to the lead's waiting call.
- **Latency under load (DEC-372):** three W1-05 p95 cases failed in the lead's full run at a load of 20 to
  33 and passed alone.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** none; 54 added.
