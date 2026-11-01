# Brief: independent test designer, W2-92 (DAEO-n0wb), run 2, batch 3 (the README map's test names, for gov accept)

You are a fresh Independent Test Designer (MR-3). Ticket: DAEO-n0wb (W2-92), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-92-tests` on branch `w2/W2-92-tests` (DEC-963); you never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-92`). Your budget is about 40 minutes.

## Step 0, before any work

Run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-n0wb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-92-tests` and `w2/W2-92-tests`). If anything differs, stop and say so. You were started in the old launch form (not sandboxed) because your check runs this suite, which uses the code-graph tool, whose daemon folder `/tmp/gov-cbm-<uid>` is read-only inside the sandbox; a tripwire compares the trees before and after you.

## The one change: the map's test names in a form `gov accept` matches

`tests/acceptance/W2-92/` (30 cases) passes in full at the ticket's head: 30 passed, 0 failed. Yet `gov accept DAEO-n0wb` (W2-96's runner, `src/gov/accept/runner.py` on `w2/integrate`: `parse_map`, `matches`, `names_a_test`, `_report`; its form is its own, and you may read it) gives every KPI line the outcome "fail" and exits 3. The reason: a KPI line fails when an item of its README map row names a test that no collected case matches. These items of `tests/acceptance/W2-92/README.md` match no case:

- success-1: `test_r1_a_record_named_in_a_plain_question_reaches_the_bundle[decision id, contract id, ticket id, W2 id, record title]`
- success-2: `test_c3_...`
- failure-2: `test_c3`, `test_c4`, `test_c5_a_question_naming_no_symbol_of_the_index_sends_no_whole_graph_query[unknown, none]`
- success-3 and failure-3: `test_f1_a_code_index_that_cannot_answer_is_named_and_the_rest_is_returned[never indexed, tool cannot read it, tool not on PATH]`
- success-4 and failure-1: `test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle[plain, batched, unknown id, unknown symbol, ticket]`, `test_u3_two_runs_on_one_store_give_the_same_bundle[new routes, plain]`

Rewrite only these items so that each names its cases in a form the runner matches (for example the full function name without the parameter list, or one item per parameter id exactly as pytest names it), keeping every row's KPI line and every test it maps exactly as now: no test added to or removed from any line, no line's red reason changed except where its test names are written, no test file touched, nothing lowered. Keep the README readable for a human reader (the parameter ids may stay in the red-reason column).

Check it before you commit: `cd /home/usain/gov-os-worktrees/W2-92-tests && TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src python3 /tmp/gov-os-lead-W2-92/td3/accept_missing.py` must print no `MISSING` line (the lead's script: it parses the map with the runner's own functions and matches it against the collected cases). Then run `gov accept` once in your worktree: `cd /home/usain/gov-os-worktrees/W2-92-tests && TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src python3 -m gov.cli.main accept DAEO-n0wb --json`, and give each line's outcome and counts. (That `src/` holds the ticket's code: you run it, you never read it.) Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once: no collection error.

## Standing rules (read first)

- Write nothing outside `tests/acceptance/W2-92/README.md` in your worktree, except temporary files under `/tmp/gov-os-lead-W2-92/td3/` (your temp folder; pass `TMPDIR=/tmp/gov-os-lead-W2-92` to every run) and pytest's own temporary folders.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground past a few minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory first (DEC-836, DEC-963):** before reading files at random, ask `gov retrieve` from the integration branch's store only: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; that store holds `w2/integrate`). Never this ticket's worktree's store, never its files. For what changed since, read `w2/integrate` itself with `git show w2/integrate:<path>`. **DEC-860:** a large question is taken in batches (`--batch-size`, then `--continue <token>`); never one giant query or context. **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; never one query over the tool's row cap.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/retrieval/graph_route.py`, `src/gov/retrieval/code_route.py`, `src/gov/retrieval/retrieve.py`, `tests/unit/retrieval/test_w2_92*`, `docs/research/W2-92-memory-measure.md`), and name in your return any such result you were served.
- **Policy 2 (DEC-820):** reads are open, writes closed. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read this ticket's implementation (the files `git -C /home/usain/gov-os-worktrees/W2-92 diff --name-only w2/integrate...w2/W2-92` names, other than your own tests), by any tool, in any tree or commit; (d) the hidden half of any evaluation set (`--part hidden`, the hidden questions' files), by whoever is measured by it: never read or run it.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under `/tmp/gov-os-lead-W2-92/td3/` written with the Write tool. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). Never this repository's store. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Install nothing (a needed tool is a P1 package in your return). No subagents that write. Never write `.gov-runtime/**`.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Scratch budget (DEC-898):** your share is 1 GB and 50,000 files and folders, outside the tracked tree. Measure with `du -s --inodes /tmp/gov-os-lead-W2-92/td3` and `du -sh` before you return and give the figures.

## Commit

The git hooks are off: before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only the README, with the trailers in the final block:

    git commit -m "W2-92: the README map names its tests in the form gov accept matches" --trailer "Task: DAEO-n0wb" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-860" --trailer "Rewrite-Reason: DEC-959 (gov accept reads the map per KPI line; no expectation changed)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-92/README.md

After it, `git log --oneline -2` and `git status --short` (clean).

## Return

Your commit's hash (12 digits); each item before and after; the checker's output; `gov accept`'s per-line outcomes and counts; the guard refusals you met; whether you used `gov retrieve` and for what; any P-R1 result you were served; your scratch measure.

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

Your final message gives these twelve fields first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), with any machine-readable payload after them. Refused twice for the same call: stop and say so.
