import pathlib
R = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
p = R / "docs/DECISION_REGISTER.md"; s = p.read_text()
entry = '''### DEC-1083 — D9-FATES decided; K9's memory bar; W2-128's ready check per DEC-1052; W2-131's follow-up a ticket of its own; grid v2 and v3 accepted; h23 traced through the re-anchoring log; a new spill floor proposed
- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`) · **Under:** DEC-1039 (3b), DEC-1052, DEC-1074, DEC-1079, DEC-1081, DEC-1082 · **Source:** `governance/project/orchestration/packages/LIFT-1/D9-FATES.md`, `packages/LIFT-1/D4B-SCORE-ONCE.md`
- **Decision:**
  - **D9-FATES:**
    - (1) The fates are approved in one approval. An independent auditor checks all 792 KPI lines before any edit
      is applied.
    - (2) **K9's memory bar:** 85 % hit@5 on the fresh 80, used once, on the pin that carries W2-92, W2-32's S11,
      W2-131 and the reranker chosen at the decision point. 95 % stays the target. If the bar is missed, S9's
      options come to the owner.
    - (3) W2-32's S6 is dropped as overtaken by the levers; R2-F1 goes to the Wave 3 parking list.
    - (4) W2-15b is out of K9.
    - (5) W2-128 is in K9; the W2-132 split comes when it is reached.
    - (6) W2-99's 13 lines go into W2-128 where they concern templates or briefs; the others are retired. The CTO
      says which.
    - (7) W1-01b, W2-66b and W2-90c close at D-10's green run.
    - (8) The six old repair tickets are retired.
    - (9) W2-42a is the home of DEC-1082 (3)'s guard rule and of G-14's path-map lines.
    - (10) Exit criterion 5: the CTO brings the proposed wording.
  - **W2-128's ready check follows DEC-1052:** missing required fields make a ticket not READY, computed by code;
    only advisory items (est_loc, non_goals) warn. **The `core.bare` tests' half** goes on D-10's red-fix list.
  - **W2-131's follow-up** (`register.leave_out` keeps a narrowed parent's id): a small ticket of its own, tests
    first, in re-pin window 4.
  - **Grid v2** (the reranker given the question) stands, and **grid v3's faithfulness check by ranked outputs** is
    accepted.
  - **h23:** the CTO reads `REANCHOR-LOG-hidden.md` (ids and dates only) before asking the checker, and reports what
    it shows.
  - **The spill floor:** the CTO proposes the new one from today's readings.
- **Basis:** question 1 (memory: one bar on a set used once) and question 2 (a ticket's readiness is computed by
  code, not warned).

'''
i = s.rindex("| Version | Date | Change |")
s = s[:i] + entry + s[i:]
s = s.rstrip("\n") + "\n| 0.467 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1083. Next free id: DEC-1084. |\n"
p.write_text(s)
f = R / "governance/project/orchestration/DECISIONS-IN-FORCE.md"
f.write_text(f.read_text() + '''- DEC-1083 (2026-11-06): D9-FATES approved (the auditor checks the 792 lines before any edit); K9's memory bar 85 %
  hit@5 on the fresh 80 once, on the pin with W2-92, W2-32 S11, W2-131 and the chosen reranker (95 % the target);
  W2-32 S6 dropped; W2-15b out of K9; W2-128 in K9; W2-128's ready check computed by code (only advisory items warn);
  W2-131's follow-up a ticket, tests first; grid v2 and v3 accepted. Basis: 1 and 2.
''')
print("DEC-1083 recorded")
