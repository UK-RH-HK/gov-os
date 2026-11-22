# Research brief: integration step two, every decision since DEC-1209 held by code or by text, and the three rubrics (DEC-1238 (6))

Role: **research** (Sonnet). Read-only; you write only `docs/emergency-2/integration/DECISIONS-HELD.md` and commit nothing.
Repositories: Gov OS `/home/usain/Dynamic-Agentic-Engineering-OS` (`w2/integrate`), EXAMIN
`/home/usain/gov-os-runs/W2-27/examin` (read only; its register and decisions DEC-001 on). Never open `~/examin-eval/**` or
`~/gov-os-eval/**`. Memory first (`gov retrieve`, whole bundle, once more in your own words). **Bounded reading:** start
from audits 1 and 4 (they already mark most decisions); read code only to confirm; at most three short Sonnet helpers.

**Read first:** `docs/emergency-2/GOLDEN-WORKFLOW.md` rules 6, 7 and 8; DEC-1238; `docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md`
(every decision DEC-1209 to DEC-1231 and EXAMIN's DEC-001 to DEC-005, carrier by carrier); audit 4
(`E2-AUDIT-4-DETERMINISM.md`) §1.7 (the standing rules and their class) and §2 (List A ids). Then DEC-1232 to DEC-1238 in
`docs/DECISION_REGISTER.md` and EXAMIN's register from DEC-006 on (audits 1 and 4 did not see them).

## Output: `docs/emergency-2/integration/DECISIONS-HELD.md`
1. **One row per decision** (Gov OS DEC-1209 to DEC-1238, item by item where items differ; EXAMIN DEC-001 on): id and item;
   what it requires in one line; held by: **code on the path** (path:line) / **code off the path** (inside `gov queue`,
   `gov launch`, `gov brief`, not used by Gov OS today) / **checked after** (auto or typed) / **text only** (where the text
   lives) / **not built** / **history** (spent, nothing to hold); in flight (branch or brief: `e2/models-rubric`,
   `LEAD-fixes-015a.md`, `e2/d1-verdict`, `e2/w2-207-runtime`); the List A id or the fix that would hold it by code.
   Counts by class at the end.
2. **The three rubrics**, each in its own section:
   - **The ticket rubric** (feature / fix / chore, golden rule 6; DEC-1219 (5)-(6), EMERGENCY-2 §4): where it is in code
     today (`gov launch --fix/--chore`, the queue's fix landing, `NEW_TICKET_NOT_FEATURE`, the patch rule's P1/P3), what
     still rests on text, and what makes it enforced on the path (e.g. the queue writes the fix record, `--direct` for
     chores, `ticket.schema.json` requires `class`), with size and when (0.1.5 in flight / integration).
   - **The model and effort rubric by criticality** (golden rule 7; DEC-1225, DEC-1236 (2)-(3); `governance/project/criticality.yaml`,
     `.claude/hooks/agent_model.py`, `src/gov/launch/`, the role files): what holds it today, what `e2/models-rubric` and
     `fixes-015a` F13 and F14 add, what is left (e.g. the CTO's own start script, effort for every role in one table, a
     change to a model or effort refused unless it names the owner's decision).
   - **The escalation rubric** (golden rule 8; `docs/emergency-2/T2-ESCALATION-RUBRIC.md`; the decisions-by-page feature,
     `docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md`): today, is the level of a decision computed by code from its
     record anywhere, is a decision below its level refused anywhere, is the judgement kept in a fixed form; then the
     design that makes it enforced on the path: the record's fields that set the level (touches a spec / KPI / Contract /
     standing decision; reversible; inside a worktree; paid or secret), the code that computes P1/P2/P3/emergency, where
     the refusal sits (the decision-record commit's basis check; the queue for a ticket that changes a spec), and how it
     joins the decisions page; size; when.
3. **Spec questions** found (DEC-1238 (10)): one decision record each (question; what was found; options with costs;
   recommendation; sources), and whether it stops work.

## Return (your final message, short)
The path; the counts by class (Gov OS and EXAMIN apart); for each rubric, held today / after 0.1.5 / what is left in one
line each; the spec questions (stoppers named).
