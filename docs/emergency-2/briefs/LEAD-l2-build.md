# Lead brief: L2's A items that need no yes: A1, A3, A4, A5 (the landing becomes the close; fixes in W2-115b's record)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
Branch `e2/l2-build` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-l2-build`. **C3** (the landing, the
merge queue, `src/gov/close/**`, `src/gov/queue/**`): the test designer and engineer run Claude Fable 5.2
(`model: "fable"`). `Task: DAEO-j9z6` (W2-115b), `Class: F`.

**Decided (DEC-1214 L2 and Q-CLOSE):** the landing and the close are one deterministic action; the landing records a red
that is red at the base as a known base red and does not block. **Read** `docs/emergency-2/L2-COMMANDS.md` §2 and §3 A
(the items, their files, KPI lines and verifies), audit 1, W2-115b's ticket `.tickets/DAEO-j9z6.md`.

**Build A1, A3, A4 and A5 as the page gives them** (A1: base reds recorded, not refused, in `close/batch.py` `isolate`
and `queue/command.py`; A3: acceptance at the landing; A4: a branch already merged; A5: the settings and `gov pause`).
Add their KPI lines to W2-115b's ticket file in your branch (a new KPI line on a closed feature is a new ticket, 4.6: if
W2-115b is closed, open `.tickets/` W2-202 for these lines instead). **Not tonight:** A2 (one close record, one
writer: it waits for the M1 lead's change to the close record, `e2/m1-context`), A6 to A8, and every B item (the
owner's yes). Keep out of `src/gov/close/command.py`'s record writing (M1's) and `src/gov/dispatch/**` (slice 2's).
**Flow:** test designer (Fable) writes the failing cases under `tests/acceptance/W2-115b/` (or W2-202), red on the base;
engineer (Fable) builds until `gov accept` is green; then `tests/unit/queue`, `tests/unit/close`, `tests/acceptance/W2-115`,
`W2-193`, `W2-194`, `W2-115b`.
