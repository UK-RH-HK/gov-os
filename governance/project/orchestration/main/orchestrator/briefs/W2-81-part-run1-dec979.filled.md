You are the ticket lead for ticket `DAEO-l78m` (`W2-81`, "the adoption proving ground"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-81` on branch `w2/W2-81`.

**This is run 1** (the ticket was claimed on 2026-10-29 and has never run; this part replaces the earlier draft). `git rev-parse --short=12 HEAD` must show `26b387a0ad3d` (the orchestrator merged `w2/integrate` in), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-l78m.md`, all its KPI and failure lines) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-81"), with the companion card below it;
- DEC-941, DEC-936 item 3.6, DEC-930, DEC-954 (Q8c, Q9f), DEC-957 (memory for this repository and any adopted one; the target 95 %, floor 85 %), DEC-833, DEC-820 (d), DEC-845, DEC-873, DEC-911, DEC-728, DEC-899 item 7, DEC-953, DEC-979 item 5 (c);
- the form W1-41's cases use to build repositories at test time (`tests/acceptance/W1-41/`, another ticket's tests, open to read);
- the adoption stages as built (`src/gov/adopt/`, read only) and CAP-44.b to CAP-44.j in the Contract, for the handling each planted problem needs.

## Why you start now

- **The owner's order (DEC-979 item 5 c):** alongside the critical chain, what EXAMIN needs: W2-81, W2-88, W2-96. Passing the proving ground is an entry criterion for EXAMIN's copy (DEC-936 item 3.6).
- **Who waits on you:** W2-88 (memory for any repository; its first proof uses your five repositories and question sets, read-only) and W2-93 (W2-81's held-out half: it starts once your README states the hidden half's form and your builders exist).

## The decisions for this run

- **The deliverable is test code, written by an independent test designer** (the ticket's role, MR-3): builders, manifest, judge, scorer, runner, the visible question half and the README, all under `tests/acceptance/W2-81/`. Only the judge's self-tests are named `test_*.py`; the builders and the runner are support modules the regression does not collect. There is no engineer and no product code in this ticket.
- **No tests worktree:** with no implementer to work beside, the test designer works in this worktree itself (launched sandboxed, `--effort high`, retrieving only from the integration branch's store, `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve …`). Run it in batches of about 90 minutes, resumed in the same session or a fresh one from your checkpoint, for example:
  1. the five builders (file by file, commit by commit, in temporary folders), the planted problems in at least two shapes each, the controls, the seed and the manifest kept outside the built repository; the secret built at run time from parts, committed early and removed later, never whole in a tracked file;
  2. the judge (FOUND_AND_HANDLED, MISSED, MISHANDLED; CLEAN or FLAGGED; NOT_BUILT for a stage not built; fail closed) and its mutation self-tests (one killed mutant per planted problem, listed in the README);
  3. the scorer (both figures always, a forbidden citation in the top five a miss), the visible question half (at least 10 per repository with gold sources and forbidden citations), the runner (one command, not collected, writing only under the folder it is given) and the README (each kind's correct handling and the record that shows it; the hidden half's form for W2-93).
- **Against the stages as built:** A0 to A6 and A8 lite now; A7 and A10 lite arrive with W2-52, not yet merged. A stage not built is NOT_BUILT and named, never passed.
- **Not in this ticket:** the hidden question half (W2-93, a separate independent auditor); the path map's `evaluation_sets` entry for it (the orchestrator's, in a gap between queues); the real run and its report (the orchestrator's, after memory and the roles); the `gov close` on a pinned release in each synthetic repository (KPI: its real run is the orchestrator's, once W2-16's release is closed; build the runner's step for it and test it with a stand-in).
- **Never:** clone this repository, its worktrees or the dev tiers; read or list the workbench; use `GOV_DEV_TIERS`; print a planted secret or a hidden question; write outside the suite's temporary folders.

## This run's order

1. The test designer's batches (above), each with its own tests passing; you check each batch's commit, trailers and the tripwire.
2. **Review (FULL):** a fresh independent reviewer (brief A3, `JUDGEMENT.md`'s two questions, effort max) on the final head: above all, can the judge call a miss handled, can a control-flagging adoption pass, can the secret's value leak into any output, can a hidden question be printed. Up to two reviews in this round (DEC-916); its probe record under `docs/probes/DAEO-l78m/`.
3. Verification: the scoped set `select_tests.py` gives, once, in the close's form (DEC-968); the self-tests under 120 s alone and under the close's parallel load; the skip guard's count unchanged.
4. Return DONE or PACKAGES, with what W2-88 and W2-93 may read and in what form.

## Running beside you

- **No running ticket holds `tests/acceptance/W2-81/`.** Keep clear of the critical chain's files (DEC-979 item 5): `src/gov/retrieval/**` and `governance/project/path-map.yaml`. You read `src/gov/adopt/` (W2-52's, paused) and write nothing outside your suite.
- **W2-86** (the path map) and **W2-96** (`gov accept`) run beside you; neither touches your paths.

## Known

- Disk: the built repositories, the large files and the legacy documents are generated in temporary folders and removed; your scratch budget is 20 GB and 1,000,000 files and folders (the common brief).
- The leads' load wait still holds until the heavy-job limit runs (DEC-979); a step held more than 90 minutes: checkpoint and return PACKAGES.

**Estimate:** about 1,200 lines of test code; about 12 to 16 hours across two or three lead sessions (three designer batches about 7 to 9 hours, the review about 2, the scoped run about 1). Plan your checkpoints for a resume.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).
