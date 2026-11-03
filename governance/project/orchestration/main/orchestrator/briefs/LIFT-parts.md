# The lifting's parallel work (the owner's DEC-1050). Read DEC-1047 and DEC-1050 in
`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (the last entries) and the investigation's list
`governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md` (and `P1-LIFT-1.md`) first.
Reports go to `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/LIFT-1/<part>.md`.
Read-only parts (R1-R3, P1) follow `briefs/INV-common.md`'s rules and return form; engineer parts (E1-E3) follow
`briefs/EMG-common.md`. Gitleaks scanning is lifted here (DEC-1045): run none.

## R1 — does the merge queue and the close already run what `gov check` protects? (the owner's question, DEC-1050 (1)-(4))
For each `gov check` family (`src/gov/check/`, the runner and its declarations): what it protects, its cost, and whether
the merge queue (`.gov-runtime/scratch/orchestrator/tools/land.py`, `governance/project/orchestration/tools/` merge queue
code) and the close (`tools/close_build.py`, the product's `gov close`) already run it or an equivalent on the merged
code, and whether the nightly does (stopped now, DEC-1049). Conclude, family by family, whether leads' `gov check` can go
altogether, and what (if anything) would be lost. Short and exact. Report `drafts/LIFT-1/R1-GOVCHECK.md`.

## R2 — why leads read about 3 % of their brief (DEC-1050 (7))
Who wrote the common lead brief and how it grew (`governance/project/briefs/LEAD-w2-common.md`, its git history: 49
commits since 19 Oct; `tools/build_lead_brief.py`, the part files `briefs/*-part-*.md`); how a lead's brief is built
and delivered (one stdin prompt of about 56,000 characters); what leads actually read, skip and re-read (the lead
transcripts: `~/.claude/projects/-home-usain-gov-os-worktrees-W2-*/*.jsonl`, and their returns in
`.gov-runtime/scratch/orchestrator/log/W2-*.json`; count Read and grep calls on the brief's named files, the decisions
they open, the steps they follow or skip, the brief-gap lines they report); where they get lost (wrong paths, wrong
commands, guard refusals from command forms the brief did not give them, re-reading). What a lead in a 170,000-line
repository actually needs (the right paths, commands, how to report) and what in the brief is noise. Evidence with
counts. Report `drafts/LIFT-1/R2-BRIEFS.md`.

## R3 — templates, as good software companies use them (DEC-1050 TEMPLATES)
Research (WebSearch/WebFetch: engineering handbooks and public templates of well-run software companies and
open-source projects: ticket and task templates, specs and acceptance criteria, definitions of ready and done, design
notes/RFCs, pull-request and review templates, hand-overs and on-call notes; cite each source). Read this repository's
current briefs, role files (`template/governance/kernel/roles/`), skills (`template/governance/kernel/skills/`) and
ticket format (`.tickets/*.md` front matter) to see what exists. Then design, for every role (research and discovery,
product-spec, test designer, engineer, QA and reviewer, lead, CTO) and for tickets and briefs: one template each, short
enough to be read whole and followed, with the right paths, commands and the return form; how every session gets the
same ones (alongside the roles and skills); and how to tell that agents read and follow them. Bring them as spec and
KPI lines for refactoring tasks (each KPI line testable). If `drafts/LIFT-1/R2-BRIEFS.md` exists when you finish your
research, read it and use its evidence. Report `drafts/LIFT-1/R3-TEMPLATES.md` (the templates in an appendix).

## P1 — the refactoring plan, drafted (DEC-1050 THE PLAN)
Draft the plan the owner asked for: every row of the combined list (§3) with its change, marked "approved (DEC-1050)",
"refused (DEC-1050)" or "pending the owner"; the ticket fates (§5); the approved test refactor (P1-INVENTORY-1, DEC-1040:
`packages/P1-INVENTORY-1.md`, `INVESTIGATION-1-COMBINED.md`); the code tidy-up (part E's four coupling edges, the
inventory's §6b); the templates (R3, as one work package); the WBS refactor (DEC-1039 step 3b: `docs/plan/WAVE_2_WBS.md`,
part D). For each step: who does it (role), the order and dependencies, how it is verified (which tests, which review),
the time, and the new estimate for EXAMIN's copy (with its reasoning; the old target was 2026-11-18). Report
`drafts/LIFT-1/P1-PLAN.md`, written so it can be updated after the owner decides the remaining rows.

## E1 — the merge queue: attribution once each way (Q-1) and the landing check on who wrote any acceptance test (G-1)
Engineer, the CTO's tools lane. Q-1: attribute a red once with the batch and once on the head without the batch; no
clone built from the nightly baseline; three rounds only for cases on the load-sensitive list (read the queue's code and
logs: `.gov-runtime/scratch/orchestrator/tools/land.py` and the merge queue under `governance/project/orchestration/tools/`;
the 20:41 run stopped because the head without the batch needed the integration store at its commit). G-1 (it goes in
before the guard's rules 1 and 5 are relaxed): before a ticket is queued, every commit in its range that touches
`tests/acceptance/` must carry `Role: independent-test-designer` (or an owner's `Role: owner`); otherwise the landing
refuses, naming the commits. Build as candidates beside the live files (`<name>.candidate.py`, backups `.pre-dec1050`);
a landing is running now from the live files: never edit them. Committed files: in worktree
`/home/usain/gov-os-worktrees/EMG-queue` (branch `emg/queue`). Tests for both; then the CTO starts one review.
`Task: DAEO-sdxk`, `Implements: DEC-1050`.

## E2 — the hidden `gov check` and the always-added lists out of scoped runs (T-4)
Engineer. W2-54's "green here" cases (they start a whole `gov check` inside a test) and the test map's always-added
lists (`record_reading`, `every_close` in `governance/project/test-map.yaml`) leave every scoped selection and run only
with the full suite (which runs next only on the owner's word, DEC-1050 (5)). The change: the test map's configuration
and the selection code (`src/gov/close/select.py`, about 5 lines; read the investigation's rows T-4 and B1-12/A1-2 for
the measured costs). Worktree `/home/usain/gov-os-worktrees/EMG-select` (branch `emg/select`). Unit tests; the scoped
set; one review follows. `Task: DAEO-sdxk`, `Implements: DEC-1050`.

## E3 — the guard's rules 1 and 5 stop guessing at shell commands (G-2); `rm` free but the catastrophic (O-7 wider)
Engineer. Build candidates of the five-rule hook in
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/` (copies of the
reviewed `drafts/act-guard-fix-3/pretooluse.py` and `bash_writes.py`; never edit `.claude/`). Rules 1 and 5: keep the
Write/Edit checks and the Bash write targets that resolve into a protected folder; a target the parser cannot resolve
is let through (no more guessing); every other rule unchanged. `rm`: allowed freely, except the catastrophic, refused
with a plain reason: deleting the repository's root, its `.git`, the main tree's tracked files, or anything outside the
project (the main tree, `~/gov-os-worktrees/`, `~/gov-os-runs/`) and its scratch (`/tmp`, `.gov-runtime/scratch/`).
Tests: the replay of every logged refusal (`.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl`; W2-42a's
`tests/acceptance/W2-42a/fixtures/refusals.json` on branch `w2/W2-42a` shows how to recover full commands), the planted
cases of ACT-GUARD-FIX-3, and the catastrophic `rm` cases. Then write the owner's ACT (exact commands to copy the hook
files into `.claude/hooks/`, the settings change that stops asking for `rm`, a check, the undo) as
`drafts/act-guard-fix-4/ACT-GUARD-FIX-4.md`. The ACT waits for E1's landing check to be live. One review follows.
