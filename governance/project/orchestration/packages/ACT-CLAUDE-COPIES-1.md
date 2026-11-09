# ACT-CLAUDE-COPIES-1: the generated `.claude/` copies of the role, skill and template files (W2-128, W2-142)

- **For:** the owner's operator agent, through its queue. Class **(b)**: it needs the owner's one-line yes. It touches
  generated role and skill files, which instruct agents (OPERATOR-AGENT-1 §2, rows `agents-skills-kernel`,
  `rulesync-other`, `claude-rest`; the operator's `act_class.py` gives (b) on this bundle).
- **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-09. Built and rehearsed by
  `.gov-runtime/scratch/orchestrator/tools/build_claude_copies_act.py`. Nothing live changes until the operator runs it.
- **Under:** DEC-1109 (2) (D-5 restarted); W2-128's CIT-P line ("the `.claude/` copies are installed by the owner's
  operator as an ACT", CAP-33, DEC-1050, DEC-1081); W2-142's S3 (its skill copies regenerated at an ACT, DEC-1094 (2));
  DEC-315 (generated copies are written only by an ACT); DEC-1057 (rehearsed first).
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-1/`, built at integrate `97f39dc4e73e`.
  **Manifest sha256 `980e03eaffb9fb5cdc84910f74bf0e900e31042af070ff826655f5a543da5a97`.**

## What it does (13 files, each with its before and after sha256 in `manifest.json`)

| files | from | why |
|---|---|---|
| `.rulesync/skills/discovery/SKILL.md`, `.rulesync/skills/retrieval/SKILL.md` | byte copies of the kernel skills (`template/governance/kernel/skills/`) | W2-142's "search again once" (both 1.1.0) and W2-138's step-5 line; portability reports these two sources as differing today |
| `.claude/skills/discovery/SKILL.md`, `.claude/skills/retrieval/SKILL.md` | rulesync 24.0.0 (the pinned version) generated from those sources | the skills sessions load |
| `.claude/agents/engineer.md` | rulesync generated from `.rulesync/subagents/engineer.md` | W2-128's role line 5 ("to fulfil the spec and its KPIs", DEC-957); portability reports it as differing today |
| `.claude/templates/{brief,role-research,role-product-spec,role-test-designer,role-engineer,role-reviewer,role-lead,role-cto}.md` (new) | byte copies of the kernel templates | what W2-153's `gov launch` will pass as the appended system prompt. Nothing reads them before W2-153 lands, so adding them changes no session today |

Not in it:
- `template/.rulesync/skills/` (the template's own rulesync sources): the operator's rule names no row for them, so
  they would make the ACT class (O). They are an ordinary ticket path, copied in W2-128's round 2a.
- Settings, hooks and permissions: unchanged. rulesync's other outputs are byte-equal to the live files (the
  rehearsal's portability check).

## Rehearsal (log `rehearsal.log`, hashed in the manifest)
In a fresh clone at `97f39dc4`:
1. `apply.sh check`, then `apply`;
2. the two manifest checks (the source and template copies equal the kernel's byte for byte; the three generated
   files carry their new lines);
3. `gov.adapters.portability`: exit 0, no findings (three findings today);
4. the changed set equals the 13 touched files;
5. `apply.sh undo`: every file back byte for byte, the tree clean.

Result: **`failures: 0`**. The operator's `validate_manifest`, `act_class.classify` (class b) and `path_rule` (no live
path) pass on the bundle.

## Before it is queued
1. **Rebuild if the touched files moved.** W2-128's round 2a may change the orchestration skill and the orchestrator
   role (review F6) and the test-design skill (F7). If it lands first, the builder is re-run with those sources and
   copies added, so one ACT carries all of them, and the manifest sha changes. If it lands after, a second run of the
   same builder makes ACT-CLAUDE-COPIES-2.
2. **The ACT review (G4):** one independent reviewer with the operator's fixed `reviewer-brief.md`. Its `review.md`
   goes into the bundle and must be READY by the pinned `verdict.py`. That is the CTO's next launched worker on this
   ACT.
3. **Queue:** one request line in `~/gov-os-operator/queue/` naming `ACT-CLAUDE-COPIES-1` and the manifest sha.

## What the owner says
"Yes, ACT-CLAUDE-COPIES-1 at manifest `<sha12>`" in the chat, once the review is READY (OPERATOR-AGENT-1 §4, (b)).
Undo: `operator_run.py undo ACT-CLAUDE-COPIES-1 <sha>` (tested in the rehearsal).
