---
task: DAEO-kmcr
decisions_applied: [DEC-954, DEC-1052, DEC-1112]
---
# W2-23 run 3 (resume -> build -> review): FULL review round 1 NOT READY on S3

Head w2/W2-23 fd1bc056f5ba (verified: gov accept 22/22; W1-41 3/3; lead_verify 4013 tests, 6 red, all W2-96 signal
cases in tests/unit/accept, environment-dependent). Review rev-1 (Opus high, session bb401577, 2.07 USD), record
`log/rev-1.result.md`: S1, S2, S4, S5, S6, S7, F1 pass; **S3 fails** on R1 and R2 (in scope, ordinary work yes, fails
open). The lead reproduced both at the head (`r1r2.py`): `citations('The old store is legacy/memory.',
['legacy/memory/decisions/leg-001.md'], [])` -> `[]`; `'See ../decisions/leg-001.md.'` -> `[]` (found with a following
comma); `'The store moved from .claude/memory/ to here'` against `.claude/memory/2025/a.md`, `.claude/memory/2026/b.md`
-> `[]`.

## P-W2-23-7: the fix round for R1 and R2, and R2's reading of "the store's folder" (Interface item 6)
- (a) Round 2 on S3 only. First td-4 (Sonnet, about 0.5 USD) adds S3 cases from the described behaviours: a folder
  citation and a `../` tail citation each at the end of a sentence (`.`), and a store whose files all sit in subfolders
  cited by the folder that holds them all. Then eng-4 (Sonnet, about 0.5 USD) changes `safety.citations`
  (`src/gov/adopt/safety.py:287-291`): the folder and tail lookaheads accept a trailing sentence stop, as the glob form
  already does (7a74947a6); the folder form covers the store's own folder (the deepest folder holding all its files)
  and each folder between it and a file. Then merge, accept, verify, and review round 2 on S3 (Opus, about 2 USD; the
  last round, DEC-1010). Cost about 3 USD and about 1.5 h. **Recommended.**
- (b) R2 read as "each file's own parent folder" (as built): R2 becomes a row; the round fixes R1 only. Cost about
  the same; leaves stores laid out in subfolders open to a wrong A8 pass.
- (c) Land as is, R1 and R2 as rows. This decides a FAIL away, which the lead may not do; it is the CTO's or owner's call.
  Cost: A8 can retire a store that is still cited (it can be recovered from the archive ref).
Recommendation: (a). Confidence: high for R1, medium-high for R2's reading. Blocks: the probe record and the landing.

## Triage of every finding
| id | KPI | where | scope / ordinary / consequence | triage |
|---|---|---|---|---|
| R1 | S3 | safety.py:287, :291 | in / yes / fails open | fix, P-W2-23-7 (reproduced) |
| R2 | S3 | safety.py:289 | in / yes / fails open | fix, P-W2-23-7 (reproduced; the reading is the CTO's) |
| R3 | S3 | safety.py:302 | in / no / fails open | row: leading-wildcard and brace globs skipped on purpose (imported rules carry `**/*`) |
| R4 | S2 | merge.py:97, :117 | in / yes / other | row: CRLF written back as LF, JSON re-indented; every line, key and order kept |
| R5 | S2 | merge.py:127-129 | out / yes / other | row: other generated files are not refreshed on a second run |
| R6 | S4 | stages.py:295 (a4) | in / yes / other | row: the A4 plan still names the shared ref `rollback/batch-<n>`; a4 is outside P-W2-23-1's call sites |
| R7 | S1 | legacy.py:98, :251, :262 | in / no / loses work | row: an ignored file at an A8 import target is overwritten, and deleted if the stage fails |
| R8 | S1 | stages.py:406 | in / no / loses work | row: a concurrent write to a planned target mid-run is deleted by the restore |
| R9 | S4 | safety.py:213-217 | in / no / other | row: a kill inside one `git mv` is refused, not resumed |
