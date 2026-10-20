# Brief: engineer — DAEO-kl5e (W2-50), FULL: the secrets scan finishes on today's stores and reuses a clean result by its hash (DEC-853)

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `878467c9` or later. The ticket's earlier rounds are implemented and green. The owner has added one behaviour to this ticket (DEC-853, 2026-10-19): the secrets-indexing check must finish on stores of today's size, and a store unchanged since its last clean scan is not scanned again. New acceptance tests for it fail against the code. You change the scan until they pass, without breaking anything that passes today.

## Step 0, before any work: the sandbox check

Report it first in your return.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kl5e','w').write('x')"` must fail.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Say in your return which questions you asked and whether they helped (the stores may be stale: then say so and read by name).
- **Reads open, writes closed (Policy 2, DEC-820).** You read freely: the whole repository, the committed context, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-50/` (its tests, helpers, conftest and README), by any tool. You may run those tests and read their names, results and failure messages;** (d) the hidden half of any evaluation set, by whoever is measured by it. Writes stay inside the paths below.
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Protected material (DEC-820).** Never read the held-out material's contents and never print a secret (a canary included). Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Never create, write, list or remove anything in the real `~/gov-os-runs/` other than your own ticket's folder, and nothing in it is needed for this work.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: run a long suite's files in separate commands (the three large cases of the new file, `-k large`, take about 3 to 6 minutes together; run them in a command of their own). **Commit your work before you run any long suite.** Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A builder test that needs a project builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder of this worktree or the main tree (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild` (with or without `--no-embeddings`), `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree; never run `gov check` against this worktree's or the main tree's real stores (the lead does that after a rebuild). Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never write under `src/gov/close/**` or `tests/unit/close/**`.
- Never ask or notify the owner (no question box, never `owner-ping`); a question is a package in your return.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## The owner's DEC-853 (2026-10-19), what you build

Today the secrets-indexing check (`python3 -m gov.secrets` in the project root; declared in `template/governance/kernel/checks/secrets-indexing.yaml`, hard-block) scans every file under the project's `.gov-runtime/` with gitleaks over standard input: the file's bytes and, for a SQLite file, its rows as text, once per rule set (two when the project's `.gitleaks.toml` extends gitleaks' defaults with rules of its own, DEC-347), with a fixed 60-second limit on each gitleaks run, as many files at a time as the default thread pool takes. On the main tree's stores (`store.db` 250 MB, the code graph's `code.db` 210 MB) a gitleaks run hit that limit, so the check failed closed and every close would be refused (P-W2-49, `governance/project/orchestration/packages/P-W2-49.md`; name it by path). One pass of gitleaks over `store.db`'s bytes alone takes 11.7 s on a quiet machine (about 21 MB/s); under a full pool the runs went below about 4 MB/s.

The owner's ruling, every line of which must hold:
1. **The time limit grows with the content's size (or a large store is scanned in bounded chunks, each within the limit, with no secret lost at a chunk's edge), and the pool is bounded so that large files are not starved. The check finishes on stores of today's size.**
2. **Every file is still scanned with every rule set. A scan that cannot finish still fails closed** (raises; the check is red, never green).
3. **A store whose hash has not changed since its last clean scan is not scanned again: its clean result is reused, keyed on the store's hash. A changed store (by one byte, whatever its size and modification time) is always scanned again in full. A finding is never reused.**

Two working figures, which the test designer was given in the same words: **a store must be decided whenever gitleaks reads its input at 1 MB/s or faster** (a twentieth of the quiet-machine rate), and **a reused clean result is labelled in the check's output (standard output or standard error of `python3 -m gov.secrets`) by a line that names the store's project-relative path and the SHA-256 hex digest of the store file's bytes it was keyed on.** A store that is scanned carries no such line. The label never holds content.

What follows from those lines, which your design must keep:
- A clean result counts only for the same bytes **and the same rule sets**: a change of the project's `.gitleaks.toml` (or anything else that changes what a scan would decide) makes no earlier clean result count.
- Only a scan that ran to its end with every rule set and found nothing is recorded as clean. A scan that raised, timed out or found something records nothing.
- The record of clean results lives inside the project (not in a shared or global place), and a record that is missing, unreadable, damaged or of another form is never trusted: the store is scanned in full (or the check fails closed). Writing the record must not leave a half-written record behind if a run is interrupted.
- Gitleaks is run exactly as today: by name, the one `PATH` finds, with its rules by the environment, over standard input. Do not change how a secret is decided, the rules (DEC-298, DEC-347), the UTF-16 handling, or what a store's content is (its bytes, and for SQLite its rows as text).
- **Keep this ticket's link rule in `stores_with_secrets` intact** (DEC-728, DEC-743 §6.1 (i), DEC-751 item 2: a link from `.gov-runtime/` into `~/gov-os-runs` is not followed; a link whose target stays inside the project is followed). Its acceptance cases (`test_w2_50_never_indexed.py`, and the link cases in the suite's other files) must stay green.
- Keep every name other modules import from `gov.secrets` working as it does: `indexable`, `path_holds_secret`, `stores_with_secrets`, `CONFIG_REL`, `_rules`, `_matches` (used by `gov.codeintel`, `gov.ci.command`, `gov.retrieval.lexical`, `gov.retrieval.semantic`). The indexers' filter `indexable` keeps its behaviour; if you share a changed helper with it, it may only gain the size-aware limit, never lose a check.
- Keep the scan's memory within reason on stores of today's size: the bounded pool must not hold many copies of several hundred MB at once.
- Proportion (DEC-135): no code beyond what DEC-853's lines and the failing tests ask. **Never make the check fail open.**

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): the three KPI lines marked [DEC-853], and its last note.
- DEC-853, DEC-285 to DEC-290, DEC-298, DEC-347, DEC-595, DEC-728, DEC-743, DEC-751 in `docs/DECISION_REGISTER.md`.
- The code: `src/gov/secrets/__init__.py`, `src/gov/secrets/__main__.py` (read only: it is not in your paths), `template/governance/kernel/checks/secrets-indexing.yaml` (read only), and how `gov check` runs a declared check (`src/gov/check/`).
- **The failing output:** `/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/log/red-9.txt` (the new file `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py` run at `878467c9`). Read it; never read the test file itself.

## What you write

- Only `src/gov/secrets/__init__.py` (the scan) and builder tests under `tests/unit/secrets/` (a new file of yours; the existing `test_secrets.py` and `test_token_rule.py` stay green and unchanged). **`src/gov/secrets/__main__.py` is not in this ticket's paths**: the reuse label comes from the scan itself. If a fix needs a path outside these, stop and return PACKAGES naming the file.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests as regression evidence only, each with a temporary project (and, where gitleaks' speed matters, a stand-in of your own on `PATH` in your temporary folder).

## Run, in the foreground, each to its end, never with `-x`

- The new file until it passes: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py -q -p no:cacheprovider -rs` (the small cases with `-k "not large"`, the large ones with `-k large`, in separate commands).
- The rest of this ticket's suite, `tests/acceptance/W2-50`, in a few commands of separate files (it holds 636 cases; it was all green before the new file).
- The earlier suites of the code you touch, the same way: W1-15, W1-16, W1-17, W1-26, W1-27, W1-30 (and W1-19 if it runs in your session; say if it cannot). Name each with its counts.
- The builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit -q -p no:cacheprovider`.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block (a later fix is a new commit, same trailers):

    git commit -m "W2-50 (DAEO-kl5e): the secrets scan finishes on today's stores and reuses a clean result by its hash (DEC-853)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-853" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Then show `git log --oneline -3`, `git log -1 --format=%B`, `git show --stat HEAD` and `git status --short`.

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

In those fields give: the sandbox check's result (step 0); each commit's hash and trailers; the lines added and removed (`git show --shortstat`); the design as built (the limit's formula or the chunking, the pool's bound, the key of a clean result, where the record lives and how a damaged one is handled, the label's form); every suite you ran with its counts; the `gov.__file__` line; the `gov retrieve` questions you asked; the guard read refusals you met (count); anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.
