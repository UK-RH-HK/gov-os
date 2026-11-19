# Lead brief: L2's A6 and A8 (the queue's --dry-run, --select, --full; the after-step); fixes and lines after W2-202

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it (and
`LEAD-COMMON.md`: add `-n auto` to slot runs of more than one file). Branch `e2/l2-build-2` from `w2/integrate`,
worktree `/home/usain/gov-os-worktrees/E2-l2-build-2`. **C3** (the landing, `src/gov/queue/**`, `src/gov/close/**`):
the test designer and the engineer run Claude Fable 5.2 (`model: "fable"`). `Class: F`.

**Where things stand:** W2-202 (L2's A1, A3, A4, A5) landed and closed tonight (merge 2b54f3d1a, ticket
`.tickets/DAEO-l2bd.md`: read its record and its lead's risks). **Read** `docs/emergency-2/L2-COMMANDS.md` §2 and §3,
items A6 and A8 (their files, KPI lines and verifies).

**Build A6 and A8 as the page gives them**, as a new ticket (a new KPI line on a closed feature is a new ticket, §4.6):
write `.tickets/` with `wbs_id: W2-206`, status in_progress, the page's S and F lines as its KPI lines.
- **A6:** `gov queue --dry-run` (steps 0 to 5, nothing moved or committed, `--out` and the `.exit` file so `gov wait`
  works), `--select` (the selection as one JSON object), `--full` (the nightly's own run on the tested merge, landing
  only on green). For `--full`: the full run is sized by the product's slot (W2-199, landed tonight in
  `src/gov/resources/slots.py` and `src/gov/dispatch/admission.py`); it must not start pools wider than its slot's CPUs
  (the owner, DEC-1216 (5): every run inside the gate, the full suite included, fewer workers rather than a peak).
- **A8:** after a move, `gov rebuild --integration <branch>` where `rebuild.yaml` names a store, and `gov check
  --structural <base>`, both as notices in `queue.json`, never changing the exit code or the landed branch.
- **Also, from W2-202's risks (fixes in W2-202's record, the failing test first):** `src/gov/queue/acceptance.py`
  replaces `runner.read_cases` at run time to keep the JUnit report: give `gov.accept.runner.accept` a small
  `keep_report` parameter instead; an acceptance run that fails without naming a failing test names its ticket as the
  culprit, not `BATCH_UNEXPLAINED` for the whole batch.

**Not tonight:** A2 (one close record, one writer: it waits for the M1 lead's `e2/m1-context`, which changes the close
record), A7 (`--direct`: the owner answers L2-6 in the morning), every B item (the owner's yes). Keep out of
`src/gov/close/command.py`'s record writing (M1's) and `src/gov/dispatch/**` (the run-time lead's).
**Flow:** test designer (Fable) writes `tests/acceptance/W2-206/`, red on the base; engineer (Fable) builds until `gov
accept W2-206` is green; then `tests/unit/queue`, `tests/unit/close`, `tests/unit/accept`, `tests/acceptance/W2-115`,
`W2-115b`, `W2-193`, `W2-194`, `W2-202`, with node on the PATH (`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`).
