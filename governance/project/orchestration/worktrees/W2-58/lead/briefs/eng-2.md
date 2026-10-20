You are a fresh engineer. Ticket: DAEO-5j8b (W2-58, "Policy 2 in the guard and the launcher: reads open, four refusals"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-58` on branch `w2/W2-58`. The ticket's guard work is built and verified; the owner has since re-baselined one clause of it (DEC-873). You make the launcher follow DEC-873 until the ticket's acceptance tests pass. The owner approved this guard and launcher change in DEC-821 and DEC-873 (CAP-33).

## How you were launched (read first)

You were started with `gov launch engineer DAEO-5j8b` from the pinned release (the bare `gov`, DEC-822), not from this worktree's launcher: this worktree's launcher still adds the `Read` deny rules for (c) and (d) that you remove, and a session it launches cannot run its own acceptance tests. Your settings carry the held-out `Read` rules (b) and no `Read` rule for (c) or (d), as DEC-873 item 2 sets. The guard hook runs this worktree's own `src/` and refuses (c) to you: Policy 2 (c) binds you all the same.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-5j8b','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-5j8b`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-58` and `w2/W2-58`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Your own session runs the guard.** The hook lines call `$CLAUDE_PROJECT_DIR/src`, and your `CLAUDE_PROJECT_DIR` is this worktree. You should not need to change the guard's read rules (DEC-873 item 1 keeps them); if you touch any file under `src/gov/guard/`, check after every edit that `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m gov.guard.hooks` still loads and lists the hook events, and run the guard's unit tests. **Never make a guard or launch decision fail open:** an exception, a file that cannot be parsed, or a git command that fails while a refusal is worked out refuses.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-58/`, by any tool (Read, Grep, `cat`, `grep`, `git show`, `git log -p`, `git diff` of it), nor the earlier acceptance cases the test designers rewrote on this branch (read those files only as they stand on the base, `git show w2/integrate:<path>`); you may run those tests and read their results (names, pass or fail, failure messages), never their source;** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`.
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (a search or listing that starts at the repository root, `governance/project/` or `.claude/`). Take such a refusal as a refusal, never look for another spelling, search named folders instead, and **count every such refusal in your return**.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`: callers of a function, a path between two functions, a symbol search), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Your Bash run as a whole is stopped at two hours: **commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere; copy single named files only, never `governance/project/`. A test that needs a repository builds a temporary one. Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package.
- Nobody runs `gov close`, `gov adopt`, `gov pause`, `gov rebuild`, or `docs/plan/tools/validate_s1.py`.
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-5j8b.md` (read-only): its KPI lines (KPI 1 restated and KPI 2 added by DEC-873) and its `allowed_paths`.
- The decisions in `docs/DECISION_REGISTER.md`: **DEC-873** (all five items), DEC-821 (its status line marks the changed words), DEC-820, DEC-845, DEC-218, DEC-242, DEC-866, DEC-135.
- The package that led to DEC-873: `governance/project/orchestration/packages/P-W2-58-1.md`. What it measured: Claude Code turns every `Read` deny rule that matches existing files into an operating-system read denial for the session's own commands (the sandbox's `filesystem.read.denyOnly`), under every rule form tried (`<folder>/**`, `<file>*`, `W2-5[8]/**`).
- The code: `src/gov/launch/launcher.py` (`build_settings`, its `Read` and `Edit` deny rules, and the descriptions of its rule forms in `_runtime_rules`, `_tree_rules` and `build_settings`), the launcher's use of this ticket's evaluation-set checks, and `tests/unit/launch/`. `git diff w2/integrate...HEAD -- src/gov/launch` shows this ticket's launcher change so far; `docs/changes/W2-58-CIT-E.md` is the ticket's change record.
- The ticket's acceptance tests: `tests/acceptance/W2-58/` — **run them, never read them.**

## The behaviour to build (DEC-873)

1. **The launcher adds no `Read` deny rule for (c) or (d)**, because running a test means reading it: the `--settings` value `gov launch <role> <T>` builds carries no `Read` deny rule (and no sandbox filesystem read denial) covering T's acceptance folder for an engineer, the files T's branch changes for a test designer, or an evaluation set's hidden part for a session the set measures. Remove what this ticket added for that (your package's estimate: about 30 lines), and any code left with no caller.
2. **The held-out material's `Read` deny rules (b) stay** in every launched role's settings, as today.
3. **A launch under a malformed `evaluation_sets` block is still refused** (fail closed, as DEC-218 does for the held-out list), with its reason; a well-formed block or none launches.
4. **The guard's read rules for (c) and (d) do not change** (DEC-873 item 1): every guard case stays as it is.
5. **Correct the launcher's own description:** its text says the Linux sandbox "skips a pattern". For `Read` rules that is wrong (measured above: a pattern that matches existing files becomes a literal read denial for the commands). Correct the text in `src/gov/launch/**` so that nothing there states that belief for `Read` rules; where the text speaks of `Edit` rules, say only what is known, and do not change those rules. Correct the same belief wherever this ticket wrote it in its own files within your paths (the comment over the `evaluation_sets` block in `governance/project/path-map.yaml` says the hidden part is refused "by the guard and by its sandbox"; this ticket's guard module may describe the removed rules), touching only those lines.
6. **The change record** `docs/changes/W2-58-CIT-E.md`: bring it to DEC-873 (the sandbox rule removed, why, the held-out rules kept, the malformed-block refusal kept, row W2-L374 for an OS-level layer), with `decisions_recorded` naming DEC-873 beside DEC-821.

Proportion (DEC-135): nothing beyond the above.

## What you write

- Only inside the ticket's `allowed_paths`, and within them only what the behaviour above needs: `src/gov/launch/**`, `src/gov/guard/reads.py` (only to remove what has no caller left, or to correct its description), `governance/project/path-map.yaml` (the comment over the `evaluation_sets` block only; **no other line: `accepted_reds` and `load_sensitive` are owner-only, DEC-757, DEC-766**), `tests/unit/launch/**`, `tests/unit/guard/**`, `docs/changes/W2-58-CIT-E.md`.
- Never anything under `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests in `tests/unit/launch/` (and `tests/unit/guard/` if you touch the guard): update the builder cases that assert the removed rules, and say which.

## How you check

- `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m pytest tests/acceptance/W2-58 -q -p no:cacheprovider -rs`, to its end, never with `-x`, until it passes (its `local_only` live cases are skipped inside your sandbox; the lead runs them).
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m pytest tests/unit/launch tests/unit/guard -q -p no:cacheprovider`.
- Commit before the longer runs, then each in its own process, the same way as the first: `tests/acceptance/W1-46`, `tests/acceptance/W1-32`, `tests/acceptance/W2-50` (the suites that drive the launcher). A foreground command is stopped at ten minutes: split a longer suite by file. Report each suite's counts; a red you did not cause (it fails the same way on `w2/integrate`'s code) is reported, not fixed.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m gov.check.pathmap` and `python3 -m gov.check.schema` (same `PYTHONPATH`) stay green.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-5j8b" --trailer "Role: engineer" --trailer "Implements: DEC-873" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Check `git log --oneline -3` and `git status --short` after each commit.

## Return

Your commits' hashes; the files changed; the tests you ran with their results; the lines added and removed; the `gov.__file__` line; the guard read refusals you met (DEC-849), counted; whether you used `gov retrieve`, and for what; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

Your return is one message. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
