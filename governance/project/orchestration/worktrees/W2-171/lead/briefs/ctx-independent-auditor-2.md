{
  "ticket": "DAEO-k1e2",
  "ticket_text": "---\nid: DAEO-k1e2\nstatus: in_progress\ndeps: [DAEO-61vm]\nlinks: [DAEO-52ku, DAEO-2bdu, DAEO-p8tv, DAEO-qz4p]\ncreated: 2026-11-11T01:20:40Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-171\ntags: [wave-2, implementation, memory, audit, full, after-the-lift]\nwbs_id: W2-171\ntitle: 'The memory audit''s measure: the control, the retrieval figures, the judged reader run, the fault rule, the misses file, the regression pool (DEC-1101 (1), DEC-1125 (2))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-61vm\nallowed_paths:\n- src/gov/memaudit/**\n- tests/unit/memaudit/**\n- docs/changes/W2-171-evidence.md\nkpis:\n  success:\n  - 'S1 The control runs first: the standing visible-40 set is measured with the audit''s declared configuration, and its hit@5 must be within 2 of the last audit''s control (the first audit''s control is within 2 of 34, E0''s figure, DEC-1097 (1)(b)). Outside that, nothing is measured, the counts say `control out of range`, and `USED` is left as written by W2-170. Verify: planted fake `gov` returning a control at 34, 33 and 31: the first two proceed, the third stops before the audit set''s first search [DEC-1097 (1), DEC-1101 (1)]'\n  - 'S2 One attempt measures the kept questions with `gov.retrieval.measure`''s matcher and source families: hit@5, full evidence and the first gold rank per question (hit@10, hit@20 and MRR beside them), each search''s ranked output kept so a label is never re-scored by searching again. Verify: a planted set of 12 questions against a fake `gov` with planted ranks: the figures equal the planted ones; the kept outputs re-score to the same figures with `--kept` [DEC-833, DEC-860, DEC-1101 (1)]'\n  - 'S3 The judged reader run: the reader answers each question from its searches with search again once (A2), a named grader judges right end to end with a second grader''s agreement beside it. The reader''s and graders'' prompts are the fresh 80''s, pinned by hash (`READER_SYS`, the schemas, the cut), so audits compare with FRESH-80-RESULT. The verdict line reads: right end to end r of n, wrong claims w of n, the exact 95 % interval, against the scaled bar (at least ceil(0.85 n) right and at most floor(0.05 n) wrong; target ceil(0.95 n)); hit@5, gold in the first bundle, the answer correct with the citation aside and one search against two (exact McNemar) are printed beside it and never judged. Verify: a fake reader and graders with planted verdicts on n=40: the line shows planted r and w and the planted interval; bar 34 and 2 [DEC-1097 (1)(d), DEC-1098 (1), DEC-1101 (1)]'\n  - 'S4 The fault rule, as FRESH-80-1 section 3.5 states it: a search not answered as declared (a bundle not reranked by the shared service, a route missing, the pool''s rerank fallen back), or a store whose sha256 changed during the attempt, makes the attempt not whole. One restart is allowed while no attempt has counted; a second fault stops the audit and goes to the owner in the counts. No restart into the same outage: the live reranker is checked ready before each attempt. Verify: planted degraded search (one restart then pass; two faults then stop); planted store change (stop, no restart) [DEC-1097 (1)(g), DEC-1101 (1)]'\n  - 'S5 A miss is a result: a verdict below either limit stands as recorded, is never run again and never re-scored to pass. The runner writes `runs/<audit>/misses.jsonl`, one line per miss (a question not right end to end at A2): `{\"id\",\"question\",\"gold_answer\",\"gold_sources\",\"answer\",\"outcome\",\"evidence_in_bundle\"}` with `outcome` one of `wrong`, `incomplete`, `not_found` and `evidence_in_bundle` the measure''s own yes or no on whether a gold place was in the first bundle; an audit with no miss writes an empty file. Verify: planted run with 5 misses: the file holds 5 lines in that form; a second run on the same audit is refused by W2-170''s `USED`; the file is the auditor brief''s input form (parsed by the brief''s own field list) [DEC-1074 (1), DEC-1101 (1), DEC-1125 (2)]'\n  - 'S6 `runs/<audit>/FIGURES.json` carries counts only: the verdict numbers, the beside figures, and for the misses, counts by rank bucket (gold at rank 6 to 20; not in the first 20), by namespace of the gold source (embedded; keyword only), by category and by route; with the auditor''s class counts added after its run. Verify: schema check over a planted run; grep for a planted question word, a planted gold path and a planted answer finds none [DEC-1101 (2), DEC-1097 (2)]'\n  - 'S7 The regression pool: after a measured audit its kept questions join `pool/` under the sets root (hidden, like a set). Each audit re-runs the pool through the retrieval measure only (hit@5 and full evidence, no model tokens): the whole pool while it holds 400 questions or fewer, else a seeded draw of 400 (the seed recorded first). The pool''s figures are printed beside the last audit''s, and a fall of 3 points or more in either is named a regression in the counts. The 79 of the fresh 80 and the 138 of earlier sets are added by one planted-tested import path, run once by the CTO. Verify: planted pools of 300 and 900 questions: whole, then a draw of 400 with the same seed twice giving the same draw; a planted fall of 4 points is named [DEC-1101 (1), DEC-1125 (2)]'\n  - 'S8 The spend is bounded and recorded: each model call''s `total_cost_usd` goes to the run''s ledger; the run stops at twice its projection (the fresh 80''s 0.157 USD a question, so 12.6 USD for 40), and a brake stop goes to the owner first; a stopped run resumes without re-asking finished questions. Verify: planted ledger over the brake: stops; resume asks only the unfinished [DEC-1097 (1), DEC-1118 (3)]'\n  failure:\n  - 'A question, gold answer, answer or source path in standard output, a log or an error text; only ids, counts and digests leave. Verify: a planted run on the fake reader and graders with a unique word in a question, a gold answer, an answer and a source path: grep of standard output, standard error, every log and `FIGURES.json` finds each 0 times'\n  - 'A set measured twice, or re-scored to pass; a label changed after its figures exist. Verify: a planted miss (S5): a second run on the same audit is refused by W2-170''s `USED` and `misses.jsonl` is byte-identical before and after the refusal; a planted verdict below the bar stays as recorded'\n  - 'A search made before `DECLARATION.json` and `USED` exist (W2-170); the store rebuilt during an attempt. Verify: the planted run''s call ledger: no search entry earlier than the file times of `DECLARATION.json` and `USED`; S4''s planted store change stops the attempt with no rebuild call in the ledger'\n  - 'The shared Ollama servers or the reranker service touched other than by their ordinary query calls. Verify: a planted run with stub servers on stand-in ports: their request logs hold only query calls, and no stop, restart, model load or unload call; no process of either server is signalled'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: FULL\nsources:\n- DEC-1101\n- DEC-1125\n- DEC-1098\n- DEC-1097\n- DEC-1074\n- DEC-833\n- DEC-860\n- DEC-1118\n- DEC-1050\n- DEC-1073\n- DEC-1052\n- DEC-1129\nest_loc: 600\nacceptance_tests:\n  path: tests/acceptance/W2-171/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines, before the engineer, on a planted set, a fake `gov` and a fake model; never a real search, GPU call or the real sets root'\ntrack: B\nlist_rows: []\nreads:  # declared by the CTO 11-11 (gov brief READS_MISSING; DEC-1121): what it reads that it does not write\n- governance/project/orchestration/packages/MEMORY-AUDIT-1.md\n- src/gov/retrieval/retrieve.py\nneeds: []\nwaits_on: []\n---\n# W2-171 The memory audit's measure\n\nThe measured part of one audit (DEC-1125 (2)): the control, the retrieval figures, the judged end-to-end run, and\nwhat feeds the auditor. It generalises the fresh 80's tools (`.gov-runtime/scratch/orchestrator/drafts/fresh80/`:\n`f80lib.py`, `run_measure.sh`, `fresh80_reader.py`, `fresh80_figures.py`), which were built for one set. The CTO copies\nthem to `.gov-runtime/scratch/ref/fresh80/` in the worktree when the ticket starts. W2-170 comes first.\n\n- **Why a tool and not the fresh 80's scripts:** those pin one set name and one run folder; a weekly audit needs the\n  same steps for a new set each time, tested on a planted set.\n- **Alternatives (one line each):** end to end for the pool as well as the fresh set (rejected: about 0.16 USD a\n  question, so the pool's cost grows each week); no pool (rejected: DEC-1101 (1) asks for the regression check).\n- **Not here:** the set's checks and the declaration (W2-170); the cycle (W2-172); the miss classes by the auditor\n  session (its brief; the launch script).\n\n[DEC-1101 (1); DEC-1125 (2)]\n\n## Interface\n\nStated by the CTO before the pair starts (DEC-1052; PKG-W2-171-IFACE-1, option (a)). The test designer writes tests to this block and the engineer conforms to it; neither changes it. A gap or a clash goes back to the CTO as a package. Bracketed lines name the KPI line each item serves (S1 to S8; F1 to F5 are the `failure:` lines in order) and its source. W2-170's Interface (DAEO-61vm, sections 1 to 10) holds and is imported, never copied: `layout.paths`, `ledger.append`, `say.say`, `declare.declare`; this block adds to it and changes none of it. The three approved briefs are not changed by anything here (DEC-1129 (2)).\n\n### 1 The command line [S1-S8, F1; W2-170 section 1, PKG-W2-171-IFACE-1 gap 1]\nFive subcommands join `python3 -m gov.memaudit` (`--help` prints usage, exit 0); W2-172's `run` calls them and calls no `declare` of its own.\n- `measure`: `declare` (W2-170: `DECLARATION.json`, then `USED`), the ready check, the control, the attempts and the fault rule, the retrieval figures (S1, S2, S4). `measure --kept <n>` runs none of that: it re-scores `attempt-<n>`'s kept outputs through `gov.retrieval.measure --kept` (that measure's own flag, on the derived folder), prints the `RETRIEVAL` line of item 8, writes nothing, exits 0 or 1 `MS-KEPT`, never 3 (S2).\n- `judge`: the reader run, the two graders, the verdict, `misses.jsonl`, `FIGURES.json` (S3, S5, S6, S8); `--resume` after a brake stop.\n- `classes`: reads `runs/<A>/miss-classes.json` (the launch script's delivered copy of the auditor's `classes.json`, `{\"<id>\": {\"class\", \"reason\"}}`) and adds the five class counts to `FIGURES.json` (S6); `MS-CLASSES` (exit 1) when its ids are not exactly `misses.jsonl`'s.\n- `pool`: the pool's re-run and the audit's questions joining the pool (S7). `pool-import`: S7's one-time import, run once by the CTO.\nFlags as W2-170 section 1 (`--sets-root`, `--audit` required; every flag with a value takes a bare name, a number, a hash or a path outside the sets root; never a folder under it): `--repo`, `--commit`, `--store`, `--gov`, `--decision` as `declare`'s (`measure`); `--repo`, `--gov` (`judge`, `pool`); `--claude <exe>` (`judge`, default `~/.local/bin/claude`); `--projection <usd>` (`judge`, item 11); `--kept <n>` (`measure`, a number); `--seed <n>` (`pool`, item 4). `--resume` (`judge`) is the one flag without a value. `pool-import` takes `--sets-root` only; its source folders are derived (item 4). Printing is `say`'s alone; every child process's standard error goes to a file in the run folder, never printed (F1).\n\n### 2 Exit codes [S1, S4, S8, F2; W2-170 section 5, gap 2]\nSame five as W2-170: 0 ok, 1 refused (a code printed, nothing written beyond what the item says), 2 stopped, 3 used, 4 usage (also an unexpected error: the one line `ERROR: <class>`). W2-170's `DC-`/`PF-` codes pass through `measure` unchanged. Exit 2 replaces W2-170's \"void\": it means the audit began and cannot go on; it writes `runs/<A>/STOPPED` holding one cause word, prints `STOPPED <cause>`, and **goes to the owner** (W2-172 stops on any non-zero; only exit 2 carries the owner's decision).\n\n| exit | when |\n|---|---|\n| 0 | `measure`: an attempt counts (`COUNTS` written). `judge`: `FIGURES.json` written, a MISS included (a miss is a result, S5). `pool`: ran, **a regression included** (printed, in `POOL.json`). `classes`, `pool-import`: done |\n| 1 | `MS-NOCOUNT` (`judge`, no `COUNTS`); `MS-NOFIGURES` (`pool`, `classes`); `MS-DIGEST` (the set's digest now is not `DECLARATION.json`'s); `MS-PIN` (`judge`, `pool`: `--gov`'s pin is not `gov_pin`); `MS-FIRSTS` (a question without a measured first call); `MS-POOLFAULT`; `MS-POOLDIFF`; `MS-IMPORTED`; `MS-IMPORTCOUNT`; `MS-KEPT`; `MS-CLASSES` |\n| 2 | `STOPPED` cause, a closed list: `control` (out of range, S1), `notready` (the probe search not answered as declared, before an attempt or the restart), `fault` (a second fault, S4), `store` (sha256 changed, S4), `brake` (twice the projection, S8) |\n| 3 | `USED` exists (`measure`); `judge` when `FIGURES.json` exists, or `reader/` or `STOPPED` exists and `--resume` is not given, or `--resume` and its conditions (item 11) do not hold; `pool` when `POOL.json` exists. Nothing is written; printed `USED` |\n| 4 | usage, as W2-170 |\n\n### 3 The layout under `runs/<A>/` and the ledger [S1-S8, F3; W2-170 section 2, gap 3]\nW2-170's files stay (`PREFLIGHT.json DROPS.json DECLARATION.json USED ledger.jsonl`). W2-171 adds, from the fresh 80's own (`run_measure.sh`, `fresh80_reader.py`), all written whole by temporary name then rename:\n```\ngov                 the wrapper (a Python file, mode 700) that keeps each retrieve call and appends its search event\nready               not a file: the probe's result is a ledger event\ncontrol-<k>/        kept/00001.json.., measure.txt, measure.err, ms          k = 1, 2: one before each attempt\nattempt-<n>/        kept/00001.json.., measure.txt, measure.err, ms, ENDED, FAULT (one cause word), DONE      n = 1, 2\nCOUNTS              the counting attempt's name (attempt-1 or attempt-2), written when it is DONE\nSTOPPED             the cause word (item 2); absent while the audit goes on\nreader/             plan.json, <qid>.json (the fresh 80's row, keys as fresh80_reader.py's one(), kind \"audit\"), .lock\nmisses.jsonl  FIGURES.json  POOL.json  pool/ (kept/, measure.txt: the pool's run)\n```\n`ledger.jsonl` events (W2-170's `seq`, `at`, `event`, then these fields; `at` is ISO UTC to the microsecond, comparable to file mtimes; numbers, ids and codes only; appends are serialised by one lock in the process, so four workers never interleave a line):\n`ready {ok, why}` (`why`: null, `no bundle`, `route`, `reranker`, `pool`, `exit`); `control {k, hit5, of, last, last_audit, ok}`; `search {phase, attempt, call, qid, rc, ms, ok}` (`phase`: `ready`, `control`, `attempt`, `later`, `pool`; `call` is the kept number or null; `qid` only for `later`); `attempt {n, state, cause}` (`state` `start`, `done` or `fault`; `cause` null or `exit`, `whole`, `degraded`, `store`); `store {n, sha256, same}`; `spend {call, qid, usd, total}` (`call`: `reader-<k>`, `grader`, `check`); `counts {attempt}`; `stopped {cause}`; `figures {right, wrong, n, passes}`; `pool {state, seed, size, drawn, digest}`. No `search` line precedes `declaration` and `used`; the wrapper appends each `search` before it returns the output (F3).\n\n### 4 The regression pool [S7, F3; W2-170 section 2, gap 4]\nConfirms W2-170 section 2: `<root>/fixtures/evaluation/memory-pool/hidden/<audit>-<qid>.yaml`, flat (a root `pool/` matches no hidden glob; the KPI's \"`pool/`\" reads as this folder). `pool` adds the sets root's path-map entries `memory-pool` and, for a draw, `memory-pool-draw` (hidden `.../memory-pool-draw/hidden/**`, the roles of `memory-verdict-2`'s) with the code of W2-170 section 7 (text insert, `DC-MAP` as there), nowhere else. Order, one call: (1) `FIGURES.json` exists (`MS-NOFIGURES`), `POOL.json` absent (exit 3); (2) the pool is the files not named `<A>-*`; its digest is W2-170's rule over them; **the seed is recorded first**: default `int(sha256(f\"{A}\\n{digest}\").hexdigest()[:15], 16)`, or `--seed`; `POOL.json` `{\"size\",\"drawn\",\"seed\",\"digest\"}` and the `pool` event `state: seed` are written before any search; (3) size <= 400: the whole pool is the set `memory-pool`; else `ids = sorted(stems)`, `random.Random(seed).sample(ids, 400)`, the drawn files copied to `memory-pool-draw/hidden/` (made fresh, removed after), measured as that set, the same seed giving the same draw; (4) the run is `gov.retrieval.measure <set> --part hidden` through the wrapper (`phase: pool`, item 12's whole check, no model call), its folder `runs/<A>/pool/`; (5) `POOL.json` gains `{\"n\",\"hit5\",\"full\",\"last_audit\",\"last_hit5\",\"last_full\",\"regression\"}` and `FIGURES.json`'s `pool` is set to the same; \"the last audit's\" figures are the `pool` block of the latest earlier audit's `FIGURES.json` (none: no comparison, `regression` false); `regression` is true when the rate of hit@5 or of full evidence is 3.0 points or more under that audit's (rates `hit5/n`, `full/n`), printed `POOL REGRESSION hit@5 <a> -> <b> %` (or `full evidence`), exit 0; (6) the audit's kept questions (not `nonexistent-id`) are copied byte-equal to `memory-pool/hidden/<A>-<qid>.yaml`, a present equal file skipped, a different one `MS-POOLDIFF`. `pool-import` copies, as `<set>-<qid>.yaml`, the 79 questions of `memory-verdict-2`'s `hidden/` and the 138 of `memory-retrieval`'s `visible/` and `hidden/` and `memory-verdict`'s `hidden/` (each less its `nonexistent-id` question: category `nonexistent-id`, ids `h24`, `m60`), derived paths; not exactly 79 and 138: `MS-IMPORTCOUNT`, nothing written; `runs/memory-pool/IMPORTED.json` (counts, digest) is written last and a present one is `MS-IMPORTED`.\n\n### 5 The control [S1, F3; DEC-1097 (1)(b), DEC-1101 (1), gap 5]\nThe set is `memory-retrieval --part visible` (the fresh 80's own control, `run_measure.sh`; E0's 34 of its 40), run as the attempts are (item 12: batch 10, bundle 6,000, stack 24,000, `GOV_ROLE=orchestrator`, `GOV_STORE` and `GOV_TICKET` unset, the wrapper) on `--repo`, with the declared settings. `last` is `control.hit5` of the `FIGURES.json` of the latest earlier `memory-audit-<date>` run folder that has one (`last_audit` names it); none: 34. In range when its 40 question lines hold, its `families:` line is present, every kept search is answered as declared (else `notready`, not `control`), and `abs(hit5 - last) <= 2` (34 and 33 proceed from 34; 31 stops: exit 2, `STOPPED control`, `USED` as W2-170 wrote it, no attempt folder). The control runs after `declare` and before the audit set's first search (the KPI wording; the fresh 80 ran it before `USED`, so a failed control now leaves the set used, see Open).\n\n### 6 The test seams [S1-S4, S8, F1, F4; gap 6]\n`--gov <exe>` is the fake `gov` for the probe, the control, the attempts (through the wrapper), the later searches and the pool; its real path must hold `pin-<12 hex>` and equal `DECLARATION.json`'s `gov_pin` (W2-170 `DC-PIN`; `MS-PIN`), and the planted tests plant that folder as W2-170 section 9 does. `--claude <exe>` is the fake reader and grader, called as the fresh 80 calls it: `-p --safe-mode --tools \"\" --no-session-persistence --output-format json --model <m> --effort high --max-budget-usd <b> --system-prompt <s> --json-schema <j>`, prompt on standard input, one JSON on standard output with `structured_output`, `usage` and `total_cost_usd` (the one Python seam is `gov.memaudit.claude.run_claude(argv, prompt, cwd)`, replaced by tests that do not use a file). The ready check is one probe search, `gov retrieve \"what decides a close\" --json` on `--repo` through `--gov`, answered as declared (item 12). The runner reads no server address and starts, stops or loads nothing: the stub Ollama and reranker servers are reached only by the fake `gov`, at the variables the real `gov` already reads (`OLLAMA_HOST`, `GOV_QUERY_OLLAMA_HOST`, and `HOME`'s `.cache/gov-os/rerank.sock`), which the runner passes on unchanged; F4's request logs are the stubs' own. The store watched is `--store`, its sha256 against `DECLARATION.json`'s `store_sha256` (item 12).\n\n### 7 The pinned prompts [S3; DEC-1097 (1)(d), DEC-1098 (1), gap 7]\n`src/gov/memaudit/prompts.py` holds, **copied verbatim** from `.gov-runtime/scratch/orchestrator/drafts/d4b/e2_run.py` (sha256 `f0099fd67ef0cb6d9f6f296a86dc4893a1fe15f3110e30074397d7cbcab9d60a`; `e2g_run.py` `35e7a4e5\u2026` and `e3_run.py` `95718dbc\u2026` hold the same strings): `READER_SYS`, `READER_SCHEMA`, `GRADER_SYS`, `GRADER_SCHEMA`, `CAP = 3`, `prompt_of`, `items_of`, `outcome`, `mcnemar`, and the grader's prompt form `\"Question: {question}\\n\\nGold answer: {gold}\\n\\nAnswer to grade: {said}\"`. The refine strings (`REFINE_*`, the glossary) and `UNRANKED_NOTE` are not copied: the glossary is a prototype, not the standard. A test recomputes these (UTF-8 text; a schema as `json.dumps(schema)`, the bytes `--json-schema` carries; a function as its source text from `def` to its last line, no final newline) and compares them with the list; the list is the pin:\n```\nREADER_SYS     a0e222af4a0f9a6ca2cb8e31dd44dc7c21e684c5a0de0e0d081947eacef85e08\nREADER_SCHEMA  216897d1c451e34033fafd75d1f6be408b0f82dacd5ff885dcad37351c578e5d\nGRADER_SYS     58d1ad87b24064b28bb09c498a9915f66f0867ffa1e09565f59fd33c7e2ac6d4\nGRADER_SCHEMA  7bfc5786b59231cb7576cdbeeef713ca3524e18205189f73c598ac323c8370a8\ngrader prompt  c12bc5ee7fe303c4e83d6c8803683e2697b1e2f595ecd382e771e61ead15879e\nprompt_of      4a8c1c65619d7111c6dbdc7aae8de6164306ea0366d9410f8ea5095a04fb8c42\nitems_of       38cb4b5de225235759064e88027287fd8de4c1fa48e24007e1e573d048aa19f1\noutcome        41a930d83aa170bb33e703b7daa39d6f9f489db9767c52a152cd1cae23899f13\nmcnemar        48e0099533762dd0b2df6f80e7b1f42c0ae214de94d76ea13964cfbe641557d7\n```\nModels: reader `claude-opus-5-5` (effort high, budget 1.5 USD a call); grader `claude-opus-5-5` (counts) and check `claude-sonnet-5-5` (agreement), 0.5 USD a call; no tools, no transcript; four workers. A call that returns nothing is run once more, never a third time (FRESH-80-1 section 3.5). The reader's cap is 3 attempts as the fresh 80 ran it; the verdict reads the A2 cut of `outcome`, A1 and A3 beside it. The nonexistent-id question counts in `n` and is judged by `outcome`'s `apart` branch (right when not found); the retrieval figures run over the questions with a gold place.\n\n### 8 The printed forms [S2, S3, F1; FRESH-80-1 section 3.4, gap 8]\n`judge` prints, after `FIGURES.json` is written (`<..>` are numbers; `pct` is `f\"{100*x/n:.1f} %\"`; the interval is Clopper-Pearson, `lo`/`hi` in percent, one decimal, by bisection on the binomial tails as `f80lib.exact_interval`):\n```\nVERDICT right end to end <r> of <n> (<pct>; exact 95 % interval <lo> to <hi> %); wrong claims <w> of <n> (<pct>)\nBAR at least <need> right (met|NOT met) and at most <max> wrong claims (met|NOT met): PASSES|MISSES; target at least <target>: reached|not reached\nBESIDE hit@5 <a> of <ng> (<pct>); in the first bundle <b>; full evidence <c>; answer correct, citation aside <d> of <n>; not found <e>\nBESIDE one search against two: A1 right <x>, A2 right <r>: <g> gains, <l> losses, exact McNemar p <p:.4f>\nBESIDE grader agreement <a> of <g>; search failures <s>; calls run once more <k>; spent <usd:.2f> USD (projection <p:.2f>, brake <b:.2f>)\n```\n`measure` prints after the counting attempt `RETRIEVAL attempt <n>: hit@5 <a> of <ng> (<pct>); hit@10 <b>; hit@20 <c>; MRR <m:.4f>; in the first bundle <d>; full evidence <e>` (the same line for `--kept`), read from the measure's own question lines (`<id> (<part>): hit@5 yes|no (first gold rank <r>|-), in the bundle yes|no; full evidence yes|no`); a faulted attempt's figures are never printed. Bar numbers are W2-170's `DECLARATION.json` `bar`; at n = 40: 34 and 2, target 38.\n\n### 9 `misses.jsonl` [S5, F2; DEC-1129 (2), DEC-1125 (2), gap 9]\nWritten by `judge` once all rows exist, before `FIGURES.json`, whole by rename, in file-name order, one object per line with exactly these keys in this order: `id`, `question`, `gold_answer`, `gold_sources`, `answer`, `outcome`, `evidence_in_bundle`. A miss is a question whose A2 `outcome(...)[\"right\"]` is false (a question with no row cannot occur: `judge` ends only with every row). `gold_sources` is the question's `sources` exactly as parsed from its YAML; `answer` is the string the grader was shown (the reader's answer, or `Not found.`); **`evidence_in_bundle` is the JSON `true` or `false`** (the auditor brief's form, not `yes`/`no`): the measure's `in the bundle` of the counting attempt. `outcome`: `not_found` when `outcome()` says `nf` or the grader's grade is `not_found`; `incomplete` when the answer was graded `correct` but its citation matches no gold place; `wrong` otherwise. An audit with no miss writes an empty file. It stays under `runs/<A>/`: with the rows it is the only place a question or an answer is written (F1).\n\n### 10 `FIGURES.json` [S6, F1; DEC-1101 (2), DEC-1097 (2), gap 10]\nCounts and fixed words only; these keys, no others, all present (`pool`, `classes`: null until `pool`, `classes` fill them):\n```\naudit, n, n_gold, bar: {need_right, max_wrong, target_right},\nverdict: {right, wrong, passes, right_ok, wrong_ok, target_ok, interval_exact: [lo, hi], not_run},\nbeside: {hit5, hit10, hit20, mrr, in_bundle, full_evidence, correct_citation_aside, not_found, a1_right, a3_right,\n         mcnemar_a1_a2: {gains, losses, p}, grader_agree, graded, search_failures},\nmisses: {total, by_outcome: {wrong, incomplete, not_found}, by_rank: {rank_1_5, rank_6_20, not_in_20},\n         by_namespace: {embedded, keyword_only}, by_category: {<the twelve category names>: n}, by_route: {lexical, semantic, both, other, none}},\ncontrol: {hit5, of, last, last_audit}, pool: null | {n, hit5, full, last_audit, last_hit5, last_full, regression},\nclasses: null | {gold_wrong, question_ambiguous, out_of_scope, retrieval_miss, answer_wrong},\nspend: {usd, projection, brake}\n```\n`interval_exact` is `[lo, hi]` as fractions to 4 places. A miss's rank bucket is the first gold rank of the counting attempt (`rank_1_5` is gold in the first 5, `not_in_20` includes no rank). `by_namespace` is `keyword_only` when the question carries `keyword: true`, else `embedded`. `by_route` is the `routes` of the first kept evidence item (calls in order) that matches a gold source: `both` when it holds `lexical` and `semantic`, `lexical`, `semantic`, `other` for any else, `none` when no item matches. `classes` is `classes`' five counts (they sum to `misses.total`).\n\n### 11 Spend and resume [S8, S5, F2; DEC-1091 (2), DEC-1118 (3), DEC-1097 (1), gap 11]\nEvery model call's `total_cost_usd` is a `spend` event of the audit's `ledger.jsonl` (not a second file); `total` is the run's sum so far, read back from the ledger at start. The projection is `0.157 x n` (n from `DECLARATION.json`; 6.28 USD for 40), or `--projection <usd>`; the brake is twice it (12.56 for 40). Before each question starts, a `total` above the brake writes `STOPPED` `brake`, prints `STOPPED brake`, ends exit 2 once the running questions finish, writes no `misses.jsonl` and no `FIGURES.json`: to the owner first. `judge --resume` is allowed only while `STOPPED` holds `brake` and no `FIGURES.json` exists, and needs a `--projection` above the last one (the owner's raised figure; else exit 4): it renames `STOPPED` to `STOPPED-<k>`, keeps every row file (a question with a row is never asked again, rows written whole), and starts from the ledger's total. Any other `judge` over an existing `reader/`, `STOPPED` or `FIGURES.json`, or a second `measure`, is exit 3: a verdict stands, is never run again and never re-scored (S5, F2).\n\n### 12 The fault rule [S4, F3, F4; FRESH-80-1 section 3.5, DEC-1097 (1)(g), gap 12]\nInside one `measure` call, as `run_measure.sh`: ready check (probe, then `control-<k>`), then `attempt-<n>` through `gov.retrieval.measure memory-audit-<date> --part hidden --root <repo> --sets-root <root> --out <attempt> --gov <wrapper>`, a new folder (an existing one: stop, never reuse). After it: the store's sha256 against `DECLARATION.json`'s `store_sha256`; unequal: `FAULT` `store`, `STOPPED` `store`, exit 2, no restart. The attempt is **whole** only when: the measure exited 0; its question lines number `n`, all `hidden`; it has a total line and a `families:` line equal to the control's; the kept files number the sum of its calls; and no kept output is degraded. Else `FAULT` holds the first cause (`exit`, `whole`, `degraded`); the attempt is kept, never counted. **Degraded** (`f80lib.degraded`, on a kept output's `result`): `result` or `result.evidence` is not a list; `result.facets.lexical` or `.semantic` is missing or its `available` is false; `result.evidence` is non-empty and `result.rerank.by != \"service\"`; or `result.pool.fallback` is true; an empty bundle with `stopping_reason` `UNRESOLVED_IDS` is not degraded. One restart is in the same call, while no attempt has counted, **after** the ready check again (probe, a new `control-<k>`; not ready: `STOPPED notready` or `control`, exit 2, nothing spent: no restart into the same outage); a fault in `attempt-2`: `STOPPED fault`. A whole attempt writes `DONE`, `COUNTS`, the `counts` event and the `RETRIEVAL` line. A later search by `judge` that fails or is degraded is counted, named by id on standard output, and gives an empty bundle (`f80lib.search`); it is not an attempt fault.\n\n---\n\n## The CTO's rulings on the Interface's open points (delegated, DEC-1112 (3), 2026-11-12 05:20)\n\n1. The control runs after `DECLARATION.json` and `USED`, as S1 and F3 say; a failed control leaves the set used (W2-170's rule).\n2. `measure` includes `declare`; W2-172's S1 already reads \"the declaration, the control and the measure (W2-171)\": no edit there.\n3. One adapter, `src/gov/memaudit/matcher.py`, is the only file that imports `gov.retrieval.measure`'s private names.\n4. The 400-draw is measured as a copied set (`memory-pool-draw`), one path-map entry in the sets root's own map.\n5. No `--restart`: a killed `measure` goes to the owner as a hand ACT.\n6. `evidence_in_bundle` is the first bundle only, as the KPI says.\n7. The reader's cap is 3, read at the A2 cut, as the fresh 80 ran it.\n8. The nonexistent-id question counts in `n` (40), as the declared bar does.\n9. The control's set is `memory-retrieval` visible (the fresh 80's `run_measure.sh`); no session opens the sets root to\n   confirm it: a missing set ends the ready check (`STOPPED notready`), and the first live run shows it.\n10. `pool-import`'s exclusions (category `nonexistent-id`, ids `h24`, `m60`) stand; the count guard (79 and 138) refuses a\n    mismatch with nothing written.\n\n## PKG-W2-171-F5-1 and run 2's readings (the CTO, delegated P2, 2026-11-12 07:12)\n\n- **(a) now, (b) before the land:** W2-170's F5 path case is a branch-scoped red on this branch (it judges any branch against\n  W2-170's paths): named in the return, it does not block this ticket's review. W2-180 (DAEO-weh2, C1) makes it judge only\n  W2-170's own branch; it must land before this ticket's land, or the queue attributes the red to this batch. Not skip_known.json.\n- **Readings confirmed:** `counts.attempt` holds the attempt's name (Interface item 3); a control with 0 question lines is\n  `notready`, 1 to 39 lines or no `families:` line is `control` (item 5); S2's planted set has 40 questions (W2-170's preflight\n  passes 36 to 40; S2's \"12\" is read as \"a planted set\"); refusal precedence and `search.ok` for a degraded answer are as built,\n  stated in the evidence; eng-1's pool restart after `MS-POOLFAULT` stands. The heavy-slot TMPDIR sits outside `~/gov-os-runs`.\n\n## PKG-W2-171-REV1-1 (the CTO, delegated P2, 2026-11-12 08:04)\n\n(a): the brake cleared at 07:56 (projection 30 USD, counting afresh); round 2 with the test-first form: a test-design batch for F-1\n(the VERDICT line's exact interval computed from the counts, not from FIGURES.json's rounded 4-place values: 32 of 40 prints\n`64.4 to 90.9 %`), an engineer for F-1 and F-2 (a faulted attempt's figures never printed by `measure --kept`), rebuild, verify,\nreview round 2 (the last, DEC-1010). F-3 (the --repo tree not checked against audit_commit) is a Wave 3 row; F-4 (an unexpected\nworker error leaves reader/ with no STOPPED) is recorded, the hand ACT of ruling 5 covers it.\n",
  "authority": [
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    },
    {
      "id": "DEC-1125",
      "sha256": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "reason": "declared in sources",
      "tokens": 945
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-1074",
      "sha256": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "reason": "declared in sources",
      "tokens": 900
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-860",
      "sha256": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "reason": "declared in sources",
      "tokens": 416
    },
    {
      "id": "DEC-1118",
      "sha256": "368cb8b5376e4b1d2c62ee606d7a3faf0d2521a2275555627996428e9d18bd15",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "368cb8b5376e4b1d2c62ee606d7a3faf0d2521a2275555627996428e9d18bd15",
      "reason": "declared in sources",
      "tokens": 578
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
    },
    {
      "id": "DEC-1129",
      "sha256": "5845f535427da47c105cd0aaf2c357d1cc033402900c0b68767d09063696bbcc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5845f535427da47c105cd0aaf2c357d1cc033402900c0b68767d09063696bbcc",
      "reason": "declared in sources",
      "tokens": 557
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 1467
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    },
    {
      "id": "DEC-1125",
      "sha256": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "reason": "declared in sources",
      "tokens": 945
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-1074",
      "sha256": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "reason": "declared in sources",
      "tokens": 900
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-860",
      "sha256": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "reason": "declared in sources",
      "tokens": 416
    },
    {
      "id": "DEC-1118",
      "sha256": "368cb8b5376e4b1d2c62ee606d7a3faf0d2521a2275555627996428e9d18bd15",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "368cb8b5376e4b1d2c62ee606d7a3faf0d2521a2275555627996428e9d18bd15",
      "reason": "declared in sources",
      "tokens": 578
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
    },
    {
      "id": "DEC-1129",
      "sha256": "5845f535427da47c105cd0aaf2c357d1cc033402900c0b68767d09063696bbcc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5845f535427da47c105cd0aaf2c357d1cc033402900c0b68767d09063696bbcc",
      "reason": "declared in sources",
      "tokens": 557
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 1467
    }
  ],
  "supplementary": [
    {
      "id": "39c783f3deadddc6d9655a2b",
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "text": "## 2. Your folder and your tree\n- **Your folder** holds `brief.md`, `seed.txt`, `CLAUDE.md`, `input/` (read-only) and `out/` (the only place you\n  write). You have only Read, Grep, Glob, Write and TodoWrite: no shell, no web, no subagents. Grep and Glob over your\n  tree read the repository; they are not memory's search.\n- **Your tree** is a plain, read-only copy of the repository at the pinned commit (`PIN`, named in `CLAUDE.md`), the\n  commit the audit measured. It is called `REPO` below.\n- **Input:**\n  - `input/set/` holds the audit's questions, one file each, in the writer's form (`id`, `question`, `gold_answer`,\n    `sources`, `commit`, `category`, `drawn`, optionally `keyword` and `naive_answer`).\n  - `input/misses.jsonl` holds one line for each miss, written by the launch script's own code from the measure:\n    `{\"id\", \"question\", \"gold_answer\", \"gold_sources\", \"answer\", \"outcome\", \"evidence_in_bundle\"}`.\n    `answer` is what the agent said. `outcome` is `wrong`, `incomplete` or `not_found`. `evidence_in_bundle` is `true`\n    when memory put a gold place in front of the agent, and `false` when it did not. It is the only fact about the\n    search you are given.\n\n",
      "tokens": 297
    },
    {
      "id": "d5a54f0775b7268834c8cade",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "text": "## 2. Your folder and your tree\n- **Your folder** holds `brief.md`, `seed.txt`, `CLAUDE.md`, `input/` (read-only) and `out/` (the only place you\n  write). You have only Read, Grep, Glob, Write and TodoWrite: no shell, no web, no subagents. Grep and Glob over your\n  tree read the repository; they are not memory's search.\n- **Your tree** is a plain, read-only copy of the repository at the pinned commit (`PIN`, named in `CLAUDE.md`), the\n  commit the audit measured. It is called `REPO` below.\n- **Input:**\n  - `input/set/` holds the audit's questions, one file each, in the writer's form (`id`, `question`, `gold_answer`,\n    `sources`, `commit`, `category`, `drawn`, optionally `keyword` and `naive_answer`).\n  - `input/misses.jsonl` holds one line for each miss, written by the launch script's own code from the measure:\n    `{\"id\", \"question\", \"gold_answer\", \"gold_sources\", \"answer\", \"outcome\", \"evidence_in_bundle\"}`.\n    `answer` is what the agent said. `outcome` is `wrong`, `incomplete` or `not_found`. `evidence_in_bundle` is `true`\n    when memory put a gold place in front of the agent, and `false` when it did not. It is the only fact about the\n    search you are given.\n\n",
      "tokens": 297
    },
    {
      "id": "5c13c16833ed3dcf1ccafdf4",
      "path": "tests/unit/orchestration/test_w2_149_indep_launch.py",
      "text": "def test_auditor_delivers_its_classes_and_the_audit_is_logged(w):\n    w.plant_set()\n    (w.sets / \"runs\" / \"e0\").mkdir(parents=True)\n    (w.sets / \"runs\" / \"e0\" / \"misses.jsonl\").write_text(\"\".join(  # W2-173 S4: classes keyed by the misses' ids\n        json.dumps({\"id\": i, \"question\": \"q\", \"gold_answer\": \"g\", \"gold_sources\": [\"s\"], \"answer\": \"a\",\n                    \"outcome\": \"wrong\", \"evidence_in_bundle\": False}) + \"\\n\" for i in (\"m1\", \"m2\")))\n    classes_text = json.dumps({  # W2-173 S4: classes keyed by the misses' ids\n        \"m1\": {\"class\": \"retrieval_miss\", \"reason\": \"no gold place reached the agent\"},\n        \"m2\": {\"class\": \"retrieval_miss\", \"reason\": \"the gold span was not in the bundle\"}}) + \"\\n\"\n    w.stub({\"session\": \"write\", \"out\": {\"out/result.json\": json.dumps({\"misses\": {\"retrieval_miss\": 2}}),\n                                        \"out/classes.json\": classes_text}})\n    rc, counts, _ = w.launch(\"auditor\", audit=\"e0\")\n    assert rc == 0, counts\n    assert w.calls()[1][\"input\"] == [\"misses.jsonl\", \"selection.json\", \"set\"]\n    assert (w.sets / \"runs\" / \"e0\" / \"miss-classes.json\").read_text() == classes_text\n",
      "tokens": 286
    },
    {
      "id": "dcf0b4960076383e15e53b67",
      "path": "tests/unit/orchestration/test_w2_173_indep_launch.py",
      "text": "def plant_audit(w, ids=MISS_IDS):\n    w.plant_set()\n    folder = w.sets / \"runs\" / \"e0\"\n    folder.mkdir(parents=True, exist_ok=True)\n    (folder / \"misses.jsonl\").write_text(\"\".join(json.dumps(\n        {\"id\": i, \"question\": \"planted\", \"gold_answer\": \"x\", \"gold_sources\": [], \"answer\": \"y\", \"outcome\": \"wrong\",\n         \"evidence_in_bundle\": False}) + \"\\n\" for i in ids))\n    return folder\n",
      "tokens": 98
    },
    {
      "id": "508d5460112c0cb3e9f4c44f",
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "text": "## 5. How you classify\nTake each line of `input/misses.jsonl`. Decide in this order, and stop at the first that holds. Judge at `PIN`, from\nthe repository.\n1. **`gold_wrong`:** the gold answer or one of its governing sources is not right at `PIN` (a replaced decision, a\n   wrong span, a changed value, a claim that no source states). Test it as the checker would (R1 and R6 of the audit\n   rubric: the governing source is the highest current record, or the code).\n2. **`question_ambiguous`:** a working agent could read the question in two ways that lead to different answers, or it\n   presupposes something false at `PIN`.\n3. **`out_of_scope`:** the answer is not in any file that memory indexes (read `governance/project/path-map.yaml`), or\n   the question needs something no file holds (a running system's state, a result not yet produced).\n4. **`retrieval_miss`:** none of the above, and `evidence_in_bundle` is `false`: memory did not put a gold place in\n   front of the agent.\n5. **`answer_wrong`:** none of the above, and `evidence_in_bundle` is `true`: memory did put it in front of the\n   agent, and the agent still answered wrongly, incompletely or \"not found\".\n\n",
      "tokens": 294
    },
    {
      "id": "86dc28814bde75e1264050d2",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md",
      "text": "### 3.2 What each brief hands back (counts only reach the CTO)\n- The launch script returns `counts.json` per run: the checker's three verdict counts, the writer's counts by kind and\n  area, the auditor's five class counts. Question text, answers and paths never leave the sets root.\n- The auditor's input `misses.jsonl` carries one fact about the search: `evidence_in_bundle`, yes or no, from the\n  measure. It decides only \"memory did not find it\" against \"memory found it and the agent answered wrongly\". It shows\n  no rank, bundle or search result.\n\n",
      "tokens": 139
    },
    {
      "id": "a295b09ebd6e192e292c6f52",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "text": "## 5. How you classify\nTake each line of `input/misses.jsonl`. Decide in this order, and stop at the first that holds. Judge at `PIN`, from\nthe repository.\n1. **`gold_wrong`:** the gold answer or one of its governing sources is not right at `PIN` (a replaced decision, a\n   wrong span, a changed value, a claim that no source states). Test it as the checker would (R1 and R6 of the audit\n   rubric: the governing source is the highest current record, or the code).\n2. **`question_ambiguous`:** a working agent could read the question in two ways that lead to different answers, or it\n   presupposes something false at `PIN`.\n3. **`out_of_scope`:** the answer is not in any file that memory indexes (read `governance/project/path-map.yaml`), or\n   the question needs something no file holds (a running system's state, a result not yet produced).\n4. **`retrieval_miss`:** none of the above, and `evidence_in_bundle` is `false`: memory did not put a gold place in\n   front of the agent.\n5. **`answer_wrong`:** none of the above, and `evidence_in_bundle` is `true`: memory did put it in front of the\n   agent, and the agent still answered wrongly, incompletely or \"not found\".\n\n",
      "tokens": 294
    },
    {
      "id": "4c6a7c3f89a63d297c7a5708",
      "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md",
      "text": "**DEC-1083 (2), 2026-11-06 (word for word):** \"K9's memory bar: 85 % hit@5 on the fresh 80, used once, on the pin that\ncarries W2-92, W2-32's S11, W2-131 and the reranker chosen at the decision point. 95 % stays the target. If the bar is\nmissed, S9's options come to the owner.\" D9-FATES \u00a73 item 1 added: \"its home: a line under W2-32's S9, so the bar sits\ninside W2-27's dependencies.\"\n\n**DEC-1097 (1)(d), 2026-11-08 (word for word):** \"**the K9 bar:** right end to end at least 85 % with wrong claims at\nmost 5 %, target 95 %, hit@5 reported beside it (on 79: at least 68 right, at most 3 wrong claims, FRESH-80-1 \u00a74.3)\".\n(1)(a): the configuration judged is window 4's pin `pin-bcea09060ebc`, the pool on, today's 6,000-token bundle, search\nagain once.\n\n**DEC-1098 (1), 2026-11-09:** \"The fresh 80 accepted; K9's memory line is met (FRESH-80-RESULT: right end to end 78 of\n79, wrong claims 0).\" **DEC-1126 (6), 2026-11-11:** W2-32 and W2-15a stay open at the lift; S9 gets \"a disposition in\nline with DEC-1097, whose end-to-end bar ... replaced the hit@5 bar of DEC-1083 (2).\"\n\nTwo things the records show that the ticket does not:\n",
      "tokens": 284
    },
    {
      "id": "2b50c057bcb277f5fe5e4b1f",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "4. **The writers:** sessions outside the system opened by the owner's operator (recommended), or the ticket's\n   independent test designer as the ticket says today?\n5. **W2-88's scope:** add the set tools and the practice record to its `allowed_paths` (recommended), or file a new\n   ticket for the set tools?\n6. **The nonexistent-id row (\u00a75):** file it as its own ticket now? *Recommended: yes*, before the first adoption.\n\n**Basis (DEC-1052's five tests):** (1) memory: every adopted repository is judged by what its agents answer, on a set\nused once; (2) without S13 and S16 a verdict could fail open (a set read, run twice, or used to choose); (3) the costly\nsteps run once per repository at Wave 0, and the refresh runs only on a merge; (4) no new approval beyond the\ndeclaration and the guard ACT; (5) the standard is already proven in use here, on the 138 and the fresh 80.\n\n**Sources read:** `.tickets/DAEO-2bdu.md` (W2-88), `DAEO-qskx.md` (W2-142), `DAEO-t8mp.md` (W2-128's line);\n`docs/research/W2-88-memory-practice.md`; LIFT-1's FRESH-80-RESULT, FRESH-80-1, E0-RESULT, E2-RESULT, E3-RESULT,\n",
      "tokens": 276
    },
    {
      "id": "5d38bb43fff7b55fe35ee1eb",
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "text": "### The D-steps, as they stand (replaces the status table's rows for D-4b, D-5, D-6, D-9, D-10, D-11)\n| step | state now | evidence |\n|---|---|---|\n| D-0 to D-3 | **done** (as the table below) | DEC-1053 `d855e41a`; `ACT-REPIN-W2.md`; `ACT-G14.md` `4edd196c`; DEC-1057 `2e5c9cd9` |\n| D-4 the suite cut | **done** | DEC-1061, merged `6008a41f` |\n| D-4b the memory stage | **done**: every experiment; **the fresh 80 PASSED, 78 of 79 right end to end (98.7 %), 0 wrong claims**, K9's memory line met (11-08); the owner decided FRESH-80-1, M3-ADOPTION-1 (keep the 0.6B), G3 and GLOSSARY-1 in DEC-1097 (11-08); W2-136, 137, 138 merged (live at the re-pin). **Still due:** GLOSSARY-1's redesign and its retest on the 138 (DEC-1097 (6) (b); `gov glossary`, W2-143 and W2-144, only if it helps; neither ticket is filed); a GPU measure, so no commit on integrate during it | `LIFT-1/FRESH-80-RESULT.md`; DEC-1097; `W2-88-STANDARD-1.md` (decided in DEC-1098 (1)); DECIDED-NOT-DONE row 17 |\n",
      "tokens": 245
    },
    {
      "id": "c5c9c504e9c46a6970c30566",
      "path": "docs/changes/W2-32-evidence.md",
      "text": "| **S9** K9's memory line (DEC-1083 (2), re-worded by DEC-1097 (1)(d), DEC-1129 (1)): right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5 reported beside it | The CTO's record. **Outcome:** the fresh 80, judged once on window 4's pin (`pin-bcea09060ebc`, commit `c00d525f`, the pool on, today's 6,000-token bundle, search again once), gave **78 of 79 right end to end (98.7 %), 0 wrong claims (0.0 %), hit@5 67 of 79 (84.8 %)**: the bar (at least 68 right, at most 3 wrong claims) is **met** and the 95 % target (at least 76) **reached**. The stricter of the two grades gives 77 right and 1 wrong claim, still a pass. Recorded in `governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md` (\"The verdict\" and its table; declared in `FRESH-80-DECLARATION.md`, `16d3d61b`), accepted by DEC-1098 (1) (\"K9's memory line is met\"), and owned as S9's disposition by DEC-1129 (1) (option (a1) of `governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md`). **The improvement rounds that ran** (the earlier note here, \"no improvement round has run yet\", was written on 2026-11-03 and is replaced): S7 (G1, round 1: the models read the whole chunk; row S7 above; commits `232b21cd` to `b7085897`), S8 (G3, round 2: routing by question type and the phrasings; row S8 above; commits `7320a3dd`, `6d4b45b9`, `3ea1c8c3`), S11 (the candidate pool, v456: row S11 above; on the tuning sets 67 of 79 with the halves' gap 15.6 to 0.4 points, `packages/LIFT-1/D4B-MORNING-2026-11-05.md` \u00a71) and the five index-time methods of DEC-1068, M1 to M5 (rows above; measured in the same morning record, M1 adopted alone and then overtaken by v456, M2 to M5 not adopted). S6 was dropped (DEC-1083 (3)). **The baseline, not the 80:** D-4b measure 1, hit@5 28 of 48 (58.3 %) on the 48 dev questions on 2026-11-03, before any round, is the baseline F1 is judged against (records in `~/gov-os-runs/D4B/m1/records/`, the pinned run excluded, in `pinned/`); it is not the fresh 80's level. **Left open:** the 80 was judged at window 4's pin, not today's (`pin-797495bdfc70`); a later fall below 85 % is brought to the owner by the memory audit (DEC-1101 (1), DEC-1125 (2)), whose first run on 11-23 measures today's pin; the 80 is spent and not measured again. | accept | accept at `9f53a61d`: success-9, 6 passed, 1 failed (`test_w2_32_record.py::test_the_evidence_file_states_s9s_and_f1s_outcome`, before this row was written). accept at `3a27107d`: success-9 **pass**, 8 passed (S9 as it stood before DEC-1129 (1)). **After DEC-1129 (1):** S9's cases are revised to the end-to-end figure by an independent test designer and `gov accept W2-32` is run again, scoped; its result is added here by the CTO | this file |\n",
      "tokens": 683
    },
    {
      "id": "DAEO-0pyc",
      "path": ".tickets/DAEO-0pyc.md",
      "text": "  - 'S9 K9''s memory line (DEC-1083 (2), re-worded by DEC-1097 (1)(d)): on the verdict set, judged once on the declared configuration, right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5 reported beside it. Judged on the fresh 80 at window 4''s pin: 78 of 79 right (98.7 %), 0 wrong claims, hit@5 67 of 79 (84.8 %) [FRESH-80-RESULT, DEC-1098 (1)]. A later fall below 85 % is brought to the owner by the memory audit (DEC-1101 (1), DEC-1125 (2)), whose first run on 11-23 measures today''s pin. Verify: the S9 cases of tests/acceptance/W2-32/, re-pointed to the end-to-end figure by an independent test designer (Rewrite-Reason: DEC-1129 (1); DEC-1126 (6) asked for the disposition), and the evidence note''s S9 row in docs/changes/W2-32-evidence.md, which records FRESH-80-RESULT''s figures (78 of 79 right, 0 wrong claims, hit@5 67 of 79) [re-worded, DEC-1129 (1)]'\n",
      "tokens": 224
    },
    {
      "id": "9af8de622102d16905be219f",
      "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md",
      "text": "### Option (a1), apply now: S9 re-worded to DEC-1097's bar, met on the fresh 80's recorded result. RECOMMENDED\n- **New S9 line:** \"S9 K9's memory line (DEC-1083 (2), re-worded by DEC-1097 (1)(d)): on the verdict set, judged once on\n  the declared configuration, right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5\n  reported beside it. Judged on the fresh 80 at window 4's pin: 78 of 79 right (98.7 %), 0 wrong claims, hit@5 67 of\n  79 (84.8 %) [FRESH-80-RESULT, DEC-1098 (1)]. A later fall below 85 % is brought to the owner by the memory audit\n  (DEC-1101 (1), DEC-1125 (2)), whose first run on 11-23 measures today's pin [re-worded, DEC-1126 (6)]\". The old\n  escalation sentence (below 85 % after two rounds; 85 to 95 % with room) is kept as the audit's rule, not repeated.\n- **Also:** the title's \"the hit@5 85 row\" changed to \"the memory line\"; the evidence note's S9 row rewritten with\n  the 80's figures; `w2_32_record.py`'s `s9_state` and its cases re-pointed to the end-to-end figure by an\n  independent test designer (`Rewrite-Reason: DEC-1126 (6)`), with the README's S9 row.\n",
      "tokens": 279
    },
    {
      "id": "c4f6740b84ea640d2c14ecbc",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "## 1. The standard, in one paragraph\nGov OS's memory standard is the configuration that the fresh 80 judged once. It has four parts: the\n**Qwen3-Reranker-0.6B**, served by the machine's one shared reranker service; **the pool on** (the `pool:` block in\n`governance/project/retrieval.yaml`); **today's 6,000-token bundle**, with its items widened to their sections; and\n**agents searching again once** when the first bundle does not answer. On the fresh 80, used once on 2026-11-08 at\nwindow 4's commit `c00d525f`, an agent reading its bundles was **right end to end on 78 of 79 (98.7 %; exact 95 %\ninterval 93.1 to 100), with 0 wrong claims**. That beats K9's bar (at least 68 right, at most 3 wrong claims) and\nreaches the 95 % target (FRESH-80-RESULT). On the 138 tuning questions the same configuration gave **128 of 138\n(92.8 %)** (E2). hit@5 was 84.8 % on the 80 and 76.8 % on the 138, which is why the bar judges what agents answer and\nreports rank beside it (DEC-1097 (1)(d)). Under DEC-1098 (1) every adopted repository builds this standard at its\nWave 0, as W2-88's practice record describes, and proves it there: first on its own tuning set, then on a fresh\nverdict set measured once.\n\n",
      "tokens": 299
    },
    {
      "id": "0ae9dba062e2ab846b2472c8",
      "path": "tests/acceptance/W2-32/test_w2_32_record.py",
      "text": "\"\"\"S9 and F1, judged on the record (README, \"What the record judges\").\n\n- S9 (re-worded by DEC-1097 (1)(d), DEC-1129 (1); ``Rewrite-Reason: DEC-1129 (1)``): K9's memory line, judged once on\n  the declared configuration, by the figure right end to end (at least 85 %, target 95 %) and the wrong claims (at\n  most 5 %); below the bar, the memory audit brings it to the owner; hit@5 is reported beside, never judged. Judged\n  on the fresh 80: 78 of 79 right, 0 wrong claims, hit@5 67 of 79 [FRESH-80-RESULT, DEC-1098 (1)].\n- F1: an improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.\n\nNeither is behaviour of W2-32's code. These cases check what a test can: the baseline record holds both figures\nagainst their bars, over repeated runs that give a noise band; the rules as ``w2_32_record`` states them; and the\nticket's evidence file states S9's and F1's outcome. The verdict on the rounds is the reviewer's, with\n``w2_32_record.py`` run on the CTO's records.\n\nThe records are read from ``W2_32_RUNS`` (default ``~/gov-os-runs/D4B``), measure 1 under ``m1/records``. Only the\n",
      "tokens": 278
    },
    {
      "id": "DAEO-f6x3",
      "path": ".tickets/DAEO-f6x3.md",
      "text": "# W2-146 The id reader reads every declared id form\n\nThe owner's DEC-1099 (2) answer (6): the nonexistent-id row filed as its own ticket now, before the first adoption.\n\n- **The defect:** the product's id reader (`gov.retrieval.lexical.ids_in`) reads only tokens of its one built-in\n  shape (`ID_SHAPE`: a capital letter, then at least one hyphen and a part, with a digit somewhere). A repository\n  whose ids take another form (no hyphen, lower case, an underscore, a space) names ids that the reader does not read\n  as ids, so `gov retrieve`'s stop (`_nowhere` in `src/gov/retrieve/command.py`) never sees them, and DEC-1071 (5)'s\n  `UNRESOLVED_IDS` cannot fire for a question naming a nonexistent id in such a form. Found at the fresh 80's\n  pre-flight (`governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md`, \"What follows\"); an adopted\n  repository will have more such forms (W2-88-STANDARD-1 \u00a75).\n- **The fix (W2-88-STANDARD-1 \u00a75):** the id forms read from the path map, beside the built-in shape. The forms used\n  by this repository's own records need no declaration; whether this repository's path map declares any form is the\n  CTO's record change, not this ticket's.\n",
      "tokens": 298
    },
    {
      "id": "bcab0b8ac642b8a816e7e1c5",
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "text": "| 14 | the label audit | (13) at each release cut and before any new verdict set; rubric v3 after the 80 | **DONE (trigger set)**; rubric v3 **DUE NOW** (after the 80) |\n| 15 | the embedder trial | (14) a Wave 3 row | **DONE (parked)**: row to add with the Wave 3 list |\n| 16 | the old window scripts (F1) | (15) fixed or retired, never reused | **DONE 11-08**: `live_window.sh`, `score_once_window.sh` and `extend_window.sh` (same defect) moved to `drafts/score-once/retired/` with a README (scratch, untracked) |\n| 17 | GLOSSARY-1 | (6) (b): redesign beside the agent's words, toward decisions, for asking; retest on the 138 after the 80; build only if it helps | **DECIDED 11-08**; **DUE NOW** (after the 80): the redesign and its declaration, then the retest on the 138 |\n| 18 | the fresh-80 path | (1): the scripts, the checker's pass (operator), the readiness review, the pre-flight, the control, the 80 | **DONE 11-08 21:46**: K9's bar PASSES, right end to end 78/79 (98.7 %), wrong claims 0 (`FRESH-80-RESULT.md`); every data condition run, all below the judged one; spent $109.05 |\n",
      "tokens": 273
    },
    {
      "id": "6f1e4ddfed30a78aeb0e868b",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md",
      "text": "  schemas), so this package supplies them. The old operator folders `~/gov-os-writer` and `~/gov-os-checker` stay as they\n  are until the default (ACT-INDEP-WALLS-1 \u00a77 item 3).\n- **The measure is a set of one-off tools.** `gov.retrieval.measure` (W2-61) gives hit@5 and full evidence and is a\n  product module. The end-to-end run that judged the fresh 80 (reader, graders, the fault rule, the figures) lives\n  in the CTO's scratch (`drafts/fresh80/`) and is pinned to one set name; it cost $12.46 and 8.2 minutes for 80\n  questions (FRESH-80-RESULT, M). **Nothing yet turns a delivered set into a measured audit.** That is W2-170 and W2-171.\n- **The schedule is not in the crontab.** The crontab holds the dispatcher (every minute) and the operator agent's launch\n  (every 10 minutes, 00:00 to 00:59 and 08:00 to 23:59). The nightly's four lines are commented out by DEC-1049 and\n  DEC-1050; when they come back, the nightly runs 04:00 to 08:00 and its check to 09:00 (DEC-973).\n- **Adopted repositories:** W2-88 (`DAEO-2bdu`) has the first practice (S12 to S17: a tuning set of about 80, a verdict\n",
      "tokens": 275
    },
    {
      "id": "98f9649bc6d789be2073b214",
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "text": "| saving if Bash outputs > 10k chars were cut to 4k (E; head/tail, quiet flags) | $7.8 (189 outputs) | $12.9 (158) | $0.1 |\n- **Total:** tool results are \u2248 20 % of transcript spend ($259 of $1,276, E). Searching instead of reading would save \u2248\n  $11-26 (0.4-0.9 pt). Capping Bash outputs would save \u2248 $21 (0.8 pt). Both overlap with A (fresh sessions at 200k),\n  which shortens every re-read (E).\n- **Risk:** one search answers 91.1 %, and searching again once answers 98.7 % (M, FRESH-80-RESULT.md). A full read misses\n  nothing in the file. Smaller bundles answered worse (top 5: 56 of 79, with 5 wrong claims). Engineers must Read a file\n  before they Edit it, and reviewers must see the whole diff. Searching saves only on files much larger than the bundle.\n- **Where it fits:** orientation questions that span many documents (\"which decision says X\"), for helpers, leads and the\n  CTO. It does not fit an engineer's, reviewer's or auditor's reading of the files they judge.\n\n",
      "tokens": 245
    },
    {
      "id": "c0470b0eeb417debbda875a7",
      "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md",
      "text": "## 8 Method and gaps\n- **Read:** the register (DEC-066, 460, 839, 957, 1118), DECISIONS-IN-FORCE, tickets W2-11, 21, 33, 60a, 60b, 104, 149,\n  153 and W1-33, 46. Also the role files, launch_worker.sh, src/gov/launch, dispatch/, the resources gate,\n  opcommon.py/operator_launch.py, class-rules.yaml, ~/.claude/settings.json (model and effort keys only), USAGE-1 \u00a71, 2,\n  5, 6, 8, FRESH-80-RESULT.md, lens F \u00a7CAP-35.\n- **Scripts (`python3 -I` here):** `agg_sessions.py` (spend by kind, model, effort; agent types); `helpers_by_type.py`;\n  `scan_tools.py` and `context_cost.py` (tool metadata; `REPL=<chars>` sets the bundle size); `agent_calls_since.py`.\n  They reuse USAGE-1's calls.jsonl and sessions.json, and open only the transcripts listed there.\n- **What was read in transcripts:** tool names; whether Read had offset or limit keys; the Agent call's subagent_type,\n  model and effort; a yes/no for `gov retrieve` in a Bash command; result lengths; path hashes; model, effort and\n  timestamps. No message text was printed or kept.\n- **Source:** model and effort precedence, code.claude.com/docs/en/sub-agents (fetched 2026-11-10; not tested on 2.1.318).\n",
      "tokens": 290
    },
    {
      "id": "f50a2344cd25767dc5f90152",
      "path": "governance/project/orchestration/packages/USAGE-1.md",
      "text": "## 2 By source\n| source | model | calls | output | cache read | cache write | $ list | pt | basis |\n|---|---|---|---|---|---|---|---|---|\n| CTO session (ad44f5fe) | opus-5-5 | 630 | 0.52 M | 310.4 M | 4.65 M | 109.69 | 4.0 | M transcript |\n| CTO helpers (44 transcripts, 3 of them nested) | opus-5-5 | 5,110 | 4.62 M | 1,280.0 M | 23.4 M | 465.53 | 16.9 | M subagents/*.jsonl |\n| Launched workers (190 transcripts, 73 worktree folders) | opus-5-5 | 8,741 | 10.23 M | 1,270.9 M | 28.5 M | 685.99 | 24.9 | M transcripts; own results agree (below) |\n| Experiments: fresh 80 + its data runs (11-08 19:32-21:46) | opus reader/grader, sonnet checker | n/a | n/a | n/a | n/a | 109.05 | 4.0 | M FRESH-80-RESULT.md (cost only; `--no-session-persistence`) |\n| Experiments: the independent writer's session | opus-5-5 | 1 | 7 | 0.03 M | 0.40 M | 3.24 | 0.1 | M (counts only) |\n| Rehearsals in ~/gov-os-runs (6 result JSONs) | sonnet/haiku | 6 | | | | 0.06 | 0.0 | M result JSONs |\n| Sentinel (b6a01869) | haiku-5-5 | 122 | 14.6 k | 12.2 M | 2.49 M | 3.14 | 0.11 | M transcript |\n| Dead-man pushes (2 runs, cwd /tmp) | haiku-5-5 | 6 | 1.0 k | 0.12 M | 0.03 M | 0.01 | 0.0 | M transcripts |\n",
      "tokens": 295
    },
    {
      "id": "83dd17fa152c21f33a295de0",
      "path": "governance/project/orchestration/packages/USAGE-RUBRIC-2.md",
      "text": "## 6 Confidence, figure by figure, and what could not be measured\n| figure | M/E | why |\n|---|---|---|\n| $1,497 transcripts + $109 fresh 80; 60 % at 16:00 | M | calls.jsonl by message id; FRESH-80-RESULT cost; usage.txt. Model $1,606 vs meter $1,650: $44 unattributed |\n| $27.5 a point | M | fit of 95 readings; moves 0.7 % with today's data |\n| spend by role | M ($), E (tags) | roles and classes are my reading of names and subjects |\n| re-priced saving at same tokens | M arithmetic on E premise | prices fetched by USAGE-1 |\n| the +30 % band | E | **no measured Sonnet-to-Opus token ratio exists**: USAGE-1, MODEL-TIERS-1, FRESH-80-RESULT have none; the only Sonnet helpers (ACT-EFFORT-HIGH-1 and ACT-PATHMAP-NS-2 preparers, 38 and 34 calls, $0.93 and $0.69) are two small jobs with no Opus twin |\n| effort max to high | E | thinking share only; fewer tokens may mean more rounds |\n| points | E | needs the meter weight above |\n| projection | E | linear pace; the 1.09-2.31 spread is the real uncertainty, larger than the saving |\nCould not be measured: the Sonnet token ratio (baseline for a later check, M, per session median: C2 designer 31 calls, $1.85;\n",
      "tokens": 291
    },
    {
      "id": "653e7af5049a8b705a09f033",
      "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md",
      "text": "## 2. Does the 80's recorded result meet DEC-1097's bar? Yes.\n\n| figure | bar (DEC-1097 (1)(d), on 79) | fresh 80 | recorded in |\n|---|---|---|---|\n| right end to end, search again once (A2) | at least 85 % (68), target 95 % (76) | **78 of 79 (98.7 %)** | FRESH-80-RESULT.md, \"The verdict\"; DEC-1098 (1); DECIDED-NOT-DONE row 18 |\n| wrong claims | at most 5 % (3) | **0 of 79** | same |\n| stricter of the two grades | (data) | 77 right, 1 wrong claim: still passes | FRESH-80-RESULT.md |\n| hit@5, reported beside | no bar | 67 of 79 (84.8 %) | FRESH-80-RESULT.md, table |\n| the 138 (data, not the verdict) | | right end to end 128 (92.8 %); hit@5 106 (76.8 %) | same table |\n\nThree cautions, so the owner sees them:\n1. **The 80 was judged at window 4's pin** (`pin-bcea09060ebc`, commit `c00d525f`). Today's pin is\n   `pin-797495bdfc70` (window 5). Retrieval changed since: W2-137 and W2-138 (store commit in results, line-hash\n   check), W2-136 and W2-145 (reranker cap and no private reranker). DEC-1083 (2) asked for the bar on the pin that\n   carries the listed items, and it was met on that pin. The first memory audit (Monday 11-23, 21:00, DEC-1125 (2),\n",
      "tokens": 290
    },
    {
      "id": "e54be0ac9c862eafb9f99c01",
      "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md",
      "text": "## 0. The short answer\n\n- **A correction first.** The \"58.3 %\" that LIFT-CLOSES-1 gives for W2-32 is **not** the fresh 80's figure. It is\n  D-4b measure 1, the baseline on the 48 dev questions on 2026-11-03, 28 of 48, before any improvement round\n  (`packages/LIFT-1/D4B-GAPS.md` line 13; `docs/changes/W2-32-evidence.md`, S9 row). The fresh 80 gave **hit@5 67 of 79\n  (84.8 %)** and **right end to end 78 of 79 (98.7 %), wrong claims 0** (`packages/LIFT-1/FRESH-80-RESULT.md`).\n- Under DEC-1097's bar the fresh 80 **passes, and reaches the 95 % target.** DEC-1098 (1) already says so: \"K9's memory\n  line is met\". So S9's trigger (a miss) never fired, and the owner is not being asked to accept a low level.\n- What is wrong is **the record**: S9's words, the evidence note's S9 row, three packages and the W2-32 acceptance\n  rule still speak of hit@5 at 85 % and of 58.3 %.\n- **Recommendation: option (a1) below** (re-word S9 to DEC-1097's end-to-end bar, met on the fresh 80's recorded\n  result, with the 11-23 audit named as the check on today's pin). Confidence: **high** that S9 should now say\n",
      "tokens": 275
    },
    {
      "id": "e247d1b9814aaa36fc18064e",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "## 5. Risks, and what stays open\n- **The glossary (DEC-1097 (6), (b)):** not in the standard. Its redesign is retested on the 138 after the 80. If the\n  retest helps, W2-88's glossary line (GLOSSARY-1 \u00a75.3) comes back as its own package. It is **not** added here.\n- **G1's fewer scored pairs (DEC-1097 (10)):** brought as an option after the lift. If adopted, ranking changes, so\n  the standard changes by that decision: the 138 are re-measured (DEC-1097 (4)), S10's settings follow it, and every\n  verdict names its pin. An adopted repository judged on the old pin keeps its verdict. Its next verdict needs a new\n  fresh set.\n- **The nonexistent-id stop (product row):** the product reads only the id forms it knows (lexical `ids_in`). On the\n  fresh 80, `UNRESOLVED_IDS` could not fire on that question's form (FRESH-80-RESULT), and an adopted repository will\n  have more forms the product does not read (JIRA keys, RFC numbers). Until the row is fixed, S12 and S14 score that\n  question on the reader's \"not found\", apart from the bar, and record the stop as \"not applicable\". The row needs a\n  ticket: id forms read from the path map. That is not W2-88's work.\n",
      "tokens": 292
    },
    {
      "id": "780ca4ad280313b0aa3cee91",
      "path": "governance/project/orchestration/reviews/W2-32-S9-review.md",
      "text": "    | `<=` at the 95 % target | 1 |\n    | no \"under target\" state | 11 |\n    | hit@5 judged as well | 6 |\n    | hit@5 judged instead of end to end | 6 |\n    | bar set to 80 | 2 |\n    | wrong-claim limit set to 10 | 2 |\n    | percentages taken over 48 instead of 79 | 6 |\n\n  - **Evidence-row case, run against changed copies of the evidence file:**\n    - The 91535d990 row (before the re-wording) fails.\n    - Without FRESH-80-RESULT it fails.\n    - With 70 of 79 / 88.6 % it fails.\n    - With 2 wrong claims it fails.\n    - With no hit@5 it fails.\n    - With **hit@5 28 of 79 it passes** (finding F-1).\n    - The original file passes.\n  - **KPI map:** `parse_map` gives keys success-1..5, 7..11 and failure-1. success-9 has 5 items and failure-1 has 3; `names_a_test` is True for each, and all 7 test functions collect.\n",
      "tokens": 205
    },
    {
      "id": "8f2447128af455a729e68f99",
      "path": "governance/project/orchestration/reviews/W2-32-S9-review.md",
      "text": "- Fix: require `hit@5 67 of 79|84\\.8 ?%`.\n- What would reverse it: an owner ruling that the reported figure only has to be present, not that particular value.\n\n**F-2. S9, blocking: no.** The evidence case checks its four conditions (end-to-end figure, wrong claims, hit@5, FRESH-80-RESULT) separately, each across every line that mentions S9. They do not have to be on S9's own row, so the figures could come from different lines, such as the `gov accept` summary lines that name S9.\n- Ordinary work: no, because the S9 row would have to lose its figures while another line naming S9 carried each one.\n- Consequence: other.\n- Fix: select the table row that begins `| **S9**` and check all four on that row.\n- What would reverse it: a planted split where the case still fails.\n\n**F-3. S9, blocking: no.** `test_the_baseline_record_holds_both_figures_against_their_bars` stays mapped under S9. It checks the 48-set baseline record's form, including the hit@5 field `floor: 85`, which the re-worded S9 line does not name. The README notes \"reported, not S9's judgement\".\n- Ordinary work: yes, because a change in the baseline record's form would turn S9 red.\n",
      "tokens": 289
    },
    {
      "id": "ef7797362979ff8c27cd8f7c",
      "path": "governance/project/orchestration/reviews/W2-32-S9-review.md",
      "text": "- **task:** DAEO-0pyc (W2-32). Independent review, round 1, of S9's re-pointed cases and of F1 being unchanged (DEC-1129 (1), DEC-1131).\n- **status:** done. Verdict READY.\n- **work_completed:** I made the five checks in the brief.\n  1. The commit `669707a76` changes only the three files the brief names. It carries `Rewrite-Reason: DEC-1129 (1)` and `Task: DAEO-0pyc`.\n  2. The S9 cases test the line's own words, and every wrong `s9_state` I planted turns them red.\n  3. The evidence-row case reads `docs/changes/W2-32-evidence.md` and holds the 80's judged figures and FRESH-80-RESULT.\n  4. F1's code and cases are unchanged.\n  5. The README's KPI map parses with `gov.accept.runner.parse_map`, and every item names a test that collects.\n- **files_changed:** none in the repository. My only scratch was a copy under `$TMPDIR/rev`.\n- **evidence:**\n  - **Changed files:** `git diff --stat 1a3669e6a 669707a76` lists only `tests/acceptance/W2-32/README.md`, `test_w2_32_record.py` and `w2_32_record.py`.\n",
      "tokens": 251
    },
    {
      "id": "1ed3f045a437ce57a41a3e63",
      "path": "tests/acceptance/W2-32/README.md",
      "text": "  wrong claims at most 5 % and under 95 % is \"met, under target\"; 95 % or above is \"met\". On the fresh 80's 79\n  questions the bar is 68 right with at most 3 wrong claims, the target 76 right. The record for S9 is the ticket's\n  evidence file (`docs/changes/W2-32-evidence.md`, S9's row): 78 of 79 right end to end (98.7 %), 0 wrong claims,\n  hit@5 67 of 79 (84.8 %), naming `FRESH-80-RESULT`; the cases read that row and the stated figures, no record\n  outside it. **F1 is unchanged:** an improvement is reverted when a count falls below the baseline's noise band. The\n  CTO's measure records (`~/gov-os-runs/D4B/`, measure 1 under `m1/records`, read through `W2_32_RUNS`) give the\n  band, and `w2_32_record.py` states the F1 rule as code; the reviewer runs it on the records:\n\n      python3 tests/acceptance/W2-32/w2_32_record.py ~/gov-os-runs/D4B/m1/records <round record.json> ...\n\n  It prints each figure's noise band over the baseline's runs, then per round F1's verdict (`revert` when a count is\n  below the band's lowest), hit@5 (reported) and S9's state (judged on a record's `total.end_to_end`: `count` right,\n",
      "tokens": 280
    },
    {
      "id": "992395672ea4fd0289b6364a",
      "path": "tests/acceptance/W2-32/README.md",
      "text": "| S9 | K9's memory line, judged once on the verdict set: right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5 reported beside it; the fresh 80 gives 78 of 79 right, 0 wrong claims, hit@5 67 of 79 [DEC-1083 (2), DEC-1097 (1)(d), DEC-1129 (1)] | `test_w2_32_record.py::test_the_baseline_record_holds_both_figures_against_their_bars` (the 48-set baseline's form, the base of F1's band; its hit@5 figures are reported, not S9's judgement); `test_w2_32_record.py::test_s9_is_met_at_85_end_to_end_with_wrong_claims_at_most_5_and_at_target_from_95` (6 cases, the rule on percentages); `test_w2_32_record.py::test_s9_on_79_questions_68_right_and_3_wrong_is_the_bar_and_76_the_target` (6 cases, the rule on counts of 79); `test_w2_32_record.py::test_s9_reports_hit_at_5_beside_the_end_to_end_figure_and_never_judges_it` (3 cases); `test_w2_32_record.py::test_the_evidence_file_states_s9s_and_f1s_outcome` (the evidence row: 78 of 79 end to end, 0 wrong claims, hit@5 beside it, FRESH-80-RESULT; the verdict is judged by the record, below) |\n",
      "tokens": 265
    },
    {
      "id": "bbd2211f3c23f7d2d877a9bd",
      "path": "tests/acceptance/W2-32/test_w2_32_record.py",
      "text": "def test_the_evidence_file_states_s9s_and_f1s_outcome():\n    assert EVIDENCE.is_file(), f\"no evidence file at {EVIDENCE.relative_to(s.ROOT)} (D4B-MEMORY-STAGE: one row per \" \\\n                               f\"KPI line, how it is verified, the command and the result)\"\n    lines = EVIDENCE.read_text(encoding=\"utf-8\").splitlines()\n    s9 = [line for line in lines if re.search(r\"\\bS9\\b\", line)]\n    f1 = [line for line in lines if re.search(r\"\\bF1\\b\", line)]\n    assert any(re.search(r\"\\b78 of 79\\b|\\b98\\.7 ?%\", line) and re.search(r\"end[ -]to[ -]end\", line, re.I) for line in s9), \\\n        \"S9's row gives the end-to-end figure of the fresh 80 (78 of 79, or 98.7 %), named end to end\"\n    assert any(re.search(r\"\\b0 wrong claims?\\b|wrong claims?:? 0\\b\", line) for line in s9), \\\n        \"S9's row gives the wrong claims (0)\"\n    assert any(re.search(r\"hit@5\\s+(\\d+ of 79|\\d+(\\.\\d+)? ?%)\", line) for line in s9), \\\n        \"S9's row gives hit@5 beside the end-to-end figure (n of 79, or a percentage)\"\n    assert any(\"FRESH-80-RESULT\" in line for line in s9), \"S9's row names FRESH-80-RESULT\"\n",
      "tokens": 274
    },
    {
      "id": "f536f043dc3eb65b557d7e98",
      "path": "tests/acceptance/W2-32/test_w2_32_record.py",
      "text": "\n\n# Rewrite-Reason: DEC-1129 (1): the evidence row carries the end-to-end figure, the wrong claims, hit@5 beside, FRESH-80-RESULT\n",
      "tokens": 33
    },
    {
      "id": "DAEO-2bdu",
      "path": ".tickets/DAEO-2bdu.md",
      "text": "  - 'S13 The fresh verdict set, used once: 80 questions, written by the same independent writer and checker under the same rubric, blind, before the first measure of the tuning set. None of its gold sources is a gold source of the tuning set. It is held outside every worktree in a folder of mode 700, declared in the path map''s evaluation_sets with every role but the orchestrator refused, and the guard refuses the measured roles a read of the set and of its run folder (as ACT-GUARD-SETS-1). It is used once, as FRESH-80-1 did. First a counts-only pre-flight: the set''s digest, how its anchors resolve at the measured commit, and whether each nonexistent id still exists nowhere. Then the checker''s staleness pass at that commit. Then a declaration, committed before any search, naming the configuration (S10), the commit, the denominator with nonexistent-id questions apart, the bar and how it rounds (S14), any data conditions as data only, and the fault rule (FRESH-80-1 \u00a73.5). Then a control on the tuning set. A USED marker is written before the first search, and the runner refuses to start once it exists. The result record gives counts only. Verify: the declaration''s commit is earlier than the USED marker; a planted USED makes the runner refuse; a planted read of the set by a measured role is refused by the guard [DEC-1098 (1), DEC-1097 (1)(b), (1)(g), DEC-1097 (2), DEC-1092 (4), DEC-1078 (3), DEC-1074 (1)] [added, DEC-1099 (2); DEC-1098 (1)]'\n",
      "tokens": 367
    },
    {
      "id": "ef2aa5c904d9736cd476303d",
      "path": "docs/research/W2-88-memory-practice.md",
      "text": "- **A glossary consulted at search-again lowers answers:** 122 against 128 (E2G, p 0.031). Keep a glossary out of the\n  search path.\n- **Most remaining misses are correct answers citing a place the label does not list** (7 of 10 at two searches):\n  strict grading understates. Report \"answer correct, citation aside\" beside the strict figure.\n- **The shared reranker's GPU is saturated** under a 20-search burst (G1): batching would not help; fewer scored pairs\n  per search would, and changes ranking (re-measure the 138 if it lands).\n- **Next:** the owner's decisions (the fresh 80's configuration and the K9 bar, M3, the glossary), then the fresh 80\n  once (`FRESH-80-1.md`, `FRESH-80-READINESS.md`).\n",
      "tokens": 176
    },
    {
      "id": "887956ade513222d86d8571a",
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "text": "### 1b. Waiting on a trigger\n\n| DEC-n (item) | What was decided | State | Next step | Trigger / when |\n|---|---|---|---|---|\n| DEC-1092 (4), DEC-1085 (7), DEC-1083 (2) | The owner decides the fresh 80's configuration and the K9 bar before the 80 runs | Package FRESH-80-1 ready. Owner holding (11-08) | Owner reads FRESH-80-READINESS and decides \u00a75's seven questions | Owner's word (held) |\n| DEC-1087 (12), DEC-1085 (3) | M3's (two-reranker) adoption decided after all the experiments | M3-ADOPTION-1 ready; keeping the 0.6B is recommended | Owner decides \u00a76 | Owner's word (held) |\n| DEC-1096 (2), (3), (5) | Glossary built and refreshed with the store, used by every agent; package beside the test | Test done (E2G: worse, 122 against 128). GLOSSARY-1 ready, parking recommended. W2-143 and W2-144 proposed, NOT filed. W2-88's line not added | Owner decides \u00a79. If built: file W2-143/144 and add W2-88's Wave-0 line | Owner's word (held) |\n",
      "tokens": 236
    },
    {
      "id": "ac01ebb7748fc7b475bc41d9",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "- **The older window scripts** `live_window.sh` and `score_once_window.sh` still carry the F1 restore defect fixed in\n  `e4_window.sh`: never reuse them unfixed.\n- **Decisions waiting:** FRESH-80-1 \u00a75 (7 questions; configuration, commit, the K9 bar), M3-ADOPTION-1 \u00a76 (keep the\n  0.6B recommended), GLOSSARY-1 \u00a79 (park recommended).\n- **ADR-0002:** refresh against the register before the lift's re-pin (DEC-1093); it belongs with \u00a75's findings.\n- **The status block counts K9 as done** from stale tags (K7-W2-REMAINDER \u00a75); a hand-kept fix is pending.\n\n",
      "tokens": 139
    },
    {
      "id": "249b917ed5a7dc6cead63101",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "  - 'S13 The fresh verdict set, used once: 80 questions, written by the same independent writer and checker under the same rubric, blind, before the first measure of the tuning set. None of its gold sources is a gold source of the tuning set. It is held outside every worktree in a folder of mode 700, declared in the path map''s evaluation_sets with every role but the orchestrator refused, and the guard refuses the measured roles a read of the set and of its run folder (as ACT-GUARD-SETS-1). It is used once, as FRESH-80-1 did. First a counts-only pre-flight: the set''s digest, how its anchors resolve at the measured commit, and whether each nonexistent id still exists nowhere. Then the checker''s staleness pass at that commit. Then a declaration, committed before any search, naming the configuration (S10), the commit, the denominator with nonexistent-id questions apart, the bar and how it rounds (S14), any data conditions as data only, and the fault rule (FRESH-80-1 \u00a73.5). Then a control on the tuning set. A USED marker is written before the first search, and the runner refuses to start once it exists. The result record gives counts only. Verify: the declaration''s commit is earlier than the USED marker; a planted USED makes the runner refuse; a planted read of the set by a measured role is refused by the guard [DEC-1098 (1), DEC-1097 (1)(b), (1)(g), DEC-1097 (2), DEC-1092 (4), DEC-1078 (3), DEC-1074 (1)] [added, DEC-1098 (1)]'\n",
      "tokens": 363
    },
    {
      "id": "ADR-0002",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "text": "## More Information\n\n- **Sources:** architecture v0.3; S0a `STACK_OPTIONS.md`, `CAPABILITY_CATALOGUE.md`; S0b2 `RESULTS.md`,\n  `GLUE_REQUIREMENTS.md`, `TOOL_REGISTRY.yaml`, `INTEGRATION_REPORT.md`; register DEC-064\u2026DEC-096, and\n  DEC-138\u2026DEC-174 for the sandbox layer, the launcher, the research role and the lesson loop; `spike-sandbox/EVIDENCE.md` (EXP-001, ADOPT-PARTIAL);\n  for Wave 2's memory, DEC-1029\u2026DEC-1097, `governance/project/tool-registry.yaml` (the `gov` entry of re-pin\n  window 4), `docs/research/W2-88-memory-practice.md`, `docs/research/W2-112-shared-reranker.md`, and\n  `governance/project/orchestration/packages/LIFT-1/` (E0 to E5, E0B, E2G, G1-PROFILE, PAT-1, BUNDLE-BUDGET-1,\n  M3-ADOPTION-1, FRESH-80-1).\n- **Revisit triggers:**\n  - a code graph above the tested envelope;\n  - vectors above ~100k (move to LanceDB, DEC-016);\n  - OpenSpec or codebase-memory-mcp breaking changes at a pin upgrade;\n  - the per-wave glue review;\n  - a reranker or embedder that makes agents answer better end to end on the 138 under a reading rule declared before\n    its figures, measured on the standing model bench (DEC-1069 (13), DEC-1097 (5));\n",
      "tokens": 288
    },
    {
      "id": "fffe27a89c0c8e199a1549ab",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md",
      "text": "- DEC-1097 (2026-11-08): **the fresh 80** judges window 4's pin, pool on, today's bundle, search again once, at\n  `c00d525f` with the visible-40 control first; every experiment on the 80 for data, only that configuration judged;\n  **K9's bar: right end to end \u2265 85 % with wrong claims \u2264 5 % (on 79: \u2265 68 right, \u2264 3 wrong), target 95 %, hit@5\n  beside it**; readers and graders read the 80; the owner's checker's staleness pass first; FRESH-80-1's twenty fixes\n  and fault rule as written; no commit, rebuild or GPU window during the run; **W2-139 and W2-140 held until after the\n  80.** ACT-GUARD-SETS-1 rebuilt (the reader folder hidden, W2-84's hidden-half cases deleted), rehearsed, applied by\n  the operator before the 80. The seven-reviewer readiness review (fix only fail-open or verdict-breaking, two rounds;\n  any retrieval change reruns E0 and E2 on the 138 first). If retrieval changes after the verdict, the 138 re-measured\n  at the release commit (W2-27 item (a)). **Keep the 0.6B** (M3, M1 for data on the 80). G3 no change before the 80.\n  **The glossary (item 6): (b)**, redesigned beside the agent's own words, ranked toward decisions, for asking,\n",
      "tokens": 291
    },
    {
      "id": "b2e74f702fb08bf4d0a755f3",
      "path": "governance/project/orchestration/packages/ACT-GUARD-SETS-1.md",
      "text": "# ACT-GUARD-SETS-1: the guard refuses the hidden sets outside the repository to the measured roles (DEC-1082 (3))\n\n- **For:** the owner, to decide the four points in \u00a75, then the owner's operator (a guard change: P-ACT-SPLIT).\n- **By:** the CTO, 2026-11-06. A read-only design, built and rehearsed in a clone by an engineer, reviewed by the CTO.\n- **Nothing live is changed** until the operator runs \u00a73.\n- **Rebuilt 2026-11-08 under DEC-1097 (2).** `apply.sh check` had stopped: the path map moved (W2-61h's\n  `evaluation_families`, `cc8139a1c8f4` \u2192 `6d79946fdbbd`); the live hook had not (`e406653ef6c9`), and the new pin's\n  guard code is byte for byte the old pin's. The rebuild adds the glob `runs/fresh-80/**` (the fresh 80's reader run and\n  kept outputs, FRESH-80-1 \u00a72 item 7) and deletes W2-84's hidden-half test cases with the ACT (DEC-1061 (4)). Rehearsed\n  again end to end: 0 failures (\u00a74). The 11-06 build is kept in `drafts/sets-root-guard/build-2026-11-06/`.\n- **The line rule, 2026-11-08 (readiness review 5 F1; the CTO's option A, within DEC-1097 (2)/(3)).** A path the shell\n",
      "tokens": 274
    },
    {
      "id": "7eb8d099bdb3291e1e9adc18",
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "text": "  (DEC-1097 (1), DEC-1092 (4)). If retrieval changes after the verdict, the 138 are measured again at the release\n  commit before the release is cut (DEC-1097 (4)).\n- Every comparison of memory reports its gains, its losses and an exact McNemar test (DEC-1079 (b) L1).\n\n## More Information\n\n- **Sources:** architecture v0.3; S0a `STACK_OPTIONS.md`, `CAPABILITY_CATALOGUE.md`; S0b2 `RESULTS.md`,\n  `GLUE_REQUIREMENTS.md`, `TOOL_REGISTRY.yaml`, `INTEGRATION_REPORT.md`; register DEC-064\u2026DEC-096, and\n  DEC-138\u2026DEC-174 for the sandbox layer, the launcher, the research role and the lesson loop; `spike-sandbox/EVIDENCE.md` (EXP-001, ADOPT-PARTIAL);\n  for Wave 2's memory, DEC-1029\u2026DEC-1097, `governance/project/tool-registry.yaml` (the `gov` entry of re-pin\n  window 4), `docs/research/W2-88-memory-practice.md`, `docs/research/W2-112-shared-reranker.md`, and\n  `governance/project/orchestration/packages/LIFT-1/` (E0 to E5, E0B, E2G, G1-PROFILE, PAT-1, BUNDLE-BUDGET-1,\n  M3-ADOPTION-1, FRESH-80-1).\n- **Revisit triggers:**\n  - a code graph above the tested envelope;\n  - vectors above ~100k (move to LanceDB, DEC-016);\n  - OpenSpec or codebase-memory-mcp breaking changes at a pin upgrade;\n",
      "tokens": 298
    },
    {
      "id": "430ff0852e17a8b320c86946",
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "text": "| DEC-1096 (2), (3), (5) | Glossary built and refreshed with the store, used by every agent; package beside the test | Test done (E2G: worse, 122 against 128). GLOSSARY-1 ready, parking recommended. W2-143 and W2-144 proposed, NOT filed. W2-88's line not added | Owner decides \u00a79. If built: file W2-143/144 and add W2-88's Wave-0 line | Owner's word (held) |\n| FRESH-80-1 \u00a72 items 14-19, \u00a72 (checker) | Fresh-80 scripts (one-shot, resume, silent-failure, citation check); staleness pass by the owner's checker | NOT BUILT / NOT RUN. Proposals, not yet decided | Build and review once the owner decides; checker's brief in READINESS \u00a72 | After the owner's FRESH-80 decision; before the 80 |\n| READINESS \u00a75 (proposal) | Seven-reviewer readiness review of memory before the 80 | Proposed, not decided | Owner says yes or no | Owner's word |\n| DEC-1093 (1) | W2-139 + W2-140 (Contract 4.3) merge and close in one batch on one green run, outside an experiment window | Filed, not started. CTO holds them until after the 80 (owner to confirm) | Owner confirms the hold. Then test designer (W2-140), then apply (W2-139) | After the fresh 80 |\n",
      "tokens": 284
    },
    {
      "id": "e8d4414d722f02067e86d1b8",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md",
      "text": "# FRESH-80-1: the fresh 80, what to expect, every fix for an honest verdict, how it runs, and the K9 bar (DEC-1092 (4), DEC-1095 (3))\n\nFor the owner. Drafted 2026-11-07 by a product-spec agent for the CTO (session `ad44f5fe`), from the records named in \u00a76. **Nothing here runs before the owner decides.** The figures below are counts from the 138 (tuning and diagnostic sets). No question, label or answer from a hidden or spent set is quoted, and the fresh 80 (`memory-verdict-2`) was not opened.\n\n",
      "tokens": 125
    },
    {
      "id": "3df273b432d451484c6810ae",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md",
      "text": "  digest after its staleness pass matches: yes. Files changed since DEC-1078's close: 0 (the checker's re-labelled\n  count: 0: unchanged 80, changed 0, ambiguous 0; the writer's step skipped).\n- **Anchors at the measured commit** (item 2, the measure's own loader): found once 179; found more than once 0;\n  missing and re-anchored by commit 0; missing with lines unchecked 0; unresolved 0 (of 179 source alternatives). Any source not found\n  once was fixed by the writer and checker before this record, or stays as the measure scores it (not found), named:\n  none.\n- **The nonexistent-id question** (item 6): 1 by category; it names no token the product reads as an id\n  (`lexical.ids_in`), so the product's check cannot run; the owner's checker searched the tree at `c00d525f` for the\n  whole token: nowhere. **Kept apart, not dropped** (`--item6-outside-nowhere`, reviewed READY); DEC-1071 (5)'s\n  `UNRESOLVED_IDS` stop is **not applicable** to it (the product cannot stop on a token it does not read as an id), so\n  it is reported apart on the reader's answer alone, outside the bar. If no, it is dropped from every figure and the drop reported (decided in FRESH-80-1 item 6): the declared\n",
      "tokens": 299
    },
    {
      "id": "42a076e80d635e58b0c62d74",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md",
      "text": "## 5. The fault rule (FRESH-80-1 \u00a73.5, as written)\n- **Before the first search** (the pre-flight, a load fault, the control outside 34 \u00b1 2 on the visible 40): the set\n  is unused; fix, then run.\n- **During the measure** (a non-zero exit, an output not whole, the backstop tripping, the machine stopping, **or a\n  retrieval answered otherwise than declared: a search whose bundle was not reranked by the shared service (`rerank.by`\n  other than `service`), a route (lexical or semantic) missing or unavailable, or the pool's rerank fallen back**): the\n  run stops; its partial outputs are kept and reported, never as the verdict; **one restart from the start follows**,\n  same commit, store and command, into a new kept folder (`attempt-2`), **whatever the partial figures show**; the\n  restart's figures count; a second fault stops everything and goes to the owner.\n  - Before the restart: the live reranker answers READY from the pin, a probe search is answered by the shared\n    service with every route, and the control passes again. If not, nothing is spent and the restart does not run\n    into the same outage: to the owner, and the one restart is taken when the servers are back.\n",
      "tokens": 297
    },
    {
      "id": "79a0cbaf69c0a33652df14a8",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md",
      "text": "# The fresh 80, declared before any search (FRESH-80-1 \u00a73.4; DEC-1097 (1))\n\nDeclared by the CTO (session `ad44f5fe`), 2026-11-08, after the pre-flight (every check as expected) and before any search of the 80; the scripts pinned `FRESH80-REVIEWED.sha256` = `d621d58bc697\u2026`. **Committed before any search of the 80**, after the pre-flight;\nthe blanks (four underscores) are filled from the pre-flight's output. Counts only: no question, label or answer of the 80 is\nnamed here.\n\n",
      "tokens": 120
    },
    {
      "id": "a0524562768f8cc82f10337f",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md",
      "text": "## 6. The hold (FRESH-80-1 item 13)\nFrom the control to the end of the judged reader run: no commit on `w2/integrate`, no store rebuild, no GPU window\n(`log/act-in-progress.txt` holds the line `FRESH-80 HOLD`, written by `drafts/fresh80/hold.sh begin` only when no\nother mark stands, and ended by `hold.sh end` only when it is that hold); W2-139 and W2-140 held. integrate's head and the\nintegration store log's new lines are recorded over the run window.\n\n**Basis:** question 1 (memory judged by what agents answer, on a set used once, by a condition chosen beforehand).\n",
      "tokens": 143
    },
    {
      "id": "e7786e8fe8efa2c8a2650372",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md",
      "text": "## 3. The denominator and the bar (DEC-1097 (1)(d); FRESH-80-1 \u00a74.3)\n- **The denominator:** 79 (the 80 less the nonexistent-id question, reported apart). A question with no row (a brake\n  stop) counts as not right; no question leaves the denominator once figures exist.\n- **The bar (K9), on the observed figure:** right end to end at A2 **at least 85 %** (at least **68 of 79**; 67 is\n  84.8 % and misses) **and** wrong claims **at most 5 %** (at most **3 of 79**; 4 is 5.1 % and misses). **Target 95 %**\n  (at least 76 of 79).\n- **Beside it, never in it:** the 95 % interval (the exact Clopper-Pearson interval named, Wilson's beside it; the exact Clopper-Pearson interval, or Wilson's as in\n  FRESH-80-1 \u00a74.3's example; both are printed); hit@5 (and hit@10, hit@20, MRR, in the bundle, full evidence); \"answer\n  correct, citation aside\"; the stricter of the two grades; grader agreement; A1 and A3; the nonexistent-id question\n  (right or not, and whether the product stopped with `UNRESOLVED_IDS` naming its id, DEC-1071 (5)); the failed later\n  searches (item 17); the citations outside every received item (item 18).\n",
      "tokens": 281
    },
    {
      "id": "03df741c85b520a4332f8797",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "## 3. ACT-GUARD-SETS-1: decided, not applied (a miss), the patch out of date\n- **Decided:** DEC-1084, apply right after re-pin window 4, the CTO's hidden-set tools converted first.\n- **The tools:** converted 11-06 (`drafts/d4b/sets_form.py`: the sets root as an argument, ids and counts only).\n- **Applied: no.** START-NEXT-SESSION of 11-07 did not list it; the CTO did not catch it.\n- **`apply.sh check` on 11-08:** exit 1, \"the files are neither as before nor as applied\"; the live\n  `.claude/hooks/pretooluse.py` (sha `e406653e\u2026`) and `governance/project/path-map.yaml` (`6d79946f\u2026`) moved since the\n  11-06 build. It cannot be applied as built.\n- **The reader-folder gap:** the ACT keeps `~/gov-os-eval/runs/**` open (results without question text), but\n  FRESH-80-1 \u00a72 item 7 puts the 80's reader rows (questions, gold, answers) under `runs/fresh-80/`. Add that folder to\n  the hidden globs.\n- **Left:** (1) an engineer rebuilds the patch against today's files, with the reader folder, in a clone; (2) the\n  end-to-end rehearsal (DEC-1057); (3) the CTO's review; (4) the owner's operator applies (about 1 minute); (5) the CTO\n",
      "tokens": 283
    },
    {
      "id": "4065429968c2fdbc156e36e7",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "## 5. Proposal: a final readiness review of memory before the 80 (not decided)\nSeven independent, read-only reviewers in parallel; each one record with the JUDGEMENT lines and a verdict block; none\nopens the 80 or any hidden or spent set.\n1. The store and its refresh hook (W2-116): every merge refreshes; no mixed halves; the backstop; failure modes.\n2. The links and status marks (W2-92, W2-129): status, in-force and changed-by right; superseded never read as current.\n3. The register ids (W2-131, W2-133): every register chunk its own id; no DEC-999.\n4. Chunking and the line cap (W2-135, drop-nested): cuts marked, lines unchanged; G3's overlapping slices and effect.\n5. Role filtering and hidden-set protection: `gov retrieve` by role; ACT-GUARD-SETS-1's state and gap; no path for a\n   measured role to the 80.\n6. The search-again practice in the briefs: the three briefs, W2-128's and W2-142's lines match what E2 measured.\n7. The fresh 80's own readiness: FRESH-80-1's twenty fixes, the scripts' one-shot and resume, the fault rule, the\n   checker's brief; against the code, without opening the 80.\n\n",
      "tokens": 278
    },
    {
      "id": "662828ad064f7f3cd8588358",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "## 6. Everything else open that touches memory or the verdict\n- **G3, overlapping slices:** to be decided after E0 (DEC-1090), still undecided. E3: today's bundle (overlaps\n  included) is best of five. Recommendation: no change before the 80; a ticket after the lift if the review finds it\n  worth it.\n- **The fresh-80 scripts** (FRESH-80-1 items 14 to 19) not built; **the checker's pass** (\u00a72) not run.\n- **The search-again practice:** in the project briefs; the kernel skills by W2-142 at the lift; W2-128's line with\n  W2-128.\n- **W2-139 and W2-140** (Contract 4.3, about 279 files): the CTO holds their integrate commits until after the 80 (no\n  change between the pre-flight and the 80; FRESH-80-1 item 13). A CTO hold, for the owner to confirm.\n- **Harness-only:** E0b's 246 seed conflicts (batch padding, the harness only); W2-138's F1 (a store built from a tree\n  with uncommitted edits hashes the edited files; a row; the measure clone is clean).\n- **The older window scripts** `live_window.sh` and `score_once_window.sh` still carry the F1 restore defect fixed in\n  `e4_window.sh`: never reuse them unfixed.\n",
      "tokens": 280
    },
    {
      "id": "7f4f2abaf223cc285c9d0c2b",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "- **Cost:** about 1 to 2 hours.\n- **What could have changed (11-05 to `c00d525f`):** DEC-1079 (mxbai dropped), DEC-1080 (the CTO's command rule),\n  DEC-1081 (W2-128 filed), DEC-1082 (permissions), DEC-1083 (K9 bar 85 % on the fresh 80, W2-32 S6 dropped, W2-15b out\n  of and W2-128 into K9), DEC-1084 (D9-FATES applied: W2-111, W2-55 S1, W2-66b, W2-90c; spill floor 2,048 MiB; exit\n  criterion 5 re-worded), DEC-1085 (W2-134), DEC-1086 (S11 re-worded, the 4,000-character cap), DEC-1087 (window 4's\n  items; the three layers back in Wave 2), DEC-1088 (`gov plan`; closed tickets never edited); tickets W2-128 to W2-136;\n  window 4's code (W2-92, W2-32 S11, W2-131, W2-133, W2-134, W2-61h S7, W2-135, W2-116, W2-129, W2-112's release, D-6\n  part 1); the register's growth shifting lines (re-anchoring handles it; FRESH-80-1 \u00a72 item 2 counts it).\n\n",
      "tokens": 212
    },
    {
      "id": "a86970867b6c964c4aee1f9a",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "# The fresh 80's readiness: what the owner holds before deciding (2026-11-08, session `ad44f5fe`)\n\nWritten for the owner and the next CTO session. The owner's word of 2026-11-08: **hold the experiments' decisions\n(FRESH-80-1, M3-ADOPTION-1, GLOSSARY-1); start nothing on the fresh 80 until the owner has decided.** Nothing here is\ndecided. FRESH-80-1 \u00a72 holds the twenty fixes and \u00a73.5 the fault rule, in full; this record holds the rest of the\nreport of 2026-11-08 (items 2 to 6).\n\n",
      "tokens": 121
    },
    {
      "id": "d68676217ba0d473d69a2abe",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "7. The fresh 80's own readiness: FRESH-80-1's twenty fixes, the scripts' one-shot and resume, the fault rule, the\n   checker's brief; against the code, without opening the 80.\n\n**Time and cost:** about 1 to 1.5 hours in parallel plus about 1 hour of triage; about 1.2 to 1.8M tokens of in-session\nagents; no GPU, no graded runs. **Fixed before the 80:** findings in scope, reachable in ordinary work, that fail open\nor would make the verdict wrong (at most two rounds); known already: ACT-GUARD-SETS-1 (rebuilt, with the reader\nfolder) and the fresh-80 scripts (FRESH-80-1 items 14 to 19). **Rows** (DEC-1010): the rest.\n\n",
      "tokens": 156
    },
    {
      "id": "f5dcfe2f2b26e899fcf448ab",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "text": "  - an *ambiguous* entry gets the second place as an alternative source, so the gold accepts either (as DEC-1078 (2)'s\n    cross-check added whole places that also state an answer);\n  - **the nonexistent-id question:** if its id now exists, flag it only and never change the question (FRESH-80-1\n    item 6 drops it from every figure, decided before the run).\n- **What the pre-flight checks, which the writer must respect:** no stray files (`*.yaml~`, swap files); the folder\n  mode 700; unchanged files keep their modification times (edit in place, never copy the folder back); the number of\n  files changed equals the entries re-labelled plus any later anchor fixes; **an ambiguous entry given an alternative\n  source counts as re-labelled.**\n- **To the CTO:** counts only (unchanged, changed, ambiguous, re-labelled, the nonexistent id flagged yes/no) and the\n  new combined digest, computed exactly as: `cd <the set's folder> && LC_ALL=C sha256sum *.yaml | sha256sum`.\n  (Corrected 2026-11-08 after readiness reviewer 7's F3 and F4.)\n- **Cost:** about 1 to 2 hours.\n- **What could have changed (11-05 to `c00d525f`):** DEC-1079 (mxbai dropped), DEC-1080 (the CTO's command rule),\n",
      "tokens": 296
    },
    {
      "id": "2b3232f142a5e8fae7c9a0e8",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md",
      "text": "## Beside the verdict (data, not judged)\n| figure | the fresh 80 (of 79) | expected (FRESH-80-1 \u00a71.4) | the 138 |\n|---|---|---|---|\n| right end to end, search again once (A2) | **78 (98.7 %)** | about 89 % (80 to 94) | 128 (92.8 %) |\n| one search (A1) | 72 (91.1 %) | about 76 % | 115 (83.3 %) |\n| up to three searches (A3) | 79 | | 128 |\n| hit@5 | 67 (84.8 %) | about 68 % | 106 (76.8 %) |\n| hit@10, hit@20, MRR | 70, 74, 0.629 | | 118, 124, 0.567 |\n| gold in the first bundle; full evidence | 74; 73 | about 85 % | 123; 116 |\n| answer correct, citation aside (A2) | 78 | | 135 |\n| the stricter of the two grades (A2) | 77 right, 1 wrong claim (still passes) | | |\n| grader agreement | 78 of 80; no grade missing | | 138 of 140 |\n- **A1 against A2:** 6 gains, 0 losses, exact McNemar p 0.031: search again once helps on a fresh set too.\n- **The one question not right at A2** was \"not found\", not a wrong answer.\n- **hit@5 at 84.8 %** sits just under the old hit@5 bar of 85 % (DEC-1083 (2)), which DEC-1097 (1)(d) replaced.\n- **The nonexistent-id question,** apart: the reader was right. DEC-1071 (5)'s `UNRESOLVED_IDS` stop is **not\n",
      "tokens": 284
    },
    {
      "id": "ab469b73b8e69b5cde5d658b",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md",
      "text": "## Data only, not judged (FRESH-80-1 \u00a73.4: no figure here chooses anything)\n| condition | right (of 79) | wrong claims | against the judged run |\n|---|---|---|---|\n| top 5, one call (e3) | 56 | 5 | 16 fewer than A1 (p < 0.0001) |\n| top 10, one call (e3) | 63 | 1 | 9 fewer than A1 (p 0.004) |\n| top 20, one call (e3) | 70 | 0 | 2 fewer than A1 (p 0.5) |\n| 40 unranked, one call (e3) | 68 | 1 | 4 fewer than A1 (p 0.13) |\n| top 20, search again (e3sa) | A1 69, A2 76, A3 79 | A2 0 | 2 fewer than A2 (p 0.5) |\n| 40 unranked, search again (e3sa) | A1 69, A2 75, A3 78 | A2 1 | 3 fewer than A2 (p 0.25) |\n| 12,000-token bundle, page 40, one call (e5) | 72 | 0 | equal to A1 (0 and 0) |\n| M3 (zerank + gte), one call (e4) | 72 | 0 | equal to A1 (0 and 0) |\n| M1 (the 0.6B + gte), one call (e4) | 72 | 0 | equal to A1 (0 and 0) |\n| the prototype glossary consulted, search again (e2g) | A1 72, A2 77, A3 77 | A2 0 | 1 fewer than A2 (p 1.0) |\n- **On a set used to choose nothing, the 138's findings hold:** the ranked, expanded bundle with search again once is\n  best; fewer items answer worse and less carefully (5 wrong claims at the top 5); a doubled bundle and both\n",
      "tokens": 291
    },
    {
      "id": "792a0fb2891aa28c8a9c6ece",
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "text": "| **D-4b the memory stage** (DEC-1055, DEC-1066-DEC-1096) | **superseded 11-11 (the state section above): done.** *Old text:* **in progress (2026-11-08)**. The build is merged; re-pin window 4 live (11-07 14:22); the pool on (`c00d525f`); PAT-1 done; **every experiment done** (E0 106/138 hit@5; E2 search again once 83.3 % \u2192 92.8 % right end to end; E3 today's 6,000-token bundle best of five; E4 M3/M1 rank higher but answer no better, 111 and 113 vs 114; E5 12,000 tokens no gain; E2G the glossary as consulted lowers, 122 vs 128). W2-136, W2-137, W2-138 merged (live at the lift). **Held by the owner (11-08):** the decisions on FRESH-80-1, M3-ADOPTION-1, GLOSSARY-1; nothing on the fresh 80 until then. **Before the 80:** ACT-GUARD-SETS-1 rebuilt and applied (overdue since window 4), the fresh-80 scripts, the checker's pass, the readiness review if approved (`FRESH-80-READINESS.md`) | `E0-RESULT.md` \u2026 `E5-RESULT.md`, `FRESH-80-1.md`, `FRESH-80-READINESS.md`, `M3-ADOPTION-1.md`, `GLOSSARY-1.md` |\n",
      "tokens": 252
    },
    {
      "id": "5301639ec4e413f4a5a6e841",
      "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md",
      "text": "  decision, marked by DEC-1083's status line; no edit needed.\n- `docs/plan/WAVE_2_WBS.md` lines 833, 859, 1861 (\"memory proven: the enlarged measure at 85 %\"; \"W2-32 (memory at\n  85 %)\"; \"the critical path is memory reaching 85 %\"): K9's entry criterion in older words; the WBS says earlier text\n  stays as history where not marked changed. Line 833 is the one that reads as a live criterion.\n- `.tickets/DAEO-h4rh.md` (W2-27) line 124 (\"memory proven\") rests on W2-32's S9 through `deps`; no 85 % hit@5 text.\n- History only, no edit: `packages/LIFT-1/E3-E5-DESIGN.md` line 56 (\"beside DEC-1083's hit@5 bar, not replacing it\");\n  `packages/LIFT-1/FRESH-80-1.md` lines 8, 233, 290-291; `packages/LIFT-1/M3-ADOPTION-1.md` line 255;\n  `packages/LIFT-1/E0-RESULT.md` line 30; `packages/LIFT-1/D4B-MEMORY-STAGE.md` line 171 (the 48 at 85 %, replaced by\n  DEC-1074 (1)); `packages/ACT-MSET-1.md`, `-2`, `-3`, `-4` (\"target 95 % hit@5, 85 % the floor\").\n\n",
      "tokens": 237
    },
    {
      "id": "67440749bec38e9aec880692",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "| one end-to-end reader run of 80 (A1\u2013A3, two graders) | $12.46 (the fresh 80); $0.157 a question (E2) | about the same: the bundle is a fixed 6,000 tokens, whatever the repository's size |\n| tuning: say 2 to 4 reader runs on the tuning set | \u2014 | about $25 to $50 |\n| the verdict's tools, once in the product | 2 to 3 h of agent work (FRESH-80-1 item 19) | none per repository once built |\n| pre-flight, staleness pass, control, judged run | about 1 to 2 h of the operator; about 45 min live | the same |\n| GPU memory | sampled peak 8,404 MiB during the measure (E0); padded reranker bound about 4.6 GB | the same: per search, not per repository |\n\n**In all, per adopted repository (est.):** about 2 to 3 days elapsed, mostly writing the two sets and tuning; about $40 to $65\nof reader and grader tokens, plus the writer's and checker's sessions; a few GPU hours; and about 3 to 4 hours of the\nowner's operator. Data conditions such as the five bundles or other rerankers are not part of the standard; on the\nfresh 80 they cost $96.59 more. **For W2-88 itself:** about +250 LOC (the set tools, S10's check, the skill step), so\n",
      "tokens": 282
    },
    {
      "id": "67c8cf807115d8ec790c21f6",
      "path": "governance/project/path-map.yaml",
      "text": "# engineer's tree ~/gov-os-worktrees/<WBS> and on its branch w2/<WBS>; in a designer's session in that tree only the\n# files its branch changes, and in the designer's <WBS>-tests tree the files the engineer's commits carried in; the\n# rest is the integrated code, which the test designer reads (DEC-963). No section, no check.\nrole_paths:\n  engineer:\n    reads_denied: [\"{ticket_tests}\"]\n  independent-test-designer:\n    reads_denied: [\"{ticket_impl}\"]\n# DEC-1082 (3), DEC-1097 (2): the sets root outside the repository, where the hidden halves are kept since ACT-D8 (the\n# measure's --sets-root), and the fresh 80's reader run (runs/fresh-80: its questions, gold answers, answers and kept\n# outputs; FRESH-80-1 \u00a72 item 7). The guard (.claude/hooks/pretooluse.py) refuses these globs, under the root and in\n# every tree, to the roles named here, and to each role a set in evaluation_sets measures (that set's hidden globs). It\n# reads this block from the main tree's copy only. Reads and the writes the guard can resolve are refused alike. Every\n# other folder under runs/ stays open. The measure and the fresh-80 scripts are unaffected: their commands name only\n",
      "tokens": 291
    },
    {
      "id": "78af9d15218bb1f4c7fd8a4a",
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "text": "  - the answer graded by one session, with a second grader on a 20 % sample, which is enough to report agreement;\n  - McNemar between each condition and today's bundle, with Holm within each experiment.\n- **The K9 bar** on end-to-end accuracy is proposed in E3's package, before its run, as DEC-1085 (6) asks.\n- **Cost in money:** I cannot give a sure figure before the pilot. E1 reads each call's own `total_cost_usd`, and I\n  project E2 to E5 from it before you set the cap (DEC-1086 C).\n\n**Impact:**\n- **memory:** the bar and the configuration chosen on what agents actually answer;\n- **time:** about 1 day before E0, and 1 to 1.5 days of experiments;\n- **cost:** about 13M input and 2.2M output tokens on Opus 5.5, priced by the pilot;\n- **EXAMIN's copy:** about 11-20 to 11-21 (from 11-19).\n\n**My recommendation on the order:** window 4 (with W2-135 and S11) \u2192 E0 and E0b \u2192 E1 \u2192 your cap \u2192 E2 \u2192 E3 \u2192 E4 \u2192 E5 \u2192\nyour decisions \u2192 the fresh 80.\n",
      "tokens": 237
    },
    {
      "id": "fcb7a00bc97027de03f456b6",
      "path": "docs/assessment/2026-10/F-models-context.md",
      "text": "### F5. The cost, token and context figures CAP-36 needs are in every result log, but nothing collects them\n\n**Evidence**\n\n- **What a result log holds.** I printed the key list from `assessment-B.json`:\n  - `total_cost_usd` (a list estimate);\n  - `duration_ms` and `duration_api_ms`;\n  - `num_turns`;\n  - `usage`, for the run;\n  - `modelUsage` per model: input, output, cache-read and cache-write tokens, `costUSD`, `contextWindow`, `maxOutputTokens` and `thinkingTokens`;\n  - `subagent_stats`, `permission_denials` and `terminal_reason`.\n\n  Table 2 needed nothing else.\n- **What `gov telemetry` covers.**\n  - It measures tokens and cost through ccusage, from the session logs under `~/.claude/` (`src/gov/telemetry/counter.py:1\u201312`).\n  - It lists provider, role, retries and others as \"UNDECIDED\" (`counter.py:37\u201339`).\n  - There is no \"effort\" anywhere in `src/gov/telemetry`, `src/gov/close` or `src/gov/launch`.\n",
      "tokens": 229
    },
    {
      "id": "5346c79c9dc0627f83bb12f9",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-a5.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 15,\n \"duration_ms\": 129186,\n \"total_cost_usd\": 0.8524988,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 1,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-a5.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 109
    },
    {
      "id": "640ca4de79a51781bf79ae3c",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-ad3a.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 12,\n \"duration_ms\": 37826,\n \"total_cost_usd\": 0.45487779999999994,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-ad3a.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "fa849547cad11863be7fcc9b",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-ad3b.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 19,\n \"duration_ms\": 67304,\n \"total_cost_usd\": 0.5601073999999999,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-ad3b.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 111
    },
    {
      "id": "bba6a123e7a96199b190d9ed",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-ad4-r7.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 16,\n \"duration_ms\": 70308,\n \"total_cost_usd\": 0.6267096,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"commit\": \"e043bb9 (Task: ORION-ad04, Role: product-spec, Implements: ADR-012)\",\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-ad4-r7.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 130
    },
    {
      "id": "535850e306187a8784e73957",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-ad4.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 25,\n \"duration_ms\": 82387,\n \"total_cost_usd\": 0.8479305999999999,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-ad4.json (the session's result envelope; its return text is not copied here)\",\n \"after_the_restart\": \"the session's commit 426dd51 was lost with the clone when the machine was restarted on 2026-10-14 (DEC-699); the session itself ran as recorded here. Run 7 redid the edit in session 16a6b9ff-8816-4e50-a417-074405944314 (launch/a-ad4-r7.json)\"\n}\n",
      "tokens": 178
    },
    {
      "id": "aa5e5d18fe2a083bb45163fb",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-adopt.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 34,\n \"duration_ms\": 1481219,\n \"total_cost_usd\": 1.2144717999999997,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 1,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-adopt.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "8688529179eebe7137780c17",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-adopt2.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 54,\n \"duration_ms\": 181740,\n \"total_cost_usd\": 1.1493494,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 1,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-adopt2.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "773e2bfef559e2b086c69a7f",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-audit.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 26,\n \"duration_ms\": 154874,\n \"total_cost_usd\": 1.2132957999999998,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-audit.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "7631a82842b700c83ec729f4",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-audit2.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 24,\n \"duration_ms\": 148485,\n \"total_cost_usd\": 1.3936332,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-audit2.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "f9200badf8db0fe7ec7215b3",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-audit3.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 16,\n \"duration_ms\": 86865,\n \"total_cost_usd\": 0.7632616,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-audit3.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "51cdfbea00a932a97cc5160a",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-eng.json",
      "text": " },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 12,\n \"duration_ms\": 31805,\n \"total_cost_usd\": 0.4320522,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-eng.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 93
    },
    {
      "id": "5c21f7c132509143e4f4cd5b",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-im02-eng.json",
      "text": " },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 13,\n \"duration_ms\": 37295,\n \"total_cost_usd\": 0.4368776,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-im02-eng.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 95
    },
    {
      "id": "d37c26b20f13aef442671963",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-im02-tests.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 20,\n \"duration_ms\": 139518,\n \"total_cost_usd\": 0.8408752,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-im02-tests.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 111
    },
    {
      "id": "0d6ac38db7cc3dacbbeca4ea",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-open6.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 32,\n \"duration_ms\": 96941,\n \"total_cost_usd\": 0.8055462000000001,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-open6.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "6e24fdd6a599b00bae7492b9",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-row25.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 13,\n \"duration_ms\": 37270,\n \"total_cost_usd\": 0.488859,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-row25.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 109
    },
    {
      "id": "6ff1a821544cf97c2991dd6f",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-spec.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 40,\n \"duration_ms\": 333106,\n \"total_cost_usd\": 2.0252790000000003,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 1,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-spec.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "06963f88ccc6cb252125680f",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-spec2.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 33,\n \"duration_ms\": 268853,\n \"total_cost_usd\": 1.5814366,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-spec2.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "e6720475c683e1aa78c76ac6",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-tests.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 19,\n \"duration_ms\": 129324,\n \"total_cost_usd\": 0.7480994,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 5,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-tests.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "e3369a6c148cd6b1932046ad",
      "path": "docs/plan/wave-1-exit/evidence/launch/a-tests2.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 24,\n \"duration_ms\": 123697,\n \"total_cost_usd\": 0.8615974,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/a-tests2.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "395dffbd6a9065acad894ef8",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-adopt.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 33,\n \"duration_ms\": 1503695,\n \"total_cost_usd\": 1.7971893999999997,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-adopt.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "cf84d99066462e14c06b8c42",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-audit.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 21,\n \"duration_ms\": 138360,\n \"total_cost_usd\": 1.1671532,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-audit.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "2c4dc21e94a16e4e7fb05a07",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-eng.json",
      "text": " },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 13,\n \"duration_ms\": 45095,\n \"total_cost_usd\": 0.6926979999999999,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-eng.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 96
    },
    {
      "id": "5518d46a52783601f9218a1f",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-row25.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 12,\n \"duration_ms\": 37533,\n \"total_cost_usd\": 0.4794744000000001,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-row25.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "321ce73840c9f523ba9b4704",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-spec.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 27,\n \"duration_ms\": 305964,\n \"total_cost_usd\": 1.53904,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-spec.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 109
    },
    {
      "id": "dbd18212f2454fbc195c5141",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-spec2.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 35,\n \"duration_ms\": 293426,\n \"total_cost_usd\": 1.6583696,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-spec2.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 110
    },
    {
      "id": "98abb5f675083706e2fc5a59",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-spec3.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 31,\n \"duration_ms\": 214648,\n \"total_cost_usd\": 1.3245074000000001,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-spec3.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    },
    {
      "id": "b8f4adcd7157ad7a4bb8670d",
      "path": "docs/plan/wave-1-exit/evidence/launch/b-tests.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 28,\n \"duration_ms\": 192960,\n \"total_cost_usd\": 1.244125,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/b-tests.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 109
    },
    {
      "id": "c1bc82fb2f959a6355927ace",
      "path": "docs/plan/wave-1-exit/evidence/launch/p4-probe.json",
      "text": "  \"note\": \"no host: only a research ticket gets an allowlist\"\n },\n \"launcher_exit\": \"0\",\n \"is_error\": false,\n \"terminal_reason\": \"completed\",\n \"num_turns\": 5,\n \"duration_ms\": 9613,\n \"total_cost_usd\": 0.27993860000000004,\n \"models\": [\n  \"claude-haiku-4-5-20251001\",\n  \"claude-opus-5-5\"\n ],\n \"permission_denials\": 0,\n \"kept_from\": \".gov-runtime/scratch/lead/log/p4-probe.json (the session's result envelope; its return text is not copied here)\"\n}\n",
      "tokens": 112
    }
  ],
  "supplementary_query": "The memory audit's measure: the control, the retrieval figures, the judged reader run, the fault rule, the misses file, the regression pool (DEC-1101 (1), DEC-1125 (2))\nS1 The control runs first: the standing visible-40 set is measured with the audit's declared configuration, and its hit@5 must be within 2 of the last audit's control (the first audit's control is within 2 of 34, E0's figure, DEC-1097 (1)(b)). Outside that, nothing is measured, the counts say `control out of range`, and `USED` is left as written by W2-170. Verify: planted fake `gov` returning a control at 34, 33 and 31: the first two proceed, the third stops before the audit set's first search [DEC-1097 (1), DEC-1101 (1)]\nS2 One attempt measures the kept questions with `gov.retrieval.measure`'s matcher and source families: hit@5, full evidence and the first gold rank per question (hit@10, hit@20 and MRR beside them), each search's ranked output kept so a label is never re-scored by searching again. Verify: a planted set of 12 questions against a fake `gov` with planted ranks: the figures equal the planted ones; the kept outputs re-score to the same figures with `--kept` [DEC-833, DEC-860, DEC-1101 (1)]\nS3 The judged reader run: the reader answers each question from its searches with search again once (A2), a named grader judges right end to end with a second grader's agreement beside it. The reader's and graders' prompts are the fresh 80's, pinned by hash (`READER_SYS`, the schemas, the cut), so audits compare with FRESH-80-RESULT. The verdict line reads: right end to end r of n, wrong claims w of n, the exact 95 % interval, against the scaled bar (at least ceil(0.85 n) right and at most floor(0.05 n) wrong; target ceil(0.95 n)); hit@5, gold in the first bundle, the answer correct with the citation aside and one search against two (exact McNemar) are printed beside it and never judged. Verify: a fake reader and graders with planted verdicts on n=40: the line shows planted r and w and the planted interval; bar 34 and 2 [DEC-1097 (1)(d), DEC-1098 (1), DEC-1101 (1)]\nS4 The fault rule, as FRESH-80-1 section 3.5 states it: a search not answered as declared (a bundle not reranked by the shared service, a route missing, the pool's rerank fallen back), or a store whose sha256 changed during the attempt, makes the attempt not whole. One restart is allowed while no attempt has counted; a second fault stops the audit and goes to the owner in the counts. No restart into the same outage: the live reranker is checked ready before each attempt. Verify: planted degraded search (one restart then pass; two faults then stop); planted store change (stop, no restart) [DEC-1097 (1)(g), DEC-1101 (1)]\nS5 A miss is a result: a verdict below either limit stands as recorded, is never run again and never re-scored to pass. The runner writes `runs/<audit>/misses.jsonl`, one line per miss (a question not right end to end at A2): `{\"id\",\"question\",\"gold_answer\",\"gold_sources\",\"answer\",\"outcome\",\"evidence_in_bundle\"}` with `outcome` one of `wrong`, `incomplete`, `not_found` and `evidence_in_bundle` the measure's own yes or no on whether a gold place was in the first bundle; an audit with no miss writes an empty file. Verify: planted run with 5 misses: the file holds 5 lines in that form; a second run on the same audit is refused by W2-170's `USED`; the file is the auditor brief's input form (parsed by the brief's own field list) [DEC-1074 (1), DEC-1101 (1), DEC-1125 (2)]\nS6 `runs/<audit>/FIGURES.json` carries counts only: the verdict numbers, the beside figures, and for the misses, counts by rank bucket (gold at rank 6 to 20; not in the first 20), by namespace of the gold source (embedded; keyword only), by category and by route; with the auditor's class counts added after its run. Verify: schema check over a planted run; grep for a planted question word, a planted gold path and a planted answer finds none [DEC-1101 (2), DEC-1097 (2)]\nS7 The regression pool: after a measured audit its kept questions join `pool/` under the sets root (hidden, like a set). Each audit re-runs the pool through the retrieval measure only (hit@5 and full evidence, no model tokens): the whole pool while it holds 400 questions or fewer, else a seeded draw of 400 (the seed recorded first). The pool's figures are printed beside the last audit's, and a fall of 3 points or more in either is named a regression in the counts. The 79 of the fresh 80 and the 138 of earlier sets are added by one planted-tested import path, run once by the CTO. Verify: planted pools of 300 and 900 questions: whole, then a draw of 400 with the same seed twice giving the same draw; a planted fall of 4 points is named [DEC-1101 (1), DEC-1125 (2)]\nS8 The spend is bounded and recorded: each model call's `total_cost_usd` goes to the run's ledger; the run stops at twice its projection (the fresh 80's 0.157 USD a question, so 12.6 USD for 40), and a brake stop goes to the owner first; a stopped run resumes without re-asking finished questions. Verify: planted ledger over the brake: stops; resume asks only the unfinished [DEC-1097 (1), DEC-1118 (3)]\nA question, gold answer, answer or source path in standard output, a log or an error text; only ids, counts and digests leave. Verify: a planted run on the fake reader and graders with a unique word in a question, a gold answer, an answer and a source path: grep of standard output, standard error, every log and `FIGURES.json` finds each 0 times\nA set measured twice, or re-scored to pass; a label changed after its figures exist. Verify: a planted miss (S5): a second run on the same audit is refused by W2-170's `USED` and `misses.jsonl` is byte-identical before and after the refusal; a planted verdict below the bar stays as recorded\nA search made before `DECLARATION.json` and `USED` exist (W2-170); the store rebuilt during an attempt. Verify: the planted run's call ledger: no search entry earlier than the file times of `DECLARATION.json` and `USED`; S4's planted store change stops the attempt with no rebuild call in the ledger\nThe shared Ollama servers or the reranker service touched other than by their ordinary query calls. Verify: a planted run with stub servers on stand-in ports: their request logs hold only query calls, and no stop, restart, model load or unload call; no process of either server is signalled\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "9d4ed97c5d62ee45238f0c2c",
      "path": "docs/plan/wave-1-exit/evidence/launch/w1-42-tests.json"
    },
    {
      "id": "3b789b53d458dc3ff59d4e80",
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/C.md"
    },
    {
      "id": "986068b520032dbe2add6029",
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md"
    },
    {
      "id": "cb9faf054558eeec4310cfa0",
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md"
    },
    {
      "id": "34578b27f6e7180914416f25",
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/E.md"
    },
    {
      "id": "8d727b6e6991ec3ec5e89f56",
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-SEARCH-AGAIN.md"
    },
    {
      "id": "919853b5956ce986b071e355",
      "path": "governance/project/orchestration/packages/LIFT-1/E1-PILOT-RESULT.md"
    },
    {
      "id": "1805ea4c7998bb7db6d5cc2f",
      "path": "governance/project/orchestration/packages/REPLAN-W2.md"
    },
    {
      "id": "0cd8526a7deb48f657e1f5bd",
      "path": "governance/project/orchestration/packages/USAGE-1.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "39c783f3deadddc6d9655a2b",
          "path": "governance/project/indep-briefs/memory-audit/auditor.md"
        },
        {
          "id": "d5a54f0775b7268834c8cade",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md"
        },
        {
          "id": "5c13c16833ed3dcf1ccafdf4",
          "path": "tests/unit/orchestration/test_w2_149_indep_launch.py"
        },
        {
          "id": "dcf0b4960076383e15e53b67",
          "path": "tests/unit/orchestration/test_w2_173_indep_launch.py"
        },
        {
          "id": "508d5460112c0cb3e9f4c44f",
          "path": "governance/project/indep-briefs/memory-audit/auditor.md"
        },
        {
          "id": "86dc28814bde75e1264050d2",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md"
        },
        {
          "id": "a295b09ebd6e192e292c6f52",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md"
        },
        {
          "id": "4c6a7c3f89a63d297c7a5708",
          "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md"
        },
        {
          "id": "2b50c057bcb277f5fe5e4b1f",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "5d38bb43fff7b55fe35ee1eb",
          "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "c5c9c504e9c46a6970c30566",
          "path": "docs/changes/W2-32-evidence.md"
        },
        {
          "id": "DAEO-0pyc",
          "path": ".tickets/DAEO-0pyc.md"
        },
        {
          "id": "9af8de622102d16905be219f",
          "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md"
        },
        {
          "id": "c4f6740b84ea640d2c14ecbc",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "0ae9dba062e2ab846b2472c8",
          "path": "tests/acceptance/W2-32/test_w2_32_record.py"
        },
        {
          "id": "DAEO-f6x3",
          "path": ".tickets/DAEO-f6x3.md"
        },
        {
          "id": "bcab0b8ac642b8a816e7e1c5",
          "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
        },
        {
          "id": "6f1e4ddfed30a78aeb0e868b",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md"
        },
        {
          "id": "98f9649bc6d789be2073b214",
          "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md"
        },
        {
          "id": "c0470b0eeb417debbda875a7",
          "path": "governance/project/orchestration/packages/MODEL-TIERS-1.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "f50a2344cd25767dc5f90152",
          "path": "governance/project/orchestration/packages/USAGE-1.md"
        },
        {
          "id": "83dd17fa152c21f33a295de0",
          "path": "governance/project/orchestration/packages/USAGE-RUBRIC-2.md"
        },
        {
          "id": "653e7af5049a8b705a09f033",
          "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md"
        },
        {
          "id": "e54be0ac9c862eafb9f99c01",
          "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md"
        },
        {
          "id": "e247d1b9814aaa36fc18064e",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "780ca4ad280313b0aa3cee91",
          "path": "governance/project/orchestration/reviews/W2-32-S9-review.md"
        },
        {
          "id": "8f2447128af455a729e68f99",
          "path": "governance/project/orchestration/reviews/W2-32-S9-review.md"
        },
        {
          "id": "ef7797362979ff8c27cd8f7c",
          "path": "governance/project/orchestration/reviews/W2-32-S9-review.md"
        },
        {
          "id": "1ed3f045a437ce57a41a3e63",
          "path": "tests/acceptance/W2-32/README.md"
        },
        {
          "id": "992395672ea4fd0289b6364a",
          "path": "tests/acceptance/W2-32/README.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "bbd2211f3c23f7d2d877a9bd",
          "path": "tests/acceptance/W2-32/test_w2_32_record.py"
        },
        {
          "id": "f536f043dc3eb65b557d7e98",
          "path": "tests/acceptance/W2-32/test_w2_32_record.py"
        },
        {
          "id": "DAEO-2bdu",
          "path": ".tickets/DAEO-2bdu.md"
        },
        {
          "id": "ef2aa5c904d9736cd476303d",
          "path": "docs/research/W2-88-memory-practice.md"
        },
        {
          "id": "887956ade513222d86d8571a",
          "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
        },
        {
          "id": "ac01ebb7748fc7b475bc41d9",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        },
        {
          "id": "249b917ed5a7dc6cead63101",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "ADR-0002",
          "path": "docs/adr/ADR-0002-architecture-and-stack.md"
        },
        {
          "id": "fffe27a89c0c8e199a1549ab",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "b2e74f702fb08bf4d0a755f3",
          "path": "governance/project/orchestration/packages/ACT-GUARD-SETS-1.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "7eb8d099bdb3291e1e9adc18",
          "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft"
        },
        {
          "id": "430ff0852e17a8b320c86946",
          "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
        },
        {
          "id": "e8d4414d722f02067e86d1b8",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md"
        },
        {
          "id": "3df273b432d451484c6810ae",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md"
        },
        {
          "id": "42a076e80d635e58b0c62d74",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md"
        },
        {
          "id": "79a0cbaf69c0a33652df14a8",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md"
        },
        {
          "id": "a0524562768f8cc82f10337f",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md"
        },
        {
          "id": "e7786e8fe8efa2c8a2650372",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md"
        },
        {
          "id": "03df741c85b520a4332f8797",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        },
        {
          "id": "4065429968c2fdbc156e36e7",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "662828ad064f7f3cd8588358",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        },
        {
          "id": "7f4f2abaf223cc285c9d0c2b",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        },
        {
          "id": "a86970867b6c964c4aee1f9a",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        },
        {
          "id": "d68676217ba0d473d69a2abe",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        },
        {
          "id": "f5dcfe2f2b26e899fcf448ab",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md"
        },
        {
          "id": "2b3232f142a5e8fae7c9a0e8",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md"
        },
        {
          "id": "ab469b73b8e69b5cde5d658b",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md"
        },
        {
          "id": "792a0fb2891aa28c8a9c6ece",
          "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md"
        },
        {
          "id": "5301639ec4e413f4a5a6e841",
          "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md"
        },
        {
          "id": "67440749bec38e9aec880692",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "67c8cf807115d8ec790c21f6",
          "path": "governance/project/path-map.yaml"
        },
        {
          "id": "78af9d15218bb1f4c7fd8a4a",
          "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md"
        },
        {
          "id": "fcb7a00bc97027de03f456b6",
          "path": "docs/assessment/2026-10/F-models-context.md"
        },
        {
          "id": "5346c79c9dc0627f83bb12f9",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-a5.json"
        },
        {
          "id": "640ca4de79a51781bf79ae3c",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-ad3a.json"
        },
        {
          "id": "fa849547cad11863be7fcc9b",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-ad3b.json"
        },
        {
          "id": "bba6a123e7a96199b190d9ed",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-ad4-r7.json"
        },
        {
          "id": "535850e306187a8784e73957",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-ad4.json"
        },
        {
          "id": "aa5e5d18fe2a083bb45163fb",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-adopt.json"
        },
        {
          "id": "8688529179eebe7137780c17",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-adopt2.json"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "773e2bfef559e2b086c69a7f",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-audit.json"
        },
        {
          "id": "7631a82842b700c83ec729f4",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-audit2.json"
        },
        {
          "id": "f9200badf8db0fe7ec7215b3",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-audit3.json"
        },
        {
          "id": "51cdfbea00a932a97cc5160a",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-eng.json"
        },
        {
          "id": "5c21f7c132509143e4f4cd5b",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-im02-eng.json"
        },
        {
          "id": "d37c26b20f13aef442671963",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-im02-tests.json"
        },
        {
          "id": "0d6ac38db7cc3dacbbeca4ea",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-open6.json"
        },
        {
          "id": "6e24fdd6a599b00bae7492b9",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-row25.json"
        },
        {
          "id": "6ff1a821544cf97c2991dd6f",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-spec.json"
        },
        {
          "id": "06963f88ccc6cb252125680f",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-spec2.json"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "e6720475c683e1aa78c76ac6",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-tests.json"
        },
        {
          "id": "e3369a6c148cd6b1932046ad",
          "path": "docs/plan/wave-1-exit/evidence/launch/a-tests2.json"
        },
        {
          "id": "395dffbd6a9065acad894ef8",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-adopt.json"
        },
        {
          "id": "cf84d99066462e14c06b8c42",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-audit.json"
        },
        {
          "id": "2c4dc21e94a16e4e7fb05a07",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-eng.json"
        },
        {
          "id": "5518d46a52783601f9218a1f",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-row25.json"
        },
        {
          "id": "321ce73840c9f523ba9b4704",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-spec.json"
        },
        {
          "id": "dbd18212f2454fbc195c5141",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-spec2.json"
        },
        {
          "id": "98abb5f675083706e2fc5a59",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-spec3.json"
        },
        {
          "id": "b8f4adcd7157ad7a4bb8670d",
          "path": "docs/plan/wave-1-exit/evidence/launch/b-tests.json"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "c1bc82fb2f959a6355927ace",
          "path": "docs/plan/wave-1-exit/evidence/launch/p4-probe.json"
        },
        {
          "id": "9d4ed97c5d62ee45238f0c2c",
          "path": "docs/plan/wave-1-exit/evidence/launch/w1-42-tests.json"
        },
        {
          "id": "3b789b53d458dc3ff59d4e80",
          "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/C.md"
        },
        {
          "id": "986068b520032dbe2add6029",
          "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md"
        },
        {
          "id": "cb9faf054558eeec4310cfa0",
          "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md"
        },
        {
          "id": "34578b27f6e7180914416f25",
          "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/E.md"
        },
        {
          "id": "8d727b6e6991ec3ec5e89f56",
          "path": "governance/project/orchestration/packages/LIFT-1/D4B-SEARCH-AGAIN.md"
        },
        {
          "id": "919853b5956ce986b071e355",
          "path": "governance/project/orchestration/packages/LIFT-1/E1-PILOT-RESULT.md"
        },
        {
          "id": "1805ea4c7998bb7db6d5cc2f",
          "path": "governance/project/orchestration/packages/REPLAN-W2.md"
        },
        {
          "id": "0cd8526a7deb48f657e1f5bd",
          "path": "governance/project/orchestration/packages/USAGE-1.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0cd8526a7deb48f657e1f5bd",
      "reason": "budget exceeded"
    },
    {
      "id": "1805ea4c7998bb7db6d5cc2f",
      "reason": "budget exceeded"
    },
    {
      "id": "34578b27f6e7180914416f25",
      "reason": "budget exceeded"
    },
    {
      "id": "3b789b53d458dc3ff59d4e80",
      "reason": "budget exceeded"
    },
    {
      "id": "8d727b6e6991ec3ec5e89f56",
      "reason": "budget exceeded"
    },
    {
      "id": "919853b5956ce986b071e355",
      "reason": "budget exceeded"
    },
    {
      "id": "986068b520032dbe2add6029",
      "reason": "budget exceeded"
    },
    {
      "id": "9d4ed97c5d62ee45238f0c2c",
      "reason": "budget exceeded"
    },
    {
      "id": "cb9faf054558eeec4310cfa0",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 39848,
  "budget": {
    "limit": 40000,
    "used": 39848
  },
  "hash": "9edfd40eff6382bd9319d28d1c1bf621591f7cbee3b7e429430226291c6486a2"
}
