You are a fresh engineer. Ticket: DAEO-zqvn (W2-13, "RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-13` on branch `w2/W2-13`. You build the code to fulfil the ticket's specification and its KPIs, never to make the tests pass. This is one batch on one behaviour of KPI success 1. Your budget is about 45 minutes of work.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zqvn','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK (in this worktree).
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-zqvn`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-13` and `w2/W2-13`). If anything differs, stop and say so.

## Where the ticket stands

The head is `962fc434c1f5`. Over the base `c38a5b49bc86` the ticket built the ranked lexical route in `src/gov/retrieval/lexical.py`: `search` answers `hits` (the exact route: every line that holds the exact question string, with file and line, by path and line, W1-17, CAP-11; **unchanged**) and `ranked` (the chunks for the fusion, best first: the exact route's chunks first, marked `exact: true`, then up to `TOP_K` word chunks by BM25 with weights for body, id and title, `exact: false`). The CTO decided this interface stays (DEC-1000, delegated; not yet in the register: this brief's text holds). Read the change with `git diff c38a5b49bc86 HEAD -- src tests/unit`.

## The behaviour to build (KPI success 1: "An exact identifier still ranks first: the exact-match route is kept as a boost, not replaced")

Today the boost applies only when the whole question occurs verbatim in a line. A question that **holds** an identifier among other words is not boosted. The acceptance run's failure message (the only thing you get from it):

    ids/z-holder.md holds QX-4471 verbatim and is not first in the ranked list for 'QX-4471 gauge reading': ['ids/a-noise.md', 'ids/b-noise.md', 'ids/z-holder.md', 'manual/manual.md', …]

In that planted corpus, `ids/z-holder.md` holds the identifier `QX-4471` verbatim; `ids/a-noise.md` and `ids/b-noise.md` mention its parts (or the other words) more often but do not hold `QX-4471` itself. Asked `QX-4471` alone, the holder already comes first, marked `exact`.

Expected:
- When the question holds an identifier (an id-shaped token: the same shape the ticket already recognises for RETR-X-02's stated gap, e.g. `DEC-9999`, `QX-4471`), the chunks that hold that identifier verbatim, as a whole token, come first in `ranked` and are marked `exact: true`, ahead of every BM25 word chunk; then the word chunks follow as today. Among the boosted chunks, BM25 orders them as it orders the exact chunks today. A chunk holding the whole question verbatim stays boosted as today.
- Every `exact: true` chunk ranks above every `exact: false` one; each chunk appears once.
- `hits` does not change: it stays the lines that hold the whole question string verbatim (for `QX-4471 gauge reading`, the lines that hold that whole string; none in that corpus). Do not add the identifier's lines to `hits`.
- Nothing else changes: a plain-word question (no identifier) ranks as today; the stated gap for an id that exists nowhere (`gov retrieve`, `src/gov/retrieve/command.py`) behaves as today; search never raises; whole tokens; at most the FTS5 queries per question the ticket's builder test `tests/unit/retrieval/test_w2_13_rerank_work.py` allows, or, if the boost needs one more query, say so and update that builder test's bound with the reason (it is your ticket's own builder test). Keep the cost small: the fused path's warm p95 budget is 0.5 s.
- Record the rule in the module docstring (the ranked list's description).

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m gov.cli.main retrieve "<question>" --json` in this worktree (its store was built with the base's code), or the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read or name the qualification oracle); (c) **this ticket's acceptance tests**: nothing under `tests/acceptance/W2-13/`, by any tool (no Read, cat, grep, git show, log -p or diff of it); you do not run them in this batch (the lead runs `gov accept` after your commit); (d) the hidden half of any evaluation set (never `--part hidden`, never a file of a set's hidden folder). Other tickets' acceptance tests are open to you, to read and to run.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads that are open (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take the refusal; never look for another form; search named folders instead. Count every refusal you meet and list them in your return. Never read `.claude/settings.json`.
- **Writes: only inside the ticket's `allowed_paths`:** `src/gov/retrieve/**`, `src/gov/retrieval/lexical*`, `src/gov/retrieval/fusion*`, `src/gov/rebuild/lexical*`, `tests/unit/retrieve/**`, `tests/unit/retrieval/**`. Never write `tests/unit/retrieve*/test_w2_92*` (W2-92's) or `test_w2_86*` (W2-86's). Never touch `tests/acceptance/**`. Scratch files go in your session's own scratchpad or temp folder (the last engineer was refused writes under `.gov-runtime/scratch/eng/`); never write `.gov-runtime/**` otherwise. Install nothing: a tool you need is a P1 escalation in your return. Never write in `~/gov-os-workbench`.
- **Files of other tickets, read only:** `src/gov/retrieval/retrieve.py`, `graph_route.py`, `code_route.py` (W2-92), `semantic.py`, `canary.py`, `src/gov/rebuild/command.py`, `watch.py`. If your change needs one of them, do not edit it: return a package naming the file and why.
- **No copies of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. No clone, copy or programme file under a `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **No `gov rebuild` of this worktree** (the lead rebuilds); never `gov rebuild --no-embeddings`, anywhere. Never `gov close`, `gov adopt`, `gov pause`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file in your scratchpad and is run from there. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token. In unit tests, assemble any planted secret at run time from parts.
- **Scratch budget (DEC-898):** your share is 3 GB and 150,000 files and folders, outside the tracked tree. Keep the sandbox's own temp folder (do not set TMPDIR). Keep pytest's own retention (never a per-run `--basetemp`); add `-o tmp_path_retention_policy=failed`. Give your measure (`du -s --inodes`, `du -sh`) in your return.
- No subagents that write. Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## Tests

- A builder test for the boost in `tests/unit/retrieval/test_w2_13_*.py` (your own planted corpus: an identifier holder against noise files that mention its parts more often; a question holding the id and other words; `hits` unchanged; every exact chunk above every non-exact one).
- Run, each to its end, never `-x`, each as its own command (the foreground limit is 10 minutes): `cd /home/usain/gov-os-worktrees/W2-13 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs` for `tests/unit/retrieval`, `tests/unit/retrieve`, `tests/acceptance/W1-17`, `tests/acceptance/W2-87`. Not W1-21, W2-107 or W1-19's real-model file (the lead's scoped run covers them). Report each with its counts; a red you did not cause is reported, not fixed.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths (`git commit -- <paths>`), with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-zqvn" --trailer "Role: engineer" --trailer "Implements: DEC-725" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only decision ids the register holds (`DEC-n`) or Contract ids the store holds (`CAP-n`): never a row, a role or another word (DEC-927 item 2). After each commit check `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the files changed; the lines added and removed; the rule you built; the FTS5 queries per question before and after; the tests you ran with their results; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence); the read refusals you met (DEC-849); whether you used `gov retrieve` and how often; your scratch measure.

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
