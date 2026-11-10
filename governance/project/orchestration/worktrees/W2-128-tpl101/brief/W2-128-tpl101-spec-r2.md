Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128-tpl101/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# DEC-1121, round 2: the ticket template 1.0.1's `class` comment names the classes the code keys on (W2-128, DAEO-t8mp)

You are a fresh **product-spec** session under W2-128's ticket. RUBRIC-2 (DEC-1120 (3)): the C3 review of round 1 found
a fail-open finding, so this round runs on Opus at high (promoted, reason recorded).

## What happened
Round 1 (`8df648cc9` on `w2/W2-128-tpl101`, worktree `/home/usain/gov-os-worktrees/W2-128-tpl101`) added to
`template/governance/kernel/templates/ticket.md`'s record block
`class: implementation              # or research, test-design, discovery, data, integration, skill` and bumped the
version to 1.0.1. The C3 review (`governance/project/orchestration/reviews/W2-128-tpl101-review.md` in the main tree:
read F1-F3 in full) failed it:
- **F1 (fails open):** the comment leaves out `specification`, `audit` and `coordination`, which `gov close` keys on:
  the DEC-307 readiness-record gate runs only when the class is `specification`, so a specification ticket filed from
  the template as `skill`/`implementation` closes without its readiness record checked.
- **F2:** the list names `discovery` and `data` (used by no ticket, read by no code) and leaves out classes in daily
  use (test-revision, config, ops, schema, template, tool, documentation, role-definition).
- **F3:** round 1's commit message says the default came from "the 1.0.0 template's old default", but 1.0.0 had no
  `class` line (the default was in W1-08's template, `079d73742`; round 1 of W2-128, `a6c83d497`, removed it).

## The task
1. Find every class value the code keys on: grep `src/gov/` for `"class"`, `.get("class"`, `["class"]` and the values
   compared against (e.g. `src/gov/close/command.py`, the ready check, the plan, the readiness gate). List them with
   path:line. Then the values in use: count `^class:` across `.tickets/*.md`.
2. Rewrite the one `class:` line (keep `implementation` as the example value) so its comment names **first every
   value the code keys on, each marked by what it triggers in a few words where the line allows** (e.g. a second
   comment line is fine if the block's style allows it; keep it short), then the common values in use. Drop values no
   code reads and no ticket uses. Nothing else in the template changes; the version stays 1.0.1.
3. Runs, once each, counts only: W1-08 and W2-128 with `--optin=lifted,breadth` (the command form in round 1's brief:
   `env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$PWD/src python3 -m pytest tests/acceptance/W1-08 tests/acceptance/W2-128 -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed --optin=lifted,breadth`;
   `PYTHONUSERBASE=/home/usain/.local` if HOME is empty), and `PYTHONPATH=$PWD/src python3 -m gov.check.schema`.
   Expect only the known path-map namespace red (`governance/project/indep-briefs/`, fixed by ACT-PATHMAP-NS-2).
4. One new commit (never amend): `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1121" --trailer "Role: product-spec"`
   `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`; its message says it answers review F1-F2
   and corrects round 1's message (F3: the default's source is W1-08's template `079d73742`, removed in `a6c83d497`).
5. Return: the commit, the template's sha256 and blob id after, the diff from `905b82a3b` (the whole change since
   1.0.0), the code-keyed values with path:line, the counts.

## Where you work
- The same worktree and branch, at `8df648cc9`. Write only `template/governance/kernel/templates/ticket.md`.
  `TMPDIR` a folder of your own under the sandbox's TMPDIR.

## Rules
- `EMG-common.md` holds, its hidden-half rule included. No GPU, no installs, no other test runs. Never
  `git worktree prune`. Single simple Bash commands. Any wait by pid only, never a name match.
- Row W2-L423's rule: under `.gov-runtime/`, commit hashes are written as 12 digits and none of that rule's keywords.
- Estimate: 20 minutes. Return the twelve fields, short.
