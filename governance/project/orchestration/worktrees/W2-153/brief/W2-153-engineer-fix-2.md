Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 fix round — the engineer's brief (DAEO-8s85)

You are a fresh engineer for **W2-153** (`.tickets/DAEO-8s85.md`: read it, especially "Decided after the build").
The build is on `w2/W2-153` (`e57be0ee8`; `gov accept W2-153` 50/50). The CTO decided the two points it raised:

1. **The skills list moves under `claudecode: skills:`** in each `.rulesync/subagents/<role>.md` and the template's
   copies. rulesync 24.0.0 drops a top-level `skills`. The portability composition follows. The test designer
   revised the S3 cases to match; the CTO merged them into your branch.
2. **The launcher's existing unit tests** (`tests/unit/launch/test_runs.py`, `test_w1_28.py`, `test_w1_32.py`,
   `test_w2_136_plan_check.py`, now in your paths) write the role's `.claude/templates/<stem>.md` in their fixtures.
   W2-136's assert that the caller's arguments end the argv allows the one appended flag. Change nothing else in
   them.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-153`, branch `w2/W2-153`, with integrate and the revised cases merged
  in. Your paths: the ticket's `allowed_paths`.
- **You never read `tests/acceptance/W2-153/`** (DEC-820 (c)). Run the cases through
  `python3 -m gov.cli.main accept W2-153 --root /home/usain/gov-os-worktrees/W2-153`. If that crashes in the sandbox,
  run `python3 -m pytest tests/acceptance/W2-153 -q -p no:cacheprovider -rf` with
  `PYTHONUSERBASE=/home/usain/.local`. Read only the result lines.
- Then `tests/unit/launch` and `tests/unit/adapters` in full, with
  `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: 0 failures. Then
  `gov accept W2-128`. Use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153/src`. No whole-suite run.
- Prove the decision on a temporary copy: rulesync generate (`rulesync generate --targets claudecode --features subagents --input-roots <copy>/.rulesync`
  into an empty temporary folder). Each generated agent must carry its skills. Quote one.
- Never start a real session. No GPU, model, network, installs or `gov retrieve`. Never open `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per
  Bash call. Search again once (DEC-1092 (1)) if a search does not answer.
- Do not merge. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- `.claude/templates/` in your tree holds eight untracked byte copies of the kernel templates, placed by the CTO so your
  branch's launcher can start you (what the ACT installs). Never commit or change them.
- **Commit** on `w2/W2-153`, only your paths, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: keep it short.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), what changed, `gov accept W2-153`'s and W2-128's counts, the unit suites' counts, and the quoted generated
  agent.
