You are the ticket lead for ticket `DAEO-wq2b` (`W2-97`, "the local merge queue"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-97` on branch `w2/W2-97`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-wq2b.md`) and its row in `docs/plan/WAVE_2_WBS.md` §1 (W2-97);
- DEC-959 item 1 (the owner's choice of a local merge queue, the push the owner's), DEC-953 (items 1, 4 and 5: the close on the 10 practices and the one selection tool), DEC-968 (a close refused only by a failure its change caused; the full suite only in the nightly), DEC-979 items 3 and 5 (a batch sends back only its culprit; the queue is in the first group of work), DEC-848, DEC-954;
- `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §5.3 item 5 and option (c): the "not rocket science rule" built locally, one writer kept;
- the CTO's close tool, which the queue's steps follow and later replace (read it, never edit it): `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_build.py` (clone, rebuild, selection, the parallel and serial runs, the alone re-run, the trace with and without the change: `trace_node`, `decisive`, `attribute`; the culprit search: `assign_culprits`, `explained_without`, `red_alone`, `merge_is_own`), its tests `tools/test_close_build.py` (26, reviewed three times on 2026-10-31), and `tools/select_tests.py` (the one selection, DEC-953 item 4).

## Why you start now

- **The owner's order (DEC-979 item 5 a):** what speeds up all the work comes first: W2-107's close (done), the batch of eight, W2-108, then the heavy-job limit and **this merge queue**.
- **What it saves:** today every close builds a clone, rebuilds and runs the scoped set again on code its lead already tested, and a red batch is traced by hand-made tools in scratch. The queue tests the merged result once, advances `w2/integrate` only to the commit it tested, and gives the close a record to cite instead of a second run.

## The decisions for this run

- **Home (the ticket's card):** `governance/project/orchestration/tools/merge_queue.py`, tracked, with unit tests under `tests/unit/orchestration/test_w2_97*` and a `README.md` in that folder. The folder does not exist yet: you make it. Nothing under `.gov-runtime/scratch/` is moved or changed by this ticket.
- **One writer:** the queue is the CTO's tool. It moves `w2/integrate` only by `--ff-only` to a merge commit it made and tested; it never pushes, never touches `main`, never amends, rebases or resets a shared branch. Until the three layers start, a ticket enters only with the CTO's approval (a flag or a file the CTO writes; say which).
- **A red batch (KPI 4) follows DEC-979 item 3** as `close_build.py` now does it: find each red's culprit (that ticket's merge taken out, the red re-run alone, three rounds), advance the rest on the same run, eject only the culprits; a red no single ticket explains, a ticket whose merge brings another ticket's commits, or a candidate that cannot be isolated, ejects the whole batch (fail closed). Reuse the reviewed functions' logic; do not import from scratch (it is untracked): copy what you need into the tracked tool, with its tests.
- **A red that the change did not cause (DEC-968):** red without the batch too is not the batch's: named in the record, the batch still advances; a red that passes alone is a flaky candidate, named, deciding nothing.
- **Skips (KPI 3):** the run is skipped only when the merged result's code paths equal the tree the lead tested (governance records left out), with the reason recorded; a change to the core gets the selection's own scope, never a full run outside the nightly.
- **The record (KPI 5):** each advance writes one record the close cites (head, tickets, selection, counts, time). Changing `close_build.py` to cite it is the CTO's, after your merge; say in your return what the close must read.
- **Stand-ins only in tests:** planted repositories with a fake integration branch and stub test commands (the ticket's acceptance line); no test touches this repository's branches, its stores or `~/gov-os-runs/`.

## This run's order (the common brief's work order, DEC-963)

1. **In parallel:** a fresh independent test designer (sandboxed, `--effort high`, in the `W2-97-tests` worktree, retrieving only from the integration branch's store) writes `tests/acceptance/W2-97/` from the ticket's KPIs and failure lines, in proportion (DEC-951 item 5: the minimum that shows each line); a fresh engineer (sandboxed, `--effort high`) builds the tool from the spec and the KPIs, never reading the tests.
2. You merge the tests branch here (`-F` message file), check the cases red on `@@HEAD@@` for their stated reasons, then the engineer runs them once, reading results only.
3. Verification: the scoped set `select_tests.py` gives, in the close's form, once before you return (DEC-968).
4. **No review (STANDARD).** Return DONE or PACKAGES.

## Running beside you

- **No running ticket holds your paths.** Keep clear of the critical chain's files (DEC-979 item 5): `src/gov/retrieval/**` (W2-13, W2-32, W2-92, W2-108) and `governance/project/path-map.yaml` (W2-86). You change no `src/` file at all.
- **The CTO's own tools** in `.gov-runtime/scratch/orchestrator/tools/` keep running closes while you build: read them, never write them.
- **W2-110 and W2-05** are paused with packages; **W2-86, W2-96** run.

## Known

- The leads' load wait in the common brief still holds until the heavy-job limit runs (DEC-979 item 1); a step held more than 90 minutes: checkpoint and return PACKAGES.
- Name as rows for the Wave 3 list anything the queue cannot do alone (for example a queue for several machines).

**Estimate:** about 250 lines of tool and 150 of unit tests; about 6 to 8 hours (tests and engineer in parallel about 3 hours, the red check and the engineer's run about 1, the scoped run about 1 to 1.5 at today's load).

If your session nears its end first, write your checkpoint and return PACKAGES naming what is left.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).
