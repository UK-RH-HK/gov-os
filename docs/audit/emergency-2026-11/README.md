# The emergency's audits and research (DEC-1209, 2026-11-16)

The one location for every audit and research report of the owner's emergency. Path map: `docs/audit/**`
(`governance/project/path-map.yaml:54`); the guard lets every independent auditor and reviewer write here
(`REVIEW_PATHS`, `.claude/hooks/pretooluse.py:81`); the CTO commits each report as it lands. Read-only audits; nothing is
lifted before the owner decides (DEC-1209 (7)).

| Report | What | State |
|---|---|---|
| `retro-P1-usage.md` | Part 1: where the work and the usage went (4,922 sessions, 33.0 B tokens) | landed 17:1x |
| `retro-P2-lifecycle.md`, `retro-P2-perticket.csv` | Part 2: the ticket lifecycle per profile; exa-g6db worked example | landed 17:1x |
| `retro-P3-lifts.md` | Part 3: what DEC-1047/DEC-1050 lifted, what crept back | landed 17:1x |
| `retro-P4-ceremony.md` | Part 4: ceremony against value, 95 rows judged | landed 17:1x |
| `retro-P5-memory-use.md` | Part 5: memory in use (the memory-in-use audit) | landed 17:2x |
| `retro-SHORT-LIST.md` | The combined short list (15 rows) and part 6's two answers, with the measures | landed 17:3x |
| `rubric-research.md` | The rubric research and design (DEC-1209 (4)) | running |
| `permissions-audit.md` | The permissions audit (the owner, 17:3x) | running |

Each report was written by a fresh, independent, read-only session; the CTO copied in those the guard refused to let
their authors write under `drafts/` (the CTO's briefing error, corrected: briefs now name this folder).
