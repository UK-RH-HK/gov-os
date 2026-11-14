You are a fresh engineer. Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37` on branch `w2/W2-37`, and write only two files: `src/gov/check/commands.py` and `tests/conftest.py`. This is P-7 (a) of DEC-812 item 6: "W2-37's paths gain `src/gov/check/commands.py` (the `RECORDED_GOV_COMMANDS` line that records `impact` only)", and the CTO's conftest line under DEC-1156 (7): `_CBM_SUITES` gains `"W2-37"`, so W2-37's code-graph cases run with the code-index tool on PATH. `gov impact` is built (`src/gov/impact/command.py`).

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37`, `w2/W2-37`); `git rev-parse HEAD` (expect prefix `f141d6366`); `git status --short` empty. If anything differs, stop and say so.
- Every pytest runs through the heavy slot, with a TMPDIR outside the repository and outside ~/gov-os-runs (your sandbox's own TMPDIR if `/tmp` is read-only), for example:
  `env TMPDIR=/tmp/gov-os-w237-eng6 PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/check tests/unit/accept/test_w2_96_run2.py tests/unit/session_watch/test_route.py tests/acceptance/W1-26/test_w1_26_recorded_commands.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first). A slot wait or a memory/CPU/disk gate refusal is a wait. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/`. No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; once more in different words if the first does not answer.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What to change (nothing else)
1. `src/gov/check/commands.py`: one new line after the `wait` line (:20), in the same form: `RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("impact",)` with a trailing comment naming W2-37 and DEC-812 item 6 (for example `# impact (W2-37, DEC-812 item 6, P-7 (a)): the change's impact query`). Keep the line within the file's existing width (about 120 columns); if the comment does not fit, put it on the line above, as the `brief`/`links`/`plan` line does. Do not change `VERSION` or any other line.
2. `tests/conftest.py`: the `_CBM_SUITES` frozenset (:324) gains `"W2-37"` (keep the existing members and their order; add it after `"W2-92"`). Nothing else in the file.

## Check
- `git diff --stat` shows 2 files, 2 insertions and 1 deletion in all (or 3 insertions if the comment is on its own line); `git diff` shows only these lines.
- Run the pytest example above: every case green except any you can show was red before your change (run it once on the clean tree first if you need the comparison). `tests/acceptance/W1-26/test_w1_26_recorded_commands.py` reads W1-07's lists, which a test designer is changing on another branch; on this branch it has no `impact` case yet: that is expected.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m gov.check.commands --help` or the module's own entry, if it has one, still runs (report what you ran).

## Commit (one commit, the two files only)
    git commit -m "W2-37: commands.py records impact (DEC-812 item 6, P-7 (a)); _CBM_SUITES gains W2-37 (DEC-1156 (7))" --trailer "Task: DAEO-6n5k" --trailer "Role: engineer" --trailer "Implements: CAP-33.g, DEC-167" -- src/gov/check/commands.py tests/conftest.py
Then show `git log -1 --format='%H%n%B'`, `git status --short`, and `git show HEAD` (the diff verbatim in your return).

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` the diff verbatim; in `tests:` the counts and any red with its failure line. Then `guard_refusals:` (none, or each refusal's command form and reason).

## The ticket's context (gov context, built by the lead outside the sandbox)
