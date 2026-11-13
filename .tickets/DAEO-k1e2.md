---
id: DAEO-k1e2
status: closed
deps: [DAEO-61vm]
links: [DAEO-52ku, DAEO-2bdu, DAEO-p8tv, DAEO-qz4p]
created: 2026-11-11T01:20:40Z
type: task
priority: 2
assignee: engineer
external-ref: W2-171
tags: [wave-2, implementation, memory, audit, full, after-the-lift]
wbs_id: W2-171
title: 'The memory audit''s measure: the control, the retrieval figures, the judged reader run, the fault rule, the misses file, the regression pool (DEC-1101 (1), DEC-1125 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-61vm
allowed_paths:
- src/gov/memaudit/**
- tests/unit/memaudit/**
- docs/changes/W2-171-evidence.md
- docs/probes/DAEO-k1e2/**  # the probe record, so the branch's path case holds at its head (as W2-157's; the CTO, 2026-11-12 12:50)
kpis:
  success:
  - 'S1 The control runs first: the standing visible-40 set is measured with the audit''s declared configuration, and its hit@5 must be within 2 of the last audit''s control (the first audit''s control is within 2 of 34, E0''s figure, DEC-1097 (1)(b)). Outside that, nothing is measured, the counts say `control out of range`, and `USED` is left as written by W2-170. Verify: planted fake `gov` returning a control at 34, 33 and 31: the first two proceed, the third stops before the audit set''s first search [DEC-1097 (1), DEC-1101 (1)]'
  - 'S2 One attempt measures the kept questions with `gov.retrieval.measure`''s matcher and source families: hit@5, full evidence and the first gold rank per question (hit@10, hit@20 and MRR beside them), each search''s ranked output kept so a label is never re-scored by searching again. Verify: a planted set of 12 questions against a fake `gov` with planted ranks: the figures equal the planted ones; the kept outputs re-score to the same figures with `--kept` [DEC-833, DEC-860, DEC-1101 (1)]'
  - 'S3 The judged reader run: the reader answers each question from its searches with search again once (A2), a named grader judges right end to end with a second grader''s agreement beside it. The reader''s and graders'' prompts are the fresh 80''s, pinned by hash (`READER_SYS`, the schemas, the cut), so audits compare with FRESH-80-RESULT. The verdict line reads: right end to end r of n, wrong claims w of n, the exact 95 % interval, against the scaled bar (at least ceil(0.85 n) right and at most floor(0.05 n) wrong; target ceil(0.95 n)); hit@5, gold in the first bundle, the answer correct with the citation aside and one search against two (exact McNemar) are printed beside it and never judged. Verify: a fake reader and graders with planted verdicts on n=40: the line shows planted r and w and the planted interval; bar 34 and 2 [DEC-1097 (1)(d), DEC-1098 (1), DEC-1101 (1)]'
  - 'S4 The fault rule, as FRESH-80-1 section 3.5 states it: a search not answered as declared (a bundle not reranked by the shared service, a route missing, the pool''s rerank fallen back), or a store whose sha256 changed during the attempt, makes the attempt not whole. One restart is allowed while no attempt has counted; a second fault stops the audit and goes to the owner in the counts. No restart into the same outage: the live reranker is checked ready before each attempt. Verify: planted degraded search (one restart then pass; two faults then stop); planted store change (stop, no restart) [DEC-1097 (1)(g), DEC-1101 (1)]'
  - 'S5 A miss is a result: a verdict below either limit stands as recorded, is never run again and never re-scored to pass. The runner writes `runs/<audit>/misses.jsonl`, one line per miss (a question not right end to end at A2): `{"id","question","gold_answer","gold_sources","answer","outcome","evidence_in_bundle"}` with `outcome` one of `wrong`, `incomplete`, `not_found` and `evidence_in_bundle` the measure''s own yes or no on whether a gold place was in the first bundle; an audit with no miss writes an empty file. Verify: planted run with 5 misses: the file holds 5 lines in that form; a second run on the same audit is refused by W2-170''s `USED`; the file is the auditor brief''s input form (parsed by the brief''s own field list) [DEC-1074 (1), DEC-1101 (1), DEC-1125 (2)]'
  - 'S6 `runs/<audit>/FIGURES.json` carries counts only: the verdict numbers, the beside figures, and for the misses, counts by rank bucket (gold at rank 6 to 20; not in the first 20), by namespace of the gold source (embedded; keyword only), by category and by route; with the auditor''s class counts added after its run. Verify: schema check over a planted run; grep for a planted question word, a planted gold path and a planted answer finds none [DEC-1101 (2), DEC-1097 (2)]'
  - 'S7 The regression pool: after a measured audit its kept questions join `pool/` under the sets root (hidden, like a set). Each audit re-runs the pool through the retrieval measure only (hit@5 and full evidence, no model tokens): the whole pool while it holds 400 questions or fewer, else a seeded draw of 400 (the seed recorded first). The pool''s figures are printed beside the last audit''s, and a fall of 3 points or more in either is named a regression in the counts. The 79 of the fresh 80 and the 138 of earlier sets are added by one planted-tested import path, run once by the CTO. Verify: planted pools of 300 and 900 questions: whole, then a draw of 400 with the same seed twice giving the same draw; a planted fall of 4 points is named [DEC-1101 (1), DEC-1125 (2)]'
  - 'S8 The spend is bounded and recorded: each model call''s `total_cost_usd` goes to the run''s ledger; the run stops at twice its projection (the fresh 80''s 0.157 USD a question, so 12.6 USD for 40), and a brake stop goes to the owner first; a stopped run resumes without re-asking finished questions. Verify: planted ledger over the brake: stops; resume asks only the unfinished [DEC-1097 (1), DEC-1118 (3)]'
  failure:
  - 'A question, gold answer, answer or source path in standard output, a log or an error text; only ids, counts and digests leave. Verify: a planted run on the fake reader and graders with a unique word in a question, a gold answer, an answer and a source path: grep of standard output, standard error, every log and `FIGURES.json` finds each 0 times'
  - 'A set measured twice, or re-scored to pass; a label changed after its figures exist. Verify: a planted miss (S5): a second run on the same audit is refused by W2-170''s `USED` and `misses.jsonl` is byte-identical before and after the refusal; a planted verdict below the bar stays as recorded'
  - 'A search made before `DECLARATION.json` and `USED` exist (W2-170); the store rebuilt during an attempt. Verify: the planted run''s call ledger: no search entry earlier than the file times of `DECLARATION.json` and `USED`; S4''s planted store change stops the attempt with no rebuild call in the ledger'
  - 'The shared Ollama servers or the reranker service touched other than by their ordinary query calls. Verify: a planted run with stub servers on stand-in ports: their request logs hold only query calls, and no stop, restart, model load or unload call; no process of either server is signalled'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: FULL
sources:
- DEC-1101
- DEC-1125
- DEC-1098
- DEC-1097
- DEC-1074
- DEC-833
- DEC-860
- DEC-1118
- DEC-1050
- DEC-1073
- DEC-1052
- DEC-1129
est_loc: 600
acceptance_tests:
  path: tests/acceptance/W2-171/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines, before the engineer, on a planted set, a fake `gov` and a fake model; never a real search, GPU call or the real sets root'
track: B
list_rows: []
reads:  # declared by the CTO 11-11 (gov brief READS_MISSING; DEC-1121): what it reads that it does not write
- governance/project/orchestration/packages/MEMORY-AUDIT-1.md
- src/gov/retrieval/retrieve.py
needs: []
waits_on: []
---
# W2-171 The memory audit's measure

The measured part of one audit (DEC-1125 (2)): the control, the retrieval figures, the judged end-to-end run, and
what feeds the auditor. It generalises the fresh 80's tools (`.gov-runtime/scratch/orchestrator/drafts/fresh80/`:
`f80lib.py`, `run_measure.sh`, `fresh80_reader.py`, `fresh80_figures.py`), which were built for one set. The CTO copies
them to `.gov-runtime/scratch/ref/fresh80/` in the worktree when the ticket starts. W2-170 comes first.

- **Why a tool and not the fresh 80's scripts:** those pin one set name and one run folder; a weekly audit needs the
  same steps for a new set each time, tested on a planted set.
- **Alternatives (one line each):** end to end for the pool as well as the fresh set (rejected: about 0.16 USD a
  question, so the pool's cost grows each week); no pool (rejected: DEC-1101 (1) asks for the regression check).
- **Not here:** the set's checks and the declaration (W2-170); the cycle (W2-172); the miss classes by the auditor
  session (its brief; the launch script).

[DEC-1101 (1); DEC-1125 (2)]

## Interface

Stated by the CTO before the pair starts (DEC-1052; PKG-W2-171-IFACE-1, option (a)). The test designer writes tests to this block and the engineer conforms to it; neither changes it. A gap or a clash goes back to the CTO as a package. Bracketed lines name the KPI line each item serves (S1 to S8; F1 to F5 are the `failure:` lines in order) and its source. W2-170's Interface (DAEO-61vm, sections 1 to 10) holds and is imported, never copied: `layout.paths`, `ledger.append`, `say.say`, `declare.declare`; this block adds to it and changes none of it. The three approved briefs are not changed by anything here (DEC-1129 (2)).

### 1 The command line [S1-S8, F1; W2-170 section 1, PKG-W2-171-IFACE-1 gap 1]
Five subcommands join `python3 -m gov.memaudit` (`--help` prints usage, exit 0); W2-172's `run` calls them and calls no `declare` of its own.
- `measure`: `declare` (W2-170: `DECLARATION.json`, then `USED`), the ready check, the control, the attempts and the fault rule, the retrieval figures (S1, S2, S4). `measure --kept <n>` runs none of that: it re-scores `attempt-<n>`'s kept outputs through `gov.retrieval.measure --kept` (that measure's own flag, on the derived folder), prints the `RETRIEVAL` line of item 8, writes nothing, exits 0 or 1 `MS-KEPT`, never 3 (S2).
- `judge`: the reader run, the two graders, the verdict, `misses.jsonl`, `FIGURES.json` (S3, S5, S6, S8); `--resume` after a brake stop.
- `classes`: reads `runs/<A>/miss-classes.json` (the launch script's delivered copy of the auditor's `classes.json`, `{"<id>": {"class", "reason"}}`) and adds the five class counts to `FIGURES.json` (S6); `MS-CLASSES` (exit 1) when its ids are not exactly `misses.jsonl`'s.
- `pool`: the pool's re-run and the audit's questions joining the pool (S7). `pool-import`: S7's one-time import, run once by the CTO.
Flags as W2-170 section 1 (`--sets-root`, `--audit` required; every flag with a value takes a bare name, a number, a hash or a path outside the sets root; never a folder under it): `--repo`, `--commit`, `--store`, `--gov`, `--decision` as `declare`'s (`measure`); `--repo`, `--gov` (`judge`, `pool`); `--claude <exe>` (`judge`, default `~/.local/bin/claude`); `--projection <usd>` (`judge`, item 11); `--kept <n>` (`measure`, a number); `--seed <n>` (`pool`, item 4). `--resume` (`judge`) is the one flag without a value. `pool-import` takes `--sets-root` only; its source folders are derived (item 4). Printing is `say`'s alone; every child process's standard error goes to a file in the run folder, never printed (F1).

### 2 Exit codes [S1, S4, S8, F2; W2-170 section 5, gap 2]
Same five as W2-170: 0 ok, 1 refused (a code printed, nothing written beyond what the item says), 2 stopped, 3 used, 4 usage (also an unexpected error: the one line `ERROR: <class>`). W2-170's `DC-`/`PF-` codes pass through `measure` unchanged. Exit 2 replaces W2-170's "void": it means the audit began and cannot go on; it writes `runs/<A>/STOPPED` holding one cause word, prints `STOPPED <cause>`, and **goes to the owner** (W2-172 stops on any non-zero; only exit 2 carries the owner's decision).

| exit | when |
|---|---|
| 0 | `measure`: an attempt counts (`COUNTS` written). `judge`: `FIGURES.json` written, a MISS included (a miss is a result, S5). `pool`: ran, **a regression included** (printed, in `POOL.json`). `classes`, `pool-import`: done |
| 1 | `MS-NOCOUNT` (`judge`, no `COUNTS`); `MS-NOFIGURES` (`pool`, `classes`); `MS-DIGEST` (the set's digest now is not `DECLARATION.json`'s); `MS-PIN` (`judge`, `pool`: `--gov`'s pin is not `gov_pin`); `MS-FIRSTS` (a question without a measured first call); `MS-POOLFAULT`; `MS-POOLDIFF`; `MS-IMPORTED`; `MS-IMPORTCOUNT`; `MS-KEPT`; `MS-CLASSES` |
| 2 | `STOPPED` cause, a closed list: `control` (out of range, S1), `notready` (the probe search not answered as declared, before an attempt or the restart), `fault` (a second fault, S4), `store` (sha256 changed, S4), `brake` (twice the projection, S8) |
| 3 | `USED` exists (`measure`); `judge` when `FIGURES.json` exists, or `reader/` or `STOPPED` exists and `--resume` is not given, or `--resume` and its conditions (item 11) do not hold; `pool` when `POOL.json` exists. Nothing is written; printed `USED` |
| 4 | usage, as W2-170 |

### 3 The layout under `runs/<A>/` and the ledger [S1-S8, F3; W2-170 section 2, gap 3]
W2-170's files stay (`PREFLIGHT.json DROPS.json DECLARATION.json USED ledger.jsonl`). W2-171 adds, from the fresh 80's own (`run_measure.sh`, `fresh80_reader.py`), all written whole by temporary name then rename:
```
gov                 the wrapper (a Python file, mode 700) that keeps each retrieve call and appends its search event
ready               not a file: the probe's result is a ledger event
control-<k>/        kept/00001.json.., measure.txt, measure.err, ms          k = 1, 2: one before each attempt
attempt-<n>/        kept/00001.json.., measure.txt, measure.err, ms, ENDED, FAULT (one cause word), DONE      n = 1, 2
COUNTS              the counting attempt's name (attempt-1 or attempt-2), written when it is DONE
STOPPED             the cause word (item 2); absent while the audit goes on
reader/             plan.json, <qid>.json (the fresh 80's row, keys as fresh80_reader.py's one(), kind "audit"), .lock
misses.jsonl  FIGURES.json  POOL.json  pool/ (kept/, measure.txt: the pool's run)
```
`ledger.jsonl` events (W2-170's `seq`, `at`, `event`, then these fields; `at` is ISO UTC to the microsecond, comparable to file mtimes; numbers, ids and codes only; appends are serialised by one lock in the process, so four workers never interleave a line):
`ready {ok, why}` (`why`: null, `no bundle`, `route`, `reranker`, `pool`, `exit`); `control {k, hit5, of, last, last_audit, ok}`; `search {phase, attempt, call, qid, rc, ms, ok}` (`phase`: `ready`, `control`, `attempt`, `later`, `pool`; `call` is the kept number or null; `qid` only for `later`); `attempt {n, state, cause}` (`state` `start`, `done` or `fault`; `cause` null or `exit`, `whole`, `degraded`, `store`); `store {n, sha256, same}`; `spend {call, qid, usd, total}` (`call`: `reader-<k>`, `grader`, `check`); `counts {attempt}`; `stopped {cause}`; `figures {right, wrong, n, passes}`; `pool {state, seed, size, drawn, digest}`. No `search` line precedes `declaration` and `used`; the wrapper appends each `search` before it returns the output (F3).

### 4 The regression pool [S7, F3; W2-170 section 2, gap 4]
Confirms W2-170 section 2: `<root>/fixtures/evaluation/memory-pool/hidden/<audit>-<qid>.yaml`, flat (a root `pool/` matches no hidden glob; the KPI's "`pool/`" reads as this folder). `pool` adds the sets root's path-map entries `memory-pool` and, for a draw, `memory-pool-draw` (hidden `.../memory-pool-draw/hidden/**`, the roles of `memory-verdict-2`'s) with the code of W2-170 section 7 (text insert, `DC-MAP` as there), nowhere else. Order, one call: (1) `FIGURES.json` exists (`MS-NOFIGURES`), `POOL.json` absent (exit 3); (2) the pool is the files not named `<A>-*`; its digest is W2-170's rule over them; **the seed is recorded first**: default `int(sha256(f"{A}\n{digest}").hexdigest()[:15], 16)`, or `--seed`; `POOL.json` `{"size","drawn","seed","digest"}` and the `pool` event `state: seed` are written before any search; (3) size <= 400: the whole pool is the set `memory-pool`; else `ids = sorted(stems)`, `random.Random(seed).sample(ids, 400)`, the drawn files copied to `memory-pool-draw/hidden/` (made fresh, removed after), measured as that set, the same seed giving the same draw; (4) the run is `gov.retrieval.measure <set> --part hidden` through the wrapper (`phase: pool`, item 12's whole check, no model call), its folder `runs/<A>/pool/`; (5) `POOL.json` gains `{"n","hit5","full","last_audit","last_hit5","last_full","regression"}` and `FIGURES.json`'s `pool` is set to the same; "the last audit's" figures are the `pool` block of the latest earlier audit's `FIGURES.json` (none: no comparison, `regression` false); `regression` is true when the rate of hit@5 or of full evidence is 3.0 points or more under that audit's (rates `hit5/n`, `full/n`), printed `POOL REGRESSION hit@5 <a> -> <b> %` (or `full evidence`), exit 0; (6) the audit's kept questions (not `nonexistent-id`) are copied byte-equal to `memory-pool/hidden/<A>-<qid>.yaml`, a present equal file skipped, a different one `MS-POOLDIFF`. `pool-import` copies, as `<set>-<qid>.yaml`, the 79 questions of `memory-verdict-2`'s `hidden/` and the 138 of `memory-retrieval`'s `visible/` and `hidden/` and `memory-verdict`'s `hidden/` (each less its `nonexistent-id` question: category `nonexistent-id`, ids `h24`, `m60`), derived paths; not exactly 79 and 138: `MS-IMPORTCOUNT`, nothing written; `runs/memory-pool/IMPORTED.json` (counts, digest) is written last and a present one is `MS-IMPORTED`.

### 5 The control [S1, F3; DEC-1097 (1)(b), DEC-1101 (1), gap 5]
The set is `memory-retrieval --part visible` (the fresh 80's own control, `run_measure.sh`; E0's 34 of its 40), run as the attempts are (item 12: batch 10, bundle 6,000, stack 24,000, `GOV_ROLE=orchestrator`, `GOV_STORE` and `GOV_TICKET` unset, the wrapper) on `--repo`, with the declared settings. `last` is `control.hit5` of the `FIGURES.json` of the latest earlier `memory-audit-<date>` run folder that has one (`last_audit` names it); none: 34. In range when its 40 question lines hold, its `families:` line is present, every kept search is answered as declared (else `notready`, not `control`), and `abs(hit5 - last) <= 2` (34 and 33 proceed from 34; 31 stops: exit 2, `STOPPED control`, `USED` as W2-170 wrote it, no attempt folder). The control runs after `declare` and before the audit set's first search (the KPI wording; the fresh 80 ran it before `USED`, so a failed control now leaves the set used, see Open).

### 6 The test seams [S1-S4, S8, F1, F4; gap 6]
`--gov <exe>` is the fake `gov` for the probe, the control, the attempts (through the wrapper), the later searches and the pool; its real path must hold `pin-<12 hex>` and equal `DECLARATION.json`'s `gov_pin` (W2-170 `DC-PIN`; `MS-PIN`), and the planted tests plant that folder as W2-170 section 9 does. `--claude <exe>` is the fake reader and grader, called as the fresh 80 calls it: `-p --safe-mode --tools "" --no-session-persistence --output-format json --model <m> --effort high --max-budget-usd <b> --system-prompt <s> --json-schema <j>`, prompt on standard input, one JSON on standard output with `structured_output`, `usage` and `total_cost_usd` (the one Python seam is `gov.memaudit.claude.run_claude(argv, prompt, cwd)`, replaced by tests that do not use a file). The ready check is one probe search, `gov retrieve "what decides a close" --json` on `--repo` through `--gov`, answered as declared (item 12). The runner reads no server address and starts, stops or loads nothing: the stub Ollama and reranker servers are reached only by the fake `gov`, at the variables the real `gov` already reads (`OLLAMA_HOST`, `GOV_QUERY_OLLAMA_HOST`, and `HOME`'s `.cache/gov-os/rerank.sock`), which the runner passes on unchanged; F4's request logs are the stubs' own. The store watched is `--store`, its sha256 against `DECLARATION.json`'s `store_sha256` (item 12).

### 7 The pinned prompts [S3; DEC-1097 (1)(d), DEC-1098 (1), gap 7]
`src/gov/memaudit/prompts.py` holds, **copied verbatim** from `.gov-runtime/scratch/orchestrator/drafts/d4b/e2_run.py` (sha256 `f0099fd67ef0cb6d9f6f296a86dc4893a1fe15f3110e30074397d7cbcab9d60a`; `e2g_run.py` `35e7a4e5…` and `e3_run.py` `95718dbc…` hold the same strings): `READER_SYS`, `READER_SCHEMA`, `GRADER_SYS`, `GRADER_SCHEMA`, `CAP = 3`, `prompt_of`, `items_of`, `outcome`, `mcnemar`, and the grader's prompt form `"Question: {question}\n\nGold answer: {gold}\n\nAnswer to grade: {said}"`. The refine strings (`REFINE_*`, the glossary) and `UNRANKED_NOTE` are not copied: the glossary is a prototype, not the standard. A test recomputes these (UTF-8 text; a schema as `json.dumps(schema)`, the bytes `--json-schema` carries; a function as its source text from `def` to its last line, no final newline) and compares them with the list; the list is the pin:
```
READER_SYS     a0e222af4a0f9a6ca2cb8e31dd44dc7c21e684c5a0de0e0d081947eacef85e08
READER_SCHEMA  216897d1c451e34033fafd75d1f6be408b0f82dacd5ff885dcad37351c578e5d
GRADER_SYS     58d1ad87b24064b28bb09c498a9915f66f0867ffa1e09565f59fd33c7e2ac6d4
GRADER_SCHEMA  7bfc5786b59231cb7576cdbeeef713ca3524e18205189f73c598ac323c8370a8
grader prompt  c12bc5ee7fe303c4e83d6c8803683e2697b1e2f595ecd382e771e61ead15879e
prompt_of      4a8c1c65619d7111c6dbdc7aae8de6164306ea0366d9410f8ea5095a04fb8c42
items_of       38cb4b5de225235759064e88027287fd8de4c1fa48e24007e1e573d048aa19f1
outcome        41a930d83aa170bb33e703b7daa39d6f9f489db9767c52a152cd1cae23899f13
mcnemar        48e0099533762dd0b2df6f80e7b1f42c0ae214de94d76ea13964cfbe641557d7
```
Models: reader `claude-opus-5-5` (effort high, budget 1.5 USD a call); grader `claude-opus-5-5` (counts) and check `claude-sonnet-5-5` (agreement), 0.5 USD a call; no tools, no transcript; four workers. A call that returns nothing is run once more, never a third time (FRESH-80-1 section 3.5). The reader's cap is 3 attempts as the fresh 80 ran it; the verdict reads the A2 cut of `outcome`, A1 and A3 beside it. The nonexistent-id question counts in `n` and is judged by `outcome`'s `apart` branch (right when not found); the retrieval figures run over the questions with a gold place.

### 8 The printed forms [S2, S3, F1; FRESH-80-1 section 3.4, gap 8]
`judge` prints, after `FIGURES.json` is written (`<..>` are numbers; `pct` is `f"{100*x/n:.1f} %"`; the interval is Clopper-Pearson, `lo`/`hi` in percent, one decimal, by bisection on the binomial tails as `f80lib.exact_interval`):
```
VERDICT right end to end <r> of <n> (<pct>; exact 95 % interval <lo> to <hi> %); wrong claims <w> of <n> (<pct>)
BAR at least <need> right (met|NOT met) and at most <max> wrong claims (met|NOT met): PASSES|MISSES; target at least <target>: reached|not reached
BESIDE hit@5 <a> of <ng> (<pct>); in the first bundle <b>; full evidence <c>; answer correct, citation aside <d> of <n>; not found <e>
BESIDE one search against two: A1 right <x>, A2 right <r>: <g> gains, <l> losses, exact McNemar p <p:.4f>
BESIDE grader agreement <a> of <g>; search failures <s>; calls run once more <k>; spent <usd:.2f> USD (projection <p:.2f>, brake <b:.2f>)
```
`measure` prints after the counting attempt `RETRIEVAL attempt <n>: hit@5 <a> of <ng> (<pct>); hit@10 <b>; hit@20 <c>; MRR <m:.4f>; in the first bundle <d>; full evidence <e>` (the same line for `--kept`), read from the measure's own question lines (`<id> (<part>): hit@5 yes|no (first gold rank <r>|-), in the bundle yes|no; full evidence yes|no`); a faulted attempt's figures are never printed. Bar numbers are W2-170's `DECLARATION.json` `bar`; at n = 40: 34 and 2, target 38.

### 9 `misses.jsonl` [S5, F2; DEC-1129 (2), DEC-1125 (2), gap 9]
Written by `judge` once all rows exist, before `FIGURES.json`, whole by rename, in file-name order, one object per line with exactly these keys in this order: `id`, `question`, `gold_answer`, `gold_sources`, `answer`, `outcome`, `evidence_in_bundle`. A miss is a question whose A2 `outcome(...)["right"]` is false (a question with no row cannot occur: `judge` ends only with every row). `gold_sources` is the question's `sources` exactly as parsed from its YAML; `answer` is the string the grader was shown (the reader's answer, or `Not found.`); **`evidence_in_bundle` is the JSON `true` or `false`** (the auditor brief's form, not `yes`/`no`): the measure's `in the bundle` of the counting attempt. `outcome`: `not_found` when `outcome()` says `nf` or the grader's grade is `not_found`; `incomplete` when the answer was graded `correct` but its citation matches no gold place; `wrong` otherwise. An audit with no miss writes an empty file. It stays under `runs/<A>/`: with the rows it is the only place a question or an answer is written (F1).

### 10 `FIGURES.json` [S6, F1; DEC-1101 (2), DEC-1097 (2), gap 10]
Counts and fixed words only; these keys, no others, all present (`pool`, `classes`: null until `pool`, `classes` fill them):
```
audit, n, n_gold, bar: {need_right, max_wrong, target_right},
verdict: {right, wrong, passes, right_ok, wrong_ok, target_ok, interval_exact: [lo, hi], not_run},
beside: {hit5, hit10, hit20, mrr, in_bundle, full_evidence, correct_citation_aside, not_found, a1_right, a3_right,
         mcnemar_a1_a2: {gains, losses, p}, grader_agree, graded, search_failures},
misses: {total, by_outcome: {wrong, incomplete, not_found}, by_rank: {rank_1_5, rank_6_20, not_in_20},
         by_namespace: {embedded, keyword_only}, by_category: {<the twelve category names>: n}, by_route: {lexical, semantic, both, other, none}},
control: {hit5, of, last, last_audit}, pool: null | {n, hit5, full, last_audit, last_hit5, last_full, regression},
classes: null | {gold_wrong, question_ambiguous, out_of_scope, retrieval_miss, answer_wrong},
spend: {usd, projection, brake}
```
`interval_exact` is `[lo, hi]` as fractions to 4 places. A miss's rank bucket is the first gold rank of the counting attempt (`rank_1_5` is gold in the first 5, `not_in_20` includes no rank). `by_namespace` is `keyword_only` when the question carries `keyword: true`, else `embedded`. `by_route` is the `routes` of the first kept evidence item (calls in order) that matches a gold source: `both` when it holds `lexical` and `semantic`, `lexical`, `semantic`, `other` for any else, `none` when no item matches. `classes` is `classes`' five counts (they sum to `misses.total`).

### 11 Spend and resume [S8, S5, F2; DEC-1091 (2), DEC-1118 (3), DEC-1097 (1), gap 11]
Every model call's `total_cost_usd` is a `spend` event of the audit's `ledger.jsonl` (not a second file); `total` is the run's sum so far, read back from the ledger at start. The projection is `0.157 x n` (n from `DECLARATION.json`; 6.28 USD for 40), or `--projection <usd>`; the brake is twice it (12.56 for 40). Before each question starts, a `total` above the brake writes `STOPPED` `brake`, prints `STOPPED brake`, ends exit 2 once the running questions finish, writes no `misses.jsonl` and no `FIGURES.json`: to the owner first. `judge --resume` is allowed only while `STOPPED` holds `brake` and no `FIGURES.json` exists, and needs a `--projection` above the last one (the owner's raised figure; else exit 4): it renames `STOPPED` to `STOPPED-<k>`, keeps every row file (a question with a row is never asked again, rows written whole), and starts from the ledger's total. Any other `judge` over an existing `reader/`, `STOPPED` or `FIGURES.json`, or a second `measure`, is exit 3: a verdict stands, is never run again and never re-scored (S5, F2).

### 12 The fault rule [S4, F3, F4; FRESH-80-1 section 3.5, DEC-1097 (1)(g), gap 12]
Inside one `measure` call, as `run_measure.sh`: ready check (probe, then `control-<k>`), then `attempt-<n>` through `gov.retrieval.measure memory-audit-<date> --part hidden --root <repo> --sets-root <root> --out <attempt> --gov <wrapper>`, a new folder (an existing one: stop, never reuse). After it: the store's sha256 against `DECLARATION.json`'s `store_sha256`; unequal: `FAULT` `store`, `STOPPED` `store`, exit 2, no restart. The attempt is **whole** only when: the measure exited 0; its question lines number `n`, all `hidden`; it has a total line and a `families:` line equal to the control's; the kept files number the sum of its calls; and no kept output is degraded. Else `FAULT` holds the first cause (`exit`, `whole`, `degraded`); the attempt is kept, never counted. **Degraded** (`f80lib.degraded`, on a kept output's `result`): `result` or `result.evidence` is not a list; `result.facets.lexical` or `.semantic` is missing or its `available` is false; `result.evidence` is non-empty and `result.rerank.by != "service"`; or `result.pool.fallback` is true; an empty bundle with `stopping_reason` `UNRESOLVED_IDS` is not degraded. One restart is in the same call, while no attempt has counted, **after** the ready check again (probe, a new `control-<k>`; not ready: `STOPPED notready` or `control`, exit 2, nothing spent: no restart into the same outage); a fault in `attempt-2`: `STOPPED fault`. A whole attempt writes `DONE`, `COUNTS`, the `counts` event and the `RETRIEVAL` line. A later search by `judge` that fails or is degraded is counted, named by id on standard output, and gives an empty bundle (`f80lib.search`); it is not an attempt fault.

---

## The CTO's rulings on the Interface's open points (delegated, DEC-1112 (3), 2026-11-12 05:20)

1. The control runs after `DECLARATION.json` and `USED`, as S1 and F3 say; a failed control leaves the set used (W2-170's rule).
2. `measure` includes `declare`; W2-172's S1 already reads "the declaration, the control and the measure (W2-171)": no edit there.
3. One adapter, `src/gov/memaudit/matcher.py`, is the only file that imports `gov.retrieval.measure`'s private names.
4. The 400-draw is measured as a copied set (`memory-pool-draw`), one path-map entry in the sets root's own map.
5. No `--restart`: a killed `measure` goes to the owner as a hand ACT.
6. `evidence_in_bundle` is the first bundle only, as the KPI says.
7. The reader's cap is 3, read at the A2 cut, as the fresh 80 ran it.
8. The nonexistent-id question counts in `n` (40), as the declared bar does.
9. The control's set is `memory-retrieval` visible (the fresh 80's `run_measure.sh`); no session opens the sets root to
   confirm it: a missing set ends the ready check (`STOPPED notready`), and the first live run shows it.
10. `pool-import`'s exclusions (category `nonexistent-id`, ids `h24`, `m60`) stand; the count guard (79 and 138) refuses a
    mismatch with nothing written.

## PKG-W2-171-F5-1 and run 2's readings (the CTO, delegated P2, 2026-11-12 07:12)

- **(a) now, (b) before the land:** W2-170's F5 path case is a branch-scoped red on this branch (it judges any branch against
  W2-170's paths): named in the return, it does not block this ticket's review. W2-180 (DAEO-weh2, C1) makes it judge only
  W2-170's own branch; it must land before this ticket's land, or the queue attributes the red to this batch. Not skip_known.json.
- **Readings confirmed:** `counts.attempt` holds the attempt's name (Interface item 3); a control with 0 question lines is
  `notready`, 1 to 39 lines or no `families:` line is `control` (item 5); S2's planted set has 40 questions (W2-170's preflight
  passes 36 to 40; S2's "12" is read as "a planted set"); refusal precedence and `search.ok` for a degraded answer are as built,
  stated in the evidence; eng-1's pool restart after `MS-POOLFAULT` stands. The heavy-slot TMPDIR sits outside `~/gov-os-runs`.

## PKG-W2-171-REV1-1 (the CTO, delegated P2, 2026-11-12 08:04)

(a): the brake cleared at 07:56 (projection 30 USD, counting afresh); round 2 with the test-first form: a test-design batch for F-1
(the VERDICT line's exact interval computed from the counts, not from FIGURES.json's rounded 4-place values: 32 of 40 prints
`64.4 to 90.9 %`), an engineer for F-1 and F-2 (a faulted attempt's figures never printed by `measure --kept`), rebuild, verify,
review round 2 (the last, DEC-1010). F-3 (the --repo tree not checked against audit_commit) is a Wave 3 row; F-4 (an unexpected
worker error leaves reader/ with no STOPPED) is recorded, the hand ACT of ruling 5 covers it.
