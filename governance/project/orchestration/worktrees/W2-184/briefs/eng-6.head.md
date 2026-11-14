# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-6 (the CLI options, P-W2-184-2 (a))

You are a fresh engineer for DAEO-6f0s (W2-184), launched on Opus because the ticket is promoted (DEC-1120 (3)). The
head is 0a4ce21fd; the full verification at 42d0867d3 (one merge of test files before it) was green, 7,992 tests.
New acceptance cases are red; make them green within the ticket's paths. The behaviour they test is interface
**7.2a** (below; the CTO's P-W2-184-2 (a) put `src/gov/launch/command.py` in the ticket's paths); the rest of the
interface is unchanged and its cases are green.

## The failing output (all you are given beyond the interface)
`tests/acceptance/W2-184/test_w2_184_cli_options.py`: 28 failed, 7 passed at 0a4ce21fd.
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-6-short.txt (the assertion lines, counted, and
  the failing case names);
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-6.txt (the full `--tb=line -rf` output).

Context: /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-eng-5.md (JSON: the ticket and its
sources, from `gov context`).

Never write under `tests/acceptance/` (the independent test designer's), and never open anything under
`fixtures/evaluation/` or a `hidden` folder.

## What to deliver
- The change in `src/gov/launch/command.py` (and only the ticket's other paths if needed).
- Unit cases in `tests/unit/launch/test_w2_184_*.py` for the parser (the three options, the usage text).
- One paragraph in `docs/changes/W2-184-CIT-E.md`: the CTO's P-W2-184-2 (a), what changed (interface 7.2 is now 7.2a).

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only `src/gov/launch/command.py`,
  `src/gov/launch/launcher.py`, `src/gov/launch/role.py`, `src/gov/launch/record.py`, `src/gov/launch/criticality.py`,
  `governance/project/criticality.yaml`, `tests/unit/launch/test_w2_184_*.py`, `docs/changes/W2-184-CIT-E.md`, and
  scratch under `.gov-runtime/scratch/eng/` (use file names no earlier session there could have written).

## How to run tests (every pytest through heavy_slot.sh; in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Before your last commit, green: `tests/unit/launch tests/unit/cli tests/acceptance/W2-184 tests/acceptance/W2-60a
tests/acceptance/W1-46 tests/acceptance/W2-20` (leave out any of these folders that does not exist), and
`gov accept W2-184 --root /home/usain/gov-os-worktrees/W2-184` if it runs in your session. Use the session's own
`$TMPDIR`. No `gov retrieve`, no `gov context`: Read and Grep, and once more in other words.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): gov launch carries --reason, --trial and --owner-named before -- (P-W2-184-2 (a), interface 7.2a)" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1120, DEC-1010" -- <your paths>
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments)

