# D-10 round 2: the review of gov accept's opt-in groups (S-D10a) and map reader (S-D10b) (W2-96, DAEO-ouet)

You are a fresh, read-only independent reviewer of tests and code. This is review round 2 of 2, the last
(DEC-1010). READY is computed by `verdict.py` from your block.

## The KPI lines (`.tickets/DAEO-ouet.md`), as the CTO decided them
- **S-D10a**, with PKG-D10a-scope (b) (DEC-1112 (3), DEC-1061 (2);
  `governance/project/orchestration/DECISIONS-IN-FORCE.md`, last entry): a formal `gov accept` enables only
  `breadth` for its map's cases, never `lifted`. A line resting only on `lifted` cases is `"outcome": "report-only"`
  (neither pass nor fail; `"report_only": ["lifted"]`); a line with cases elsewhere too is measured on what runs; a
  line whose cases run zero for any other reason still fails. The report names the enabled groups (`"optin"`) on every
  result, an `error` included (round 1's F3).
- **S-D10b:** the map reader reads every line a cell lists, or refuses the map naming the cell; never drops one.

## Round 1 (`governance/project/orchestration/reviews/D10-W2-96-accept-review.md`)
F1 (blocking): forms with words between names were dropped (W1-49 rows 88/89, W2-92 row 128, `S2-S4`,
`Success 2–Success 4`, `Success 1 or failure 2`, `Success 1 to 3`, `Success 1 (and failure 2)`,
`Success 1 — and failure 2`). F2: lifted ran and counted (now scope (b)). F3: groups absent on a crash.

## What to review: worktree `/home/usain/gov-os-worktrees/W2-96-d10b`, head `bb71be1cf`
- Tests (designer): `5e36c7fc5` and `51f1f547a` on top of round 1's `88c0772ff`; the D-10 files
  `tests/acceptance/W2-96/test_w2_96_at_d10a_optin.py`, `test_w2_96_at_d10b_cells.py`, the README rows.
- Code (engineer): `dac10e5df`, `1df7ccd60` (`src/gov/accept/runner.py`; `tests/unit/accept/test_w2_96_d10_r2.py`).
  The engineer's rule: after the first line name, a further name is read when a join precedes it
  (`, ; / & + ( and or with`), ignored when it repeats a line already read, else the cell is refused; brackets are
  citations, not joins; a possessive mention (`S1's …`) refuses. Their own choice: a run whose every line is
  report-only fails (it measures nothing).
- The engineer's measurements: W2-96 (before the test fix) 144/3; W1-49 refused (its older `Edge:`/`DEC-259:`
  rows); W2-92 newly refused at row 128 (`S1's record route`); W1-46 334/36 with `report_only ["lifted"]` (386/107
  when lifted ran); W1-27 159/19 (round 1's F5 and unmapped breadth reds). Map survey: 112 of 115 read as before;
  W2-150 and W2-72 read more lines.

## Check
1. Run the D-10 files and the premises file (both opt-ins, `-n 4`), then `tests/unit/accept`, and `gov accept W2-96`
   the declared way (`PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-96`). Counts.
2. No fail-open: F1's forms each read in full or refused; no listed line silently dropped (try forms of your own);
   no readable form changed meaning except by reading more; a report-only line never passes the run alone and never
   hides a red of a case that ran; `lifted` never runs in a formal accept; zero-run lines still fail; groups named on
   errors; no test content leaks.
3. F2 and F3 closed as decided; the engineer's two choices (all-report-only fails; possessive refuses) sound or not.
4. Trailers on the round-2 commits.

KPI ids for the verdict block: `s-d10a-optin`, `s-d10b-reader`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- Run tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-d10b/src`, a TMPDIR of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` (or a `.local` link) if you set an empty HOME.
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080). `EMG-common.md`'s hidden-half
  rule holds.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox
  and `ps` checks first); your answers to the checks; every finding with its two lines and scope; at the end the
  fenced `verdict` block `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI
  id, each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 20 minutes.
