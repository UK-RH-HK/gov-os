## Walls (hard; break one and stop)
- **Never open, list, grep or print anything under the evaluation sets' root (`~/gov-os-eval`) or any `hidden/` folder**, in this repository or anywhere. No real hidden half exists in git; if a search would cross one, name the folder the search starts at so it does not. Every hidden half your work touches is a **planted stand-in you write in your sandbox's `$TMPDIR`** (or a pytest `tmp_path`), never in the repository.
- **Never quote a question or an answer** (stand-in or otherwise) in a commit message, your return, a log or a note.
- Never write `fixtures/evaluation/adoption-proving-ground/hidden/**` (the path is in the ticket's list for the delivery, not for you).
- W2-81's files other than `tests/acceptance/W2-81/w2_81_run.py` and `tests/acceptance/W2-81/test_w2_81_runner.py` are read-only (DEC-1010 item 4, DEC-1144 (6)).
- Reads are open otherwise (DEC-820): the whole repository, git history. Never read the counterpart's work on this ticket (see your section).

## Running tests
- Every pytest through the slot and with a TMPDIR outside the repository (your sandbox's `$TMPDIR`):
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR="$TMPDIR" PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<your tree>/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (read the first lines of `heavy_slot.sh` for its exact form if this one is refused). A resource gate's refusal is a wait: run it again later, it does not count as a refusal (DEC-1146).
- A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`. **So no test name of yours may contain `real`, `green_here` or `time_limit`** unless it is meant to be deselected there.
- Anything longer than one line goes in a script file under `<your tree>/.gov-runtime/scratch/` (or `$TMPDIR`), run with `bash <file>` or `python3 <file>`. Write files with the Write and Edit tools and absolute paths. Waits by pid only; no hand-written sleep loops.
- No `gov retrieve` and no `gov context` in the sandbox: search with Read and Grep, and search again once in other words (DEC-1065).
- A session refused twice for the same action stops and says so; never work around a refusal by another tool or form (DEC-1142 (9)). No merge inside the sandbox. No new ticket.

## Commit (your paths only, in your tree)
```
git commit -m "<subject: what changed, never a question or answer>" --trailer "Task: DAEO-6y0x" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-941, DEC-828, DEC-820, DEC-845, DEC-873, DEC-1010" -- <paths>
```
An id you need that is not in that list (DEC-1143, DEC-1144 ...) goes in your return's `discoveries`, never in `Implements:`.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
then `commits: <hash12> <subject> | trailers as committed`, and `guard_refusals: none | - <time> | <form> | <reason as the hook gave it> | true or false-positive`.
`status` is DONE, PACKAGES or ESCALATION. `tests` gives the counts (passed/failed) of each run you made and the command.
