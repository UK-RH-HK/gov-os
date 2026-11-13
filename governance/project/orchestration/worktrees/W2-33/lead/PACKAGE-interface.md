# W2-33 (DAEO-lrre) run 1: interface package (DEC-1052), before the pair starts

task: DAEO-lrre · decisions_applied: DEC-1052, DEC-957 (Q2, Q3, Q10), DEC-1087 (13), DEC-1120 (2)

## Question
The ticket does not state the interface its tests and its product-spec worker must share, and five verify
clauses need code outside its allowed paths. State the interface and route those clauses before the pair starts?

## Gaps found (read 2026-11-12 ~21:35)
1. Line forms not stated. S4/S5 want "the same sentence" in every role file, S6 four statements, S3 the per-stream rule,
   but no line head or wording is given, so a test designer and a writer working apart cannot meet.
   S2/S7 forms are given only in part: W2-60a's reader (w2/W2-60a `src/gov/launch/role.py:35-40`) reads
   `- **Launch default:** model <claude-…>, effort <low|medium|high|xhigh|max>` and `- **Skills:** a, b`; S7's own
   form is `Launch default: model <m>, effort <e>` with `<m>` "Opus"/"Sonnet" (not a model id) and no line form for
   `Launch by criticality:`.
2. CTO and Senior Engineer. S2 ("the CTO's and the Senior Engineer's files give effort high") and S7 ("senior engineer
   Opus high") name a Senior Engineer file, but the line that creates it is still under `moved:` (to Wave 3, DEC-1083),
   although DEC-1087 (13) reversed that move. The roles folder has no `senior-engineer.md`.
3. S2 "the launcher's plan for a planted ticket prints the file's model and effort": W2-60a's launcher (DAEO-cv58,
   in_progress, last commit 2026-11-01) is not on w2/integrate; and by DEC-957 Q10 W2-60a merges after W2-33,
   so W2-33 cannot wait for it.
4. S3 "a planted write elsewhere is refused by the guard": `qa-engineer` is not in KNOWN_ROLES
   (`src/gov/guard/decide.py:18`); that change is W2-60b's own KPI line (DAEO-ecac line 36; open, deps W2-60a).
5. S5 "a planted launch of two writing sessions into one worktree is refused by the launcher, naming the worktree":
   no such check in `src/gov/launch/` or `src/gov/dispatch/`, and no ticket holds it (grep of .tickets/).
6. S7 "the generated agents carry the same lines" and F1 "the generation check names it as drifted": `.claude/agents/**`
   is outside the paths (DEC-315, DEC-1112 (3)); the generation and byte check is W2-153's (DAEO-8s85, in_progress).
7. S6 "a planted review brief ... yields a returned verdict": a live model run, not a deterministic acceptance test.
8. CIT-P (CAP-33): kernel role files go to the owner before merge; no CIT-P path (`docs/changes/…`) is in the paths.

## Options
- **A (recommended).** The CTO amends the ticket (a P2: scope and KPIs within the approved spec, DEC-957) with:
  - Files: new `roles/ticket-lead.md` (ROLES-SPEC-1 §3.3, DEC-957 Q2) and `roles/qa-engineer.md`; no
    `independent-reviewer.md`; `orchestrator.md` loses the heading `## The ticket lead` and is the CTO's file (id kept).
  - Line form (ROLES-SPEC-1 §5.1, Q3; W2-60a's reader), each line once and whole:
    `- **Version:** x.y.z` · `- **Launch default:** model claude-opus-5-5|claude-sonnet-5-5, effort high` ·
    `- **Launch by criticality:** C3 model <id>, effort <e>; C2 …; C1 …; C0 …` (only where RUBRIC-2 varies; QA's C2 written
    `C2 model claude-opus-5-5, effort high on FULL, model claude-sonnet-5-5, effort high otherwise`) ·
    `- **Skills:** a, b` · `- **Model tier:** see Launch default` (kept, names the line).
  - `- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in
    parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are ready,
    through gov accept; the QA engineer alone reads both.` (word for word in every file)
  - `- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works in
    its own tests worktree, merged by the lead.` (word for word in every file)
  - QA engineer lines: `- **Per stream:**`, `- **Moderator:**`, `- **Wave 3 row:**`, `- **Verdict:**` (per KPI),
    `- **Rounds:**` (at most two), with the KPI's wording.
  - Senior Engineer: its clauses in S2 and S7 hold only for a `senior-engineer.md` that exists; the file itself stays
    with the moved line (or the CTO restores that line under DEC-1087 (13): a separate P2, est. +60 lines).
  - Clauses outside the paths move to their owners' tickets, the role-file statement kept here:
    S2's launcher plan → W2-60a; S3's guard refusal → W2-60b (already its line 36); S5's launcher refusal → added to
    W2-60b (or W2-60a); S7's generated copies and F1's drift → W2-153's generation check after the copies ACT.
  - S6's planted brief: the reviewer runs it as a probe and the probe record carries the verdict.
  - Paths: add `docs/changes/W2-33-CIT-P.md` (or the CTO names the combined K3 CIT-P path).
  Cost: one ticket edit by the CTO (~20 min) and two small KPI additions to W2-60b; then the pair starts as run 1 (est.
  260 lines unchanged). Blocks nothing else.
- **B.** Keep the ticket; the test designer writes tests for the out-of-path clauses that stay red until W2-60a,
  W2-60b and W2-153 land. Cost: W2-33 cannot close (W2-60a waits on W2-33, Q10: a cycle); S5 has no owner and stays red.
- **C.** Defer W2-33 to after the layers' plan (DEC-1087 (13)). Cost: W2-60a stays unmergeable (Q10); RUBRIC-2 stays
  out of the product's role files.

## Recommendation
A. Confidence: medium-high (the line forms and the routing are from ROLES-SPEC-1 and the tickets as read; the
Senior Engineer scope is the CTO's call: medium).

## What it blocks
W2-33's test design and implementation (both need the same line forms); through Q10, W2-60a's merge.
