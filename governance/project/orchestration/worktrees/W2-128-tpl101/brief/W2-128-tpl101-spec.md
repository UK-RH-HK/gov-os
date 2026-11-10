Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128-tpl101/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# DEC-1121: the kernel ticket template 1.0.1 gains `class` (W2-128, DAEO-t8mp)

You are a fresh **product-spec** session under W2-128's ticket (`.tickets/DAEO-t8mp.md`: the kernel templates). Under
RUBRIC-2 (DEC-1120) you run on Sonnet at high; your work is C3 (the kernel), so an Opus reviewer checks it after you.

## Why
The owner approved W2-128's templates as version 1.0.0 (DEC-1116). W1-08's test designer then found a DEC-105
contradiction: CAP-31.a (`docs/contract/CONTRACT_v4.md` ~line 494: "task contract with class, role, inputs, allowed
paths, KPIs, profile") names `class`, and `template/governance/kernel/schemas/ticket.schema.json` keeps `class` as an
optional property, but the 1.0.0 ticket template's fenced ```yaml record block has no `class` (the old W1-08 template
had `class: implementation`). `tests/acceptance/W1-08/test_w1_08_ticket.py::test_the_ticket_template_carries_the_nine_fields`
(opt-in `breadth`) is red for that. The owner chose (a) (DEC-1121, `grep -n "^### DEC-1121" docs/DECISION_REGISTER.md`):
add `class` to the ticket template as version 1.0.1; the owner approves its hash before it lands.

## The task
1. In `template/governance/kernel/templates/ticket.md`: add `class` to the record block, in the block's own style
   (one line with a short comment listing the allowed values). Take the allowed values from the schema's `class`
   property (read it: enum or pattern); if the schema gives none, take them from the Contract/kernel docs and say
   where. Place it where CAP-31.a's order suggests (near `type`/`role`). Bump the front matter `version: 1.0.0` → `1.0.1`.
   Change nothing else in the template.
2. Anything that pins the template's version or bytes must follow, and nothing else: look for `1.0.0` or the ticket
   template's hash in `template/governance/kernel/templates/keys.yaml`, the templates' README, the facts file and its
   schema, `tests/acceptance/W2-128/` and TEMPLATES-APPROVAL-1 (`governance/project/orchestration/packages/`). Where a
   test of W2-128 pins the version or a hash of the ticket template, report it and update it only if the test reads a
   record that is meant to follow the template (else leave it and say why: that is a test designer's change, not
   yours). List every place you found.
3. Run, from the worktree root, each once:
   - `env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$PWD/src python3 -m pytest tests/acceptance/W1-08 -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed --optin=lifted,breadth`
     (expect the nine-fields case green now, and nothing newly red);
   - the same for `tests/acceptance/W2-128`;
   - `PYTHONPATH=$PWD/src python3 -m gov.check.schema` (exit 0).
   Report counts only (head and tail of the output).
4. One commit with `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1121" --trailer "Role: product-spec"`
   `--trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.
5. In your return give: the commit, the template's sha256 before and after (`sha256sum template/governance/kernel/templates/ticket.md`),
   the git blob id after (`git rev-parse HEAD:template/governance/kernel/templates/ticket.md`), and the diff of the
   template (it should be two hunks: the version and the `class` line).

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-128-tpl101`, branch `w2/W2-128-tpl101`, at `905b82a3b`.
- Write only `template/governance/kernel/templates/**` and, if step 2 requires, `tests/acceptance/W2-128/**` and the
  approval package's table (say so). `TMPDIR` a folder of your own under the sandbox's TMPDIR. If HOME is empty in
  your sandbox, set `PYTHONUSERBASE=/home/usain/.local` so pytest is found.

## Rules
- `EMG-common.md` holds, its hidden-half rule included. No GPU, no installs, no other test runs. Never
  `git worktree prune`. Single simple Bash commands. Any wait by pid only, never a name match.
- Row W2-L423's rule: under `.gov-runtime/`, commit hashes are written as 12 digits and none of that rule's keywords.
- If your context passes ~200k tokens, commit what is done, write a hand-over note in your return and stop.
- Estimate: 20 minutes. Return the twelve fields, short.
