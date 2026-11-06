import pathlib
R = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
p = R / "docs/DECISION_REGISTER.md"; s = p.read_text()
entry = '''### DEC-1084 — D9-FATES §5 decided and the fates applied; exit criterion 5 re-worded; the spill floor 2,048 MiB; the measure re-anchors in memory (a W2-61h line); ACT-GUARD-SETS-1 decided; L5 and an 80-candidate cell measured; the bundle's figures asked
- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`) · **Under:** DEC-1083, DEC-1082 (3), DEC-1081 (3), DEC-1079 · **Source:** `governance/project/orchestration/packages/LIFT-1/D9-FATES.md` (v2.1), `packages/ACT-GUARD-SETS-1.md`, `packages/LIFT-1/D4B-SCORE-ONCE.md` · **Changes:** DEC-1083 (7) (W2-66b and W2-90c)
- **Decision:**
  - **D9-FATES §5:**
    - (1) W2-111 stays open as a LITE test revision outside K9.
    - (2) W2-55's S1 is re-worded as proposed ("the decisions validator checks domain, status and scope, and names
      each entry without them (`TAG_MISSING`)"), and W2-55 closes formally.
    - (3) W2-66b is a red-fix item in D-10. W2-90c stays open as its own ticket, its named run after W2-105 and
      W2-110 merge.
    - **The fates are applied now.**
  - **Exit criterion 5 is approved as worded:** AR-1 to AR-10, each shown once, in order, in the Wave 2 exit run's
    record (W2-46), and audited in the exit audit (W2-47). The AR lines whose tickets moved to Wave 3 are named as
    Wave 3 in W2-46's record (DEC-953, DEC-954, W-8).
  - **The spill floor:** 2,048 MiB, set by the CTO and re-read in a week.
  - **The measure's anchoring: a W2-61h line, tests first.** The measure re-anchors a set's labels in memory for the
    commit it measures and never rewrites the sets root.
  - **ACT-GUARD-SETS-1:**
    - (1) yes: six refused roles, and `transcripts/**`;
    - (2) (a): applied right after re-pin window 4. Before that, the CTO's hidden-set tools take the sets root as an
      argument and open the files in their own code, printing ids and counts only;
    - (3) diagnostics on spent sets run outside the guard, by the owner's checker or operator, with no exception in
      the code;
    - (4) the live worktrees with measured roles get the merge the same day.
  - **After the grid:**
    - L5 (phrasing and the term map) is measured on the 138, by the rule;
    - one more cell: the 0.6B reranking 80 candidates instead of 40, scored in a short window, to show whether a
      wider pool helps or hurts.
  - **A question, figures only, from the kept runs, with no GPU.** For the 0.6B and the 4B on the 138:
    - hit@5, hit@10 and "in the bundle", side by side, per set;
    - the first call's bundle size in tokens (median and p90);
    - what a full top 10 would cost, if it is not already sent.

    Nothing is decided on the bar until the owner sees them.
- **Basis:** question 1 (memory: the bar judged on what agents receive) and question 2 (the hidden halves refused to
  every measured role).

'''
i = s.rindex("| Version | Date | Change |")
s = s[:i] + entry + s[i:]
s = s.rstrip("\n") + "\n| 0.468 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1084; DEC-1083 (7) changed. Next free id: DEC-1085. |\n"
i = s.index("### DEC-1083 —"); j = s.index("- **Status:**", i); k = s.index("\n", j)
s = s[:k] + (", DEC-1084 (W2-66b, W2-90c)" if "**Changed by:**" in s[j:k] else " · **Changed by:** DEC-1084 (W2-66b, W2-90c)") + s[k:]
p.write_text(s)
f = R / "governance/project/orchestration/DECISIONS-IN-FORCE.md"
f.write_text(f.read_text() + '''- DEC-1084 (2026-11-06): D9-FATES §5 decided (W2-111 open, LITE, outside K9; W2-55 S1 re-worded and closed; W2-66b a
  D-10 red-fix item; W2-90c its own ticket) and the fates applied; exit criterion 5 re-worded; spill floor 2,048 MiB;
  the measure re-anchors in memory (W2-61h, tests first); ACT-GUARD-SETS-1 decided (after window 4; the CTO's tools
  take the sets root first); L5 and an 80-candidate 0.6B cell measured. Basis: 1 and 2.
''')
print("DEC-1084 recorded")
