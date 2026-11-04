# D-4, applying the cut (test designers; CTO session 33b3628c, 2026-11-03; DEC-1061)

Read first, whole: `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`, `governance/project/orchestration/INTENT-DEC-1052.md`,
the register's `### DEC-1061` entry (grep; the register is 1.6 MB), `governance/project/orchestration/packages/LIFT-1/D4-LIST.md`
(as decided), your part's list (`D4-LIST-A.md` or `D4-LIST-B.md`) and the reviewer's findings
(`.gov-runtime/scratch/orchestrator/reviews/d4-list.md`: F2, F3, F4 are fixed in the cut).

**Where:** your own worktree and branch (`~/gov-os-worktrees/D4-cut-a`, `w2/D4-cut-a`; or `-b`), cut from
`w2/integrate` at `7842fd94`. Write only `tests/**` there (and `fixtures/evaluation/**` if a row needs it). Commits
with `Task: DAEO-sdxk`, `Implements: DEC-1061`, `Role: independent-test-designer`, a `Rewrite-Reason:` line on every
commit that changes an existing test (the row and the decision), Co-Authored-By as EMG-common shows. **One commit per
step** below, so the review and any revert are per step. TMPDIR as your task brief says.

**The order (DEC-1061):**
1. **Today's red fixes in your part first** (each its own commit, each shown green by running that suite alone).
2. **The opt-in mechanism** (part B builds it, part A only writes its list): `tests/conftest.py`'s
   `pytest_collection_modifyitems` reads **every `tests/optin-lifted*.txt`** (a path or node id per line, then `#` and
   why, the form of `.gov-runtime/scratch/orchestrator/tools/nightly_only.txt`) and deselects their entries unless the run
   says `--optin=lifted` or `GOV_TESTS_OPTIN=lifted`. Part B writes `tests/optin-lifted.txt`; part A writes
   `tests/optin-lifted-guard.txt`. Show it both ways (deselected by default; collected with the option).
3. **The cut, suite by suite** (one commit per suite or family): move to `lifted` (a list entry; never delete those
   files), fold parameters to representative cases (keep every class a KPI line names), apply tier 2's cap of 6 per KPI
   line **after keeping each line's named case first** (F2), delete only the rows the list says delete (D1, D2 and
   part B's four). For each suite, regenerate its README's KPI map: every kept KPI line names the case(s) that cover it in
   the full run, and every line moved to `lifted` says so (F3: the 89 lines without a named case get one). Run each cut
   suite alone after its commit: green.
4. **Your counts at the end:** `pytest tests --collect-only -q` (default, i.e. without the opt-in) and with
   `--optin=lifted`, through `heavy_slot.sh`: your part's cases in the full run and in `lifted`, against the list's figures
   (within about ±15 %; explain any larger difference).

**Rules:** no full suite (DEC-1049): only the suites you change, run alone, through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
`PYTHONPATH=<your worktree>/src`. The CTO's configuration changes (the test map, the path map, `ci.yml`,
`select_tests.py`) are not yours: where a row needs one (T-6, T-7, T-10, T-11, Q-8, Q-10), revise only the test, and
say in your return exactly what configuration change it expects. Never read the hidden half, held-out material or secrets.

**Return:** the twelve fields of EMG-common; the per-step commits in `files_changed`; the counts in `evidence`.
