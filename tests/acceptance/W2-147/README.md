# W2-147 acceptance tests: gov plan breaks a cycle only at a ticket inside it

Ticket DAEO-zi7s (W2-147), profile STANDARD, the owner's DEC-1102 (DEC-1088 (1), DEC-1099). Written by the
independent test designer (MR-3) from the ticket's KPI lines S1 to S4 and its three failure lines, before any
implementation, reading only the integrated code (`w2/integrate` `003f0bc23d47`; `src/gov/plan` last changed at
`69aa361ab73c`, W2-136).

## How they run

    env PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-147 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

In process, under 1 s, no model, no network, no GPU. Without a `PYTHONPATH`, the worktree's own `src`. Each case
plants its own ticket store in its temporary folder (never this repository's `.tickets/`), and `GOV_*` and `GIT_*`
variables are cleared. Git is needed for S4's reference (below).

## The interface the tests assume

The command is today's: `gov plan --root <root>` (text) and `gov plan --root <root> --json` (the envelope
`{"ok", "command": "plan", "result", "session"}`), driven through `gov.cli.main.main`. Nothing new is asked of its
form; the tests read:

- `result["batches"]`: lists of ticket ids, batch 1 first. `result["waits"]`: entries
  `{"ticket", "waits_for", "code", "what"}`. `result["codes"]` and the first text line name `CYCLE_TIEBREAK` when a
  cycle is broken.
- **A kept wait** of a ticket on another by `waits_on` is `{"ticket": <the waiting>, "waits_for": <the waited on>,
  "code": "WAITS_ON", "what": <the id as written in waits_on>}`; text `T2 waits for T1 (WAITS_ON <id>)`.
- **A break** is named as integrate names it today (W2-136's unit test
  `test_a_needs_after_write_cycle_is_broken_by_the_key_and_named`): one wait entry per broken wait,
  `{"ticket": <the ticket the chosen one had waited on>, "waits_for": <the ticket chosen>, "code": "CYCLE_TIEBREAK",
  "what": "<the broken wait's code> <its id or path>"}`; text `U waits for X (CYCLE_TIEBREAK WAITS_ON U)` when X,
  chosen, had waited on U. So `waits_for` names the ticket chosen and `what` the wait broken.
- **The choice** (the oracle, `w2_147_support.expected_breaks`, read from the planted graph alone): each cycle is a
  strongly connected component of two or more tickets, or one ticket that waits on itself. The ticket chosen is the
  component's first by the fixed key (priority, the lower first; then WBS order, natural; then id), and only its
  waits on tickets of the same component are broken. No other wait is broken.
- **A self-loop** (`waits_on` naming the ticket itself) is a cycle: broken at that ticket and named
  `{"ticket": X, "waits_for": X, "code": "CYCLE_TIEBREAK", "what": "WAITS_ON X"}`, text
  `X waits for X (CYCLE_TIEBREAK WAITS_ON X)`; X stays in a batch. (Today `hard_waits` drops a wait on itself
  without a word.)

## The planted graphs (`w2_147_graphs.py`)

Each ticket writes a path of its own and declares `needs: []`, so only `waits_on` joins them.

- `S1`: A waits on B, B on A; C waits on A and sorts first (priority 0). Expected: A's wait on B broken, C after A.
- `S2`: the case of 2026-11-09 with stand-ins of the same shape (`DAEO-s145` W2-145 and `DAEO-s137` W2-137 in a
  cycle, `DAEO-s088` W2-88 waiting on W2-145, `DAEO-s027` W2-27 on W2-88), one priority, waits by WBS id with a
  reason (`W2-88 — needs its result`). Expected: W2-137's wait on W2-145 broken; W2-88 and W2-27 keep theirs; batches
  W2-145 < W2-88 < W2-27.
- `TWO_CYCLES`: A-B and D-E, E waiting on B too (between the cycles), A on G (outside), F (outside, priority 0) on D;
  E (priority 0) is the second cycle's first and sorts before A. Expected: A's wait on B and E's wait on D broken,
  nothing else.
- `SELF_LOOP`: X waits on X; Y (outside, priority 0) waits on X; Z on nothing. Expected: X's wait on itself broken
  and named, Y after X.
- No cycle: `S1` without B's wait on A; `S2` without W2-137's wait; `MIXED_NO_CYCLE`, every other part of the plan (a
  `depends_on`, a needs on another's writes, overlapping writes, `READS_WIDE`, a `plan_override`, a closed ticket, a
  wait on an open record holding two tickets, an `UNKNOWN_WAIT` and a missing `needs:`: exit 1).

**S4's reference** (`w2_147_support.run_today`): `src/gov/plan/*.py` at `003f0bc23d47` (blobs `__init__`
`f4d3c8513e57`, `command` `73e8b31b1d4f`, `derive` `c9d4ac514077`, `overlap` `c3dc65eb1fa1`, `render`
`f19718bc0921`, `tickets` `0b69f8e181ce`), read with `git show` and loaded as a package of its own beside the
running tree's; its `command.run` is called with the CLI's defaults and its stdout and exit code compared byte for
byte with the running tree's `gov plan` on the same store. These are the ticket's only source paths
(`src/gov/plan/**`), so the two differ by the fix alone.

**S3's file orders:** the same tickets written under two sets of file names whose sorted orders are different
permutations (and written in reverse), at the same root.

## KPI lines, tests, and the outcome on `w2/integrate` `003f0bc23d47`

Run in the launch sandbox through the heavy slot: **25 tests, 10 failed, 15 passed** (0.44 s). Every red fails on
the fault the ticket names, none on a premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_147_inside.py::test_s1_the_break_falls_inside_the_cycle_at_its_first_ticket_by_the_key` | red | `_order` picks C (outside, first by the key): `TK-a waits for TK-c (CYCLE_TIEBREAK WAITS_ON TK-a)` beside A's break |
| S1 | `test_w2_147_inside.py::test_s1_the_outside_waiters_wait_is_kept_and_never_named_broken` | red | C's wait on A is broken (named CYCLE_TIEBREAK), no `TK-c waits for TK-a (WAITS_ON TK-a)` line |
| S2 | `test_w2_147_inside.py::test_s2_the_outside_waiter_is_batched_after_the_ticket_it_waits_on` | red | batches `[[TK-c, TK-a], [TK-b]]`: C shares A's batch |
| S2 | `test_w2_147_inside.py::test_s2_the_case_of_2026_11_09_keeps_w2_27s_wait_on_w2_88` | red | W2-27's wait on W2-88 and W2-88's on W2-145 are both broken; W2-27 is in batch 1 |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[s1-outside-waiter-text]` | green (guard) | today's plan reads the files sorted and orders by the key; a fix must keep that |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[s1-outside-waiter-json]` | green (guard) | as above, `--json` |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[s2-2026-11-09-text]` | green (guard) | as above |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[s2-2026-11-09-json]` | green (guard) | as above |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[two-cycles-text]` | green (guard) | as above |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[two-cycles-json]` | green (guard) | as above |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[self-loop-text]` | green (guard) | as above |
| S3 | `test_w2_147_named.py::test_s3_two_shuffled_file_orders_give_byte_identical_output[self-loop-json]` | green (guard) | as above |
| S3 | `test_w2_147_named.py::test_s3_each_break_is_named_with_the_ticket_chosen_and_the_waits_broken[s1-outside-waiter]` | red | an extra break names C (`waits_for` TK-c) |
| S3 | `test_w2_147_named.py::test_s3_each_break_is_named_with_the_ticket_chosen_and_the_waits_broken[s2-2026-11-09]` | red | extra breaks name W2-27 and W2-88 |
| S3 | `test_w2_147_named.py::test_s3_each_break_is_named_with_the_ticket_chosen_and_the_waits_broken[two-cycles]` | red | extra breaks: F's wait on D (F outside) and E's wait on B (between the cycles) |
| S3 | `test_w2_147_named.py::test_s3_each_break_is_named_with_the_ticket_chosen_and_the_waits_broken[self-loop]` | red | the self-loop is dropped: no CYCLE_TIEBREAK at all |
| S4 | `test_w2_147_graphs.py::test_s4_two_separate_cycles_are_each_broken_once_inside_themselves` | red | four breaks: F's wait on D (outside) and E's wait on B (between the cycles) beside one in each cycle |
| S4 | `test_w2_147_graphs.py::test_s4_a_self_loop_is_broken_at_that_ticket_and_named` | red | the wait on itself is dropped, not broken and named |
| S4 | `test_w2_147_graphs.py::test_s4_no_cycle_gives_integrates_output_byte_for_byte[s1-without-the-cycle-text]` | green (guard) | the running tree is today's code; any change in a plan with no cycle fails it |
| S4 | `test_w2_147_graphs.py::test_s4_no_cycle_gives_integrates_output_byte_for_byte[s1-without-the-cycle-json]` | green (guard) | as above, `--json` |
| S4 | `test_w2_147_graphs.py::test_s4_no_cycle_gives_integrates_output_byte_for_byte[s2-without-the-cycle-text]` | green (guard) | as above |
| S4 | `test_w2_147_graphs.py::test_s4_no_cycle_gives_integrates_output_byte_for_byte[s2-without-the-cycle-json]` | green (guard) | as above |
| S4 | `test_w2_147_graphs.py::test_s4_no_cycle_gives_integrates_output_byte_for_byte[mixed-text]` | green (guard) | as above; every other part of the plan, exit 1 |
| S4 | `test_w2_147_graphs.py::test_s4_no_cycle_gives_integrates_output_byte_for_byte[mixed-json]` | green (guard) | as above |
| S4 | `test_w2_147_graphs.py::test_s4_premise_todays_code_breaks_the_outside_waiter` | green (premise) | at `003f0bc23d47` S1's graph names C broken: the reference is the code before the fix |

The three failure lines: "a wait of a ticket outside every cycle broken, or a ticket outside the cycle chosen" is
S1's two cases, S2's two and S3's naming cases; "a break chosen differently in another file order, or not named"
is S3's two; "any change in the output for tickets with no cycle" is S4's six byte-for-byte cases.

**A check of the tests themselves** (a scratch copy of `src`, never committed): `_order` choosing, when no ticket is
ready, the first by the key among tickets whose remaining waits are all inside their own component, and breaking
only those, with `hard_waits` keeping a `waits_on` on the ticket itself, passes all 25. A naive fix (the first
ticket of any cycle by the key, all its waits broken) fails the two `two-cycles` cases (it breaks E's wait on B,
between the cycles).

## Notes and limits

- **N-1. "Chosen by the fixed key" read as the component's first.** S1 says the ticket is chosen from the component
  by the key; the oracle takes the component's first by the key even when that ticket also waits on a ticket
  outside the component (E in `TWO_CYCLES`): only its waits from inside are broken, and it still waits for B.
- **N-2. Simple cycles only.** Each planted component is one simple cycle, so one chosen ticket's breaks leave it
  acyclic. A component that needs a second break after the first (a figure eight) is not planted; how it is broken
  again is not stated.
- **N-3. Self-loops by `waits_on` only.** A `depends_on` on the ticket itself, or a `needs:` on its own writes, are
  not planted; today both are dropped too (`hard_waits`), and the KPI line names "a ticket waiting on itself".
- **N-4. The break's orientation is integrate's.** The tests keep today's naming of a break (`waits_for` the chosen
  ticket). A fix that turned it round would fail S1's first case, S3's naming cases and the self-loop's text line.
- **N-5. S4's reference is pinned.** If another ticket changes `src/gov/plan` on integrate before this one lands, S4's
  six cases compare against `003f0bc23d47` and may go red for a reason that is not this fix; then the pin moves by a
  test designer's revision, and what S4 compares is unchanged.

## Files

- `w2_147_support.py`: planting, running `gov plan` in process, today's code from git, the oracle.
- `w2_147_graphs.py`: the planted graphs.
- `conftest.py`: the path and the cleared environment.
- `test_w2_147_inside.py` (S1, S2), `test_w2_147_named.py` (S3), `test_w2_147_graphs.py` (S4).
