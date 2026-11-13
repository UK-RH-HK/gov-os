# AUDIT-NIGHT-1 (c2): ticket lines for what is already decided

By the product-spec helper for the CTO (Sonnet, high, class C1), 2026-11-11, at head `9bb497925ed7`. DEC-1125 (3) (iii) c.
Brief: `NIGHT-ticket-lines.md`. **Nothing was committed.** Sixteen ticket files and two package files are changed (the
other file in `git status`, `ACT-REPIN-W5.md`, is another helper's). No status, existing KPI meaning, acceptance
criterion or closed ticket was changed. **M** means measured; **E** my judgement.

**The commit for the ticket edits** should carry `Implements: DEC-1125, DEC-1123, DEC-1120, DEC-1119, DEC-1112,
DEC-1101, DEC-1088, DEC-1045, DEC-1044, DEC-1041, DEC-315` (DEC-1088 (6): each change to an open ticket marked with
its decision, or `gov links` reads TICKET_CHANGE_UNMARKED).

## 1. What each ticket got

| Item | Ticket | Change (old → new) |
|---|---|---|
| 1 | W2-115 `DAEO-emq1` | **New success line:** the trailers switch (the family `product-traceability-trailers` a warning, `severity: warning`; `gov close` never refuses on a missing trailer; `traceability.py` an on-demand report; Verify: planted history, YELLOW not RED, exit 0, report lists commits) [DEC-1123 (3), CAP-33, LIFT-1 P1-PLAN Q-8]. **Two paths added:** `src/gov/close/traceability.py` and `template/governance/kernel/checks/product-traceability-trailers.yaml`. The line says the declaration is a **kernel file** and changes only under this ticket's CIT-P (CAP-33), named in the commit body. Sources + DEC-1123, CAP-33. |
| 7 (P-4) | W2-115 `DAEO-emq1` | **New success line:** `gov close --verify <ticket>` runs the scoped selection, the parallel and the serial phase, writes `select.json`, one JUnit file per phase, a summary line and its exit file last; exit 0/1/2/3 [DEC-1052, DEC-1079, DEC-1050]. Sources + DEC-1125, DEC-1052, DEC-1079. |
| 2 | W2-33 `DAEO-lrre` | **New success line:** each role file carries `Launch default:` and `Launch by criticality:` with RUBRIC-2's values (RUBRIC-2-APPLY §3); the `Model tier` field stays and names the line; the generated agents carry the same [DEC-1120 (2), DEC-1119 (2)]. Sources + DEC-1119, DEC-1120. Existing line 2 (defaults per role, effort high for the CTO and Senior Engineers) is **kept**: the new line extends it and does not contradict it. |
| 2, 7 (P-3) | W2-60b `DAEO-ecac` | **New success line:** the session record carries tier, criticality (C0-C3) and promotion reason, each null when not given [DEC-1120 (3)]. Sources + DEC-1120. |
| 3 | W2-60a `DAEO-cv58` | **Not edited.** `packages/AUDIT-NIGHT-1/w2-60a-options.md` holds the three costed options. |
| 4 | W2-88 `DAEO-2bdu` | **S18-S23 added** after S17, one failure line for the three faults, `depends_on` and `deps` + `DAEO-61vm`, `DAEO-k1e2`, `DAEO-p8tv` (W2-170 to W2-172). Sources + DEC-1101, DEC-1125. |
| 5 | W2-20 `DAEO-r30l` | Sources + DEC-1041 (and DEC-1045, for P-5). |
| 5 | W2-42a `DAEO-03ub` | Sources + DEC-1044. |
| 6 | W2-27 `DAEO-h4rh` | `depends_on` and `deps` + `DAEO-03ub` (W2-42a), `DAEO-f58b` (W2-116), `DAEO-2tfd` (W2-145), `DAEO-8s85` (W2-153), `DAEO-ylsh` (W2-156), `DAEO-ozyt` (W2-157); a YAML comment cites DEC-1112 (3); sources + DEC-1112. **See §3: one of these makes a plan cycle.** |
| 7 (P-5) | W2-20 `DAEO-r30l` | **New success line:** the secrets scan's one switch `governance/project/secrets.yaml` (`scan: on|off`) and where it is named; Verify: `tests/unit/secrets_check/test_dec1045_switch.py` (M: the file exists) [DEC-1045]. |
| 7 (P-7) | W2-116 `DAEO-f58b` | **New success line:** `gov launch` points every worker session's retrieval at the integration store; a designer's never reads a worktree's store; Verify: a launcher unit test per worker role [DEC-1087 (3), DEC-963]. The old line 3 (designer only) is kept. |
| 7 | P-1 | **Held** (DEC-1100 (4): "WAITS: proven in use"). **P-2** is item 3. P-6 and P-8 were not in my list. |
| 8 | the nine tickets | `.claude/**` lines out of `allowed_paths` (full list below), each place carrying one YAML comment citing DEC-315 and DEC-1112 (3); DEC-315 and DEC-1112 added to each ticket's sources. |
| 9 | W2-153 `DAEO-8s85` | `allowed_paths`: `tests/unit/resources/test_w2_20_launch.py` → `tests/unit/resources/test_w2_20_unit_launch.py` (renamed by `ae489a979`, M: `git ls-files`, `git log --follow`); the same fix in the body's R1 note. |
| 9 | W2-66c `DAEO-btcs` | **No change; nothing to place** (§4). |

### Item 8: lines removed
- `DAEO-2bdu` (W2-88): `.claude/skills/adopt/SKILL.md` (the kernel `template/governance/kernel/skills/adopt/SKILL.md` and the `.rulesync` copies stay).
- `DAEO-6icv` (W2-101): `.claude/skills/{frontend,ui-ux,devops}/**`.
- `DAEO-k7hz` (W2-11): six lines: `.claude/skills/orchestration/**`, `.claude/skills/audit/**`, `.claude/agents/orchestrator.md`, `.claude/skills/*/SKILL.md`, `.claude/skills/test-design/**`, `.claude/skills/qa-review/**`.
- `DAEO-kmcr` (W2-23): `.claude/settings.json`. This one is not a generated copy; the comment says a launched session cannot edit it and a change to this repository's own file goes by ACT. The adapter code and fixtures stay.
- `DAEO-lrre` (W2-33): `.claude/agents/**`.
- `DAEO-siiz` (W2-52): `.claude/skills/adopt/SKILL.md`.
- `DAEO-uw5h` (W2-100): `.claude/skills/{backend,api,data,security}/**`.
- `DAEO-wi46` (W2-98): `.claude/skills/spec-writing/**`.
- `DAEO-xwro` (W2-141): `.claude/hooks/role_reads.py`. The staged copy `docs/changes/W2-141-hook/**` stays in the paths, and the operator's ACT applies it.
- Checked after: `allowed_paths` of all nine start with no `.claude` entry (M, a script over the parsed YAML).

## 2. The checks (M)
- YAML of each of the 16 files parses; no duplicate path or source; `deps` equals `depends_on` in all 16.
- `python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py <repo> HEAD`: **all 9 families ok**; `links: ok (0 new since HEAD, 1577 standing)`: no new UNLINKED_ID.
- `tk dep cycle`: none.
- The plan, run from `src/` read-only on the main tree: 98 tickets, 21 batches, 528 waits, no `PLAN_CANNOT_RUN`. The pinned `gov` has no `plan` command yet, so I ran `gov.plan.derive.make_plan` from the source. **One new cycle tie-break:** §3.

## 3. Found while doing it (for the CTO)
1. **W2-27's new dependency on W2-156 makes a plan cycle (M).** The plan shows `DAEO-ylsh waits for DAEO-h4rh (CYCLE_TIEBREAK DEPENDS_ON DAEO-ylsh)`. Cause: W2-156 writes `src/gov/launch/launcher.py` (and `commands.py`); W2-82 (`DAEO-4k3l`, priority 1, depends on W2-27) writes `launcher.py` too, and the plan orders overlapping writers by priority and WBS order, so it puts W2-82 before W2-156. So W2-27 → W2-156 → W2-82 → W2-27. DEC-1102's rule breaks it at W2-156, which means the plan places W2-156 **after** W2-27, the opposite of what the dependency is for. Without my W2-27 edit the plan shows only the three cycle tie-breaks that were already there (W2-155, W2-159, W2-160) (M, on a scratch copy). W2-157 is not affected. A notice, not a refusal. Ways out, for the CTO: give `DAEO-ylsh` a `plan_override` with a decision id; or drop W2-156 from W2-27's list again (one line); or, after the lift, make the plan skip an overlap pair that explicit dependencies already order (a code change, the same cause as AUDIT-NIGHT-1 c §4.8). I kept the edit because the brief named it; I recommend the override, 65 % confidence (E).
2. **W2-33 is where the role files' default lines live.** `RUBRIC-2-APPLY` §3 and DEC-1120 (5) say W2-33; `DAEO-k7hz`'s own text says its role file "stays limited to DEC-866's sweep sentences (W2-33 holds the rest)". W2-60a's body (line 72) still says "W2-11's widening". I did not touch it (body prose of a ticket I may not edit tonight); the options file lists it as a step.
3. **W2-33's three "moved to Wave 3" lines** are still moved, though DEC-1087 (13) brought them back (P1-17). Not in my list; left.
4. **W2-115's switch may need a third path.** Q-8 also says `accepted_history` and `trailers_base` are deleted; their code is in `src/gov/close/history.py` (M: `trailers_base`, `accepted_history`), which W2-115's paths do not hold. My line asks only for the severity change, the notice and the report, so it needs the two paths I added. If the owner wants the code deleted, `history.py` is a third path.
5. **W2-115's `gov close --verify` needs W2-154's serial phase** (`DAEO-l4gf`). I did not add a wait. The plan of the audit puts W2-154 (batch 8) after W2-115 (batch 7) (AUDIT-NIGHT-1 c §5), so the CTO may add `DAEO-l4gf` to W2-115's waits, or let the line be built after W2-154 lands; either is a one-line choice.
6. **A project-side override** is the other way to the trailers switch (P1-PLAN P1-21 "to settle"). I took the kernel declaration because the brief said to say so in the line (CAP-33). If the CTO settles the override, the line's second sentence changes.
7. **W2-60b's new line depends on W2-60a's choice.** It reads criticality and promotion from W2-60a's launch record. Under the options "defer" and "re-baseline" those keys are null, which the line allows.
8. **The re-pin note for W2-141:** its path line is gone, so the ticket no longer lets a launched worker "edit" the live hook even in name. The staged copy and the ACT are as before.

## 4. Item 9: W2-66c's path (not placed)
Audit f said `tests/optin-lifted-breadth.txt` "is now `tests/optin-breadth.txt`". **At HEAD that is not so (M):** `tests/optin-lifted-breadth.txt` is tracked, `tests/optin-breadth.txt` does not exist anywhere, and `git grep optin-breadth` finds only the audit's own sentence. Every path and test node id in `DAEO-btcs` resolves at HEAD (M: the four named test files and the four node ids; the three named acceptance files). The one missing path is its own deliverable, `tests/acceptance/W2-66/test_w2_66_select_fixes.py`, which does not exist yet. So I changed nothing. `gov doctor` may be counting the ticket for a reference in a record it reads beside it: the CTO may run it once on this head.

## 5. What I did not do
No ticket outside the sixteen. No `allowed_paths` change for any other path. No KPI of W2-60a. No edit of the ticket bodies' prose, except the one path in W2-153's R1 note. No `gov plan --ready`, no commit, no `src/` read except `src/gov/plan/` and `src/gov/close/` to name a path. Scratch: 316 KB, 11 files, under the session's scratchpad. One mistaken write: I created a one-line file `/tmp/claude-1000/-home-usain/Dynamic-Agentic-Engineering-OS/x` by a typo in a path (outside the project and my scratch); I may not `rm` there, so it stays for the CTO to delete.
