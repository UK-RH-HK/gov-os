# Brief: engineer, W2-92 (DAEO-n0wb), run 2, batch 8 (a red in the builder tests)

You are a fresh engineer. Ticket: DAEO-n0wb (W2-92), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-92` on branch `w2/W2-92`. The routes are built and committed (`src/gov/retrieval/graph_route.py`, `src/gov/retrieval/code_route.py`, the route list and the record-graph read in `src/gov/retrieval/retrieve.py`, builder tests `tests/unit/retrieval/test_w2_92_routes.py`; final code `d72c96fc029c`). Read them and `git log -p 7ca16b19df3f..HEAD -- src tests/unit` first. Your budget is about 40 minutes.

## Step 0, before any work

Run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-n0wb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-92` and `w2/W2-92`). If anything differs, stop and say so. You were started in the old launch form (not sandboxed), as the earlier batches were, because the code route needs the code-graph tool; a tripwire compares the trees before and after you.

## The failing output (the lead's scoped run at `fd03541c042d`, and alone)

`TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src python3 -m pytest tests/unit/retrieval/test_w2_92_routes.py -q -p no:cacheprovider`: **5 failed, 35 passed**, in a plain serial run of the whole file and in the scoped parallel run:

- `test_a_symbol_is_asked_in_small_pages_and_its_spans_join_as_chunks[Who calls rrf?]`: `AssertionError: assert set() == {'query_graph...search_graph'}`
- `test_a_plain_word_joins_only_with_a_code_cue[Where is rrf defined?-^(rrf)$]`: `IndexError: list index out of range`
- `test_a_plain_word_joins_only_with_a_code_cue[What are the callers of rrf?-^(rrf)$]`: `IndexError: list index out of range`
- `test_a_plain_word_joins_only_with_a_code_cue[Does \`helper\` reach rrf?-^(helper|rrf)$]`: `IndexError: list index out of range`
- `test_a_plain_word_joins_only_with_a_code_cue[Is rrf faster than fuse_scores?-^(fuse_scores)$]`: `IndexError: list index out of range`

Each passes when run alone or with only its own test function; the file's first failure follows the record-route title tests (`test_only_ids_and_titles_…`, `test_a_records_title_…`, `test_a_title_read_once_…`). So something that one process keeps between tests (the tool sessions kept per process, the front-matter cache, or another module-level state) makes a later question send no request to the planted session. Find the cause. If it is in the product (a question answered from state that belongs to another root, index or tool), fix the product: that is a real defect of a per-process cache (KPI 4: two runs on one store give the same bundle; and no answer from a stale session or cache). If it is only the tests' isolation (a fixture that patches the tool's session but leaves a cached one in place), fix the tests so each starts from a clean process state. Say which, with the evidence. Then run the whole file serially and with `-n 4`, and `tests/unit/retrieve`, `tests/unit/retrieval`, `tests/unit/closure` and `tests/unit/close/test_context.py` (foreground, `TMPDIR=/tmp/gov-os-lead-W2-92`, never `-x`): all green.

Change nothing else. In particular, leave the record-graph read's behaviour exactly as it is (a decision about it is pending with the CTO), and never touch `tests/acceptance/**`.

## Standing rules (read first)

- Write nothing outside your allowed paths in this worktree (`src/gov/retrieval/graph_route.py`, `src/gov/retrieval/code_route.py`, `src/gov/retrieval/retrieve.py`, `tests/unit/retrieval/test_w2_92*`), except under `/tmp/gov-os-lead-W2-92/eng8/` (your temp folder; pass `TMPDIR=/tmp/gov-os-lead-W2-92` to every test run), pytest's own temporary folders, and the code-graph tool's own daemon folder.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground past a few minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory first (DEC-836):** before reading files at random, ask `gov retrieve`: `cd /home/usain/gov-os-worktrees/W2-92 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src python3 -m gov.cli.main retrieve "<question>" --json`. **DEC-860:** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget; never one giant query or context. **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; never one query over the tool's row cap.
- **Policy 2 (DEC-820):** reads are open, writes closed. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-92/`, by any tool; you may run those tests through `gov accept` and see their names, results and failure messages, never their source; (d) the hidden half of any evaluation set (`--part hidden`, the hidden questions' files), by whoever is measured by it: never read or run it.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under `/tmp/gov-os-lead-W2-92/eng8/` written with the Write tool. A refused form is not retried in another disguise. No `rm`.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Never copy the repository or a folder of it; tests that need a repository build a temporary one from scratch. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never run `gov rebuild`, never `gov rebuild --no-embeddings`, never `gov close`, `gov adopt` or `gov pause`. Install nothing (a needed tool is a P1 package in your return). No subagents that write. Never write `tests/acceptance/**` or `.gov-runtime/**`.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Scratch budget (DEC-898):** your share is 2 GB and 100,000 files and folders, outside the tracked tree. Measure `du -s --inodes /tmp/gov-os-lead-W2-92/eng8` and `du -sh` before you return.
- Never run the full suite (DEC-968).

## Commit

The git hooks are off: before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block:

    git commit -m "W2-92: <what you fixed, in one line>" --trailer "Task: DAEO-n0wb" --trailer "Role: engineer" --trailer "Implements: DEC-957, DEC-859, DEC-860, DEC-424, CAP-12, CAP-13, CAP-18" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

After it, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the cause (product or tests) with its evidence; the files changed with lines added and removed; the tests you ran with their results; the guard refusals you met; whether you used `gov retrieve` and for what; your scratch measure.

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
