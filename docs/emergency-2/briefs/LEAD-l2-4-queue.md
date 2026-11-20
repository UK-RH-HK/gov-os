# Lead brief: Gov OS's own landing onto `gov queue` (L2-4; the owner, DEC-1217 (1), DEC-1223 (9))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (worktree, the machine rule, memory first, the flow,
trailers, models, the C3 trial). Name: `l2-4-queue`; worktree `/home/usain/gov-os-worktrees/E2-l2-4-queue`, branch
`e2/l2-4-queue` from `w2/integrate`. **Do not merge**; the CTO lands it.

**The owner's decision** (`docs/emergency-2/L2-COMMANDS.md`, row L2-4; DEC-1217 (1)): "Gov OS's own landing moves onto
`gov queue` after one green proving landing; the scratch landing tools retire." The base is green (release 0.1.4).

**What the CTO found on 2026-11-20 (read first, then confirm with the code):** the first try,
`gov queue DAEO-sdhj=e2/w2-17-fixes --onto w2/integrate --select` (a fix branch under a closed ticket, with `Fix:`
trailers), was refused: `SELECTION_REFUSED: 6 changed path(s) nothing maps to a suite`. The six were documents the
branch never wrote: `docs/emergency-2/briefs/*.md`, `docs/emergency-2/proposals/*.md`, `docs/emergency-2/release-0.1.4/STEPS.md`
and `repin.sh`, all committed on `w2/integrate` after the last green full-suite record (`e74765954`). The selection
(`src/gov/close/select.py` around line 770-820; `src/gov/queue/command.py` `_candidate`, `_changed`) seems to take the
change from the green base, not from the branch's fork, so every document the CTO commits after a green run blocks
every landing. Adding `docs/emergency-2/**` to the test map's `record_only` is refused by W2-66
(`test_the_record_only_paths_are_dec_891_s_places_and_nothing_else`, `test_the_record_only_list_hides_no_code_path`).

## Your work
1. **Find the defect's cause and its owning ticket** (W2-202 or W2-206 by their KPI lines; or the selection's own
   ticket): is "change since the green base" the intended model (then a document with no test must still be placeable,
   e.g. a document that is not code selects nothing, the way governance files select nothing), or is the change meant
   to be the branch's own (then the base is wrong)? Decide from the tickets' KPI lines and DEC-891 (look it up in the
   register or the archive) and say which, with the evidence. It is a **fix** under that ticket (no new ticket),
   recorded in its record, failing test first by the test designer, every commit with `Task:` and `Fix:` trailers in
   ONE final paragraph. C3 (`src/gov/close/**`, `src/gov/queue/**`): test designer Opus, engineer Sonnet.
2. **One green proving landing through `gov queue`** on a scratch clone of this repository first (never the real
   `w2/integrate`): a planted fix branch and a planted feature branch land, with documents committed on the base after
   its green record; the close record and the landing's answer as L2 describes. Then tell the CTO the exact command for
   the real proving landing (the CTO runs it on the next branch it lands).
3. **The scratch landing tools retire** only after that real proving landing (the CTO's call when it has run): list
   them now (`.gov-runtime/scratch/orchestrator/tools/` merge queue, land scripts; `governance/project/orchestration/tools/merge_queue.py`;
   `acceptance/W2-97` and `tests/unit/orchestration`'s merge-queue cases, which TI-2 retires at that point) with what
   still calls each, so the CTO can retire them in one chore.

## Green and return
`gov accept` of the owning ticket green; `tests/unit/close`, `tests/unit/queue`, W2-202, W2-206, W2-66, W2-201,
`tests/unit/optin`. Return: branch and head; the cause and the owning ticket with evidence; the fix lines and tests;
the scratch-clone proving landing's evidence; the command for the real one; the retirement list; the trial figures.
