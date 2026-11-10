# The review of ACT-WIN-TOAST-1: tools/win_toast.ps1 out of the test map's record_only list (DEC-1112 (3))

You are a fresh, read-only independent reviewer of an ACT before it goes to the operator agent's queue (class (a);
DEC-1104 (2): rehearsal, a READY review and matching hashes). READY is computed by `verdict.py` from your block.

## The ACT
- **The package:** `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-WIN-TOAST-1.md`.
- **The drafts:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/win-toast/`:
  `apply.sh` (check, apply, undo), `test-map.candidate.yaml`, `test-map.patch`, `rehearse.sh`, `rehearsal.log`.
- **Why:** W2-66's D-10 review F2 (`reviews/D10-W2-66-review.md`). `governance/project/test-map.yaml` lists
  `governance/project/orchestration/tools/win_toast.ps1` as record-only, while `governance/project/orchestration/tools/deadman.py`
  runs it. A change to it would therefore run only the record set and skip its tests, which fails open for the
  selection. The CTO decided (delegated, DEC-1112 (3)) that it is not record-only.

## Check
1. **The change is exactly what the package says:** one `record_only` line turned into a comment that keeps it; every
   other key unchanged. Compare `test-map.candidate.yaml` with the live map, and recompute both sha256s against the
   package's.
2. **It only tightens:**
   - after it, what does `src/gov/close/select.py` (read it) do with a change to `win_toast.ps1`: unplaced, so the
     full set, or something else?
   - Is any other record or path affected?
   - Does W2-66's live-map suite stay green (the rehearsal says 89 passed)? Run it read-only against a copy of the
     candidate if you can, without writing the live map.
3. **apply.sh is safe:**
   - `check` changes nothing;
   - `apply` refuses on a map in an unknown state;
   - `undo` restores byte for byte and checks the backup's hash;
   - it works only in the tree it sits in.
   - Is the class (a) right?
4. **The operator's commit line:** `Role: owner`, `Task: decision-record`; only the map is committed.

KPI id for the verdict block: `act-win-toast-1`.

You write nothing in any tree; run nothing that writes the live map (read `apply.sh`, do not run `apply`).

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<the branch's worktree>/src`, a TMPDIR folder of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` if you set an empty HOME (so pytest is found).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
