# Brief td-3: independent test designer for DAEO-p8tv (W2-172), one revision batch, profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-p8tv (W2-172). Your suite `tests/acceptance/W2-172/` is
merged, green and reviewed at 0c16d8afb0b5. The merge queue ejected that head at 21:19 on 2026-11-12: every W2-172
acceptance case failed `conftest.py:49`, the path-hygiene precondition `clean_paths`, because the queue's clone lives at
`/home/usain/gov-os-runs/W2-00/merge-queue/warm/merged`, so `W.SRC` (the repository's own `src/`, which no test prints)
holds `runs/` (`gov-os-runs/` matches the folder word `runs/`).

Your task: one batch that revises the hygiene check so it no longer refuses the repository's own location (`W.SRC`, and
the interpreter path `sys.executable`), while it still refuses any path the test's world builds and that can be printed
(`world.sets`, `world.repo`, `world.link`, `world.stub`, `world.gov`, `world.claude`, `world.gate_stub`, `world.shim`)
holding a sets-root word (`W.FORBIDDEN`). Nothing else changes: no case weakened, no KPI assertion dropped.

Check every hygiene site, not only `conftest.clean_paths`:
- `conftest.py:42-49` (`clean_paths`).
- `test_w2_172_s1_cycle.py:82` (its own loop over world paths; keep it, it names no repository path).
- the line greps (`test_w2_172_s1_cycle.py:86-89`, `test_w2_172_f1_f4_access.py:40-47` and `:153`) and anything else
  that greps printed lines or child argv for `W.FORBIDDEN`. Item 2 of the ticket's Interface fixes the step lines'
  first word as `<py>` (`sys.executable`). If the interpreter's own path could hold a word, a grep must not fail on that
  exact token alone; any other occurrence of a word must still fail. Decide how (e.g. compare the argv after its first
  element, or remove only the exact `sys.executable` token), and say how in the docstring.
- `README.md`'s path-hygiene paragraph (line ~53): state the new rule.

Every changed test or helper gets, in its docstring or comment, the line
`Rewrite-Reason: the merge queue's clone path (21:19 ejection)`, and the commit message names it too.

You never read the engineer's work on this ticket (`src/gov/memaudit/` driver files this ticket added,
`memaudit_cron.sh`, `tests/unit/memaudit/`); you need none of it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-172-tests |
| branch | w2/W2-172-tests (from 0c16d8afb0b5) |
| your allowed paths | tests/acceptance/W2-172/** |
| the ticket (KPI lines and the Interface at its end) | /home/usain/gov-os-worktrees/W2-172-tests/.tickets/DAEO-p8tv.md (else /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-p8tv.md, read-only) |

Search with the Read, Grep and Glob tools; search again once in different words if the first does not answer
(DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the real `~/gov-os-eval`, `~/gov-os-runs`, a
hidden half or the crontab.

## Prove it (both green; quote both summary lines)
Every pytest through heavy_slot.sh. A heavy-slot or resource refusal is a wait: run again when it opens.
Set up once: `mkdir -p /tmp/gov-w2-172-td3/pt /home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/empty-home`

1. In your tree (cwd /home/usain/gov-os-worktrees/W2-172-tests):
   `TMPDIR=/tmp/gov-w2-172-td3/pt bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172-tests/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
2. From a clone under a folder named `runs` (as the queue's): after your commit,
   `git clone -q /home/usain/gov-os-worktrees/W2-172-tests /tmp/gov-w2-172-td3/gov-os-runs/x/clone` (the branch
   w2/W2-172-tests checked out), then the same pytest line with cwd, `PYTHONPATH` and the test folder all in the clone
   (`HOME` may stay the empty-home above). Before your fix this run fails at `conftest.py:49`; show that once too (run
   it in a clone of 0c16d8afb0b5 at `/tmp/gov-w2-172-td3/gov-os-runs/y/clone`, `-x` is enough).

## Rules
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only, one commit:
  `git commit -m "W2-172 (DAEO-p8tv): path hygiene judges the world's paths, not the repository's own location (Rewrite-Reason: the merge queue's clone path (21:19 ejection))" --trailer "Task: DAEO-p8tv" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073" -- tests/acceptance/W2-172`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed (each changed case or helper) / evidence (the three pytest summary lines: your tree, the
clone after, the clone before) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form |
the hook's reason | true or false-positive).
