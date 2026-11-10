# A fresh FULL probe of W2-96 (DAEO-ouet) after D-10's S-D10a/b merge (DEC-1112 (3), PKG-D10a-scope (b))

You are a fresh, read-only independent reviewer: the **FULL probe** of W2-96 covering everything since its last
probe (`docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md`, pass at `8b31965edae8`).

## What changed since that probe
- `.tickets/DAEO-ouet.md` gained S-D10a and S-D10b (`bbe222c59`).
- The merge `8f6e66a17` into w2/integrate brought `w2/W2-96-d10b` at `bb71be1cf`: tests `88c0772ff`, `5e36c7fc5`,
  `51f1f547a` (`tests/acceptance/W2-96/`, the D-10 files and README rows); code `04b52305a`, `3ac8e892f`,
  `dac10e5df`, `1df7ccd60` (`src/gov/accept/runner.py`, `tests/unit/accept/test_w2_96_d10*.py`); and an untrailered
  scratch merge `08c31e7ff` (tests beside code, kept by the CTO).
- Read `git log 8b31965edae8..8f6e66a17 -- .tickets/DAEO-ouet.md src/gov/accept tests/acceptance/W2-96 tests/unit/accept`
  to confirm nothing else touched W2-96's judged files.
- The two-round review (`governance/project/orchestration/reviews/D10-W2-96-accept-review.md`, READY at round 2)
  left rows F1-F4 of round 2; do not re-litigate them unless you find them reachable in ordinary work.
- Scope (b): a formal accept enables only `breadth`; a line resting only on `lifted` cases is `report-only`
  (DEC-1061 (2)), never pass; groups named on every result.

## What to judge, against W2-96's KPIs (its ticket file at `8f6e66a17`), every line, S-D10a/b included
1. **Run read-only** in `/home/usain/gov-os-worktrees/W2-96-d10b` (detached at `8f6e66a17`):
   - W2-96's acceptance folder (both opt-ins, `-n 4`);
   - `tests/unit/accept` (both opt-ins, `-n 4`);
   - `gov accept W2-96` the declared way:
     `PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-96`.
   Report the counts. The last probe found the declared run failing four lines with every case passing; say whether
   that still holds.
2. No fail-open in the KPIs' terms: no test content leaks; unmapped cases counted; exit codes as declared; nothing
   written; the reader never drops a listed line; lifted never runs or passes in a formal accept.
3. **Your judgement:** pass or fail for W2-96 at `8f6e66a17`.

KPI id for the verdict block: `w2-96-full-probe`. Put the probed commit and your session id in `evidence`.

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
  fenced `verdict` block `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 20 minutes.
