Your lead again, resuming you in the same worktree (`/home/usain/gov-os-worktrees/W2-91`, branch `w2/W2-91`). This is your second batch. All the rules of your first brief still hold: the sandbox check first (step 0), DEC-732 (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-91/src` per command, the `gov.__file__` line quoted), Policy 2 (c) and (d) (never read `tests/acceptance/W2-91/`; never read the hidden half), the read refusals (DEC-849), the guard's command forms, scratch in your session scratchpad or the sandbox's own temp folder, the hooks check before committing, row W2-L423's rule (12-digit hashes), refused twice for the same call: stop and say so.

**Since your first batch:** the test designer's README map was fixed (`f57fa0cdf694`, merged as `a53650525fd8`); `/home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/TESTS-READY` exists. The lead has rebuilt the base and the head with the embedder and run W2-61's measure on the visible half; the facts are in files the lead wrote for you (below).

## 1. The acceptance tests, once

Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-91/src python3 -m gov.cli.main accept DAEO-a3u2` once, reading results only (never `pytest` on `tests/acceptance/`, never their source). Report pass or fail per KPI line and the counts. If a line fails, stop after step 1 and return the failing output (no change to the path map in this batch without the lead).

## 2. The evidence record (DEC-995, DEC-996 (A), the ticket's sixth success line)

Write `docs/changes/W2-91-evidence.md` (the ticket's record path since the claim; the old `docs/research/W2-91-memory-measure.md` is not written). Its form is W2-61's, as W2-86 kept it: read `docs/research/W2-86-memory-measure.md` and `docs/research/W2-61-baseline.md` and follow W2-86's sections (header with ticket, date, sources and the scores-only sentence; 1 what was measured and where; 2 the stores' fingerprint; 3 the runs; 4 the totals with both figures together; 5 per question beside the last measures; 6 the vectors per namespace; 7 deviations; 8 how to repeat it). Its facts come only from the lead's files:

- `/home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/facts.md` (the runs: clones, commits, retriever, records, totals, per question for control and head, and the `--compare` result);
- `/home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/facts-runs.md` (the rebuilds' start and end times, exit codes, digests, the sha256 of each store file, the gates);
- `/home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/vectors.json` (per namespace, judged by the head's path map: tracked files, chunks and chunks with vectors in the base clone's store and in the head clone's; the paths that gained or lost vectors).

What the record must say (the KPI lines):
- **Both figures always together** (DEC-833 item 3): hit@5 against CAP-10's floor of 85 and the owner's target of 95 % (DEC-957), full evidence against 99 %, and the in-the-bundle count; per question; beside W2-86's figures (its control and head, pinned gov, and its supplementary tree-code head) and W2-61's baseline, taken from their records `docs/research/W2-86-memory-measure.md` and `docs/research/W2-61-baseline.md`. A figure never alone.
- **The hidden half was neither read nor run;** the record holds scores only (ids, counts, ranks, digests), never a question's text, a gold answer or a retrieved item's text.
- **The vectors (KPI 1, 2 and 5):** for each namespace, the count of chunks with vectors at the base and at the head, from the clones' stores; that the root files, every tracked file under `governance/**` and under `schemas/**` have vectors at the head; that `fixtures/**`, `.claude/**`, `.rulesync/**`, `template/.rulesync/**`, the `kernel-vendored` parts and `cli/**` have none; and the vector diff: which paths gained vectors, that none outside the newly embedded sets gained or lost any except the ticket's own new files (name them).
- **The restricted overlay (KPI 3):** what you found in the code in your first batch (the indexer reads `embedding_policy` only, `src/gov/retrieval/semantic.py`; nothing reads `sensitivity` or `export_policy` beyond the schema's field list), so embedding the overlay changes no export or sharing rule; and that no export path exists today, so the line's "planted export case" cannot show an export refusal (the lead has returned this to the orchestrator as a package; say so, without deciding it).
- **The held-out list file:** the overlay now embeds every tracked file under `governance/**`, which includes the held-out list file (file names only, no held-out contents; its text was already in the lexical index). Say so in one sentence, without typing its path.
- **What the figures mean:** the like-for-like pair is head against control (same pinned retriever, same code); say what moved and what did not, per question, as W2-86's §5 and §7 do. Draw no conclusion the facts do not hold.

Commit only that file, with the trailers in the final block:

    git commit -m "W2-91: the evidence record: W2-61's measure at the base and the head, and the vectors per namespace" --trailer "Task: DAEO-a3u2" --trailer "Role: engineer" --trailer "Implements: DEC-957,DEC-833,DEC-860,DEC-996" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

Your last message: **the twelve fields first, each as a labelled line** (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), then the sandbox check, the `gov accept` result per KPI line, your commit's 12-digit hash, the lines added, the `gov.__file__` line, the `gov retrieve` calls you made (the store is built now), and the guard refusals you met. Refused twice for the same call: stop and say so.
