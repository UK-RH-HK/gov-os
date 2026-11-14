# Brief: engineer, DAEO-drhj (W2-104), run 4 — `skilleval` back in `commands.py`, beside `impact`

You are a fresh engineer. Ticket: `DAEO-drhj` (W2-104), profile STANDARD, class C2. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-104` on branch `w2/W2-104`. The ticket's harness (`gov skilleval`, in
`src/gov/skilleval/`) is built, verified and committed. Your lead has merged `w2/integrate` (head `72c6def8871a`, which
now holds W2-37's `impact`) into the branch as `0e469cc37`; in that merge `src/gov/check/commands.py` took integrate's
side exactly (DEC-1173 (1)), so the `skilleval` line run 3 had there is gone. Your task is one commit: add it back.
Nothing else.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-drhj`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-104` and `w2/W2-104`),
  `git rev-parse --short=12 HEAD` (expect `0e469cc37...`) and `git status --short` (expect nothing). If anything
  differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag,
  no stash.
- **The code under test (DEC-732):** every test run and every `gov` command used for verification runs this worktree's
  own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src` set per command. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest through the heavy slot** with `TMPDIR` your sandbox's own `$TMPDIR` (keep it; never set it, never
  `--basetemp`), `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  A slot gate's refusal or wait is a wait, not a refusal.
- **Reads (DEC-820):** reads are open, except: (a) secrets and keys, never read or printed; (b) the held-out
  qualification material's contents (never read, search, diff or copy it; its file names may be seen); (c) the
  counterpart's work on this ticket: you never read `tests/acceptance/W2-104/` by any tool (run it only through
  `gov accept`, which your lead does); (d) the hidden half of any evaluation set. Never open an evaluation set's root
  or any hidden or memory-verdict folder. You search with the Read and Grep tools, naming the folder a search starts
  at; if the first search does not answer, search once more in different words, then answer from what you read or say
  "not found" (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065).
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute
  paths. Anything longer than one line goes in a script file in your sandbox's `$TMPDIR`.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal by another tool or
  form (DEC-1142 (9)); report it.
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- Write commit hashes as 12 digits in your return, never the full 40.

## The task: `skilleval` in `src/gov/check/commands.py` (DEC-1020)

After integrate's `impact` line (`RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("impact",)  # impact (W2-37, ...`),
add run 3's line exactly:

    RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("skilleval",)  # skilleval (W2-104, DEC-747, DEC-1020): the skill evaluation harness

(`git show 39ceaec2a:src/gov/check/commands.py` shows it as run 3 had it.) Nothing else in the file changes.

Check, to the end, never `-x`:
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -c "from gov.check.commands import RECORDED_GOV_COMMANDS; print(RECORDED_GOV_COMMANDS)"`
  shows integrate's commands with `impact` and then `skilleval` last.
- `cd /home/usain/gov-os-worktrees/W2-104 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -m gov.check.commands; echo exit=$?` (exit 0).
- `git diff w2/integrate -- src/gov/check/commands.py` shows only your one added line.
- The unit tests below, through the heavy slot:
  `tests/unit/skilleval tests/unit/check/test_check.py tests/unit/check/test_kernel_followup.py`.

Commit only that file (check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no
`pre-commit` file; if one is there, stop and return; never `--no-verify`):

    git commit -m "W2-104: skilleval back in commands.py's recorded commands, beside W2-37's impact, as DEC-1020 recorded it" --trailer "Task: DAEO-drhj" --trailer "Role: engineer" --trailer "Implements: DEC-959, DEC-820" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- src/gov/check/commands.py

(`Implements:` names only the ticket's `sources:`, DEC-959 and DEC-820 (DEC-927); DEC-747 and DEC-1020 stay in the
subject only.)

Then `git log --oneline -2` and `git status --short` (expect nothing but the sandbox's own `/dev/null` mount points,
if any; name them).

Your lead runs `gov accept` and the wider suites after you return; you do not.

## Return

Your last message, complete in itself. **The twelve fields come first, each a labelled line** ("none" where there is
nothing). Include: the sandbox check's result first in `evidence`; the commit's 12-digit hash and trailers; its diff
stat; the tests you ran with their counts; the `gov.__file__` line; the read refusals you met; your scratch figures
(`du -s --inodes` and `du -sh` of your `$TMPDIR` at the end); anything refused or not settled, as a package (question,
options with cost, recommendation, confidence, what it blocks).

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

## Context bundle (`gov context DAEO-drhj --role engineer`, built by your lead outside the sandbox)

The ticket's sources are DEC-959 (ACCEPTED) and DEC-820 (ACCEPTED); the ticket text is in
`/home/usain/gov-os-worktrees/W2-104/.tickets/DAEO-drhj.md` as merged. Its allowed paths: `docs/probes/DAEO-drhj/**`,
`src/gov/skilleval/**`, `tests/unit/skilleval/test_w2_104*`, `governance/project/skill-imports.yaml`,
`src/gov/check/commands.py`. Bundle hash `662fdd5214da`.
