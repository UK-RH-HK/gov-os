Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: engineer, DAEO-emq1 (W2-115), FULL, class C3 — the owner's P1-K (a): drop the fallback; R2-5's run line (run 5, eng-7)

Budget: projection 3 USD. Keep your context short: this is a two-line change and a one-line doc fix.

You are a fresh engineer for ticket DAEO-emq1 (W2-115), in `/home/usain/gov-os-worktrees/W2-115` on `w2/W2-115`
(DEC-963), head 93d722a38. Step 0 (the sandbox check), every standing rule, the writes (the ticket's `allowed_paths:`
only), the never-read rule for `tests/acceptance/W2-115/**`, the Interface, the commands, the commit form and the
return are those of the first engineer's brief, copied beside this one:
`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/eng-1.md` (read it whole), and the lead's answers in
`eng-2.md` beside it (binding). Do step 0 first and report it first. `gov accept` crashes in the sandbox: do not run
it; the lead runs it outside. The decision being built is the ticket's last section, "P1-K decided"
(`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md`; the owner, DEC-1150 (2), 2026-11-12).

**Every pytest run goes through the heavy-job slot**, with a TMPDIR outside the repository and outside
`~/gov-os-runs` (your sandbox TMPDIR is fine), `PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`,
`-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

A heavy-slot, memory, CPU or disk gate refusal is a wait, not a refusal: run it again when it opens (DEC-1146). If the
slot script is refused by the sandbox, say so and run the same line without it, once. A session refused twice for an
action stops and says so; it never reaches the same effect by another command, form or file (DEC-1142 (9)). Never
write a hand-made `sleep`/`until` wait loop.

## The change 1 (S4, F1; R2-1, the owner's P1-K (a))

`src/gov/close/select.py` `head_without_change` (line ~542) returns the green base when it is an ancestor of HEAD, else
the parent of the ticket's oldest own commit (`own_base`). The owner dropped that fallback: it returns **the green base
when it is an ancestor of HEAD, and None otherwise**. With no head without the change, `attribution.attribute` already
judges every red as the change's (`base is None` → the run without is ABSENT); check it does, and correct the reason
text it appends (`src/gov/close/attribution.py` ~line 392 says "the ticket has no commit of its own", which is now
wrong: say no green base on HEAD's line is known, so the red is the change's). Update the docstrings that name the
dropped fallback. Keep `--base` (an explicit base the caller gives) as it is. Keep the selection (S2, S3) and every
other S4, S5, S6 behaviour unchanged; drop or keep `own_base`'s parameter as is cleanest, updating its one caller.

Unit tests (`tests/unit/close/test_w2_115*`, yours): revise any case asserting the fallback (`tests/unit/close/
test_w2_115_select.py` names `head_without_change`), and add one that fails before your change: a green base that is
not an ancestor of HEAD with an own commit present gives None; none at all gives None.

The failing output (do not open the test files): `/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/reds-7.txt`.
In short, two acceptance cases expect `gov close` to refuse `RED_CAUSED` (red caused, no repair ticket, ticket not
closed) when (a) the only green record names a commit HEAD does not contain and the red is red on the parent of the
oldest own commit too, and (b) there is no green record at all and an untrailered first commit broke the test; today
both close at exit 0.

## The change 2 (S9; R2-5)

`docs/research/W2-115-smart-close.md` line 34, inside the inline script's docstring, reads
`Run: PYTHONPATH=<worktree>/src python3 -I s9.py <close-build log folder>`. `-I` ignores `PYTHONPATH`, so `gov` cannot be
imported. Drop `-I` on that line only (the document's re-run paragraph already runs without it). Nothing else.

## Commits

Two commits in eng-1.md's form (`Task: DAEO-emq1`, `Role: engineer`, `Implements:` from the ticket's sources only,
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`):
1. `W2-115 (DAEO-emq1): no green base on HEAD's line, no head without the change: every red is the change's (P1-K (a), R2-1)`
   with `Implements: DEC-988, DEC-989, DEC-1083, DEC-983`.
2. `W2-115 (DAEO-emq1): the S9 script's run line without -I (R2-5)` with `Implements: DEC-983`.

## Done

Your unit tests, `tests/unit/close/`, and the strict suites eng-1.md names (F4) pass in your runs; quote each last
line; return as eng-1.md says, `status` DONE when you believe both reds are fixed (say how you checked without the
acceptance files).
