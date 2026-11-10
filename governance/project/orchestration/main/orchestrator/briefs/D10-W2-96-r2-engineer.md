# D-10 round 2: the map reader reads every listed form or refuses; scope (b); groups on a crash (W2-96, DAEO-ouet)

You are a fresh **engineer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`; read S-D10a and S-D10b). Your
branch holds round 1's work (`04b52305a`, `3ac8e892f`; and a scratch merge `08c31e7ff` of the designer's cases, which
you leave alone and never read: `tests/acceptance/W2-96/` stays excluded, `EMG-common.md`'s rule). Round 1's review
(`governance/project/orchestration/reviews/D10-W2-96-accept-review.md`, read F1, F2, F3) and the CTO's decision
PKG-D10a-scope (b) (DEC-1112 (3); `governance/project/orchestration/DECISIONS-IN-FORCE.md`, last entry) give:

1. **F1, the reader (blocking).** `parse_map` and its helpers read every line a cell lists, or refuse the map naming
   the cell (`ACCEPT_MAP_UNREADABLE`, as now); never keep the first and drop the rest silently. Forms seen in maps in
   use: `Success 5 [CAP-37.g], first half, and failure 1` (W1-49 row 88), `… second half, and failure 2` (row 89),
   `Success 6 with success 4.` (W2-92 row 128), `S2-S4`, `Success 2–Success 4`, `Success 1 to 3`,
   `Success 1 or failure 2`, `Success 1 (and failure 2)`, `Success 1 — and failure 2`, `failures 4, 5`. The safe
   rule: after the first line name, any further line name in the cell is either read or the cell is refused. Every
   form readable today keeps its meaning (the round-1 review checked 116 READMEs: keep that true).
2. **Scope (b).** A formal `gov accept` enables only `breadth` (`tests/optin-lifted-breadth.txt`) for its map's
   cases, never `lifted` (`tests/optin-lifted.txt`); lifted is report-only (DEC-1061 (2)). Interface:
   - a KPI line whose mapped cases rest **only** on `lifted` entries: `"outcome": "report-only"` (text:
     `report-only (lifted)`); neither pass nor fail, and it does not by itself fail the run; top-level
     `"report_only": ["lifted"]`; `"optin"` never holds `lifted`;
   - a line with cases in `lifted` and elsewhere is measured on the cases that run;
   - a line whose cases run zero for any other reason still fails (not a looser rule).
3. **F3.** Once groups are set, every result names them in `"optin"`, an `error` (crash) included, in `--json` and
   text.

## The task
- Implement in `src/gov/accept/**`; unit tests in `tests/unit/accept/test_w2_96*` (yours). Keep `tests/unit/accept`
  green (163 today; run it with `--optin=lifted --optin=breadth -n 4`).
- Run `gov accept` the declared way with your tree's code on W2-96, W1-49, W2-92, W1-46 and W1-27
  (`PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept <W>`, through
  the heavy slot); report each line's outcome, and name any map now refused with its cell (a map fix row, not yours).

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-96-d10b`, branch `w2/W2-96-d10b`. Write only `src/gov/accept/**` and
  `tests/unit/accept/test_w2_96*`.
- The heavy slot, `PYTHONPATH=<worktree>/src`, your own TMPDIR=/tmp/…, `PYTHONUSERBASE=/home/usain/.local` if HOME is
  a scratch folder (round 1's F4: give the scratch HOME a `.local` link if pytest cannot be imported).

## Rules
- `EMG-common.md` holds, including its hidden-half rule. No GPU, no installs, never the full suite, never
  `git worktree prune`.
- Commit on `w2/W2-96-d10b` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1112, DEC-1061"`
  `--trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge,
  push, amend or rebase.
- Estimate: 45 minutes. Return the twelve fields, short: the design, unit counts, the five `gov accept` results, any
  refused map, the head commit.
