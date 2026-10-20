# Brief: independent test designer — DAEO-kl5e (W2-50), FULL: acceptance tests for the secrets scan's size, pool and reuse (DEC-853)

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `c2b094da` or later. The ticket's earlier rounds are implemented and their acceptance suite `tests/acceptance/W2-50/` (613 cases, all green) stays as it is. The owner has added one more behaviour to this ticket (DEC-853, 2026-10-19): the secrets-indexing check must finish on stores of today's size, and a store unchanged since its last clean scan is not scanned again. You write acceptance tests for it, before its implementation exists, from behaviour, and you show them red.

## Step 0, before any work: the sandbox check

Report it first in your return.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kl5e','w').write('x')"` must fail.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know (the decisions, how the check is declared and run, how earlier suites test it) before reading files at random. Say in your return which questions you asked.
- **Reads open, writes closed (Policy 2, DEC-820).** You read freely: the whole repository, the committed context, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); **(c) the counterpart's work on this ticket: you never read this ticket's implementation — no file that `git diff --name-only w2/integrate...HEAD` names, other than this ticket's own acceptance tests under `tests/acceptance/W2-50/`, by any tool. In particular `src/gov/secrets/__init__.py` as it stands in this worktree is this ticket's implementation: read the existing code only as it stands on the base, with `git show w2/integrate:<path>`;** (d) the hidden half of any evaluation set, by whoever is measured by it. Writes stay inside the paths below.
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Protected material (DEC-820).** Never read the held-out material's contents and never print a secret. Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Never touch the real `~/gov-os-runs/` (no create, write, list or remove) and never the real `~/gov-os-worktrees/` outside this worktree.
- **A canary secret** in a test is a made-up value that gitleaks' rules match (as the existing suites under `tests/acceptance/W1-15/` and `tests/acceptance/W2-50/test_w2_50_never_indexed.py` build theirs), written by the test into its temporary folder at run time, never a real key. Never print one in a message.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: run long files in separate commands. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A test that needs a project builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder of this worktree or the main tree (DEC-673); a temporary project your test builds in its own temporary folder has its own `.gov-runtime/` with the stores the test makes.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild` (with or without `--no-embeddings`), `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Tests launch no real `claude` session and use no network. Never write under `src/`.
- Never ask or notify the owner (no question box, never `owner-ping`); a question is a package in your return.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): the KPI lines marked [DEC-853], and its last note.
- The decision DEC-853 and the package behind it, `governance/project/orchestration/packages/P-W2-49.md` (name it by its path; do not search `governance/project/`). Also DEC-136, DEC-221, DEC-285 to DEC-290, DEC-298, DEC-347, DEC-462, DEC-595, DEC-732 in `docs/DECISION_REGISTER.md`.
- How the check is declared and run: `template/governance/kernel/checks/secrets-indexing.yaml` (the command `python3 -m gov.secrets` in the project root, exit 0 green, exit non-zero red), and how `gov check` runs a declared check. The existing scan as it stands on the base: `git show w2/integrate:src/gov/secrets/__init__.py` and `git show w2/integrate:src/gov/secrets/__main__.py` (never the worktree's copy of `__init__.py`).
- How earlier suites test this check through its public command: `tests/acceptance/W1-15/` and `tests/acceptance/W2-50/test_w2_50_never_indexed.py` with `tests/acceptance/W2-50/w2_50_support.py` and `conftest.py`. Reuse their means of building a temporary project (its `.gitleaks.toml`, its path map, its `.gov-runtime/` stores) where they fit.
- `gitleaks` 8.30.1 is at `~/.local/bin/gitleaks`; `gitleaks stdin --help` is a public source for how it reads.

## The owner's DEC-853 (2026-10-19), as the behaviour to test

Today the secrets-indexing check scans every file under the project's `.gov-runtime/` with gitleaks over standard input: the file's bytes and, for a SQLite file, its rows as text, once per rule set (two when the project's `.gitleaks.toml` extends gitleaks' defaults with rules of its own), with a fixed 60-second limit on each gitleaks run, many files at a time. On the main tree's stores (`store.db` 250 MB, the code graph's `code.db` 210 MB) a gitleaks run hit that limit, so the check failed (closed) and every close would be refused. One pass of gitleaks over `store.db`'s bytes alone takes 11.7 s on a quiet machine (about 21 MB/s); under a full pool the runs went below about 4 MB/s.

The owner's ruling:
1. The time limit grows with the content's size (or a large store is scanned in bounded chunks, each within the limit), and the pool is bounded so that large files are not starved. **The check finishes on stores of today's size.**
2. **Every file is still scanned with every rule set; a scan that cannot finish still fails closed** (the check is red, never green).
3. **A store whose hash has not changed since its last clean scan is not scanned again: its clean result is reused, keyed on the store's hash. A changed store (by one byte) is always scanned again in full. A finding is never reused.**

Two working figures for your tests, which the engineer is given in the same words: **a store must be decided whenever gitleaks reads its input at 1 MB/s or faster** (a twentieth of the quiet-machine rate), and **a reused clean result is labelled in the check's output (standard output or standard error of `python3 -m gov.secrets`) by a line that names the store's project-relative path and the SHA-256 hex digest of the store file's bytes it was keyed on.** A store that is scanned carries no such line.

## The behaviours to test (described behaviour)

Test each through the check's public command (`python3 -m gov.secrets` run in a temporary project's root with `PYTHONPATH` as above), and through `gov check` where it adds something. FULL, thorough, no combinatorial expansion (DEC-221).

1. **A large store is decided.** A temporary project whose `.gov-runtime/` holds a store large enough that today's scan cannot finish it within its fixed limit: the check finishes with a verdict — green when the store is clean, red naming the store when it holds a canary. Find first, by measurement on this machine, how to make today's scan fail on it deterministically. You may use real gitleaks on a store large enough (if the size stays within reason for a test: memory and disk), or put on `PATH` a stand-in named `gitleaks` that delegates every decision to the real `~/.local/bin/gitleaks` and only reads its input more slowly, at a stated rate no slower than 1 MB/s (so that today's fixed 60-second limit fails and a fix that meets the working figure passes). Keep wide margins: the machine is shared and loaded. Say in the README which you chose and why, with the sizes, the rate and the times you measured. Also: a large store among many small files (the pool full) is decided.
2. **An unchanged store is not scanned again.** After a clean run, a second run over the same unchanged store gives the same green verdict, does not pass the store's content to gitleaks again, and labels its clean result as reused with the store's path and the SHA-256 hex digest of its bytes (the working figure above). A public means to see what gitleaks was given: a delegating stand-in `gitleaks` on `PATH` that logs, in the test's temporary folder, what it received (its size, and which marker strings of yours it saw), then hands the decision to the real gitleaks.
3. **A store changed by one byte is scanned again in full.** Change one byte of a store that was clean (also with its size and modification time kept the same), run again: the store is not labelled as reused, and gitleaks is given all of it again (for example, markers you placed at its start, middle and end are all seen, with every rule set), and the verdict is decided anew. A one-byte change that makes a canary appear in it is found.
4. **A finding is never reused.** A store holding a canary is red, naming the store, on every run (at least three in a row), each time from a fresh scan: gitleaks is given its content each time, and no reuse label names it. A store that was clean and then gains a canary is red on the next run.
5. **Every file with every rule set.** With a project `.gitleaks.toml` that extends gitleaks' defaults with rules of its own (two rule sets), each store is scanned with both; a store holding a value that only the project's own rule matches is red. **A change of the project's rules makes no earlier clean result count:** a store that was clean under the old rules, unchanged itself, and holding a value only a newly added rule matches, is red on the next run.
6. **A scan that cannot finish fails closed.** A stand-in `gitleaks` that never finishes (or crashes, or exits with an unexpected code) on a store: the check is red (non-zero exit), never green, and within a bounded time; and afterwards, with the real gitleaks back, that store is scanned in full (no clean result was recorded from the failed run). If the scan leaves a record of its clean results somewhere in the project, a damaged copy of that record never makes a store count as clean: the store is scanned in full or the check fails closed. Find the record, if any, only by its public effect (what a run leaves in the temporary project), never by reading the implementation.
7. **Controls (pass now and after):** a small clean project is green; a small store with a canary is red naming the store, never the secret; the check's output never holds the secret's value.

## What you write

- Only inside `tests/acceptance/W2-50/`: the new cases in **a new file**, plus your own helpers in a new file there if you need them. No earlier file of this suite and no other ticket's tests are changed. No throwaway implementation is left in the tree.
- Update the README: a new section for these tests, **"tests added for the owner's DEC-853, before its implementation"**, mapping each DEC-853 KPI line (the two success lines and the failure line in `.tickets/DAEO-kl5e.md`) to its tests, each with its expected red reason; the stand-in(s) you used and why they are public means; the sizes, rates and times you measured; the case count, and the new total of the suite.
- Behaviour through public interfaces, never internals (no import of a private module, no name of code to be written). Deterministic, no network. Child processes get `PYTHONPATH` as the suite already passes it. Every case cleans up after itself in its temporary folder; large files live only there.
- Red first: run your new file to its end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50/<your file> -q -p no:cacheprovider -rs`
  Each new test fails for the reason the README states, or passes today for a stated reason (a control, or a behaviour today's scan already has, such as a finding never reused). Then run `tests/acceptance/W2-50/test_w2_50_never_indexed.py` and `tests/acceptance/W2-50/test_w2_50_code_under_test.py` once to show they give what they gave before (green).
- A behaviour you cannot turn into a test without a reading no source supports is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), with no test.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for the secrets scan's size, pool and reuse by hash (DEC-853)" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-853" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

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

In those fields give: the sandbox check's result (step 0); your commit's hash and trailers; the `gov.__file__` line; your new file's counts and the red reason of each failing case as you saw it; which cases pass today and why; the stand-ins, sizes, rates and times; the `gov retrieve` questions you asked; the guard read refusals you met (count). Refused twice for the same call: stop and say so.
