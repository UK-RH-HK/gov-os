You are a fresh engineer. Ticket: DAEO-zqvn (W2-13, "RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-13` on branch `w2/W2-13`. You build the code to fulfil the ticket's specification and its KPIs, never to make the tests pass. This is one batch on one behaviour: the fused retrieval's warm latency (KPI success 3, second half). Your budget is about 75 minutes of work.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zqvn','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK (in this worktree).
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-zqvn`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-13` and `w2/W2-13`). If anything differs, stop and say so.

## Where the ticket stands

The branch's head is `12bca6c58610`. Over the base `c38a5b49bc86` the ticket built the ranked lexical route in `src/gov/retrieval/lexical.py` (FTS5 `bm25()` with weights for body, id and title; `search` answers `hits`, the exact lines, unchanged, and `ranked`, the exact chunks first and then up to `TOP_K` word chunks by BM25), the fusion of `ranked` in `src/gov/retrieval/fusion.py`, and the stated gap in `src/gov/retrieve/command.py`. Read the change with `git diff c38a5b49bc86 HEAD -- src tests/unit`. The CTO decided (DEC-1000, delegated; not yet in the register: this brief's text holds) that this interface stays: `hits` exact, `ranked` the route's ranking. **Do not change what `hits` or `ranked` hold, and do not touch `src/gov/retrieval/retrieve.py`** (W2-92 holds it; the line that makes the bundle fuse `ranked` comes later, not from you).

## The behaviour to fix

KPI success 3: "Retrieval latency stays within the retrieve budget on the dev tiers", the budget of W1-19's warm-query case: **p95 at most 0.5 s**. The lead timed `gov.retrieval.fusion.search(root, question, None, refresh=False)` warm (three warm-up questions, then each of the dev query set's 52 questions, one process, this machine's Ollama and reranker), on the two dev tiers cloned and rebuilt with the real embedder:

- base `c38a5b49bc86`: p95 0.547 s (three slowest 0.547, 0.652, 0.905);
- head: p95 0.727 s (three slowest 0.727, 0.753, 1.126);
- both under the same machine load (15 to 25), one after the other. The head's fused path costs about 1.33 times the base's.
- The lexical route alone, `lexical.search(..., refresh=False)`, on the same tiers: p95 0.010 s. `RERANK_TOP` (30) and semantic's `TOP_K` (30) are the same on base and head.

Find what in the ticket's change costs the extra time on the fused path, and remove that cost, so that the head's fused path costs no more than the base's (the lead then re-measures it with the real models; the target is the 0.5 s budget on a quiet machine). Candidates to check, not conclusions: the work the fusion does per fused chunk once lexical contributes up to 30 more (`rrf`, `_records`, the reranker's input: which chunks reach it, how long their text is), the lexical route's second query with many OR terms on a large tier, any per-call opening, freshness or `git` work, and anything the ranked route repeats per question. Measure before you change: time each stage of `fusion.search` (lexical, semantic, `rrf`, `_records`, rerank) on base code and head code side by side. Your sandbox runs a private Ollama on the CPU, so absolute model times prove nothing about the shared GPU; compare stages and ratios between base and head under the same conditions, and time the non-model stages directly. To run the base's code beside the head's, copy single named files from `git show c38a5b49bc86:<path>` into your scratch (never a copy of the tree).

Constraints: no change to the KPIs' behaviour (the ranked route's order and content, the exact list, the stated gap, "unavailable" never raising, the secrets filter); no lower quality to buy speed without saying so: if the only fix is a trade (fewer lexical chunks in `ranked`, fewer chunks reranked), do not make it: return it as a package with the figures (P-n: question, why now, options, impact, reversibility, cost, recommendation, confidence). `RERANK_TOP` and `RERANK_CHARS` are DEC-406's: changing them is a package, not a fix. Proportion (DEC-135): the smallest change that removes the cost.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists (or with a package and no commit, if the fix is a trade). **Commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m gov.cli.main retrieve "<question>" --json` in this worktree (its store was built with the base's code), or the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read or name the qualification oracle); (c) **this ticket's acceptance tests**: nothing under `tests/acceptance/W2-13/`, by any tool (no Read, cat, grep, git show or diff of it); you do not run them either in this batch (the lead runs `gov accept` after your commit); (d) the hidden half of any evaluation set (never `--part hidden`, never a file of a set's hidden folder). Other tickets' acceptance tests are open to you, to read and to run.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads that are open (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take the refusal; never look for another form; search named folders instead. Count every refusal you meet and list them in your return. Never read `.claude/settings.json`.
- **Writes: only inside the ticket's `allowed_paths`:** `src/gov/retrieve/**`, `src/gov/retrieval/lexical*`, `src/gov/retrieval/fusion*`, `src/gov/rebuild/lexical*`, `tests/unit/retrieve/**`, `tests/unit/retrieval/**`. Never write `tests/unit/retrieve*/test_w2_92*` (W2-92's) or `test_w2_86*` (W2-86's). Never touch `tests/acceptance/**`. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/` (your scratch: `/home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/eng/`). Install nothing: a tool you need is a P1 escalation in your return. Never write in `~/gov-os-workbench`; dev tiers are used by name only through `GOV_DEV_TIERS` (default `~/gov-os-workbench/synthetic`) and cloned into a temporary folder (outside the tracked tree, never under `.gov-runtime/`).
- **Files of other tickets, read only:** `src/gov/retrieval/retrieve.py`, `graph_route.py`, `code_route.py` (W2-92), `semantic.py`, `canary.py`, `src/gov/rebuild/command.py`, `watch.py`. If your fix needs one of them, do not edit it: return a package naming the file and why.
- **No copies of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in copies single named files, never `governance/project/`. No clone, copy or programme file under a `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **No `gov rebuild` of this worktree** (the lead rebuilds); never `gov rebuild --no-embeddings`, anywhere. A temporary clone of a dev tier may be indexed by the lexical refresh (`lexical.search(..., refresh=True)` or `lexical.refresh`) or rebuilt there if your sandbox allows it. Never `gov close`, `gov adopt`, `gov pause`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under your scratch and is run from there. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (your scratch and your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token. In unit tests, assemble any planted secret at run time from parts, never as one literal.
- **Scratch budget (DEC-898):** your share is 5 GB and 300,000 files and folders, outside the tracked tree. Keep the sandbox's own temp folder (do not set TMPDIR). Keep pytest's own retention (never a per-run `--basetemp`); add `-o tmp_path_retention_policy=failed`. Remove what you make as soon as it is no longer needed. Give your measure (`du -s --inodes`, `du -sh`) in your return.
- No subagents that write. Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- A test designer works in parallel in another worktree; you never read its work.

## Tests

- A builder test for what you change, in `tests/unit/retrieval/test_w2_13_*.py`, as regression evidence (no wall-clock assertion that a loaded machine could flip; assert the work done, such as the calls or chunks, where that is what you fixed).
- Run, each to its end, never `-x`: `cd /home/usain/gov-os-worktrees/W2-13 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m pytest tests/unit/retrieval tests/unit/retrieve tests/acceptance/W1-17 tests/acceptance/W1-21 tests/acceptance/W2-87 tests/acceptance/W2-107 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs` (skip `tests/acceptance/W1-19/test_w1_19_real_models.py`, a latency file the lead runs). Report each with its counts; a red you did not cause is reported, not fixed.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths (`git commit -- <paths>`), with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-zqvn" --trailer "Role: engineer" --trailer "Implements: DEC-725, DEC-802" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only decision ids the register holds (`DEC-n`) or Contract ids the store holds (`CAP-n`): never a row, a role or another word (DEC-927 item 2). After each commit check `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the files changed; the lines added and removed; the stage timings you measured, base against head, before and after your change, and what you found the cost to be; the tests you ran with their results; any package; the read refusals you met (DEC-849); whether you used `gov retrieve` and how often; your scratch measure.

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
