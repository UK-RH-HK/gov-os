# PKG-W2-171-IFACE-1 — W2-171 (DAEO-k1e2) states no interface; the pair cannot start (DEC-1052)

Lead run 1 (build), 2026-11-12 ~01:50 UTC. No worker launched, nothing committed.

## Question
`.tickets/DAEO-k1e2.md` has KPI lines but no `## Interface` section. W2-170 (DAEO-61vm) had the same gap and got
one through PKG-W2-170-IFACE-1, option (a) (`briefs/LIFT-w2-170-iface.md`). A test designer and an engineer started
now would each invent the command line, exit codes, file forms and test seams below, and the tests would not fit the
code. Who states them, and when?

## Options (cost)
- **(a) Recommended.** The CTO (or a product-spec helper, as LIFT-w2-170-iface) adds `## Interface` to DAEO-k1e2 from
  the gap list below, then a fresh lead run (build). Cost: about 45 min helper (Sonnet high, C2, about 3 USD) + the
  CTO's read; the pair starts next day-slot. Keeps the ticket as the one place the reviewer audits against.
- (b) The lead writes one interface block into both briefs and the pair works to it. Cost: none now; but against
  DEC-1052's letter (the ticket states it), W2-172/W2-173 cannot cite it, and the FULL review audits code against a
  block that is not in the ticket. A likely review finding.
- (c) Split the ticket: S1, S2, S4 (control, retrieval figures, fault rule) now with a short interface; S3, S5-S8 later.
  Cost: a new ticket and Definition of Ready; two review rounds; the first audit (Mon 11-23) needs both halves anyway.
Confidence in (a): high. Blocks: all of W2-171, hence W2-172 and W2-173's measure-dependent lines, and the first audit.

## What the Interface must state (gaps found; a proposal for each)
1. **Command line.** W2-170 §1 fixes `python3 -m gov.memaudit <subcommand>` and says W2-172 adds `run due baseline
   status`. W2-171's subcommands are not named. Proposal: `measure` (control, attempts, kept outputs, retrieval figures;
   S1 S2 S4), `judge` (the reader run, graders, verdict line, misses.jsonl, FIGURES.json; S3 S5 S6 S8, `--resume`),
   `rescore --kept` (S2's re-score; or say `--kept` is `gov.retrieval.measure`'s own flag on the kept folder), `pool`
   (S7 re-run), `pool-import` (S7's one-time 79 + 138; its source folders named as derived paths, never flags),
   `classes` (S6's auditor class counts added to FIGURES.json, or say W2-172/W2-173 adds them). Flags as W2-170 §1
   (`--sets-root`, `--audit`, no flag naming a folder under the root).
2. **Exit codes.** W2-170 uses 0-4 (ok, refused, void, used, usage). Needed for: control out of range (S1), fault stop
   after the restart (S4), store changed (S4), reranker not ready (S4), brake stop (S8), pool regression (S7: exit 0 with
   a counts line, or not?). W2-172 S3 stops on any non-zero; it must know which of these are "to the owner".
3. **Layout under `runs/<A>/`.** Proposal from the fresh 80: `attempt-<n>/{kept/00001.json.., measure.txt, FAULT,
   DONE}`, `COUNTS` (the counting attempt), `STOPPED` (cause word), `reader/<qid>.json` rows (resume), `misses.jsonl`,
   `FIGURES.json`; and the events W2-171 appends to W2-170's `ledger.jsonl` (W2-170 §2 names `search`, `spend`; also
   `control`, `attempt`, `fault`, `restart`, `store`, `brake`?) and their fields (F3's "no search entry earlier than
   DECLARATION.json and USED" needs `at` comparable to file mtimes).
4. **The pool's place.** The KPI says `pool/` under the sets root; W2-170 §2 already fixed
   `fixtures/evaluation/memory-pool/hidden/<audit>-<qid>.yaml` (a root `pool/` matches no hidden glob). The Interface
   should confirm W2-170's place, say where the seed is recorded first and where the "last audit's" pool figures are
   read from (S7), and the draw's algorithm (e.g. `random.Random(seed).sample(sorted(ids), 400)`).
5. **The control (S1).** Which set and part ("the standing visible-40": `memory-verdict-2 --part visible`?), which
   declared settings it runs with (DECLARATION.json `settings`), and where "the last audit's control" is read (the last
   measured audit's FIGURES.json `control.hit5`?; none found: 34). "Within 2" is |x - last| <= 2 (31 stops at 34: yes).
6. **Test seams (S1-S4, S8, F1, F4).** How the fake `gov` is named (`--gov <exe>`, as `gov.retrieval.measure`), how the
   fake reader and graders are named (`--claude <exe>`, or a Python seam like f80lib's `_run_claude`), how the reranker
   ready check is made (command or URL), and how stub Ollama and reranker servers on stand-in ports are pointed at
   (env or flag names) for F4's request logs. Which store file's sha256 is watched (the declared `store_sha256` and
   path from DECLARATION.json?).
7. **The pinned prompts (S3).** `READER_SYS`, `READER_SCHEMA`, `GRADER_SYS`, `GRADER_SCHEMA`, `CAP`, `prompt_of`, the
   A1/A2/A3 cut (`outcome`) and the refine parts live in the CTO's scratch, `drafts/d4b/e2_run.py` (sha256 f0099fd6…),
   `e2g_run.py` (35e7a4e5…), `e3_run.py` (95718dbc…), read by syntax tree in f80lib. Product code cannot import scratch:
   the Interface must say they are copied verbatim into `src/gov/memaudit/` and what the hash pins (each string's
   sha256, listed in the ticket). Also the models: the reader `claude-opus-5-5` high, grader `claude-opus-5-5` (counts),
   second grader `claude-sonnet-5-5` (agreement), as the fresh 80 ran.
8. **The verdict line (S3)** as an exact printed form, and the beside lines (hit@5, gold in the first bundle, answer
   correct with citation aside, McNemar one search vs two: exact two-sided p) in their forms.
9. **misses.jsonl (S5).** The KPI says `evidence_in_bundle` "yes or no"; the approved auditor brief (DEC-1129 (2),
   unchangeable) says JSON `true`/`false`. The Interface should say booleans. Also the map from the grader's verdict to
   `outcome` (`wrong`/`incomplete`/`not_found`), and the form of `gold_sources` (the question's `sources` as written?).
10. **FIGURES.json schema (S6).** Exact keys: the verdict numbers, the beside figures, misses by rank bucket (names:
    `rank_6_20`, `not_in_20`; and a miss with gold in the first 5?), by namespace (embedded vs keyword-only: from the
    question's `keyword` bool?), by category, by route (which route: the one that ranked the first gold item?), the
    control, the pool block, the auditor's five class counts (key names as the auditor brief's `result.json`).
11. **Spend and resume (S8 vs S5/F2).** The ledger (W2-170's `ledger.jsonl` `spend` events, or a separate file), the
    projection (0.157 x n) and the brake (2x), what "to the owner first" writes, and how `--resume` after a brake stop
    is told apart from a second run that `USED` must refuse (S5, F2): e.g. resume allowed only while `STOPPED` holds
    `brake` and no `FIGURES.json` exists.
12. **Fault rule details (S4).** "Not answered as declared" as testable fields of the fake `gov`'s JSON (f80lib
    `degraded()`: `rerank.by != "service"`, a route missing/unavailable, the pool rerank fallen back); whether the
    restart is inside one `measure` invocation (as run_measure.sh) or a second invocation.

## Also found
- The fresh-80 reference copies were not in the worktree (`.gov-runtime/scratch/ref/fresh80/` absent at start); the
  brief says the CTO copies them. They also need `drafts/d4b/e2_run.py`, `e2g_run.py`, `e3_run.py` beside them (item 7).
