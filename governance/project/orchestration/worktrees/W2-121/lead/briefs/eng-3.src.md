# Brief eng-3: engineer, fix round, for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You fix the independent review's round-1 findings F-1 to F-4 and F-6 in `gov dispatch` (ticket DAEO-cb2b, W2-121
part a). The code is yours from the first round: `src/gov/dispatch/` (read `src/gov/dispatch/__init__.py`'s docstring
first: the KPI map; the findings sit mostly in `returns.py` and `config.py`). You never read the acceptance tests
(`tests/acceptance/W2-121/`; the guard refuses them); a test designer is writing new ones from the same readings now.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121 |
| branch | w2/W2-121 |
| allowed paths | src/gov/dispatch/**, tests/unit/dispatch/** |
| ticket (KPI S4, S5, S9; the Interface section; the sections P-W2-121-5 to P-W2-121-7 at its end) | /home/usain/gov-os-worktrees/W2-121/.tickets/DAEO-cb2b.md |
| the round-1 interface readings (still hold) | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/interface-1.md |
| **the fix round's readings (build to these, word for word)** | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/interface-2.md |
| the context bundle (the ticket and its sources) | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/ctx-eng-3.md |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The findings (the reviewer's words, shortened; the fix is interface-2.md's line of the same id)
- **F-1 (blocking, S4), returns.py:109 and :146.** Read a return item (moved to `inbox/read/`), then delete it: the next
  pass writes `<log>.return.txt` into `inbox/` again as unread. The same for never-ran items (`never-ran.txt` is written
  but never read). The record that an item was written must outlive the item.
- **F-2 (blocking, S4), returns.py:166.** `escalated.txt` is written before the notifier runs: a notifier that fails once
  (exit != 0, or a timeout, which also marks every other escalation due that pass as done) loses the escalation for
  good, and the failure shows only in that one pass's status. Record only on exit 0; retry no sooner than
  `notify_retry_s` (new key, default 600); show the failure in every pass while it lasts; a timeout ends that pass's
  escalations without recording the rest.
- **F-3 (major, S5/S4), returns.py:165, config.py:133.** `notifier_command` optional at load, but a missing one raises a
  configuration error mid-pass, after a start: every pass exits 2 with `PASS FAILED` while sessions keep being started,
  and the status hides them. Make it required at load (exit 2 naming the key, nothing started).
- **F-4 (major, S9), returns.py:85.** A `files_changed` path that exists only untracked in the worktree counts as
  resolved. An untracked, not-ignored path (or one only staged) is unresolved; an ignored one that exists resolves.
- **F-6 (minor, S9), returns.py:128.** A hung git while resolving writes every id and path as `unresolved:` into a
  permanent item. Write them as `unchecked: could not be checked (<the failure>): <names>` instead, no `unresolved:`
  line for them.

## Rules
- Test first: for each finding a unit test in tests/unit/dispatch/ that plants the reviewer's case, seen red, then the
  fix. Update the unit tests the readings change (a missing `notifier_command` is now exit 2 at load).
- Keep the module docstrings (`__init__.py`'s KPI map, `returns.py`'s) true to the new behaviour, and `notify_retry_s`
  in `config.py` with the other keys (no default may name this repository's branches, paths or ticket ids: S6).
- Change nothing else; no refactor beyond the findings.
- Every pytest run goes through the heavy-slot gate, one folder per run, TMPDIR outside the repository:
  `env HOME=/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-121/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/dispatch -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  End with the whole unit folder green.
- Commit in batches (one per finding or two is fine), your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: engineer" --trailer "Implements: DEC-1007, DEC-1014" -- src/gov/dispatch tests/unit/dispatch`
- One-line commands only (the Write tool is refused under .gov-runtime/scratch/ in the sandbox; use it for your own
  paths). Never touch .gov-runtime/scratch/lead/.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (each finding: what changed, file:line) / files_changed / evidence (the pytest summary line) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
