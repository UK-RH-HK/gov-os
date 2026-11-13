import re
p = "template/governance/kernel/skills/adopt/SKILL.md"
t = open(p, encoding="utf-8").read()
old_w3 = "Wave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, A9 itself, A11 (full audit) and the full verdict.\n"
new_w3 = ("Wave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, the full A9 "
          "(its lite form, the Wave 0 memory practice, is the section below), A11 (full audit) and the full verdict.\n")
assert old_w3 in t
t = t.replace(old_w3, new_w3)
old_src = "## Governing sources\n\nDEC-006, DEC-090, DEC-388, DEC-694, DEC-700, CAP-44, CAP-54.\n"
assert old_src in t
new_sections = """## A9: Wave 0 memory practice

An adopted repository gets its memory built in Wave 0, in the order below (A9 lite). The practice record `docs/research/W2-88-memory-practice.md` holds the methods, the figures and the lessons behind each step.

1. Assess the repository and plan its refactoring for full indexing.
2. Census the stated links (records, front matter, trailers, text) and build the graph from them.
3. Build the store with the standard (Gov OS's memory standard, pinned and written in the A9 record) and its refresh (the store rebuilt after every merge, a failed build leaving the last good store in service). [DEC-1098 (1), DEC-1072 (2)]
4. Have the verdict set and the tuning set written, by independent writers under the rubric, both held outside every worktree. [DEC-1071 (1)-(3), DEC-1074 (4)]
5. Measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points. [DEC-1071 (1)-(3), DEC-1074 (4)]
6. Declare and measure the verdict set once. A miss stands as it is: the set is never run again. [DEC-1071 (1)-(3), DEC-1098 (1)]
7. Record every method and figure, in the adopted repository's copy of the practice record. [DEC-1072 (2)]

## Verify clauses for adopted tickets

A repository adopted by Gov OS brings tickets written before adoption, and the brief of a ticket is refused while a KPI line has no `Verify:` clause. The pass below gives such a ticket its clauses and leaves the ready check as it is. [DEC-1130, DEC-1083]

- The pass runs for a ticket about to launch, not for the whole tracker. [DEC-1130]
- A product-spec session writes the clauses; the tool never writes one. [DEC-1130, DEC-1050]
- Three things check the clauses: the tool, the ticket's test designer and the auditor's sample. [DEC-1130, DEC-1083]
- The owner approves the rule once, not ticket by ticket. [DEC-1130]

The tool is `gov adopt`. Its list option prints, for each open or in-progress ticket that has a KPI line with no verify, the ticket id and the labels of those lines, and the answers file names only the tickets about to launch. Its apply option takes the answers file (YAML, outside the repository: ticket id, then label, then clause) and checks it before it writes anything: every named ticket exists and is not closed, every named label exists, every line still lacking a verify is answered, and each clause is text of its own. It then appends ` Verify: <clause>` to the lines' text, editing the text only (no YAML dump, which would lose comments), and adds the marker `verify_pass: <date> <session>` to the ticket's front matter. [DEC-1130]

## Governing sources

DEC-006, DEC-050, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1130, CAP-44, CAP-54.
"""
new_sections = new_sections.replace("DEC-006, DEC-050, ", "DEC-006, ")
t = t.replace(old_src, new_sections)
open(p, "w", encoding="utf-8").write(t)
