# Brief eng-3: engineer for DAEO-ozyt (W2-157), profile STANDARD, class C2: review round 1's fix

You are a fresh engineer for ticket DAEO-ozyt (W2-157: the GPU backstop, `gov resources --backstop <pgid>...`). The
code is built (`src/gov/resources/backstop.py`, head 97e44155c of w2/W2-157). An independent review found that when the
backstop's own process group is among the named groups, a trip's SIGSTOP to that group freezes the backstop before it
pauses the groups named after it and before it writes the TRIP line and the inbox item. The lead settled the wanted
behaviour as L5b below; the independent test designer's cases for it are red. You fix the code to L5b and make one
documentation addition, and nothing else. You never read or change `tests/acceptance/` (an independent test
designer's); the failing output below is all you get of it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157 |
| branch | w2/W2-157 |
| your allowed paths | src/gov/resources/backstop.py, src/gov/resources/command.py, src/gov/resources/config.py, tests/unit/resources/test_w2_157*, docs/changes/W2-157-evidence.md |
| the ticket (S1: every live named group paused; S4: one inbox item, then the watch ends) | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| the readings L1-L9 as applied (L5 the groups and the trip, L6 the log, L7 the inbox item, L8 the result) | docs/changes/W2-157-evidence.md |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## L5b (the lead's reading, added after review round 1's FR-1 and FR-2): the backstop's own group is paused last

When the process group of the `gov` process itself (`os.getpgrp()`) is among the named groups (for example a job
started with `&` from the same non-interactive shell that runs `gov resources --backstop`, so both share one group):

1. at start, the start log line (L6) carries `; own group <g> named: paused last` at its end;
2. on a trip, every other live named group is paused first (SIGSTOP, in the order named); then the TRIP log line (L6) and
   the one inbox item (L7) are written, the item's `paused:` line listing every paused group the own group included,
   with its `resume:` and `stop:` lines, and one more line `note: the backstop's own group <g> is paused last; resuming
   it resumes the backstop, which then ends`; then, last of all, SIGSTOP to the own group (which stops `gov` too);
3. so while everything is stopped, every named group is stopped and the TRIP line and the item exist; after
   `kill -CONT -- -<g>` the command ends: exit 0, `tripped: true`, `paused` holding every paused group (the own one
   included), as L8.

When the own group is not named, nothing changes. Nothing else is signalled; no group is refused for being the own one.

## The failing output (6 failed, 1 passed; the assertion lines)
```
FAILED test_w2_157_own_group.py::test_s4_the_own_group_is_paused_last_after_every_other_group_the_trip_line_and_the_item[first]
  AssertionError: gov is stopped (the own group 2532233 was paused) but the named group 2532229 is still not paused (state S): the own group was paused before the other groups
FAILED ...[middle]
  AssertionError: gov is stopped (the own group 2532552 was paused) but the named group 2532545 is still not paused (state S): the own group was paused before the other groups
FAILED ...[last]
  AssertionError: gov is stopped but the log holds 0 TRIP lines, not one (the TRIP line is written before the own group is paused): ['2026-11-12 06:41:09 start: limit 15872 MiB; every 0.1 s; groups 2532910 2532911 2532913; skipped (ended) none; embedders none']
FAILED test_w2_157_own_group.py::test_s4_a_job_sharing_the_backstops_group_and_a_second_group_named_after_it_are_both_paused
  AssertionError: the second group 2532916 kept running although gov is stopped (state S): the SIGSTOP to the shared group froze the backstop before it paused the second group
FAILED test_w2_157_own_group.py::test_s1_the_own_group_named_alone_is_paused_after_the_trip_line_and_the_item
  AssertionError: gov is stopped but the log holds 0 TRIP lines, not one (the TRIP line is written before the own group is paused): ['2026-11-12 06:41:14 start: limit 15872 MiB; every 0.1 s; groups 2533170; skipped (ended) none; embedders none']
FAILED test_w2_157_own_group.py::test_s4_a_group_that_has_ended_is_skipped_beside_the_own_group_which_is_still_paused_last
  AssertionError: gov is stopped (the own group 2533178 was paused) but the named group 2533177 is still not paused (state S): the own group was paused before the other groups
PASSED test_w2_157_own_group.py::test_s4_when_the_own_group_is_not_named_it_is_not_paused_and_there_is_no_note
```
The tests run `gov` inside a new session whose group is named (e.g. `setsid sh -c '<job> & exec python3 -m
gov.cli.main resources --backstop <that group> <another group> ...'`), then check every group's state and the log and
inbox item while gov is stopped, then `kill -CONT -- -<own group>` and read the envelope.

## The documentation addition (review finding FR-5)
In the evidence's operator step for this machine, one sentence: when the query server runs on the CPU
(`embedding_servers.query.device` `cpu`, a supported fallback), leave its entry (port 11435) out of
`gpu_backstop_embedders`, since its `size_vram` is then 0 and every poll would trip.

## Safety
Your unit tests plant their own process groups only (children started with `start_new_session=True` or `setsid`) and
stand-ins under `tmp_path`; never signal a process you did not start; never run `--backstop` against a real group, the
real GPU or the real HOME's gate.json. A unit test that pauses the backstop's own group must run gov in a child
session of its own, never in pytest's group.

## Rules
- Unit tests first in `tests/unit/resources/test_w2_157_backstop.py` that fail on the present code, then the fix.
- Keep W2-20's tests green: run `tests/unit/resources` and `tests/acceptance/W2-20` before the commit, in the form
  `env HOME=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-157/src python3 -m pytest <folder> -q -p no:cacheprovider
  -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
- Add to `docs/changes/W2-157-evidence.md`: L5b as applied with its unit tests, and the FR-5 sentence.
- Anything longer than one line goes in a script file under `$TMPDIR`, run with `bash <file>`. Literal paths only. No
  merge, no push, no edit outside your paths. A refused call is reported, never worked around. For a new file,
  `git add <path>` before `git commit -- <paths>`.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: engineer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1073" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of tests/unit/resources and tests/acceptance/W2-20)
/ tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:`
(hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
