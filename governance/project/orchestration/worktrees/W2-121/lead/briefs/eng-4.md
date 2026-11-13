# Brief eng-4: engineer (fix round, one red) for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You fix one acceptance failure in `gov dispatch` (ticket DAEO-cb2b, W2-121 part a). The code is in
`src/gov/dispatch/` (read `src/gov/dispatch/__init__.py`'s docstring first: the KPI map; the inbox items are in
`returns.py` and `state.py`). You never read the acceptance tests (tests/acceptance/W2-121/; the guard refuses them);
you get their failing output only, below.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121 |
| branch | w2/W2-121 |
| allowed paths | src/gov/dispatch/**, tests/unit/dispatch/** |
| ticket (KPI S4; the section P-W2-121-7 at its end) | /home/usain/gov-os-worktrees/W2-121/.tickets/DAEO-cb2b.md |

## The rule the failing case checks (the lead's reading F-1, given to the engineer and the test designer alike)
An inbox item (`<log>.return.txt`, `<log>.never-ran.txt`, `<log>.owner.txt`), once written, is never written again, as
unread or at all, even after it is deleted from `inbox/` or from `inbox/read/`. The record that it was written lives in
the state folder outside `inbox/` and outlives the item. **An item already in `inbox/` or `inbox/read/` also counts as
written (a state folder from before this record)**: so an item a pass finds there, which the dispatcher did not write
itself (a state folder from before the record existed), must be recorded as written when a pass sees it, so that its
later deletion does not make a pass write it again.

## The failing output (250 of 251 acceptance and unit cases pass; this one fails)
```
    def test_s4_an_item_already_in_the_inbox_counts_as_written_even_after_it_is_deleted(project):
        p = project
        entry = p.add_ticket(901)
        p.finish_session(entry)          # the session's logs/<log> and logs/<log>.exit exist; it is in started.txt
        planted = p.plant_item(f"{entry.log}.return.txt", entry.log, entry.w2, status="DONE")   # written by the test, not a pass
        passes(p, 2)                     # two `gov dispatch tick` passes
        assert [i.path for i in p.items()] == [planted], [i.text for i in p.items()]    # passes
        planted.unlink()
        passes(p, 2)
>       assert p.all_items() == []       # inbox/ and inbox/read/
E       AssertionError: Left contains one more item: Item(path=.../.gov-runtime/dispatch/inbox/W2-901-A5-run.json.return.txt,
E         'log: W2-901-A5-run.json\nW2: W2-901\nstatus: DONE\nkind: return\nticket: DAEO-a901\nexit: 0\ntime: 2026-11-12T06:29:31+00:00\n')
tests/acceptance/W2-121/test_s4_items_once_ever.py:77: AssertionError
FAILED tests/acceptance/W2-121/test_s4_items_once_ever.py::test_s4_an_item_already_in_the_inbox_counts_as_written_even_after_it_is_deleted
```

## Rules
- Test first: add a unit test in tests/unit/dispatch/ that plants an item by hand (not through a pass) in `inbox/`, and
  another in `inbox/read/`, runs a pass, deletes each, runs passes, and asserts nothing is written again; see it red,
  then fix. Keep every other unit test green.
- Then run the whole unit folder through the heavy-slot gate, TMPDIR outside the repository:
  `env HOME=/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-121/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/dispatch -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- Change nothing else. Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: engineer" --trailer "Implements: DEC-1007" -- src/gov/dispatch tests/unit/dispatch`
- One-line commands only (the Write tool is refused under .gov-runtime/scratch/ in the sandbox). Never touch
  .gov-runtime/scratch/lead/. Leave no untracked folder (e.g. pytest-of-usain/) in the tree.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
