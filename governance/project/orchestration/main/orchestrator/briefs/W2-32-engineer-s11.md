# W2-32's engineer, re-pin window 4: S11, the candidate pool v456, into the product (DEC-1074 (5))

You are W2-32's engineer (`DAEO-0pyc`), launched by `gov launch` under that ticket's id, so the guard keeps you from
the ticket's acceptance tests. The CTO acts as the ticket's lead (no lead runs, DEC-1051).

**Read first, whole:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md`
(its "Engineer" paragraph is your job's form), `EMG-common.md` beside it,
`governance/project/orchestration/INTENT-DEC-1052.md`, and the ticket `.tickets/DAEO-0pyc.md`: its KPI line S11, the
new failure line, `allowed_paths`, and the note "DEC-1074 (5) placed here" at its end.

**Your worktree:** `/home/usain/gov-os-worktrees/W2-32` (branch `w2/W2-32`, brought to today's `w2/integrate` by the
CTO). Write only the ticket's `allowed_paths`.

**What you build:** S11 as the ticket states it: five settings under a `pool:` block in
`governance/project/retrieval.yaml`, read and validated by the loader (`CONFIG_INVALID` naming `pool.<key>`), each
absent or 0 meaning today's behaviour exactly:
- `pool.meaning_uncut`: `retrieve._phrased`'s meaning route fused over the phrasings and not cut back to its depth;
- `pool.route_depth`: the keyword and meaning routes' depth (`lexical.TOP_K`, `semantic.TOP_K`, 30 today), set per
  search, never as a process-wide change;
- `pool.rerank_depth`: the first n fused candidates reranked once, in one pass, every request under the padded bound
  (at most 16 texts, count × longest at most 24,000 characters), and the pages cut from that one order, in place of
  each page's 20 reranked apart;
- `pool.per_file_first10`: at most n chunks of one file in the first 10 of the final order, the rest kept after them,
  none lost;
- `pool.drop_nested`: an item whose lines lie inside an earlier item's of the same file dropped from the bundle.

**The measured reference** is the research harness's v456
(`/home/usain/gov-os-worktrees/research-retrieval/docs/research/EXP-003/retrieval-survey/night/harness/rx.py`: its
`sem_uncut`, `sem_k`/`lex_k`, `depth`, `perfile` and `dedup` switches). Read it and build the same behaviour into
`retrieve.py`'s own path, so that with 60, 40, 2 and both true the product gives the harness's v456 result question
for question. The CTO checks that by the measure on the D-4b clone; you check it with your own unit tests on stand-ins.
Do not switch the settings on in this repository's `retrieval.yaml`: the CTO does that after its measure.

**Your own unit tests** with stand-ins. **Your evidence file** `docs/changes/W2-32-evidence.md`: an S11 row (how
verified, the command, the result, the commit). **Stop when your unit tests pass**; the CTO merges the designer's tests
(`w2/W2-32-tests`) and you then run `gov accept W2-32` once, reading results only. Never read
`tests/acceptance/W2-32/`.

**Runs:** through the heavy slot, as `EMG-d4b-launched.md` says. **Commits:** `Task: DAEO-0pyc`,
`Implements: DEC-1071, DEC-1074`, `Role: engineer`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
**Return:** the sandbox and `ps` checks first, then the twelve labelled fields. Est.: 3 hours.
