Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-152-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-152 — a link-notice fix in your cases, the independent test designer's brief (DAEO-o5x1)

You are a fresh independent test designer for **W2-152** (`.tickets/DAEO-o5x1.md`), which is merged. The structural
pass's `gov links` family reports three notices in your predecessor's revision-2 cases:
`UNKNOWN_ID W2-901`, `W2-908` and `W2-909` in a test file, `tests/acceptance/W2-152/test_w2_152_rev2.py:40`. The
cause: that line is a comment naming the planted ids. `gov links` counts an id inside a string literal (not a
docstring) as a planted stand-in (W2-129 S17), but not one in a comment.

## The change
- Reword the comment at line 40 (and any other comment in `tests/acceptance/W2-152/` that names a planted `W2-9xx`
  or `DAEO-fx..` id) so it no longer names the ids. For example: "the closed planted ticket and the open one; the
  briefed ticket itself is not used".
- Alternatively, move the ids into the code's own string literals, where they already are.
- Change no assertion, fixture or behaviour. The 67 cases stay exactly as they are.
- Check: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-152-tests/src python3 -m gov.cli.main links --since HEAD~1 --root /home/usain/gov-os-worktrees/W2-152-tests`
  after your commit. Expect no `UNKNOWN_ID` in `tests/acceptance/W2-152/`. Also run the folder's cases:
  `python3 -m pytest tests/acceptance/W2-152 -q -p no:cacheprovider -m "not local_only"`, which must give the same
  counts as before.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-152-tests`, branch `w2/W2-152-tests`, with integrate merged by the
  CTO. Write only `tests/acceptance/W2-152/`.
- Never open `/home/usain/gov-os-worktrees/W2-152`, `w2/W2-152` or `src/gov/brief/`. Keep searches inside your
  worktree. No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the
  sandbox.
- **Commit** on `w2/W2-152-tests`, only `tests/acceptance/W2-152/`, with
  `--trailer "Task: DAEO-o5x1" --trailer "Implements: DEC-1050" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A one-line round.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the diff, `gov links`'s line, the folder's counts, the commit.
