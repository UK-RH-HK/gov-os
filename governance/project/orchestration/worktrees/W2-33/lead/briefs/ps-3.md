# Brief ps-3: product-spec worker for DAEO-lrre (W2-33), fix round, class C2

You are a fresh product-spec worker (DEC-995) for ticket DAEO-lrre (W2-33). The role files are written; the
acceptance run has one red KPI line. You are given its failing output only. Fix the role files so the KPI line holds,
changing nothing else. Never read `tests/acceptance/**` (the independent test designer's work on this ticket, DEC-820).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-33 (branch w2/W2-33) |
| your paths | template/governance/kernel/roles/orchestrator.md and template/.rulesync/subagents/orchestrator.md |
| the ticket (current copy) | /home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/context/DAEO-lrre.ticket.md (KPI S9 and F1) |
| how the rulesync copy is made | src/gov/adapters/portability.py:176 `compose(root, role)`: after the kernel file is final, the copy's full text is exactly `compose('/home/usain/gov-os-worktrees/W2-33', 'orchestrator')`, its front matter unchanged |

## The KPI line (S9)
Both copies of the template's orchestrator role file state the CTO-only install rule, name the key and the CTO's
`GOV_TICKET`, and no longer say the guard asks on every install. Verify: grep of both files finds in each the
CTO-only install rule, the key name and `GOV_TICKET`, and finds no sentence saying the guard asks on every install
[DEC-971 item 4]. (F1: no sentence in either file may say the guard asks, or prompts, on every / each / all installs,
or that every install is asked.)

## The failing output (both cases of S9; F1 passes)
```
template/governance/kernel/roles/orchestrator.md: does not state that only the orchestrator on the project's coordination ticket is asked for an install (no statement with ['install', '\\bonly\\b', 'coordination[\\s_]ticket', '\\b(orchestrator|CTO)\\b', '\\bask(s|ed)?\\b'])
template/.rulesync/subagents/orchestrator.md: does not state that only the orchestrator on the project's coordination ticket is asked for an install (no statement with ['install', '\\bonly\\b', 'coordination[\\s_]ticket', '\\b(orchestrator|CTO)\\b', '\\bask(s|ed)?\\b'])
```
A "statement" is a sentence or clause split after a full stop or a semicolon; the five words must stand within three
consecutive statements. The other two S9 statements (every other session refused; `coordination_ticket` and
`GOV_TICKET` with the install rule) already hold: keep them.

## Rules
- **Forms (the guard refused an earlier worker's compound Bash call that wrote a script with a heredoc; do not use
  that form, and write no script file):** make the change with the **Edit tool** only, on both files. The rulesync
  copy's body holds the kernel file's body verbatim (after its front matter and the role template part), so make the
  identical edit to the same sentence in `template/.rulesync/subagents/orchestrator.md`. Then check, read-only, with
  this one Bash line (it writes nothing):
  `cd /home/usain/gov-os-worktrees/W2-33 && PYTHONPATH=src python3 -c "from gov.adapters.portability import compose; from pathlib import Path; print(compose('.', 'orchestrator') == Path('template/.rulesync/subagents/orchestrator.md').read_text(encoding='utf-8'))"`
  It must print True.
- Change only the wording of the `PACKAGE_INSTALL` item that is needed. Every line form elsewhere in the file
  (Version, Launch default, Skills, Model tier, Work order, One writer per worktree) stays exactly as it is.
- Commit your paths only, as a single-line command:
  `git commit -m "<subject>" --trailer "Task: DAEO-lrre" --trailer "Role: product-spec" --trailer "Implements: DEC-957, DEC-954" -- template/governance/kernel/roles/orchestrator.md template/.rulesync/subagents/orchestrator.md`
- Refused once by the guard, the sandbox or a hook for a call: do not reach the same effect by another command, form
  or file; report it and stop (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence (the changed sentence before and after; compose equality) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` and `guard_refusals:`.
