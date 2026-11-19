# Lead brief: the run-time tool, slice 3: across sessions (W2-205, the ticket is written)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it (and
`LEAD-COMMON.md`: add `-n auto` to slot runs of more than one file). Branch `e2/rt-slice3` from `w2/integrate`,
worktree `/home/usain/gov-os-worktrees/E2-rt-slice3`. Run-time tool code is C2 (Sonnet helpers); the two kernel hooks
(`template/governance/kernel/hooks/stop.py`, `sessionstart.py`) are kernel text, C3: the test designer and the engineer
for the hook part run Claude Fable 5.2 (`model: "fable"`); the CTO approves the hooks' change by this brief (§3.5).
`Task: DAEO-rt3s`, `Class: F`.

**Your ticket:** `.tickets/DAEO-rt3s.md` (W2-205; the slice 2 lead wrote it and the CTO renumbered it from W2-200,
which is another ticket's number: its tests live under `tests/acceptance/W2-205/` and `test_w2_205*`). Set it
`in_progress` in your branch. Slice 2 (W2-199, `.tickets/DAEO-rt2s.md`) landed tonight at befe40431: read its code in
`src/gov/dispatch/` and `src/gov/resources/slots.py` first. Audit 3 `docs/emergency-2/audits/03-run-time-tool.md` and
EMERGENCY-2 §6.3 (RT-1 to RT-8) are the design.

**The CTO's rulings on the ticket (amend its KPI lines in your branch to match, before the test designer starts):**
1. **The Stop check blocks a turn end only for an unread `wake` message, once per message.** Drop "or no `gov msg wait`
   is armed for the session": the owner retired inbox waiters and idle-check wake-ups (DEC-1212 (4)); a session that
   waits on nothing must be able to end its turn without a block.
2. **The ticket's open question: (a).** The Stop check does not block for a launchable ticket; the dispatcher starts
   ready work itself.
3. **The stall check and the push stay in the live tick, untouched** (DEC-1214 T1, T2; DEC-1216 (5): the owner keeps the
   CTO-stall push). The 99 % plan push and the owner's decision pushes are the CTO's own and not this slice's.
4. **RT-5's relaunch is off by default** until the cut-over: built and tested, switched by a config key, so tonight's
   live leads (started by `start_lead.sh`, not `gov launch`) are never relaunched by a pass.
5. **Nothing live is switched:** not the cron line, not the scratch dispatcher, not the scratch `heavy_slot.sh`, not the
   hooks registered in this repository's own `.claude/settings.json` (the template's hooks change; the root's copies
   follow at the cut-over, slice 4).

**Flow:** test designer writes `tests/acceptance/W2-205/` from the amended KPI lines, red on the base; engineer builds
until `gov accept W2-205` is green; then `tests/unit/dispatch`, `tests/unit/msg`, `tests/unit/launch`,
`tests/unit/checkpoint`, `tests/unit/hooks`, `tests/acceptance/W2-121c`, `W2-199`, and W2-05 (the hooks' source cases)
with node on the PATH (`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`). Then, if time remains, write slice 4's
ticket (the cut-over: the cron line, the product slot replacing the scratch script, the gate file's `heavy_slots`, the
retirements of audit 3) as the next free W2 number the CTO gives you in your return's reply: leave its `wbs_id` as
`W2-TBD` and stop.
