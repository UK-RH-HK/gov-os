You are a fresh engineer. Ticket: DAEO-e8f0 (W2-71), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-71` on branch `w2/W2-71`. You implement the ticket until its acceptance tests pass. Your time budget is about 90 minutes; the estimate is about 50 lines in `src/gov/secrets/`.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-e8f0','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (the twelve fields below), saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-e8f0`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-71` and `w2/W2-71`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Commit your work before any long run.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **Reads (DEC-820, Policy 2):** you read freely: the whole repository, the committed context, git history. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it; never read or name the qualification oracle); (c) the counterpart's work on this ticket: **you never read `tests/acceptance/W2-71/`**, by any tool (you may run those tests and see their names, results and failure messages, never their source); (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return. Never read `.claude/settings.json`.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and for what.
- **Row W2-L423's rule (owner, standing, DEC-911) — read this twice.** One gitleaks default rule takes a bare 40-hex string for a token when one of its two keywords stands in the same text. Its vendor's name is written here only in two parts, `"source" + "graph"`; its rule id is that name followed by `-access-token`; its two keywords are that name and `"sgp" + "_"`. In every file you write (code, unit tests, comments, docstrings, commit message) and in your messages and return, **the rule's id and its two keywords are written only in parts, joined at run time**, never whole, in any case. Under `.gov-runtime/`, write commit hashes as 12 digits, never 40. Call the rule "row W2-L423's rule" in prose. Unit tests build any token at test time from parts or random hex, never store one whole, and never print one.
- **Protected material:** never print a secret. Never write in `~/gov-os-workbench`; clones the ticket needs go under `~/gov-os-runs/W2-71/`, from an exact path. Dev-tier tests use `GOV_DEV_TIERS` by name only.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); copy single named files only, never `governance/project/`. A test that needs a repository builds a temporary one from scratch.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Disk (DEC-898):** your share of the ticket's scratch budget is 6 GB and 300,000 files and folders. Keep pytest's own temp retention (never `--basetemp`); do not set `TMPDIR` (the sandbox sets your temp folder). Remove every temp tree you make as soon as it is not needed.
- **The machine:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run at most a single test file at a time; check before each run. You run this ticket's acceptance folder, `tests/unit/secrets_check/`, `tests/acceptance/W1-15/` and `tests/acceptance/W2-69/`; never the whole tree's suites (the lead does).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-e8f0.md` (read-only): its KPI lines and its `allowed_paths`. The card W2-71 in `docs/plan/WAVE_2_WBS.md` §2; row W2-L423 in `docs/plan/WAVE_2_LIST.md`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-911 (item 4 above all), DEC-298, DEC-347, DEC-853, DEC-290, DEC-909, DEC-897, DEC-135.
- The code the ticket touches: `src/gov/secrets/__init__.py` and its unit tests in `tests/unit/secrets_check/`. `src/gov/guard/containment.py` shows how this project runs git with an environment that cannot point it at another repository (`_GIT`, `_GIT_ELSEWHERE`, `_git_env`).
- The acceptance tests' results only: run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src python3 -m pytest tests/acceptance/W2-71 -q -p no:cacheprovider -rs` and read the names, results and failure messages.

## The behaviour (DEC-911 item 4, the ticket's KPIs; decided ground)

- A match of row W2-L423's rule whose matched secret is exactly 40 hex digits naming a commit object of the repository being scanned (what `git cat-file -e <sha>^{commit}` in that project answers) is no finding, for the secrets-indexing check (`stores_with_secrets`) and the pre-index filter (`indexable`, and `path_holds_secret` which shares the call), in a file and in a stored value.
- Everything else stays a finding, failing closed: any other rule (also when its match is such a hash); any other match of that rule (its prefixed forms; 39 or 41 digits; a short hash; a hash that names no commit object of that project: another repository's commit, a tree, a blob, nothing); and any match whose verification cannot run or does not answer clearly (no git, the project is not a repository, git exits with an error, git does not answer in time). A file that holds an exempt hash and any other finding is a finding.
- **The repository asked is the project's own:** run git against the project root, with an environment that cannot redirect it (no `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`; no replace objects), and so that a root that is not itself a repository is not answered by a repository above it. A linked worktree of this repository is its repository.
- **Matches are held in memory only:** no report file is written anywhere (the project, the temp folder), no match is printed, logged or put in an exception's message, and the clean-result record (DEC-853) never records a finding (its rules stand as they are: a store is recorded clean only when every scan of it ran and every match was exempt). Every file scanned today is still scanned, with every rule set (both configurations of DEC-347); no allowlist is added to any configuration, and the rule stays on.
- **Budgets:** keep the verification within the check's existing process time limits, with a bounded git call (for example one batch query per scan rather than one process per hash), and cache the answers per scan only, never across scans. The gitleaks calls keep their present time limits and pool.
- **Exactly 40 digits, and the object itself a commit:** check the length and the hex form before git is asked (git resolves 39- and 12-digit prefixes to their commit), and require the object named to be a commit itself (an annotated tag's id, which `^{commit}` peels to a commit, is not exempt; flagging it fails closed). A real commit's id quoted in upper case may be exempt or a finding: either is acceptable; a 40-hex string in any case that names no commit stays a finding.
- **Git's answer is read from its exit code and its output together:** a git that exits non-zero, or whose output does not say the object is a commit, is no exemption. A git that does not answer is stopped by a bounded time limit (of the order of the project's other git calls, about 10 s, not the check's whole limit), and the match stays a finding.
- **An exempt match does not end the scan early:** a text whose only findings are exempt still goes to every rule set (DEC-347), and any rule set's non-exempt finding is a finding.
- **The rule's id and keywords** appear in your code only in parts joined at run time (for example `"".join(("source", "graph"))`); never as adjacent string literals or a `+` of literals, which Python folds into one constant in the compiled file.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/secrets_check/` (new files), as regression evidence only (MR-3).
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. Never make a guard or gate decision fail open: every failure KPI must still refuse.
- Run, each to its end (never `-x`), until they pass: `tests/acceptance/W2-71`, then `tests/unit/secrets_check`, `tests/acceptance/W1-15` and `tests/acceptance/W2-69`, each with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src python3 -m pytest <folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`. Name any red you did not cause with its cause.
- Before committing, check that no file you wrote holds either keyword of row W2-L423's rule whole, in any case (search with the keyword joined at run time in a one-line Python command, printing paths only).

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-e8f0" --trailer "Role: engineer" --trailer "Implements: DEC-911" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The subject and body hold no keyword of row W2-L423's rule whole and no full hash.

## Return

One message, your last, complete in itself. In `evidence` and `tests`: step 0's result, your commit's hash (12 digits), the files changed, the lines added and removed, each suite you ran with its counts, the `gov.__file__` line, the refusals met, whether you used `gov retrieve`. Anything you were refused or could not settle is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Write commit hashes as 12 digits.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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
