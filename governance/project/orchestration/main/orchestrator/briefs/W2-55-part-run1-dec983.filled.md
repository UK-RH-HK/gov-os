You are the ticket lead for ticket `DAEO-arrl` (`W2-55`, "Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-55` on branch `w2/W2-55`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `84c1d4277b9c`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-arrl.md`) in full, as changed on 2026-10-31 by DEC-983 (its last success KPI, `gov context --in-force`, and the body line that it runs before W2-115), and its card in `docs/plan/WAVE_2_WBS.md` §2;
- DEC-791 item 1, DEC-825 items 2 and 4, DEC-866, DEC-851, DEC-786, DEC-941, DEC-833 item 3, DEC-952 item 5, DEC-953 item 7, DEC-982 and DEC-983 in `docs/DECISION_REGISTER.md`;
- `governance/project/orchestration/packages/SMART-WORK-1.md` (practice 15, and the four contradictions it found: W2-20, W2-97, W2-38 and W2-12, which KPI 5's check would have caught);
- `governance/project/orchestration/DECISIONS-IN-FORCE.md` (this repository's hand-made digest: what `--in-force` generates, from the register);
- the code: `src/gov/decisions/` (the checker, W2-03's), `src/gov/context/` (`command.py`, `context_check.py`) and `src/gov/retrieve/command.py`.

## Why you start now

The owner's order (DEC-983): W2-55 runs before W2-115, the smart close. Its KPI 5 ("supersession propagates") finds the tests, code, skills and KPIs that still enforce a superseded or changed decision, before the close is rebuilt on them. It also gives the digest of the decisions in force that every fresh session loads (practice 15). W2-03 (`DAEO-ym8a`), which owned the decision files, is closed.

## The decisions for this run

- **The work order (DEC-963):** a fresh independent test designer (sandboxed, `--effort high`, in the `W2-55-tests` worktree, retrieving only from the integration branch's store) writes `tests/acceptance/W2-55/` from the KPIs, in proportion, red first; **in parallel**, a fresh engineer (sandboxed, `--effort high`) builds to the spec and the KPIs, never reading the tests, and runs them once ready through `gov accept`, reading pass or fail only. You merge the tests branch (`-F` message file), one writer per worktree.
- **The backfill is a proposal only** (KPI 4): `docs/research/W2-55-backfill.md`, every entry's proposed domain, status, scope and "lands in" tag with its reason, the 120 amends and refines DEC-825 left, and a sample for the owner. **Nothing is written to `docs/DECISION_REGISTER.md`** (it is not in your paths); the orchestrator applies the accepted backfill.
- **KPI 5, supersession propagates:** its check names, for each superseded or changed decision, every test, code path, skill, brief, ticket KPI, prompt line or path-map line that still enforces it without a recorded reason. Run it on this repository and give its findings in your return (expect at least the four SMART-WORK-1 found, now fixed by DEC-983: say whether it still finds them). A finding is a report, not a change outside your paths.
- **`gov context --in-force`:** generated from the register, one line each, superseded and done entries left out, the count left out stated. **The session-start hook's loading of it is the owner's CIT-P question (DEC-952 item 5) and the hook is not in your paths:** build the command, and return the hook's change as a package with the CIT-P line, not as an edit.
- **Shared files:** `src/gov/context/**` you hold now (W2-04, which shares it, is open and not running; W2-14 and W2-15a wait for W2-04 later). `src/gov/retrieve/**` you share with **W2-13**, which is on the critical chain and starts as soon as W2-108 closes: touch only the decisions filter in `src/gov/retrieve/command.py`, keep it small, and whichever merges second merges back (DEC-786). Do not touch `src/gov/retrieval/**` or the path map (the critical chain's files).
- **The measure (KPI 6):** W2-61's 20-question measure after the change, both figures beside the baseline and W2-87's (hit@5 11 of 20, full evidence 11 of 20), on a clone, as W2-86's brief describes.
- **Verification:** the scoped set once (DEC-968); every suite goes through `verify_lock.sh`, which takes a heavy-job slot (DEC-983; no load wait). Any red the change did not cause is named for the CTO.
- **No review** (STANDARD).
- **If a step is held for more than 90 minutes:** write your checkpoint and return PACKAGES.

## This run's order

1. The test designer and the engineer in parallel; merge the tests; check them red on the base yourself.
2. The engineer's build to green through `gov accept`; KPI 5's check run on this repository; the backfill proposal.
3. The measure; the scoped run.
4. Return DONE (the branch ready to merge) or PACKAGES (the hook's CIT-P line among them).

**Estimate:** about 150 lines of code and the backfill record; about 6 to 8 hours.
