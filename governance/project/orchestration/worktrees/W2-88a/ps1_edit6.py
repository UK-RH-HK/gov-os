p = "docs/research/W2-88-memory-practice.md"
t = open(p, encoding="utf-8").read()
start = t.index("## 6. For an adopted repository's Wave 0 (the practice in order)\n")
end = t.index("## 7. What changed on 2026-11-06")
new = """## 6. For an adopted repository's Wave 0 (the practice in order)
The adopt skill's A9 step (`template/governance/kernel/skills/adopt/SKILL.md`) states these seven steps in this order.
1. Assess the repository and plan its refactoring for full indexing (W2-88's KPIs).
2. Census its stated links (records, front matter, trailers, text) and build the graph from them.
3. Build the store with the standard and its refresh: chunk by meaning (sections, answer units, code by definition), give
   every reader the heading path, serve it with Gov OS's memory standard, and rebuild it after every merge (§7).
4. Have the verdict set and the tuning set written, by independent writers under the rubric. Keep the hidden check and the
   verdict set outside every tree.
5. Measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points on
   sets of about 80 (DEC-1074 (4)). Diagnose by stage and by structure.
6. Declare and measure the verdict set once.
7. Record every method and figure here, or in the repository's copy of this record.

Note: the models (reranker, embedder) are chosen on all three sets, with speed and GPU figures, after the structure is
fixed; the standard of step 3 names the choice Gov OS made (DEC-1098).

"""
t = t[:start] + new + t[end:]
open(p, "w", encoding="utf-8").write(t)
