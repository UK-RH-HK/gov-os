# Brief ps-4: product-spec worker for DAEO-lrre (W2-33), fix round, class C2

You are a fresh product-spec worker (DEC-995) for ticket DAEO-lrre (W2-33). The kernel role files are written and the
ticket's own acceptance run is green. The full suite has three reds in an older suite (W2-128) that this ticket's
change turned red. You are given their failing output only. Fix the role files so these hold again, changing
nothing else. Never read `tests/acceptance/**` (DEC-820).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-33 (branch w2/W2-33) |
| your paths | template/governance/kernel/roles/orchestrator.md, template/governance/kernel/roles/engineer.md, template/.rulesync/subagents/orchestrator.md |
| the ticket (current copy) | /home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/context/DAEO-lrre.ticket.md (`## Interface`: the line forms; each line once and whole at column 0; their position in the file is free) |
| the kernel brief templates | template/governance/kernel/templates/ (`brief-lead.md`, `role-lead.md`, `brief.md`) |

## The failing output (three cases)
```
FAILED test_w2_128_round2a::test_review_f6_orchestrator_role_names_no_retired_brief_text_as_content[kernel]
AssertionError: template/governance/kernel/roles/orchestrator.md names no kernel template (role-lead.md or the templates folder) for a lead's brief, nor is its body role-lead.md's body
FAILED test_w2_128_round2a::test_review_f6_orchestrator_role_names_no_retired_brief_text_as_content[rulesync]
AssertionError: template/.rulesync/subagents/orchestrator.md names no kernel template (role-lead.md or the templates folder) for a lead's brief, nor is its body role-lead.md's body
FAILED test_w2_128_templates::test_s4_engineer_role_line_5_says_to_fulfil_the_spec_and_its_kpis
AssertionError: roles/engineer.md line 5 is '- **Version:** 1.1.0'  (the case wants line 5 of the file to be the Purpose line carrying "to fulfil the spec and its KPIs")
```
What the first two guard: the CTO starts each ticket lead, and the CTO's file must say which kernel templates a lead's
brief is built from (before this ticket, the removed ticket-lead section of orchestrator.md said "from the kernel
templates `brief.md` and `role-lead.md`"). The same file must not name a retired brief text as the content a lead or
worker is started from.

## What to do
1. `orchestrator.md`: in the item where the CTO starts ticket leads (Purpose or the lead-related statement), add in
   one sentence that the CTO starts each ticket lead from the kernel templates `role-lead.md` (the role) and
   `brief.md` (the envelope) in `template/governance/kernel/templates/`, citing DEC-1050 (and DEC-537, as the old
   text did). `brief-lead.md` there is a retired one-line pointer to those two: do not name it. Make **the identical edit**
   to the same sentence in `template/.rulesync/subagents/orchestrator.md`, whose body holds the kernel file's body
   verbatim after the role template part.
2. `engineer.md`: put the Purpose line (it carries "to fulfil the spec and its KPIs") on line 5 of the file. Move the
   defaults lines (Version, Launch default, Launch by criticality, Skills, Model tier, Work order, One writer per
   worktree) to directly after the Purpose item, unchanged and whole. Change no wording.
3. Check, read-only, with these one-line commands (they write nothing):
   `cd /home/usain/gov-os-worktrees/W2-33 && PYTHONPATH=src python3 -c "from gov.adapters.portability import compose; from pathlib import Path; print(compose('.', 'orchestrator') == Path('template/.rulesync/subagents/orchestrator.md').read_text(encoding='utf-8'))"` (must print True)
   `sed -n 5p /home/usain/gov-os-worktrees/W2-33/template/governance/kernel/roles/engineer.md`

## Rules
- **Forms:** the Edit tool only for the changes; no script file, no heredoc, no compound command that writes. An
  earlier worker's compound Bash heredoc was refused by the guard.
- Every line form stays exactly as it is, once and whole at column 0.
- Commit your paths only, as a single-line command:
  `git commit -m "<subject>" --trailer "Task: DAEO-lrre" --trailer "Role: product-spec" --trailer "Implements: DEC-957, DEC-954, DEC-236" -- template/governance/kernel/roles/orchestrator.md template/governance/kernel/roles/engineer.md template/.rulesync/subagents/orchestrator.md`
- Refused once by the guard, the sandbox or a hook for a call: do not reach the same effect by another command, form
  or file; report it and stop (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence (each changed sentence before and after; the two checks' output) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` and `guard_refusals:`.
