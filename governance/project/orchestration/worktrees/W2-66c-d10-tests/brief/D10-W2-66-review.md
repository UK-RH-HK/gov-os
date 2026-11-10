Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-66c-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of W2-66's DEC-891 record case leaving out files code reads (W2-66c, DAEO-btcs)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- `tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only[governance/project/orchestration/]`
  called W2-149's result schemas (`governance/project/orchestration/tools/indep-schemas/*.schema.json`) records,
  because they are not code by suffix, and failed because the test map does not list them record-only.
- But `indep_launch.py` reads them. Record-only would skip their tests on a change, which fails open for the
  selection.
- The CTO decided option (a) (delegated, DEC-1112 (3)): the case does not count files read by code.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-66c-d10-tests show dc5c0fd87`.
  - **The rule:** a file under a DEC-891 place is not a record when it sits under a `tools/` folder and a tracked
    `.py` directly in that folder holds a string literal (read with `ast`) exactly equal to the file's path from
    that folder, or one of its folders. `.md` files are always records.
  - `25d72380f` is the CTO's ticket commit (W2-66c in progress for the launch).
- **The designer's runs:** W2-66 1 failed and 168 passed → 169 passed (9 deselected by the exclusion).
  - The rule leaves out 6 files: the 5 schemas and `tools/win_toast.ps1` (named by `deadman.py`).
  - Planted records stay records.

## Check
1. **No fail-open:**
   - Can the rule take a real record out of the case? Consider a `.json` or `.yaml` record a tool merely names in a
     string, a record a `.py` names in a log message, a folder-level string such as `"dispatch"` excluding every file
     under it, and a `tools/` folder anywhere under a DEC-891 place.
   - Is "a string literal equals the path" a sound proxy for "code reads it"?
2. **The finding on `win_toast.ps1`:** the test map lists it record-only while `deadman.py` runs it. Is that a fail
   open the revised case now hides? Should a case catch a record-only entry that code reads? Report it as a finding
   with its scope.
3. **The other cases are unchanged and pass** (`test_paths_dec_891_does_not_name_are_not_record_only`, the
   hides-no-code-path case).
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only `tests/acceptance/W2-66/**`
   changed, plus the CTO's ticket line.

KPI id for the verdict block: `w2-66-records-read-by-code`.

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
