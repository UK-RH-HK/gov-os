# Brief: engineer, W2-42a (DAEO-03ub), R4 (blob revision-colon-paths judged as reads) and R5 (the guard's judge never raises) (DEC-1157 (12), DEC-1180 (4))

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh engineer.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head {HEAD}.
Your paths: src/gov/guard/reads.py (the fix); src/gov/guard/decide.py or src/gov/guard/bash_writes.py only if a crash
sits there; tests/unit/guard/test_w2_42a* for unit cases of what you change; one short paragraph in
docs/changes/W2-42a-evidence.md. Nothing else changes. Never tests/acceptance/ (the test designer's).
Commit with (all trailers in ONE final paragraph; no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1157, DEC-1180, DEC-1128, DEC-1133" -- <your paths>`

## What to make pass
The acceptance cases below fail on {HEAD}; their failing output is all you are given. Make them pass by changing the
product's guard, under these rules:
- A revision-colon-path naming a blob (`git diff REV:PATH REV:PATH`, one or both sides; `git show REV:PATH`) is read as
  its path, under the read rules that path names (the hidden part, secrets, held-out, the counterpart's work): a path
  the role may read is allowed; one it may not is refused by its rule. A revision word that names no commit, tree or
  blob is refused, by a ruled refusal (a refusal text naming why), not an exception.
- A crash becomes a ruled decision: no Bash or tool input makes the judge (`reads._Judge.tool`/`command`, `decide()`,
  the parser `decide.py`/`bash_writes.py` reaches) raise inside itself. Fix each crash at its cause (a length check, a
  guarded index), not by wrapping the judge in a blanket `except` that turns every fault into a refusal or an allow.
- The error path itself stays for genuine faults (git missing, an unreadable path map, the deadline): they still fail
  closed.
- Nothing refused today that writes into a walled path (tests/acceptance/, outside a reviewer's record) or reads a
  refused one (secrets, the hidden part, held-out material) becomes allowed. Fail closed when in doubt.
Also run the whole acceptance folder tests/acceptance/W2-42a and tests/unit/guard: nothing green there may turn red.

## How to run (pytest only through the heavy slot; one line each; `mkdir -p $TMPDIR/empty-home` first)
`cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest {FILES} -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Whole folders: the same line with `tests/acceptance/W2-42a tests/unit/guard -n auto -m "not local_only" -k "not real and not green_here and not time_limit"`.
The heavy slot may queue: that is a wait. Anything longer than one line goes in a script file under `$TMPDIR`, run
with bash or python3. Use the sandbox's own `$TMPDIR`; never write outside it and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit hash(es) (12), the
counts of the failing files and of the two whole folders after your fix; in `work_completed`: each crash you fixed
as file:function and the change, and how the blob read is judged (the functions changed: the live hook's ACT copies
them). A refusal twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it.
Search with Read and Grep only (no gov retrieve, no gov context in the sandbox); search again once, in other words.
Never open the evaluation sets' root or any hidden or memory-verdict folder. No merge in the sandbox. A resource
gate's refusal is a wait.

## The failing output (on {HEAD})

```
