# Brief: independent test designer, DAEO-drhj (W2-104), run 4 — `skilleval` back in W1-07's and W1-32's lists, beside `impact`

You are a fresh independent test designer (MR-3). Ticket: `DAEO-drhj` (W2-104), profile STANDARD, class C2. You work
only in the tests worktree `/home/usain/gov-os-worktrees/W2-104-tests` on branch `w2/W2-104-tests` (DEC-963); you never
write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-104`. Your lead has merged `w2/integrate` (head
`72c6def8871a`, which now holds W2-37's `impact`) into the ticket branch as `0e469cc37`. In that merge every conflicted
file took integrate's side exactly (DEC-1173 (1)), so `skilleval`, which this ticket recorded in run 3, is no longer in
W1-07's and W1-32's lists. Your branch starts at `0e469cc37`. Your task is one commit: add `skilleval` back, beside
`impact`. Nothing else.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-drhj`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-104-tests` and
  `w2/W2-104-tests`), `git rev-parse --short=12 HEAD` (expect `0e469cc37...`) and `git status --short` (expect
  nothing). If anything differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag,
  no stash.
- **The code under test (DEC-732):** in your tree every test run uses
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104-tests/src` set per command; quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104-tests/src python3 -c "import gov; print(gov.__file__)"` in your
  return. `src/gov/check/commands.py` is the engineer's (it adds `skilleval` there in the ticket's tree, in parallel):
  never edit it, never read it.
- **Every pytest through the heavy slot**, with `TMPDIR` your sandbox's own `$TMPDIR` (keep it; never set it, never
  `--basetemp`), `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-104-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  A slot gate's refusal or wait is a wait, not a refusal.
- **Reads (DEC-820):** reads are open, except: (a) secrets and keys, never read or printed; (b) the held-out
  qualification material's contents (never read, search, diff or copy it; its file names may be seen); (c) the
  counterpart's work on this ticket: you never read this ticket's implementation by any tool: nothing under
  `src/gov/skilleval/`, `tests/unit/skilleval/`, `governance/project/skill-imports.yaml`, nor
  `src/gov/check/commands.py`, in any tree or commit; (d) the hidden half of any evaluation set. Never open an
  evaluation set's root or any hidden or memory-verdict folder. You search with the Read and Grep tools, naming the
  folder a search starts at; if the first search does not answer, search once more in different words, then answer
  from what you read or say "not found" (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065). For run 3's
  text of each file, `git show 39ceaec2a:<path>` works (the ticket branch before this merge).
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute
  paths. Anything longer than one line goes in a script file in your sandbox's `$TMPDIR`.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal by another tool or
  form (DEC-1142 (9)); report it.
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- Write commit hashes as 12 digits in your return, never the full 40.

## The task: `skilleval` beside `impact` (DEC-747, DEC-1020)

Integrate's text in each file is kept exactly as it is; you only add. Run 3's additions (`git show 39ceaec2a:<path>`)
show the form; follow integrate's form where they differ.

1. `tests/acceptance/W1-07/w1_07_support.py`: after integrate's `impact` line, a short comment and
   `RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("skilleval",)` (DEC-542's one line; run 3's comment was
   `# DEC-747 (W2-104): ``skilleval`` joins them too.`).
2. `tests/acceptance/W1-07/test_w1_07_recorded_commands.py`: in the count case, a comment line for `skilleval`
   (DEC-747, W2-104) after integrate's W2-37 comment, and the pinned sorted list becomes integrate's ten plus
   `"skilleval"` in sorted place: eleven. In the parametrized help case's docstring, a line that `skilleval` (DEC-747,
   W2-104) makes the recorded `gov` commands ten.
3. `tests/acceptance/W1-07/README.md`: the paragraph near line 227 that lists the commands in `RECORDED_GOV_COMMANDS`
   names `skilleval` since DEC-747, W2-104 (as run 3 named it); and after integrate's last paragraph (P-7 (a), W2-37),
   one paragraph for this ticket in the same form: `skilleval` recorded beside `impact`, the recorded commands eleven
   (ten `gov` commands and `lock`), the count case pins the eleven, the help case gains `[skilleval]`, W1-32's first
   assert gains `skilleval`, and the section's case count. Change no other line.
4. `tests/acceptance/W1-32/test_w1_32_command_set.py`: in `test_the_command_set_is_the_twelve_and_the_three_recorded_ones`,
   a docstring line for DEC-747 (W2-104) after integrate's W2-37 line, and the first assert's set gains `"skilleval"`
   in sorted place. Nothing else.

The point of each case stays as it is: a command no list records still fails, a recorded command gone from `gov --help`
still fails. In your tree `gov --help` already offers `skilleval` (the harness is built and registered), so these
cases go green with your change even before the engineer's `commands.py` line.

Check, to the end, never `-x`:
- `git diff 0e469cc37 -- <the four files>` shows only additions of yours (and the changed list or set lines); quote
  `git diff --stat 0e469cc37`.
- `tests/acceptance/W1-07` and `tests/acceptance/W1-32` through the heavy slot: all pass, or name each red with its
  output and why it is not yours (for example a case that needs a network or the main tree).

Commit only the four files:

    git commit -m "W2-104: skilleval back in W1-07's and W1-32's lists, beside W2-37's impact (DEC-747, DEC-1020)" --trailer "Task: DAEO-drhj" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959, DEC-820" --trailer "Rewrite-Reason: DEC-1020 skilleval, after W2-37's impact (run 4)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W1-07/w1_07_support.py tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-07/README.md tests/acceptance/W1-32/test_w1_32_command_set.py

(`Implements:` names only the ticket's `sources:` (DEC-927); DEC-747 and DEC-1020 stay in the subject and the reason.)
Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one is there,
stop and return; never `--no-verify`.

Then `git log --oneline -2` and `git status --short` (expect nothing but the sandbox's own `/dev/null` mount points,
if any; name them).

## Return

Your last message, complete in itself. **The twelve fields come first, each a labelled line** ("none" where there is
nothing). Include: the sandbox check's result first in `evidence`; the commit's 12-digit hash and trailers; its diff
stat; each suite run with its counts; the `gov.__file__` line; the read refusals you met; your scratch figures
(`du -s --inodes` and `du -sh` of your `$TMPDIR` at the end); anything refused or not settled, as a package (question,
options with cost, recommendation, confidence, what it blocks).

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

## Context bundle (`gov context DAEO-drhj --role independent-test-designer`, built by your lead outside the sandbox)

The ticket's sources are DEC-959 (ACCEPTED) and DEC-820 (ACCEPTED); the ticket text, with its seven KPI lines, is in
`/home/usain/gov-os-worktrees/W2-104-tests/.tickets/DAEO-drhj.md`. Acceptance tests: `tests/acceptance/W2-104/`
(yours, unchanged this run). Bundle hash `662fdd5214da`.
