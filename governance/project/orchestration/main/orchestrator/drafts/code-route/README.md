# The code route's figures on the 138 and the 80 (DEC-1098 (2)(b)), counts only

By a research agent for the Wave 2 CTO, 2026-11-09. The author read no question, label, answer or kept output, and
opened nothing under `~/gov-os-eval/`. The script opens the kept outputs in its own code and prints only counts.

## The command (the CTO runs it, CPU only, about a minute; no retrieval, no GPU)

```
nice -n 10 ~/.local/share/gov-os/pin-bcea09060ebc/bin/python -I \
  /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/code-route/code_route_counts.py \
  --sets-root ~/gov-os-eval
```

Run it as the orchestrator (the role the measures ran as). A session the sets measure is refused, by the measure's
own rule. Everything else is a default:
- the clone: E0's, `~/gov-os-runs/D4B/w4-e0/repo`. It must be at `c00d525fd420`, or the script refuses. It was at
  that commit on 2026-11-09.
- the 138: E0's kept outputs `<root>/runs/w4-e0/r80` (`memory-retrieval --part all`) and `r60`
  (`memory-verdict --part hidden`), with E0's `measure.txt` under `~/gov-os-runs/D4B/w4-e0/out/`.
- the 80: `<root>/runs/fresh-80/attempt-1/kept` (`memory-verdict-2 --part hidden`).
- the budgets: batch 10, bundle 6,000, stack 24,000, the defaults both measures ran with.

## What it does

It calls `gov.retrieval.measure.measure` unchanged on the kept outputs (`--kept`). That brings the measure's own
loader, refusal, hidden-cover check, in-memory re-anchoring, families and call-order reader, and its check that the
kept outputs and the calls match exactly. Only `_ask` is wrapped: it records each call's document, lets the measure
score the question, then rebuilds the same stacked context with each item's `routes` and checks that its first gold
rank equals the measure's. It prints per set, and for "the 138" and "the 80" in total, with and without the category
`nonexistent-id`, which is scored apart:
- questions; the code route asked (`facets.code` in the first call's bundle), and how many of those were unavailable;
  the routing put a code hit ahead (`routing.code`);
- questions whose bundle (first call) holds a code-route item, and the same for the stacked context;
- questions with any gold match; questions whose **first gold-matching item came by the code route** (`code` among its
  `routes`), the same by the code route alone, and the same within the first five; questions where **some**
  gold-matching item came by the code route;
- the code route's share of bundle items and of stacked items, all routes and code alone;
- per category name, as counts only (never a question id): questions; code item in the bundle; first gold by code;
  first gold by code alone; first gold by code in the first five; any gold by code. The callers questions are the
  line of their category, by the name the set files give it.

Its header lines check the re-read three ways: the kept outputs read whole, the first gold rank equal to the
measure's for every question, and hit@5 re-scored equal to the measure's recorded `total:` line (only that one line of
`measure.txt` is read). If any of these differs, the line says so.

A fault prints one line. Its traceback goes to `code_route_counts.err` in the fresh 80's run folder, where f80lib's
tools put theirs and which ACT-GUARD-SETS-1 hides. The script writes nothing else.

## The planted test (passed 2026-11-09)

```
~/.local/share/gov-os/pin-bcea09060ebc/bin/python -I \
  /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/code-route/test_planted.py
```

It builds a fake sets root, clone and kept outputs in the same layout, in a new temporary folder (`--work <empty
folder>` to choose one): 7 questions in three categories, one with two calls (a continuation and a repeated item), an
empty stated-gap bundle and an unavailable code facet. It checks:
1. every count against a hand count;
2. that no question id, question text, answer or sets-root path is printed;
3. that a kept output left over is refused;
4. that a measured session (`GOV_ROLE=independent-auditor`) is refused;
5. that a clone at another commit is refused.

Result: `PLANTED TEST: PASS`.

## Reading the figures

- "Came by the code route" means `code` is among the item's `routes`: the fusion's record of every route that returned
  that chunk (`fusion.rrf`, carried to the item by `retrieve.item`). "Alone" means the code route was the only route
  that returned it, so no other route would have put it there.
- A pooled or code-first reorder does not change `routes`. An item expanded to its parent keeps the routes of the
  child that was hit.
