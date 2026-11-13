
## Rules
- One test (or more) per KPI line S1-S8 and F1-F5, each doing what its Verify says, read with the Interface item the
  line names. Name each after its id (`test_s1_...`, `test_f3_...`). Cover each exit code and printed code of
  Interface item 2 that a KPI line reaches (`STOPPED control|notready|fault|store|brake`, exit 3 `USED`, `MS-KEPT`,
  `MS-CLASSES`, `MS-POOLDIFF`, `MS-IMPORTCOUNT`, `MS-IMPORTED`, `MS-NOCOUNT`), and the printed forms of item 8 exactly.
- Reach the code as its callers do: `python3 -m gov.memaudit measure|judge|classes|pool|pool-import --sets-root <root>
  --audit memory-audit-<date> ...` in a child process, judged by exit code, printed lines, and the files and ledger
  events under `<root>/runs/<A>/` (Interface items 1-3). Every child gets this tree's `src/` first on `PYTHONPATH`
  (fail the run if it would import `gov` from elsewhere, as W2-170's suite does). In-process imports only where the
  Interface names a Python seam: `gov.memaudit.prompts` (item 7's hash list: recompute each hash as the item says and
  compare) and `gov.memaudit.claude.run_claude`. Never import `gov.memaudit`'s new modules at collection, so the suite
  runs red by failing, not by erroring at import.
- The seams (item 6): `--gov <exe>` a fake `gov` (a small Python script; its real path inside a planted
  `pin-<12 hex>` folder equal to `DECLARATION.json`'s `gov_pin`, as W2-170's world plants it) that answers
  `retrieve ... --json` with planted ranked outputs (the shape `gov.retrieval.measure` reads and `f80lib.degraded`
  checks: `result.evidence`, `result.facets.lexical/semantic.available`, `result.rerank.by`, `result.pool.fallback`),
  so ranks, degraded answers and faults are planted per call or per attempt; `--claude <exe>` a fake reader and grader
  answering the fresh 80's argv with one JSON (`structured_output`, `usage`, `total_cost_usd`) from planted verdicts
  and costs. The store is a planted file whose sha256 a planted fake changes mid-attempt for S4's store case.
- S1: planted controls at 34, 33 and 31 against no earlier audit (last = 34); also one with an earlier
  `memory-audit-<date>` `FIGURES.json` holding a `control.hit5` to show `last` is read from it. 31: exit 2,
  `STOPPED control`, `USED` byte-equal to what `declare` wrote, no `attempt-*` folder, no `search` event of phase
  `attempt`.
- S2: 12 planted questions with planted first-gold ranks; the printed `RETRIEVAL` line and `COUNTS` equal the planted
  figures; `measure --kept <n>` prints the same line, writes nothing, exits 0.
- S3: n=40, planted grader verdicts giving known r and w; the VERDICT and BAR lines (bar 34 and 2, target 38), the
  interval to one decimal as Clopper-Pearson; `FIGURES.json`'s `verdict.interval_exact` to 4 places.
- S4: one degraded search in attempt-1 then a clean attempt-2 (exit 0, `COUNTS` = attempt-2, attempt-1's `FAULT`
  `degraded`); two faults (exit 2, `STOPPED fault`); store changed (exit 2, `STOPPED store`, no attempt-2, no rebuild
  call); not ready at the probe (exit 2, `STOPPED notready`, nothing spent).
- S5/F2: 5 planted misses: `misses.jsonl` has 5 lines with exactly item 9's keys in order and `evidence_in_bundle`
  JSON true/false; parse it with the auditor brief's own field list (section 2 of auditor.md); a second `measure` and a
  second `judge` exit 3 and `misses.jsonl` is byte-identical before and after; no miss: an empty file.
- S6/F1: `FIGURES.json` has exactly item 10's keys; plant a unique word in a question, a gold answer, an answer and a
  source path, then grep standard output, standard error, every file under `runs/<A>/` except `misses.jsonl`,
  `reader/` and the kept outputs (item 9 names them the only places a question or answer is written; the kept
  outputs are the retriever's own output), and `FIGURES.json`: 0 hits each. Then `classes` with a planted
  `miss-classes.json` adds the five counts; ids not equal to `misses.jsonl`'s: `MS-CLASSES`.
- S7: planted pools of 300 and 900 (item 4's layout): the whole 300; a draw of 400 from 900, the same seed twice the
  same draw, the seed in `POOL.json` before any `pool` search event; a planted fall of 4 points named
  `POOL REGRESSION`, exit 0; the audit's questions copied into the pool after; `pool-import` with planted 79 and 138
  (and a wrong count: `MS-IMPORTCOUNT`, nothing written; a second run: `MS-IMPORTED`).
- S8: planted costs that pass the brake: exit 2 `STOPPED brake`, no `misses.jsonl`, no `FIGURES.json`; `judge
  --resume --projection <higher>` asks only the unfinished questions (count the fake reader's calls by qid).
- F3: from the ledger, no `search` event's `at` earlier than the mtimes of `DECLARATION.json` and `USED`.
- F4: stub Ollama and reranker servers (small HTTP / unix-socket servers in the test, on stand-in ports, logging every
  request), reached only by the fake `gov` at `OLLAMA_HOST`, `GOV_QUERY_OLLAMA_HOST` and the planted HOME's
  `.cache/gov-os/rerank.sock`; their logs hold only query calls; the stub processes are never signalled.
- F5: `git diff --name-only <merge-base with w2/integrate>...HEAD` lists only the ticket's allowed_paths plus
  `tests/acceptance/W2-171/` (the test's own files). It is green only when the branch is clean; say so in its docstring.
- Tests are red now (no `measure`/`judge`/... subcommands yet). Run them and say which are red and why; anything green
  now is a fault in the test unless it guards "nothing else happens".
- Keep the suite fast (seconds per case, the whole folder in a few minutes): the fake commands only. No test named with
  `real`, `green_here` or `time_limit` unless it must be skipped by that filter. Bounded polls, never a bare sleep.
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-171-tests/.gov-runtime/scratch/empty-home
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-171-tests/src python3 -m pytest
  tests/acceptance/W2-171 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"
  -k "not real and not green_here and not time_limit"`.
- Add `tests/acceptance/W2-171/README.md` as W2-170's: how the tests reach the code, what is planted, each KPI's cases.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-171-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-k1e2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1074, DEC-833, DEC-860, DEC-1118, DEC-1050, DEC-1073" -- tests/acceptance/W2-171`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## Added after launch (the CTO's order, 2026-11-12): every pytest goes through the heavy-slot gate
`TMPDIR=/home/usain/gov-os-runs/tmp/W2-171 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<tree>/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<tree>/src python3 -m pytest <one folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`, one folder per run.
