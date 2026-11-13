Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: engineer, DAEO-emq1 (W2-115), FULL, class C3 — five acceptance reds after the fix round (run 4, eng-6, red iteration 1)

Budget: projection 6 USD. Keep your context short: read only what each red needs; cut long outputs to head and tail.

You are a fresh engineer for ticket DAEO-emq1 (W2-115), in `/home/usain/gov-os-worktrees/W2-115` on `w2/W2-115`
(DEC-963), head d8db5bb6f. Step 0 (the sandbox check), every standing rule, the writes (the ticket's `allowed_paths:`
only), the never-read rule for `tests/acceptance/W2-115/**`, the Interface, the commands, the commit form and the
return are those of the first engineer's brief, copied beside this one:
`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/eng-1.md` (read it whole), and the lead's answers in
`eng-2.md` beside it (binding). Do step 0 first and report it first. `gov accept` crashes in the sandbox: do not run
it; the lead runs it outside. The decision being built is the ticket's line "PK-3 (a)" near its end: reds are judged
against the green base when it is an ancestor of HEAD, else the parent of the ticket's oldest own commit (DEC-988 item
3, DEC-989); a batch culprit whose red is its own new test is blamed once confirmed with that candidate alone. The
previous engineer's three commits (bdbf7f069 F-7, 4810c0828 F-1, b5ae48b88 F-3) built it; its own unit tests pass.

**Every pytest run goes through the heavy-job slot**, with a TMPDIR outside the repository and outside
`~/gov-os-runs` (your sandbox TMPDIR is fine), `PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`,
`-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

If the slot script is refused by the sandbox, say so and run the same line without it, once. A session refused twice
for an action stops and says so; it never reaches the same effect by another command, form or file (DEC-1142 (9)).

## The reds (the failing output only; do not open the test files)

Five acceptance cases fail at b5ae48b88654, alone and in the lead's verify, the same way each time:
`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/reds-6.txt` (pytest `--tb=short`). In short:

1. Two batch cases (a culprit whose red is its own new test): `gov.close.batch run A B C` exits 3 `RUN_INCOMPLETE`:
   "the run on rest did not complete: the parallel run did not complete (pytest exit 4; slot: no heavy-job slots are
   configured (heavy_slots); the run took no slot); nothing lands". Expected: A goes back, B and C land on the same
   run. Find why the run on the rest (or the confirmation run with the candidate alone) gets pytest exit 4 in a
   planted project with no `heavy_slots` configured, where the other batch runs complete.
2. Three close cases: "the red was not run once on the head without the change: []" (one existing S4 case that was
   green before the fix round) and "the red was not judged against a base where it passes (runs without the change:
   [])" (two F-1 cases). The scoped close's record (or what it exposes of the runs on the head without the change)
   holds no run on the base after the F-1 change: find where the new base (`select.head_without_change`) stops the
   red's run on it from happening or being recorded.

Each red's fix keeps the selection (S2, S3) and every other S4 and S6 behaviour unchanged. Add a unit test per red
that fails before your fix.

## Done

Your unit tests, `tests/unit/close/`, and the strict suites eng-1.md names (F4) pass in your runs; commit each fix
with eng-1.md's form; return as eng-1.md says, `status` DONE when you believe the five are fixed (say how you checked
without the acceptance files).
