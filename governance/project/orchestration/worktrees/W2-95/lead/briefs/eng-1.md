# Brief: engineer, DAEO-57hm (W2-95), run 1

You are a fresh engineer. Ticket: DAEO-57hm (W2-95), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-95` on branch `w2/W2-95`. You build the ticket's code to fulfil its specification and KPIs (never to make the tests pass); the independent test designer writes the acceptance tests at the same time, in another worktree, from the same KPIs (DEC-959 item 7, DEC-963).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-57hm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (do not delete anything).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-57hm`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-95` and `w2/W2-95`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no tag. The one merge you make is the TESTS-READY merge below, with `--no-ff`.
- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. Here <this worktree> is `/home/usain/gov-os-worktrees/W2-95`, so: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src python3 -c "import gov; print(gov.__file__)"`.
- **Reads are open, with four exceptions (DEC-820):** (a) never read or print secrets or keys; (b) never read the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **never read this ticket's acceptance tests**: nothing under `tests/acceptance/W2-95/` by any tool, in this worktree, in `/home/usain/gov-os-worktrees/W2-95-tests`, or on the branch `w2/W2-95-tests` (no `git show`, `git diff` or `git log -p` of them). You may run them and read their results (names, pass or fail, failure messages), never their source; (d) never read the hidden half of any evaluation set by which you are measured.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take such a refusal; never look for another form; search named folders instead. Count the refusals you met and give them in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src python3 -m gov.cli.main retrieve "<question>" --json`, run in this worktree. **Never one giant query or context (DEC-860):** take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **This worktree's store is still being rebuilt as you start**, and inside the sandbox `gov retrieve` may try to reach a blocked network and hang: run it as `timeout 120 env PYTHONPATH=… python3 -m gov.cli.main retrieve …`, and if it answers STORE_MISSING, hangs or times out, say so in your return and read the files this brief names instead.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under your session's temp folder with the Write tool, and run that file. Write files with the Write and Edit tools and literal absolute paths. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need for the ticket, do not work around it: return it as a package.
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder (not needed here). Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); a test that needs a repository builds a temporary one from scratch. No clone, copy or programme file under any `.gov-runtime/` folder. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` and your return give commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your scratch budget (DEC-898):** 5 GB and 250,000 files and folders, outside the tracked tree (your session's temp folder, which `gov launch` sets, plus pytest's temp folders). Keep pytest's own retention (no `--basetemp`); use `-o tmp_path_retention_policy=failed`. Remove every temporary repository you made as soon as it is no longer needed. Measure (`du -s --inodes`, `du -sh` of your temp folder) at the end and give the figures in your return.
- **The git hooks are uninstalled until W2-08:** before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`.
- Install nothing: a tool you need is a package (P1, installs are the owner's). No subagents that write. You never ask the owner anything; a question is a package in your return. Never run `gov close`, `gov adopt` or `gov pause`. Never write `governance/project/path-map.yaml` (shared; owner-only lists).

## What you read

- The ticket file `.tickets/DAEO-57hm.md` (read-only): its KPI lines and its `allowed_paths`.
- The fault, as filed: `governance/project/orchestration/packages/P-W2-H064.md`, and row W2-H064 in `docs/plan/WAVE_2_LIST.md`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-959 (item 9, item 7), DEC-954 (Q9f), DEC-694, DEC-381; DEC-135 (proportion).
- The code the ticket touches: `src/gov/check/pathmap.py` (the check, `core-pathmap`); how `gov check` runs it (`template/governance/kernel/checks/core-pathmap.yaml`, `src/gov/check/runner.py`: the command's JSON on stdout and its exit code become the findings and the status); the path map's schema (`template/governance/kernel/schemas/path-map.schema.json`, `src/gov/config/path_map_schema.py`) and loader (`src/gov/config/loader.py`). The path map's pattern language, as the schema states it: `*` stays inside one folder, `**` crosses folders; other readers of the path map already match that way (for example `src/gov/secrets/__init__.py`'s `_matches`).

## What to build (the KPIs, and the lead's readings)

1. core-pathmap reads `namespaces` in the form the schema states (a mapping of a name to its entry, whose `paths` is a list of patterns) and the older list form (a list of entries each with `name` and `paths`). For each tracked path (`git ls-files`) it names the path when it matches no namespace or more than one, with the namespaces it matched; patterns are judged in the path map's language (`*` inside one folder, `**` across folders), not with `fnmatch`'s `*`, which crosses folders. Keep the findings this check gives today for those two cases (their codes and fields): they are its public interface.
2. **Fail closed:** a path map that is missing where the project declares one, cannot be read (an OS error, not UTF-8), cannot be parsed (broken YAML), whose top level is not a map, that has no `namespaces`, whose `namespaces` is of neither form, or whose entries are of a form the schema does not state, is a finding naming the cause (the path map's file and what is wrong); the check is never green on it. Listing the tracked paths failing (git not answering) is a finding too, never green. **The lead's reading of "where the project declares one" (to be confirmed by the CTO; say in your return if you see it otherwise):** a repository that has the folder `governance/project/` declares a path map at `governance/project/path-map.yaml`, and a missing file there is a finding; a folder with no `governance/project/` is no Gov OS project, and the check stays as it is today for it (the existing unit test `tests/unit/check/test_check.py::test_pathmap_no_pathmap` expects no finding for such a folder).
3. The same check validates a refactored path map of an adopted repository: any repository's `governance/project/path-map.yaml`, judged against that repository's tracked paths.
4. Nothing else in `gov check` changes (DEC-381): touch only `src/gov/check/pathmap.py`. The command, run from a repository's root, keeps printing its findings as a JSON list and exiting non-zero when there are findings, zero when green.
5. Proportion (DEC-135): about 60 lines; no code for edge cases beyond these lines. Never make a check fail open.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/check/pathmap.py` and `tests/unit/check/test_w2_95*` (your builder tests, test-driven, as regression evidence: planted path maps in temporary git repositories; never this repository's own path map). Never `tests/acceptance/**` (MR-3). A test you think is wrong is a package, never edited and never worked around.
- Run your unit tests with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src python3 -m pytest tests/unit/check -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to the end (never `-x`).
- Commit your work before you run anything long, with the trailers in the final block:

      git commit -m "W2-95 (DAEO-57hm): core-pathmap reads the mapping form and fails closed" --trailer "Task: DAEO-57hm" --trailer "Role: engineer" --trailer "Implements: DEC-959" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  `Implements:` holds only decision ids the register holds (DEC-n) or Contract ids (CAP-n), never a word. Check `git log --oneline -2` and `git status --short` after each commit.

## TESTS-READY (DEC-959 item 7, DEC-963)

When you have built and committed, check whether the file `/home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/TESTS-READY` exists. If it does not yet exist, wait for it in the foreground with short checks (`sleep 60` then look again, each command well under ten minutes) for up to 60 minutes in all; if it still does not exist, return and say so (the lead will run the acceptance tests itself). When it exists (it names the tests' commit):
1. Merge the tests branch: `git merge --no-ff w2/W2-95-tests -m "W2-95 (DAEO-57hm): merge the acceptance tests" --trailer "Task: DAEO-57hm" --trailer "Role: engineer"` (if your git refuses `--trailer` on merge, put the two trailer lines at the end of the message with `-m` twice instead). Do not read the merged test files.
2. Run the acceptance tests once, reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src python3 -m pytest tests/acceptance/W2-95 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rA` to the end. Report the counts and the names of any failing case with its failure message.
3. If a case fails, fix the code to the spec and KPIs (never to the test), commit again, and run the acceptance tests once more. If you believe a failing test contradicts the spec, return it as a package with the failure message; do not bend the code to it.
4. If another ticket's existing test (outside `tests/acceptance/W2-95/`) would need revising because this check now judges what it did not before (a planted repository it expected green), do not change the code to keep it green: name the test and the reason in your return.

## Return

Your commits' hashes (12 digits); the files changed; the tests you ran with their results; the lines added and removed; the `gov.__file__` line; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence); the sandbox check; the read refusals you met; whether you used `gov retrieve`; your scratch measure.

Return one message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
