You are a fresh engineer. Ticket: DAEO-cv58 (W2-60a), profile FULL, class C3. Worktree `/home/usain/gov-os-worktrees/W2-60a`, branch `w2/W2-60a`. One small red to fix in the launcher. Time budget about 40 minutes. The acceptance tests are the test designer's; you never change them.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a`, `w2/W2-60a`). If anything differs, stop and say so.

## Rules

- Foreground only. Your paths: `src/gov/launch/launcher.py` (its settings-building lines only), `src/gov/launch/record.py`, `tests/unit/launch/test_launch_record*`, `tests/unit/launch/test_role*`. Never edit `tests/acceptance/**`; do not grep or read under `tests/acceptance/W2-60a/` (the guard refuses it to you); `tests/acceptance/W2-56/` you may read. W2-05 holds the git-environment lines of `src/gov/**/*.py`: leave them alone.
- A guard refusal is the answer: stop and report it (twice for the same call: stop; never another form).
- Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with your session's own `$TMPDIR` as TMPDIR, `HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`; write the output to a file under `$TMPDIR` and read its tail. A resource gate's refusal is a wait.
- Write with the Write and Edit tools and absolute paths. No merge, checkout, reset, stash, clean, rebase or push. Commit your files only: `git commit -m "<subject>" --trailer "Task: DAEO-cv58" --trailer "Role: engineer" --trailer "Implements: DEC-826, DEC-839" -- <your paths>`. Commit hash in 12 digits.

## The failing case (its output only)

`tests/acceptance/W2-56/test_w2_56_sandbox_block.py:105`, `test_s3_no_sandbox_entry_is_made_from_any_allowed_path`: two launches in one box, for two tickets, must give the same settings (but the write list's length and env). It fails with "the sandbox block or the deny rules change with the ticket's allowed paths". The two deny lists hold the same rules in a different order: the first launch writes `.gov-runtime/launches` (the launch record folder, W2-60a S8); the second launch's list then has `Edit(<P>/.gov-runtime/launches)` among the `.gov-runtime` entries that the launcher lists from the folder's present contents, where the first launch had it at the end beside `Edit(<P>/.gov-runtime/launches/**)` (`record.deny_rules`). See `launcher.py` around line 476 (`list(dict.fromkeys(deny + record.deny_rules(records) + user_rules["deny"]))`) and the `.gov-runtime` deny builder around line 167.

Fix: the deny list must be the same on every launch, whether or not the record folder exists yet: the same rules, in the same order, each once. The smallest form is likely to leave the record folder's name out of the `.gov-runtime` listing (its two rules come from `record.deny_rules` always); check that the folder is still denied by both literal rules once each (S8: "the folder denied by two literal `Edit` rules once each and not on the write list"). Add a unit case: two builds, before and after the folder exists, give equal deny lists.

## Verify, then return

Run `tests/acceptance/W2-56/test_w2_56_sandbox_block.py`, `tests/unit/launch` and `tests/acceptance/W2-60a` (each its own run). Return the twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line: the sandbox check, the counts per run, every red named, the guard refusals met (count), and your commit's hash and trailers.
