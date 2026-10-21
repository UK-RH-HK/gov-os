You are a fresh independent test designer (MR-3). Ticket: DAEO-0rfi (W2-54), profile FULL, **run 5, second test-design batch** (after the first review). You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`, launched through `gov launch` under its OS sandbox. Run 5's first test designer (`49f1f81e`) corrected three acceptance cases to DEC-874 (delegated, 2026-10-20; in this worktree's register); the first review of the head `0ccafe25` found that one of them still does not hold once W2-02's merge is in the history. You correct that, and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` must **fail**. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must **work**. If (a) wrote the file or (b) failed, stop there and return, naming what happened (never delete a file (a) made).

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`) and `git log --oneline -1` (expect `0ccafe25`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`, and run a long suite file by file.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- The test command: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/<file> -q -p no:cacheprovider -rs`, run to its end, never with `-x`.
- **Memory first (DEC-836):** for what you need to know, ask `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main retrieve "<question>" --json` before reading files at random. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Reads open, writes closed (Policy 2, DEC-820).** You read freely: the repository, git history, other worktrees and branches. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); **(c) the counterpart's work on this ticket: you, the test designer, never read this ticket's implementation — in particular never the contents of `src/gov/check/schema.py`, `src/gov/context/**`, `src/gov/retrieval/semantic.py`, `src/gov/retrieval/ollama.py`, this ticket's `tests/unit/**` or `template/governance/kernel/checks/context-reproducibility.yaml`. Your cases may run git commands that read the names of files W2-54's commits touch and the lines they add, as the cases' own subject; you yourself do not study the implementation's code;** (d) the hidden half of any evaluation set, by whoever is measured by it. Writes stay inside your paths below.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count the refusals you met and list them in your return.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`. Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No copy of the tree:** never `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it, anywhere. A case reads other commits through `git show <commit>:<path>`, `git log` and `git diff` (nothing is checked out); a case that needs a repository builds a temporary one from scratch in its `tmp_path`. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Tests never write the main tree's store, another worktree's, or this worktree's.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.mcp.json`, `docs/source`, …): never commit them.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`. Never ask or notify the owner (no question box, no `owner-ping`).
- **Inside your sandbox `gov` reaches no shared Ollama** and the GPU is hidden: the `shared_gpu` and `local_only` cases, `test_w2_54_green_here.py`, the time-limit case on this repository, W1-21's real-models case, `gov rebuild` and `gov check` are the lead's: leave them out and say so.
- The guard refuses here-documents and unresolvable variables in Bash write targets (and may refuse Python's `**` unpacking inside a Bash command): write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**`.
- **What you may change:** `tests/acceptance/W2-54/**` only (in practice `w2_54_support.py`, `test_w2_54_audit_report.py` and the README). No other folder. The lead compares the tree before and after your session.
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): KPI success line S4 (the `audit-report` type, "nothing of W2-02's other types").
- DEC-874 in `docs/DECISION_REGISTER.md` (search for `### DEC-874`).
- `tests/acceptance/W2-54/README.md` (its section "Run 5 (DEC-874)"), `tests/acceptance/W2-54/test_w2_54_audit_report.py` and `w2_54_support.py` (the run-5 helpers).

## DEC-874 item 1, as decided

KPI S4 is about W2-54's own change, not about the tree: **W2-54's own commits bring in no schema file and no type of W2-02's beyond `audit-report`, which holds before and after W2-02 merges.** W2-02's branch commit `4ce16df2` holds W2-02's types merged with `w2/integrate` (W2-02's merge-back `666f56d1` resolved `src/gov/check/schema.py` to W2-02's side); every W2-54 commit is among its ancestors.

## What the first review found (a described behaviour, DEC-136)

- **The `[…-4ce16df2]` parametrisations of `test_w2_02_s_other_types_are_judged_as_an_unknown_type` do not read `4ce16df2`'s history.** The readings of the lines W2-54's own commits add to core-schema's module, and of W2-54's last own commit to that module, give the same answer for `4ce16df2`, for `HEAD` and for a revision that does not exist: they read the history of the checked-out branch whatever history the case names. So "passes on `4ce16df2`" is not shown for this case. (The file case `test_no_schema_file_of_w2_02_s_other_types_comes_with_it` does read the named history.)
- **When those readings do read `4ce16df2`'s history** (as the reviewer did, redirecting only the case's git reads), all four parametrisations fail with "no commit of W2-54's own in HEAD touches src/gov/check/schema.py". A history limited to that one file follows only one side of W2-02's merge-back (the side whose module the merge kept, W2-02's) and never reaches W2-54's own commit `4f753c72` that added the `audit-report` type to it; with every commit of the history read, it is found. The same would happen on `w2/integrate` once W2-02 merges into it, and on W2-02's branch after its re-merge: DEC-874's next steps would go red on this case with no wrong change of W2-54's.
- What should happen: each parametrisation reads the history it names; the case holds on `HEAD` and on `4ce16df2` (and on any history in which another ticket's merge keeps its own side of a file W2-54 changed); it still fails, naming the commit and line, when W2-54's own commit adds `close` or `adoption-verdict` to core-schema's type map or standalone types.

## What you change

- Correct the reading(s) used by `test_w2_02_s_other_types_are_judged_as_an_unknown_type` (and any other run-5 helper with the same fault) so that the named history is what is read, and every own commit of it is found whatever merges lie between, as the file case's reading already does. Your choice how; state it in the README's "Run 5 (DEC-874)" section, with a short note "second batch": what was wrong, what changed.
- **Prove it in the case's own self-check** (the built histories your fixture already makes): add (1) a built history in which a merge of another `Task:` keeps its own side of the module W2-54's own commit changed (the shape of W2-02's merge-back), on which the reading still finds W2-54's own commit and the case passes; and (2) a check that a history that does not exist is an error, not a pass.
- **No other expectation changes.** The case's assertions (no own added line names the type; core-schema, as W2-54's last own commit to the module leaves it, judges the record as an unknown type) stay as they are; the file case and every other case of the file stay as they are; test ids keep their names; nothing is deleted or skipped. The commit carries `Rewrite-Reason: DEC-874`.

## Runs (each to its end, never `-x`)

1. Step 0 and the start checks; the `gov.__file__` line.
2. Show the fault first, before your change: a throwaway in your temporary folder (written with the Write tool) that calls the case's readings with a revision that does not exist and with `4ce16df2`, and prints what they return.
3. After your change: the three corrected cases (all parametrisations, `-v`); then `tests/acceptance/W2-54/test_w2_54_audit_report.py` in full (expected: all green but `test_core_schema_is_green_on_this_repository_with_w1_43_untouched`, red on W2-53's close record of type `close`, which only W2-02 defines — known, not yours to change); then `tests/acceptance/W2-54` with `-m "not local_only and not shared_gpu" --ignore=tests/acceptance/W2-54/test_w2_54_green_here.py --deselect tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit` (the lead's), file by file if needed.
4. The throwaway of step 2 again, after the change: `4ce16df2` now gives W2-54's own commit `4f753c72`; a revision that does not exist is an error.
5. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header`: quote its last line (no collection error).
6. Name every case that is not green, with its output.

## Commit

Commit only your test paths, one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "W2-54 (DAEO-0rfi): run 5, second batch: <what>" --trailer "Task: DAEO-0rfi" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-773" --trailer "Rewrite-Reason: DEC-874 (orchestrator, delegated, 2026-10-20): <...>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

In the fields: the sandbox check's result first; your commit's hash; what the readings returned before and after (steps 2 and 4); each changed helper or case with what it read before and after (no other expectation lowered); the runs with their counts; the `gov.__file__` line; the collection's last line; whether you used `gov retrieve`; the guard read refusals you met (DEC-849); any package.
