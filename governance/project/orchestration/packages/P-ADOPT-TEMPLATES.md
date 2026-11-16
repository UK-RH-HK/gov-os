# P-ADOPT-TEMPLATES: `gov launch` cannot start any worker in an adopted repository (LAUNCH_NO_TEMPLATE, release 0.1.0)

## 1. What happened
- W2-81's python-app (F-009) and rust-workspace (F-004) reached A5. `gov launch independent-auditor` refuses with
  `LAUNCH_NO_TEMPLATE: the role template <repo>/.claude/templates/role-reviewer.md is missing`.
- The launcher reads each role's template from `.claude/templates/` (`launcher.template_args`; W2-153, DEC-1050). In
  Gov OS's own repository those copies are "written only by an ACT" (DEC-315).
- In an adopted repository, nothing writes them. The kit ships the templates at `governance/kernel/templates/role-*.md`,
  and neither `copier copy` nor `gov adapters generate` copies them into `.claude/templates/`. EXAMIN's copy has none
  either, so its A5 meets the same refusal right after its settings fix.
- So in 0.1.0 no worker (auditor, engineer, test designer) can be launched in any adopted repository. That blocks A5,
  A7 and A10 in all seven adoptions, and the LITE ticket.

## 2. Rehearsed (2026-11-16 00:10, clones of EXAMIN and python-app)
- `operator_templates.py` copies the kit's seven `role-*.md` byte for byte into `.claude/templates/` and makes one owner
  commit per repository. The tree is clean after.
- On the clones, the launcher's own `template_args` then passes for the auditor, engineer and test designer roles. On
  the live repositories it still refuses.

## 3. Options
- **(a) Tonight's interim, recommended.** Your operator runs the script once over the seven repositories: one owner
  commit each, the same route as F-011 (DEC-1188 (1)). Then:
  - I resume python-app and rust-workspace at A5;
  - the others reach A5 with the templates in place;
  - EXAMIN's A5 follows its settings fix.

  **The product fix:** W2-153 (DAEO-8s85) reopened within its purpose ("the template copies generated and checked"),
  so that `gov adapters generate` writes `.claude/templates/` from the kit's templates in an adopted repository (and
  `gov doctor` names a missing copy), shipped in release 0.1.1. About half a day; 0.1.1 moves accordingly or ships
  without it, which is your call at the sitting.
- **(b) Interim only;** the product fix becomes a new ticket after W2-27 (your P1). 0.1.1 ships with the gap.
- **(c) No interim.** Every adoption stops at A5 until 0.1.1 carries the fix, and the overnight run stalls.

## 4. The operator's commands (a plain terminal; after EXAMIN's settings script, if not yet run)
```
env | grep '^GOV_'          # must print nothing
sha256sum /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/adopt-templates/operator_templates.py
python3 -I /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/adopt-templates/operator_templates.py
#   seven lines "<repo>: 7 templates, <commit>, status after: ''"
```
The script refuses before writing anything if a tree is not clean. A W2-81 session working at that moment can leave
its tree unclean; then wait a minute and run it again.

**Your line:** `P-ADOPT-TEMPLATES (a)` (or (b), (c)).
