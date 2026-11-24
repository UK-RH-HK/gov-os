# Practice first: the six proposals (DEC-1245 (4)), for the owner's yes

`docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md` · product-spec, 2026-11-24 · Gov OS `w2/integrate` at `ff8951d85` · **proposed, for the owner's yes**; nothing here is built or committed, and the answers come on the page `docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html` (batch B-2026-11-24-practice, 31 cards)

**What the owner asked for.** DEC-1245 (4): six proposals on one decisions page, in the form of his last two: the tool status list, friction from the repositories, old work under new releases, decisions, the rubrics register, data in specs. DEC-1245 (1): "from now, every repository works by the golden workflow v2 as written practice"; products use only the tools proven in real use.

**How it was made.** Memory first: `gov retrieve` ran three times (the store was at `0bd2945b04fe`, one stale path: the register); each bundle was read whole and one search in my own words followed. Then the files named in each source line. `gov decisions in-force` was run for the count (190 lines). Nothing was run to prove a tool; every status below rests on records that exist, and says which. A statement I could not check is marked "not checked".

**Sources, by short name.** "TOOL-MAP row n" is `docs/emergency-2/integration/TOOL-MAP.md` §1; "RECORDS-MAP" is `docs/emergency-2/integration/RECORDS-MAP.md`; "I-n" is `docs/emergency-2/integration/FINDINGS.md`; "plan n-n" is `docs/emergency-2/integration/INTEGRATION-PLAN.md`; "HELD" is `docs/emergency-2/integration/DECISIONS-HELD.md`; "audit 4" is `docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md`; "A-n" is audit 4's List A; "GW" is `docs/emergency-2/GOLDEN-WORKFLOW.md`; "W1 to W16" are GW's steps.

**The answer in six lines.**

1. **Tool list:** 52 tools in the 16 steps: **17 green, 17 amber, 18 not yet in the product**. It keeps every tool in the status the owner expected. It adds "not yet" rows beside four of them (memory's refresh and schedule, the kit's settings, adopt's verdict and imports, accept's two missing checks) and puts a rule on two greens (`gov update`, `gov doctor`).
2. **Friction:** one log per repository in eight fixed columns, collected daily by a read-only pull, a stopper pushed at once, status brought back by the product's own session.
3. **Old work:** every record carries `release:`; closed work is never re-checked; new rules read the field, as `ready.new_since` already does for one date.
4. **Decisions:** 190 are in force. Of the 30 that HELD classed (DEC-1209 to DEC-1238): **1 held by code on the path, 6 spent, 3 partial, 20 text or not built**; 153 older and 7 newer are not classed. At least **7** would leave agents' reading now, at most about **18** from what is classed today.
5. **Rubrics:** 20 rubrics found, each with its decisions and its enforcement; one file, `docs/RUBRICS.md`, and a kit copy.
6. **Data in specs:** the spec form already has a `## Test data` table that `check_spec.py` reads; the proposal adds kinds `none` and `real`, a `path`, the KPI lines served, and a ready check that goes red when the data is not there.

---

## 1. The tool status list

**Problem.** DEC-1245 (1) says products use only tools proven in real use, and each release ships a list with a green, amber and "not yet" status for each tool. No such list exists. Without it a repository's CTO cannot tell a tool that works from a tool that is built (GW §1 "Today" column is typed by the CTO and says "partly" for 11 of 16 steps).

**Proposal.** One row for each tool the golden workflow's steps use, from TOOL-MAP §1 (102 rows, of which 55 are in the product and 37 outside it; I kept the ones a product's steps need, 52). Three statuses:

- **Green:** proven in real use (named: EXAMIN, W2-81's run, Gov OS's own work), and no open finding that fails open or loses work in ordinary use. Use it now. The row says what to read to know it worked (a record, not the exit code, DEC-1240).
- **Amber:** built, not proven. The step is done by hand as the workflow says, the plain path (plan §1 rule 1); the row says what the hand step is.
- **Not yet in the product:** no product code, or the code is a scratch script outside the kit. The row gives the documented equivalent meanwhile (a cron line, a hand step).

**What code holds and what stays practice.** Code holds nothing of the list's content: the CTO sets it from the tool map and the findings (DEC-1245 (1)). Code holds three things: the machine copy is read by `gov doctor`, which prints it and the release it describes; the first line of `gov retrieve` already prints the store and HEAD commits; a green row names the record that proves a run (the "It must produce" column), so a CTO reads the record and not the exit code (DEC-1240; I-11 passed its scoped runs and failed the full suite). The statuses and hand steps are practice.

**Where it lives, so adopted repositories get it.** (a) `docs/releases/<v>/TOOL-STATUS.md`, for people, one for each release, written by the CTO before the owner builds the record (I did not check whether `gov release` hashes extra files in that folder). (b) `governance/kernel/tool-status.yaml` in the kit: a machine copy that `gov update` carries, because the project overlay is never overwritten by an update (IMPORTS spec line 72). It sits in the kernel folder, with no schema, because a patch release cannot add or remove a kit schema (DEC-1223 (7), P5; `LEAD-fixes-015b.md` F2); the schema comes with the next full release. (c) A `gov doctor` part `tool_status` prints it (W2-22, DAEO-xm6l, a fix of size S).

**Rides.** The markdown for release 0.1.5 is a chore the CTO can commit now; products need it today. The machine copy and the doctor part ride Phase 0 and the first patch release after 0.1.5, with memory first (DEC-1245 (2)). Plan items 3-1, 3-2 and 4-1 turn rows green when they pass on the scratch repository.

**How a tool moves.** Amber to green: the integration proves it on the scratch repository (DEC-1245 (1), the test of DEC-1240), and the next release's list says so; products gain it through `gov update`. Green to amber: not decided anywhere; the proposal is at once, in a patch release, when a finding marked "blocks or loses work: yes" (proposal 2) names a green tool.

### The list

Counts: **17 green, 17 amber, 18 not yet** of 52. "It must produce" is for green rows only.

| # | Step | Tool | Status | Why, and where it was proven or fails | It must produce (green) | Hand step, or the equivalent meanwhile |
|---|---|---|---|---|---|---|
| TL01 | W1 | `gov adopt` stages A0 to A10 and AS | **green** | Ran on EXAMIN (the W2-27 run) and on the six W2-81 repositories on 0.1.4: one has no A10 (analysis R11, the rust map with a path in two namespaces, A9 `FABRIC_INCOMPLETE`); the run's other reds are the verdict, findings and test set-up (R2 to R8). Open: A4 not built, A2 reads doctor's glob (RECORDS-MAP §0 (2), (3), §3.4). | one commit per stage, `governance/adoption/<stage>-*.md`, no `CHAIN_BROKEN` | After A3 run `gov check` (core-pathmap) and compare `git ls-files` with the map by eye; keep no root `*` namespace. |
| TL02 | W1 | Adoption verdict stage (CAP-44.h) | not yet | On `e2/d1-verdict`, not merged (TOOL-MAP row 1; plan 5-8). | — | The A10 auditor's record is read by the CTO, who writes the verdict as the first line of the adoption note and tells the owner. |
| TL03 | W1 | Imports step (use, absorb, study) | not yet | A spec only; the fourth stream starts when EXAMIN's fresh 80 passes (X-3; IMPORTS-ADOPTION-SPEC). | — | The adopter lists what the repository brings in and gives each use, absorb or study, with its licence as the licence file states it, in a table in the adoption record (a note, never a gate: IMPORTS spec line 66). |
| TL04 | W1 | `gov adapters` with `rulesync` | **green** | Generates the files of an adopted repository (EXAMIN's generated block, `portability.py:415-446`); slots fixed in 015a F11. I-16 (a second generated block) hit Gov OS's hand-written head, which has no markers. | CLAUDE.md and AGENTS.md hold one copy of the head and are equal | Never run `gov adapters generate` on a head written by hand without `gov:generated` markers (I-16); edit the head by hand and keep the two files equal. |
| TL05 | W1 | Kit settings: the two denies, five hooks, `disableClaudeAiConnectors` | **green** | Reached EXAMIN (`.claude/settings.json:4-9`); the connectors key is in the kit since 015a F1 (`template/governance/kernel/settings.json:8`), so in a repository from release 0.1.5. | `.claude/settings.json` holds the two deny lines and the connectors key | None. |
| TL06 | W1 | Kit settings: `defaultMode` and the model hook `agent_model.py` | not yet | The kit has neither (grep over `template/`; TOOL-MAP rows 3, 57; plan 4-2). An adopted repository's own sessions prompt; EXAMIN runs an older hook copy of 2,124 bytes. | — | Copy Gov OS's `.claude/hooks/agent_model.py` and its hook line, and add `"defaultMode": "bypassPermissions"` under `permissions` in the repository's `.claude/settings.json` (Gov OS's own, lines 75 to 83). |
| TL07 | W1 | A machine too small refused at adoption and install (P-8) | not yet | No check at adoption or install (TOOL-MAP row 45; plan 3-7). | — | Run `gov resources --check` before adopting; `gov launch` already refuses with a reason (exit 3). |
| TL08 | W2 | `gov rebuild` (builds the store) | **green** | Runs after every Gov OS merge and builds EXAMIN's store; today's `gov retrieve` header reads `store 0bd2945b04fe ... head ff8951d853e1, 1 stale path`. Open: stale and legacy documents are not kept out by default (route in 0.1.6; W2-81's A4). | the store's commit equals HEAD (first line of `gov retrieve`) | Keep legacy folders in an `archive-legacy` namespace the path map does not index (EXAMIN `path-map.yaml:232-243`). |
| TL09 | W2 | The code-graph binary `codebase-memory-mcp` and the `ollama` wrapper | not yet | Outside the product, installed by hand and shared by every repository on the machine (TOOL-MAP rows 6, 7; plan 4-1). | — | Nothing to install per repository; `gov doctor` checks the registered tools. |
| TL10 | W2 | `gov retrieve` | **green** | Used in every session; this document's own bundle ran today. The bundle is cut at 6,000 tokens (A-11). | a bundle with ids and paths, and a `stale` list that is empty or named | The agent reads the whole bundle printed, then searches once more in its own words (CLAUDE.md). |
| TL11 | W2 | `gov memory-use` | amber | A typed log; helpers log no role (A-35; TOOL-MAP row 9). | — | Nothing depends on it; count memory use from the findings if the owner asks. |
| TL12 | W3 | Refresh after each commit (the `reference-transaction` git hook) | not yet | Untracked in `.git/hooks`, fires only for `w2/integrate`, in no adopted repository; a failed refresh was not retried (I-9: `REBUILD_FAILED` 22 November 13:53:49, store 23 commits behind; TOOL-MAP row 11; plan 0-1, 0-3). | — | Run `gov rebuild` after each merge batch; a cron line `30 3 * * * cd <repo> && gov rebuild >> .gov-runtime/refresh.log 2>&1` (not tried on a product); read the first line of `gov retrieve` and rebuild when it shows a store behind HEAD. |
| TL13 | W3 | The embedders started at boot | not yet | A `@reboot` cron line to a scratch script (I-7; TOOL-MAP row 12; plan 3-2, MA-5). | — | The two embedding servers are the machine's, shared by every repository: one `@reboot` line in the crontab, not one per product. |
| TL14 | W4 | `gov memaudit` (the fresh 80) | **green** | First fresh 80: 78 of 79 right (DEC-1098); W2-81 graded five repositories; the stamp (F15) and the strict rule (D5) are merged for 0.1.5; I-11 (declare refused sets with no forbidden list) is fixed (`87f11837a`). | `FIGURES.json` with release, commit, models, rule and the end-to-end figure | EXAMIN's fresh 80 on 0.1.5 is the next proof. |
| TL15 | W4 | The weekly schedule of the measure | not yet | No crontab line runs it (TOOL-MAP rows 15, 92; plan 3-3). | — | One weekly cron line per repository: Monday 21:00, `memaudit_cron.sh --repo <dir>` (its header; it runs what is due and exits 5 when a writer's delivery is awaited). The script sits in Gov OS's tools folder, outside the product. |
| TL16 | W5 | `gov decisions in-force` and `basis` | **green** | The CTO reads the digest at every start (`role-cto.md:39`); `basis` is typed; nothing runs it at a commit (A-28). | 190 digest lines today; `basis` prints no `BASIS_MISSING` for a new rule | Run `gov decisions basis --range <A>..<B>` before committing a decision. |
| TL17 | W5 | Levels from the record, refusal below the level, `gov decisions answer`, the page, the push | not yet | Not built (TOOL-MAP rows 17 to 21; F-2 and F-3, plan 5-4, 5-5). | — | The page by hand in this form (HTML and a GOV-ANSWERS 1 sheet); the CTO writes the register entry with `Decided-by: owner (chat)`; a stopper pushes through Claude Code's own push (TOOL-MAP row 20). |
| TL18 | W6 | `gov impact` | amber | No caller; over 106 s and a 150 s timeout on one decision id (I-5; TOOL-MAP row 22; plan 1-8). | — | Trace by hand: `gov retrieve "<id> affects"` and `grep -rn "<id>" docs .tickets src tests`. Do not run `gov impact` on a record id. |
| TL19 | W6 | `gov links` | amber | Typed; automatic only in the landing; no `KPI_DRIFT` (TOOL-MAP row 26). | — | Run it before a return (`role-lead.md:79`); compare a ticket's KPI lines with its spec by eye. |
| TL20 | W7 | `gov plan` | amber | Typed; the ready list is hand-written (TOOL-MAP row 30). | — | Order the waves by hand from `depends_on`, `waits_on` and write paths. |
| TL21 | W7 | `gov readiness` | amber | Typed; no plan item is checked before work starts (TOOL-MAP row 31). | — | Run it on each spec and ticket before the brief. |
| TL22 | W7 | `gov discover` and `check_spec.py` | amber | Built, unused by Gov OS's planning, wired into no gate (TOOL-MAP rows 32, 33). | — | Write the spec and ticket from the templates; run `check_spec.py` on each spec by hand. |
| TL23 | W7 | `gov check` (G1 to G3, schemas, core-pathmap) | amber | Typed; nothing schedules it (A-29); a ticket-only change skips the schema check at the land (RECORDS-MAP §1.1). | — | Run `gov check` after each merge. |
| TL24 | W8 | `gov brief` | amber | EXAMIN ran it 3 times, Gov OS none; the bundle in a brief is cut (A-11; TOOL-MAP row 36). | — | Write the brief from `templates/brief.md` with the whole memory bundle pasted; run `gov brief <ticket>` to print the ready check even when the brief is written by hand. |
| TL25 | W8 | `gov launch` | amber | No launch record in Gov OS or EXAMIN since 16 November (TOOL-MAP row 37; audit 4 §1.1). | — | Start `claude -p` from the brief with model and effort by the table (CTO and senior engineer Opus high; ticket, fix and chore leads Sonnet medium; every other role Sonnet high; DEC-1242 R-4) and `--strict-mcp-config`. |
| TL26 | W8 | `gov dispatch` and the run-time tool | amber | Built; the cron runs the old scratch tick, which starts nothing (TOOL-MAP rows 42, 43; W2-207). | — | The CTO starts and watches leads by hand, within what the machine holds. |
| TL27 | W8 | `gov resources` (the gate) | **green** | Inside `gov launch`, every test slot and the memory cron line; exit 3 when shut. | exit 0 open, or exit 3 with a reason | None. |
| TL28 | W8 | `gov pause` | amber | Read by launch, queue and `release --patch`; the starters read it from 0.1.5 (015a F10); not shown in use. | — | The owner types it; a product has no starter but its CTO. |
| TL29 | W8 | `gov spend` (the brake) | amber | Runs inside `gov launch`; `check` never scheduled and never fired (TOOL-MAP row 47). | — | The CTO reads usage by hand (TL49). |
| TL30 | W9 | Red on the base | not yet | No code (TOOL-MAP row 52; plan 1-3). | — | The test designer runs the acceptance folder on the base commit and pastes the red output into its return; the CTO reads it before the engineer starts. |
| TL31 | W9 | The acceptance map pre-check (`gov accept --map-only`) | not yet | Not built (A-12; plan 1-10). | — | The designer runs `gov accept <ID>` once to see that the README map parses. |
| TL32 | W10 | `gov accept` | **green** | Typed by every lead; W2-209 128 of 128 (CTO-HANDOVER.md:53); runs at the land. 66 of 188 old folders fail the map parse (RECORDS-MAP §1.2). | pass or fail per KPI line, in JSON | An old ticket's unreadable map is not the test; only new tickets are judged by it. |
| TL33 | W10 | The helper's return hook (SubagentStop) | **green** | In the kit; its three bugs fixed in 015a F12. | a return missing a field is refused | None. |
| TL34 | W10 | The lead's return form | not yet | Two forms disagree and nothing checks them (TOOL-MAP row 56; A-7). | — | Use `LEAD-COMMON.md:30`: branch, head, KPI evidence, reds not yours; decide, never ask (I-10). |
| TL35 | W11 | The landing (`gov queue`; `gov land` from plan 1-1) | amber | One real landing, `4f779086f` (22 November); I-1 and I-2 fixed in 0.1.5 and verified; then `fixes-015a` was merged by hand and 95 reds followed (I-14); exit 3 in all six W2-81 repositories; no `queue.yaml` in Gov OS. | — | The plain path (INTEGRATION-PLAN §1 rule 1): merge by hand in a clone; run `gov accept`; run the tests of the folders the change touches and the suites `test-map.yaml` names (the list `gov queue --select` prints, when it runs); check authors with `git log --format='%h [%(trailers:key=Role,valueonly,separator=)]' <base>..<branch> -- tests/acceptance` (CTO-HANDOVER.md:50); run `gov check`; record the merge. |
| TL36 | W11 | A red's diagnosis record (DEC-1242 T-12) | not yet | No form (plan 1-6). | — | `docs/probes/<ticket>/<n>.md` with one `cause:` line for each red id, by the CTO. |
| TL37 | W11 | Path-map coverage at the landing (G-8, Q-1) | not yet | `core-pathmap` runs only as an after-step notice (RECORDS-MAP §0 (1); plan 1-11). | — | Run `gov check` after each merge; put the line for a new folder in the same commit. |
| TL38 | W12 | `gov launch --fix` and `--chore`, the fix record | amber | Built, used by nothing (TOOL-MAP rows 68, 69). | — | A fix: failing test first, then a `## Fix:` section in the owning ticket and a `Fix:` trailer. A chore: a direct commit with `Task: chore` and `Class: C`. |
| TL39 | W12 | `gov land --direct` for chores that touch code | not yet | Not built (A-16; TOOL-MAP row 70). | — | As TL38; list the chore in the digest by hand. |
| TL40 | W13 | `gov release` (full) and the re-pin | **green** | Cut 0.1.0 to 0.1.4, each re-pinned with self-rollback (`docs/releases/`; TOOL-MAP rows 72, 74). | `docs/releases/<v>/manifest.json` verified, a tag, `~/.local/bin/gov` re-linked | None. The owner cuts. |
| TL41 | W13 | `gov release --patch` | amber | Switched off (`patch_releases: off`); gate G2 reads a nightly record while the nightly is off (TOOL-MAP row 73). | — | The owner cuts. |
| TL42 | W14 | `gov update` | **green** | First updates found two bugs, both fixed for 0.1.5 (merge `2cadc0cf8`): `context_watch.py` twice in EXAMIN (report 28, F4) and `gov doctor` red after the update in 6 of 6 W2-81 repositories (22 November, F6). Not re-run on a real repository yet. | `governance/updates/<B>.json`, and `gov doctor` no worse than before | After each update run `gov doctor`; if it is worse, `gov update --rollback` (one revert commit) and log a finding. |
| TL43 | W14 | `gov install` and the pin | **green** | Used in every re-pin; hash-verified (TOOL-MAP row 76). | a pinned environment, hash checked | None. |
| TL44 | W15 | `gov backup` | **green** | Hourly for Gov OS and EXAMIN (crontab line 7), with one 41-hour gap, 20 to 22 November, that nothing noticed (A-8). | a verified bundle newer than 70 minutes in `~/.gov-os/backups/` | One cron line per repository: `7 * * * * gov backup --root <repo> --name <name>`. |
| TL45 | W15 | `gov checkpoint` with its hooks | **green** | PreCompact, Stop and SessionStart run in every session; scratch checkpoints are kept up to 24 November; a lead has no `GOV_TICKET`, so writes none (RECORDS-MAP §1.3). | a checkpoint record with `next_action` | The CTO's morning handover is a checkpoint with a `RESUME HERE` section, by hand (DEC-1242 T-13). |
| TL46 | W15 | `gov msg` | **green** | Wake messages between sessions (TOOL-MAP row 80). A message to a running `claude -p` lead is never read. | the message in the inbox | Change a lead's scope in its brief or at the landing. |
| TL47 | W15 | The scheduler (`gov dispatch pass` and its one cron line) | not yet | Built in slices; the old scratch watchers are live (TOOL-MAP row 43; plan 3-1). | — | The cron lines of TL12, TL13, TL15, TL44 and TL48, and `gov doctor` weekly: `0 20 * * 1 cd <repo> && gov doctor >> .gov-runtime/doctor.log 2>&1`. |
| TL48 | W15 | The 3-hour stall push | not yet | `tools/stall_check.sh` in Gov OS's scratch folder (DEC-1243 (4)); retires with plan 3-13. | — | A copy of that script in the product's own run folder with its two path lines changed, on cron every 15 minutes. |
| TL49 | W15 | Usage and context figures, pushes at 95 and 99 % | not yet | Scratch `usage_log.sh` and `cto_watch.sh` (TOOL-MAP rows 82, 83; plan 3-10). | — | The plan is one figure for the machine and Gov OS's CTO's watcher already sees it; a product's CTO adds nothing. |
| TL50 | W15 | `gov status` and the status block | amber | `gov status` never refuses; the status block is the scratch `status_block.py` (TOOL-MAP rows 71, 86; plan 3-12). | — | End each report with the block by hand: tickets landed, chores, fixes and counts from `git log` and `.tickets/`, never copied forward (DEC-1216 (3)). |
| TL51 | W16 | `gov doctor` | **green** | Ran on the six W2-81 repositories and in every update rehearsal. On a map with a root `*` (Gov OS's) `path_map` passes with unmapped files (RECORDS-MAP §0 (2)); EXAMIN agrees under every matcher (§3.3). `path_compliance` fails on EXAMIN for moved-path text (F-009). | one healthy or drift line for each part | Read `path_map` as proof only for a map with no root `*`; read `path_compliance` as a notice. |
| TL52 | W16 | `gov telemetry` | amber | Typed; no schedule (TOOL-MAP row 90). | — | Nothing depends on it. |

### Where the evidence differs from the owner's expected list

| The owner expected | Evidence | The list says |
|---|---|---|
| Green: memory and its measure | Build, retrieve and the measure are used daily (TL08, TL10, TL14). The refresh hook is untracked and fires only for `w2/integrate`; a failed refresh was not retried (I-9); the boot start and the weekly measure are cron lines to scratch scripts (TOOL-MAP rows 11, 12, 15) | Green for TL08, TL10, TL14; **not yet** for TL12, TL13, TL15, each with its cron or hand equivalent |
| Green: `gov adopt` | Ran on EXAMIN and six W2-81 repositories; the verdict stage and the imports step are not at HEAD; A4 is not built (TOOL-MAP row 1; RECORDS-MAP §3.4) | Green for A0 to A10 and AS (TL01); **not yet** for the verdict (TL02) and imports (TL03) |
| Green: `gov update` | Two real bugs (hook twice, doctor red 6 of 6), both fixed for 0.1.5, not re-run on a real repository (`LEAD-fixes-015b.md` F4, F6) | Green with the rule "doctor after, roll back if worse" (TL42) |
| Green: `gov doctor` | `path_map` passes with unmapped files on a map with a root `*` (RECORDS-MAP §0 (2)); adopted maps have none | Green with two read-rules (TL51) |
| Green: `gov accept` | 66 of 188 old folders fail the map parse; new ones parse (RECORDS-MAP §1.2) | Green (TL32); the two missing checks are **not yet** (TL30, TL31) |
| Green: the kit's settings | The two denies, hooks and connectors key are in the kit. `defaultMode` and the model hook are not (TOOL-MAP rows 3, 57) | Split: TL05 green, TL06 **not yet** |
| Amber: the landing, `gov launch`, `gov brief`, `gov impact`, the dispatcher | Confirmed (TL35, TL25, TL24, TL18, TL26). `gov impact` must not be run on a record id (I-5) | Amber, with that rule on TL18 |

### Options and costs

- **(a) Approve the list as drafted** (recommended). Cost: the CTO re-reads it at each release until the enforcement field fills it (GW "How to read"; A-23).
- **(b) Approve with the owner's changes.** Cost: the CTO applies them before the first product uses the list.
- **(c) Not yet:** products use only the tools the owner named. Cost: no hand steps are written, and the greens beyond his list (TL04, TL16, TL27, TL33, TL40, TL43 to TL46) become amber by default.

Alternatives for where it ships and how a tool moves are cards TL-10 and TL-11 on the page.

---

## 2. Friction from the repositories

**Problem.** Gov OS finds its bugs by running its own work (FINDINGS.md has I-1 to I-16). Products will hit others, and silent ones. Today a product's CTO has no place to write them and Gov OS has no way to read them, so a bug in a green tool could sit in one repository for weeks (I-9 and the 41-hour backup gap, A-8, both went unnoticed).

**Proposal.**

1. **One log in each repository, in a fixed form:** `governance/project/findings/FINDINGS.md`. It sits in the `project` namespace the kit's path map already holds (`template/governance/project/path-map.yaml`: `governance/project/**`), so no new map line is needed, and `gov update` never overwrites it. A markdown table with these columns, in this order:

| Column | Holds |
|---|---|
| `id` | `F-<n>` within the repository |
| `what happened` | one or two sentences |
| `evidence` | a path:line, a command and its output, or a record id |
| `Gov OS release` | the release the repository was on (from `governance/framework.lock`) |
| `step` | W1 to W16 |
| `blocks or loses work` | `yes` or `no`: yes only if ordinary work hits it and it fails open or loses work (the golden rule's "what may block") |
| `kind` | `bug` (in a green tool, silent ones included), `workflow-gap`, `hand-step-pain` (on an amber tool), `missing-capability` |
| `status` | `open`, `routed <where>`, `fixed in <release>`, `decided <DEC>`, `wave-3`, `closed <reason>` |

2. **Collected by code, daily.** A new read-only command, `gov findings collect`, reads each registered repository's log at its integration branch's head with `git show`, checks the form, and writes a machine copy and a daily digest under `~/.gov-os/findings/` (machine state, outside every worktree, like `~/.gov-os/inbox/`). A registry file, `~/.gov-os/findings/repos.yaml`, names each repository, its path and its branch. Until the scheduler holds it (plan 3-1), one cron line runs it each morning.
3. **A stopper pushes the owner at once.** A row with `blocks or loses work: yes` is a stopper. The product's CTO pushes the owner at once, as for any stopper (DEC-1217 (5)); the collector also wakes Gov OS's CTO through the inbox, who pushes if no push was seen. A push by code waits for plan 3-13.
4. **Routing, by kind.** Bug: a fix under its owning ticket, failing test first, in the next patch release, and it arrives by `gov update`. Workflow gap: a change to the workflow for the owner's yes, on the next page. Hand-step pain: it orders which amber tool is proven first (the integration plan's order is re-read each time). Missing capability: a Wave 3 candidate (EMERGENCY-2 §8.4).
5. **Status written back.** The collector writes each row's status to `~/.gov-os/findings/<repository>.status`; the product's own session applies it to its own log with one command, `gov findings sync`, at its start. No code writes into another repository's worktree (a dirty worktree makes the landing refuse, `QUEUE_WORKTREE_DIRTY`, 015b F8).
6. **Judge tools by what they produce.** Each repository CTO checks the record a green tool must produce (the "It must produce" column of proposal 1), not its exit code. A tool that exits 0 and leaves no record is a finding of kind `bug` (I-11: scoped runs were green, the full suite was red).

**What code holds and what stays practice.** Code: the form check, the collection, the daily digest, the status feed, `gov findings sync`. Practice: writing the rows, the CTO's routing, the push by the repository's CTO (until 3-13).

**Where it lives in the kit.** The log template: `governance/kernel/templates/findings-log.md`. The row schema: `governance/kernel/schemas/findings-row.schema.json` (a kit schema is added, so it ships with the next full release, DEC-1223 (7) P5); until then the CTO uses the template and the collector checks the columns in code. The practice line goes into the head of CLAUDE.md and AGENTS.md through the kit's rules file `template/.rulesync/rules/governance.md` (a kernel text change: the CTO's, with the owner's yes).

**Rides.** The log form is practice from today. `gov findings collect` and `sync` are a new feature (the owner's yes adds it, plan §1 rule 3): size S to M, about $2.50 to $6.60 at the plan's unit costs, in stream S beside 3-1 and 3-3. Gov OS's own `FINDINGS.md` (I-1 to I-16) adopts the form when its next row is written; old rows stay (proposal 3).

**Options and costs.** The page has one card for each real choice.

- **Approval:** (a) approve (recommended); (b) with changes; (c) keep Gov OS's seven-column shape for all repositories: cost, no `kind` or `blocks` column, so a stopper cannot be read by code.
- **How collected:** (a) a daily read-only pull (recommended): a new command; (b) each CTO sends rows by `gov msg`: cost, it relies on goodwill and has no form check; (c) Gov OS's CTO reads each log by hand: cost, it is today's way and it missed I-9 for a day.
- **Status back:** (a) by release and `gov update` only: cost, slow for non-bugs; (b) the machine status file and `gov findings sync` (recommended); (c) the collector commits into the product's log: cost, a cross-repository write and a dirty-worktree refusal.
- **A stopper:** (a) the CTO pushes at once and the collector backs it (recommended); (b) the collector only: cost, up to a day late; (c) shown in the morning brief: cost, against DEC-1245 (4).

---

## 3. Old work under new releases

**Problem.** Rules and forms change each release. A new rule that is read as applying to old, closed work either blocks it or forces a rewrite of history. Today a date does this job for one rule: the ready check applies `reads`, `needs` and `waits_on` only to a ticket created on or after `ready.new_since` (`facts.yaml:185-189`; `brief/build.py:170`). No record carries the release it was made under: 0 of 271 tickets have a `release:` line, and no schema names one (grep over `.tickets/` and the kit's schemas).

**Proposal** (DEC-1245 (4)).

1. **Every ticket and every record carries the release it was made under:** a `release:` field (the version, `0.1.5`), set at creation by the tool that creates it, from `governance/framework.lock`. Where: tickets, specs, plans and waves, close records, decision entries, findings rows (`Gov OS release` column).
2. **Closed work is accepted as it is and never re-checked** against a rule newer than its release.
3. **A new rule applies only to work created after it.** Each check names the release it starts at (`since_release`) and reads the field, as `ready.new_since` does with a date and as Q-6 does for `gov accept` ("for tickets created from the change on; older ones exempt").
4. **A reopened ticket moves to the current forms then,** that ticket only: its first commit brings its front matter to the current form and sets `release:` to the current one.
5. **A rule that stops lost work or a fail-open applies at once,** to all work, old included (the golden rule: that is the only kind of finding that blocks). Its decision record says so in one line, `Applies: at once, <reason>`.
6. **`gov update` never rewrites history.** It writes only the kernel, the kit's files and its own update record; the project overlay and closed records are not touched (`update/core.py:593`, the overlay check).
7. **`gov doctor` shows earlier forms as a notice:** a count by release and the record paths, never a failure.

**What code holds and what stays practice.** Code: the field set at creation (`gov discover --ticket`, `tk`, the landing's close record); the schema property; each check reading `since_release` against the record's `release:`; doctor's notice; `gov update`'s refusal to touch the overlay. Practice: the owner's rule that closed work is not re-checked; the CTO marking a rule `Applies: at once`; the reopening session moving its ticket.

**Where it lives in the kit.** A `release` property in the ticket, specification, close and plan schemas (`template/governance/kernel/schemas/`; a property is added to existing schemas, not a schema added, so it is not blocked by RB-7 P5); a `since_release` key in each check's declaration (`governance/kernel/checks/*.yaml`); doctor's notice in `src/gov/doctor/`.

**Rides.** Practice from today: new tickets and specs carry `release:` by hand. Code: plan item 2-11 (the ticket schema: `kind`, `specification`; add `release` there), the checks of 2-3, 5-10 and 5-11 read it, doctor's notice rides 3-6 and 3-11. One change is needed at the start: Q-6's `ready.new_since` date becomes a release.

**Old work with no field.** Its release is derived from its `created:` date and the release dates in `docs/releases/<v>/`, by code, and never written back. 0.1.0 to 0.1.4 have records; work older than 0.1.0 is "before 0.1.0".

**Options and costs.** Cards OW-0 to OW-3 on the page.

- **Approval:** (a) approve (recommended); (b) with changes; (c) not yet, keep dates only: cost, two releases in a day cannot be told apart, and a date is not what a check should name.
- **Old records' release:** (a) derive from `created`, never write (recommended); (b) backfill `release:` into 271 tickets and the old records: cost, a chore that edits 271 closed tickets (a `CLOSED_TICKET_EDITED` finding in `links/check.py`), and history changes; (c) one bucket "before the field": cost, no way to say which rule predates which ticket.
- **At once:** (a) the decision record marks it, the CTO sets it, the owner sees it on the page (recommended); (b) a fixed list in kernel text: cost, drifts; (c) the owner decides each time: cost, a stopper for each.
- **Reopening:** (a) by the reopening session's first commit, by hand (recommended); (b) build `gov reopen` now: cost, a new command for a rare event; (c) never reopen, a new KPI line is a new ticket: cost, a fix to a closed ticket's record would still need the move.

---

## 4. Decisions

**Problem.** `gov decisions in-force` lists **190** decisions, about 6,800 tokens of titles (27,115 characters over four, my estimate), and every CTO reads them at each start. Many are spent, many say a thing code already holds, and some are choices, not rules. Nothing says what deserves a decision record at all; and the owner's own words in DEC-1245 (4) already say a spec change is not one.

**Proposal.**

1. **A rubric for what is recorded as a decision.** *Recorded:* a standing rule or practice; a choice whose reason matters later; an exception to a rule; a measurement period; a rubric. *Not recorded:* a spec change (it is a change to the spec file, and git keeps its history); a one-off instruction; a status report. The test: if the reason would be needed in a month and no file says it, it is a decision.
2. **Every new decision names what it affects:** an `Affects:` line with paths, specs or workflow steps (W1 to W16), or `none`. The impact trace (W6) reads it, so a change to a decision shows the paths and steps it touches. Today the graph has `Under`, `Changes` and `Supersedes` links only (`store/loader.py:410-470`).
3. **A decision that code holds is marked so and leaves agents' reading.** The marker is the `Enforced-by:` line A-23 already adds for a new standing rule (plan 5-1; DEC-1238 (1b)): `Enforced-by: code <check id or path:line>`. The in-force digest (`decisions/command.py:79-86`) hides an entry whose marker resolves to an existing check, as it already hides `superseded` and `done` entries (`decisions/register.py` `leave_out`). The other classes (checked after, judgement, text) stay in the digest.
4. **Spent decisions** (status DONE, which the digest already hides) are marked by the CTO as one chore commit.

**How many are in force today: 190** (`gov decisions in-force`, register `docs/DECISION_REGISTER.md`). By HELD's classes (it reads DEC-1209 to DEC-1238, at `1085f9b95` on 22 November; some rows have moved since):

| Group | Decisions | Held by code on the path | Spent (history) | Partial (typed, or code outside the product) | Text only or not built |
|---|---|---|---|---|---|
| DEC-1209 to DEC-1238, classed by HELD | 30 | 1 (DEC-1213) | 6 (1209, 1215, 1226, 1230, 1231, 1237) | 3 (1210, 1216, 1221) | 20 |
| DEC-1239 to DEC-1245, newer than HELD | 7 | not classed | not classed | not classed | not classed |
| Before DEC-1209, never classed by HELD | 153 | not classed | not classed | not classed | not classed |
| **All in force** | **190** | | | | |

A decision's class is the weakest of its items (HELD's rule), and HELD classes items, so I grouped them by decision with a script over HELD's tables. Audit 4 §1.7 classed 11 of the 153 older ones as enforced for their producers: DEC-030, 032 to 037, 091, 815, 409, 772.

**How many would leave agents' reading:**

- **At least 7 now** (3.7 % of 190): 1 held by code on the path and 6 spent.
- **At most about 18** from what is classed today (9.5 %): the 7 and the 11 older ones audit 4 calls enforced; those 11 are enforced "for producers", so each needs a look before it leaves.
- **The 153 older ones decide the rest.** A pass over them, in HELD's key, is the real answer (card DE-2). Audit 4 notes the digest keeps DEC-1088, 1209, 1215, 933, 953 and 1182 without their changes, and I count about 15 architecture choices (DEC-001 to DEC-025) that are choices, not rules; the owner may let those leave too (card DE-1, option c).
- Most decisions will stay: 20 of the 30 classed are text only or not built. A decision held by an instruction cannot leave; agents must read it.

**What code holds and what stays practice.** Code: the `Enforced-by:` and `Affects:` lines required on a new decision by the basis check (`gov decisions basis`, extended with plan 5-1 and 5-4); the digest's hiding. Practice: deciding what is a decision, writing the lines, the one-time classing of the old ones.

**Where it lives in the kit.** The rubric: the `decision-record.md` template (`template/governance/kernel/templates/`) and a section of `docs/RUBRICS.md` (proposal 5). The two lines: the template and the basis check.

**Rides.** Plan 5-1 (the enforcement field, F-1) and 5-4 (the record's stated facts, F-2): `Affects:` and `Enforced-by:` are two more lines on the record those items already change. The digest change is a fix under W2-200 (`decisions/command.py:79`). Practice from today: the CTO writes both lines in every new decision.

**Options and costs.** Cards DE-0 to DE-2 on the page.

- **Approval:** (a) approve the rubric and `Affects:` (recommended); (b) with changes; (c) the rubric only, no `Affects:` line: cost, the impact trace stays blind to a decision's paths and steps.
- **The marker:** (a) reuse `Enforced-by:` (recommended); (b) a new `Held-by:` line: cost, two names for one thing and two checks; (c) (a) plus a `reference` class for the 15 architecture choices: cost, a fourth class to keep, about 8 % more relief.
- **The old 153:** (a) one pass by a read-only research session on Sonnet, the CTO applying the result in one commit (recommended): cost about $6.60 at the plan's M unit cost; (b) classing each when it is next touched: cost, the digest stays near 190 for months; (c) no pass: cost, only new decisions are marked.

---

## 5. The rubrics register

**Problem.** The owner has decided rubrics one at a time over a month: DEC-1120, DEC-1204, DEC-1208, DEC-1219, DEC-1225, DEC-1242 and more. They are scattered over many decisions and several files, and nothing says which a code check holds. GW §3 says every standing rule carries its enforcement; for the rubrics nobody has written it down.

**Proposal.** One file, **`docs/RUBRICS.md`** in Gov OS and its copy in the kit, **`governance/kernel/RUBRICS.md`** (the kernel folder, so `gov update` carries it). One row for each rubric: its rule in one line, the decisions that made it, and its **enforcement** field: `code` (held by code, with the check), `checked-after` (found after the fact, auto or typed), or `instruction` (only a sentence). The values are A-23's `class` values (audit 4 §4.2): `instruction` is A-23's `judgement`. A column `binds` says `every repository` or `Gov OS only`. The kit copy carries the rows that bind every repository. A new or changed rubric is a standing decision, so it comes to the owner (GW rule 8: P1).

**How A-23's field fills it.** When plan item 5-1 lands, the `enforcement:` block of `contract.yaml` and the `Enforced-by:` line of a decision (proposal 4) are the source. A G1 check (`kernel/checks/enforcement.yaml`, plan 5-1) compares each RUBRICS.md row's `by:` with them and refuses a `code` row whose check does not exist. Until then the CTO fills the column by hand from HELD and audit 4, at each release (as GW's "Today" column is filled).

### The register (20 rubrics)

Rubrics 1 to 12 are the owner's list; 13 to 20 are the others I found in the register and EMERGENCY-2.

| # | Rubric | The rule in one line | Decisions | Enforcement today | Binds |
|---|---|---|---|---|---|
| 1 | The golden rule and the threat model | Value first; honest mistakes, not an adversary; only a finding that fails open or loses work blocks; two review rounds then the owner once; READY by code | DEC-1204 (merges DEC-039, DEC-801, DEC-1010 (1)), DEC-1207 | `instruction`; READY computed from the verdict block's fields, `checked-after` (`close/command.py:1860-1864`); the rounds contradict `ESCALATION_AT = 3` (`close/state.py:17`; plan 1-2) | every repository |
| 2 | The work rubric | A ticket is a feature with spec and KPIs; a bug is a fix under its owning ticket, failing test first; a chore changes no behaviour and keeps tests unchanged and green; a new KPI line on a closed feature is a new ticket | DEC-1208 (provisional), DEC-1219 (5), (6), DEC-1242 R-1, R-2, R-3, R-8 | `code` off the path for the fix record and `NEW_TICKET_NOT_FEATURE` notice (`queue/checks.py`, `queue/fix.py`); `kind` field not built (plan 2-11); the rest `instruction` | every repository |
| 3 | Models and effort | Opus only for each product's CTO and a senior engineer per stream; every other agent Sonnet, critical work included; effort by role in one table; a change comes to the owner first | DEC-1120 (changed), DEC-1212 (2), DEC-1225, DEC-1236 (2), (3), DEC-1242 R-4, R-5, T-10 | `code`: the helper hook (`agent_model.py`) and `gov launch`; the start scripts and the one-file table are `instruction` until plan 2-7, 2-9 | every repository |
| 4 | Criticality C0 to C3 | It keeps review depth and the profile; it no longer varies the model | DEC-1120 (1), DEC-1242 R-5 | `code` (`launch/criticality.py`, `criticality.yaml`); promotion and probe retire (plan 2-10) | every repository |
| 5 | Escalation P1, P2, P3 and emergency | Every decision at its level; the level computed from the record's stated facts; the owner's decisions on one page, a stopper at once | DEC-1219 (2) (`T2-ESCALATION-RUBRIC.md`), DEC-1236 (1), DEC-1242 R-6, T-1 | `instruction`; one fact `checked-after` and defeated by a skip (`check/authority.py:44`); first slice is plan 5-4 | every repository |
| 6 | Usage | One plan for the machine; pushes at 95 and 99 %; a stall push after 3 hours; context and wake cost measured daily; no cap on the CTO's window | DEC-1218 (1), DEC-1216 (5), DEC-1229, DEC-838, DEC-1243 (4), DEC-1244 X-2 | `checked-after` by scratch scripts outside the product (`cto_watch.sh`, `usage_log.sh`, `stall_check.sh`); code at plan 3-10, 3-13 | the plan: every repository; the scripts: Gov OS only |
| 7 | Tests | Acceptance tests by an independent designer, red on the base; every landing runs the impact-selected tests; the full suite only for a release and weekly; no hand-picked set | DEC-069, DEC-906, DEC-968 (changed), DEC-1241 P-2, DEC-1242 T-3, T-8, DEC-1243 (3) (replaced), DEC-1244 X-1 | `code` off the path for authorship (`queue/checks.py:52-73`) and selection; red on the base not built (plan 1-3); the rest `instruction` | every repository |
| 8 | Fix loops | The same failure three times stops the loop; the CTO finds the root cause and fixes it at the root | DEC-1244 Q-7 (c) | `instruction`; code at plan 5-13 | every repository |
| 9 | Releases | The CTO cuts patch releases for content the owner approved, by code, with `release-authority.yaml` as the off-switch and a rehearsal first; bigger releases and every push stay the owner's | DEC-1223 (RB-1 to RB-7), DEC-1226, DEC-1235 (2) | `code` in `gov release --patch` (gates G0 to G4), switched off (`patch_releases: off`); the full release is the owner's | Gov OS only |
| 10 | The memory standard | Fresh 80 questions (40 and 40 hidden) for every measure, end to end, 95 %, graded by Sonnet with the strict citation rule; memory first and search once more, in every repository, refreshed after each merge | DEC-1098 (1), DEC-1101, DEC-1207 (3), DEC-1210, DEC-1225 (4), DEC-1227 D5, DEC-1092, DEC-1245 (2) | `code` in `gov memaudit` (preflight, hidden-set scan), run by hand, `checked-after` (typed); "memory first" `instruction`; the refresh schedule is not yet in the product (proposal 1, TL12, TL15) | every repository |
| 11 | Imports | Each import is use, absorb or study; its licence a note, never a gate; study searchable under a ceiling; MCP tools are imports | DEC-1222 (1), DEC-1223 (8), DEC-1228 | not built (a spec: `IMPORTS-ADOPTION-SPEC.md`); `instruction` until the fourth stream (X-3) | every repository |
| 12 | Data in specs | Every spec and KPI line declares its data need and its path; the ready check goes red when the data is missing | DEC-1245 (4) (this proposal 6) | `checked-after` (typed): the spec form's `## Test data` table (`check_spec.py:146-170`); the ready check is new | every repository |
| 13 | Review convergence and what may block | A moderator triages each finding against the change's scope; two rounds | DEC-1204 (2), (3) | merged into rubric 1; the code allows a third round | every repository |
| 14 | The three measures and the floor | Every release prints steps, tools and Contract items; at the exit the owner sets a baseline X % | DEC-1241 P-6, DEC-1244 Q-14 | not built (plan 5-6); `instruction` | Gov OS only |
| 15 | Decision packages and the page | At most five open packages (P1 may bypass); one page, a GOV-ANSWERS sheet | DEC-093, DEC-818, DEC-1236 (1) | `instruction`; the page by hand | every repository |
| 16 | The machine and the resource gate | Working size 0.75 GiB per session; a gate refusal is a wait; disk and inodes checked | DEC-898, DEC-1146, DEC-1149 | `code` (`gov resources`, `launch/command.py:7`) | every repository |
| 17 | Proportionality profiles and readiness | Required cells by profile; no defaulted N/A; spines close at FULL | DEC-005, DEC-085 | `checked-after` (typed): `gov readiness` | every repository |
| 18 | Secrets scanning | No scan on a private repository; one full scan before it goes public or is shared | DEC-1170, DEC-1182, EMERGENCY-2 §2.11 | a setting (`secrets.yaml` `scan: off`) against the kit CI that scans on push (TOOL-MAP row 91); `instruction` | every repository |
| 19 | Pings and quiet hours | A ping that does not stop the CTO; none at night; only the 99 % push wakes the owner | DEC-972, DEC-973, DEC-1216 (2) | `instruction` | Gov OS only |
| 20 | Test independence and acceptance exemptions | Only an independent test designer commits under `tests/acceptance/`; exemptions by exact commit | DEC-906, DEC-912, DEC-1243 (1) | `code` at the landing (`queue/checks.py:52-73`), bypassed by a hand merge (I-12, I-15); `path-map.yaml` `acceptance_exemptions` | every repository |

I read each "enforcement today" from HELD, TOOL-MAP and audit 4, not from the code again; the dates of those reads are in each file's header.

**What code holds and what stays practice.** Code: nothing yet; once 5-1 lands, the G1 check on the `by:` of each row. Practice: writing and re-reading the rows; the owner's yes for each change.

**Where it lives in the kit.** `governance/kernel/RUBRICS.md` (kernel text: the CTO decides, the owner approves, EMERGENCY-2 §3.5). The head of CLAUDE.md and AGENTS.md points to it beside the golden workflow pointer (the rules file `template/.rulesync/rules/governance.md`).

**Rides.** The file is a chore now (the CTO writes it, the owner approves its text); the kit copy goes with the first patch release after 0.1.5 as text, not a schema. The enforcement column fills from plan 5-1 and the file is checked by 5-1's G1 check; plan 5-3 (the workflow as the spine) cites it from the Charter and the Contract.

**Options and costs.** Cards RG-0 to RG-2 on the page.

- **Approval:** (a) approve the register and its 20 rubrics (recommended); (b) with changes; (c) not yet.
- **Form:** (a) a hand-written file now, the column filled from A-23 later (recommended); (b) generated from a `Rubric:` tag on each decision: cost, it needs 5-1 first and tags 20 decisions; (c) leave the rubrics in the register and CLAUDE.md: cost, the scatter this proposal exists to end.
- **The kit's copy:** (a) only rows that bind every repository (recommended); (b) every row: cost, Gov OS-only rules read as binding a product; (c) none: cost, a product's CTO cannot read the rubrics it is held to.

---

## 6. Data in specs

**Problem.** A spec says what a feature does, and its tests need data, but a test designer can find the data missing, synthetic where the spec meant real, or imported without a licence. The spec form already asks for a `## Test data` table (the sixth of nine headings, `spec-form.md:63-81`), and `check_spec.py:146-170` refuses a table with a missing owner, privacy, secrets or licence cell, and exits 2 with a P1 for a row with `secured: no`. But it is typed, wired into no gate (A-23b), allows only `imported` and `synthetic`, names no path, and does not say which KPI line a row serves. Nothing makes a ticket wait for data that is not there.

**Proposal.** Extend the table that exists; add no new place.

1. **`kind` takes four values:** `none` (the spec needs no data: one row says so), `synthetic`, `imported`, `real`.
2. **New columns:** `path` (where the data is, or for synthetic data where its recipe and seed are); `serves` (the KPI ids, such as `K1, K3`, or `all`); `import class` (for an imported row: `use`, `absorb` or `study`, the imports rule, DEC-1222 (1)).
3. **An imported row's licence** is the licence file's SPDX id, or `unrecognised`; a copyleft or unrecognised licence is named in the row. Today's refusal of an unlicensed imported row stays for test data (card DS-3).
4. **A `real` row names an accepted decision id** of the owner in its `owner` cell and its data stays outside the tracked tree (EXAMIN DEC-003: "revisit before real data", a P1).
5. **The ready check is red when the data is not at its path** (`DATA_MISSING`, naming the row), and green when the kind is `none` or the path holds the data (for `synthetic`, the recipe and seed; for `imported`, the data and its licence record; for `real`, the file on disk). It runs in `gov brief`'s ready check (`brief/build.py:157-186`), reading the table of the spec the ticket names (`specification:`, Q-2), and in `gov plan` (plan 2-3: plan, brief, launch and landing read the same fields). No new ticket field is needed.
6. **The test designer builds on that data,** and its brief lists the rows that serve each KPI line it must test (the brief is generated from the spec, G-3).
7. **Old specs** (proposal 3): a spec created before the release that carries the check has no `serves` or `path`; `gov doctor` shows it as a notice, never red. The check applies to specs created from that release on.

**What code holds and what stays practice.** Code: `check_spec.py` (the new columns and kinds), the ready check's `DATA_MISSING`, the plan check, doctor's notice. Practice: writing the table; securing the data; the owner's decision for `real` rows.

**Where it lives in the kit.** The field is in the spec form (`template/governance/kernel/skills/spec-writing/spec-form.md` and `check_spec.py`, kernel text: the CTO's change with the owner's yes). No ticket schema change. Which check reads it: `gov brief`'s ready check and `gov plan` (plan 2-3); the typed `check_spec.py` stays, wired into the brief's ready check by A-23b (plan 5-11).

**Rides.** Practice from today: every new spec fills the extended table by hand. Code: plan 2-3 (the ready check reads the same fields) and 5-11 (A-23b wires `check_spec.py` into the ready check); the spec-form change is kernel text, with the next full release for `check_spec.py`'s new columns.

**Options and costs.** Cards DS-0 to DS-4 on the page.

- **Approval:** (a) approve (recommended); (b) with changes; (c) not yet.
- **Granularity:** (a) one table, a `serves` column naming the KPI ids (recommended); (b) a data line under each K-line: cost, it changes the KPI line's form that `check_spec.py` and Q-5 fix; (c) one declaration for the whole spec: cost, a KPI that needs none cannot show it.
- **Real data:** (a) a `real` row must name an accepted owner decision (recommended); (b) a path only: cost, no stopper before real data; (c) no real data in specs: cost, EXAMIN's real data could not be specified.
- **An unlicensed imported source:** (a) red for test data, a note for adoption's imports (recommended); (b) a note everywhere: cost, unlicensed data enters a repository as test data; (c) red everywhere: cost, adoption stops on vendored folders, against DEC-1222.
- **Old specs:** (a) a notice, red only for specs created from the release on (recommended); (b) red for all, with a backfill of every spec: cost, a chore over every closed spec; (c) assume `synthetic`: cost, the check says nothing.

---

## What I could not place, and choices I made

- **Two sources disagree on a licence for data** (card DS-3): `spec-form.md:79-81` refuses an unlicensed imported test-data row; `IMPORTS-ADOPTION-SPEC.md` line 66 says licence is "a note, never a gate". The later owner decision is DEC-1222 (19 November), which is about adopting what a repository already holds; the refusal is about data a spec asks to bring in. I read them as two cases, and put both on the card.
- **0.1.5 is not cut** (`docs/emergency-2/release-0.1.5/STEPS.md`; the tag list ends at `v0.1.4`). Statuses that say "fixed for 0.1.5" rest on merged code and tests, not a cut release.
- **I did not run any tool** to confirm a status; the list rests on TOOL-MAP, RECORDS-MAP, FINDINGS, audit 4, the W2-81 analysis and the `gov retrieve` header. Rows TL12 and TL44's cron lines are untried on a product.
- **Class of a decision** (proposal 4) is my grouping of HELD's items by decision (weakest live item); HELD itself classes items and reads 22 November.
- **The `release:` field's source** is `governance/framework.lock` (named in the kit's path map); I did not read how the lock names the release.
- **Whether `gov release` hashes extra files** in `docs/releases/<v>/` (proposal 1, where it lives) is not checked.
- **Ownership of new tickets:** `gov findings`, the `tool_status` doctor part and the data check are features or fixes for the owner's yes and for W2-22, W2-152 and W2-129 respectively; I did not find a wbs id for the findings command ("none: new").
- Unplaced: the owner's list has nothing on **`gov spend`** or **`gov telemetry`**; I listed them amber.
