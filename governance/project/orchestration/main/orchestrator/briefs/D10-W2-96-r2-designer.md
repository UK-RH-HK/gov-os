# D-10 round 2: tests for the map reader's listed forms, scope (b) and the crash result (W2-96, DAEO-ouet; S-D10a, S-D10b)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`; read its
S-D10a and S-D10b lines). Round 1's review found three things; the CTO decided the scope question (PKG-D10a-scope
(b), delegated under DEC-1112 (3); `governance/project/orchestration/DECISIONS-IN-FORCE.md`, last entry).

## The behaviour to test
1. **Scope (b), a revision of your folder's own cases (Rewrite-Reason below).** A formal `gov accept` enables only the
   `breadth` group (`tests/optin-lifted-breadth.txt`) for its map's cases, never `lifted` (`tests/optin-lifted.txt`).
   DEC-1061 (2): lifted is report-only. So:
   - a KPI line whose mapped cases rest **only** on `lifted` cases has `"outcome": "report-only"` in `--json` (the
     text form prints `report-only (lifted)` for it); it is neither pass nor fail and does not by itself fail the
     run; the top-level `"report_only": ["lifted"]` names the group; `"optin"` never holds `lifted`;
   - a line with some cases in `lifted` and some elsewhere is measured on the cases that run (lifted's do not run);
   - a line whose cases run zero for any other reason (named nowhere, or in no group) still fails;
   - a `lifted` case never runs in a formal accept (a failing lifted case changes nothing).
   The variants `a-case-in-lifted-passes` and `lines-in-both-groups-through-every-list-name` in
   `test_w2_96_at_d10a_optin.py` assert the old reading (lifted enabled); revise them to the above.
2. **F1: every listed form is read in full or refused, never dropped.** For each cell below, the report names every
   line the cell lists (each with the row's case), or the map is refused naming the cell (`ACCEPT_MAP_UNREADABLE`, as
   now). Never: only the first line reported and the others neither reported nor refused.
   - `Success 5 [CAP-37.g], first half, and failure 1` (W1-49 row 88) and `… second half, and failure 2` (row 89)
   - `Success 6 with success 4.` (W2-92 row 128)
   - `S2-S4`, `Success 2–Success 4`, `Success 1 to 3`
   - `Success 1 or failure 2`, `Success 1 (and failure 2)`, `Success 1 — and failure 2`
   - `Success 4, failures 4, 5`
   Your existing red case `words-between-the-names` covers one form; extend in its style, one variant per form.
   Include the fail-open shape: the second line mapped nowhere else, and the second line also mapped on another,
   passing row while this row's case fails (its line must not read `pass`).
3. **F3: a crash result names the groups.** When a run with a group enabled ends in an `error` (any kind, e.g. a
   planted project whose test run cannot start), `"optin"` still names the enabled groups, in `--json` and text.

Keep every existing case green or as it is; the readable forms' guard stays.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-96-d10b-tests`, branch `w2/W2-96-d10b-tests` (head `88c0772ff`).
- Write only `tests/acceptance/W2-96/**`; map every new case in the README by full node id (S-D10a = Success 7,
  S-D10b = Success 8) with its red reason. Do not read `src/gov/accept/**` (DEC-820 (c)).
- Show the new and revised cases red at the tree's code for the stated reason (`PYTHONPATH=<worktree>/src`,
  `--optin=lifted --optin=breadth -n 4`, the heavy slot, your own TMPDIR=/tmp/…, `PYTHONUSERBASE=/home/usain/.local`
  if HOME is a scratch folder). Run only W2-96's D-10 files and the premises file; never the full suite.

## Rules
- `EMG-common.md` holds, including its hidden-half rule. No GPU, no installs, never `git worktree prune`.
- Commit on `w2/W2-96-d10b-tests` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1112, DEC-1061"`
  `--trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: PKG-D10a-scope (b) (DEC-1112 (3), DEC-1061 (2)); DEC-866"`
  `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.
- Estimate: 40 minutes. Return the twelve fields, short: the cases added and revised, red and why, the head commit.
