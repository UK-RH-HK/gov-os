import pathlib
R = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
p = R / "docs/DECISION_REGISTER.md"; s = p.read_text()
entry = '''### DEC-1081 — ACT-PERMISSIONS-1 without the eight `git -C` rules; W2-128 (the templates) filed; two more rerankers measured now (gte-reranker-modernbert-base, zerank-1-small); "score once, combine freely"
- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`) · **Under:** DEC-1080, DEC-1079, DEC-1076, DEC-974 · **Changes:** DEC-1080 (2) (the `git -C` rules), DEC-1079 (a) (the reranker candidates)
- **Decision:**
  - **(1) ACT-PERMISSIONS-1 approved without the eight `git -C` rules** (the CTO uses plain git; the wildcard overlap
    goes with them). The ACT and its rehearsal are revised to that and handed to the operator.
  - **(2) W2-128, the templates ticket, approved: filed** (DEC-974).
  - **(3) Two more rerankers, measured now:** gte-reranker-modernbert-base (149M) and zerank-1-small (1.7B,
    Qwen3-based). Each one's licence, size and input template confirmed; their downloads an ACT for the operator, with
    nothing else installed if possible (a needed package is named).
    - **Score once, combine freely:** each model (the 0.6B, the 4B, gte-modernbert, zerank-1-small) scores every kept
      candidate list of the 138 once, in one quiet GPU window under the safety rules. Then, at no GPU cost and on the
      fixed pipeline (after L3), replays of: each model alone; gte-modernbert for code questions and a Qwen model for
      the rest; cascades (a small or fast model first, a stronger one over its top N); two rerankers in parallel, their
      scores normalised and merged. The grid is declared before the runs; judged by the rule with McNemar; the speed and
      GPU memory of any winning combination measured in a real window before it goes to the owner.
    - At the decision point the best combination goes onto the fresh 80 once, beside the 0.6B. Nothing is adopted or
      installed in the product before the owner decides.
- **Basis:** question 1 (memory: the reranker chosen from every candidate that fits, with its cost beside it) and
  question 4 (scores computed once and combined offline cost the GPU once).

'''
i = s.rindex("| Version | Date | Change |")
s = s[:i] + entry + s[i:]
s = s.rstrip("\n") + "\n| 0.465 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1081; DEC-1080 (2) and DEC-1079 (a) changed. Next free id: DEC-1082. |\n"
for dec, part in (("DEC-1080", "DEC-1081 (1)"), ("DEC-1079", "DEC-1081 (3)")):
    i = s.index(f"### {dec} —"); j = s.index("- **Status:**", i); k = s.index("\n", j)
    s = s[:k] + (f", {part}" if "**Changed by:**" in s[j:k] else f" · **Changed by:** {part}") + s[k:]
p.write_text(s)
f = R / "governance/project/orchestration/DECISIONS-IN-FORCE.md"
f.write_text(f.read_text() + '''- DEC-1081 (2026-11-06): ACT-PERMISSIONS-1 without the `git -C` rules; W2-128 filed; gte-reranker-modernbert-base and
  zerank-1-small measured now (their downloads an ACT): every Qwen3 model and these two score each kept candidate list
  of the 138 once in one quiet window; then replays at no GPU cost on the fixed pipeline (alone; by question type;
  cascades; two merged), the grid declared first, judged with McNemar; a winner's speed and GPU measured for real before
  the owner; the best onto the fresh 80 once. Nothing adopted or installed before the owner decides. Basis: 1 and 4.
''')
print("DEC-1081 recorded")
