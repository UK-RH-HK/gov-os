# Brief: engineer, W2-107 (DAEO-kiar), profile FULL: the rebuild record's counts line (DEC-970 P-W2-107-3, DEC-975 item 1)

You are a fresh engineer, started by the orchestrator (the CTO), who acts as this ticket's lead for its last batch. Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-107` on branch `w2/W2-107` (head `d2339a3f`, the integration branch merged in). The ticket's code, builder tests and acceptance tests are committed and verified; its reviews have passed. One change is left for you: the rebuild's JSON record gives the secrets filter's counts. It is the owner's top priority (DEC-975): work steadily, and return as soon as it is done.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) In this worktree, `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107` and `w2/W2-107`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your work is done and your commit exists. Never wait in the foreground for more than ten minutes for one command.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (`<this worktree>` is `/home/usain/gov-os-worktrees/W2-107`.)
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context (DEC-860). A code question (DEC-859) uses the code-graph tool's own traversal, small and targeted.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) this ticket's acceptance tests: never read anything under the acceptance folder `W2-107/` by any tool; you run them and read their results only;** (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`.
- **The guard's command forms:** no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **No copy of the tree.** Install nothing. No subagents that write. Your budget: 3 GB and 100,000 files and folders outside the tracked tree, the sandbox's own `TMPDIR`; `-o tmp_path_retention_policy=failed`. Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here.

## What you read

- The ticket `.tickets/DAEO-kiar.md`: its `allowed_paths` (now with `src/gov/rebuild/command.py`, for this one change only), its success KPI 7 ("The rebuild's record says how many contents and names were scanned and how many were answered from the cache"), and the body's last paragraph ("At merge").
- `src/gov/secrets/__init__.py`: `scan_counts()` (lines 83 to 95: per kind, `scanned` and `remembered`, as a fresh dict; a caller takes the difference around its own work) and `_KINDS`.
- `src/gov/rebuild/command.py` (W2-76's file, merged): the function that ends with `return {"digest": ..., "store": ..., "stores": ..., "compaction": ...}` (about line 201), and how `watch.filtered(...)` wraps the secrets filter in the lexical and code-index stages. `src/gov/rebuild/watch.py` you read, never edit.
- The builder tests in `tests/unit/secrets_check/` (yours to add to, as a new `test_w2_107_record.py`).

## Your task

1. In `src/gov/rebuild/command.py` only: take `gov.secrets.scan_counts()` before the rebuild's first stage that runs the secrets filter and after the last, and add their difference to the returned record as one new key, `"secrets_counts"`, of the same form as `scan_counts()` (per kind, `scanned` and `remembered`). Nothing else in the file changes: no other key, no change of order or form of the existing keys. If the import of `gov.secrets` can fail in a way the rest of the rebuild survives today, the key says so (`{"unavailable": "<reason>"}`) and the rebuild goes on, as it does today. **Check one thing and say what you found:** whether every call of the secrets filter in a rebuild runs in this process (the counts are per process). If a stage runs it in a child process, the counts would miss those texts: say which stage, and do not paper over it.
2. A new builder test file `tests/unit/secrets_check/test_w2_107_record.py`: a rebuild's record holds `secrets_counts` with every kind of `scan_counts()` and both numbers; on an unchanged second rebuild of the same small planted tree, `scanned` falls and `remembered` rises for file contents (use a machine cache path of the test's own, `GOV_SECRETS_CACHE` in the test's environment, never the real `~/.cache/gov-os/`). Keep it small and fast; no embedder (if the rebuild needs one, use the same means the existing builder or W2-76 tests use to run a rebuild without the real embedder; never `--no-embeddings` on a real store).
3. Run to their end and quote the counts: the builder tests `tests/unit/secrets_check`; W2-76's acceptance folder `tests/acceptance/W2-76` (it reads the rebuild record: a new key must not break it; reading its results only is enough, you may read its source since it is not this ticket's); this ticket's acceptance folder in the two commands the README splits it into (`test_w2_107_review_findings.py`, `test_w2_107_fail_closed.py`, `test_w2_107_concurrency.py`, `test_w2_107_default_place.py` first; then the folder with `--ignore` for those four). All with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest <...> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`. A failure: quote its name and message, and if it is not yours, change nothing for it and name it.
4. Check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds only `*.sample` files (if a `pre-commit` file is there, stop and return), then commit both files:

        git commit -m "W2-107: the rebuild's record gives the secrets filter's counts, scanned and remembered per kind (DEC-970 P-W2-107-3, KPI 7)" --trailer "Task: DAEO-kiar" --trailer "Implements: DEC-966, DEC-970, DEC-975" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

    Never `--no-verify`, never `core.hooksPath`. Then `git log --oneline -2`, `git status --short` and `git diff --stat HEAD~1`.

## Return

Step 0's result; your commit (12 digits) and its diff stat; the in-process finding of task 1; the counts of each suite (passed, failed, skipped) with each failure's name and message; the `gov.__file__` line; every guard refusal (time, the command's form, the reason given); whether you used `gov retrieve`; any package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
