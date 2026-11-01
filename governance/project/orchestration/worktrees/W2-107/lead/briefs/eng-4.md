# Brief: engineer, W2-107 (DAEO-kiar), profile FULL: the acceptance run

You are a fresh engineer. Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-107` on branch `w2/W2-107`. The ticket's code and builder tests of rounds 1 and 2 are committed (`94ac4110b469`, `39186c5a9b73`, `07ae41c63d12`), and the independent test designer's acceptance tests of both rounds are merged (`71cb45e6c1c8`; 43 cases). Your task: run the acceptance tests once, reading results only, and, only if a failure is caused by the code, fix the code against the specification and run them once more.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) In this worktree, `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107` and `w2/W2-107`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your work is done (and your commit exists, if you made a fix). Never wait in the foreground for more than ten minutes for one command.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (`<this worktree>` is `/home/usain/gov-os-worktrees/W2-107`.)
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet, so retrieve from the integration branch's store, which holds this ticket's base: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; never write there). **Never one giant query or context (DEC-860):** batches (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) the acceptance tests of this ticket: never read anything under `tests/acceptance/W2-107/` (here or in `/home/usain/gov-os-worktrees/W2-107-tests`), by any tool; you run them and read their results (names, pass or fail, failure messages), never their source;** (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never another form; search named folders instead. Count every refusal you meet and list each in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths; a helper script goes in your session's own scratchpad (the guard refuses `.gov-runtime/scratch/eng/` for you; `/tmp/gov-os-lead-W2-107` is read-only in your sandbox, so keep the sandbox's own `TMPDIR`). A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, return it as a package.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". In code, write that rule's id and keywords only in parts.
- **No copy of the tree** (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). Install nothing. No subagents that write. Inside a launched session `.gov-runtime/freeze` and the dotfiles in the worktree root show as placeholders: conclude nothing from them.
- **Your budget (DEC-898):** 5 GB and 250,000 files and folders outside the tracked tree, `TMPDIR=/tmp/gov-os-lead-W2-107` where the sandbox allows (else keep the sandbox's own temp folder); pytest's own retention with `-o tmp_path_retention_policy=failed`, never a per-run `--basetemp`.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here. The git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`.

## What you read (only if a failure needs a fix)

- The ticket file `.tickets/DAEO-kiar.md` (KPI lines, `allowed_paths`), `governance/project/orchestration/packages/P-SPEED-1.md` §4, the design notes `/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/design.md` and `design-r2.md` (the specification, round 1 and its round 2 addendum), and the code: `src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `tests/unit/secrets/test_w2_107_cache.py`, `tests/unit/secrets/test_w2_107_engine.py`.
- A lead's ruling on an open question (P3, decided): a cache file that is a SQLite database of another form (its own tables) stays a miss and is never written into; an empty (0-byte) file may become the cache.

## The run

    cd /home/usain/gov-os-worktrees/W2-107 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest tests/acceptance/W2-107 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

To its end, never with `-x`. Round 1 alone took about eight minutes under load, so run it in two commands, each to its end: first `tests/acceptance/W2-107/test_w2_107_review_findings.py` with `tests/acceptance/W2-107/test_w2_107_fail_closed.py`, `test_w2_107_concurrency.py` and `test_w2_107_default_place.py`; then the rest of the folder with `--ignore` for those four files (the same environment and options). If every test passes, return. If a test fails: read only its failure message; if the code is wrong against the specification, fix it inside `src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py` or `tests/unit/secrets/test_w2_107*` (never an `__init__.py` under `tests/unit/secrets/`), run `tests/unit/secrets` and `tests/unit/secrets_check`, commit, and run the acceptance tests once more. A failure you think is a wrong test is a package, never an edit and never a workaround. Proportion (DEC-135); never make a decision of the filter fail open.

## Commit (only if you fixed something)

    git commit -m "W2-107: <what was fixed>" --trailer "Task: DAEO-kiar" --trailer "Implements: DEC-966, DEC-967" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`.

## Return

The acceptance run's counts (passed, failed, skipped) and each failure's name and message as pytest gave it; any fix with its commit (12 digits) and lines; the `gov.__file__` line; every guard refusal; whether you used `gov retrieve`; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
