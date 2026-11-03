# The owner's intent (DEC-1052) — read this before building any ticket that points here

**The one question.** Everything is judged on one question: does it help deliver tests and code that match the KPIs
and the spec, with less drift? In order:
1. Does it serve memory, spec-and-KPI development, role separation, or the traffic of tickets?
2. Without it, would ordinary work fail open or lose work (DEC-1010)?
3. Does it run only where the risk is (the change, or the full suite), not everywhere every time?
4. Does it make agents deliver more with less drift, or only add records, approvals and pings?
5. A practice enters the product only after it has proven itself in use, never the same day.

**Templates, not more text.** Every session (research and discovery, product-spec, test designer, engineer, QA and
reviewer, lead, CTO), every ticket and every brief uses the same short templates, read whole and followed: the right
paths, the commands (shipped as scripts), how to report. Stable rules apart from the facts filled in per task. A line
belongs in a template only where it changes what is done. Product-spec writes the templates; the CTO approves them.

**READY and DONE are computed by code, not declared.** As `verdict.py` computes READY from a reviewer's structured
verdict, the tools compute READY and DONE from the filled templates' required fields: the non-goals, how each KPI line
is verified, the definition of done. A missing field refuses READY or DONE; it is never a warning. How well agents read
and follow the templates is measured, and those measures only report.

**Role separation from the path map, deterministically.** Each role's reads and writes are its paths in the path map.
The engineer never reads the acceptance tests. The test designer never reads the engineer's new code (it may read the
integrated code, DEC-963). Simple path checks; no guessing at shell commands. Repeated QA findings mean the spec is
missing something: they go back to product-spec.

**What memory holds.** Memory embeds the WBS, the specs and KPIs, the tickets, the code and the decisions. Tests and
the close, checkpoint and probe records are not embedded: they stay in keyword search, and tickets link to their tests.
