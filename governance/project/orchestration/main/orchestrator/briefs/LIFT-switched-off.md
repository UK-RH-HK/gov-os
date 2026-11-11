# Every control switched off in the emergency, and the set-up B sweep (DEC-1128 (1), (4))

Read `LIFT-common.md` first (scratch only, read-only everywhere else; run no test suite). Role: research helper,
Sonnet high, class C1 (DEC-1120). Scratch folder:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/switched-off/`.
Read DEC-1128 in `docs/DECISION_REGISTER.md` first, word for word.

## Part 1: the list (DEC-1128 (1))
One list of **every guard rule, gate and check switched off, lifted, relaxed, deselected, made a warning, or
bypassed during the emergency** (from about DEC-1030, 11-01, to now; check earlier if a record says so). Search the
register (DEC-1030 onward: "lifted", "switched off", "off", "warning", "suspended", "deferred", "bypass", "opt-in",
"known red", "freeze", "emergency", "until"), DECIDED-NOT-DONE, DECISIONS-IN-FORCE, `packages/` (EMERGENCY-TOOLS-1,
D10-*, D4-LIST, LIFT-1/*, P1-PLAN, the ACT packages), `governance/project/path-map.yaml` (its comments and lists),
`governance/project/test-map.yaml`, `tests/conftest.py` (opt-in groups such as `lifted`, `breadth`), the nightly
(`governance/project/orchestration/nightly/`), `.claude/settings.json` hooks, the guard (`.claude/hooks/`,
`src/gov/guard/`) for rules marked off or not wired, `gov check`'s config (findings ruled warnings, e.g.
product-traceability-trailers), the close's gates (W2-115, `known reds`, `load_sensitive`, `acceptance_exemptions`),
the dispatcher's and slots' lifted rules (`dispatch/config.json`, DEC-1052 O-A1 "the slots rule lifted"). Also the
other direction: a guard rule made live in the emergency without set-up A's 100 % (W2-141's rule, live from the
re-pin at 13:31 UTC today; the guard fixes ACT-GUARD-FIX-1 to 4, G14, G14b, INDEP-WALLS-1): under DEC-1128 (2) these
are "new guard rules"; list them in their own section with the evidence they went live on.

For each, one row: the control (what it checks, where it lives); what was done to it (off, lifted, warning, narrowed,
exempted), when, and by which decision or ACT (id, commit); why; its home ticket (DAEO id and W2 id) or "none";
what must be true before it returns: for a guard rule, **set-up A's evidence against the 100 % bar on the path map's
actions** (find set-up A's records: DEC-1112, DEC-1113, `packages/` SANDBOX-GUARD / SETUP-A*, its briefs and results;
say what set-up A has measured so far and what it has not); for a gate or check, the ticket's acceptance or the
decision named; and **when** after the lift (from FORECAST-W2-3 and the plan: `gov plan --open`, the ticket's batch).
Mark the controls with no home ticket and no return condition: those are the drift.

## Part 2: the set-up B sweep (DEC-1128 (4), DEC-866)
Every place that still plans set-up B, sandboxed leads, or "sandbox work" beyond the workers' existing launcher
sandbox: tickets (`.tickets/`, by id and by words: set-up B, sandbox experiment, SANDBOX-GUARD, EXP-002, W2-40),
DECIDED-NOT-DONE rows (25, 28, 29, 48 and any other), packages, briefs (`governance/project/briefs/`,
`governance/project/prompts/w2-orchestrator.md`), the Wave 3 parking list. A list only: path, line, what it says,
the change DEC-1128 (4) implies (retire, re-word, or keep with a reason); never edit.

## Write
`SWITCHED-OFF-1.md` in your folder: §1 the controls switched off (table), §2 guard rules made live in the emergency
(table), §3 the drift (no home, no condition), §4 set-up A's state against the 100 % bar, §5 the set-up B sweep. Plain
language for the owner. Return the twelve fields, short. Estimate 1.5 h.
