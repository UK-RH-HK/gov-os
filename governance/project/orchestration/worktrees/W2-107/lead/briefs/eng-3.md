# Brief: engineer, W2-107 (DAEO-kiar), profile FULL: round 2 (the review's findings)

You are a fresh engineer. Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-107` on branch `w2/W2-107`. Round 1's code and builder tests are committed (`94ac4110b469`, `39186c5a9b73`), the acceptance tests of round 1 are merged and pass (33 of 33). An independent review found behaviours the code gets wrong; they are given below as the specification's round 2 addendum. You build to it (never to the tests); an independent test designer writes the matching acceptance tests in parallel, in its own worktree.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) In this worktree, `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107` and `w2/W2-107`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground for more than ten minutes for one command (run a suite file by file if a whole run would pass that).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no tag; the one merge you make is the tests branch's (below).
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (`<this worktree>` is `/home/usain/gov-os-worktrees/W2-107`.)
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet, so retrieve from the integration branch's store, which holds this ticket's base: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; never write there). **Never one giant query or context (DEC-860):** batches (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) the acceptance tests of this ticket: never read anything under `tests/acceptance/W2-107/` (here or in `/home/usain/gov-os-worktrees/W2-107-tests`), by any tool; you run them and read their results (names, pass or fail, failure messages), never their source;** (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never another form; search named folders instead. Count every refusal and list each in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths; a helper script goes in your session's own scratchpad (the guard refuses `.gov-runtime/scratch/eng/` for you). A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, return it as a package.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". In code and unit tests, write that rule's id and keywords only in parts, and build every planted secret at run time from parts.
- **No copy of the tree** (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); unit tests that need a repository build a temporary one. Install nothing. No subagents that write. Inside a launched session `.gov-runtime/freeze` and the dotfiles in the worktree root show as placeholders: conclude nothing from them.
- **Your budget (DEC-898):** 5 GB and 250,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-107` where the sandbox allows (else the sandbox's own temp folder); pytest's own retention with `-o tmp_path_retention_policy=failed`, never a per-run `--basetemp`.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here. Your unit tests never touch the real `~/.cache/gov-os/`: each sets `GOV_SECRETS_CACHE` to a file in its `tmp_path`. The git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`. After every commit, `git log --oneline -2` and `git status --short`.

## What you read

- The ticket file `.tickets/DAEO-kiar.md`, `governance/project/orchestration/packages/P-SPEED-1.md` §4 (the approved design keys the engine on gitleaks' version string), the round-1 design note (`/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/design.md`), and the addendum below.
- The code: `src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `tests/unit/secrets/test_w2_107_cache.py`, and the existing tests in `tests/unit/secrets_check/` (they patch `subprocess.run` inside `gov.secrets`; under pytest with no named cache no fingerprint is computed, so a version call made only when a cache is in use is never seen by them; keep it that way).
- The decisions: DEC-966 item 4, DEC-911 item 4, DEC-285, DEC-853, DEC-135.

## The design note, round 2 addendum (the specification)

The design note of round 1 stands, with items 3 and 6 extended as follows.

A. **The engine's identity also carries gitleaks' version string.** The fingerprint is a sha256 over the cache format's version, the filter's reading form (B), the sha256 of each rule set, the sha256 of the bytes of the gitleaks that `PATH` finds, **and the version string that gitleaks reports** (`gitleaks version`, run through that same `PATH` entry). So an upgrade behind a wrapper or version-manager shim whose own bytes stay the same (the shim runs whichever release a link or setting names) still changes the fingerprint and forgets every verdict. The version is asked only when a cache is in use (never under pytest without a named cache, never with `GOV_SECRETS_CACHE` empty), at most once per process for each binary as its path and file status identify it. A version that cannot be read (an error, a non-zero exit, no answer in a short time, an empty answer) means no cache for that call: the text is scanned as if there were none, and nothing is written.

B. **The filter's reading form is in the fingerprint.** The filter keeps a version of what a scan reads (how a text is cut into pieces and forms before gitleaks sees it; today the module's `_FORM`, which its docstring calls "the form of the record and of what a scan reads"). That version is part of the fingerprint, so a change to how the filter reads a text, made the module's way (the version raised), forgets every remembered verdict, in every worktree that shares the cache.

C. **One engine per judgement.** The fingerprint is taken once, before the scan, and the same one serves the lookup and the write. After the scan, the verdict is written only if the gitleaks that `PATH` finds is still the same file (the same path, and the same file status: device, inode, size, change and modification times) as before the scan; otherwise nothing is written for that text, so a gitleaks replaced during a scan never has its new identity credited with a verdict an older engine gave.

D. **A cache that can be read but not written still answers.** Every row carries the fingerprint it was judged under, and a read answers only rows of the current fingerprint, so a cache file (or its folder) that is read-only, or a write lock that cannot be had, still answers the current engine's clean verdicts; it writes nothing, clears nothing, and never answers a row of another engine. (Before, a cache that could not be written was never read.)

Unchanged: only clean is remembered; any finding (an exempt commit hash included) never is; every error is a miss; a scan that cannot decide raises; the cache holds no content or path; `indexable` and `path_holds_secret` keep their signatures, order and raising; `scan_counts()` as before; the round-1 acceptance tests keep passing.

Not this round (residuals the lead returns): a gitleaks upgraded behind a shim during one process's run; rule sets evicting each other's verdicts; an extended rule file outside the fingerprint; a held lock's two-second waits; a relative `GOV_SECRETS_CACHE`.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `tests/unit/secrets/test_w2_107*` (never an `__init__.py` under `tests/unit/secrets/`: it would shadow the standard library's `secrets`). Nothing in `src/gov/rebuild/**`, nothing else in `src/`, never `tests/acceptance/**`.
- Builder tests for A to D in `tests/unit/secrets/test_w2_107_*.py`, as regression evidence only (a shim with constant bytes switching releases; a stand-in that replaces itself during its first scan; the reading form raised in-process; a populated cache made read-only).
- Proportion (DEC-135): no code beyond A to D. Never make a decision of the filter fail open. Keep the module's style.

## The acceptance tests arrive while you work (DEC-963)

When `/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/TESTS-READY-2` exists (check it at each step, and again when you have built and committed), run in this worktree:

    git merge --no-ff w2/W2-107-tests -m "Merge w2/W2-107-tests into w2/W2-107: W2-107's acceptance tests for the review's findings" -m "Task: DAEO-kiar
    Role: engineer"

(the second `-m` is the trailer paragraph: two lines, `Task: DAEO-kiar` and `Role: engineer`; git's merge takes no `--trailer`), then run the acceptance tests once, reading results only:

    cd /home/usain/gov-os-worktrees/W2-107 && TMPDIR=/tmp/gov-os-lead-W2-107 PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest tests/acceptance/W2-107 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

A failure you think is a wrong test is a package, never an edit and never a workaround. A failure your code causes is yours to fix against the specification, then one more run. If the file does not exist when you have built, committed and run your tests, return without waiting.

## Commit

Commit your code and unit tests before running any long suite:

    git commit -m "W2-107: the engine's version and reading form in the fingerprint, one engine per judgement, a read-only cache still answers" --trailer "Task: DAEO-kiar" --trailer "Implements: DEC-966, DEC-967" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then run, each to its end, never with `-x`: `tests/unit/secrets`, `tests/unit/secrets_check`, `tests/unit/retrieval`, `tests/unit/codeintel`, and the round-1 acceptance tests (`tests/acceptance/W2-107`, results only), and the collection check `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (quote its last line).

## Return

Your commits (12 digits) with their trailers; the files changed; the lines added and removed; the tests you ran with their counts; the acceptance run's result; the `gov.__file__` line; every guard refusal; whether you used `gov retrieve`; anything you could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
