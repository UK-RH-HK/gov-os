Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

You are a fresh Engineer. Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2, run 7, fix iteration 3 (the last). The narrow independent check of run 7 failed S27 on one blocker, P1-1, below. You are given that failing output only. You work only in the ticket's worktree `/home/usain/gov-os-worktrees/W2-88` (branch `w2/W2-88`, head ef9c773c3 at your start; the lead may merge a test-design revision into it while you work, touching only `tests/acceptance/W2-88/`). You never read the acceptance tests (DEC-820). Budget: about 1 hour, one commit.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-2bdu`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-88`, `w2/W2-88`). If anything differs, stop and say so.

## Allowed paths
`src/gov/secrets/__init__.py`, `tests/unit/secrets/test_w2_88*`, `docs/changes/W2-88-evidence.md`. Anything else: name it in your return, do not change it.

## The failing output (the narrow check's finding P1-1, success-27, blocker; `.gov-runtime/scratch/lead/log/nc-3.review.md`)
- **What is wrong:** File A ends with a bare generic key, such as `password:` on its last line or `token =` with no value. The next file in the batch, B, starts with a secret that only gitleaks' `generic-api-key` rule catches (for example `API_KEY=<value>` on its first line). gitleaks then reports one match from A's line 4 to B's line 7: its `\s` classes cross the blank-line separator, and the match swallows B's own match. `_scan_batch` puts the finding back only on its StartLine (A). A is re-judged alone and is clean. B is in no owner set, so it is judged clean, kept as indexable, and written to the reuse record as `scanned` clean.
- **Reproduced by the checker:** a pair probe gave `MISMATCH ['tail_key', 'generic_env'] batch [False, False] alone [False, True] owners [0]`, plus 3 more variants; end to end on 12 planted files, a23678e27 keeps 11 of 12 and leaves out `config/11-prod.env`, the head keeps 12 of 12; line span `('generic-api-key', 4, 7)`, with A on lines 2 to 6 and B starting at line 7.
- **Behaviour it should have:** the one-per-file form's verdict, always. A finding is put back on **every** file its StartLine to EndLine covers, and each is judged alone; the checker also offers "the file after an owner whose alone scan comes back clean is judged alone": do whichever makes the verdict equal the one-per-file form's for every pair (both, if one alone leaves a case). The records written as clean by run 7's batching are never reused: change the reuse record's form key (`_FORM`, or what keys it) so every record the batched scan wrote before this fix is ignored. A file a finding names is already re-judged alone, so the fix costs little speed: re-measure the 5,000-file tree (as `docs/changes/W2-88-evidence.md` "Run 7" did, a23678e27's code against yours, same slot) and update the figures there; S27's line is at least 10 times.

## The work
1. Unit tests first in `tests/unit/secrets/test_w2_88_scan.py` (red, then green): the shadowing pair in both orders and with each rule form you can make (`password:` / `token =` / `secret:` bare at A's end; B's first line a generic key; a batch of more than two, the pair in the middle), the verdict equal to the one-per-file form's per file; a record written under the old form key is not reused. Planted secrets built from parts in your tmp; never print a value.
2. The fix in `src/gov/secrets/__init__.py`. Then run `tests/unit/secrets`, `tests/unit/secrets_check` and `tests/unit/adopt` (the known red `tests/unit/adopt/test_safety.py::test_s1_a_stage_writes_nothing_over_an_untracked_file` stays), and the re-measure. Commit once.

## How to run
`env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=<a subfolder of the sandbox's own $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/secrets tests/unit/secrets_check tests/unit/adopt -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`. A resource gate's refusal is a wait. Never `-x`.

## Rules
- Write files with the Write and Edit tools and absolute paths. Scripts only under a subfolder of the sandbox's own `$TMPDIR` (never `.gov-runtime/scratch/eng/`). No here-document, no backticks, no `bash -c '…'`. **Refused twice for the same call: stop and say so** (DEC-1142 (9)).
- Before the commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file and `git status` shows no merge in progress. Never `--no-verify`, amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-2bdu" --trailer "Role: engineer" --trailer "Implements: DEC-954, CAP-44.b, CAP-44.f, CAP-17" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`.
- Never run `gov adopt`, `gov rebuild`, `gov close` against a real repository; install nothing on the machine; never ask the owner.

## Return
One message, your last. The twelve fields first, each a labelled line; then where the fix is (path:line), the unit counts, the S27 figures before and after with the ratio, the sandbox check, your commit (12-digit hash and subject).
```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
Refused twice for the same call: stop and say so.
