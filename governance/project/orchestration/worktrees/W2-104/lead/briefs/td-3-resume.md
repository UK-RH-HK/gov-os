# Resume: independent test designer, DAEO-drhj (W2-104), run 3 — verify and commit the edits already made

You are a fresh independent test designer resuming a predecessor's task. **Read the full task first:**
`/home/usain/gov-os-worktrees/W2-104-tests/.gov-runtime/scratch/brief/td-3.md` (its standing rules, its two parts,
their checks and their two commit commands all hold for you, word for word, except where this page differs).

## What your predecessor left (session 21dac6dd)

It made all the edits of both parts, in `/home/usain/gov-os-worktrees/W2-104-tests`, and committed nothing: its
session ended while it waited for a background pytest run, so it never verified and its return lacked all twelve
fields. `git status --short` shows exactly five modified files: the four of Part 1
(`tests/acceptance/W1-07/README.md`, `test_w1_07_recorded_commands.py`, `w1_07_support.py`,
`tests/acceptance/W1-32/test_w1_32_command_set.py`) and Part 2's `tests/acceptance/W2-104/w2_104_support.py`. HEAD is
still `349341ab8`.

## What you do

1. The start checks of td-3.md, except that `git status --short` shows those five files (anything else: stop and say
   so).
2. Read the diff (`git diff`) against td-3.md's two parts and correct anything that does not meet them (Edit tool).
3. Run every check of both parts **in the foreground, one at a time, and wait for each to finish**. Never start a
   command in the background, never use Monitor or any wait for an event, never end your turn while anything runs:
   your session ends with your last message and nothing left running is ever read. A long pytest is fine in the
   foreground (give the Bash call a timeout of 600000 ms; if a suite needs longer, run it in parts, for example
   `tests/acceptance/W1-07` and `tests/acceptance/W1-32` as two runs).
4. Commit Part 1's four files, then Part 2's one file, with td-3.md's two commit commands exactly.
5. Return the twelve fields as td-3.md says. Name in `discoveries` that you resumed a predecessor's edits and what, if
   anything, you corrected.
