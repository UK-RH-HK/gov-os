You are a fresh independent test designer (MR-3). Ticket: DAEO-0rfi (W2-54), profile FULL, **run 5**, a short correction after the merge. You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`, launched through `gov launch` under its OS sandbox. W2-54's code is merged into `w2/integrate`; three of its acceptance cases assert that W2-02's other types do not exist **in the tree**, so they turn red on any tree that holds W2-02's merge. The orchestrator's DEC-874 (delegated, 2026-10-20; in this worktree's register) decides how they change. You make those changes, and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` must **fail**. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must **work**. If (a) wrote the file or (b) failed, stop there and return, naming what happened (never delete a file (a) made).

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`) and `git log --oneline -1` (expect `de42a87d`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`, and run a long suite file by file.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- The test command: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/<file> -q -p no:cacheprovider -rs`, run to its end, never with `-x`.
- **Memory first (DEC-836):** for what you need to know, ask `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main retrieve "<question>" --json` before reading files at random. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Reads open, writes closed (Policy 2, DEC-820).** You read freely: the repository, git history, other worktrees and branches. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); **(c) the counterpart's work on this ticket: you, the test designer, never read this ticket's implementation — the files `git diff --name-only w2/integrate~1...HEAD` and W2-54's own commits name, other than your own tests (`tests/acceptance/W2-54/**`) — in particular never the contents of `src/gov/check/schema.py`, `src/gov/context/**`, `src/gov/retrieval/semantic.py`, `src/gov/retrieval/ollama.py`, `tests/unit/**` of this ticket or `template/governance/kernel/checks/context-reproducibility.yaml`. Your cases may run git commands that read the names of files W2-54's commits touch and the lines they add, as the cases' own subject; you yourself do not study the implementation's code;** (d) the hidden half of any evaluation set, by whoever is measured by it. Reviewers read everything. Writes stay inside your paths below.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count the refusals you met and list them in your return.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`. Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No copy of the tree:** never `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it, anywhere. A case reads other commits through `git show <commit>:<path>`, `git log` and `git diff` (nothing is checked out); a case that needs a repository builds a temporary one from scratch in its `tmp_path`. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Tests never write the main tree's store, another worktree's, or this worktree's.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.mcp.json`, `docs/source`, …): never commit them.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`. Never ask or notify the owner (no question box, no `owner-ping`).
- **Inside your sandbox `gov` reaches no shared Ollama** and the GPU is hidden: the `shared_gpu` and `local_only` cases, `test_w2_54_green_here.py`, W1-21's real-models case, `gov rebuild` and `gov check` are the lead's: leave them out and say so.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**`.
- **What you may change:** `tests/acceptance/W2-54/**` only (in practice `test_w2_54_audit_report.py`, the README, and `w2_54_support.py` if a helper is needed). No other folder. The lead compares the tree before and after your session.
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): its KPI lines (success line S4, the `audit-report` type, and failure line 3) and sources.
- DEC-874 and DEC-768 in `docs/DECISION_REGISTER.md` (search for `### DEC-874` and `### DEC-768`).
- `tests/acceptance/W2-54/README.md` (its first section, on KPI S4 and its cases), `tests/acceptance/W2-54/test_w2_54_audit_report.py` and `w2_54_support.py`.

## The three cases and DEC-874

The cases, as they stand:
- `test_no_schema_file_of_w2_02_s_other_types_comes_with_it`: asserts that `close.schema.json` and `adoption-verdict.schema.json` do not exist in this tree's schema folders;
- `test_w2_02_s_other_types_are_judged_as_an_unknown_type[close]` and `[adoption-verdict]`: assert that core-schema, run from this tree, judges a `close` or `adoption-verdict` record as it judges an unknown type.

On any tree that holds W2-02's merge, W2-02's own types exist, so these fail although W2-54 did nothing wrong. **DEC-874 item 1:** KPI S4 ("the `audit-report` type exactly as W2-02 defines it … nothing of W2-02's other types", DEC-768 item 1) is unchanged in meaning: **it is about W2-54's own change, not about the tree.** The cases are corrected to that meaning: **W2-54's own commits bring in no schema file and no type of W2-02's beyond `audit-report`**, which holds before and after W2-02 merges.

What the corrected cases must do:
1. **Judge W2-54's own change through git, not the tree's present state.** W2-54's own commits are the non-merge commits whose `Task:` trailer is `DAEO-0rfi` (every commit of this ticket carries it; W2-02's carry `Task: DAEO-zflj`). For example: the files those commits add or change (`git log --no-merges --name-status`), and the lines they add to `src/gov/check/schema.py` (`git log --no-merges -p -- src/gov/check/schema.py`), read against their parents. Choose the reading, state it in the README, and keep it exact: a W2-54 commit that added `close.schema.json` or `adoption-verdict.schema.json` under either schema folder, or added `close` or `adoption-verdict` to core-schema's type map or its standalone types, makes a case fail, naming the commit and the file or line. Mind that a merge of `w2/integrate` into this branch (its commits are merges) is not W2-54's own change.
2. **Pass both on this branch and with W2-02's types present.** W2-02's branch commit `4ce16df2` holds W2-02's types merged with `w2/integrate`, and every W2-54 commit is among its ancestors. Make the cases judge both histories: `HEAD` and `4ce16df2` (pin it in `w2_54_support.py` as `2a35fd7b` is pinned, with a comment), for instance as a parameter of each case, read through `git` only (never checked out). Both must pass with today's history.
3. **Keep the behavioural part where it still states S4's meaning:** the `[close]` / `[adoption-verdict]` case may keep a run of core-schema if it runs core-schema as W2-54's own change leaves it (for example, `git show` of a single named file of W2-54's own last commit that touched it into the case's temporary folder), or it may become a reading of W2-54's own added lines; your choice, stated in the README. Its two parametrisations stay (`close`, `adoption-verdict`).
4. **Show each corrected case red when the meaning is broken:** inside the case or in a throwaway outside the tree, a temporary repository built from scratch in which a commit carrying `Task: DAEO-0rfi` adds a `close.schema.json` or a `"close"` type entry, and the reading you chose fails on it; and passes when only another `Task:` brings it in. Leave no throwaway in the tree; a parametrised fixture inside the test is fine.

**No other expectation changes.** The other cases of the file (the schema file byte for byte as W2-02's at `2a35fd7b`; the audit folder; the fields; failure line 3; W1-43's body untouched) stay exactly as they are. Nothing is deleted or skipped; the three test ids keep their names (if a parameter is added, the existing ids gain a parameter, and say so). Each change carries `Rewrite-Reason: DEC-874`. The README gets a short "Run 5 (DEC-874)" section: what each case asked before and after, and why.

## Runs (each to its end, never `-x`)

1. Step 0 and the start checks; the `gov.__file__` line.
2. After your changes: the three corrected cases (all parametrisations), then `tests/acceptance/W2-54/test_w2_54_audit_report.py` in full, then `tests/acceptance/W2-54` in full with `-m "not local_only and not shared_gpu" --ignore=tests/acceptance/W2-54/test_w2_54_green_here.py` (or the suite's own marker names, as the README states), file by file if one run would pass 10 minutes. Expected: every case green with today's code.
3. The red demonstration of item 4, with its output.
4. Also run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` and quote its last line (no collection error).
5. Name every case that is not green, with its output.

## Commit

Commit only your test paths, one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "W2-54 (DAEO-0rfi): run 5: <what>" --trailer "Task: DAEO-0rfi" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-773" --trailer "Rewrite-Reason: DEC-874 (orchestrator, delegated, 2026-10-20): <...>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, check `git log --oneline -2` and `git status --short`: a commit you did not make, stop and say so.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Nothing comes before the twelve fields. Refused twice for the same call, stop and say so.

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

In the fields: the sandbox check's result first; your commit's hash; each changed case with what it asked or asserted before and after (no other expectation lowered); the runs with their counts; the red demonstration; the `gov.__file__` line; the collection's last line; whether you used `gov retrieve`; the guard read refusals you met (DEC-849); any package.
