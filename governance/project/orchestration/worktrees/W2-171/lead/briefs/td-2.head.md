# Brief td-2: independent test designer for DAEO-k1e2 (W2-171), review round 2 fix batch, profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-k1e2 (W2-171: the memory audit's measure, `python3 -m
gov.memaudit measure|judge|classes|pool|pool-import`). Your suite already exists at tests/acceptance/W2-171/ (td-1's,
merged and green). The FULL review round 1 found two behaviours it does not test. The CTO ruled (ticket, section
`PKG-W2-171-REV1-1`): test them first (DEC-136), as behaviours, then an engineer fixes them. Add acceptance cases for
the two behaviours below, red on today's code, and touch nothing else of the suite unless a shared helper (world,
scenario, fake) must grow to plant them; every existing case stays as it is and green.

You write to the ticket's `## Interface` (items 1-12) and the CTO's rulings under it; you never change it. A gap or a
clash comes back as a package (status PACKAGES: question, options with cost, recommendation, confidence, what it
blocks). You do not read the engineer's code on this ticket (`src/gov/memaudit/` modules this ticket added, beyond
W2-170's `declare`, `ledger`, `say`, `layout`), and you do not need to: reach it as its callers do (the child process),
as td-1's suite already does.

## The two behaviours (from the review's findings, described as behaviours)

**B-1 (finding F-1, S3, Interface item 8): the VERDICT line's exact 95 % interval is computed from the counts.**
Item 8: the interval is Clopper-Pearson, `lo`/`hi` in percent to one decimal, by bisection on the binomial tails as
`f80lib.exact_interval` (the fresh 80's, at /home/usain/gov-os-worktrees/W2-171-tests/.gov-runtime/scratch/ref/fresh80/f80lib.py).
The printed bounds are the exact bounds of (r, n) rounded once to one decimal, never a re-rounding of `FIGURES.json`'s
4-place `interval_exact` fractions. The planted cases (exact bounds in brackets):
- 32 right of 40 prints `exact 95 % interval 64.4 to 90.9 %` (64.352 %, 90.948 %; a double rounding prints 64.3 to 91.0);
- 78 right of 79 prints `exact 95 % interval 93.1 to 100.0 %` (93.148 %; a double rounding prints 93.2), if your world
  can plant a set of 79 (W2-170's preflight passes 36 to 40 questions: if 79 cannot be planted, cover 32 of 40 and one
  more r at n = 40 where the two roundings differ, which you find by computing; say which in the docstring).
- `FIGURES.json`'s `verdict.interval_exact` stays `[lo, hi]` as fractions to 4 places (item 10) for the same run.
Compute the expected bound in the test as an independent Clopper-Pearson (your own bisection or a closed form you
write), and also assert the literal strings above, so the case is not only the code's arithmetic mirrored.

**B-2 (finding F-2, S2, Interface items 1, 2 and 8): `measure --kept <n>` never prints a faulted attempt's figures.**
Item 8: "a faulted attempt's figures are never printed"; item 1: `measure --kept <n>` "prints the `RETRIEVAL` line of
item 8, writes nothing, exits 0 or 1 `MS-KEPT`, never 3". The lead's reading (inside the Interface: `MS-KEPT` is the
only refusal item 1 gives `--kept`): for an attempt folder holding `FAULT` (for example a degraded attempt-1 whose kept
outputs are whole in number, then a clean attempt-2 that counts; S4's planted restart), `measure --kept 1` exits 1,
prints `MS-KEPT`, prints no `RETRIEVAL` line, writes nothing and searches nothing; `measure --kept 2` on the same run
prints attempt-2's `RETRIEVAL` line and exits 0. Cover at least the degraded cause; the `exit` cause too if cheap. If
you read the Interface otherwise, return PACKAGES rather than test your own reading.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-171-tests |
| branch | w2/W2-171-tests |
| your allowed paths | tests/acceptance/W2-171/** |
| the ticket (KPI lines, Interface items 1-12, rulings, PKG-W2-171-REV1-1 at its end) | /home/usain/gov-os-worktrees/W2-171-tests/.tickets/DAEO-k1e2.md |
| your suite (README.md first; the S2, S3, S4 files and w2_171_scenario.py) | tests/acceptance/W2-171/ |
| the fresh 80's reference (exact_interval) | /home/usain/gov-os-worktrees/W2-171-tests/.gov-runtime/scratch/ref/fresh80/ |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The held-out and hidden-half rules (DEC-820 (b), (d))
Everything is planted under pytest's `tmp_path`, as your suite already does. Never the real sets root (`~/gov-os-eval`),
the real runs folder (`~/gov-os-runs`), the real HOME, a real search, a real model call. Never open any evaluation
set's hidden half.

## Rules
- Every pytest through the heavy-slot gate (the CTO's order), one folder or one file per run, with a TMPDIR outside the
  repository and outside ~/gov-os-runs (your sandbox's own temp folder: `mkdir -p "$TMPDIR/W2-171-td2"` once):
  `TMPDIR="$TMPDIR/W2-171-td2" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-171-tests/src python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- Run your new cases (red now, each for the reason named: say which and why), then the whole tests/acceptance/W2-171
  once before your last commit: every old case green except W2-170-style branch checks the README already names.
- Name new cases `test_s3_...` and `test_s2_...` after the KPI line; a docstring saying which finding and Interface item
  each covers. Update tests/acceptance/W2-171/README.md's per-KPI list.
- Keep it fast: the fake commands only; bounded polls, never a bare sleep. No test name with `real`, `green_here`,
  `time_limit`.
- Literal paths only as write targets; no merge, no push, no edit outside your paths.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-k1e2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1097, DEC-833, DEC-860" -- tests/acceptance/W2-171`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line of each run; which cases are red and why) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

The ticket's context packet (`gov context DAEO-k1e2 --role independent-test-designer`, built by your lead) follows;
its `ticket_text` is the same ticket file as above.

