# Brief: independent test designer, W2-184 (DAEO-6f0s), batch td-6 (the CLI options, P-W2-184-2 (a))

You are a fresh independent test designer for DAEO-6f0s (W2-184). Batches td-1 to td-5 are merged
(`tests/acceptance/W2-184/`, 472 cases). The CTO decided P-W2-184-2 (a) (the ticket's second-last paragraph):
`src/gov/launch/command.py` joins the ticket's paths so that `gov launch` itself carries `--reason`, `--trial` and
`--owner-named` before `--`. Until now the cases that need these options call `gov.launch.launcher.launch(...)` with
keyword arguments in a child process (interface 7.2; `w2_184_support.py`'s `launch`). Write the cases for the
described behaviour (interface **7.2a**, below). Do not read the engineer's work (`src/gov/launch/`): test the
behaviour as described. You are launched on Opus because the ticket is promoted (DEC-1120 (3)).

Context: /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-td-5.md (JSON: the ticket text and its
sources, from `gov context`).

## The behaviour (7.2a)
Drive the real `gov launch` command line (as W2-60a's and your folder's CLI-driven cases do, with the stand-in CLI),
not the keyword call. At least:
1. **Each option through the CLI gives the keyword case's result.** `--owner-named DEC-<n>`: a FULL ticket's auditor
   launch that repeats a recorded setting is accepted and records `owner_named`; without it, refused (exit 1, no
   record, no session). `--trial <id>`: a planted trial record admits its model after `--` and the record holds the
   trial id. `--reason <text>`: a max effort of the launch's own choice is accepted and recorded with the reason;
   without it, refused.
2. **The forms are checked through the CLI too:** a malformed `--owner-named` (not `DEC-<number>`), a `--trial` id
   with a character outside letters, digits, `.`, `_`, `-`, and an empty `--reason` each refuse with exit 1 before
   any record or session.
3. **Before `--` only:** `--owner-named DEC-<n>` written after `--` is not taken as the option (the passthrough's own
   checks judge it, as before; no `owner_named` recorded).
4. **The usage line names the three options** (`gov launch --help` or the usage on a bad call).
5. **Unchanged:** `--plan` prints the role file's default line as before; a launch with none of the options behaves
   as the existing cases say.
Name, per case, what it fails on at the current head (the CLI has no such options: argparse exits 2 on an unknown
option).

Put the cases in a new file `tests/acceptance/W2-184/test_w2_184_cli_options.py` (support additions in
`w2_184_support.py` if needed; keep every existing case). Add a line to the folder's `README.md`.

**Do not open, list or read anything under `fixtures/evaluation/` or any `hidden` folder.**

## Where you write
- Your tree: /home/usain/gov-os-worktrees/W2-184-tests, branch w2/W2-184-tests (at 42d0867d3). Write only
  `tests/acceptance/W2-184/` (and scratch under your tree's `.gov-runtime/scratch/`).

## How to run tests (every pytest through heavy_slot.sh)
```
env HOME=/home/usain/gov-os-worktrees/W2-184-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Use the session's own `$TMPDIR`. No `gov retrieve`, no `gov context`: Read and Grep, and once more in other words.
Report the new cases' red/green at your tree's head, with the failing lines of the red ones.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184-tests commit -m "W2-184 (DAEO-6f0s) tests: gov launch carries --reason, --trial and --owner-named before -- (P-W2-184-2 (a), interface 7.2a)" --trailer "Task: DAEO-6f0s" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1120, DEC-1010" -- tests/acceptance/W2-184
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments)

