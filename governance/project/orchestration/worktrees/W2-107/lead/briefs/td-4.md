# Brief: independent test designer, W2-107 (DAEO-kiar), profile FULL: resume, one older case revised (DEC-970, P-W2-107-2 (a))

You are a fresh independent test designer (MR-3). Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-107-tests` on branch `w2/W2-107-tests` (DEC-963). You never write in the ticket's own worktree `/home/usain/gov-os-worktrees/W2-107`. You revise one case of an earlier ticket's suite (W1-16) under a decision the owner's CTO has made, described below.

## Step 0, before any work (report it first in your return)

You run outside the sandbox, because the case you run needs the code-graph daemon (the sandbox mounts its folder read-only), so step 0 is the identity check only: run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107-tests` and `w2/W2-107-tests`). If anything differs, stop and say so. Write nothing outside your worktree, except your session's own scratchpad and pytest's own temp folders.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground for more than ten minutes for one command.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; never write there). Never the ticket worktree's store. For what changed on `w2/integrate` since that store was built, `git show w2/integrate:<path>`. **Never one giant query or context (DEC-860):** batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `tests/unit/secrets/test_w2_107*`, `tests/unit/secrets_check/test_w2_107*`), and name in your return any such result you were served.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) this ticket's implementation: you never read the files the ticket branch changes against its base (`git -C /home/usain/gov-os-worktrees/W2-107 diff --name-only w2/integrate...w2/W2-107` names them), other than the acceptance tests; read existing code as it stands on `w2/integrate` (`git show w2/integrate:<path>`);** (d) the hidden half of any evaluation set, by whoever is measured by it. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never another form; search named folders instead. Count every refusal and list each in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document (`<<EOF`), no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths. A helper or throwaway script goes in your session's own scratchpad. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard refuses the write you need (the W1-16 file is not in the ticket's `allowed_paths`; the ticket's body names it for you), return it as a package with the refusal's exact text; never another form.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (For you, `<this worktree>` is `/home/usain/gov-os-worktrees/W2-107-tests`.)
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Protected material and copies:** no copy of the tree (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); tests that need a repository build a temporary one. Install nothing. No subagents that write. Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here.
- **Your budget (DEC-898):** 3 GB and 100,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-107` on every run; pytest's own retention with `-o tmp_path_retention_policy=failed`, never a per-run `--basetemp`. Remove what you make as soon as it is no longer needed.

## What you read

- The ticket file `.tickets/DAEO-kiar.md`: its first KPI line names the cache's one place, `~/.cache/gov-os/secrets-scan.sqlite`, outside every repository; its body names your task.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-970 (its W2-107 line: P-W2-107-2 (a)), DEC-967, DEC-966 item 4, DEC-866, DEC-491, DEC-462; and `governance/project/orchestration/packages/P-SPEED-1.md` §4.
- W1-16's suite: `tests/acceptance/W1-16/test_w1_16_home.py`, its `w1_16_support.py`, `conftest.py` and `README.md`.

## Your task

`tests/acceptance/W1-16/test_w1_16_home.py::test_no_index_file_exists_outside_gov_runtime_after_a_run` sweeps for index files (SQLite files, their side files, graph dumps) everywhere a child process could write, its temporary HOME included. Since W2-107, the product remembers clean gitleaks verdicts in one machine-wide cache at `<HOME>/.cache/gov-os/secrets-scan.sqlite` (SQLite, hashes and verdicts only), so under the child's HOME that file, and SQLite's `-wal` and `-shm` side files beside it, appear after a run, and the case fails. The owner's approved design puts the cache there (DEC-967); the CTO decided (DEC-970, P-W2-107-2 (a)) that the case is revised to leave out **exactly** that file and its `-wal` and `-shm`, and nothing else.

What you do:
- Revise only that case (and, if it is the cleaner form, a helper of W1-16's support that only this case uses; if another case uses the helper, give this case its own exclusion instead) so that, under each place the case sweeps, exactly `<that place's HOME>/.cache/gov-os/secrets-scan.sqlite`, `…-wal` and `…-shm` are left out, and only when that place is the child's HOME (or holds it at that relative path). Any other SQLite file anywhere, another file in `.cache/gov-os/`, or a file of that name anywhere else, still fails the case. Lower no other expectation, in this case or any other.
- Update W1-16's README where it describes this case, in a line, citing DEC-970 and DEC-967.
- Run the case to its end, never with `-x`: `cd /home/usain/gov-os-worktrees/W2-107-tests && TMPDIR=/tmp/gov-os-lead-W2-107 PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest "tests/acceptance/W1-16/test_w1_16_home.py" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs` (the whole file, which shares the run's fixtures; it starts the code-graph daemon). Report its counts; every case of the file must pass. This worktree's `src/` holds the ticket's code, so the cache really appears in the child's HOME: say in your return whether you saw it (by listing names only, from a throwaway check in your scratchpad if you need one; never by reading the ticket's code).
- Collection stays clean: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests/acceptance/W1-16 --collect-only -q -p no:cacheprovider --no-header` (quote its last line).
- A dispute (you think the decision cannot be met without lowering another expectation) is a package, never a guess.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds only `*.sample` files (if a `pre-commit` file is there, stop and return). Then:

    git commit -m "W1-16: the home sweep leaves out exactly the secrets scan cache and its -wal/-shm (DEC-970, P-W2-107-2 (a))" --trailer "Task: DAEO-kiar" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-970, DEC-967, DEC-966" --trailer "Rewrite-Reason: DEC-967" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Never `--no-verify`, never `core.hooksPath`. After the commit, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); what you changed and why, in a few lines; the file's counts; whether the cache appeared in the child's HOME; the `gov.__file__` line; the collection's last line; every guard refusal (time, the command's form, the reason given); whether you used `gov retrieve`; any package.

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
