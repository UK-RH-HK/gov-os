# Brief: engineer (second session), W2-116 (DAEO-f58b) pass 2b: finish S2 and make the acceptance cases pass

You are the engineer for ticket DAEO-f58b (W2-116), profile STANDARD, taking over from a first engineer session
that stopped at a lead's hold (a lead fault, not the engineer's). Nothing of its work is lost. Read its checkpoint first:
/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/eng/checkpoint.txt, and its notes in the same folder.

## The state of the tree (w2/W2-116, /home/usain/gov-os-worktrees/W2-116; you are its one writer)
- Committed: R2-F3 (09247e423: `src/gov/retrieval/retrieve.py`, `tests/unit/retrieval/test_w2_116_token_mark.py`).
- Merged by the lead: the independent test designer's acceptance cases (20d6a21f5), in `tests/acceptance/W2-116/`:
  `test_w2_116_s2_when_due.py`, `test_w2_116_s2_config.py`, `test_w2_116_s2_status.py`,
  `test_w2_116_r2f3_continuation.py`, `w2_116_s2_support.py`, and a README section "Pass 2b". They are read-only to
  you: never edit `tests/acceptance/`. A case you believe contradicts the interface below: build to the interface,
  and name the case (file:line) and the contradiction in `unresolved`.
- Uncommitted, the first session's work (yours now): `src/gov/rebuild/integration.py`, `src/gov/rebuild/command.py`,
  `src/gov/status/command.py`, `src/gov/status/integration_store.py` (new), `governance/project/rebuild.yaml`,
  `tests/unit/rebuild/test_w2_116_when_due.py` (new), `tests/unit/status/test_w2_116_integration_store.py` (new).
  `git diff` and read them before changing anything.

## What to do
1. Apply the first session's PENDING list (checkpoint): the `integration.now()` offset fix (an ISO `GOV_NOW` with an
   offset keeps that offset's wall clock; only a naive one is local time), and `monkeypatch.delenv("GOV_NOW",
   raising=False)` in its unit test.
2. **The lead settles the first session's interface gap (DEC-1052):** the record keeps only the last refresh, so after
   an `after_nightly` refresh at 10:00 and a `second` refresh at 18:00, the literal rule would make one more
   `after_nightly` refresh due. Not so: `<link>.refresh.json` also carries `after_nightly_at`, the `at` of the last
   refresh with reason `after_nightly` (written by that refresh, carried over unchanged by a `second` refresh), and the
   rule "no scheduled refresh with reason `after_nightly` has an `at` on today's date" reads it. The acceptance case
   `test_s2_success_second_is_due_once_after_its_time_and_brings_the_store_to_the_branch_head` expects `not_due` on the
   tick after the second refresh. The extra key is allowed: the interface lists the fields the record must have.
3. The other choices the first session made (in its return): the command line's `--integration <branch>` is what is
   built and `gov status` reads the config's `branch`; an empty `GOV_NOW` is invalid; a missing `after_nightly` block is
   key `integration_refresh.after_nightly.latest` with value null; an `after_nightly` that is not a map is key
   `integration_refresh.after_nightly`; a verdict file stamped after `now` does not count yet; a record with no readable
   `at` is no record. The lead accepts them; keep them unless an acceptance case shows otherwise (then name it).
4. Make the new unit files pass, then the acceptance cases in `tests/acceptance/W2-116/` (all of them: pass 1's must
   stay green), then `tests/unit/rebuild`, `tests/unit/status`, `tests/unit/retrieval`, `tests/unit/retrieve`.
5. Commit in batches: S2 (`integration.py`, `command.py`, `rebuild.yaml`, the when-due unit test) together, so the
   `integration_refresh` line lands with the code that reads it; then the status part (`src/gov/status/**`, its unit
   test); then the evidence.
6. The evidence record `docs/changes/W2-116-evidence.md`: add a "Pass 2b" section: what was built, the due rules, the
   record (with `after_nightly_at`), the stale rule and R2-F3's mark, each against the interface; the choices in item 3;
   the commands run and their counts.

## Known and others' reds (name, never fix)
- `tests/unit/status/test_status.py:172` (`test_a_status_with_a_part_not_read_names_every_such_place`) asserts the
  exact `PARTS` tuple and `not_read == []`; the interface's new part turns it red. It is outside the ticket's paths:
  name it with the output line; the CTO fixes it (DEC-1156 (7)).
- The three `test_cto_safety_nets.py` live-inbox cases and `test_w2_23_space.py:94`.
- Any other ticket's case red on this branch: name it with file:line.

## Paths you may write (this pass)
`src/gov/rebuild/integration.py`, `src/gov/rebuild/command.py`, `src/gov/status/**`, `src/gov/retrieval/retrieve.py`,
`src/gov/retrieve/command.py`, `src/gov/launch/store.py`, `governance/project/rebuild.yaml`,
`docs/changes/W2-116-evidence.md`, `tests/unit/rebuild/test_w2_116*`, `tests/unit/status/test_w2_116*`,
`tests/unit/retrieval/test_w2_116*`. Scratch: /home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/eng/
(the first session found the Write tool refused there once; a plain heredoc through Bash worked).

## How to run pytest (every run)
```
env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
`/tmp` is read-only in the sandbox: keep the sandbox's own `TMPDIR` (outside the repository). A whole-folder run adds
`-m "not local_only" -k "not real and not green_here and not time_limit"` and
`HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home`. Put a multi-line command in a script under
your scratch and run it with `bash`; run a long one with the tool's own background mode, never a nested `( … ) &`. A
resource gate's refusal is a wait (DEC-1146). The `heavy-slot-waits.jsonl: Read-only file system` line is harmless.
Never open the evaluation sets' root or any hidden or memory-verdict folder. No `gov retrieve` or `gov context` in the
sandbox: search with Read and Grep, and once more in other words if the first does not answer (DEC-1065).

## Commit
```
git -C /home/usain/gov-os-worktrees/W2-116 commit -m "<subject>" --trailer "Task: DAEO-f58b" --trailer "Role: engineer" --trailer "Implements: DEC-983, DEC-982, DEC-966, DEC-963, DEC-1087" -- <paths>
```
`Implements:` only ids from the ticket's `sources:`. There is no hold this time: the lead will not touch the tree until
you return.

## Rules
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it (DEC-1142 (9)).
- Keep the checkpoint in your scratch (STATE / HEAD / NEXT), rewritten at each commit.
- Leave the tree with nothing uncommitted of yours when you return (`git status --short` empty but for ignored files).

## Return (your last message; only it is read, so put everything in it)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES, ESCALATION) /
work_completed / files_changed / evidence (each suite's counts) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` with hash12 and subject.

