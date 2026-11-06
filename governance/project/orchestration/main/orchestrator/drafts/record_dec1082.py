import pathlib
R = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
p = R / "docs/DECISION_REGISTER.md"; s = p.read_text()
entry = '''### DEC-1082 — The permissions' missed points accepted and ACT-PERMISSIONS-2 applied; the health check's decisions: the three stopped agents started again, the DEC-999 labels a priority fix, the guard refuses the hidden sets outside the repository to the measured roles, the spill reading investigated, the score-once window after its review
- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`) · **Under:** DEC-1080, DEC-1081, DEC-1073, DEC-820 (d), DEC-1052 · **Changes:** DEC-1080 (P-PERMISSIONS-1's premise: the user-level settings allow all; the guard is the check)
- **Decision:**
  - **(0) Permissions.** P-PERMISSIONS-1 missed two points, accepted under our threat model: the owner's user-level
    settings allow every Bash command, Read, Edit, Write and web access, so the project's allow list adds nothing for
    Bash and its "keep asking" list does not ask; the guard is the real check. ACT-PERMISSIONS-2 (the measure clones
    and the worktrees as additional directories; `~/gov-os-eval` kept asking as the owner's last check; Read denied on
    the three hidden folders) is applied by the operator (check 2 of 2, 3 of 3).
  - **(1) The three agents stopped at 09:36 are started again:** L5 (phrasing), D-6 part 1, D-9's drafter. L5's 427
    uncommitted lines are reviewed first: continued from if sound, else L5 starts clean; the owner is told which.
  - **(2) The DEC-999 labels** (the live pin labels register chunks of other entries `DEC-999`): a priority fix,
    ahead of the levers' work, since an agent citing the wrong decision is drift. First: whether re-pin window 4's
    builds already fix it; if not, a ticket of its own (an independent test designer, then an engineer), the fix in
    re-pin window 4.
  - **(3) The guard and the sets root:** no user-level denies (they would lock out the owner's writer, checker and
    operator, who must read and write those folders). The root fix instead: the guard refuses the hidden sets outside
    the repository to the measured roles (engineer, research and the orchestrator) and allows the roles that write
    and check them; a guard change, an ACT for the operator, rehearsed.
  - **(4) The dispatcher's spill reading:** why `powershell.exe` fails from WSL ("Exec format error"), and the smallest
    fix; a WSL setting is an ACT for the operator.
  - **(5) The score-once window:** the review's findings fixed, a short re-review, then the window, as planned
    (DEC-1081 (3)).
- **Basis:** question 2 (the hidden halves refused to every measured role wherever they lie; a wrong citation is
  drift) and question 4 (prompts only where they carry a decision).

'''
i = s.rindex("| Version | Date | Change |")
s = s[:i] + entry + s[i:]
s = s.rstrip("\n") + "\n| 0.466 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1082; DEC-1080 changed. Next free id: DEC-1083. |\n"
i = s.index("### DEC-1080 —"); j = s.index("- **Status:**", i); k = s.index("\n", j)
s = s[:k] + (", DEC-1082 (0)" if "**Changed by:**" in s[j:k] else " · **Changed by:** DEC-1082 (0)") + s[k:]
p.write_text(s)
f = R / "governance/project/orchestration/DECISIONS-IN-FORCE.md"
f.write_text(f.read_text() + '''- DEC-1082 (2026-11-06): the user-level allow-all accepted (the guard is the check); ACT-PERMISSIONS-2 applied; the
  three stopped agents started again (L5 from its lines if sound); the DEC-999 labels a priority fix ahead of the
  levers (window 4's builds checked first, else a ticket, tests first); the guard refuses the hidden sets outside the
  repository to engineer, research and orchestrator (an ACT); the spill reading investigated; the score-once window
  after its review. Basis: 2 and 4.
''')
print("DEC-1082 recorded")
