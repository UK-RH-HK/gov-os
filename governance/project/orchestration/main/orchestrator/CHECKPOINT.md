# CHECKPOINT — W2 orchestrator, the CTO (`orchestrator DAEO-sdxk`)

## RESUME HERE — HANDOVER of 2026-10-30 21:36 GMT, for the fresh session after ACT 1 (DEC-955, DEC-957)

**Read first, in order:** `governance/project/prompts/w2-orchestrator.md` §0 (v3.47: DEC-953, DEC-954, DEC-957's
work order and escalation rubric); `governance/project/orchestration/DECISIONS-IN-FORCE.md`; this block. Owner texts
verbatim: `drafts/DEC-953-owner-text.md`, `drafts/DEC-954-owner-text.md`; DEC-955 to DEC-957 in the register.
**Check first:** `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; that ACT 1 is committed (`git log
--oneline -5 -- .claude/settings.json` shows the owner's `ACT-1-GUARD` commit) and the hook is wired (`python3
.gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS` ends
PASS, 38 cases). If ACT 1 is NOT committed: stop and tell the owner.

**State at the handover (main tree clean at `aafd45c1`, nothing staged):**
- Closed on the 10 practices: W2-71 (`9f448448`; own suite back-filled 304/304, `26495f56`).
- Merged, not closed: W2-57, W2-77, W2-03, W2-26 (their batch was STOPPED at 21:19 by the owner, DEC-957 item 1:
  it tested the head with my register fault), W2-61 (merged `758cd53f`, not yet closed).
- Leads running: W2-87 only (started 16:29; register defect first, then authority order; re-measure with W2-61's
  measure). Returns land in `log/<W2>-A5-*.json`; watchers to arm: `tools/lead_return_watch.sh`,
  `tools/interim_watch.sh` (background). Monitors running detached: mem_sampler, usage_watch, oom_watch.
- Returned, waiting for after ACT 1: W2-85 (route done, head `d113ff5ea045`: merge + close), W2-64 (run 2 brief
  `briefs/W2-64-A5-run2.md`: P-W2-64-1 (a) fixture revision, scoped run of the corrected tests only), W2-76 (run 2:
  DEC-956's two items; write `briefs/W2-76-part-run2.md` from its return `log/W2-76-A5-run1.json`), W2-78 parked.
- `CLOSE-HEAD` (scratch) pins closes to `aafd45c1` (corrected register, before ACT 1) until W2-90 lands; then delete.
- The main tree's store was rebuilt 21:20 to 21:34 with the current code (the STORE_MISSING cause: a store built
  before W2-03's `span` column; log `log/rebuild-main-2026-10-30.json`); `gov retrieve` answers `ok: true` there
  again (checked 21:35). Its stderr carries the reranker's progress lines: read stdout alone for the JSON.

**The fresh session's order (DEC-954, DEC-955, DEC-957):**
1. **W2-90 first:** file it (LITE, independent test designer; the owner's named decision under DEC-906, DEC-957):
   revise the 235 live-wiring tests (`/tmp/gov-os-act1/confirmed.json`, if gone re-derive with `tools/act1_tests.py`
   + `tools/act1_confirm.py`; 19 files: W1-46 142, W1-05 77, W2-59 5, W1-47 4, W1-49 2, W1-28 2, W1-50 2, W2-65 1)
   to judge the kernel's wiring, `Rewrite-Reason: DEC-953 item 2`, lowering nothing; claim, worktree, brief, lead.
2. **The batch re-run:** `python3 tools/close_build.py W2-57 W2-77 W2-03 W2-26` (background; full; on CLOSE-HEAD).
   Before it: check W2-54's green-here and time-limit cases alone on a rebuilt clone at `aafd45c1` are green (the
   register re-mark, `6fd19a5f`). Then W2-85's merge and close, W2-61's close.
3. **Then, in parallel within the gate:** W2-64 run 2, W2-76 run 2, the 10 built tickets (W2-67, W2-51, W2-49,
   W2-37, W2-16, W2-84, W2-05, W2-20, W2-52, W2-60a) each finished and closed on the 10 practices (merge
   `w2/integrate` into each kept worktree first, so it carries ACT 1's settings), and the streams S1 memory,
   S2 roles, S3 sandbox, S4 adoption + proving ground.
4. **The roles research session (DEC-957 item 8), now:** a research worker (effort high) on a software company's
   roles and skills from the CTO down (the QA engineer among them; domain engineers as engineer + domain skill),
   what each skill contains, best practice, who integrates (SE per stream, CTO across) and who may push, benchmarking
   as a research skill. Reports to the owner as a package with insights. Until the owner decides: Q6 (the CTO the
   only main-tree writer), the push the owner's.
5. **Memory (DEC-957):** target 95 % (floor 85 %); all seven gaps of `packages/MEMORY-SPEC-MAP.md` closed before
   ready; the 48-question measure (W2-61h writes the 28 new; judged on the hidden half, >= 21 of 24); file W2-86,
   W2-88 (draft `drafts/tickets/W2-88.md`), and tickets for the graph/code-graph routes, embeddings of root files +
   `governance/**` + `schemas/**`, W2-81's hidden half, EXAMIN's question set; apply
   `drafts/plan-dec954/TICKET-EDITS.md` one commit per ticket (and W2-78's three rows).
6. **The roles (ROLES-SPEC-1 approved with DEC-957's answers):** W2-33 r1 (role default lines) before W2-60a's merge;
   W2-11 r1 versions the skill copies; the combined CIT-P; new W2-89 (`gov streams`), W2-00a/b/c; the domain skill
   packs in Wave 2; the escalation rubric into the playbooks (W2-83b).
7. Then ACT 2 (one re-pin), the three layers in new sessions, EXAMIN only when K9's criteria are met.
- **Housekeeping:** remove `~/gov-os-runs/W2-00/close/W2-57+W2-77+W2-03+W2-26-20261030-191445/` (the stopped batch's
  clone; my old guard refused writes there), `/dev/shm/gov-os-W2-76-held.lock`, `/tmp/gov-os-act1/` once W2-90's
  list is taken; brief gaps from today's returns into `governance/project/orchestration/brief-gaps.md`.
- **Milestone 2** (pinged when done): the five closes (W2-71 done; the batch of four), selection proven scoped
  (W2-71: 5,091 tests vs ~16,900 full; ~46 min testing at load 35 after an 83-min lock wait; the batch gives the
  full time), the gates lifted, the guard at five rules. **Milestone 3:** memory and the roles landed.
- **Lessons today:** "lifted" is not "superseded" (status lines are read by the context check); a scoped selection
  must keep the ticket's own suite; nightly-route entries stay out of a close; never `pkill -f`; no backticks or
  braces in inline commands under the old guard (gone after ACT 1); validate parsers' inputs before comparing runs.

## Earlier notes of 2026-10-30 evening (superseded by the handover above)

**DEC-955 (owner): ACT 1 first.** A close refused before ACT 1 is committed is not repaired until it is. Right
after ACT 1 is committed: write the handover (checkpoint + RESUME HERE), tell the owner it is ready, and STOP; the
fresh session starts under the five-rule guard. ACT-1-GUARD: `governance/project/orchestration/packages/ACT-1-GUARD.md`
(+ `.hooks.patch`); trial clone `/tmp/gov-os-act1/repo`; test sweep `tools/act1_tests.py` -> /tmp/gov-os-act1/.
ROLES-SPEC-1 sent (`acbd8353`), awaiting approval.
**19:35 state:** ACT-1-GUARD sent (`bd07b650`, pinged): 235 live-wiring tests (19 files: W1-46 142, W1-05 77, W2-59 5,
W1-47 4, W1-49 2, W1-28 2, W1-50 2, W2-65 1; `/tmp/gov-os-act1/confirmed.json`) go red -> W2-90 (LITE, test designer,
owner's named decision asked) first after ACT 1. `CLOSE-HEAD` pins closes to `9f448448` (pre-ACT) until W2-90 lands;
remove the file then. W2-71 CLOSED `9f448448` (scoped, 5,091 tests, parallel 7,767 s incl. ~83 min lock wait, so
~46 min testing at load 35; 1 flaky candidate W2-54 green-here). Batch W2-57+W2-77+W2-03+W2-26 running (full, pre-ACT
clone). Plan+WBS committed `e814289d`; MEMORY-SPEC-MAP in packages; TICKET-EDITS.md and W2-88 draft in
drafts/plan-dec954 + drafts/tickets for the fresh session (one commit per ticket; file W2-86, W2-88, W2-90; rows of
W2-78). W2-64 run 2 brief ready (`briefs/W2-64-A5-run2.md`), waits for ACT 1. Leads: W2-87, W2-85 running.
**20:35:** W2-76 returned PACKAGES (6.85 h, $11.04; rebuild 307 s, secrets filter 275 s of it). DEC-956 (delegated):
P-W2-76-1 (a) test designer fixes its watchdog case's setup; P-W2-76-3 (a) per-run rebuild-lock override set by the
root conftest, W2-76 paths + `tests/conftest.py`; run 2 after ACT 1. **DEC-956 is appended to the register but NOT
committed** (no main-tree commits while the owner runs ACT 1): commit it, then widen DAEO-tgk2's paths (own commit),
right after ACT 1. Left for removal after ACT 1: `/dev/shm/gov-os-W2-76-held.lock` (guard refused).
**21:05, W2-85 returned PACKAGES** (2.29 h, $5.47): route done (head `d113ff5ea045`), merge + close after ACT 1. Its
findings, all MY slips, fixed in the working tree, NOT committed (ACT window):
- (1) my DEC-866 marks "SUPERSEDED by DEC-953" on 14 status lines (`3f28e09c`) made the context check red on content
  (11 tickets cite them): re-marked as `<original status> · **Lifted by:** DEC-953 (...)` in docs/DECISION_REGISTER.md
  (uncommitted, with DEC-956). Verify after ACT 1: W2-54's green-here and time-limit cases alone on a rebuilt clone.
  The running batch (cloned after `3f28e09c`) will likely be refused on them: DEC-955, ACT 1 first; then re-run the
  batch with CLOSE-HEAD moved to the fixed head (not a repair of those tickets: the cause is the register).
- (2) close_build ran nightly-route entries in its serial phase: fixed (`gov.close.serial.phase`).
- (3) scoped selection ignored the ticket's own acceptance suite: fixed in select_tests.py (own suite kept). W2-71's
  close lacked its own suite: back-fill run on `a4939b45` in `/tmp/gov-os-w271-own/` -> append the result to
  `governance/project/orchestration/closes/W2-71-DAEO-e8f0.md` (commit after ACT 1). Tell the owner either way.

**The plan ahead (owner, DEC-954; PLAN-W2-DEC953 approved with amendments). In this order:**
1. **ACT 1, the five-rule guard** (milestone 2, with its ping): the four of DEC-953 item 2 + rule 5 (independent
   reviewers and auditors write only their own review and audit records in their allowed paths; nothing else),
   and the hidden half refused from EVERY worktree (W2-84's fix, Q9b). Hook: `.claude/hooks/pretooluse.py`;
   check: `tools/guard4_check.py` (planted cases). ACT = the settings regeneration (owner's act), with the
   live-settings tests revised by a test designer. Milestone 2 also = gates lifted, selection proven scoped (4c),
   the five closes (W2-71, W2-77, W2-57, W2-03, W2-26) done.
2. **Then, in parallel, within the resource gate:** the 10 built tickets finished and closed on the 10 practices
   under the five-rule guard (W2-67, W2-51, W2-49, W2-37, W2-16, W2-84, W2-05, W2-20, W2-52, W2-60a — W2-60a's
   scoped last round may finish meanwhile), and the plan's streams: S1 memory, S2 roles/skills/briefs,
   S3 sandbox, S4 adoption and proving ground. Already going before ACT 1: W2-87, W2-86, W2-85, W2-76
   (finish+close), W2-64 (P-W2-64-1 (a): fixtures revised, scoped run of the corrected tests only).
3. **The roles spec first, for the owner's approval** (existing pieces; every role CTO → Senior Engineer → lead,
   test designer, implementer, reviewer, auditor, others: duties, read/write, skills, model, brief contents,
   handover; gaps and the ticket filling each). W2-60b, W2-11, W2-33 (re-scoped), W2-83a/b build nothing
   further until it is approved. One combined CIT-P for the four K3 tickets.
4. **Memory lands, for this repository AND any adopted repository (Q9f):** quick wins W2-86, W2-87 (register fix
   inside), then W2-55, W2-04, W2-05, W2-06, W2-13, W2-15a, W2-32; the measure enlarged (Q9a: ~40-50 questions,
   visible + hidden halves, size and time cost proposed); judged on the combined memory spec (Q9c); the memory
   spec mapped to tickets (Q9d); below 85 % after two rounds -> escalate (Q9e); the any-repository memory ticket
   filed in Wave 2's minimum (assess, plan refactoring as governed tickets, full index + embeddings, SQLite +
   vector store; proven on W2-81's synthetic repos, two messy public GitHub repos, the register's test repos;
   EXAMIN's copy its live trial).
5. **The roles land** (S2: CTO and Senior Engineer roles, skills, briefs; a coordination ticket per stream; the
   CTO's watchers of each Senior Engineer's state).
6. **ACT 2, one re-pin** once memory, the roles and the three layers' foundations have landed.
7. **The three layers start, in new sessions:** the CTO and a Senior Engineer per stream.
8. **EXAMIN's copy only when K9's entry criteria are met** (Q1: gated by milestones and core closes, never by a
   date; dates are weekly estimates). W2-16 cuts the numbered, frozen release W2-81 and EXAMIN install (Q8c).
- **Standing from DEC-954:** closes take the test lock ahead of any lead's full run; W2-78 parked (rows filed);
  W2-67's rounds right after the quick wins; Q10 machine-use breakdown after W2-76/W2-06 and scoped tests;
  W2-20 on DEC-950 in Wave 2 (machine-agnostic in Wave 3); milestones 2 and 3 pinged; the roles spec sent as
  soon as ready.

## Earlier RESUME (2026-10-30 16:20 — DEC-953 IN FORCE)

- **DEC-952 + DEC-953 recorded `6c1b3d3f`** (prompt v3.45 §0, common lead brief with the DEC-953 block). Owner text
  verbatim: `drafts/DEC-953-owner-text.md`. Gates lifted; closes = `tools/close_build.py` (10 practices);
  selection = `tools/select_tests.py` (governance left out; ticket's own merges/merge base).
- **Running:** closes W2-71 (scoped) then batch W2-57+W2-77+W2-03+W2-26 (full), background, logs
  `log/close-build-*.out`, `log/close-build/`. Helpers (in-session agents): PLAN (item 10; returns text, save to
  `governance/project/orchestration/packages/PLAN-W2-DEC953.md`, ping = milestone 1); GUARD switch-off proposal
  (item 2; ACT if owner needed); DECISIONS (item 7; drafts in `drafts/decisions-dec953/`, move to
  `governance/project/orchestration/`, mark DEC-866 status lines).
- **Proof 4c so far:** `log/select-proof-1.json`, `-2.json`: W2-76 scoped; W2-64 full (src/gov/check/schema.py core);
  W2-78 full (close code + test-map); W2-71 scoped; W2-57, W2-77, W2-03 full (core); W2-26 full (UNPLACED research
  docs). Timing comes from the closes.
- **Withdrawn:** ACT-TESTMAP-1, ACT-REPIN-3, P-W2-03-CONTAINMENT (answered). Leads W2-64/76/78 keep building; new
  tickets wait for plan approval except quick wins W2-86, W2-87 (+ register-as-one-record) — to claim and launch.

## Earlier (2026-10-30 — OWNER CHANGE OF COURSE; superseded by DEC-953 above)

- **Owner, 2026-10-30 (chat):** stop dog-fooding the half-built Gov OS; build and test it first. Before anything
  else, an independent read-only audit of every Gov OS feature used to run this repo's development (cost, faults
  caught, standard-practice replacement, keep/lift/replace), as one package with the minimum close practices.
- **Holds until the owner decides from the audit:** ALL closes (no re-queue of W2-71/77/57/26); W2-03's lift;
  ACT-TESTMAP-1 (not committed: W2-66's live test-map test refused it; edit undone, tree clean). Build no new gate,
  tool, rule or package. No new lead starts (read of "before anything else"); running leads W2-64, W2-78, W2-76
  keep building. After-queue list below is on hold.
- **Audit:** `briefs/AUDIT-GOV-FEATURES-1.md`, independent-auditor on DAEO-sdxk, effort max, read-only, return in
  `log/AUDIT-GOV-FEATURES-1.json`; save the package verbatim to
  `governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md`, then ping P1.
- **Audit DONE 14:26** (36 min, $38.58): package committed `a4939b45`, P1 pinged. Recommends DEC-105 option (a):
  build-phase close with §5's 10 practices, gates lifted/replaced per §4, clean `gov close` proof re-run at the end
  (batched by W2-68); W2-03 closes under it; ACT-TESTMAP-1 lifted (2 prose lines, DEC-891 widened, live test
  revised, nightly/** left out). Awaiting the owner's answer: (a)/(b)/(c) and per-feature lifts.
- **Monitors kept:** mem_sampler, usage_watch, oom_watch (old session). Re-armed here: lead_return_watch,
  interim_watch. Wake timers (05:37/07:30/07:45) not yet set again.

## Earlier RESUME (2026-10-30 13:15 GMT — HANDOVER to a fresh session (owner, 2026-10-30 item 6))

**Read first, in this order:**
1. `.gov-runtime/scratch/orchestrator/drafts/RULES-IN-FORCE.md`, the rules in force (53, from the register). It moves to `governance/project/orchestration/` with DEC-952.
2. `.gov-runtime/scratch/orchestrator/log/after-queue-2026-10-30.md`, the work due now, in order.
3. `log/report-state.json` and `tools/status_block.py`: every report ends with that block (DEC-948), then at most five lines on what changed and what the owner must do (owner, 2026-10-30). Keep it accurate; fix stale lines first.

**State at 13:15:**
- **The close queue ended:**
  - W2-03 was refused at 13:08 on `CONTAINMENT_FINDING`. Its merge `b23bf1ac` has two merge bases, so DEC-918 reads every path as its own; against the integration parent its own change is 11 files. All tests passed (16,887 and 104). Package `drafts/P-W2-03-CONTAINMENT.md` is sent; recommended (a), the owner's lift, then re-close as `DAEO-ym8a:DEC-<n>`.
  - W2-71, W2-77, W2-57 and W2-26 did not run. Their merges each have one merge base: re-queue them at once (`tools/close_queue.sh DAEO-e8f0 DAEO-b6hm DAEO-cy5o DAEO-2ds6`, background).
- **The owner commits ACT-TESTMAP-1** (pinged with this handover). Do not commit in the main tree until that commit is in.
- **The order after it:** the after-queue list. In short:
  - resume W2-84 first (`briefs/W2-84-part-run1b.md`), merge W2-61;
  - record DEC-952 (the owner's items of 2026-10-30: memory quick wins, scoped verification, morning close batches, the digest, a fresh session each morning, interim results, the memory-chain line);
  - W2-86 as a path-map line;
  - file and claim W2-87, then W2-55, W2-04 and W2-85, then the leads;
  - re-pin 3's ACT the moment W2-71 and W2-77 close.
- **Leads running:** W2-64, W2-78 and W2-76.
- **Returned, to resume after the closes (all stopped by the 90-minute rule, held by the close queue):**
  - W2-51 (13:09): only its serial phase and a `gov check` re-run are left;
  - W2-84 (`briefs/W2-84-part-run1b.md`);
  - W2-67 (after-queue item 8).

  Write each a short resume part (scoped verification by DEC-952).
  - Returns go to `log/<W2>-A5-*.json`.
  - Start the watchers again in the new session: `tools/lead_return_watch.sh` and `tools/interim_watch.sh`, each in the background, re-armed after each event.
  - Start detached leads with `tools/lead_chain2.sh <spec>` (gate `tools/gate_check.py`, DEC-947 floor 3 GiB; `tools/oom_watch.sh` and `tools/mem_sampler.sh` run detached; `tools/usage_watch.sh` too).
- **Briefs** are built from `drafts/LEAD-w2-common.dec952.md` (DEC-952's scoped verification) with `GOV_BRIEF_COMMON=<that path>`, until it is committed as the common brief.
- **Memory:** W2-61's baseline is hit@5 8/20 (40 %) and full evidence 12/20 (60 %), against 85 and 99 %. Memory is not cut. The re-estimate follows the first quick win's re-measure, with W2-61's measure on a clone, as an unmeasured role.
- **Open owner items:**
  - P-W2-03-CONTAINMENT;
  - ACT-TESTMAP-1 (being committed);
  - the hook injection of the digest (a CIT-P, ask);
  - Q-2 for W2-15a (`DAEO-rd0g`; package to write).
- **Timers:** this session's 05:37, 07:30 and 07:45 waits die with it. Set them again (`tools/wake_at.sh`). The 07:30 package carries the night only (DEC-949); keep 07:15 to 07:35 clear of long foreground work (DEC-951 B).
- **The slips log:** `log/drift-2026-w44.txt`, for the weekly drift count.
- **Never:** commit during a close queue; untracked files in the main tree during a queue; `pkill -f` matching your own command; inline Python with backticks (the guard refuses it: use a script file).

### STATE-OF-GOV-OS (DEC-940)
- Final file with re-pin 3's measured close times, in the first morning package after re-pin 3, at the latest 11-01.
  Drafts: drafts/state/ (STATE-head + annexes A-E). REPLAN-W2, P-SCOPE-RECORDS-1, P-TOOLS-REVIEW-1 are in packages/.

### Now
- **Pin:** gov = pin-5c401220 (DEC-935, registry `bc37c419`); pin-6a4696eb kept. Tools read the pin from
  ~/.local/bin/gov's first line. The nightly route takes 15 entries out of the close (nightly only now).
- **Merged-not-closed:** W2-58, W2-63, W2-07, W2-67 (r1), W2-57. W2-65's worktree kept (guard refused my rm of its
  stray `pytest-of-usain/`) -> digest.
- **ACT-W2-57-LS-1 done** (owner `6367e965`). ACT-W2-57-LS-2 (W1-46 x23, W1-19) next: validate with the new pin
  (`tools/act_clone_run.sh`), then send.
- **Nightly:** committed `governance/project/orchestration/nightly/` (DEC-934; ping gate DEC-936, 28/28 tests);
  crontab 3 lines + Windows wake task (owner, checked). Morning: read status.txt + pings.log, relay P1s (prompt §7);
  digest reports each night's line, estimate vs actual.
- **Lessons:** check tracked files; never commit after `;`; register before a ticket citing it; long commands in
  the background. W2-58's review cases fail inside a Claude session: row.
- **Rows added:** W2-L449, W2-M407, W2-L450. Run clones under ~/gov-os-runs/W2-00 (3G+) never removed ->
  P-TOOLS-REVIEW-1.
- **W2-67** held (probe stale; `d0140d4d`).

### Standing owner rules (short; full text in the register and prompt v3.18; DEC-851)
- **Window (DEC-838):** full window, no compaction threshold. **Checkpoint at every handover (DEC-837);** keep this
  section < 10,000 chars (older text: CHECKPOINT-ARCHIVE.md). **Memory used (DEC-836):** `gov retrieve` in every brief.
- **Parallelism (DEC-847/880):** gate in the launch command (load1 < 20, MemAvailable >= 6710886 kB); never in a
  close's quiet window; ceiling 10; fewer until W2-66.
- **Disk and scratch (DEC-898, `17515bba`):** `bash tools/disk_gate.sh &&` in every launch command (>= 100 GiB and
  >= 10,000,000 inodes free; figures provisional until the owner confirms); queue/nightly/trials call it. Every
  auditor/trial/research brief: 30 GB + 2,000,000 files budget; lead + workers 20 GB + 1,000,000; own TMPDIR,
  pytest's own retention (never per-run --basetemp), clean up as they go, scratch size in the return's evidence;
  over budget -> stop heavy work, return PACKAGES/PARTIAL, I ping P1. W2-20 KPI `efa2e4b0`.
- **Notify (DEC-855):** six-part package in my message + `packages/<id>.md`; start all independent work; LAST ACTION
  `~/.local/bin/owner-ping "<P1|P2|COMMIT|ACT> <id> | gates <...> | <need>"`; never AskUserQuestion; no secret,
  key, held-out path or file content. During a queue: ping only if a close is refused (new or seen cause).
- **Reports:** countdown first, progress line first (DEC-878: closed / merged-not-closed / built-held / in flight /
  not started of 58; keystones done / in progress / ahead of 9); owner acts collected at the top in order (DEC-888);
  last line OWNER_ACTION.
- **Commits (DEC-861, DEC-896):** decision records `Task: decision-record`, `Role: orchestrator`, `Decided-by: owner
  (chat, <date>)`; a commit that changes a ticket file carries THAT ticket's Task (+ Implements); never Role:
  owner; never push. Ratchet entries and code/test/kernel accepted-history entries = the owner's Role: owner commit
  (DEC-862 (a), DEC-891), validated first with the pin's readers (`tools/validate_entry.py`, DEC-895).
- **No placeholders (DEC-893):** exact times only; `tools/placeholder_scan.py` (in record_checks.sh).
- **After every merge (DEC-895):** `tools/probe_impact.py <merge>`; a stale probe of a merged-not-closed FULL
  ticket is scheduled at once.
- **Closes:** `tools/close_queue.sh <ids>` runs gates (c) checkpoint, rebuild, (a) collection, (f) record suites,
  (g) network, (b) gov check, (e) trailers, (h) work-without-a-task (pin's code), (d) tree as the close reads it.
  **Until the first re-pin, no close unless (a)-(h) all predict a pass (DEC-896).** Record edits:
  `tools/record_checks.sh` first; no main-tree commits while a queue runs. Never rebuild-until-green.
- **Policy 1 (DEC-887):** `python3 governance/project/orchestration/sync_context.py --commit "<subject>"` (record/w2;
  safe during closes); `--main` only with a head-moving decision commit, never during a close. Owner's daily push:
  `git -C /home/usain/Dynamic-Agentic-Engineering-OS push origin w2/integrate record/w2`.
- **Supersession (DEC-866):** mark at once, sweep by id and value.
- **Settings changes and ACTs (DEC-925, standing):** any settings change or regeneration -> a full run in the close's
  form on a clone with it applied + a sweep for dependent tests, BEFORE the owner's commit; every ACT's commands in
  `governance/project/orchestration/packages/ACT-<id>.md`, named in the ping.
- **Implements: ids (DEC-927, standing):** gate (e) = `tools/trailer_gate.py` also refuses an Implements item that is
  not a DEC the register holds or a CAP the store holds; leads run it on their worktree before returning
  (LEAD-w2-common); build_lead_brief.py refuses a non-id IMPL. CAP-n reading ACCEPTED by the owner (DEC-928).
- **ACT wording (DEC-928, standing):** "a plain terminal, not a Claude session" only when an ACT replaces or
  reinstalls gov (a re-pin); an owner commit of a patch is run by the owner's operator.

### Plan in force (DEC-933..DEC-939)
- **Merged, not closed (7):** W2-58 (re-close decided, DEC-939 item 3), W2-63, W2-07, W2-57 (re-probe run 4 after
  W2-68's merge), W2-67 r1 (rest held `d0140d4d`, probe stale), W2-75, W2-68 (batch off until W2-77). **Held, 10+ days
  stale:** W2-03, 05, 16, 20, 26, 37, 49, 51, 52 (merge-back each). W2-71 run 2 in flight (F1). Re-pin 3 = W2-68 + W2-71
  (+ W2-77 if ready); each judge improvement re-pinned as it lands (DEC-933).
- **Residual rows to file:** W2-72's F5-F8 etc.; W2-L452 (W2-58 review cases fail inside a Claude session); W2-68's
  F2-F6; W2-71's F2-F7; W2-57's P-1/P-2/P-R2-T1 for the digest.
- **Standing (summary):** full runs `-o tmp_path_retention_policy=failed` under `flock /tmp/gov-os-verify.lock`;
  rebuilds under `flock /tmp/gov-os-rebuild.lock` (DEC-939); tests/acceptance/ only by test designers (DEC-906);
  owner commits = ratchet, accepted_history, exemptions; remove returned leads' temp folders after a holder check.

### Next
1. **Queue end:** commit DEC-939 + DEC-940 (state request) + prompt v3.38 + LEAD-w2-common (rebuild lock, 01:00 cut-off,
   AND the guard's command-form rules: no $VAR write targets, heredocs, backticks, inline python with braces; slip S10)
   + rows + nightly folder (drafts/nightly-next2) + ACT-PUSHOVER-1; tk W2-76, W2-77; queue W2-58; leads W2-77, W2-76.
2. **STATE-OF-GOV-OS + re-plan + P-SCOPE-RECORDS-1 + P-TOOLS-REVIEW-1: ALL DRAFTED** in drafts/state/ (STATE-head.md +
   annexes A..E; REPLAN-W2.md, target EXAMIN start 2026-11-18, range 11-14..11-25; P-SCOPE-RECORDS-1.md -> W2-78;
   P-TOOLS-REVIEW-1.md -> W2-79/80 + auditor). At delivery: add re-pin 3's measured close times to STATE §3, make
   STATE one file (head + annexes) under packages/, commit with the others in the first morning package after re-pin
   3 (latest 2026-11-01's).
3. ACT-REPIN-3, ACT-W2-57-LS-2, W2-67 merge-back + re-probe, then K4 (file W2-55, W2-61, W2-64; resume W2-03, W2-05,
   W2-37) and K3 (file W2-60, W2-56) leads in parallel up to the resource gate.
4. KEEP until the owner says: .gov-runtime/scratch/owner-share/replan-2026-10-29/ and .zip (owner reviewing the re-plan). Next free: DEC-940; ticket W2-78; rows W2-M408, W2-L451 (drafted), W2-L452.

### Never
push/tag/rebase/main; amend w2/integrate; `gov approve`; Role: owner; `rebuild --no-embeddings`; tk close a W2
ticket without the owner; hooks; --no-verify; print secrets or held-out contents, or name the qualification
oracle; ~/gov-os-workbench; grow accepted_reds/load_sensitive; weaken a hard-block check; let the ratchet retry;
`$VAR` write targets (also sed -i); heredocs/backticks in commands (DEC-409).

## Archive
The long history moved to `CHECKPOINT-ARCHIVE.md` beside this file (DEC-792, 2026-10-18).

<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-10-29T14:49:22Z 345890073adc74569c2ee97068be8beab3ba1b8b801bae4f04676e38f9eae8ef
git head: 4f5937653719c10772c6906665e38845b5eabe37
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0z8c [in_progress] - W2-05 The git environment of every check, hook and helper; the settings re-sort <- [DAEO-g0ip]
  DAEO-2ds6 [in_progress] - W2-26 EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)
  DAEO-2gc7 [in_progress] - W2-68 Batched closes, reuse on the same code, and two fingerprints
  DAEO-49o5 [in_progress] - W2-16 Immutable, hash-pinned releases (CAP-43.b lite) <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-5j8b [in_progress] - W2-58 Policy 2 in the guard and the launcher: reads open, four refusals
  DAEO-6n5k [in_progress] - W2-37 gov impact <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-9nys [in_progress] - W2-67 Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions
  DAEO-cy5o [in_progress] - W2-57 Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry
  DAEO-e8f0 [in_progress] - W2-71 The secrets check passes a real commit hash of this repository for row W2-L423's rule only
  DAEO-egsy [in_progress] - W2-51 The Wave 2 plan validator <- [DAEO-g0ip]
  DAEO-ha8z [in_progress] - W2-49 Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P) <- [DAEO-g0ip, DAEO-egsy]
  DAEO-r30l [in_progress] - W2-20 Machine-wide resource gate <- [DAEO-g0ip]
  DAEO-siiz [in_progress] - W2-52 The lite A7 and A10 stage records <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-ym8a [in_progress] - W2-03 Decisions as records, each with its own hash <- [DAEO-g0ip, DAEO-zflj]
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  4f593765 [w2/integrate]
  /home/usain/gov-os-worktrees/W2-00-record   48236df6 [record/w2]
  /home/usain/gov-os-worktrees/W2-03          9a3e3456 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-05          f19f156e [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-07          31ddf173 [w2/W2-07]
  /home/usain/gov-os-worktrees/W2-16          1908149d [w2/W2-16]
  /home/usain/gov-os-worktrees/W2-20          1a54976c [w2/W2-20]
  /home/usain/gov-os-worktrees/W2-26          62c4e477 [w2/W2-26]
  /home/usain/gov-os-worktrees/W2-37          2ff873b2 [w2/W2-37]
  /home/usain/gov-os-worktrees/W2-49          19d45246 [w2/W2-49]
  /home/usain/gov-os-worktrees/W2-51          c2c80e6c [w2/W2-51]
  /home/usain/gov-os-worktrees/W2-52          a21f06a7 [w2/W2-52]
  /home/usain/gov-os-worktrees/W2-57          bd418982 [w2/W2-57]
  /home/usain/gov-os-worktrees/W2-58          09f5ebfa [w2/W2-58]
  /home/usain/gov-os-worktrees/W2-63          ad38ed68 [w2/W2-63]
  /home/usain/gov-os-worktrees/W2-65          f6881547 [w2/W2-65]
  /home/usain/gov-os-worktrees/W2-67          d0140d4d [w2/W2-67]
  /home/usain/gov-os-worktrees/W2-68          05ec0f6a [w2/W2-68]
  /home/usain/gov-os-worktrees/W2-71          c9939587 [w2/W2-71]
  /home/usain/gov-os-worktrees/W2-75          e7f90cd3 [w2/W2-75]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
