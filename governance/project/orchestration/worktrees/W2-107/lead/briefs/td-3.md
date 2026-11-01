# Brief: independent test designer, W2-107 (DAEO-kiar), profile FULL: round 2, one case revised

You are a fresh independent test designer (MR-3). Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-107-tests` on branch `w2/W2-107-tests` (DEC-963), which holds this ticket's acceptance tests of round 1 (`83fdd88d43f7`, 33 tests in `tests/acceptance/W2-107/`, with their README). You never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-107`. You revise one case of round 2 whose premise does not hold, described below.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) In your worktree, `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside your worktree (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107-tests` and `w2/W2-107-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground for more than ten minutes for one command (run the suite file by file if a whole run would pass that).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store. For what changed on `w2/integrate` since that store was built, `git show w2/integrate:<path>`. **Never one giant query or context (DEC-860):** batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never the whole graph. **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `tests/unit/secrets/test_w2_107*`), and name in your return any such result you were served.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) this ticket's implementation: you never read the files the ticket branch changes against its base (`git -C /home/usain/gov-os-worktrees/W2-107 diff --name-only w2/integrate...w2/W2-107` names them), other than your own tests; read the existing code as it stands on `w2/integrate` (`git show w2/integrate:src/gov/secrets/__init__.py`), never the ticket worktree's copy;** (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never another form; search named folders instead. Count every refusal and list each in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document (`<<EOF`), no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths. The guard refuses `.gov-runtime/scratch/td/` for you: a helper or throwaway script goes in your session's own scratchpad. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, return it as a package.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (For you, `<this worktree>` is `/home/usain/gov-os-worktrees/W2-107-tests`; your tests keep importing `gov` from whatever `PYTHONPATH` the run gives.)
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". In test files, write that rule's id and keywords only in parts, and build every planted secret at run time from parts.
- **No copy of the tree;** a test that needs a repository builds a temporary one in `tmp_path`. Inside a launched session `.gov-runtime/freeze` and the dotfiles in the worktree root show as placeholders: conclude nothing from them. Install nothing. No subagents that write.
- **Your budget (DEC-898):** 5 GB and 250,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-107` where the sandbox allows (else the sandbox's own temp folder); pytest's own retention with `-o tmp_path_retention_policy=failed`, never a per-run `--basetemp`. Remove what you make as soon as it is no longer needed.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here; your tests do not run `gov rebuild`. Every test sets `GOV_SECRETS_CACHE` to a file in its own `tmp_path` and never touches `~/.cache/gov-os/`.

## What you read

- Your own tests of round 1 and their README (`tests/acceptance/W2-107/`), the ticket file `.tickets/DAEO-kiar.md`, `governance/project/orchestration/packages/P-SPEED-1.md` §4, and the design note of round 1, which your README already follows. The decisions: DEC-966 item 4, DEC-911 item 4, DEC-285, DEC-136, DEC-413, DEC-491, DEC-462.
- The existing code on `w2/integrate` only (`git show w2/integrate:src/gov/secrets/__init__.py`): it holds the filter's reading form, the module constant the docstring calls "the form of the record and of what a scan reads".
- A lead's ruling from round 1 (P3, decided as you recommended): a SQLite file of another form at the cache's place stays a miss and is never written into; an empty file may become the cache.

## Your task: one test of round 2 whose premise does not hold

The tests worktree's branch holds both rounds of this ticket's acceptance tests (`4f94f5bf5b68`). Run against the implementation, 42 of the 43 cases pass; one fails:

    tests/acceptance/W2-107/test_w2_107_review_findings.py::test_a_cache_whose_write_lock_is_held_elsewhere_still_answers_its_clean_texts
    test_w2_107_review_findings.py:420: AssertionError: nothing is written while the lock is held elsewhere
    assert b"SQLite form...30e0e3cbclean" == b"SQLite form...30e0e3cbclean"; At index 8196 diff: b'\x04' != b'\x03'

Every assertion before it passed (no error, the verdicts right, the calls as expected, the time within the limit).

**The lead's reading of the test (a described behaviour, not code):** the case takes the write lock on the cache with one connection, then, in the same process, reads the cache file's bytes (a whole-file open and close) to keep a snapshot. On POSIX, closing any descriptor of a file cancels every advisory lock the process holds on that file, the holding connection's included; SQLite documents this as a hazard ("How To Corrupt An SQLite Database File", the section on POSIX advisory locks cancelled by close()). So, from that read on, no write lock is held, and the child may write: the bytes differ because the lock the case means to hold is no longer there, not because the filter wrote through a held lock. The design note D asks that a cache whose write lock cannot be had still answers and writes nothing; it says nothing of a cache whose lock was dropped.

**What you do:** keep the case's intent (a write lock really held by another connection for the whole of the child's run; the remembered texts answered; nothing written meanwhile) and change only how it is set up or observed, so the lock is never dropped by the case itself: for example, take the snapshot before the lock, or read the bytes from another process, or observe "nothing written" another way that opens no descriptor of the cache in the holder's process while the lock is held. Lower no other expectation. Check, with plain SQLite in your scratchpad (no `gov` code), that your form really keeps the lock held for the child's run (a plain writer in a child process is refused throughout). Then run the changed case, the file `test_w2_107_review_findings.py`, on the base code (it fails for the README's stated reason, or is named a guard), and update the README's line for it if its red reason changes.

## What you write

- Only `tests/acceptance/W2-107/test_w2_107_review_findings.py` (that case, and a helper of your own if you need one) and, if needed, the README's line for it.
- Run, to its end, never with `-x`: `cd /home/usain/gov-os-worktrees/W2-107-tests && PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests/acceptance/W2-107/test_w2_107_review_findings.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs` (the sandbox's own `TMPDIR`). Collection stays clean: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (quote its last line).
- A dispute (you think the case's premise did hold) is a package, never a guess.

## Commit

    git commit -m "W2-107: the held-lock case keeps its lock held (no read of the cache in the holder's process)" --trailer "Task: DAEO-kiar" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-966, DEC-967" --trailer "Rewrite-Reason: the case's own read of the cache file dropped the lock it holds (POSIX close cancels the process's locks), so its premise did not hold" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`. After the commit, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); what you changed and why; the plain-SQLite check's result; the file's counts on the base; the `gov.__file__` line; the collection's last line; every guard refusal; whether you used `gov retrieve`; any package.

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
