# Brief: independent test designer, W2-107 (DAEO-kiar), profile FULL: round 2 (the review's findings)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-107-tests` on branch `w2/W2-107-tests` (DEC-963), which holds this ticket's acceptance tests of round 1 (`83fdd88d43f7`, 33 tests in `tests/acceptance/W2-107/`, with their README). You never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-107`. An independent review of the implementation found behaviours the tests miss; they are given to you below as behaviours (DEC-136). You add the tests that catch them, in parallel with an engineer who fixes them, and you show them red on the ticket's base code.

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

## The design note, round 2 addendum (the specification; behaviour only)

The design note of round 1 stands, with items 3 and 6 extended as follows.

A. **The engine's identity also carries gitleaks' version string.** The fingerprint is a sha256 over the cache format's version, the filter's reading form (B), the sha256 of each rule set, the sha256 of the bytes of the gitleaks that `PATH` finds, **and the version string that gitleaks reports** (`gitleaks version`, run through that same `PATH` entry). So an upgrade behind a wrapper or version-manager shim whose own bytes stay the same (the shim runs whichever release a link or setting names) still changes the fingerprint and forgets every verdict. The version is asked only when a cache is in use (never under pytest without a named cache, never with `GOV_SECRETS_CACHE` empty), at most once per process for each binary as its path and file status identify it. A version that cannot be read (an error, a non-zero exit, no answer in a short time, an empty answer) means no cache for that call: the text is scanned as if there were none, and nothing is written.

B. **The filter's reading form is in the fingerprint.** The filter keeps a version of what a scan reads (how a text is cut into pieces and forms before gitleaks sees it; today the module's `_FORM`, which its docstring calls "the form of the record and of what a scan reads"). That version is part of the fingerprint, so a change to how the filter reads a text, made the module's way (the version raised), forgets every remembered verdict, in every worktree that shares the cache.

C. **One engine per judgement.** The fingerprint is taken once, before the scan, and the same one serves the lookup and the write. After the scan, the verdict is written only if the gitleaks that `PATH` finds is still the same file (the same path, and the same file status: device, inode, size, change and modification times) as before the scan; otherwise nothing is written for that text, so a gitleaks replaced during a scan never has its new identity credited with a verdict an older engine gave.

D. **A cache that can be read but not written still answers.** Every row carries the fingerprint it was judged under, and a read answers only rows of the current fingerprint, so a cache file (or its folder) that is read-only, or a write lock that cannot be had, still answers the current engine's clean verdicts; it writes nothing, clears nothing, and never answers a row of another engine. (Before, a cache that could not be written was never read.)

Unchanged: only clean is remembered; any finding (an exempt commit hash included) never is; every error is a miss; a scan that cannot decide raises; the cache holds no content or path; `indexable` and `path_holds_secret` keep their signatures, order and raising; `scan_counts()` as before.

## The behaviours to test (from the review, as behaviours)

1. **An upgrade behind a shim (A).** `gitleaks` first on `PATH` is a shim whose own bytes never change and which runs whichever "release" a link or a setting file next to it names. Release one stands for an older gitleaks that does not know a rule (for example, it answers every scan as gitleaks would but never reports the planted secret, and reports its own version string); release two is the real gitleaks (it reports the real version). A file holding the planted secret is filtered with a cache under release one (let through, remembered clean), then the shim is switched to release two and the file is filtered again, in a fresh process: it must be scanned again and dropped, and every remembered text rescanned. Also: a gitleaks whose version cannot be read (non-zero exit or empty answer for `version`, scans normal) gets correct verdicts with every text scanned, every time, and nothing remembered.
2. **A gitleaks replaced during a scan (C).** A plain stand-in first on `PATH` that, during its first scan call, replaces the file at its own `PATH` place by a rename with another engine (a different file, as an upgrade landing while a rebuild runs), then answers. Nothing judged during that switch is remembered: a later call (in a fresh process, under the new engine) scans that text again, and a planted secret only the new engine knows is dropped.
3. **A change of the filter's reading form (B).** A text remembered clean, then the filter's reading form raised the module's way (the constant named above, on the module the tests import, in-process), must be scanned again (and every other remembered text with it). If you judge that this can only be reached through a private name, say so in the README and in your return; the engineer's builder test then covers it, and you still add the test if the constant is the documented convention.
4. **A read-only cache still answers (D).** A cache populated by one call, then made read-only (the file, and in a second case its folder), answers the current engine's clean texts on the next call (no scan for them), writes nothing (the file's bytes unchanged), and never answers a text remembered under another engine (a different stand-in first on `PATH` scans everything and the read-only cache stays as it was).

Each test fails on the ticket's base code for a reason the README states, or is named a guard with why. The round-1 tests stay as they are; if one of them must change (for example a stand-in that must also answer `version`), change only that, lower no other expectation, and say so.

## What you write

- Only inside `tests/acceptance/W2-107/`: new tests (a new file, for example `test_w2_107_review_findings.py`) and the README's new rows (each finding to its tests and red reason). No `__init__.py` named `secrets`; no module named after a standard-library module.
- **Red first:** run the new tests, and then the whole folder once, to their end, never with `-x`: `cd /home/usain/gov-os-worktrees/W2-107-tests && TMPDIR=/tmp/gov-os-lead-W2-107 PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests/acceptance/W2-107 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`. Collection stays clean: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (quote its last line).
- An ambiguous behaviour or a dispute is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), never a guess.

## Commit

Commit only your test paths, with the trailers in the final block. These tests come after the implementation began (DEC-491), so the commit carries the reason:

    git commit -m "W2-107: acceptance tests for the review's findings (a shim upgrade, a mid-scan upgrade, the reading form, a read-only cache)" --trailer "Task: DAEO-kiar" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-966, DEC-967" --trailer "Rewrite-Reason: the FULL review's findings F-1 to F-3 and R-1, given as behaviours (DEC-136, DEC-413)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`. After the commit, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the new test count and names; each behaviour with its tests; the red reasons as you saw them (counts), and the whole folder's counts on the base; any round-1 test you changed, with why; the `gov.__file__` line; the collection's last line; every guard refusal; whether you used `gov retrieve`, and any result under the implementation paths you were served; any package.

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
