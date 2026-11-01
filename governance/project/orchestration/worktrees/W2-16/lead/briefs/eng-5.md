# Brief: engineer (W2-16 round 3, the acceptance run, DEC-963)

You are a fresh engineer. Ticket: `DAEO-49o5` (`W2-16`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`. An earlier engineer built DEC-772 item 1 (commit `bb49523039c7`: `gov release <version>` is the owner's alone, from a plain terminal with a typed code; the seam `gov.release.command._release_test`). The independent test designer's cases are now merged (`b023b9c1`). You run the acceptance suite once, reading results only, and repair the code only where a failure shows the code is wrong.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-49o5','w').write('x')"` must fail. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-49o5`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`) and `git log --oneline -1` (expect `b023b9c1`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Reads (DEC-820, Policy 2).** You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never the qualification oracle; **(c) the counterpart's work: never read `tests/acceptance/W2-16/`, here, in `/home/usain/gov-os-worktrees/W2-16-tests` or in git history** (no Read, cat, grep, diff or `git show` of it); you run those tests and read their names, results and failure messages; (d) the hidden half of any evaluation set.
- **Retrieval (DEC-836, DEC-860, DEC-859):** what you need to know you ask first with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m gov.cli.main retrieve "<question>" --json` (this worktree's store may answer `STORE_MISSING`; then read the named files). Never one giant query: batches (`--batch-size`, then `--continue <token>`). A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted; if it is not available, search named folders with Grep. Drop unread any result under `tests/acceptance/W2-16/`.
- **Read refusals (DEC-849):** the guard may refuse a search that starts at the repository root, `governance/project/` or `.claude/`. Take it, never another form; count them in your return.
- **Scratch budget (DEC-898):** your share is 4 GB and 200,000 files and folders. Keep pytest's own temp retention (no `--basetemp`); clean what you make; give `du -sh` and `du -s --inodes` of what you leave.
- **Commit hashes (row W2-L423's rule, DEC-911):** under `.gov-runtime/`, 12-digit hashes only, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Run everything in the foreground; a single tool call is cut off at 10 minutes, so run the suite file by file (`tests/acceptance/W2-16/test_*.py`, one after another, never two at once). No `git checkout`, `reset`, `clean`, `stash`, amend or rebase. Never read `.claude/settings*.json` or `~/.claude/`. Never write in `~/gov-os-workbench`. Never copy the repository or a folder of it. `.gov-runtime/freeze` shows as a placeholder device file in a launched session: conclude nothing from it. Write files with Write and Edit and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never run `gov release` against this repository's real history, `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`. Never set `GOV_ROLE` or `GOV_TICKET` on a command line. Never touch `tests/acceptance/**` (MR-3).
- If the guard or the sandbox refuses something you needed, return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6). Record each refusal by the guard (time, the command's form in one line, the reason it gave).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you do

1. Run, file by file, each to its end, never `-x`:

       PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16/<file> -q -p no:cacheprovider -rfEs -o tmp_path_retention_policy=failed

2. A failure whose message shows the code is wrong against the specification in `.gov-runtime/scratch/lead/briefs/spec-dec772.md` (read it; it is the round's specification) and the ticket's KPIs: repair it in `src/gov/release/**` (builder tests in `tests/unit/release/**`), only what the failure needs, never failing open; commit; run the failing file once more. A failure you judge to be the test's fault: never edit it and never work around it; return it as a package with the failure message.
3. Then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/unit/release tests/unit/lock -q -p no:cacheprovider`.

Only `src/gov/release/**`, `tests/unit/release/**` and `docs/releases/README.md` may change. Before each commit check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file. Trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-49o5" --trailer "Role: engineer" --trailer "Implements: DEC-772, CAP-43.b, DEC-722" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`. If nothing needs repair, make no commit.

## Return

Your last message, complete in itself: the sandbox check; each file's counts and each red case by name with its message; any repair (commit, files, why); the `gov.__file__` line; whether you used `gov retrieve`; the guard's refusals and read refusals; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
