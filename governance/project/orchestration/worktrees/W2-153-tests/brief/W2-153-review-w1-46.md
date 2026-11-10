Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 — the W1-46 revision, the independent review (DAEO-8s85)

You are a fresh, read-only independent reviewer. Review one test revision made under **W2-153**
(`.tickets/DAEO-8s85.md`: its S1 and Interface).

## What happened
- W2-153 (merged on integrate) appends exactly one pair after the caller's arguments:
  `--append-system-prompt-file <root>/.claude/templates/<stem>.md`. The CTO ruled the order is W2-153's intent
  (DEC-1112 (3)); W2-56's S6 was revised the same way.
- Two W1-46 cases asserted the caller's arguments end the argv "unchanged, in order", and turned red:
  - `test_w1_46_bypass_and_added_directories.py::test_a_harmless_permission_mode_is_launched[accept-edits]`;
  - `test_w1_46_guard_wiring.py::test_a_headless_workers_ordinary_arguments_pass_unchanged[engineer]`.
- A test designer revised them under DEC-866: `w2/W2-153-tests` commit `23f63f49eccc`
  (`git show 23f63f49eccc`), in `/home/usain/gov-os-worktrees/W2-153-tests`.

## Check
- **Strength:** the revised assertions still fail on a dropped, extra or reordered caller argument, and on anything
  after the caller's arguments other than exactly that one pair. Probe it: write small inputs to the helper in a
  scratch Python call, read-only. Is the helper's path check strict, ending `.claude/templates/<stem>.md`?
- **Scope:** nothing else in W1-46 changed; the `Rewrite-Reason:` trailer is present; W1-35/W2-56 tests are untouched.
- **Why only one parameter of each case was red:** `[accept-edits-joined]` and `[research]` passed before the change
  (the designer's discovery). Does that point to a gap, such as a launch path without the template pair, or a case
  that does not look at the tail? Look at the cases and integrate's launcher (`src/gov/launch/launcher.py`) and say.
- **The folder on the tree:**
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit" --tb=no`
  should give 122 passed, 0 failed.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- You write nothing in any tree, and run tests read-only with `-p no:cacheprovider`. Single simple Bash commands
  (DEC-1080). Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - every finding with `scope: in|out`;
  - the fenced `verdict` block in DEC-1010's form, one entry, `"kpi": "S1"` (W2-153's S1 as the two cases see it):
    `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [...]}]}`.
