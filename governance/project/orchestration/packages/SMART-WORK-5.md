# SMART-WORK-5: DEC-1014 in the Gov OS (item 6, DEC-1003)

**Priority:** P2. The lines marked **done** are already in their tickets. The lines marked **proposed** wait for the
owner. Once approved, each is applied when its ticket next runs (DEC-1004).

## 1. Done today

- **W2-122 (`DAEO-blwa`), product-wide.** "The warm base is the project's configured integration store (W2-116's, a
  path in the project's configuration), never a path of this repository in the code; a project without one rebuilds
  cold, named." Committed in `934e65b9`; merged into the worktree before the lead starts.
- **W2-123 (`DAEO-qzrq`), product-wide.** "The parallel requests and the CPU cap are read from the gate's
  configuration file (W2-20), with the measured defaults; nothing of this machine is written in the code." Committed in
  `ec4ac5b0`; merged into the worktree.
- **W2-121 (`DAEO-cb2b`), item 5.** "A landing never waits for a close it does not conflict with: a running close
  blocks a landing only when a ticket it closes is among the landing's, or while it is committing its records;
  otherwise the landing goes ahead, and two record commits never collide (retried)." Committed in `26665f43`.
  - The CTO's dispatcher v4 builds the same rule here first; it is under independent review.

## 2. The 9 practices and their product tickets

| # | Practice (DEC-1014 item 1) | Product ticket and line | State |
|---|---|---|---|
| 1 | Claims only through the dispatcher's readiness check | W2-82 (the Definition of Ready: `gov claim` checks it, `gov launch` refuses) and W2-121 KPI 2 | covered |
| 2 | The status block generated from files | W2-11, SMART-WORK-4 line 6 | covered |
| 3 | The remaining watchers into dispatcher passes | W2-121 / W2-118, SMART-WORK-4 line 12 | covered |
| 4 | The dispatcher watches the sentinel's heartbeat | W2-121, SMART-WORK-4 line 11 | covered; **the sentinel session stays ours** (§3) |
| 5 | The checkpoint under 300 lines, RESUME HERE first | W2-11, SMART-WORK-4 line 10 | covered |
| 6 | A tool change carries its before-and-after measurement | none | **stays ours** (§3); its audit is W3-P20 |
| 7 | A different model or effort for the second review on fail-open FULL tickets; a lead's agreement is not corroboration | W2-60a and W2-11 | **proposed** lines A and B |
| 8 | The moderator's triage before any round is declared | W2-11 / W2-33 (SMART-WORK-3) and W2-115, SMART-WORK-4 line 5 | covered |
| 9 | Net ticket growth in the daily document; over 5 % a week, a re-plan package | W2-11 | **proposed** line C |
| + | The warm base refreshed after every landing (DEC-1014 item 4) | W2-116 and W2-117 | **proposed** lines D and E |

### Proposed lines

- **A. W2-60a (`DAEO-cv58`), the role, its model and effort loaded at launch.**
  - "On a FULL ticket that could fail open, the second review is launched with a different model or effort setting from
    the first, taken from the role defaults; the launch record shows both, and the same setting twice is refused unless
    the owner named it [DEC-1014 item 1, RESEARCH-AGENT-FAILURES-1 row 4]."
  - SMART-WORK-4 line 3 (reviewer recall per model, on W2-93 / W2-81) then measures whether the difference catches more.
- **B. W2-11 (`DAEO-k7hz`), the orchestration skill.**
  - "Delegation does not count the recommendation and the proposer's agreement as corroboration on a decision that
    touches verification; that needs an independent reviewer's record [DEC-1014 item 1, row 4]."
  - Why: today the kernel skill counts that agreement as corroboration (`template/governance/kernel/skills/orchestration/SKILL.md:38`).
    That is a product defect, not only a practice.
- **C. W2-11 (`DAEO-k7hz`), the orchestration skill's daily document.**
  - "The daily document gives the week's net ticket growth (filed minus closed, counted from the tickets) and the share
    of new tickets that fix the machinery; when net growth passes a configured share of the remaining plan in a week
    (default 5 %), it goes to the owner as one re-plan package with DEC-105's three options, not as single P1s
    [DEC-1014 item 1, row 2]."
  - The 5 % threshold is the research's lowest-confidence figure, so it is configurable.
- **D. W2-116 (`DAEO-f58b`), the integration store in the product.**
  - "The store is also refreshed after every landing on the integration branch, and it is the warm base that
    `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what
    changed since is re-embedded [DEC-1014 items 4 and 6]."
- **E. W2-117 (`DAEO-zkr9`), `gov queue`.**
  - "After each landing, the queue starts the integration store's refresh (W2-116) and seeds its own warm clones from
    it [DEC-1014 items 4 and 6]."

## 3. What stays this repository's own, and why

- **The tool-change measurement (practice 6).**
  - In an adopted repository the orchestrator has no tools lane of its own. Its tools are the Gov OS's commands.
  - Those commands change through tickets, which already need measured evidence (DEC-996 A) and CIT-P (CAP-33).
  - The lane exists here only because the CTO builds tools before the product has them. Each of those tools is retired
    as its product ticket lands: `land.py` → W2-117; `heavy_slot.sh` → W2-20; the dispatcher → W2-121.
  - The independent audit of the orchestrator's commits is parked as W3-P20.
- **The sentinel session (practice 4, the second half).**
  - The Haiku session in tmux that pushes through the Claude app depends on one owner's devices and channels.
  - The product gets the part that does not depend on them: the dispatcher's heartbeat alert (W2-121, SMART-WORK-4 line
    11) through the host's notifier.
  - The full dead-man's switch as a product feature is already parked as W3-P16, to be decided after the two-day trial
    (ACT-SENTINEL-1).
- **The CTO's scratch tools (`.gov-runtime/scratch/orchestrator/tools/`).** They are not practices. Each is mapped above
  and retired as its ticket lands.

## 4. Options

- **(a) Approve lines A to E as written (recommended).** Each is applied when its ticket next runs. Cost: five KPI
  lines, no new ticket.
- **(b) Approve D and E only, the seeding half.** Practices 7 and 9 stay prose only, and the kernel skill keeps
  counting agreement as corroboration.
- **(c) Defer all five to Wave 3.** EXAMIN's orchestrator gets seeding without a refresh, and the corroboration defect
  ships.
