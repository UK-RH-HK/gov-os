# Brief td-4: independent test designer for DAEO-lrre (W2-33): revise two older W1-33 cases

You are the independent test designer (MR-3) for ticket DAEO-lrre (W2-33). The owner has decided (DEC-1156 (3);
DEC-957; DEC-1120 (2)) that every kernel role file carries the Interface's lines (Version, Launch default, Launch by
criticality where RUBRIC-2 varies, Skills, Model tier "see Launch default", Work order, One writer per worktree), and
that the kernel roles grow from six to nine (the six plus `ticket-lead`, `qa-engineer`, `senior-engineer`; no
`independent-reviewer`). Two older W1-33 cases assert the old state. Under DEC-1156 (7) the CTO has added both files
to this ticket's paths so that you revise **exactly these two cases**, each with a `Rewrite-Reason:` comment. You never
read the product-spec worker's work on this ticket (the role files as changed on w2/W2-33 after `c70bbb69d` for
research.md): you write to the decisions and to the ticket's Interface, not to the files.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-33-tests |
| branch | w2/W2-33-tests (base `707d23b82`) |
| your two writable files | tests/acceptance/W1-33/test_w1_33_kernel_role_files.py, tests/acceptance/W1-33/test_w1_33_agent_definitions.py (not `w1_33_support.py`, not the README, not any other suite) |
| the ticket (current copy; `## Interface` holds the line forms) | /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/context/DAEO-lrre.ticket.md |
| context packet | /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/context/ctx-td.json |
| case 1 | `test_w1_33_kernel_role_files.py:149-155` `test_the_research_role_file_is_unchanged` (DEC-163) |
| case 2 | `test_w1_33_agent_definitions.py:86-90` `test_there_is_one_definition_per_role_and_the_research_one` |
| support module (read only) | tests/acceptance/W1-33/w1_33_support.py (`ROLES` :67, `RESEARCH_ROLE_FILE_SHA256` :80, `sha256` :157, `live_support.agent_definitions`) |
| the research role file as W1-46 placed it (read this, not HEAD's) | `git -C /home/usain/gov-os-worktrees/W2-33-tests show c70bbb69d:template/governance/kernel/roles/research.md` |
| a Rewrite-Reason example | tests/acceptance/W1-33/test_w1_33_agent_definitions.py `test_the_research_definition_is_the_generated_one` (its docstring); tests/acceptance/W1-35/test_w1_35_orchestration.py (search `Rewrite-Reason`) |
| the decisions | docs/DECISION_REGISTER.md by id only: DEC-1156 (3) and (7), DEC-163, DEC-957, DEC-1120 (2), DEC-959 item 3 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065).

## What to revise (keep each case's intent; change what it reads)
1. **Case 1, research.md unchanged (DEC-163).** Keep its point: the kernel holds one research role file, and its own
   body is the one W1-46 placed, apart from the owner's every-role-file lines. Keep the glob assertion as it is.
   Replace the whole-file hash with: the file's lines, less every line that starts with one of the Interface's line
   heads (`- **Version:**`, `- **Launch default:**`, `- **Launch by criticality:**`, `- **Skills:**`,
   `- **Model tier:**`, `- **Work order:**`, `- **One writer per worktree:**`), equal the W1-46 file's lines less the
   same heads. Pin the W1-46 side as a constant in the test file (a sha256 of the filtered W1-46 text, computed once by
   you from `git show c70bbb69d:...`, with a comment saying how; the support module is not yours), so the case needs
   no git at run time. Also assert research.md carries each of the Interface's lines whose value the ticket fixes for
   research (Launch default `model claude-sonnet-5-5, effort high`; Model tier `see Launch default`; the Work order and
   One writer sentences word for word) — only if you can write them from the ticket's Interface and S7 alone. Rename
   the case if its name no longer fits (e.g. `..._body_is_unchanged`); keep its docstring's DEC-163.
2. **Case 2, the agents roster.** The definitions under `.claude/agents/` are one per kernel role: the nine role ids
   (the five of `support.ROLES`, `research`, `ticket-lead`, `qa-engineer`, `senior-engineer`; define the added names
   locally) and no `independent-reviewer`; each defined once. This case is red until the copies ACT generates the
   three new agents (the CTO pairs that ACT with the land): say so in its docstring. Do not touch `.claude/`.
3. Each revised case carries a `# Rewrite-Reason: DEC-1156 (3), (7): ...` comment saying what changed and why. Change
   nothing else in either file.

## Rules
- Run W1-33 before your change and after (`mkdir -p /tmp/gov-w2-33-td4` first). Expected after: case 1 green on this
  base (the filtered body equals W1-46's) or red naming the line that differs; case 2 red (six agents found, nine
  wanted); no other W1-33 case changes state. Say which are red and why. Every pytest through the heavy-slot gate:
  `TMPDIR=/tmp/gov-w2-33-td4 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-33-tests/src python3 -m pytest tests/acceptance/W1-33 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A heavy-slot or resource refusal is a wait.
- No test named with `real`, `green_here` or `time_limit`. Paths compared with `Path.is_relative_to`, never a text
  search of a temporary path (DEC-1155).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/.
- Commit your two files only, one commit:
  `git commit -m "<subject>" --trailer "Task: DAEO-lrre" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-959, DEC-1120" --trailer "Rewrite-Reason: DEC-1156 (3), (7): every role file carries the owner's lines; the kernel roles are nine" -- tests/acceptance/W1-33/test_w1_33_kernel_role_files.py tests/acceptance/W1-33/test_w1_33_agent_definitions.py`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines before and after) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
