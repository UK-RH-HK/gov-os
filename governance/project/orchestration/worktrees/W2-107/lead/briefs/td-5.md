# Brief: independent test designer, W2-107 (DAEO-kiar), profile FULL: one older case revised (DEC-978, as P-W2-107-2 (a))

You are a fresh independent test designer (MR-3), started by the orchestrator (the CTO), who acts as this ticket's lead for its last batch. Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-107-tests` on branch `w2/W2-107-tests` (DEC-963). You never write in the ticket's own worktree `/home/usain/gov-os-worktrees/W2-107`. You revise one case of an earlier ticket's suite (W1-27) under a decision the CTO has made (DEC-978), the same remedy DEC-970's P-W2-107-2 (a) applied to W1-16's home case this morning. It is the owner's top priority (DEC-975): work steadily and return as soon as it is done.

## Step 0, before any work (report it first in your return)

You run outside the sandbox, because the case you run starts a rebuild whose code index needs the code-graph daemon (the sandbox mounts its folder read-only), so step 0 is the identity check only: run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107-tests` and `w2/W2-107-tests`). If anything differs, stop and say so. Write nothing outside your worktree, except your session's own scratchpad and pytest's own temp folders.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message. Return only after your commit exists. Never wait in the foreground for more than ten minutes for one command.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **Retrieval (DEC-963, DEC-836):** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` only (the integration branch's store, a read), in batches (DEC-860). **P-R1:** drop unread any result under this ticket's implementation paths (`src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `src/gov/rebuild/command.py`, `tests/unit/secrets_check/test_w2_107*`), and name any such result you were served.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) this ticket's implementation: never read the files the ticket's branch changed (those four paths above); read existing code as it stands on the integration branch before W2-107 (`git show 789513df655c:<path>`);** (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`. Take a guard refusal as a refusal, never another form; count each and list it. Never read `.claude/settings.json`.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths. A throwaway script goes in your session's own scratchpad. **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard refuses the write you need (the W1-27 file is not in the ticket's `allowed_paths`; the ticket's body names it for you, "W1-27 (DEC-978)"), return it as a package with the refusal's exact text.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (For you, `<this worktree>` is `/home/usain/gov-os-worktrees/W2-107-tests`.)
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- No copy of the tree; tests that need a repository build a temporary one. Install nothing. No subagents that write. Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here (the case's own rebuild in its temporary project is the test's, not yours).
- **Budget:** 3 GB and 100,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-107` on every run (make it if missing); `-o tmp_path_retention_policy=failed`. Remove what you make when done.

## What you read

- The ticket `.tickets/DAEO-kiar.md`: its first KPI line names the cache's one place, `~/.cache/gov-os/secrets-scan.sqlite`, outside every repository; its body's "W1-27 (DEC-978)" paragraph is your task.
- In `docs/DECISION_REGISTER.md`: DEC-978, DEC-970 (its W2-107 line), DEC-967, DEC-966 item 4.
- W1-27's suite: `tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py`, its support files and its `README.md`.
- For the form this morning's designer used, W1-16's revised case: `git show 50f10962609a` (the commit, an acceptance test; open to read).

## Your task

`test_the_mode_writes_only_under_gov_runtime` in that file asserts that the rebuild's no-embeddings mode writes nothing in the home it is given. Since W2-107, a rebuild creates the machine-wide secrets cache in that home. The close saw, word for word: "AssertionError: the mode wrote in the home it was given: created: .cache / created: .cache/gov-os / created: .cache/gov-os/secrets-scan.sqlite". The owner's approved design puts the cache there (DEC-967), and DEC-978 decides the case is revised to leave out **exactly** that cache, and nothing else:

- Under the home the case gives, leave out exactly `.cache/gov-os/secrets-scan.sqlite`, `.cache/gov-os/secrets-scan.sqlite-wal` and `.cache/gov-os/secrets-scan.sqlite-shm`, and the folders `.cache` and `.cache/gov-os` only where they hold nothing but those (and each other). Any other file or folder written in that home (another file in `.cache/gov-os/`, a file of that name anywhere else, a `-journal` file, anything under `.cache/` but `gov-os/`) still fails the case. Lower no other expectation, in this case or any other; the rest of the file is unchanged.
- Plant near misses in a throwaway check of your own (your scratchpad) or as cases, as this morning's designer did, and show that each still fails the assertion: another file in `.cache/gov-os/`, a `-journal` beside the cache, the same name under another folder of the home.
- Update W1-27's README where it describes this case, in a line, citing DEC-978 and DEC-967.
- Run the whole file to its end, never with `-x`: `cd /home/usain/gov-os-worktrees/W2-107-tests && TMPDIR=/tmp/gov-os-lead-W2-107 PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`. Every case must pass. Then W1-16's home file the same way (`tests/acceptance/W1-16/test_w1_16_home.py`), to show this morning's revision still holds. Report both counts.
- Collection stays clean: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests/acceptance/W1-27 --collect-only -q -p no:cacheprovider --no-header` (quote its last line).
- A dispute (you think the decision cannot be met without lowering another expectation) is a package, never a guess.

## Commit

Check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds only `*.sample` files (if a `pre-commit` file is there, stop and return). Then:

    git commit -m "W1-27: the no-embeddings mode's home check leaves out exactly the secrets scan cache (DEC-978, as P-W2-107-2 (a))" --trailer "Task: DAEO-kiar" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-978, DEC-970, DEC-967" --trailer "Rewrite-Reason: DEC-967" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Never `--no-verify`, never `core.hooksPath`. After the commit, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); what you changed and why, in a few lines; the near misses and their results; both files' counts; the `gov.__file__` line; the collection's last line; every guard refusal (time, the command's form, the reason given); whether you used `gov retrieve`; any package.

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

Refused twice for the same call: stop and say so.
