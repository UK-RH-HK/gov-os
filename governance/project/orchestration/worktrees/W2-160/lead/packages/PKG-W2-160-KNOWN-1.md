task: DAEO-fd0p
# PKG-W2-160-KNOWN-1: W2-159's F4 scope case is red on every other ticket's branch, and skip_known.json does not name it

## Question
`tests/acceptance/W2-159/test_f4_scope.py::test_f4_the_branch_changes_only_the_tickets_allowed_paths` compares
`git diff --name-only <merge-base of HEAD and w2/integrate>...HEAD` with **W2-159's** allowed_paths (DAEO-6lid). On
w2/integrate the diff is empty, so it is green there and stays green after any merge. On a ticket branch that changes
any file it is red. Here it lists W2-160's own paths (`src/gov/wait/**`, `docs/changes/W2-160-evidence.md`, ...).
lead_verify selects W2-159's suite for every branch that touches `src/gov/session_watch/`, `src/gov/cli/main.py` or
`src/gov/check/commands.py`, and the last of these is the file that records every new command. It is not in
`skip_known.json`, so the lead may not name it as known. Which option does the CTO choose?

## Options
(a) **Name it in skip_known.json (recommended).** List this one case as known red on any branch other than
    `w2/W2-159`. Cost: one line in the CTO's tool file. It costs nothing on integrate, where the case still runs
    and still guards.
(b) **Fix the test.** W2-159's test skips, naming the reason, unless the branch is `w2/W2-159`. Cost: a test
    designer's change on a closed ticket's folder, so a new ticket or an ACT is needed (the owner, DEC-974). Every
    branch in the meantime needs (a) anyway.
(c) **Land W2-160 with the red named in the probe record**, with no list change. Cost: the next ticket that touches
    `check/commands.py` meets the same red.

## Recommendation
(a) now, confidence high, with (b) noted for the owner's next planning pass. This red is not W2-160's. It gives the
same result on any branch.

## What it blocks
lead_verify's green line for W2-160. `gov accept W2-160` is a pass (66/0). The branch's diff is inside allowed_paths
(the lead's F4 check).

## Accept in one line
"PKG-W2-160-KNOWN-1 (a): skip_known.json names W2-159's test_f4_scope case as known red off w2/W2-159."
