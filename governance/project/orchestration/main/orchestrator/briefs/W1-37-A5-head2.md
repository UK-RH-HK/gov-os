You are the ticket lead for ticket `DAEO-yvzh` (`W1-37`, "Superpowers three-skill vendoring"), profile LITE, working only in the worktree `/home/usain/gov-os-worktrees/W1-37` on branch `w1/W1-37`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). LITE: one test per KPI line; no reviewer step.

## State of this ticket

- An earlier lead ran a test designer, which wrote no tests and returned four packages (DP-1 to DP-4). All four are now decided; this worktree's branch has been brought up to `w1/integrate`, which holds them. Read DEC-244, DEC-245, DEC-246 and DEC-247 in `docs/DECISION_REGISTER.md`, with DEC-074 Q5, DEC-194 and DEC-199:
  - DEC-244: copy the three skill folders from `template/governance/kernel/vendor/superpowers/skills/` into `template/governance/kernel/skills/superpowers/<skill>/`; the vendor folder stays unchanged.
  - DEC-245: "namespaced" means the folder; the copies stay byte-identical to the vendor copy; version v6.4.2 is recorded beside them. Whether a version must also be in each `SKILL.md` frontmatter (CAP-24) is with the owner; no test asserts either way on that point.
  - DEC-246: a record file inside `skills/superpowers/` carries the source version, the vendor folder's digest by the DEC-199 rule and the copy's digest by the same rule; a test recomputes both offline.
  - DEC-247: size is floor(characters ÷ 4) of each `SKILL.md`, at or below 2,389, 2,360 and 899; no tolerance; the measured sizes go in the record.
- No acceptance tests exist yet; nothing is implemented. Earlier KPI disputes on this ticket: 4 (count them in the learning metrics).
- Installs nothing, downloads nothing.

## What you do, in order

1. **Test design** (brief A1, a fresh designer, profile LITE, DEC-221), with the four decisions above.
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh).
4. **Verify** every suite and the validator.

