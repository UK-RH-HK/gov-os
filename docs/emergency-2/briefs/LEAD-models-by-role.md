# Lead brief: models and effort by role, held by code in every repository through the kit (DEC-1246 (3)(b))

You are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10). Where this brief leaves a choice, make it and say what you chose in your return.

## Why
DEC-1246 (3)(b): "every session's model and effort set by its role from the rubric table, never by a start script or by hand; criticality setting review depth", in every repository through the kit. It ships in 0.1.6.

**The one thing you must not do:** change any role's model or effort (DEC-1236 (3)). The table reproduces today's values exactly (DEC-1225, DEC-1236 (2), DEC-1242 R-4): each product's CTO and a senior engineer: Opus, high; ticket, fix and chore leads: Sonnet, medium; every other role (test designer, engineer, product-spec, research, auditor, QA): Sonnet, high; a wide audit the owner asks for: Opus, high; no Fable anywhere. If the code today disagrees with that table anywhere, say so in your return; do not resolve it by changing a value the owner has not decided.

## What
Read rows 2-7, 2-9, 2-10 (Phase 2) and 4-2 (Phase 4) of `docs/emergency-2/integration/INTEGRATION-PLAN.md` §2 in full: each row's "what" is your spec, its "verify" your KPI line. Write them as K-lines (ids MR-1 = 2-9, MR-2 = 2-10, MR-3 = 2-7, MR-4 = 4-2, each with verify and failure line) into the owning tickets' `## Fix:` sections on your branch; the CTO approves them by this brief.
- **2-9** the effort table in one file (with the model column), read by `gov launch`, the role files and the start-script check; a row changed without `Decided-by: owner` reported by the basis check. Owner: W2-201 (`.tickets/DAEO-k1us.md`, closed: a fix).
- **2-10** criticality no longer varies the model; it keeps review depth and the profile; promotion and probe on Opus retire. W2-201.
- **2-7** a check that the start scripts (`.gov-runtime/scratch/orchestrator/tools/start_lead.sh`, `start_cto.sh`, `start_audit.sh`) match the table; `start_cto.sh` stops calling the Fable substitution reader. The scripts are the CTO's: edit them only to remove the Fable reader; the check is yours. W2-201.
- **4-2** the kit complete: `agent_model.py` and its hook line in the kit (`template/.rulesync/hooks.jsonc`), reading the same table; `defaultMode: bypassPermissions` in the kit's settings; the root `permissions.jsonc` aligned with the two live deny lines (git push, sudo). EXAMIN runs an older 2,124-byte hook copy that `gov update` must replace. Owner: W2-208 (`.tickets/DAEO-kt8e.md`, closed: a fix). Beware I-16 (`docs/emergency-2/integration/FINDINGS.md`): `gov adapters generate` duplicated the governance head in hand-written CLAUDE.md and AGENTS.md; do not run it on Gov OS's own tree; check `.claude/settings.json` after any generation in a scratch repository.

Kernel text you may change for these items (the CTO approves it by naming it here): the role files' model and effort lines under `template/governance/kernel/roles/` (they read the table instead of restating it, values unchanged), the kit's hooks and settings files.

Code area (stream B): `src/gov/launch/`, `.claude/hooks/agent_model.py`, `template/`, `governance/project/` configuration for the table. Stay out of `src/gov/dispatch/`, `src/gov/resources/`, `src/gov/rebuild*`, `src/gov/decisions/` (other leads).

## Where
Worktree `/home/usain/gov-os-worktrees/E2-models-by-role`, branch `e2/models-by-role` from `w2/integrate`.

## Green
LEAD-COMMON's flow (test designer first, red on the base; then the engineer). Then the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue models=e2/models-by-role --onto w2/integrate --select`; run exactly that list through the heavy slot (DEC-1244 X-1). Check the acceptance trailers (LEAD-COMMON).

## Return
Branch and head; MR-1 to MR-4 with tests and result; the selected suites' summary lines; the table as built (role, model, effort, decided); every place the code disagreed with the table before your change; reds not yours; the C3-trial counts.
