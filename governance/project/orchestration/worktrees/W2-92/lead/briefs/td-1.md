# Brief: independent test designer, W2-92 (DAEO-n0wb), run 1

You are a fresh Independent Test Designer (MR-3). Ticket: DAEO-n0wb (W2-92), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-92-tests` on branch `w2/W2-92-tests` (DEC-963); you never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-92`). You write the ticket's acceptance tests from its KPI lines and its sources, in parallel with the engineer, and you show them red. Your budget is about 90 minutes.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-n0wb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-92-tests` and `w2/W2-92-tests`). If anything differs, stop and say so.
- You were started in the old launch form (not sandboxed) because this ticket's tests may need the code-graph tool, whose daemon folder `/tmp/gov-cbm-<uid>` is read-only inside the sandbox. A tripwire compares the trees before and after you: write nothing outside `tests/acceptance/W2-92/` in your worktree, except temporary folders under `/tmp/gov-os-lead-W2-92/` (your temp folder; pass `TMPDIR=/tmp/gov-os-lead-W2-92` to every test run) and pytest's own temporary folders.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. Your tests, once merged into the ticket's worktree and run from there, must exercise that worktree's code: the README says how (tests that start `gov` as a child process pass the running tree's `src/` on `PYTHONPATH`; tests that import `gov` import it from the `PYTHONPATH` the runner sets).
- **Memory first (DEC-836, DEC-963):** before reading files at random, ask `gov retrieve` from the integration branch's store only: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; that store holds `w2/integrate`). Never this ticket's worktree's store, never its files. For what changed since that store's refresh, read `w2/integrate` itself with `git show w2/integrate:<path>`. **DEC-860:** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget; never one giant query or context. **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/retrieval/graph_route.py`, `src/gov/retrieval/code_route.py`, `src/gov/retrieval/retrieve.py`, `tests/unit/retrieval/test_w2_92*`, `docs/research/W2-92-memory-measure.md`), and name in your return any such result you were served. (`retrieve.py` as it stands on `w2/integrate` is the existing public interface and you may read it there with `git show w2/integrate:src/gov/retrieval/retrieve.py`; you never read any version of it from the ticket's branch.)
- **Policy 2 (DEC-820):** reads are open, writes closed. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read this ticket's implementation (the files `git -C /home/usain/gov-os-worktrees/W2-92 diff --name-only w2/integrate...w2/W2-92` names, other than your own tests), by any tool; (d) the hidden half of any evaluation set (`--part hidden`, the hidden questions' files), by whoever is measured by it: never read or run it.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under `/tmp/gov-os-lead-W2-92/td/` written with the Write tool. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). Tests that need a repository build a temporary one from scratch (`git init` in a temporary folder, single named files written by the test). Never this repository's store. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only, clone into a temporary folder, and are marked `local_only` (you should not need them).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Install nothing (a needed tool is a P1 package in your return). No subagents that write. Never write `.gov-runtime/**`.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Scratch budget (DEC-898):** your share is 4 GB and 200,000 files and folders, outside the tracked tree (your temp folder included). Clean up each temporary tree as soon as it is no longer needed; measure with `du -s --inodes /tmp/gov-os-lead-W2-92/td` and `du -sh` before you return and give the figures.
- Never wait in the foreground past a few minutes.

## What you read

- The ticket file `.tickets/DAEO-n0wb.md` (read-only): its KPI lines (success and failure), its `allowed_paths` and its sources.
- Its card in `docs/plan/WAVE_2_WBS.md` (§2, the W2-92 row) and §0 (rules for every ticket).
- `governance/project/orchestration/packages/MEMORY-SPEC-MAP.md`, §A.2 gaps 2 and 3 (named, not searched).
- The sources in `docs/DECISION_REGISTER.md` and `docs/contract/contract.yaml`: DEC-957, DEC-954 (Q9c), DEC-859, DEC-860, DEC-424, DEC-833, CAP-12, CAP-13, CAP-18; also DEC-900.
- The public interfaces the ticket must work with, as they stand on `w2/integrate`: `gov retrieve` (its CLI and its JSON bundle: `stopping_reason`, `evidence`, `batches`, `merge`, `expansions`, `gaps`, `facets`, `budget`, `continuation`), the Python function `gov.retrieval.retrieve.retrieve(root, query, ...)`, `gov rebuild` (which builds a project's record store, lexical and semantic indexes and code index), `gov closure` and the code index wrapper `gov.codeintel` (public functions only). Earlier acceptance suites show how a planted repository, its store and its code index are built in a temporary folder: `tests/acceptance/W1-20/` (closure over records and code, with a stub tool), `tests/acceptance/W1-21/` (retrieve), `tests/acceptance/W2-87/` (retrieve with a register), `tests/acceptance/W1-16/` (the code index). You read no private part of an implementation to learn what a test should expect.

## The behaviour to test (the KPI lines, in their words)

Today a plain question to `gov retrieve` uses only the lexical and semantic routes; the record closure joins only when start ids are given with `--ticket` or `--id`, and the code graph's callers and definitions come only from `gov closure` or `gov impact` given a symbol. This ticket adds two routes to plain-question retrieval:

1. **The record route.** An id found in a plain question (a decision id `DEC-n`, a Contract id `CAP-n`, a ticket id, or a W2 id) or a record title found in it becomes a start id, so the record closure joins the fusion at radius 0 or 1, without `--ticket` or `--id`: the evidence of the named record (and, at radius 1, of its near records) reaches the bundle. A question that names no record gets today's bundle, item for item. [DEC-957, DEC-954 Q9c, CAP-13, CAP-18]
2. **The code route.** A symbol name found in a plain question is asked of the code index (its definition, callers and callees) with the code-graph tool's own traversal, in small, paged answers, and the file spans it returns join the fusion as a route: for "who calls X", the callers' spans reach the bundle. A question that names no symbol gets today's bundle. [DEC-957, DEC-859, CAP-12, CAP-18]
3. **Fail closed per route.** A missing or unreadable code index, or a missing or unreadable record store, is named in the bundle's stopping reasons for that route (the bundle says which route could not answer and why), never silently "ok", and never a failure of the whole answer (the other routes' evidence is still returned). [DEC-957, DEC-860]
4. **Nothing else changes.** The budget, the batches, the continuation, DEC-424's records ahead (failure and lesson records in a ticket's closure come first) and W2-87's authority order are as today; two runs on one store give the same bundle. [DEC-424, DEC-860]

Failure lines (each must be shown refused or absent by a test):
- A question that names no record or symbol gets a different bundle than today.
- A whole-graph query to the code-graph tool, or one over the tool's row cap (an answer asked for more rows than the tool's cap). A stand-in tool on `PATH` that records every request it is sent is one way to observe this.
- A missing index reported ok, or failing the whole answer.
- (The measure's line, "a figure reported without the other, or the hidden half read or run", is the lead's re-measure record, not a test of yours; say so in the README.)

Key edge cases for STANDARD: an id the store does not hold (names no record: today's bundle); an id given both in the question and with `--id`; a question naming both a record and a symbol; determinism across two runs; the continuation of a batched answer when a new route contributed.

If a KPI line is ambiguous (for example, what "today's bundle, item for item" must compare, or how a missing record store can be told apart from a store that refuses the whole answer today), do not guess: test what is unambiguous and return the rest as a package with your recommendation and confidence.

## What you write

- Only inside `tests/acceptance/W2-92/`. No earlier ticket's test is revised unless a KPI line names it; if you think one must be, name it as a package.
- STANDARD (DEC-221): every KPI line's success and failure, plus the key edge cases above; no combinatorial expansion. Behaviour through public interfaces, never internals. Deterministic, no network; a test that needs the embedder or the code-graph tool either uses a stand-in or is skipped with a stated reason only where the real tool is absent (say which in the README).
- "Today's bundle" is observable without reading the new code: the bundle the same question gets from the same planted store through the existing interface with the new routes absent, for example the base code's answer recorded in the test, or the bundle of a question with the named words removed; choose a form that stays valid once the implementation lands, and explain it in the README.
- A README mapping each KPI line to its tests and its expected red reason at the base `7ca16b19df3f`, and how the tests exercise the running tree's `src/` (DEC-732).
- Red first: run your suite to its end (never `-x`) in your worktree: `TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src python3 -m pytest tests/acceptance/W2-92 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`; the tests fail for the reason the README states (the success lines red; failure lines that the base already satisfies may pass, and the README says which).
- Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once before committing: no collection error (for example, no test module or package name that clashes with another suite's or the standard library's).

## Commit

The git hooks are off: before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths (`git add tests/acceptance/W2-92` then `git commit -m "<subject>" -- tests/acceptance/W2-92` style), with the trailers in the final block:

    git commit -m "W2-92: acceptance tests for the record and code routes of plain-question retrieval" --trailer "Task: DAEO-n0wb" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-859, DEC-860, DEC-424, CAP-12, CAP-13, CAP-18" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, `git log --oneline -2` and `git status --short` (clean).

## Return

Your commit's hash (12 digits); the test count; the KPI lines with their tests; the red reason as you saw it, with the counts; every earlier test you would revise, with its reason; any package; the guard refusals you met; whether you used `gov retrieve` and for what; any P-R1 result you were served; your scratch measure.

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
