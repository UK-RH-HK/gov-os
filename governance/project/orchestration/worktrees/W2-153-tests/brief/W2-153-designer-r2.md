Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 revision 2 — the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer for **W2-153** (`.tickets/DAEO-8s85.md`). Your predecessor's 50 cases
(TESTS-READY `0c73fd5a2cbe`) are in `tests/acceptance/W2-153/`. The CTO then decided two things, now in the ticket's
body under "Decided after the build", which is merged into your branch:

- **The skills list sits under `claudecode: skills:`** in each `.rulesync/subagents/<role>.md`, not at the top level.
  rulesync 24.0.0 drops a top-level `skills` from the generated agent, so S3 would deliver nothing.
- The launcher's existing unit tests write the template copy in their fixtures. This is the engineer's work, and
  needs no acceptance case.

## The change
- `test_w2_153_sources.py`, the S3 cases: read the list at `front["claudecode"]["skills"]`, not `front["skills"]`.
  "The front matter changed beyond the skills list" becomes: equal to integrate's except `claudecode.skills` added
  (the rest of `claudecode`, such as `tools`, unchanged). The test-design rule (D-5) stays as it is, applied to
  `claudecode.skills`.
- Add one case: a source with the list at the top level (and none under `claudecode`) is not accepted. That is the
  silent loss this decision prevents.
- If any S3 portability fixture plants a top-level `skills:`, move it the same way.
- Update the README's map and its notes. Change nothing else.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`, with integrate merged in by the
  CTO. Write only `tests/acceptance/W2-153/`.
- **Never read the implementation:** never open `/home/usain/gov-os-worktrees/W2-153` or `w2/W2-153`. Keep every
  search inside your worktree.
- Run only your cases, with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not found):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src python3 -m pytest tests/acceptance/W2-153 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit"`.
- No GPU, model, network or installs; no real session. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the
  sandbox. Search again once (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-153-tests`, only `tests/acceptance/W2-153/`, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: keep it short.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the cases changed and added, the run's counts, the commit and `TESTS-READY <hash12>`.
