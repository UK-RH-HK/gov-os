You are a fresh engineer. Ticket: DAEO-zqvn (W2-13, "RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-13` on branch `w2/W2-13`. You build the code to fulfil the ticket's specification and its KPIs, never to make the tests pass. Your budget is about 90 minutes of work.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zqvn','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK (in this worktree).
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-zqvn`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-13` and `w2/W2-13`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet (the lead rebuilds it after your work, with your code), so ask the integration branch's store, which holds this ticket's base: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). The form `PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m gov.cli.main retrieve "<question>" --json` answers STORE_MISSING here until then. Never one giant query or context: take a large question in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read or name the qualification oracle); (c) **this ticket's acceptance tests**: nothing under `tests/acceptance/W2-13/`, by any tool (no Read, cat, grep, git show or diff of it). You may run them only through `gov accept` (below) and see only pass or fail per KPI line and the counts; (d) the hidden half of any evaluation set (never `--part hidden`, never a file of a set's hidden folder). Other tickets' acceptance tests are open to you, to read and to run.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads that are open (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take the refusal; never look for another form; search named folders instead. Count every refusal you meet and list them in your return. Never read `.claude/settings.json`.
- **Writes: only inside the ticket's `allowed_paths`:** `src/gov/retrieve/**`, `src/gov/retrieval/lexical*`, `src/gov/retrieval/fusion*`, `src/gov/rebuild/lexical*`, `tests/unit/retrieve/**`, `tests/unit/retrieval/**`. Never write `tests/unit/retrieve*/test_w2_92*` (W2-92's, running now) or `test_w2_86*` (W2-86's). Never touch `tests/acceptance/**`. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/` (your scratch: `/home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/eng/`). Install nothing: a tool you need is a package (a P1 escalation in your return). Never write in `~/gov-os-workbench`; dev-tier runs use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Files of other tickets, read only:** W2-92 holds `src/gov/retrieval/graph_route.py`, `code_route.py` and `src/gov/retrieval/retrieve.py`'s route list; `retrieve.py`, `semantic.py`, `canary.py`, `src/gov/rebuild/command.py` and `src/gov/rebuild/watch.py` are outside your paths. If your change needs any file outside your paths, do not edit it: return a package naming the file and why.
- **No copies of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one. No clone, copy or programme file under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **No `gov rebuild` here** (your sandbox cannot reach the code-graph daemon; the lead rebuilds). Never `gov rebuild --no-embeddings`, anywhere. Never `gov close`, `gov adopt`, `gov pause`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under your scratch and is run from there. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (your scratch and your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token. In unit tests, assemble any planted secret at run time from parts, never as one literal.
- **Scratch budget (DEC-898):** your share is 5 GB and 300,000 files and folders, outside the tracked tree. Keep the sandbox's own temp folder; where you set one, use `TMPDIR=/tmp/gov-os-lead-W2-13`. Keep pytest's own retention (never a per-run `--basetemp`); add `-o tmp_path_retention_policy=failed`. Remove what you make as soon as it is no longer needed. Give your measure (`du -s --inodes`, `du -sh`) in your return.
- No subagents that write. Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-zqvn.md` (read-only): its KPI lines and its `allowed_paths`; its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-13") and section 0.
- Its rows, in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`: W2-L233, W2-M071, W2-M072, W2-M098, W2-M100, W2-M102, W2-M292, W2-M296. **Re-check each row's state against the code as you take it in (DEC-718):** a row already fixed is reported with the commit that fixed it; a row your paths cannot reach is reported as such.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-725, DEC-900, DEC-260, DEC-342, DEC-343, DEC-344, DEC-396, DEC-414, DEC-406, DEC-374, DEC-379, DEC-957, DEC-135, DEC-718; AR-9 and CAP-11 in `docs/contract/`. Lens G's F8 and R8 (`docs/assessment/2026-10/G-tools-glue.md`): FTS5's own `bm25()` with column weights and `ORDER BY rank`; a trigram table for exact identifiers in place of Python substring filtering.
- The code the ticket touches: `src/gov/retrieval/lexical.py`, `fusion.py`, `src/gov/retrieve/command.py`; and, read only, what uses them: `src/gov/retrieval/retrieve.py`, `semantic.py` (it reads `lexical_chunk` and `lexical_fts.text` directly), `canary.py`, `retrieve_check.py`, `src/gov/rebuild/command.py` and `watch.py` (W2-107's content-hash secrets cache sits in front of the lexical index through `lexical.indexable`: keep it working), `src/gov/decisions/register.py`, `src/gov/store/loader.py`.
- `docs/research/W2-61-baseline.md`, and W2-86's record (`git show 362bb64f6:docs/research/W2-86-memory-measure.md`): ranking is the remaining cause of the memory measure's misses.

## What to build (the KPI lines)

Success 1, the ranked lexical route [DEC-725, W2-M102, W2-L233, W2-M292, W2-M072, W2-M100]: the lexical index is an SQLite FTS5 table over the same parents and spans as today, built by `gov rebuild` (through the lexical refresh it already calls). A plain-word question returns hits ranked by BM25, with field weights for id, title and body. The lead's reading of the fields: **id** is the identifier a document is known by (a record's id, such as a DEC-n or a ticket id in its frontmatter or heading); **title** is the heading of the document or of the section (parent) the chunk lies in; **body** is the text. An exact identifier still ranks first: the exact-match route is kept as a boost, not replaced (every line that holds the exact string is still found with its file and line, CAP-11, W1-17). The question is matched by its words, not as one phrase (W2-M292); case and stems handled, whole tokens matched (W2-M072, W2-M100), and the choice you make recorded in the module's docstring.

Success 2: the fusion receives a ranked lexical list beside the semantic one, so that lexical, semantic and the reranker each contribute.

Success 3 [W2-M071]: lexical search returns "unavailable" (`available: false`, state `FACET_UNAVAILABLE`, a reason; DEC-260's mapping) instead of raising: a missing, empty, stale or unreadable store, a store built by the code before your change, and any question (no token, FTS5 syntax, quotes, operators) never raise. Retrieval latency stays within the retrieve budget on the dev tiers (W1-19's warm-query p95 of 0.5 s).

Success 4 [AR-9, W2-M296, DEC-900]: a question about an id that exists nowhere (an id-shaped token such as `DEC-9999` that no file holds and no record has), asked as the question alone, stops with a named reason and no unrelated items: the stated gap (the id named among the gaps, a stopping reason that names a gap; today it returns 20 unrelated semantic items and `BUDGET_EXHAUSTED_WITH_GAPS`). A question naming an id that does exist is answered as before. `retrieve.py` is outside your paths; `src/gov/retrieve/command.py` (`gov retrieve`) is inside them. If the stated gap cannot be built inside your paths, return a package.

Failure 1: RETR-A-04's bundle is unchanged (citations, three parent expansions, stopping reason).
Failure 2: the secrets filter applies to the FTS5 table as to the old index: a planted canary is never indexed (nothing from a file the filter refuses enters any lexical table).

Constraints: keep the store's existing tables and the columns other modules read (`lexical_file`, `lexical_parent`, `lexical_chunk`, `lexical_fts` with its `text`), the index's incremental refresh by blob, its freshness and its digest semantics, and the public answers of `search`, `chunks`, `parent`, `digest`, `freshness` and `refresh`. Proportion (DEC-135): no code for edge cases beyond the KPI lines and the rows. Never make a guard or gate decision fail open. About 300 lines of code is the estimate.

## Tests

- Builder tests in `tests/unit/retrieval/test_w2_13_*.py` (or `tests/unit/retrieve/test_w2_13_*.py`), your own test-driven development, as regression evidence only.
- Run your unit tests and the earlier tickets' suites your change can reach, each to its end, never with `-x`: `cd /home/usain/gov-os-worktrees/W2-13 && TMPDIR=/tmp/gov-os-lead-W2-13 PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`, with `<paths>` among `tests/unit/retrieval tests/unit/retrieve tests/acceptance/W1-17 tests/acceptance/W1-20 tests/acceptance/W1-21 tests/acceptance/W1-22 tests/acceptance/W2-107 tests/acceptance/W2-108 tests/acceptance/W2-87 tests/acceptance/W2-55` (skip `tests/acceptance/W1-19/test_w1_19_real_models.py`, a latency file run alone by the lead). Report each with its counts; a red you did not cause is reported, not fixed.
- **The acceptance tests arrive while you work (DEC-963):** the test designer works in parallel in its own worktree; the lead merges its tests into this worktree only while your command is not running. When `/home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/TESTS-READY` exists and your work is committed, run them once, through `gov accept` only: `cd /home/usain/gov-os-worktrees/W2-13 && TMPDIR=/tmp/gov-os-lead-W2-13 PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m gov.cli.main accept DAEO-zqvn --json`, and report its per-line results and counts. Never run `pytest` on `tests/acceptance/W2-13/` yourself. If the file does not exist when you have committed, return; the lead resumes you for that run.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths (`git commit -- <paths>`), with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-zqvn" --trailer "Role: engineer" --trailer "Implements: DEC-725, DEC-900" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only decision ids the register holds (`DEC-n`) or Contract ids the store holds (`CAP-n`): never a row, a role or another word (DEC-927 item 2). After each commit check `git log --oneline -2` and `git status --short`.

## Return

Your commits' hashes (12 digits); the files changed; the lines added and removed; the tests you ran with their results; `gov accept`'s per-line result if you ran it; each list row with its state as you found it and as you left it; your reading of any KPI term; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence); the read refusals you met (DEC-849); whether you used `gov retrieve` and how often; your scratch measure.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Refused twice for the same call: stop and say so; no third try.
