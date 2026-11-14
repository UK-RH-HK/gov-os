You are a fresh independent test designer. Ticket: DAEO-cv58 (W2-60a), profile FULL. Worktree `/home/usain/gov-os-worktrees/W2-60a-tests`, branch `w2/W2-60a-tests` (an engineer works in the main tree `/home/usain/gov-os-worktrees/W2-60a` at the same time: never write there). One job: revise one decided-behaviour helper in `tests/acceptance/W1-46/w1_46_support.py` (P-10 (a), the CTO's decision under DEC-1156 (7)). Time budget about 30 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a-tests`, `w2/W2-60a-tests`). If anything differs, stop and say so.

## Rules

- Foreground only. Your one file: `tests/acceptance/W1-46/w1_46_support.py`, edited with the Edit tool and its absolute path. A guard refusal is the answer: stop and report it (twice for the same call: stop; never another form). Never code under `src/`.
- Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with your session's own `$TMPDIR` as TMPDIR, `HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a-tests/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`; write the output to a file under `$TMPDIR` and read its tail. A resource gate's refusal is a wait.
- Commit your file only: `git commit -m "<subject>" --trailer "Task: DAEO-cv58" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-826, DEC-839" --trailer "Rewrite-Reason: <one line naming P-4 (A) (DEC-1167) and DEC-1156 (7)>" -- tests/acceptance/W1-46/w1_46_support.py`. No merge, checkout, reset, stash, clean, rebase or push. Commit hash in 12 digits.

## The job

`w1_46_support.py:506`, `caller_args_then_template_pair`, accepts only the old trailing pair `--append-system-prompt-file <root>/.claude/templates/<stem>.md`. Since the merge of w2/integrate into W2-60a (P-4 (A)), a worker launch hands exactly one `--append-system-prompt-file <TMPDIR>/role-<role>.md` (the role text, a blank line, the template's bytes), placed last after the caller's arguments, which still reach the CLI as one unchanged run. Three cases fail on the helper alone: `test_w1_46_bypass_and_added_directories.py:108` `[accept-edits]`, `test_w1_46_guard_wiring.py:68` `[engineer]`, `tests/acceptance/W1-28/test_w1_28_launch_product_spec.py:110`.

Revise the helper so it accepts exactly one `--append-system-prompt-file <path>` pair after the caller's unchanged run, where `<path>`'s file name is `role-<role>.md` (and, if the helper keeps the old form for leads, the old template pair stays accepted only there). It must still refuse: a second pair, a pair before or inside the caller's run, any change, addition or removal in the caller's arguments, and anything after the pair. Keep the helper's name and signature (or add an argument with a default) so its callers stay as they are; change no case's assertion text.

## Verify, then return

Run `tests/acceptance/W1-46` and `tests/acceptance/W1-28` (each its own run): the three cases green, nothing else turned red. Show the helper still refuses the forms above (a short check of your own under `$TMPDIR`, not committed). Return the twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line: the sandbox check, the counts per run, every red named, the guard refusals met (count), and your commit's hash and trailers.
