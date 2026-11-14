# Commits of 2026-11-13 whose trailers git does not read (P1-LANDING-72C6 (a))

Twelve commits by the CTO (session f3886235), 17:32 to 20:07 UTC, carry their `Task:`, `Role:`, `Implements:` and
`Decided-by:` lines in the body's second-to-last paragraph: a blank line separates them from `Co-Authored-By:` and
`Claude-Session:`, and git reads trailers only from the last paragraph. The lines are in each body as written; this
record gives each commit's intended trailers, for the tools that read trailers (the landing check, `gov links`, the
traceability checks). History is not amended (DEC-412). From 20:15 every CTO commit carries all its trailers in one
final paragraph, checked after each commit with `git log -1 --format='%(trailers:key=Task,valueonly)'`.

| Commit | Branch | Intended trailers | Subject |
|---|---|---|---|
| 5a2f5223c | w2/integrate | Task: DAEO-sdxk; Role: orchestrator | P1-W2-88-NC-1: the package for W2-88's run 6 |
| f7ab50ac0 | w2/integrate | Task: DAEO-cv58; Role: orchestrator | W2-60a: P-8 (a), the older launch suites' fixtures in the paths |
| 579f889f4 | w2/integrate | Task: decision-record; Role: orchestrator; Decided-by: owner (chat, 2026-11-13) | DEC-1172 |
| 730477098 | w2/integrate | Task: DAEO-6n5k; Role: orchestrator | W2-37: P-7 (a)'s paths and _CBM_SUITES's conftest line |
| bdcf7af73 | w2/integrate | Task: DAEO-drhj; Role: orchestrator | W2-104: Verify clauses for S1-S4 and F1-F3 |
| 0d08622f0 | w2/integrate | Task: DAEO-t8mp, DAEO-p3ln, DAEO-zi7s; Role: orchestrator; Implements: DEC-953, DEC-1132 | W2-128, W2-136, W2-147 closed |
| 713fcf744 | w2/W2-104 (lands with W2-104) | Task: DAEO-drhj; Role: orchestrator; Implements: DEC-1157 | W2-104: the lead's role template |
| 8801ffd17 | w2/integrate | Task: DAEO-f58b; Role: orchestrator | W2-116: S2's interface stated; widened |
| 5b6ed1b49 | w2/integrate | Task: DAEO-h4rh; Role: orchestrator | W2-27: depends_on loses the five cut tickets |
| 73569aafd | w2/integrate | Task: decision-record; Role: orchestrator; Decided-by: owner (chat, 2026-11-13) | DEC-1173 |
| 0ee2de2d9 | w2/W2-37 (merged by 72c6def88) | Task: DAEO-6n5k; Role: orchestrator | W2-37: its independent review records committed |
| 72c6def88 | w2/integrate | Task: DAEO-6n5k; Role: orchestrator; Implements: DEC-1166, DEC-812 | Merge w2/W2-37 (the landing check's P1) |

**72c6def88 and the landing check's P1.** The merge touched a kernel control path
(`template/governance/kernel/skills/change/SKILL.md`). The landing check read it as outside a ticket because its
`Task:` line was not parsed. The change is W2-37's: the owner approved its bytes (`cdf43a49…`) by DEC-1166 (4); the
kernel gate passed on them; the tree equals git's own merge of its parents. The owner accepted the item as recorded by
P1-LANDING-72C6 (a).
