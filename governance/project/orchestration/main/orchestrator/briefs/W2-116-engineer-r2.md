# W2-116 — the engineer's ride-along fixes before window 4 (DAEO-f58b)

You are the engineer for **W2-116**, resumed. The review (`.gov-runtime/scratch/orchestrator/reviews/w2-116.md`; read
F1 to F8 with their probes) is READY. The CTO has taken its small fixes to ride along before window 4 puts the store
live (DEC-802). Integrate is merged into your branch: it holds `rebuild.yaml`'s `integration_store`.

## Fix, with a unit test each
- **F1:** read the branch's head **after** taking the store's lock, not before, so a refresh that waited never moves
  the link back to an older head. A refresh that finds the ready half already at the head does nothing.
- **F2:** resolve the store's root **once per search** (in `_store_root`, or wherever `GOV_STORE` is read): read the
  link's target once, and use that resolved path for every facet. A search that spans a switch then reads one half
  only.
- **F4:** `gov launch` reads the store's place from the **main repository's** `governance/project/rebuild.yaml` (the
  common git directory's main worktree), not the launch tree's. A worktree branched before the line existed still gets
  `GOV_STORE`.
- **F8:** a seed from a base **ahead of** the tree is not labelled `behind`. Name the relation as it is (`behind`,
  `ahead`, or `diverged`), with the base's head.
- **F6 (code part):** each log line of the refresh starts with its date and time.

## Not yours (the CTO's)
- **F5 and F6's slot order:** the hook line in window 4's ACT. Restate the hook in your evidence with
  `env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u GOV_REBUILD_LOCK` before the command, and the store's lock taken
  before the heavy slot. Do not install it.
- **F3 and F7:** rows.

## Tests and rules
As in your first brief:
- your unit tests;
- every run through the heavy slot;
- `gov accept W2-116` with `HOME=/home/usain`;
- then `tests/unit/rebuild`, `tests/unit/launch` and `tests/unit/retrieve`, with `GOV_TESTS_OPTIN=lifted,breadth`;
- update the evidence record.

Never read `tests/acceptance/W2-116/`. The hidden-half rule. DEC-1080 (Read and Grep tools; one simple command per Bash
call; no `cd … &&`; no `git -C`; one line before a command that will ask). Do not merge integrate.

Commit with `--trailer "Task: DAEO-f58b" --trailer "Implements: DEC-1087" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with the diff's size, the new unit tests, `gov accept`'s counts, the regression counts and
the restated hook line.
