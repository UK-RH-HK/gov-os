# W2-147 evidence: `gov plan` breaks a cycle only at a ticket inside it (DAEO-zi7s; DEC-1102)

**What it is.** `src/gov/plan/derive.py`'s `_order` broke the incoming waits of the first remaining ticket by the fixed
key whenever the order was stuck, even when that ticket was not in a cycle. On 2026-11-09 it broke W2-27's wait on
W2-88 while W2-145 and W2-137 formed the cycle. A plan that silently drops a real wait would launch work out of order.

## The change (`src/gov/plan/derive.py` only)

- **`_components`** (new): the strongly connected components of the tickets still to order (Tarjan's, iterative,
  visited in the fixed key's order, so the result does not depend on file order).
- **`_break_ticket`** (new): when no ticket is ready, every remaining ticket waits on another remaining ticket, so the
  first component no other remaining ticket leads into is a cycle (or a self-loop). The break ticket is that
  component's first ticket by the fixed key (priority, then WBS order, then id); of the components no other leads
  into, the one whose first ticket comes first by the key is broken first.
- **`_order`**: breaks only the chosen ticket's waits from inside its component; a ticket outside every cycle is never
  chosen and keeps all its waits, so it is batched after what it waits on. A component that still holds a cycle after
  one break is broken again inside what is left of it.
- **The self-loop:** `hard_waits(..., self_loop=True)` keeps a `waits_on` on the ticket itself; `make_plan` passes it,
  so the self-loop is broken at that ticket and named. The default (`self_loop=False`) keeps `gov launch`'s lead check
  (`src/gov/launch/plan_check.py`, outside this ticket's paths) as it was: a self-wait does not refuse a lead.
- **Naming:** unchanged form: each broken wait is a `CYCLE_TIEBREAK` wait, `<waited-on> waits for <chosen> (CYCLE_TIEBREAK
  <code> <what>)` in the text and `{"ticket", "waits_for": <chosen>, "code": "CYCLE_TIEBREAK", "what"}` in `--json`; the
  code is in the first line's codes.
- **No cycle:** the stuck branch never runs, so the output is unchanged.

Diff: `src/gov/plan/derive.py` +69 −10; unit tests `tests/unit/plan/test_w2_147_cycles.py` (13 tests, new).

## One row per KPI line

| KPI | Evidence | Outcome |
|---|---|---|
| S1 the break falls inside the cycle, only its waits from inside are broken | `test_a_cycle_with_an_outside_waiter_is_broken_inside_the_cycle` (A↔B, outside C waits on A and sorts first: the break is A's wait on B; C's wait on A kept), `test_an_outside_ticket_the_cycle_waits_on_is_never_broken`, `test_a_three_ticket_cycle_breaks_only_its_first_ticket_s_waits_from_inside`, `test_order_breaks_a_downstream_cycle_only_after_its_upstream_one`; `gov accept W2-147` success-1 2/2 | pass |
| S2 a ticket outside every cycle keeps all its waits and is batched after them | `test_the_outside_waiter_is_batched_after_what_it_waits_on`, `test_the_case_seen_on_2026_11_09_keeps_w2_27_s_wait_on_w2_88` (W2-27 waits for W2-88 kept; batches W2-137, W2-145, W2-88, W2-27); `gov accept` success-2 2/2 | pass |
| S3 deterministic and named | every planted graph above planted in two file orders, text and `--json` compared byte for byte (`same_in_two_orders`); `test_the_break_is_counted_in_the_codes_and_the_waits`; `test_a_needs_cycle_breaks_at_its_first_ticket_by_the_key_as_before`; `gov accept` success-3 12/12 | pass |
| S4 the planted graphs | `test_two_separate_cycles_are_each_broken_once_inside_themselves` (the wait between the cycles and the outside waiter's kept), `test_two_unlinked_cycles_are_broken_once_each`, `test_a_self_loop_is_broken_at_that_ticket_and_named`, `test_the_launch_check_s_waits_still_leave_a_self_wait_out`, `test_with_no_cycle_the_output_is_byte_identical_to_integrate_s` (a store with every wait code, a held ticket, an override, a warning and two findings, its text pinned from integrate's 003f0bc23d47 before the change); `gov accept` success-4 9/9 | pass |

## Runs (2026-11-09, `PYTHONPATH=<worktree>/src`, through `heavy_slot.sh`)

- Before the change: the new unit tests 9 red, 4 green (the defect reproduced: the seen case broke T-27's wait on
  T-88); `gov accept W2-147` 15 passed, 10 failed.
- After: `tests/unit/plan` 69 passed; `gov accept W2-147` 25 passed, 0 failed; `tests/acceptance/W2-136` 76 passed;
  `tests/unit/launch/test_w2_136_plan_check.py` 34 passed.

[DEC-1102, DEC-1088 (1)]
