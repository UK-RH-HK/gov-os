# Brief: engineer, W2-107 (DAEO-kiar), profile FULL: resume, the unit files moved (DEC-970, P-W2-107-1 (a)), then the acceptance run

You are a fresh engineer. Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-107` on branch `w2/W2-107`. The ticket's code, builder tests and acceptance tests are committed; its review has passed. Two things are left for you: move the two builder test files to the ticket's new unit path, and run the acceptance tests once, reading results only.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) In this worktree, `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107` and `w2/W2-107`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your work is done and your commit exists. Never wait in the foreground for more than ten minutes for one command.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (`<this worktree>` is `/home/usain/gov-os-worktrees/W2-107`.)
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m gov.cli.main retrieve "<question>" --json` in this worktree. **Never one giant query or context (DEC-860):** batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) the acceptance tests of this ticket: never read anything under `tests/acceptance/W2-107/` (here or in `/home/usain/gov-os-worktrees/W2-107-tests`), by any tool; you run them and read their results (names, pass or fail, failure messages), never their source;** (d) the hidden half of any evaluation set, by whoever is measured by it. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never another form; search named folders instead. Count every refusal you meet and list each in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths; a helper script goes in your session's own scratchpad (`/tmp/gov-os-lead-W2-107` is read-only in your sandbox, so keep the sandbox's own `TMPDIR`). A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, return it as a package with the refusal's exact text.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **No copy of the tree** (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). Install nothing. No subagents that write. Inside a launched session `.gov-runtime/freeze` and the dotfiles in the worktree root show as placeholders: conclude nothing from them.
- **Your budget (DEC-898):** 3 GB and 100,000 files and folders outside the tracked tree, the sandbox's own `TMPDIR`; pytest's own retention with `-o tmp_path_retention_policy=failed`, never a per-run `--basetemp`. Remove what you make as soon as it is no longer needed.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here.

## What you read

- The ticket file `.tickets/DAEO-kiar.md` (its `allowed_paths` and its body's DEC-970 line), and DEC-970's W2-107 line in `docs/DECISION_REGISTER.md`.
- `tests/acceptance/W2-69/test_w2_69_unit_folder_renamed.py` is another ticket's test you may read: its case `test_the_unit_folder_named_secrets_is_gone` requires that `tests/unit/secrets/` does not exist at all (a test package named `secrets` shadows the standard library's).
- The two builder test files `tests/unit/secrets/test_w2_107_cache.py` and `tests/unit/secrets/test_w2_107_engine.py`, and the folder they go to, `tests/unit/secrets_check/` (it has an `__init__.py`; the old folder had none).

## Your task

1. Move the two files with git: `git mv tests/unit/secrets/test_w2_107_cache.py tests/unit/secrets_check/test_w2_107_cache.py` and the same for `test_w2_107_engine.py`. Change their content only where the move needs it (a path, an import or a module name that depended on the old folder); say what, if anything.
2. Make `tests/unit/secrets/` disappear from the working tree: after the move, only an ignored `__pycache__/` is left in it. Remove it with `rm -r /home/usain/gov-os-worktrees/W2-107/tests/unit/secrets/__pycache__` and then `rmdir /home/usain/gov-os-worktrees/W2-107/tests/unit/secrets`. If either is refused (by the guard, the sandbox or a permission prompt), take it, never another form, and name the refusal and what is left in your return.
3. Run the builder tests to their end: `cd /home/usain/gov-os-worktrees/W2-107 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest tests/unit/secrets_check -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`, and W2-69's suite: the same with `tests/acceptance/W2-69/test_w2_69_unit_folder_renamed.py`. Quote the counts.
4. Check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds only `*.sample` files (if a `pre-commit` file is there, stop and return), then commit:

        git commit -m "W2-107: the builder tests move to tests/unit/secrets_check/ (DEC-970, P-W2-107-1 (a))" --trailer "Task: DAEO-kiar" --trailer "Implements: DEC-970, DEC-966, DEC-967" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

    Never `--no-verify`, never `core.hooksPath`. Then `git log --oneline -2` and `git status --short`.
5. Run this ticket's acceptance tests once, reading results only, to their end, never with `-x`, in two commands (the whole folder took about eight minutes under load): first `cd /home/usain/gov-os-worktrees/W2-107 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest tests/acceptance/W2-107/test_w2_107_review_findings.py tests/acceptance/W2-107/test_w2_107_fail_closed.py tests/acceptance/W2-107/test_w2_107_concurrency.py tests/acceptance/W2-107/test_w2_107_default_place.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`; then `tests/acceptance/W2-107` with `--ignore` for those four files (the same environment and options). 43 cases are expected to pass. A failure: quote its name and message as pytest gave it, change nothing, and return; a failure you think is a wrong test is a package, never an edit. Never make a decision of the filter fail open.

## Return

Step 0's result; your commit (12 digits) and what moved; whether `tests/unit/secrets/` is gone; the builder, W2-69 and acceptance counts (passed, failed, skipped) with each failure's name and message; the `gov.__file__` line; every guard refusal (time, the command's form, the reason given); whether you used `gov retrieve`; any package.

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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
