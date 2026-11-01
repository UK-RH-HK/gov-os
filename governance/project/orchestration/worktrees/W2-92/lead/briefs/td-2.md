# Brief: independent test designer, W2-92 (DAEO-n0wb), run 2 (one revision under DEC-1006, P-W2-92-2)

You are a fresh Independent Test Designer (MR-3). Ticket: DAEO-n0wb (W2-92), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-92-tests` on branch `w2/W2-92-tests` (DEC-963); you never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-92`). Your budget is about 60 minutes.

## Step 0, before any work

Run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-n0wb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-92-tests` and `w2/W2-92-tests`). If anything differs, stop and say so. You were started in the old launch form (not sandboxed) because this suite uses the code-graph tool, whose daemon folder `/tmp/gov-cbm-<uid>` is read-only inside the sandbox; a tripwire compares the trees before and after you.

## The one change (DEC-1006, P-W2-92-2 (a), decided by the CTO)

The suite `tests/acceptance/W2-92/` was written by an earlier test designer of this ticket (commit `5679104a81d9`). Its case `test_w2_92_fail_closed.py::test_f1_a_code_index_that_cannot_answer_is_named_and_the_rest_is_returned` (three parameters: never indexed, tool cannot read it, tool not on PATH) checks, with the code index broken, that the bundle for the question `w92_leaf` still holds the lexical route's evidence, and names `app/leaf.py`, `app/middle.py` and `app/top.py`. In the planted project, `app/top.py` never contains the word `w92_leaf` (it imports and calls `w92_mid`), so the lexical route cannot return it: the lead's probe with the base code (`7ca16b19df3f`, where the new routes do not exist) on the same planted store returned `app/leaf.py` and `app/middle.py` spans only. The decision: **set f1's expected set to today's lexical evidence for `w92_leaf`, lowering nothing else.** "Today's" means what the existing lexical route answers for that question on that planted store, with the new routes absent.

- Establish today's lexical evidence yourself, without reading this ticket's implementation: either from the planted files (which planted files contain the word, as the lexical route matches it) or by running the base code against the planted store: the clone `/home/usain/gov-os-runs/W2-92/base` is at `7ca16b19df3f` (before any of this ticket's code), and `PYTHONPATH=/home/usain/gov-os-runs/W2-92/base/src` runs it. Write nothing in that clone (it is the measure's control). Prefer a form that stays valid as the implementation changes: for example, the expected set computed in the test from the planted files' text, or the paths the base answered, written into the test with a comment saying where they came from.
- Change only f1's expected set (and its comment and the README's line for f1). Every other assertion of f1 (the facet named not available with a reason, the answer not failing) and every other case stays exactly as it is. No other test is revised.
- Then run your suite to its end (never `-x`): `cd /home/usain/gov-os-worktrees/W2-92-tests && TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src python3 -m pytest tests/acceptance/W2-92 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, and give the counts. (That `src/` holds the ticket's run-1 code; you run it, you never read it. Expect f3 and possibly others red there: the engineer is changing the code in parallel; report the names of the failing cases and their one-line messages, nothing more.) Also run the same command with `PYTHONPATH=/home/usain/gov-os-runs/W2-92/base/src` and say whether f1's three cases now fail at the base only for their facet check (the code route does not exist there), not for the evidence.
- Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once before committing: no collection error.

## Standing rules (read first)

- Write nothing outside `tests/acceptance/W2-92/` in your worktree, except temporary files under `/tmp/gov-os-lead-W2-92/td2/` (your temp folder; pass `TMPDIR=/tmp/gov-os-lead-W2-92` to every test run) and pytest's own temporary folders.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground past a few minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. Your tests, once merged into the ticket's worktree and run from there, must exercise that worktree's code (the README already says how; keep it so).
- **Memory first (DEC-836, DEC-963):** before reading files at random, ask `gov retrieve` from the integration branch's store only: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; that store holds `w2/integrate`). Never this ticket's worktree's store, never its files. For what changed since that store's refresh, read `w2/integrate` itself with `git show w2/integrate:<path>`. **DEC-860:** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget; never one giant query or context. **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/retrieval/graph_route.py`, `src/gov/retrieval/code_route.py`, `src/gov/retrieval/retrieve.py`, `tests/unit/retrieval/test_w2_92*`, `docs/research/W2-92-memory-measure.md`), and name in your return any such result you were served.
- **Policy 2 (DEC-820):** reads are open, writes closed. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read this ticket's implementation (the files `git -C /home/usain/gov-os-worktrees/W2-92 diff --name-only w2/integrate...w2/W2-92` names, other than your own tests), by any tool, in any tree or commit; (d) the hidden half of any evaluation set (`--part hidden`, the hidden questions' files), by whoever is measured by it: never read or run it.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under `/tmp/gov-os-lead-W2-92/td2/` written with the Write tool. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). Tests that need a repository build a temporary one from scratch. Never this repository's store. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Install nothing (a needed tool is a P1 package in your return). No subagents that write. Never write `.gov-runtime/**`.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Scratch budget (DEC-898):** your share is 2 GB and 100,000 files and folders, outside the tracked tree (your temp folder included). Clean up each temporary tree you make as soon as it is no longer needed; measure with `du -s --inodes /tmp/gov-os-lead-W2-92/td2` and `du -sh` before you return and give the figures.

## Commit

The git hooks are off: before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, with the trailers in the final block:

    git commit -m "W2-92: f1's expected set is the lexical route's evidence for w92_leaf" --trailer "Task: DAEO-n0wb" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-860, CAP-12" --trailer "Rewrite-Reason: DEC-1006 (P-W2-92-2)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-92

After it, `git log --oneline -2` and `git status --short` (clean).

## Return

Your commit's hash (12 digits); the diff's size; the expected set before and after and where the new one comes from; the suite's counts at the run-1 code and at the base, with the failing names; the guard refusals you met; whether you used `gov retrieve` and for what; any P-R1 result you were served; your scratch measure.

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
