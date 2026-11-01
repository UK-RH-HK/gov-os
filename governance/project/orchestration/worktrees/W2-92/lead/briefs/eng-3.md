# Brief: engineer, W2-92 (DAEO-n0wb), run 1, batch 3 (repair)

You are a fresh engineer. Ticket: DAEO-n0wb (W2-92), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-92` on branch `w2/W2-92`. The two routes are built and committed on this branch (`46f40ded18a8`, then `fedb871187f7`: `src/gov/retrieval/graph_route.py`, `src/gov/retrieval/code_route.py`, the route list in `src/gov/retrieval/retrieve.py`, `tests/unit/retrieval/test_w2_92_routes.py`); read them and `git log -p 46f40ded18a8^..HEAD -- src tests/unit` first. Your job is the repair below, to the specification and KPI lines, never to the tests. Your budget is about 75 minutes.

## The repair

**A. KPI 2, the code route's purpose (a regression of the last commit).** At `fedb871187f7` the code index is asked only about words shaped as code (backticks, a call, an underscore or an inner capital). KPI 2 says a symbol name found in a plain question is asked of the code index; this ticket exists so that questions like "Who calls rrf?" and "Who calls indexable?" on this repository (the measure's Q11 and Q10; MEMORY-SPEC-MAP gap 3: today Q10's first caller is at rank 25) get their callers through the code route. A plain lowercase name that is a symbol of the code index must take the code route again. At the same time, KPI 2 and DEC-860 still hold for a question whose words name no symbol: today's bundle, and no needless cost (each session of the code-graph tool starts its daemon, about 6 s). How you tell which plain words name a symbol is yours to design; the failure message below shows how the acceptance tests read a name search sent for plain words that name no symbol.

**B. The failing acceptance output at `fedb871187f7`** (23 passed, 7 failed; the failures' messages, and nothing else):

1. `test_w2_92_code_route.py::test_c2_the_code_route_asks_the_tools_traversal_never_the_whole_graph_nor_over_the_cap` — "a whole-graph query was sent to the code-graph tool (DEC-859): [{'tool': 'search_graph', 'args': {'project': 'code', 'format': 'json', 'limit': 50, 'offset': 0, 'qn_pattern': '^(code\\.app\\.middle\\.w92_mid|code\\.app\\.middle\\.w92_side)$'}, 'over_cap': False}]". The question named `w92_leaf`; the request names only its callers.
2. `test_c3_a_question_naming_both_a_record_and_a_symbol_takes_both_routes` and `test_c4_the_command_takes_the_code_route_of_a_plain_question` — the same request, the same message.
3. Three cases of `test_w2_92_fail_closed.py::test_f1_…` and `test_f3_…`: these are with the lead (packages); change nothing for them.
4. Earlier, at `46f40ded18a8`, now passing and to be kept passing: `test_c5_a_question_naming_no_symbol_of_the_index_sends_no_whole_graph_query[none]` — "'harbour tide almanac' sent a whole-graph or over-cap request to the code-graph tool: [{'tool': 'search_graph', 'args': {'project': 'code', 'format': 'json', 'limit': 50, 'offset': 0, 'name_pattern': '^(almanac|harbour|tide)$'}, 'over_cap': False}]".

**C. The callers' and callees' spans.** `trace_path` gives qualified names without spans, and the follow-up lookup by the neighbours' qualified names is what B.1 reports. DEC-859 names `query_graph` among the tool's own traversal: a targeted `query_graph` that names the question's symbol (for example the CALLS edges into and out of that one qualified name, returning each neighbour's file and lines), small (`max_rows` 50) and paged, gives the spans in one answer. Try it. Measure its time on this worktree's code index for `rrf` and `indexable` (the code index is current; ask the tool directly from a scratch script, not through the stale store). If it answers within a few seconds there and keeps every request small and targeted, use it; if not, keep the current form and return the question as a package with your measurements.

Keep everything else that passes passing: KPI 3 (a missing or unreadable code index is named for a question that names a symbol, never silently ok, never a failure of the whole answer); a question that names no record or symbol gets today's bundle in every field; the record title fix. Then run your unit tests, the existing tests in `tests/unit/retrieve`, `tests/unit/retrieval` and `tests/unit/closure`, and `gov accept` once (below), commit, and return. Use `gov retrieve` (below) for anything you need to know about the repository before reading files at random. Report, for "Who calls rrf?" and "Who calls indexable?", whether the code route takes them and which requests it sends (tool, arguments, rows, seconds).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-n0wb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-92` and `w2/W2-92`). If anything differs, stop and say so.
- You were started in the old launch form (not sandboxed) because your work needs the code-graph tool, whose daemon folder `/tmp/gov-cbm-<uid>` is read-only inside the sandbox. A tripwire compares the trees before and after you: write nothing outside your allowed paths in this worktree, except under `/tmp/gov-os-lead-W2-92/eng/` (your temp folder; pass `TMPDIR=/tmp/gov-os-lead-W2-92` to every test run), pytest's own temporary folders, and the code-graph tool's own daemon folder.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground past a few minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory first (DEC-836):** before reading files at random, ask `gov retrieve`: `cd /home/usain/gov-os-worktrees/W2-92 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src python3 -m gov.cli.main retrieve "<question>" --json`. **DEC-860:** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget; never one giant query or context. **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap.
- **Policy 2 (DEC-820):** reads are open, writes closed. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-92/` (nor the branch `w2/W2-92-tests` or the worktree `/home/usain/gov-os-worktrees/W2-92-tests`), by any tool; you may run those tests through `gov accept` and see their names, results and failure messages, never their source; (d) the hidden half of any evaluation set (`--part hidden`, the hidden questions' files), by whoever is measured by it: never read or run it.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under `/tmp/gov-os-lead-W2-92/eng/` written with the Write tool. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it); a throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. Tests that need a repository build a temporary one from scratch. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never run `gov rebuild` (the lead rebuilds; this worktree's store and code index are built), never `gov rebuild --no-embeddings`, never `gov close`, `gov adopt` or `gov pause`. Install nothing (a needed tool is a P1 package in your return). No subagents that write. Never write `tests/acceptance/**` or `.gov-runtime/**`.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Scratch budget (DEC-898):** your share is 6 GB and 300,000 files and folders, outside the tracked tree. Clean up as you go; measure `du -s --inodes /tmp/gov-os-lead-W2-92/eng` and `du -sh` before you return and give the figures.
- Never run the full suite (DEC-968). Your own unit tests and the existing retrieval and closure unit tests are what you run while you build.

## What you read

- The ticket file `.tickets/DAEO-n0wb.md` (read-only): its KPI lines and its `allowed_paths`.
- Its card in `docs/plan/WAVE_2_WBS.md` (§2, the W2-92 row) and §0.
- `governance/project/orchestration/packages/MEMORY-SPEC-MAP.md`, §A.2 gaps 2 and 3 (named, not searched) — the reason for this ticket.
- The sources in `docs/DECISION_REGISTER.md` and `docs/contract/contract.yaml`: DEC-957, DEC-954 (Q9c), DEC-859, DEC-860, DEC-424, DEC-833, CAP-12, CAP-13, CAP-18.
- The code it touches: `src/gov/retrieval/retrieve.py` (the route list: the lexical and semantic answers, and the closure route that today runs only with `--ticket` or `--id`), `src/gov/closure/__init__.py` (the record closure and `depth_of_radius`), `src/gov/records` (the record graph: records, titles, edges), `src/gov/codeintel/__init__.py` (the code-graph tool's wrapper; note that its `definitions`, `callers` and `callees` load the whole graph, which DEC-859 forbids for a question), `src/gov/retrieval/authority.py` (W2-87's order), `src/gov/retrieval/lexical.py` (chunks: read only), `src/gov/retrieval/fusion.py` (rrf: read only). The code-graph tool's own tools are listed by the binary (`codebase-memory-mcp`); this worktree's code index is under `.gov-runtime/codeintel/`.

## What to build (the KPI lines)

1. **The record route** (`src/gov/retrieval/graph_route.py`): an id found in a plain question (`DEC-n`, `CAP-n`, a ticket id `DAEO-xxxx`, or a W2 id, resolved to its ticket) or a record title found in it becomes a start id, so the record closure joins the fusion at radius 0 or 1, without `--ticket` or `--id`. Only ids and titles the record store holds become start ids. A question that names no record gets today's bundle, item for item. [DEC-957, DEC-954 Q9c, CAP-13, CAP-18]
2. **The code route** (`src/gov/retrieval/code_route.py`): a symbol name found in a plain question is asked of the code index (definition, callers, callees) with the code-graph tool's own traversal (`search_graph`, `trace_path`, or a targeted `query_graph`) in small, paged answers, never a whole-graph query and never a request over the tool's row cap; the file spans it returns (mapped from the index's staged copy back to repository paths) join the fusion as a route, as the store's lexical chunks that cover those spans. A question that names no symbol gets today's bundle. [DEC-957, DEC-859, CAP-12, CAP-18]
3. **Fail closed per route:** a missing or unreadable code index, or a missing or unreadable record store, is named in the bundle's stopping reasons for that route (its facet: not available, with a reason that says which and why), never silently ok, and never a failure of the whole answer: the other routes' evidence still comes back. [DEC-957, DEC-860]
4. **Nothing else changes:** the budget, the batches, the continuation, DEC-424's records ahead and W2-87's authority order are as today; two runs on one store give the same bundle (everything sorted, nothing time- or order-dependent). A question that names no record or symbol gets a bundle equal to today's in every field (no new facet, route, gap or stopping reason). [DEC-424, DEC-860]
- **In `retrieve.py`, only the route list changes: one call each** to the two new modules, beside the lexical, semantic and closure routes. The ranking (W2-87's authority order), what is left out (W2-55), fusion and lexical are not touched: W2-13 holds `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/retrieve/**` and the rest of `tests/unit/retrieval/**` (read only for you). If your change needs any other file, stop and return it as a package.
- **An open scope question, not yours to settle:** today a project whose record graph cannot be read refuses every question with `STORE_MISSING`, raised where `retrieve.py` reads the record graph and W2-87's authority order, before any route runs. Meeting KPI 3 for a missing record store would need a change there, outside the route list. Do not make it. Build everything else; if you see how it would be done, describe the smallest change (lines, behaviour) in your return as a package, with your recommendation and confidence.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. Estimate: about 200 lines of code.
- Builder tests only as new files `tests/unit/retrieval/test_w2_92*.py`, as regression evidence (they build a temporary repository; never this repository's store).

## The acceptance tests (DEC-963)

The independent test designer writes `tests/acceptance/W2-92/` in parallel in its own worktree; the lead merges them into this worktree between your batches. If `/home/usain/gov-os-worktrees/W2-92/.gov-runtime/scratch/lead/TESTS-READY` exists, run them once, reading results only, through `gov accept` only: `cd /home/usain/gov-os-worktrees/W2-92 && TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src python3 -m gov.cli.main accept DAEO-n0wb --json`, and report pass or fail per KPI line with the counts. Never run `pytest` on `tests/acceptance/` yourself. If it does not exist, say so and do not wait for it. Commit your work before running any long suite.

## Commit

The git hooks are off: before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block:

    git commit -m "W2-92: repair of the record and code routes (batch 3)" --trailer "Task: DAEO-n0wb" --trailer "Role: engineer" --trailer "Implements: DEC-957, DEC-859, DEC-860, DEC-424, CAP-12, CAP-13, CAP-18" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the files changed; the lines added and removed; the tests you ran with their results; the real-case check; the `gov accept` result if run; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence); the guard refusals you met; whether you used `gov retrieve` and for what; your scratch measure. Your scratch folder `/tmp/gov-os-lead-W2-92/eng/` already holds an earlier batch's probe files; leave them (no `rm` there), and put yours under `/tmp/gov-os-lead-W2-92/eng3/`; `/tmp/gov-os-lead-W2-92/eng2/` holds the last batch's throwaway index: leave it too.

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
