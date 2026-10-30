You are the ticket lead for ticket `DAEO-av72` (`W2-79`, "Acceptance tests for the orchestrator's lead brief builder"), profile LITE, a test-design ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-79` on branch `w2/W2-79`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. `git ls-files governance/project/orchestration/tools/` must list `build_lead_brief.py`, `placeholder_scan.py` and `README.md`. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-av72.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-79");
- the package `governance/project/orchestration/packages/P-TOOLS-REVIEW-1.md`: §2 (the builder's row) and §4 (a);
- DEC-941 (item 5), DEC-927 (item 2), DEC-820 ((c) and (d)), DEC-849, DEC-824, DEC-893, DEC-868 and DEC-936;
- the committed tool and its README under `governance/project/orchestration/tools/`, and the committed common brief, `governance/project/briefs/LEAD-w2-common.md` (its block on the guard's command forms);
- the guard's read decision (`src/gov/guard/reads.py`, `src/gov/guard/decide.py`), and its reading of a shell command's write targets in `decide.py`;
- DEC-893's scan as committed, `governance/project/orchestration/tools/placeholder_scan.py`.

## Why you start now

- **P-TOOLS-REVIEW-1 (a), accepted by the owner (DEC-941 item 5):** commit and test the orchestrator's tools, then an independent auditor's review.
- **The builder fills every lead's brief and every worker's `Implements:` trailer, and nothing tests it.**
  - It caused T7: a role in IMPL put 41 commits on DEC-927's correction list.
  - A check against the role's refusals would have caught P2: W2-68's test designer was sent to a read the guard refuses.
  - A required block on the guard's command forms would have caught S10: about 45 of 74 lead returns relearned them.
- **Every lead started from today is built by it.**

## The decisions for this run

- **Who writes what.**
  - A fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`) writes `tests/acceptance/W2-79/**`: the cases and a README that maps each KPI line to its cases and its red reason, and states the interface the cases assume. Nothing else.
  - Nobody in this ticket changes the tool. The orchestrator's change turns the red cases green after your merge, as a record commit under `governance/project/orchestration/tools/` (the card), and the tools' independent audit reads it.
  - No engineer runs here, and you write no test.
- **The precondition (the orchestrator's, before your launch):** `build_lead_brief.py`, `placeholder_scan.py` and the tools' `README.md` are committed on `w2/integrate` under `governance/project/orchestration/tools/`, and are in your head (the check above). If they are not, return PACKAGES. Never copy them from the main tree's `.gov-runtime/scratch/orchestrator/tools/`.
- **How the cases find the tool.** Your only allowed path is `tests/acceptance/W2-79/**`.
  - The cases run `governance/project/orchestration/tools/build_lead_brief.py` of the repository that holds the test file, found from the test file's own location, as a process (`sys.executable`).
  - Never an absolute path into the main tree, and never the scratch copy. So this worktree, a close of the main tree and the nightly's clone each test their own committed copy.
  - A missing tool fails, naming it; it is never skipped.
  - The common brief and the guard decision are given through the interface the README states: settable, defaulting to the committed brief and the pinned guard. Where the committed tool lacks that interface, the cases are red for that reason, named.
- **Planted, never real.** The refused-read cases build a temporary repository from scratch, with its own ticket file, path map and planted folders: an acceptance folder, a design note among the ticket's implementation paths (P2's form), a planted secrets file, and a planted evaluation set whose hidden part a measured role is sent to.
  - No case reads or names this repository's held-out material, or any `fixtures/evaluation/**/hidden/**` path (KPI line 2; DEC-820 (d)).
  - The committed common brief with an ordinary ticket part is not flagged: its own prohibitions direct no read.
- **Read from the source, never copied:**
  - each command form the guard-forms block names is judged by the guard's own decision on a sample command of that form;
  - DEC-893's placeholder forms are read from the scan;
  - the slots are those the tool fills.

  A case that copies a list it could read is a finding.
- **The angle slots the common brief keeps** for the lead's own launches (`<role>`, `<name>`, `<effort>`) are not placeholders.
- **Red first, each for its own reason.** The cases KPI line 7 names are red today: the refused read, the guard-forms block, the part's own slots, the empty value and the unresolved id. The cases of what the tool already does (a role in IMPL refused, a slot missing, a placeholder left in the common part) are green now, unless the interface is missing. A case red for any other reason is a finding before you return.
- **Hermetic:** the cases write only in their temporary folders, need no network, run under 30 s alone, and are never skipped.
- **Policy 2 (c) here:** this ticket's implementation is the orchestrator's later change to the tool. The test designer reads the tool as committed at your head.

## Your checks (a script file under `.gov-runtime/scratch/lead/`; never `python3 -c` with braces, DEC-409)

- `tests/acceptance/W2-79/` alone, twice: the red set is exactly the README's, each red for its stated reason; no skip (`-rs`); under 30 s.
- `git status --short` shows nothing outside `tests/acceptance/W2-79/`, and the tripwire shows no change in the main tree or another worktree.
- `pytest --collect-only -q` over `tests`: no collection error.

## Verification

The full run in the close's form, under the lock, with the retention option and the disk gate first.
- **W2-79's own red cases are red in it by design:** name each with its README reason. Any other red is named with its cause.
- **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), run no suite and no full run. Wait, and go on the moment it is gone. Your full run also waits for the verification lock.
- **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
- **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
- **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.

**Running beside you:**
- No running ticket holds `tests/acceptance/W2-79/**`.
- W2-58 (`DAEO-5j8b`, closing) holds `src/gov/guard/decide.py`, `reads.py`, `heldout.py` and `protected.py`: the cases call its decision and edit nothing.
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`. W2-61 holds `src/gov/retrieval/measure.py`. W2-03 holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`. W2-05 holds the git-environment lines across `src/gov/**/*.py`, and `src/gov/util/gitenv.py`. W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`. W2-77 holds `src/gov/close/nightly.py`. W2-68 is closing.

Do not touch any of these.

**No review (LITE).**

## This run's order

1. The precondition check (above).
2. The test designer.
3. Your checks.
4. Rebuild and verify in full.
5. **Return** DONE or PACKAGES. DONE means the branch is ready to merge; the orchestrator's change to the tool follows, and the ticket closes when it turns the red cases green.

**Estimate:** about 220 lines, about 4 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
