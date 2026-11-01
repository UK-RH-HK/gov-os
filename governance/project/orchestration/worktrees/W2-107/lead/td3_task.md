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
