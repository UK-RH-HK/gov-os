# Audit 4: determinism across the whole of Gov OS (the owner, 2026-11-22; DEC-1225 (2))

Date 2026-11-22 · Gov OS `w2/integrate` at `266d6507c`; EXAMIN `/home/usain/gov-os-runs/W2-27/examin` at `44fd59d` (read only) · auditor: fresh, read-only, Opus, with eight Sonnet helpers for the wide reading, one per area: commands (two halves), roles and templates, skills, hooks and schedules, standing rules, the flow, and the Contract table. Every row below comes from a helper's evidence or my own reading. I re-checked by hand the claims that the lists rest on: `start_lead.sh:1-11`, `start_cto.sh:1-21`, `close/state.py:17`, `retrieval/retrieve.py:48`, `check/authority.py:44`, `.git/hooks/reference-transaction:1-20`, the integration-store log, `adapters/merge.py:1-24` and `.rulesync/permissions.jsonc`.

**Builds on, does not repeat:** audit 2 (`E2-AUDIT-2-CONTRACT-IN-CODE.md`, cited "A2 <row>"), audit 1 (`E2-AUDIT-1-DECISIONS.md`, "A1"), audit 3 (`E2-AUDIT-3-MCP-TOOLS.md`, "A3") and the merged gap table (`.gov-runtime/scratch/orchestrator/log/audits-merged-2026-11-22.md`, ids M-nn, N-nn and W-n). A2's base was `3ab01e94b`. Seventeen commits have landed since then, and only these change a class: W2-209's release work (`2b47d3354`), the D6 doctor fix (`9a4adb350`) and the registry lines for REA and Node (`e03dd938b`).

**In flight** (counted as "in flight", with the branch named): `e2/l2-4-queue` (queue fixes, the proving evidence; Gov OS's landing is **not** moved yet); `e2/models-rubric`, `e2/d1-verdict` and `e2/w2-207-runtime` (each only a ticket commit on the branch; their code sits uncommitted in the worktrees); `e2/d5-memaudit-strict` (code and tests); the briefs `LEAD-fixes-015.md` (committed), and the untracked briefs `LEAD-fixes-015a.md` (F1, F3, F10, F11, F12), `LEAD-fixes-015b.md` (F2, F4 to F9) and `LEAD-contract-015.md`, which split it and add to it.

**Decisions.** DEC-1230 and DEC-1231 were read in the register. **DEC-1232 and DEC-1233 are not in the register.** It ends at DEC-1231, `DECISION_REGISTER.md:2061`. They are cited only by the four untracked briefs above. What I know of them comes from those briefs: DEC-1232 (6) no claude.ai connectors; DEC-1233 (1) the Contract text; (2) the 0.1.5 fixes; (6) "the determinism fields on every item … follow audit 4". DEC-463 asks that a decision be recorded before a commit cites it.

**Memory.** I ran `gov retrieve` twice and read each bundle whole: the Charter's principle 4, ADR-0001, audit 01's READY/DONE rows, the twelve-field return and the ROLES-SPEC hand-off chain. Each helper ran its own. The integration store is **23 commits behind HEAD**: the automatic refresh at 13:53 today failed (`EMBEDDER_UNAVAILABLE`) and nothing retried it (`integration-store.log`). That is itself a finding (A-10).

No test suite was run. I wrote nothing but this file, plus scratch notes under `/tmp/audit4/`.

## 0. The answer in eight lines

1. **The live Contract items (188), by their weakest part:** 21 % enforced by code on the path sessions take; 13 % enforced only off the path; 31 % checked after (4 % by themselves, 27 % only when typed); 19 % judgement; 16 % not built (§4.1).
   - What code really holds today: the two deny lines; the helper-model hook; the helpers' twelve-field return; the checkpoint and wake hooks; `gov update`; `gov adopt`'s stage chain; the owner-only `gov release`; the hourly backup; memory's own answers (precedence, stale marking, fail-closed embedder).
2. **Refusals that are built but off the path:** most of the flow's refusals sit in `gov queue` and `gov launch`, and Gov OS bypasses both. It lands by hand merge, and starts leads with `start_lead.sh` (no template, no ready check, no pause, no claim, no checkpoint, since `GOV_TICKET` is unset).
3. **Checks that exist but must be typed:** doctor, check, telemetry, basis, the fresh 80, the transcript scan, `gov accept`. Nothing schedules them. Lefthook is not installed, CI is manual, and the nightly is commented out against EMERGENCY-2 A-1. The one automatic memory refresh failed today with no retry.
4. **The rest is judgement:** every role, every skill step, every template body, and most standing rules. Some of it must stay judgement. Much of it has an output form that code could check and does not.
5. **Three ordinary mistakes are caught by nothing today**, and each fails open or loses work:
   - uncommitted work left in a lead's worktree at the land;
   - a mis-trailered or all-green acceptance folder landed by hand merge (the trailer case already happened once, `CTO-HANDOVER.md` §5);
   - the memory measure's figure carries no release, model or rule stamp, so a stale grading looks like the new baseline.
6. **List A** (§2) holds 39 conversions:
   - 8 protect against lost work or a fail-open;
   - 15 protect against wrong results;
   - 11 protect against drift;
   - 5 protect against cost.
   - 12 are in flight or for 0.1.5; 24 are for 0.1.6, most of them S or XS; 3 are later.
7. **List B** (§3) specifies the 16 agent jobs. Today 9 of the 16 hand-offs have no form, or a form nothing checks. Each entry names the form and the check that would make the hand-off safe without goodwill.
8. **The rule becomes assessable by code** (A-23): every Contract item and every new standing decision carries an `enforcement:` field (class, the check that holds it or the List B job), and a G1 check refuses an item without one. §4 gives the 320 Contract rows, already filled, and the Charter sentence.

## How to read the classes

| Class | Meaning |
|---|---|
| **enforced** | Code refuses *before* the act, on a path today's sessions take (path:line given). |
| **enforced (off path)** | Code refuses before the act, but inside a tool today's Gov OS sessions do not go through (`gov queue`, `gov launch`, `gov brief`, `gov discover`, `gov ci`). Once the path goes through the tool, it is enforced. |
| **checked after (auto)** | Code finds it after the fact, by itself: a hook, cron, git hook or the queue's after-step. |
| **checked after (typed)** | Code finds it after the fact, only when someone types the command. |
| **judgement** | An agent decides. The cell says where the instruction lives. |

"(state)" marks a rule that is only a configuration state with no refusing code (for example "no guard").

---

## 1. The inventory

### 1.1 Every `gov` command (36 command modules; `cli/main.py:93-113`; all listed by `gov --help`)

Who runs a command by itself today: cron runs `gov backup`, and the reference-transaction hook runs `gov rebuild --integration`. The hooks import `checkpoint`, `update.pending` and `msg.stopcheck` as libraries. Everything else is typed, or runs inside the off-path queue or launcher.

| command | for | class | in flight | evidence |
|---|---|---|---|---|
| status | one-read project state | checked after (typed); never refuses | — | `status/command.py:1-14,140-153` |
| check | declared checks G1-G2 | checked after (typed); `--structural` runs automatically only in the queue's after-step (off path) | — | `check/command.py:86`; `queue/after.py:53`; `ci.yml:28-30` manual |
| readiness | READY of spec or ticket | checked after (typed) | — | `readiness/command.py:15` |
| doctor | install and project health | checked after (typed); a patch-only CLI gap is now drift, exit 0 | 015a F1(c); 015b F2, F6 | `doctor/command.py:950,102-113`; `9a4adb350` |
| rebuild | recreate derived stores | checked after (auto: reference-transaction after each `w2/integrate` update). It fails closed and **nothing retries** | — | `.git/hooks/reference-transaction:15`; `integration-store.log` 13:53:49 `REBUILD_FAILED`, store 23 commits behind |
| closure | lineage of ids | judgement aid (a reader) | — | `closure/__init__.py:47` |
| retrieve | memory search | enforced for its answer (stale never current, unresolved ids refused); *using* it is judgement; a 6,000-token budget the Contract forbids | — | `retrieve/command.py:128,202`; `retrieval/retrieve.py:48` |
| checkpoint | write, watch, resume | checked after (auto: the hooks call the library); `--watch` typed | — | `precompact.py:175`; `stop.py:72`; `checkpoint/command.py:20` |
| close | strict close (retired by L2-1) | enforced (off path), typed only. It still carries the strict default, `ESCALATION_AT = 3`, repair tickets and a containment refusal | N-04 | `close/state.py:17`; `close/command.py:511-575,1510` |
| adopt | adoption A0-A10, AS | enforced (the only way to adopt) | e2/d1-verdict | `adopt/stages.py:61-80,541-565`; `spec_audit.py:271-323` |
| pause | freeze, cancel, rollback | enforced in `gov launch`, `gov queue` and `gov release --patch` (new since A2); **not read** by `start_lead.sh`, the scratch tick or `gov dispatch` | 015a F10 | `pause/command.py:304-307`; `launcher.py:351-362`; `queue/command.py:162-177`; `release/gates.py:160-182` |
| accept | acceptance per KPI line | checked after (typed); enforced (off path) at the land | 015b F5 | `accept/runner.py:6,732`; `queue/checks.py:166-181` |
| adapters | generate agent and settings files | checked after (typed); the merge keeps the project's own entries first, so the deny lines survive | 015a F11 | `adapters/merge.py:6-13`; `portability.py:277` |
| backup | verified git bundle | checked after (auto: cron hourly); nothing checks the bundle's age | — | `backup/command.py:1-8`; crontab `7 * * * *` |
| brief | filled brief, refused unready | enforced (off path); 1 run in the memory-use log | — | `brief/build.py:157-186,192` |
| ci | hook and CI gates | enforced (off path); nothing calls it | — | `ci/command.py:18-37`; no `pre-commit` in `.git/hooks` |
| decisions | basis check, in-force digest | checked after (typed) | — | `decisions/command.py:1-15` |
| discover | idea to spec, gap tickets | enforced (off path) | — | `discover/command.py:1-15` |
| dispatch | the product dispatcher | enforced (off path); cron runs the scratch `run_tick.sh` instead | e2/w2-207-runtime | `dispatch/command.py:30-36` |
| impact | CIT-P over the graphs | judgement aid | — | `impact/command.py` |
| install | hash-verified pinned install | enforced | — | `install/pin.py:1-20` |
| launch | start a session | enforced (off path): no launch record in Gov OS or EXAMIN since 16 Nov | 015a F1, F10; models-rubric | `launcher.py:194,269,361,394,741-788,1167` |
| links | link-integrity notice | checked after (typed; automatic only inside the off-path queue) | — | `links/command.py:1-15`; `check/structural.py:220-229` |
| memaudit deliver, preflight, void, declare | the measure's code steps | enforced inside `fresh` (started by hand) | e2/d5 | `deliver.py:43-82`; `preflight.py:75`; `drops.py:50-134`; `declare.py:172-198` |
| memaudit judge | reader and graders | judgement (models) inside code; code counts the verdict; reader and grader on Opus | models-rubric R4; e2/d5 | `memaudit/judge.py:33`; `prompts.py:14-33`; `figures.py` |
| memaudit scan | hidden-set transcript scan | checked after (typed; the last step of `fresh`) | — | `scan.py:204`; `fresh.py:291-330` |
| memory-use | count the memory log | checked after (typed) | — | `memory_use/__init__.py:72` |
| msg | inbox messages | enforced for the Stop wake (auto); `audit` typed | — | `kernel/hooks/stop.py:60-70`; `msg/stopcheck.py:55-72` |
| plan | dependency map, batches | checked after (typed) | — | `plan/command.py:20` |
| queue | the landing | enforced (off path): Gov OS merges by hand (§1.2 step 5) | e2/l2-4-queue; 015b F8 | `queue/checks.py:52-181`; `queue/command.py:160-431` |
| release (full) | the owner builds a release | enforced (owner only, clean tree, version new); **no acceptance gate** | contract-015 (wording) | `release/command.py:55-112`; `release/__init__.py:171-200` |
| release --patch | the CTO cuts a patch | enforced (G0-G4), switched off (`patch_releases: off`) | 015a F10; 015b F7 | `release/gates.py:56-185`; `release-authority.yaml` |
| resources | machine resource gate | enforced (off path): only the committed `heavy_slot.sh` calls it; the scratch copy the hook uses does not | e2/w2-207 | `resources/command.py:26-31` |
| session-watch | orchestrator Stop checks | checked after (typed); in no settings file | — | `session_watch/` |
| skilleval | skill scenarios | judgement (a model judges a model), typed; default model Opus, outside the rubric | — | `skilleval/command.py:25-30`; `harness.py:33` |
| spend | runaway brake | enforced (off path) in `gov launch` only; `check` never scheduled; it has never fired | — | `spend/brake.py:82-95`; `launcher.py:1167` |
| telemetry | governance token share | checked after (typed) | — | `telemetry/command.py:13,32` |
| update | move to a release | enforced (refuses dirty, manifest, files; rolls back; never offers a burned release) | 015b F4, F6 | `update/core.py:256-280,480`; `update/pending.py:81-117` |
| wait | bounded wait on an exit file | enforced (usage only) | — | `wait/command.py:1-8` |

Library code with no caller (A2 rows stand): `tasks/claims.claim()` (CAP-23.a); `retrieval/validate.py` (CAP-55.a); `retrieval/learning.record()` (CAP-19.c); `retrieval/synthesis.py:67` (CAP-57.a).

### 1.2 Each step of the flow (EMERGENCY-2 §4.3, plus release, update, adopt, the memory measure, fix, chore and session start)

"Gov OS today" is what actually runs. Cells cite the merged table where a fix is placed.

| step | what must be true | class | in flight | evidence |
|---|---|---|---|---|
| 1 Spec and KPIs | ticket READY: KPI lines each with a verify, allowed paths, dependencies closed | enforced (off path) | N-06 | `brief/build.py:157-186`; Gov OS leads start from hand briefs; EXAMIN ran `gov brief` 3 times (REQUESTS 2026-11-20) |
| 1 | spec's K-lines are the ticket's KPI lines | judgement (`check_spec.py` typed, linked to nothing) | — | `spec-writing/SKILL.md:47-50` |
| 1 | a new KPI line on a closed feature is a new ticket | judgement | — | EMERGENCY-2 §4.6; nothing refuses a hand edit of `kpis` |
| 1 | the ticket is claimed by one holder | judgement | N-06 | `tasks/claims.py:42` has no caller (A2 CAP-23.a) |
| 2 Test design | acceptance commits carry `Role: independent-test-designer` | enforced (off path); judgement in Gov OS (a hand `git log` read, missed once) | e2/l2-4-queue | `queue/checks.py:52-73`; `CTO-HANDOVER.md` §2, §5 |
| 2 | red on the base | judgement (self-reported, e.g. `8a95d3873` "5 pass on the base") | N-03 | no base run in `src/gov/queue/` |
| 2 | README maps every KPI line | enforced (off path) at the land; checked after (typed) otherwise. 72 of 189 folders fail the parse (24 have no README, 11 map nothing, 37 are unreadable) | 015b F5 | `accept/runner.py:139,726-733` |
| 2 | the designer does not read implementation | judgement | — | `LEAD-COMMON.md:25`; `test-design` skill |
| 3 Build | helper model is Sonnet | enforced | models-rubric R3 | `.claude/hooks/agent_model.py:159-198` |
| 3 | stay inside `allowed_paths` | checked after (a notice, off path) | W-1 | `queue/checks.py:80-93` |
| 3 | helper return has 12 fields | enforced (fault: next-line values, no `stop_hook_active`, exit 2 on an exception) | 015a F12 | `kernel/hooks/subagentstop.py:34,59,66-67` |
| 3 | memory first | judgement; checked after (typed log; helpers log no role) | N-13 | `gov memory-use`; A2 §5.3 |
| 4 Accept | `gov accept` green per KPI line | checked after (typed); enforced (off path) at the land | e2/l2-4-queue | `accept/runner.py:1-9`; `queue/acceptance.py` |
| 5 Landing | merge by code | enforced (off path); Gov OS hand-merges | e2/l2-4-queue | `queue/command.py:586`; `9a4adb350`, `2b47d3354` are hand merges |
| 5 | impact-selected tests on the merged result | enforced (off path); after a landing, an automatic scoped run only for commits outside a ticket touching settings, registry or test map | e2/l2-4-queue | `queue/command.py:323-372`; `landing_select.sh` |
| 5 | test authorship | enforced (off path) | e2/l2-4-queue | `queue/checks.py:52-73` |
| 5 | no uncommitted work left behind | **nothing** | 015b F8 | `queue/command.py:193-237` reads the branch tip; `_checked_out` `:415-447` checks only the integration worktree |
| 5 | trailers | checked after (typed `gov close`); none in the queue | N-02 | `close/command.py:504-523` |
| 5 | store fresh | checked after (auto refresh), but it fails silently; no refusal | N-02 | reference-transaction `:15`; log 13:53:49 |
| 5 | disk floor | judgement | N-02 | none in the queue |
| 5 | pause stops landing | enforced (off path) | — | `queue/command.py:162-178` |
| 5 | kernel text only by the CTO | judgement (`kernel_gate.py` still exists, called only by scratch tools) | contract-015 | A2 CAP-24.c corrected: `kernel_gate.py` 161 lines, `hand_merge_check.sh:20` |
| 6 Close | closes at the land; close record by code | enforced (off path); Gov OS writes records by hand | e2/l2-4-queue | `queue/command.py:381-414`; `94556a8f7` |
| 7 Release | full release by the owner only | enforced | — | `release/command.py:63-117` |
| 7 | certified by the acceptance record | judgement | N-15 | `release/__init__.py:171-226` reads none |
| 7 | patch rule P1-P5 and gates G0-G4 | enforced, switched off | 015b F7 | `release/patch.py:152-170`; `gates.py` |
| 7 | tag never rewritten | judgement | N-16 | `git tag -f` unchecked |
| 8 Update | verified, rolled back, burned release never offered | enforced | — | `update/core.py:472-606`; `pending.py:81-117` |
| 8 | pending update shown at session start | checked after (auto), not at a fresh start | W-5 | matcher `compact\|clear\|resume`, `.claude/settings.json:29` |
| 8 | doctor still green after update; hook once | checked after (typed) | 015b F4, F6 | real G3 run: 6 of 6 red (`g3-real-20261122.json`); EXAMIN `context_watch` twice |
| 9 Adopt | A0-A10 in order, a commit per stage | enforced | — | `adopt/command.py:24`; EXAMIN `9a74a57`..`28b7b4d` |
| 9 | A5, A7, A10 by a fresh auditor | enforced (the session id is a typed string) | A-20 | `adopt/stages.py:541-589`; `lite_gates.py:80-90` |
| 9 | AS before A3 | enforced | — | `spec_audit.py:271-323` |
| 9 | lite verdict (CAP-44.h) | judgement (no code) | e2/d1-verdict | `adopt/command.py:24` has no VERDICT stage |
| 10 Memory measure | delivery form, pre-flight, drops, declare, single use | enforced inside `fresh` | — | `deliver.py`, `preflight.py`, `drops.py`, `declare.py:172-190` |
| 10 | reader has only the memory tool | enforced | — | `memaudit/claude.py:3,31` |
| 10 | reader and grader models | enforced, **wrong value** (Opus) | models-rubric R4 | `judge.py:31-33` |
| 10 | citing a forbidden source is wrong | judgement (lenient) | e2/d5 | `matcher.py`; it bites only where a question carries a `forbidden` list |
| 10 | figures name release, models, rule | **nothing** | A-9 | `figures.py` has no model or release key |
| 10 | hidden set unread | checked after (typed, the last step of `fresh`) | — | `scan.py`, `fresh.py:291-330` |
| 10 | run weekly | checked after (typed); no cron line | N-19 | `memaudit_cron.sh` not in the crontab |
| 11 Fix | lands under its closed ticket with `Fix:` | enforced (off path) | e2/l2-4-queue | `queue/checks.py:140-153`; `queue/fix.py` |
| 11 | failing test first | judgement | A-15 | A2 CAP-31.b |
| 11 | `## Fix:` section in the owning ticket | judgement (no form; `ticket.md:65` says the opposite) | A-15 | `.tickets/DAEO-xm6l.md:84-96` |
| 12 Chore | direct commit, tests unchanged and green, in the digest | judgement | A-16 | no `queue --direct`; `Class: C` is typed text |
| 13 Session start | CTO: handover present, one tmux name | enforced (script) | models-rubric | `start_cto.sh:11-12` |
| 13 | CTO gets its role card | **nothing**: `role-cto.md` reaches no session | A-24 | `start_cto.sh:13-20`; `launcher.py:107` omits it |
| 13 | lead: template, rubric, pause, claim, record, checkpoint | judgement | N-06 | `start_lead.sh:5-7`: no template, no `GOV_TICKET` (so no checkpoint is written), no pause read |
| 13 | worker: filled role file | judgement; the role files carry literal slots (engineer 10, orchestrator 46) | 015a F11 | A2 MR-5 |
| 13 | no claude.ai connectors | enforced for leads (`--strict-mcp-config`); **not** for the CTO and its helpers; the settings key the 015a brief says is present is absent | 015a F1 | `start_lead.sh:6`; `start_cto.sh:19-20`; `.claude/settings.json` |

### 1.3 Roles (`template/governance/kernel/roles/`, 9; generated to `.claude/agents/`; EXAMIN byte-identical)

For every role, code reads only the launch lines (`Version`, `Launch default`, `Launch by criticality`, `Skills`) in `gov launch` (`launch/role.py:38-45`, off path), and portability compares the copies (typed, `portability.py:269-309`). Purpose, paths, tools, hand-off and work order are judgement.

| role | for | class | in flight | evidence (stale text EMERGENCY-2 retired; slots in the generated copy) |
|---|---|---|---|---|
| engineer | implements one ticket | judgement; launch lines enforced (off path) | models-rubric; 015a F11 | guard `:3,16`, sandbox `:22-23`, permission classes `:28-34`; C3 on Opus `:10`; 10 slots |
| independent-test-designer | acceptance tests first | judgement; authorship enforced (off path) at the land | same | guard `:3,16`, sandbox `:23-24`; 9 slots |
| independent-auditor | read-only audit | judgement; the Opus exception has no limit | same | the generated copy opens with the QA probe template (`agents/independent-auditor.md:17-55`); `:15` per-ticket review; 8 slots |
| orchestrator (CTO) | runs the flow | judgement; `start_cto.sh` sets its model itself | same | the generated copy opens "You are the ticket lead for {ID}" (`agents/orchestrator.md:17`); `:11` "runs every close"; 46 slots |
| product-spec | specs, schemas, templates | judgement | same | guard `:16`, sandbox `:20-21`; `spec-writing` on no role's skill line; 9 slots |
| qa-engineer | checks a stream's tickets | judgement; `gov launch` would refuse it (no template) | — | `:12-13` QA per ticket before merge (§3.6 says none) |
| research | one experiment | judgement | 015a F11 | guard `:14`, research allowlist `:18-19`; 6 slots |
| senior-engineer | one stream under the CTO | judgement; no code names it, no start path | — | `:14` guard; hand-off folder does not exist |
| ticket-lead | one ticket's loop | judgement; `start_lead.sh` loads neither this file nor `role-lead.md` | — | `:12` FULL probe, `:24` three iterations, `:11,25` guard |

### 1.4 Skills (`template/governance/kernel/skills/`, 19 plus 3 vendored; `.claude/skills/` copies are body-identical; EXAMIN identical except `.claude/skills/judging-work` at 1.1.0)

Every skill's steps are judgement. The code that touches skills: `skill_validator.py` (frontmatter, ≤60-token description, typed, and only for the 9 skills named in a `skill-regression-*` declaration); `skilleval` (typed); the bump check (reads only `kernel/vendor`, `check/runner.py:57,305`). "Mem" is the memory-first line: full / short / none.

| skill | for | class (what code checks of its output) | mem | stale | evidence |
|---|---|---|---|---|---|
| adopt | adoption A0-A11 | `gov adopt` refuses a missing AS or verdict (enforced); the A9 practice record unchecked | none | `:9` guard; `:71` operator | `adopt/SKILL.md:11-71` |
| api, backend, data, devops, frontend, security, ui-ux | domain methods | judgement; `gov accept` (typed); `check_domain_skill.py` checks the skill file only, called by nothing | short | guard in each (`api:15`, `backend:15,58` …) | SV covers none |
| audit | fidelity audit | `audit_validator` (typed) only under `docs/audit/`; today's audits live elsewhere, so nothing validates them; it never asks for the `verdict` block that close needs | short | guard `:11,20,22,28`; review of FULL before merge `:61-65`; "six parts" `:69` | `audit/SKILL.md:36-65` |
| change | change lifecycle | schema of CIT-P/CIT-E records (typed); `:29` names the wrong command (`gov closure`) | none | all CIT-P/CIT-E `:23-61` | — |
| checkpoint | checkpoints | written and read by hooks (auto) | short | guard `:11` | `checkpoint/SKILL.md:19-48` |
| discovery | discovery, packages | package schema id/type/status only; P1-P3 ranking and ≤5 open have no code | short | sandbox `:32`; CIT-P `:35` | — |
| judging-work | one rule for judging | the fenced `verdict` block is parsed at close (fails closed); the rest judgement; **its description is 81 tokens, so the validator exits 1, but no declaration runs it** | none | — | `close/command.py:1496,1803` |
| orchestration | running a wave | trailer gate in `gov close` (typed); package schema thin | none | `:26` gov close; `:36` second review; `:37` three iterations; `:45` six parts | — |
| planning | tickets, gap tickets | `ticket.schema.json` (typed); `gov readiness` (typed); names neither `gov plan` nor feature/fix/chore | none | — | — |
| qa-review | QA before merge | nothing validates the findings report; it never asks for the `verdict` block | short | guard; `:15` review of green | `qa-review/SKILL.md:35-55` |
| retrieval | run `gov retrieve` | stopping reason made by the tool; `validate()` has no caller | **full** `:28-29` | guard `:11` | — |
| spec-writing | write a spec | `check_spec.py` (typed; nine parts, `Fails if:`); wired into no gate | short | guard `:12` | `spec-writing/SKILL.md:47-50` |
| test-design | independent tests | authorship (off path); README map by `gov accept` (typed); red-on-base has no code | none | — | `test-design/SKILL.md:47,51,61-63` |
| superpowers ×3 (debugging, TDD, verification) | vendored v6.4.2 | judgement; no output | none | debugging's "3+ fixes" loop differs from two rounds | `vendored.yaml` |
| openspec-* ×6 (`.claude/skills` only) | OpenSpec workflow | the `openspec validate --strict` CLI (typed, `runner.py:272-278`) | none | — | generated by `openspec` 1.13.2 |
| EXAMIN's 9 own skills | product methods | judgement; no SV declaration | — | — | EXAMIN `.claude/skills/` |

### 1.5 Templates (`template/governance/kernel/templates/`, 22)

| template | for | who fills | class | evidence |
|---|---|---|---|---|
| brief.md (T-0) | envelope and return | `gov brief` (off path); by hand today | checked by `gov brief` only (ready, `{UPPER}` slots); the return's 12 labels by SubagentStop for helpers; `template:`, `commits:`, `brief_gaps:` are read by nothing | `build.py:152-220`; stale `:38,40,62` (sandbox, guard, `guard_refusals:`) |
| keys.yaml | slot names | product-spec | read by `gov brief` | `build.py:343` |
| role-engineer, role-test-designer, role-product-spec, role-research | worker cards | `gov brief`; the generated agent copies keep their slots | judgement; copy equality checked after (typed) | `portability.py:88-89` |
| role-reviewer | probe and verdict block | `gov brief` (also used for qa-engineer) | the verdict block is enforced (off path) at close; READY is computed | `close/command.py:1803-1877` |
| role-lead | lead card, run kinds | not delivered on today's start path | judgement | stale `:49` three iterations, `:51` FULL review, `:13-14` `w2/{W2}` |
| role-cto | CTO card | none: it reaches no session | judgement | `start_cto.sh` appends nothing; stale `:8,24` |
| ticket.md | feature ticket | lead, CTO, product-spec | schema (typed) requires only role, allowed_paths, kpis; ready check (off path); queue notice (off path) | `ticket.schema.json`; `ticket.md:65` contradicts `## Fix:` sections |
| research.md | research record | research | schema checks the frontmatter only (typed); its headings differ from `role-research.md:15` | `research.schema.json` |
| checkpoint.md | checkpoint | hooks, `gov checkpoint` | written by code (auto) | A2 CAP-37.a |
| decision-package.md | owner package | CTO | schema checks id/type/status only; the template has 10 headings, the skill says 6 | A2 MR-6 |
| decision-record.md | register entry | CTO | basis check (typed); owner fact skipped (`check/authority.py:44`) | A2 CAP-01.b |
| failure.md, lesson.md | records | worker, CTO | schema (typed); no writer in `src/gov` | A2 CAP-14.a |
| skill.md | new skill | product-spec | `skill_validator` (typed, partial) | §1.4 |
| brief-engineer, brief-lead, brief-product-spec, brief-reviewer, brief-test-designer | retired stubs | — | n/a | one line each |

**Missing forms** (no template or schema): the lead's return; the senior engineer's hand-offs; a fix section; a chore; a red-landing diagnosis; the auditor's adoption records (A5 and A7/A10 differ by key); the QA findings report.

### 1.6 Hooks and automatic triggers

| hook or trigger | for | class | in Gov OS / EXAMIN / kit | in flight | evidence and fault |
|---|---|---|---|---|---|
| deny `git push`, `sudo` | owner's boundary | enforced (Bash tool only; a script a session runs is not covered) | yes / yes / yes (kit has only the space form) | — | `.claude/settings.json:75-80`. The root `.rulesync/permissions.jsonc` lacks the push deny; the merge keeps it (`merge.py:10-13`), so this is drift, not a hole |
| defaultMode bypassPermissions | no prompts | judgement (state) | yes / yes / **no** (launchers pass it) | — | kit `settings.json` has no `defaultMode` |
| PreToolUse `Agent\|Task` agent_model.py | helper model rule | enforced | yes / old copy / **not in kit** | — | `agent_model.py:159-198`; EXAMIN's 2,124-byte first version lets an unreadable call through; `gov update` never carries it |
| SubagentStop | 12-field return | enforced; fails closed and can loop | yes / yes / yes | 015a F12 | `subagentstop.py:34` (same-line regex), no `stop_hook_active`, `:66-67` exit 2 on any exception (hand-tested) |
| Stop | wake block, checkpoint | enforced (one block per wake); checkpoint is checked after (auto) and needs `GOV_TICKET` | yes / yes / yes | — | `stop.py:64-84`; leads have no `GOV_TICKET`, so no checkpoint |
| PreCompact | checkpoint before compaction | checked after (auto) | yes / yes / yes | — | `precompact.py:175`; same `GOV_TICKET` gap |
| SessionStart `compact\|clear\|resume` | resume, pending update | checked after (auto); not at a fresh start | yes / older / yes | W-5 | `.claude/settings.json:29`; a fresh CTO or lead gets no pending-update line (DEC-1223 (6)) |
| PostToolUse `Bash` context_watch | 85 % reminder | checked after (auto) | yes / **twice** / yes | 015b F4 | EXAMIN `.claude/settings.json` PostToolUse |
| reference-transaction `prepared` | operator ACT freeze | enforced only while a retired file exists (inert) | yes / no / no | — | `.git/hooks/reference-transaction:8-12` |
| reference-transaction `committed`: store refresh | memory current after a landing | checked after (auto); **failed today, no retry, no alert** | yes / no / no | — | `:15`; log 13:53:49 |
| reference-transaction `committed`: landing_select | scoped run after an out-of-ticket landing | checked after (auto) | yes / no / no | — | `:16`; `landing_select.sh` |
| lefthook pre-commit, pre-push | G1/G2/G3, staged secrets | inert (not installed) | no / no (file present) / yes | — | `core.hooksPath` unset; `lefthook.yml.jinja` |
| cron `* * * * *` run_tick.sh | scratch dispatcher | checked after (auto): stall wake, health, GPU; starts nothing (ready.txt has 0 entries) | yes / no / no | e2/w2-207 | `dispatcher.py:3389-3469` |
| cron hourly `gov backup` | bundles outside the trees | checked after (auto) | yes (covers EXAMIN) / — / no | — | last run 14:07 today |
| cron `@reboot` embedders_at_boot.sh | embedders after a restart | checked after (auto); did not hold (90-minute outage today) | yes / no / no | w2-207 MA-5 | crontab |
| cron nightly, morning check, sweep | full regression | inert (commented), against A-1 "keep" | — | — | last nightly 2026-11-17 |
| cron memaudit | weekly measure | inert (no line) | — | — | `memaudit_cron.sh` |
| `.github/workflows/ci.yml` | CI | inert: Gov OS manual; EXAMIN and the kit run on push but have no remote, and push is denied | — | — | `ci.yml:28-30` |
| start_lead.sh (scratch, in use) | start a lead | judgement (the CTO decides); adds `--strict-mcp-config`; no brief check | — | 015a F1, F10 | `start_lead.sh:1-11`; the tracked copy differs |
| start_cto.sh | fresh CTO | enforced: handover present, one name; no MCP flag, no role card | — | models-rubric | `start_cto.sh:11-20` |
| cto_watch.sh | CTO's watcher | checked after (typed, one per CTO) | — | RT-7 | — |

### 1.7 Standing rules (CLAUDE.md, AGENTS.md, the kit head, Charter v6, EMERGENCY-2, the decisions in force)

Duplicates are merged; every copy is cited. AGENTS.md line = CLAUDE.md line + 4. K = `template/.rulesync/rules/governance.md`; X = EXAMIN's generated block.

**Head files**

| rule | for | class | in flight | evidence |
|---|---|---|---|---|
| Read EMERGENCY-2 first; it overrides the Contract | reading order | judgement | — | CLAUDE.md:5; no hook injects it (`sessionstart.py` injects only the checkpoint) |
| Old checkpoint, start page, in-force list are history | no stale reading | judgement | — | CLAUDE.md:5 |
| Trust, catch and correct; no guard, sandbox or prompts | the owner's aim | judgement (state) | — | CLAUDE.md:9; `src/gov/guard` holds only `__pycache__`; nothing refuses re-adding a guard |
| Sessions stay apart by start place, folders and brief | no cross-talk | judgement | — | EMERGENCY-2:62 "nothing enforces it" |
| Two denies: `git push`, `sudo` | owner keeps push | enforced | — | `.claude/settings.json:75-80`; `git -C <dir> push` is untested |
| Releases and re-pins are the owner's | owner's releases | enforced (full release); the patch route is built but off; **the text contradicts DEC-1223/1226** | contract-015 (Charter only) | CLAUDE.md:9, K:19-20, `judging-work:23-24`; `release/command.py:100-108` |
| Feature = ticket with spec and KPIs | sizing | enforced (off path) | — | CLAUDE.md:10; `brief/build.py:157-186`; queue notice `checks.py:111-136` |
| Bug = fix under the owning ticket, failing test first | no fix tickets | enforced (off path) for the landing; judgement for test-first | A-15 | `queue/fix.py`; A2 CAP-31.b |
| Chore = direct commit, tests unchanged, in the digest | no chore tickets | judgement | A-16 | no `--direct` in `src/gov/queue` |
| New KPI line on a closed feature = new ticket | no reopen | judgement | — | nothing refuses |
| Test designer writes acceptance tests, red on base | MR-3 | enforced (off path) for authorship; judgement for red-on-base | e2/l2-4-queue | `queue/checks.py:50-71` |
| Engineer builds until `gov accept` is green | done = green | enforced (off path) | e2/l2-4-queue | `queue/acceptance.py` |
| Landing merges, runs impact tests, checks paths and authors; ticket closes at the land | deterministic landing | enforced (off path); judgement in Gov OS today | e2/l2-4-queue | CLAUDE.md:11 says "by code"; Gov OS hand-merges |
| If red, find and fix the cause | red handling | judgement | — | CLAUDE.md:11 |
| Memory first; read the whole bundle; search once more | use memory | judgement; checked after (typed log) | N-13 | CLAUDE.md:12; `BUNDLE_BUDGET` cuts the bundle (`retrieve.py:48`) |
| Look a decision up by id | decisions by id | judgement | — | CLAUDE.md:12 |
| Roles apart by landing, templates, briefs, skills, path map | separation | checked after (typed) | — | `portability.py:277` |
| A ticket lead never merges | lead stays in branch | judgement | — | CLAUDE.md:25; nothing refuses |
| Auditor is fresh and read-only | independent audit | judgement; enforced (off path) at A5/A7/A10 by a typed id | A-20 | `independent-auditor.md:21` grants Write |
| Kernel and instruction text change only by the CTO | stop drift | judgement | contract-015 | CLAUDE.md:27; no check (A2 CAP-24.c) |
| Value first | golden rule | judgement | — | CLAUDE.md:31 |
| Threat model: honest mistakes, not an adversary | scope | judgement | — | CLAUDE.md:32 |
| What may block (in scope, ordinary, fails open or loses work) | no endless rounds | checked after (auto at close) from the verdict block's fields; triage is judgement | — | `close/command.py:1860-1864` |
| Review only for red, failed landing, broken feature | no review of green | judgement | — | CLAUDE.md:34; `launcher.py:784-792` refuses only a third FULL round |
| Two rounds, then the owner once; READY by code | convergence | enforced (off path) for READY; **the rounds contradict** (`ESCALATION_AT = 3`) | N-04 | `close/state.py:17`; `role-lead.md:49` |
| Golden rules at the head of every adopted CLAUDE.md/AGENTS.md | rules reach adopters | judgement (no check); Gov OS's own file puts them last | N-26 | K:12-27; CLAUDE.md:29-35 |
| Generated block is not hand-edited | one source | checked after (typed) | — | `portability.py:415-446` |
| AGENTS.md ≤ ~1.5k tokens | small head | judgement (no check). Gov OS is ~1.1k tokens, inside the cap; EXAMIN's ~2.7k is over | contract-015 | `telemetry/counter.py:57` estimate |
| EXAMIN head rules (cite ids with meaning; one test process; scan before push) | product hygiene | judgement; "scan before push" contradicts §2.11 | — | X:41-107 |

**Charter v6**

| rule | for | class | evidence |
|---|---|---|---|
| P1 memory in the repo; `.gov-runtime` derived | one truth | checked after (typed) | A2 CAP-07.a |
| P2 one release line; adapters from one source | agnostic | checked after (typed) | `portability.py:415-446` |
| P3 governance is code, not prose | determinism | judgement (meta); lefthook and CI, which it names, are not running | Charter:75-78 |
| P4 deterministic where it can be | the rule this audit assesses | judgement; no code assesses it | Charter:79-82 (A-23) |
| P5 ≤10-15 % governance tokens; no packet ceiling | cost | checked after (typed); the ceiling still exists in code | `telemetry/command.py:32`; `retrieve.py:48` |
| P6 retrieval complete; a stopping reason | accurate memory | enforced (producer); validator unwired | `retrieve.py:795-814` |
| P7 paths allowed, checked at the landing | no write refusal | checked after (a notice, off path) | `queue/checks.py:80-93` |
| P8 the CTO approves every install | tool control | judgement; doctor drift typed; no check that a tool has a row | A2 §2 |
| P9 two rounds then the owner | stop machinery | as above | — |
| MR-1 to MR-6 | master rules | see §4 rows MR-1 to MR-6 | A2 §3 |
| Loop count never shown to the looper | blind loops | judgement; the counter file is readable | A2 CAP-59.b |
| Profiles; no defaulted N/A; spine closes FULL | proportion | checked after (typed) | `readiness/checker.py` |
| Hard boundary: history, hourly bundle, G3 and CI on push | recover | checked after (auto) for the bundle; the G3/CI half is not running | Charter:52-58 |
| Approvals only from the owner's git account | no self-approval | checked after (typed), **defeated** by the skip | `check/authority.py:44` |
| Precedence: Charter, Contract, ADRs; decisions beat documents | conflicts | enforced in retrieval ranking | `retrieval/authority.py:258` |
| Non-goals (guard, sandbox, ACT, root of trust, install gate) | no regrowth | judgement (state) | Charter:221-239 |

**EMERGENCY-2** (rules not already above)

| rule | for | class | in flight | evidence |
|---|---|---|---|---|
| §2.3 the CTO's four places; others only their repo and run folder | access scope | judgement (state) | — | no path denies |
| §2.7 hidden sets: scan voids; reader memory-only; never open the eval folders | honest measure | checked after (typed) for the scan; enforced for the reader; judgement for "never open" | — | `fresh.py:282-303`; `claude.py:31` |
| §2.11 no gitleaks while private | no scan cost | judgement; the kit CI scans on push | N-12 | `ci.yml.jinja:73` |
| §4.5 the rubric from data, set in code | right-sized runs | enforced (helpers); enforced (off path) (`gov launch`); judgement (leads, CTO) | models-rubric | `agent_model.py`; `start_lead.sh:6` |
| §5.2 hit@k no floor anywhere | measure end to end | **contradicted**: `FLOOR, TARGET = 85, 99` | 015b F9 | `retrieval/measure.py:52,78` |
| §5.3 a fresh 80, end to end, 95 % | memory proof | checked after (typed) | e2/d5; models-rubric | `memaudit/fresh.py` |
| §5.4 memory by construction | agents use memory | enforced (off path) for the brief; judgement for starts | N-13 | A2 §5 |
| §5.5 `gov context` off | no ceiling | enforced (the command is gone) | — | `cli/main.py` |
| §5.8 no CPU fallback | memory quality | enforced | — | `semantic.py:541-572` |
| A-1 keep the nightly, brake, slots, dead-man | machine safety | **contradicted**: nightly commented, brake never scheduled, no dead-man line | w2-207 | crontab |
| RT-1 to RT-8 | run-time tool | RT-2, RT-4, RT-6 checked after (auto) or by construction; RT-1 typed; RT-3, RT-7 not built; RT-5 hooks only; RT-8 off path | w2-207; models-rubric | A2 CAP-64 |
| §10.1 basis line checked at the commit; weekly review | no regrowth | checked after (typed) | N-11 | `decisions/basis.py` |
| §10.2 weekly measures | regrowth watch | checked after (typed), partly no code | W-3 | A2 CAP-40.c |
| §10.3 transcripts kept 365 days | scan evidence | enforced (a setting), unchecked | N-16 | `~/.claude/settings.json` |

**Decisions in force** (DEC-1209 to DEC-1231 and older standing ones the digest lists; architecture choices are omitted as not rules)

| rule | for | class | in flight | evidence |
|---|---|---|---|---|
| DEC-1209 no new tickets, leads or rounds | stop the cycle | judgement; lifted in practice by A-10; still whole in the digest | — | register 1851 |
| DEC-1212 (1), 1218 (2), 1229: CTO full window, fresh daily; wake cost measured | CTO cost | judgement; measuring is a scratch script | N-18 | `usage_log.sh` |
| DEC-1212 (2), 1225: helpers Sonnet; another model refused | rubric | enforced | models-rubric | `agent_model.py:159-198` |
| DEC-1225 (1)(5): launched roles and leads Sonnet; role files say so | rubric | enforced (off path); judgement for leads and the CTO; role files still say C3 Opus | models-rubric | `roles/engineer.md:10` |
| DEC-1225 (2): only an owner-asked wide audit on Opus | cost | judgement: the standing auditor exception lets any auditor through | models-rubric R3 | `model-exceptions.yaml:12-13` |
| DEC-1212 (4): no fork; no waiter or idle hooks | usage | enforced (fork); judgement (rest) | — | `agent_model.py:159-167` |
| DEC-1213: AS before A3 | adoption | enforced | — | `stages.py:475` |
| DEC-1214 K2: planned waves; changes ask the owner | owner control | enforced (off path) at launch | — | `launcher.py:47-48` |
| DEC-1214 L2, DEC-1217 (1): close into queue; drop accepted reds; `--direct`; Gov OS lands through the queue | one landing | judgement (not landed) | e2/l2-4-queue | `close/command.py:559`; `path-map.yaml:483,495` |
| DEC-1214 NIGHT, A-1: nightly off until green / keep | regression | judgement (state); contradictory | N-19 | crontab |
| DEC-1214 T2, 1217 (5): push the owner at 95 %/99 % and for stopping decisions | owner alerts | judgement | — | scratch dispatcher |
| DEC-1216 (3): every report ends with the status block | honest status | judgement (scratch `status_block.py`) | A-32 | — |
| DEC-1217 (6): `gov update` never restores removed denies | two denies | enforced | — | `update/core.py:22-24,382-390` |
| DEC-1217 (7): golden rules at the head | adopters | judgement | N-26 | — |
| DEC-1219 (5)(6): launcher takes fix and chore; new ticket flagged at the land | rubric in code | enforced (off path) | — | `launcher.py:45-52`; `checks.py:111-136` |
| DEC-1220 (2): tmux by exact name | no wrong kill | judgement | — | memory note |
| DEC-1221, 1227 D5: Sonnet grading; strict forbidden rule | one grading | checked after (typed); the strict rule is not in HEAD | e2/d5 | `matcher.py` |
| DEC-1222, 1228: imports; MCP tools as imports, given by role | tools | judgement (not built) | 015a F1 | no `imports` module |
| DEC-1223 RB-1/2/7, 1226: patch releases by the CTO by code | release on behalf | enforced, switched off | — | `release/gates.py:64-77` |
| DEC-1223 RB-3 to RB-5: adopted repos wait 4 h after a pin | auto-update | judgement (not built) | w2-207 | — |
| DEC-1224, 1226, 1231: release plan; verdict after 0.1.5 | plan | judgement | e2/d1-verdict | — |
| DEC-1227 D6: patch-only CLI gap exit 0 | quiet drift | checked after (typed) | contract-015 | `9a4adb350` |
| DEC-1227 D7: adopted repos must land | adopt then land | enforced (off path) (nothing refuses either way) | e2/d7-adopt-lands | — |
| DEC-1230: audits read-only on Opus | audits | judgement | — | — |
| DEC-1232 (6): no claude.ai connectors (unrecorded) | fail-open | enforced for leads only | 015a F1 | `start_lead.sh:6` |
| DEC-409, 772: unfreeze and release only by the owner in person | owner acts | enforced | — | `pause/command.py:212-231`; `release/command.py:100-108` |
| DEC-420: `AUTH_REQUIRED` stops launching | no futile launches | judgement (no code) | — | grep: no hit |
| DEC-728, 732, 898: own run folder; worktree runs own `src/`; resource gate | scratch and load | judgement; the gate by convention | — | — |
| DEC-861, 866, 463: the CTO records owner decisions; a commit citing an unrecorded decision is flagged | decision hygiene | checked after (typed); **DEC-1232/1233 are cited unrecorded today** | — | `decisions/checker.py:137-178` |
| DEC-933, 961, 968: nightly at 04:00, check at 08:00 | regression | judgement (state): commented | N-19 | crontab |
| DEC-998, 1007, 1030: dead-man; dispatcher keeps the machine full | liveness | checked after (auto) for the tick; no dead-man | w2-207 | `run_tick.sh` |
| DEC-1088: plan at launch; "closed tickets never edited" | order | enforced (off path); the second half is overturned by §4.2 but still in the digest | — | — |
| DEC-836, 859, 860, 1092: memory used, in batches, search again | memory | judgement | — | — |
| DEC-838, 1146, 1149, 1157: full window; usage never stops a lead | no stalls | judgement | — | — |
| DEC-030 to 037, 091, 815: stopping reasons, closure, canaries | retrieval method | enforced (producers); canaries checked after (typed) | — | A2 CAP-16, 17, 55 |
| DEC-803, 943, 462: entry criteria; brief gaps in every return | brief quality | judgement; `brief_gaps:` is read by nothing | — | A2 §5.2 |

**Contradictions found among the rules** (for the CTO; none fails open):
- Releases: CLAUDE.md, the kit head, `judging-work` and the Charter say the owner's, against DEC-1223/1226.
- The golden rule: placement and three wordings.
- Rounds: two against `ESCALATION_AT = 3` and `role-lead.md:49`.
- Nightly and dead-man: A-1 against DEC-1214 NIGHT and §6.1.
- No ceiling: against `BUNDLE_BUDGET`.
- hit@k: against `FLOOR = 85`.
- Gitleaks: §2.11 against DEC-1182 and EXAMIN's head.
- The in-force digest keeps DEC-1088, 1209, 1215, 933, 953 and 1182 without their changes, because it follows only `Changes:` lines.
- CLAUDE.md:5's "until the Contract is re-baselined": Contract v5 is accepted.
- `LEAD-fixes-015a.md` says Gov OS's settings carry `disableClaudeAiConnectors`; they do not.

---

## 2. List A: what can become deterministic

Ordered by what it protects: **(1) lost work and fail-open**, then **(2) wrong results**, then **(3) drift**, then **(4) cost**. Within a group, the most often hit comes first.

Sizes: XS ≤10 LOC or a configuration line; S ≤50; M ≤200; L more.

Place: **0.1.5** only where it is already in flight or briefed, or is a configuration line; **0.1.6** for the rest of what an honest agent hits in ordinary work; **later** for what needs a construction to hit (EMERGENCY-2 §3.2) or waits on another feature.

### 2.1 Lost work and fail-open

| id | element | the code that would do it (where, smallest form) | size | place (why) | protects |
|---|---|---|---|---|---|
| A-1 | The landing in Gov OS | Run the L2-4 proving landing, then land only through `gov queue` (add `governance/project/queue.yaml`). Retire `land.py`, `close_queue.sh`, `hand_merge_check.sh` and `kernel_gate.py`'s callers | XS (code exists) + chore | 0.1.5, in flight `e2/l2-4-queue` (M-07) | Authorship, impact tests, close at the land: all of §1.2 step 5 moves from judgement to enforced. The hand authorship read has already failed once |
| A-2 | Uncommitted work at the land | `queue/checks.py`: before the merge, `git -C <worktree of the branch> status --porcelain` on tracked and untracked paths. Refuse `QUEUE_WORKTREE_DIRTY`, naming files. Until A-1, the same line in the CTO's hand-merge routine (a chore today) | S | 0.1.5, briefed 015b F8 (N-01) | Lost work: three lead worktrees hold uncommitted trees now, and 30 worktrees are due for removal |
| A-3 | Red on the base | `queue/command.py`: run the ticket's acceptance folder on the merge base (`batch.isolate` at base). Refuse `ACCEPTANCE_GREEN_ON_BASE` when a KPI line is green there, unless the README row carries `pins: <reason>` (as `8a95d3873`'s 5 cases need) | M | 0.1.6 (N-03; under W2-202) | Fail-open: a test that tests nothing passes the land |
| A-4 | No claude.ai connectors; MCP by role | `disableClaudeAiConnectors: true` in the kit settings and Gov OS's settings; `gov launch` passes `--strict-mcp-config` plus the role's MCP list; `start_cto.sh` gets the flag; doctor drift line | S | 0.1.5, briefed 015a F1 (M-03, DEC-1232 (6)) | Fail-open: the CTO session and its helpers reach Gmail, Drive and Calendar today |
| A-5 | Pause stops every starter | `start_lead.sh`, `run_tick.sh` and `gov dispatch` exit while `.gov-runtime/freeze` exists; `gov pause` sends one stop message per live inbox | S | 0.1.5, briefed 015a F10 (N-07) | Fail-open of the owner's brake before releases on his behalf |
| A-6 | Lead start | `gov launch lead --brief <file>` replaces `start_lead.sh`. It appends `role-lead.md`, sets `GOV_TICKET` (so Stop and PreCompact write checkpoints), reads pause and spend, claims the ticket, writes the launch record, takes the rubric model, and refuses a brief with an unfilled `{UPPER}` slot or an empty memory section | M | 0.1.6 (N-06; under W2-136, W2-153) | Lost work: leads write no checkpoint today, so a compaction or crash loses their place. Also wrong results (unready ticket) |
| A-7 | Lead return | At a lead's end, run `subagentstop.check()` over the JSON `result`, plus required lines `branch:`, `head:`, `worktree_clean: yes\|no`. Missing fields go into the wake message to the CTO | S | 0.1.6 (A2 §5.6 #4; under W1-29) | Lost work: an unreported head or an unclean worktree is caught before the CTO acts on it |
| A-8 | Backup age | `gov doctor` part `backup`: newest bundle under 70 min, else unhealthy; doctor in a daily cron line | XS | 0.1.6 code; cron line 0.1.5 chore (N-16, N-19) | Lost work: a 41-hour gap (20-22 Nov) went unnoticed |

### 2.2 Wrong results

| id | element | the code that would do it | size | place (why) | protects |
|---|---|---|---|---|---|
| A-9 | The memory measure's figure | In flight: Sonnet reader and grader (models-rubric R4) and the strict rule (e2/d5). Add: `FIGURES.json` stamps `release`, `commit`, `reader_model`, `grader_models`, `forbidden_rule` and `questions_with_forbidden: n`. `declare` refuses `strict` when no question carries a list | S | 0.1.5 (before EXAMIN's fresh 80; M-01) | A wrong release figure: a 0.1.4-graded or silently lenient figure would look like the new baseline |
| A-10 | Memory current | The minute tick runs `gov rebuild --integration --when-due` (exists, `rebuild/command.py:10-14`) so a failed refresh retries. `gov status` turns red, and `gov brief` names it, when the store is behind HEAD after a failed refresh | XS cron + S | 0.1.5 cron chore; 0.1.6 code | Wrong answers: the store is 23 commits behind now, after a silent failure |
| A-11 | Uncut bundle | `brief/memory.py` carries the bundle text, not index lines; drop `BUNDLE_BUDGET` for the brief's retrieval | S | 0.1.6 (N-13; or the owner re-words CAP-15) | Agents miss evidence; contradicts Charter P5 and CLAUDE.md:12 |
| A-12 | The acceptance map | `gov accept --map-only <ID>` in the queue's pre-checks and as a G1 structural check over `tests/acceptance/*/README.md`. Of the 72 folders that fail today, mark the closed ones `legacy: true` (skipped), fix the live ones | S | 0.1.6 | A KPI line nothing proves is found when the tests are committed, not at the land |
| A-13 | Release certified | `gov release` (full) refuses without `docs/releases/<v>/acceptance.json` all-pass (proving run, EXAMIN fresh 80, Contract checks) | S | 0.1.6 (N-15, after N-27's wording) | A release cut on an unproved candidate |
| A-14 | Owner approval facts | Delete the skip at `check/authority.py:44`; check new ACCEPTED register entries for `Decided-by: owner` | S | 0.1.6 (N-10) | A decision treated as in force without the owner |
| A-15 | A fix | `queue/fix.py` writes the `## Fix: <line>` section in the owning ticket itself from the `Fix:` trailer (the form becomes code). A notice when no test-adding commit precedes the first source commit of the fix (test first) | S | 0.1.6 (CAP-31.b; W-1 part) | A fix recorded nowhere, or with no failing test first |
| A-16 | A chore | `gov queue --direct` for chores (impact-selected tests, no ticket). A notice when a `Class: C` commit changes `tests/**` or `src/**` beyond records | M | 0.1.6 (N-04; L2-6) | A "chore" that changed behaviour lands untested |
| A-17 | Review findings | `qa-review` and `audit` tell the reviewer to end with the fenced `verdict` block (kernel text, the CTO). The close/land parser validates each finding's two lines and severity in the QA report as it does in the probe record | XS text + S | 0.1.6 | Findings that block READY silently: today no record means READY (`close/command.py:1820`) |
| A-18 | Loop budget | Retire `gov close` (B1: `COMMAND_RETIRED`), or `ESCALATION_AT = 2` | XS-S | 0.1.6 (N-04) | A third round against DEC-1204 |
| A-19 | Decision package | `decision-package.schema.json` requires the ten headings; at most five open counted by `gov status` | S | 0.1.6 (A2 MR-6) | Packages missing options or reversibility |
| A-20 | Auditor independence | A5, A7, A10 and AS: compare `auditor_session` with a launch record of role `independent-auditor` that started after the record it checks | S | later (needs A-6's launch records; a typed id is an honest-mistake guard already) | A self-declared "fresh" auditor |
| A-21 | Lite verdict | the VERDICT stage refuses a "not met" condition without an accepted decision | M | 0.1.6, in flight `e2/d1-verdict` (DEC-1231) | An adoption declared healthy on unmet conditions |
| A-22 | Model per launch | Leads and the CTO take the rubric's model from code; role files lose the Opus/Haiku lines; the auditor exception gets a limiter | M | in flight `e2/models-rubric` | Wrong model for the job |
| A-23b | Spec-to-ticket link | `gov brief`'s ready check runs `check_spec.py` on the ticket's spec and refuses when the ticket's KPI lines differ from the spec's K-lines | S | 0.1.6 | Tests written to a ticket that drifted from its spec |

### 2.3 Drift

| id | element | the code that would do it | size | place (why) | protects |
|---|---|---|---|---|---|
| A-23 | **The owner's rule itself** | Each `contract.yaml` item (and each envelope rule and MR) gains `enforcement: {class: code\|checked-after\|judgement, by: <check id, command or path:line>, job: <List B id>}`. A G1 check (`kernel/checks/enforcement.yaml`) refuses an item without it, or with a `by:` that names no existing check or path. `gov status` prints the counts by class. The basis check (`decisions/basis.py`) also requires an `Enforced-by:` line on a new standing rule: a check id, or a List B job | S | 0.1.6 (DEC-1233 (6)) | The rule "deterministic where it can be" drifting back into prose; Gov OS assessed by it |
| A-24 | Role files as delivered | Generated agent files without slots (015a F11). `orchestrator.md` composed from `role-cto.md`, not `role-lead.md`; `independent-auditor.md` without the probe preamble. `start_cto.sh` (later `gov launch orchestrator`) appends `role-cto.md` | XS-S | 0.1.5 (F11, N-08) | Every helper and the CTO read the wrong or unfilled card |
| A-25 | Kernel text lint | A G1 check over `kernel/roles`, `templates` and `skills`: retired phrases (the guard decides, sandbox, permission classes, three iterations, six parts, `gov close`, CIT-P, `gov context`, accepted reds) and a missing memory-first line, as a notice from the reference-transaction hook | XS | 0.1.6, after the kernel sweep (N-24, N-25) | Two stories in agents' heads; CAP-65.b |
| A-26 | Skill health | One `skill-regression` declaration over the whole skills root (it would show `judging-work`'s 81-token description red); the bump check reads `kernel/skills` and `kernel/roles`; a `.claude` copy's version equals its kernel version (catches EXAMIN's `judging-work` 1.1.0) | S | 0.1.6 (A2 CAP-24.a) | Silent skill drift in adopted repositories |
| A-27 | Kit completeness | `agent_model.py` and its hook line in `template/.rulesync/hooks.jsonc`, so `gov update` ships it (EXAMIN runs the old one). `defaultMode` in the kit settings. The root `.rulesync/permissions.jsonc` aligned with the live deny lines | S | 0.1.6 | Adopted repos drift from Gov OS's rules |
| A-28 | Basis at the decision commit | `gov decisions basis HEAD^..HEAD` from the reference-transaction hook, as an inbox notice | XS | 0.1.6 (N-11) | Rules without an incident (A-8 of EMERGENCY-2) |
| A-29 | Schedules | Crontab: the nightly back (A-1 keep), `gov doctor` daily, `memaudit_cron.sh` weekly, `gov decisions basis --week`, `gov spend check` in the tick, `gov telemetry` weekly. G1/G2 as reference-transaction notices instead of a blocking pre-commit (the CTO decides between that and `lefthook install`, against §2.1) | XS | 0.1.5 chore (N-19) | Typed-only checks that nobody types |
| A-30 | Fresh-start injection | add `startup` to the SessionStart matcher, so the pending-update line reaches a fresh CTO and lead | XS | 0.1.6 (W-5; the CTO decides against §11) | DEC-1223 (6) never reaches fresh sessions |
| A-31 | Doctor lines | Deny-lines present; path-map matcher shared with `check/pathmap`; released tag unchanged; 365-day setting | XS each | 0.1.6 (N-16) | Quiet loss of the boundary or the evidence |
| A-32 | Digest and status block | `gov status --digest`: chores (`Class: C` commits), fixes (`Fix:` trailers), tickets landed, and the status block counts, replacing the scratch `status_block.py` | S | 0.1.6 (DEC-1216 (3); §4.6 "listed in the digest") | Hand-counted status; chores never listed |
| A-33 | Containment per commit | `path_notices` per commit `Role`/`Task` | M | later (W-1: a construction to hit) | Paths |

### 2.4 Cost

| id | element | the code that would do it | size | place | protects |
|---|---|---|---|---|---|
| A-34 | SubagentStop | next-line values, `stop_hook_active` exit 0, an exception exits 0 with a stderr line | S | 0.1.5, briefed 015a F12 (N-09) | Endless blocks; tokens on every helper |
| A-35 | Helpers' memory use | the Agent hook passes `GOV_ROLE`/`GOV_TICKET` to the spawn, so a helper's `gov retrieve` is logged with its role | S | 0.1.6 (N-13 part) | "Did the engineer ask memory?" becomes countable |
| A-36 | Session cost | per-session context and wake cost from transcripts, a daily line | S-M | 0.1.6 (N-18, DEC-1229) | CTO and lead spend |
| A-37 | Weekly measures | `gov status --weekly`: product share, owner messages a day, landing time, cost per ticket, governance share red over 0.15 | M | later (W-3) | §10.2 measured by code |
| A-38 | One run-time tool | cron runs `gov dispatch pass`; one watcher; slots from the machine | L | in flight `e2/w2-207-runtime` (after 0.1.5) | Watcher spend; RT-1, 3, 7 |

**Counts:**
- 39 rows (A-23 and A-23b are counted separately).
- By group: 8 lost work or fail-open, 15 wrong results, 11 drift, 5 cost.
- By place: 12 in flight or 0.1.5 (some with a 0.1.6 code part); 24 for 0.1.6; 3 later (A-20, A-33, A-37).

---

## 3. List B: what must stay with agents, specified so

**The rule for every hand-off:** an agent may rely only on what code has checked. Anything else in a hand-off is re-checked by the consumer or by the landing. The "checked by code" line of each entry says which check makes the hand-off safe. "Needed: A-n" points to the List A row that builds it.

### C-0 The common envelope (applies to every entry below)

| | Today | Specified |
|---|---|---|
| **Started by** | Helpers: the Agent tool with `subagent_type`. Leads: `start_lead.sh`. The CTO: `start_cto.sh`. | `gov launch <role> (<ticket> \| --fix "<line>" \| --chore "<line>")` for every session (A-6), which writes a launch record (role, model, effort, template sha256, brief sha256). Helpers stay Agent-tool spawns; the hook passes `GOV_ROLE` and `GOV_TICKET` (A-35). |
| **Receives** | A hand-written prompt. The role file as system prompt, with unfilled slots. | `brief.md` filled by `gov brief <role> <ticket>`. Slots: `{ID} {TITLE} {TICKET_FILE} {PATHS} {COMMIT_PATHS} {SOURCES} {NON_GOALS} {PROFILE} {REGISTER} {BRANCH} {WRITE_TREE} {ROLE} {ROLE_VERSION} {ROLE_TEMPLATE} {DOD_REFS} {LEAD_NOTE}` (drop `{STEP:guard_refusal_lines}`). Then the role template with its own slots, filled. The **memory section** is the `gov retrieve` bundle for the ticket's question, uncut (A-11). The skills on the role's `Skills` line. |
| **Produces** | The 12 fields (helpers only). Trailers typed by hand. | The final message opens with the 12 labelled fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action). `status:` is one of DONE \| PACKAGES \| ESCALATION \| ESCALATION_BLOCKED \| LAUNCH_BLOCKED \| AUTH_REQUIRED. The role's payload comes after. Commits end with one trailer paragraph: `Class: F\|C\|Q`, `Task: <ticket id>\|chore`, `Role: <role>`, `Fix: <line>` (fix only), `Implements: <source ids>`, `Co-Authored-By:`. |
| **Form** | `brief.md`, `keys.yaml`, the role templates, `briefs-and-returns.md:25-55` | Same; plus `return.schema.json` (none today: needed) for the 12 fields and each role's payload keys below. |
| **Checked by code** | SubagentStop for helpers (label presence; enforced). `gov brief` refuses an unready ticket or an unfilled slot (off path). | `gov launch` refuses an unfilled slot or an empty memory section (A-6). SubagentStop forgiving (A-34). The lead's return checked (A-7). The queue notices missing trailers (N-02). |

### B1 Spec and KPIs (product-spec)

| | |
|---|---|
| **Receives** | C-0, with role-product-spec slots `{CONTRACT} {KERNEL} {PATHS}`. The owner's or CTO's idea, or the discovery record and its decision packages. The memory bundle on the feature (prior decisions, specs, KPIs). Skills: `spec-writing` (on no role's Skills line today: add it) and `planning`. |
| **Produces** | (1) The spec `<paths>/<stem>.md` in the nine parts of `spec-writing/spec-form.md` (Problem … Accepted by). (2) KPI lines `- K<n>: <observable behaviour>`, each with `Verify: <how>` and `Fails if: <line>`, no code names. (3) A test-data table with an owner. (4) `<stem>.P1.md` for data that cannot be secured. (5) Open questions as decision packages. (6) The ticket's front matter: `class: feature`, `kpis.success[].line/verify`, `kpis.failure[]`, `allowed_paths`, `sources`, `needs`, `waits_on`. Commits carry `Role: product-spec`, `Task:`, `Implements:`. |
| **Form** | Exists: `spec-form.md`, `templates/ticket.md`, `ticket.schema.json`. |
| **Checked by code** | Today: `check_spec.py` and `gov discover --check` (typed); the ticket schema (typed); `gov brief`'s ready check (off path). Needed: A-23b (the ready check runs `check_spec.py` and refuses a ticket whose KPI lines differ from the spec's K-lines) and A-6 (no lead starts on an unready ticket). |
| **Hand-offs** | To B2 and B3: the ticket's KPI lines. They may rely on each line being observable, having a verify and a failure line, and matching the spec, once A-23b holds. To B14: READY, computed. |

### B2 Independent test design

| | |
|---|---|
| **Receives** | C-0, with role-test-designer slots `{ID} {ACCEPTANCE} {ACCEPTANCE_README} {TESTS_TREE}`. Only the ticket's KPI lines and its Interface section (where it lives, command and error names, signatures), never implementation written after the base. The memory bundle from the integration store only. Skill `test-design`. Its own tests worktree. |
| **Produces** | `tests/acceptance/<ID>/test_*.py`. A `README.md` map: a table `\| KPI \| Test \| pins \|`, with rows `success-N` / `failure-N`, test node ids in code spans, and `pins: <reason>` only for a line that passes on the base by design. `acceptance_tests.path` in the ticket. Commits: `Role: independent-test-designer`, `Task:`, plus `Fix:` for a fix's failing test and `Rewrite-Reason: <decision>` when it changes an existing test. Return payload: `tests: <n> tests; <r> red on base; <p> pinned`. |
| **Form** | Exists: the README form (`test-design/test-kinds.md:27-55`, parsed by `accept/runner.py:139`). Needed: the `pins` column (A-3). |
| **Checked by code** | Today: test authorship, `NO_ACCEPTANCE_TESTS` and `ACCEPT_NO_MAP` in `gov queue` (off path; on path with A-1). Needed: red on the base (A-3) and the map at commit (A-12). |
| **Hand-offs** | To B3: every KPI line has at least one test, fails on the base for the stated reason, and is frozen (a wrong test goes back to B2, never edited by B3). To B13 and the queue: `gov accept <ID>` reports per line. |

### B3 Implementation (engineer)

| | |
|---|---|
| **Receives** | C-0, with role-engineer slots `{ID} {TREE} {TESTS_READY} {UNIT_TEST_PATH}` and the `{CMD:…}` lines. The ticket's KPI lines, `allowed_paths` and Interface. The TESTS-READY marker once B2's tests are merged into its branch. The memory bundle. Skills: TDD plus the domain skill the ticket names (api, backend, data, devops, frontend, security, ui-ux). |
| **Produces** | Code and unit tests inside `allowed_paths`, never under `tests/acceptance/`. Commits with `Role: engineer`, `Task:`, `Implements:`, `Class: F`. Return payload: `accept: <ID> green \| red <lines>`, `loc: <n>`. |
| **Form** | Exists: `role-engineer.md`; the commit block in `brief.md:48-68`. |
| **Checked by code** | Today: the 12 fields (enforced). Needed on path, via A-1: an acceptance-path edit refused (authorship); the containment notice; `gov accept` at the land. |
| **Hand-offs** | To B13: the branch with `gov accept` green. The queue trusts nothing in the return: it re-runs the tests. |

### B4 A fix

| | |
|---|---|
| **Receives** | The owning ticket id, the bug as one line (the `Fix:` line), the failing evidence (log, test output, report id), the memory bundle. Started with `gov launch <role> <ticket> --fix "<line>"`. |
| **Produces** | (1) When no test caught the bug: a failing test by B2 with `Role: independent-test-designer` and `Fix: <line>`, committed **first**. (2) The change by B3, with `Task: <owning ticket>` and `Fix: <line>`. (3) A section `## Fix: <line> (<source>)` in the owning ticket: cause, test, commits, landed head. No new ticket. |
| **Form** | Today prose only (`.tickets/DAEO-xm6l.md:84-96`; `ticket.md:65` says the opposite). Needed: the queue writes the section itself from the trailer, so the form is code (A-15). |
| **Checked by code** | Today: `gov queue`'s fix landing needs `Task:` plus `Fix:` on a closed ticket (off path; A-1). The patch rule P3 reads `Fix:` (`release/patch.py:152-170`). Needed: the test-first notice (A-15). |
| **Hand-offs** | To the digest (A-32) and the release notes (they read `Fix:`). The owning ticket's record is the history. |

### B5 A chore

| | |
|---|---|
| **Receives** | One line saying what and why, and the paths (records, docs, configuration). No ticket. |
| **Produces** | A direct commit with `Class: C`, `Task: chore`, `Role: <role>`. Tests unchanged. Landed by `gov queue --direct` (A-16). |
| **Form** | None: needed. One trailer form (`Task: chore`; briefs use `chore` and `emergency-2` today), fixed in LEAD-COMMON and read by A-16 and A-32. |
| **Checked by code** | Needed: A-16 (impact tests run; a notice when `tests/**` or `src/**` changed) and A-32 (listed in the digest). |
| **Hand-offs** | To the digest; to the patch release notes (`- Chore:`, `release/patch.py:236-254`). |

### B6 Review after a red landing

| | |
|---|---|
| **Receives** | The queue's red list `reds[{test, verdict: flaky\|base\|culprit}]` (`queue/command.py:715-721`), the merged head, the ticket, the failing logs. role-reviewer slots `{ID} {HEAD} {TREE}`. Skill `judging-work`. The memory bundle for the failing area. Sonnet (DEC-1225 (2)). |
| **Produces** | Either a fix (then B4), or a probe record `docs/probes/<ticket>/<n>.md` with `probe.schema.json` front matter. It holds one `cause:` line per red id the queue listed, and each finding as scope, severity, `Ordinary work: yes\|no, because …` and `Consequence: fails open\|loses work\|other`. The fenced `verdict` block comes last. |
| **Form** | Exists: `role-reviewer.md`, `probe.schema.json`. Needed: the `cause:` line per queue red id (a red-landing diagnosis form). |
| **Checked by code** | Today: the close parser computes READY from the verdict block and blocks on a malformed finding (`close/command.py:1803-1877`; typed or off path). Needed (A-17): the same parse when the queue re-lands, a refusal when a queue red id has no `cause:` line, and "no record means READY" only when there was no red. |
| **Hand-offs** | To the moderator (B14, or B15 for a stream): triage against scope. At most two rounds; READY computed. |

### B7 The independent auditor's verdict

| | |
|---|---|
| **Receives** | The question, the scope, the evidence pack (paths and commit), the yardstick (sources plus accepted decisions), read-only, and its one output path. The memory bundle. Skills `audit` and `judging-work`. A fresh session, started by `gov launch independent-auditor` (A-6, A-20). |
| **Produces** | One report: front matter `milestone`, `commit`, `pack_sha256`; a table `item \| class \| evidence`; each blocking finding with the two lines; the fenced `verdict` block. Nothing else written. |
| **Form** | Exists: `audit-report.schema.json`, which applies to `docs/audit/**` only. The E2 audits (this one included) use none of it. Needed: the validator reads `docs/emergency-2/audits/` too, or audits use the form. |
| **Checked by code** | Today: `audit_validator` (typed). Needed: run in the queue's structural family for report paths; A-20 for freshness. |
| **Hand-offs** | To the owner and the CTO. At release acceptance, the release gate reads its verdict (A-13). |

### B8 Research

| | |
|---|---|
| **Receives** | The question, the decision it feeds, a stop rule, one experiment folder, a budget. The memory bundle. Skill `discovery`. |
| **Produces** | `research.md` in the folder with the headings Question, Decision it feeds, Stop rule, Method, Sources, Measurements, Uncertainty, Conclusion, and front matter `decisions:`, `sources:`. One commit, `Role: research`. Return payload: `verdict:` in two lines. |
| **Form** | Exists: `templates/research.md`, but its headings differ from `role-research.md:15`. Needed: one heading list. |
| **Checked by code** | Today: front matter by schema (typed); research cannot become authority (`check/authority.py:13,60`, typed). Needed: the body headings in the schema, run in the queue's record gate. |
| **Hand-offs** | To B14, which writes a decision or KPI lines from the verdict. B14 may rely on research never becoming authority (code). |

### B9 Planning a wave

| | |
|---|---|
| **Receives** | The owner's goals and decisions, `gov readiness` rows, open tickets, the rubric, the memory bundle. Skill `planning`. |
| **Produces** | Feature tickets (B1's form) and gap tickets linked to readiness rows. A wave file `governance/project/waves/<n>.yaml` (tickets, order, owner's approval id). `gov plan` output and its `--ready` list. |
| **Form** | Exists: `ticket.md` and its schema. Needed: the wave file form (DEC-1214 K2's set list), read by `gov plan` and by the launcher's plan check (`launcher.py:47-48`). |
| **Checked by code** | Today: `gov plan` findings (typed); the ready check (off path). Needed: `ticket.schema.json` requires `class`; a ticket added to a planned wave without the owner's id is a queue notice. |
| **Hand-offs** | To B14 and the dispatcher: launch in plan order. |

### B10 Memory measure: question writing and checking

| | |
|---|---|
| **Receives** | The writer brief from `gov memaudit brief --kind writer`, with slots `{{repository}} {{round}} {{half}} {{commit}} {{sample_size}} {{exclude}} {{category_count}} {{by_area}} {{min_kept}} {{half_less_one}}`, plus `seed.txt`, `input/selection.json` and the pinned snapshot. **No memory bundle.** The checker gets its brief and `input/set/`. |
| **Produces** | Writer: `out/set/qNN.yaml` (id, question, gold_answer, sources, commit, category, drawn, `forbidden:` list) and `result.json` counts. Checker: `notes.md` in the "# Cross-check notes" form (accept \| revise \| reject per id) and `result.json`. |
| **Form** | Exists: `memaudit/briefs/writer.py`, `checker.py`, `deliver.py`. |
| **Checked by code** | Enforced inside `fresh`: `deliver` (DL-*), ten pre-flight checks, drops, single-use declare. Needed (A-9): the count of questions with a `forbidden` list, and a refusal of strict grading when none has one. Then the transcript scan. |
| **Hand-offs** | To B11, which never sees the gold. The CTO sees counts only. |

### B11 Memory measure: reading

| | |
|---|---|
| **Receives** | One question. The product's memory tool only (`--tools ""` plus `gov retrieve`). Sonnet (R4). |
| **Produces** | JSON `{verdict: answer\|search_again\|not_found, answer, citations: [path:line]}`. At most three loops. |
| **Form** | Exists: `prompts.py` READER_SYS and its schema (hash-tested). |
| **Checked by code** | Code runs it (`judge.py:78-122`); the JSON schema; the citation matcher (`matcher.py`). |
| **Hand-offs** | To B12. |

### B12 Memory measure: grading

| | |
|---|---|
| **Receives** | The question, the gold answer, sources, the `forbidden` list, the reader's answer and citations. |
| **Produces** | `correct \| wrong \| not_found`, plus a second grade from another model as a check. |
| **Form** | Exists: `prompts.py`. |
| **Checked by code** | `outcome()`: right only if the grade is correct, the citation is right and no forbidden path is cited (e2/d5). The figures and the 95 % verdict are code. Needed: the second grader's disagreement as a printed notice, and the figure stamp (A-9). |
| **Hand-offs** | `FIGURES.json` goes to the owner and to the release gate (A-13). |

### B13 The ticket lead's loop

| | |
|---|---|
| **Receives** | `gov launch lead <ticket> --brief <file>` (A-6): the brief (ticket, branch, worktree, base, KPI lines or the fixes, the green set). `role-lead.md` filled (`{ID} {BASE} {TREE} {TESTS_TREE} {STORE_TREE} {TICKET_FILE} {RUN_KIND}`; drop `{KNOWN_REDS}`, `{STEP:context_ceiling}`, `{STEP:scratch_measure}`). `LEAD-COMMON.md`. The memory bundle. Environment `GOV_TICKET`, `GOV_ROLE=ticket-lead`, `GOV_MSG_ADDRESS`. |
| **Produces** | The branch and its commits. B2, B3 (and B6 on red) as helpers. Never a merge. The final message: the 12 fields, then `branch:`, `head:`, `worktree_clean: yes\|no`, `accept: <per KPI line>`, `reds_not_mine:`, `owner_line:`. |
| **Form** | Today `role-lead.md:78-82` and `LEAD-COMMON.md:28` disagree. Needed: one return form in `role-lead.md`, with the field list held in code (A-7). |
| **Checked by code** | Needed: A-7 (fields), A-2 (clean worktree at the land), A-1 (the queue re-checks the rest). |
| **Hand-offs** | To B14, which may rely on branch, head and clean. The queue re-runs everything else, so the CTO trusts no other claim. |

### B14 CTO orchestration

| | |
|---|---|
| **Receives** | `gov launch orchestrator` (or `start_cto.sh` with `role-cto.md` appended, A-24): CLAUDE.md, EMERGENCY-2, the handover, the inbox, `gov status --json` and `--digest`, the in-force digest, the memory bundle. |
| **Produces** | Register entries (`decision-record.md`, with `Basis:`, `Enforced-by:` (A-23), `Decided-by: owner (chat, date)`). Briefs filled by `gov brief`. Packages with ten headings. Lead launches by `gov launch`. Landings by `gov queue`. The digest and status block (A-32). The handover in the checkpoint form. |
| **Form** | Exists: `decision-record.md`, `decision-package.md`, `role-cto.md`, `checkpoint.md`. Needed: the digest (A-32); the handover as a checkpoint with a RESUME HERE section. |
| **Checked by code** | Today: basis (typed); package schema (thin). Needed: A-28, A-14, A-19, A-23; the queue does the landing (A-1). |
| **Hand-offs** | To the owner (packages, digest), to leads (briefs), to the next CTO (handover). |

### B15 Senior engineer (one stream under the CTO)

| | |
|---|---|
| **Receives** | From B14: a stream (its ticket list), the decisions, its stream folder. Not used today: leads run directly under the CTO. Build only when several streams run. |
| **Produces** | Hand-offs `READY_TO_CLOSE`, `PACKAGES`, `ESCALATION`, `STATE`, `STREAM_CHECKPOINT` as `gov msg` messages of those kinds, each with `ticket`, `head`, `evidence`, `decision_needed`. |
| **Form** | None: needed. `stream-handoff.schema.json`. |
| **Checked by code** | None: needed. `gov msg send` validates the kind and its keys. |
| **Hand-offs** | To B14. It may rely on READY_TO_CLOSE meaning the queue's land passed, not the lead's word. |

### B16 Adoption's judged stages (A5, A7, A10, AS answers, the lite verdict)

| | |
|---|---|
| **Receives** | The stage's input records (A3 path map, AS record, inventory) with their sha256, the yardstick, read-only. A fresh session (A-20). |
| **Produces** | A verdict record: front matter `stage`, `verdict: pass\|not met`, `auditor_session`, `checked: [{record, sha256}]`, `conditions: [{id, met, evidence}]`. Committed with `Role: independent-auditor`. |
| **Form** | Exists: `adoption-verdict.schema.json`, which no code writes. A5 uses another key set than A7 and A10. Needed: one schema for all four. |
| **Checked by code** | Enforced: `adopt/stages.py:541-565` and `lite_gates.py:62-105` refuse NO_VERDICT, VERDICT_NOT_PASS, VERDICT_OTHER_RECORD and VERDICT_NOT_INDEPENDENT. AS has no auditor (needed). The verdict stage is in flight (`e2/d1-verdict`, A-21). |
| **Hand-offs** | To `gov adopt`'s next stage, and to the owner for an exception. |

**Where List B stands today:**
- **Form and check both exist:** B10, B11, B12 and B16 (not AS).
- **The form exists, but its check is off path or typed:** B1, B2, B3 and B6.
- **No form, or no check:** B4, B5, B7, B8, B9, B13, B14 and B15.

---

## 4. The Contract and Charter fields

### 4.1 Every Contract item: built, enforced today, why not and when, what it should be

There are 320 rows: 6 envelope rules, 6 master rules, 69 capabilities and 239 covers items, extracted from `docs/contract/contract.yaml`.
- **Classes** come from A2 §3, §4 and §5.4, and changed only where a commit since `3ab01e94b` or an in-flight branch changes them.
- **Built:** "yes" on a judgement row means the instruction text exists.
- **Enforced today:** "code" means enforced; "code off path" means enforced (off path). A split cell lists the stronger part first.
- **CAP-nn rows** are roll-ups: the weakest class of their live items.
- **"Should be":** a code check, in eight words or fewer, or "agent: Bn" naming the List B entry.
- **Placements:** 0.1.6 and Wave 3 placements are the merged table's proposals (N-nn, W-n) or List A rows (A-n), not owner decisions. F-n are items of briefs 015a and 015b.

| id | wave | built | enforced today | if not built: why and when | should be |
|---|---|---|---|---|---|
| ENV-scale | — | part | judgement | later (a tested limit; no check measures a graph against it) | code: A1 inventory notes graph over 80k nodes |
| ENV-ram | — | part | code / none | in flight: e2/w2-207-runtime (ticket only; RT-3) | code: slots from detected machine |
| ENV-token | — | part | checked after typed / none | Wave 3 (W-3); limit text: brief contract-015 | code: status line red over 0.15 |
| ENV-boundary | — | yes | code / checked after auto / judgement | - | code: deny-lines assertion in portability |
| ENV-loop | — | part | code off path | 0.1.6 (N-04) | code: ESCALATION_AT = 2 |
| ENV-tool_installs | — | part | checked after typed / judgement | 0.1.6 (N-09 imports); F2 in flight: brief fixes-015b | code: doctor lists tools lacking row |
| MR-1 | — | part | code off path / checked after typed | 0.1.6 (N-06) | code: lead start refuses unready ticket |
| MR-2 | — | part | checked after typed | Wave 3 (W-4) | code: core-claims on branch's new tickets |
| MR-3 | — | part | code off path / judgement / none | in flight: e2/l2-4-queue; red-on-base 0.1.6 (N-03) | code: queue runs acceptance on base |
| MR-4 | — | part | code off path / none / judgement | 0.1.6 (N-15); AS Wave 3 (W-4) | code: gov release needs acceptance record |
| MR-5 | — | part | checked after typed | 0.1.5 (N-08; F11 brief fixes-015a) | code: portability refuses unfilled slot |
| MR-6 | — | part | judgement | Wave 3 (W-5); skill text 0.1.6 (N-25) | code: schema requires ten headings |
| CAP-01 | W1 | part | checked after typed / code | roll-up of its items | see items |
| CAP-01.a | W1 | yes | code | - | code: as built |
| CAP-01.b | W1 | part | checked after typed | 0.1.6 (N-10) | code: drop skip; check Decided-by owner |
| CAP-01.c | W1 | yes | checked after typed | - | code: as built |
| CAP-01.d | W1 | yes | code | - | code: as built |
| CAP-02 | W1 | yes | checked after typed | roll-up of its items | see items |
| CAP-02.a | W1 | yes | checked after typed | - | code: doctor in queue after-step |
| CAP-02.b | NONE | no | n/a | non-goal | — |
| CAP-02.c | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-03 | W1 | part | none / code | roll-up of its items | see items |
| CAP-03.a | W1 | part | code / none | 0.1.6 (N-12) | code: gov release --public runs one scan |
| CAP-03.b | W1 | yes | code | - | code: as built |
| CAP-03.c | W1 | yes | code | - | code: as built |
| CAP-03.d | W1 | yes | code | - | code: as built |
| CAP-03.e | W1 | yes | code | - | code: as built |
| CAP-04 | W2 | part | code off path / checked after typed | - | code: gov spend check in minute tick |
| CAP-04.a | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-04.b | W1 | yes | checked after typed | - | code: weekly cron line for telemetry |
| CAP-04.c | W1 | no | none | 0.1.6 (N-13) | code: drop BUNDLE_BUDGET ceiling |
| CAP-04.d | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-05 | W1 | part | none / code off path / code | roll-up of its items | see items |
| CAP-05.a | W1 | part | code off path / none | 0.1.5 (F10, brief fixes-015a) | code: start scripts exit while frozen |
| CAP-05.b | W1 | yes | code | - | code: as built |
| CAP-05.c | W1 | yes | code | - | code: as built |
| CAP-05.d | W1 | yes | code | - | code: as built |
| CAP-06 | W1 | part | checked after typed / code off path / code | roll-up of its items | see items |
| CAP-06.a | W1 | part | checked after typed | 0.1.6 (N-16) | code: doctor reuses pathmap matcher |
| CAP-06.b | W1 | yes | code off path | - | code: as built |
| CAP-06.c | W1 | yes | code off path | - | code: as built |
| CAP-06.d | W1 | yes | code off path | - | code: as built |
| CAP-06.e | W1 | yes | code | - | code: as built |
| CAP-07 | W1 | yes | checked after typed / code | roll-up of its items | see items |
| CAP-07.a | W1 | yes | code / checked after typed | - | code: as built |
| CAP-07.b | W1 | yes | code / checked after typed | - | code: as built |
| CAP-08 | W1 | yes | code | roll-up of its items | see items |
| CAP-08.a | W1 | yes | code | - | code: as built |
| CAP-09 | W1 | yes | checked after typed / code | roll-up of its items | see items |
| CAP-09.a | W1 | yes | code / checked after typed | - | code: as built |
| CAP-09.b | W1 | yes | code / checked after typed | - | code: as built |
| CAP-10 | W1 | yes | checked after typed | in flight: e2/d5-memaudit-strict (grading rule) | code: install weekly memaudit cron line |
| CAP-10.a | W1 | yes | code | - | code: as built |
| CAP-10.b | W2 | yes | code | - | code: as built |
| CAP-11 | W1 | yes | code | roll-up of its items | see items |
| CAP-11.a | W1 | yes | code | - | code: as built |
| CAP-12 | W1 | yes | code | roll-up of its items | see items |
| CAP-12.a | W1 | yes | code | - | code: as built |
| CAP-12.b | W1 | yes | code | - | code: as built |
| CAP-13 | W1 | yes | checked after typed / code | roll-up of its items | see items |
| CAP-13.a | W1 | yes | code / checked after typed | - | code: as built |
| CAP-13.b | W1 | yes | code | - | code: as built |
| CAP-14 | W1 | part | code | roll-up of its items | see items |
| CAP-14.a | W1 | part | code | Wave 3 (W-2) | code: failure-record writer at red landing |
| CAP-15 | W2 | part | code off path | 0.1.6 (N-13) | code: brief carries bundle text |
| CAP-15.a | W2 | yes | code off path | - | code: lead start requires gov brief |
| CAP-15.b | W2 | yes | code off path | - | code: lead start requires gov brief |
| CAP-15.c | W2 | yes | code off path | - | code: lead start requires gov brief |
| CAP-15.d | NONE | no | n/a | non-goal | — |
| CAP-15.e | W2 | part | code off path | 0.1.6 (N-06) | code: launch record holds brief sha |
| CAP-15.f | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-15.g | NONE | no | n/a | non-goal | — |
| CAP-16 | W1 | part | judgement / code | roll-up of its items | see items |
| CAP-16.a | W1 | yes | code | - | code: as built |
| CAP-16.b | W1 | part | judgement | Wave 3 (W-2) | code: call validate() at end of retrieve |
| CAP-16.c | W1 | yes | code | - | code: as built |
| CAP-17 | W1 | part | checked after typed / checked after auto / code | roll-up of its items | see items |
| CAP-17.a | W1 | yes | code | - | code: as built |
| CAP-17.b | W2 | yes | checked after auto (fails silently: note 9) | 0.1.5 chore + 0.1.6 (A-10) | code: retry when due; status red when behind |
| CAP-17.c | W1 | part | checked after typed | Wave 3 (W-2) | code: canaries at end of gov rebuild |
| CAP-18 | W1 | yes | code | roll-up of its items | see items |
| CAP-18.a | W1 | yes | code | - | code: as built |
| CAP-18.b | W1 | yes | code | - | code: as built |
| CAP-19 | W2 | part | none / code | roll-up of its items | see items |
| CAP-19.a | W2 | yes | code | - | code: as built |
| CAP-19.b | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-19.c | W2 | part | none | Wave 3 (W-2) | code: memaudit records each miss |
| CAP-20 | W1 | yes | checked after typed | roll-up of its items | see items |
| CAP-20.a | W1 | yes | checked after typed | - | code: as built |
| CAP-21 | W1 | part | judgement / checked after typed | roll-up of its items | see items |
| CAP-21.a | W1 | part | checked after typed / judgement | 0.1.6 (N-10); kernel text see CAP-24.c | code: as CAP-01.b |
| CAP-21.b | NONE | no | n/a | non-goal | — |
| CAP-22 | W2 | part | judgement / checked after typed / checked after auto / code off path | roll-up of its items | see items |
| CAP-22.a | W1 | part | checked after typed | 0.1.5 (N-08; F11 brief fixes-015a) | code: portability refuses unfilled slot |
| CAP-22.b | W2 | part | checked after auto | 0.1.6 (N-06) | code: end message names return file |
| CAP-22.c | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-22.d | W1 | yes | judgement / code off path | - | agent: B8 |
| CAP-23 | W2 | part | none / judgement / code off path / code | roll-up of its items | see items |
| CAP-23.a | W1 | part | none | 0.1.6 (N-06) | code: gov launch calls claims.claim |
| CAP-23.b | W2 | part | code | in flight: e2/w2-207-runtime (ticket only) | code: cron on gov dispatch tick |
| CAP-23.c | W2 | part | code off path / judgement | in flight: e2/l2-4-queue | code: Gov OS lands through gov queue |
| CAP-24 | W1 | part | none / judgement / checked after typed / checked after auto | roll-up of its items | see items |
| CAP-24.a | W1 | part | checked after auto | Wave 3 (W-2) | code: bump check reads kernel/skills |
| CAP-24.b | W1 | yes | checked after typed | - | code: as built |
| CAP-24.c | W1 | part | judgement / none | 0.1.6 (N-29, owner picks); wording: brief contract-015 | agent: B14 |
| CAP-25 | W1 | part | judgement / checked after typed / code | roll-up of its items | see items |
| CAP-25.a | W1 | yes | checked after typed | F2 in flight: brief fixes-015b (doctor finds own-folder tools) | code: doctor in daily cron line |
| CAP-25.b | W1 | part | judgement / code | 0.1.6 (N-09) | code: doctor lists tools lacking row |
| CAP-25.c | NONE | no | n/a | non-goal | — |
| CAP-25.d | W1 | yes | checked after typed | D6 landed 9a4adb350; wording: brief contract-015 | code: as built |
| CAP-25.e | NONE | no | n/a | non-goal | — |
| CAP-25.f | NONE | no | n/a | non-goal | — |
| CAP-25.g | NONE | no | n/a | non-goal | — |
| CAP-26 | NONE | no | n/a | non-goal | — |
| CAP-26.a | NONE | no | n/a | non-goal | — |
| CAP-27 | W1 | yes | checked after typed | roll-up of its items | see items |
| CAP-27.a | W1 | yes | checked after typed | - | code: as built |
| CAP-27.b | NONE | no | n/a | non-goal | — |
| CAP-28 | W1 | part | judgement / code | roll-up of its items | see items |
| CAP-28.a | W1 | part | judgement | 0.1.6 (N-25) | code: status block from script |
| CAP-28.b | W1 | yes | code | - | code: as built |
| CAP-29 | W3 | no | n/a | Wave 3 by design | — |
| CAP-29.a | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-29.b | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-30 | W2 | part | judgement / checked after typed / code off path | roll-up of its items | see items |
| CAP-30.a | W1 | yes | checked after typed | - | code: as built |
| CAP-30.b | W1 | yes | code off path | 0.1.6 (N-06) | code: lead start refuses non-READY ticket |
| CAP-30.c | W2 | yes | checked after typed | - | code: as built |
| CAP-30.d | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-30.e | W1 | yes | checked after typed | - | code: as built |
| CAP-30.f | W1 | part | judgement | Wave 3 (W-1) | code: notice if src precedes acceptance commit |
| CAP-30.g | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-31 | W1 | part | none / checked after typed / code off path / code | roll-up of its items | see items |
| CAP-31.a | W1 | yes | checked after typed / code off path | - | code: as built |
| CAP-31.b | W1 | part | code off path / none | Wave 3 (W-1) | code: test commit before source in fix |
| CAP-31.c | W1 | yes | code | - | code: as built |
| CAP-31.d | W1 | yes | code off path | - | code: as MR-1 |
| CAP-32 | W3 | yes | judgement / checked after typed | roll-up of its items | see items |
| CAP-32.a | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-32.b | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-32.c | W1 | yes | judgement | - | agent: B8 |
| CAP-32.d | W2 | yes | checked after typed | - | code: as built |
| CAP-33 | W2 | part | judgement / checked after typed | roll-up of its items | see items |
| CAP-33.a | W1 | part | judgement | 0.1.6 (N-25) | agent: B14 |
| CAP-33.b | W2 | yes | checked after typed | - | code: as built |
| CAP-33.c | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-33.d | W1 | part | judgement | Wave 3 (W-1) | code: notice on contract/charter edit without DEC |
| CAP-33.e | W1 | yes | judgement | - | agent: B14 |
| CAP-33.f | W1 | yes | judgement | - | agent: B14 |
| CAP-33.g | W2 | yes | judgement | - | agent: B14 |
| CAP-34 | W1 | part | judgement / checked after typed / code | roll-up of its items | see items |
| CAP-34.a | W1 | yes | judgement | - | agent: B14 |
| CAP-34.b | W1 | part | judgement | Wave 3 (W-5) | code: schema requires ten headings |
| CAP-34.c | W1 | yes | judgement | - | agent: B14 |
| CAP-34.d | W1 | yes | checked after typed | - | code: as built |
| CAP-34.e | W1 | yes | code | - | code: as built |
| CAP-35 | W2 | part | none / code off path / code | roll-up of its items | see items |
| CAP-35.a | W2 | part | code off path / code / none | in flight: e2/models-rubric (ticket only); leads 0.1.6 (N-06) | code: lead start through gov launch |
| CAP-35.b | W2 | part | code off path / code / none | in flight: e2/models-rubric (ticket only); leads 0.1.6 (N-06) | code: lead start through gov launch |
| CAP-35.c | W2 | part | code off path / code / none | in flight: e2/models-rubric (ticket only); leads 0.1.6 (N-06) | code: lead start through gov launch |
| CAP-36 | W3 | no | n/a | Wave 3 by design | — |
| CAP-36.a | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-37 | W1 | part | none / judgement / code | roll-up of its items | see items |
| CAP-37.a | W1 | yes | code | - | code: as built |
| CAP-37.b | W1 | part | code / judgement | - | code: gov launch writes start checkpoint |
| CAP-37.c | W1 | part | code / none | in flight: e2/w2-207-runtime (ticket only) | code: schedule stale-session marking |
| CAP-37.d | W1 | part | code / none | 0.1.5 (F12 brief fixes-015a, hook); leads 0.1.6 (N-06) | code: field check on lead return |
| CAP-37.e | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-37.f | W1 | yes | code | Wave 3 (W-5, startup matcher) | code: as built |
| CAP-37.g | W1 | yes | code | - | code: as built |
| CAP-38 | W1 | yes | code off path / checked after typed | in flight: e2/l2-4-queue | code: as built (queue runs gov accept) |
| CAP-38.a | W1 | yes | judgement | - | agent: B2 |
| CAP-38.b | W1 | yes | checked after typed | - | code: as built |
| CAP-38.c | W1 | part | code off path / judgement | in flight: e2/l2-4-queue | code: Gov OS lands through gov queue |
| CAP-38.d | W1 | part | none | 0.1.5 (N-19; nightly --optin added 074856dad) | code: restore nightly cron line |
| CAP-38.e | W1 | yes | judgement | - | agent: B2 |
| CAP-38.f | NONE | no | n/a | non-goal | — |
| CAP-39 | W2 | part | none | 0.1.6 (N-02) | code: queue refuses on STORE_STALE |
| CAP-39.a | W1 | yes | checked after typed | 0.1.5 (N-19, lefthook check first) | code: lefthook install |
| CAP-39.b | W2 | yes | checked after typed | - | code: as built |
| CAP-39.c | W2 | part | code off path / judgement | in flight: e2/l2-4-queue | code: Gov OS lands through gov queue |
| CAP-39.d | W1 | yes | code | - | code: as built |
| CAP-39.e | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-40 | W1 | part | none / checked after typed | roll-up of its items | see items |
| CAP-40.a | W1 | part | checked after typed | 0.1.6 (N-06) | code: gov launch writes lead session record |
| CAP-40.b | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-40.c | W1 | part | none | Wave 3 (W-3) | code: gov status --weekly |
| CAP-40.d | NONE | no | n/a | non-goal | — |
| CAP-41 | W1 | yes | judgement / checked after typed | roll-up of its items | see items |
| CAP-41.a | W1 | yes | judgement | - | agent: B14 |
| CAP-41.b | W1 | yes | checked after typed | - | code: as built |
| CAP-41.c | W1 | yes | checked after typed | - | code: as built |
| CAP-41.d | W1 | yes | judgement | - | agent: B14 |
| CAP-41.e | NONE | no | n/a | non-goal | — |
| CAP-41.f | W1 | yes | checked after typed | - | code: as built |
| CAP-41.g | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-41.h | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-41.i | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-41.j | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-42 | W1 | yes | code off path | roll-up of its items | see items |
| CAP-42.a | W1 | yes | code off path | - | code: as built |
| CAP-42.b | W1 | yes | code off path | - | code: as built |
| CAP-42.c | W1 | yes | code off path | - | code: as built |
| CAP-43 | W1 | part | judgement / checked after typed / code | roll-up of its items | see items |
| CAP-43.a | W1 | yes | code / checked after typed | - | code: as built |
| CAP-43.b | W2 | yes | code | - | code: doctor tag-immutability line |
| CAP-43.c | W2 | part | judgement / code | plain release 0.1.6 (N-15, after N-27); wording: brief contract-015 | code: gov release needs acceptance.json |
| CAP-43.d | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-44 | W3 | part | none / checked after typed / code off path / code | roll-up of its items | see items |
| CAP-44.a | W1 | yes | code | - | code: as built |
| CAP-44.b | W1 | yes | code off path | - | code: as built |
| CAP-44.c | W1 | part | code off path | - | code: session id vs launch record |
| CAP-44.d | W1 | yes | code off path | - | code: as built |
| CAP-44.e | W1 | yes | code off path | - | code: as built |
| CAP-44.f | W2 | part | code off path / none | AS Wave 3 (W-4) | code: AS takes verdict held to auditor |
| CAP-44.g | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-44.h | W2 | part | checked after typed | in flight: e2/d1-verdict (ticket only); rides 0.1.6 (DEC-1231) | code: VERDICT stage refuses unmet condition |
| CAP-44.i | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-44.j | W1 | yes | code off path | - | code: as built |
| CAP-44.k | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-44.l | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-44.m | W2 | yes | code off path | - | code: as built |
| CAP-45 | W2 | part | checked after auto / code | roll-up of its items | see items |
| CAP-45.a | W2 | yes | code | F4 and F6 in flight: brief fixes-015b | code: as built |
| CAP-45.b | W2 | part | checked after auto | Wave 3 (W-5, startup matcher; CTO decides) | code: add startup to matcher |
| CAP-46 | W1 | yes | checked after typed | roll-up of its items | see items |
| CAP-46.a | W1 | yes | checked after typed | - | code: as built |
| CAP-47 | W3 | part | none / judgement / code off path | roll-up of its items | see items |
| CAP-47.a | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-47.b | W1 | part | code off path / none | - | code: gov launch bounded pack |
| CAP-47.c | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-47.d | W1 | part | judgement / code off path | 0.1.6 (N-15) | code: release refuses without auditor record |
| CAP-48 | W3 | no | n/a | Wave 3 by design | — |
| CAP-48.a | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-48.b | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-49 | W2 | yes | checked after typed | roll-up of its items | see items |
| CAP-49.a | W2 | yes | checked after typed | in flight: e2/d5-memaudit-strict (grading rule) | code: as built |
| CAP-49.b | NONE | no | n/a | non-goal | — |
| CAP-49.c | NONE | no | n/a | non-goal | — |
| CAP-50 | W3 | part | none / checked after typed / code off path | roll-up of its items | see items |
| CAP-50.a | W1 | yes | checked after typed | - | code: as built |
| CAP-50.b | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-50.c | W1 | part | code off path / none | 0.1.6 (N-02) | code: trailer notice in queue checks |
| CAP-50.d | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-50.e | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-50.f | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-50.g | W3 | no | n/a | Wave 3 by design | code: when friction asks |
| CAP-51 | W1 | yes | checked after typed / checked after auto / code | roll-up of its items | see items |
| CAP-51.a | W1 | yes | checked after typed / checked after auto | Wave 3 (W-4) | code: decision checker in reference hook |
| CAP-51.b | W1 | yes | code | - | code: as built |
| CAP-52 | W1 | yes | checked after typed / code | roll-up of its items | see items |
| CAP-52.a | W1 | yes | checked after typed | 0.1.6 (N-16) | code: deny-lines assertion in portability |
| CAP-52.b | W1 | yes | code | - | code: as built |
| CAP-53 | W2 | part | judgement / checked after typed / code off path | roll-up of its items | see items |
| CAP-53.a | W1 | part | code off path / checked after typed / judgement | in flight: e2/models-rubric (ticket only) | code: lead start through gov launch |
| CAP-53.b | NONE | no | n/a | non-goal | — |
| CAP-53.c | W1 | part | checked after typed | Wave 3 (W-3) | code: governance share red over limit |
| CAP-54 | W1 | yes | checked after typed | roll-up of its items | see items |
| CAP-54.a | W1 | yes | checked after typed | - | code: as built |
| CAP-54.b | W1 | yes | checked after typed | - | code: as built |
| CAP-55 | W1 | part | none / code | roll-up of its items | see items |
| CAP-55.a | W1 | part | code / none | Wave 3 (W-2) | code: call validate() in gov retrieve |
| CAP-56 | W1 | yes | judgement | roll-up of its items | see items |
| CAP-56.a | W1 | yes | judgement | - | code: memory-use log line per session |
| CAP-57 | W1 | part | none / code | roll-up of its items | see items |
| CAP-57.a | W1 | part | code / none | - | code: as built |
| CAP-58 | W1 | part | code off path | roll-up of its items | see items |
| CAP-58.a | NONE | no | n/a | non-goal | — |
| CAP-58.b | NONE | no | n/a | non-goal | — |
| CAP-58.c | NONE | no | n/a | non-goal | — |
| CAP-58.d | NONE | no | n/a | non-goal | — |
| CAP-58.e | NONE | no | n/a | non-goal | — |
| CAP-58.f | NONE | no | n/a | non-goal | — |
| CAP-58.g | NONE | no | n/a | non-goal | — |
| CAP-58.h | W1 | part | code off path | Wave 3 (W-1); containment notice 0.1.6 (N-04) | code: per-commit trailer notice |
| CAP-59 | W1 | part | none / judgement / code off path | roll-up of its items | see items |
| CAP-59.a | W1 | part | code off path | 0.1.6 (N-04) | code: ESCALATION_AT = 2 |
| CAP-59.b | W1 | part | none | - | code: counter file outside looper's reach |
| CAP-59.c | W1 | part | judgement | - | agent: B13 |
| CAP-60 | NONE | no | n/a | non-goal | — |
| CAP-60.a | NONE | no | n/a | non-goal | — |
| CAP-61 | W1 | yes | checked after typed / code off path | roll-up of its items | see items |
| CAP-61.a | NONE | no | n/a | non-goal | — |
| CAP-61.b | W1 | yes | code off path | 0.1.6 (N-06; not used since 18 Nov) | code: lead start through gov launch |
| CAP-61.c | NONE | no | n/a | non-goal | — |
| CAP-61.d | W1 | yes | code off path | - | code: as built |
| CAP-61.e | W1 | yes | checked after typed | D6 landed 9a4adb350; wording: brief contract-015 | code: as built |
| CAP-61.f | NONE | no | n/a | non-goal | — |
| CAP-62 | NONE | no | n/a | non-goal | — |
| CAP-62.a | NONE | no | n/a | non-goal | — |
| CAP-63 | W2 | part | code off path / judgement | in flight: e2/l2-4-queue; 0.1.5 (N-01, F8 brief fixes-015b) | code: queue refuses dirty tree, stale store |
| CAP-63.a | W2 | part | code off path / judgement / none | in flight: e2/l2-4-queue; 0.1.5 (N-01, F8); 0.1.6 (N-02) | code: refuse dirty tree, stale store, disk |
| CAP-63.b | W2 | yes | code off path / judgement | in flight: e2/l2-4-queue | code: Gov OS lands through gov queue |
| CAP-63.c | W2 | yes | code off path / judgement | in flight: e2/l2-4-queue | code: Gov OS lands through gov queue |
| CAP-63.d | W2 | yes | code off path | - | code: as built |
| CAP-64 | W2 | part | none | in flight: e2/w2-207-runtime (ticket only) | code: cron gov dispatch tick |
| CAP-64.a | W2 | yes | checked after typed | in flight: e2/w2-207-runtime (ticket only) | code: as built |
| CAP-64.b | W2 | yes | code off path / checked after auto | - | code: as built |
| CAP-64.c | W2 | no | none | in flight: e2/w2-207-runtime (ticket only) | code: cron gov dispatch tick |
| CAP-64.d | W2 | yes | checked after auto | - | code: as built |
| CAP-64.e | W2 | part | code / none | in flight: e2/w2-207-runtime (ticket only) | code: schedule crash relaunch |
| CAP-64.f | W2 | yes | code / judgement | - | code: as built |
| CAP-64.g | W2 | no | none | in flight: e2/w2-207-runtime (ticket only) | code: one watcher, retire the others |
| CAP-64.h | W2 | part | code off path / none | in flight: e2/models-rubric (ticket only); leads 0.1.6 (N-06) | code: lead start through gov launch |
| CAP-64.i | W2 | yes | checked after auto | - | code: as built |
| CAP-64.j | W2 | yes | judgement | - | agent: B14 |
| CAP-65 | W2 | part | code off path / checked after typed / judgement | 0.1.6 (N-13, N-25) | code: brief carries bundle text |
| CAP-65.a | W2 | part | code off path | 0.1.6 (N-13) | code: brief carries bundle text |
| CAP-65.b | W2 | part | judgement | 0.1.6 (N-25) | code: check each skill's memory line |
| CAP-65.c | W2 | part | code / checked after typed | 0.1.6 (N-13) | code: log role from CLAUDE_AGENT_TYPE |
| CAP-66 | W2 | yes | checked after typed / code | roll-up of its items | see items |
| CAP-66.a | W2 | yes | checked after typed | in flight: e2/d5-memaudit-strict (grading rule) | code: as built |
| CAP-66.b | W2 | yes | code | - | code: as built |
| CAP-67 | W2 | yes | checked after auto | roll-up of its items | see items |
| CAP-67.a | W2 | yes | checked after auto | 0.1.6 (N-16) | code: doctor line newest bundle < 70 min |
| CAP-68 | W2 | part | checked after typed | roll-up of its items | see items |
| CAP-68.a | W2 | part | checked after typed | 0.1.6 (N-11) | code: basis check in reference hook |
| CAP-68.b | W2 | yes | checked after typed | 0.1.5 (N-19) | code: weekly cron line |
| CAP-69 | W1 | yes | code | roll-up of its items | see items |
| CAP-69.a | W1 | yes | code | 0.1.6 (N-16) | code: doctor line for the setting |

**Counts.** These cover the 251 leaf items (envelope rules, master rules and covers items), each counted by the **weakest** class in its cell. The weakest class is the honest measure for the owner's rule.

| wave | code | code off path | checked after auto | checked after typed | judgement | none | n/a | total |
|---|---|---|---|---|---|---|---|---|
| W1 | 33 | 17 | 1 | 36 | 24 | 15 | 0 | 126 |
| W2 | 6 | 7 | 7 | 11 | 9 | 10 | 0 | 50 |
| W3 | 0 | 0 | 0 | 0 | 0 | 0 | 35 | 35 |
| NONE (non-goals) | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 28 |
| envelope and MR | 0 | 1 | 0 | 3 | 3 | 5 | 0 | 12 |
| **all** | **39** | **25** | **8** | **50** | **36** | **30** | **63** | **251** |

- Of the 188 live items, by weakest class: 21 % code, 13 % code off path, 31 % checked after, 19 % judgement and 16 % none.
- Counted by the stronger class instead, the figures are 56 / 45 / 7 / 45 / 26 / 9.
- The gap between the two counts is mostly the off-path tools (A-1, A-6) and typed checks nobody schedules (A-29).

**Notes to the table**
1. CAP-01.b and CAP-21.a: the check exists but `check/authority.py:44` skips `ACTIVE_UNAPPROVED`, so "checked after typed" is defeated (A-14).
2. CAP-04.c is "built: no" because code does the opposite: `retrieval/retrieve.py:48` `BUNDLE_BUDGET = 6000` (A-11).
3. CAP-43.c and MR-4 have changed since A2. `gov release --patch` (`2b47d3354`) refuses before the cut unless G0 to G4 pass. G0 is the owner's authority file (committed `off`), G1 the patch rule, G2 a suite record on the commit, G3 the update rehearsal, and G4 a clean state. The plain `gov release` still has no acceptance gate, hence "part" (A-13).
4. CAP-25.d and CAP-61.e: D6 (`9a4adb350`) makes a patch-only CLI gap drift with exit 0. The class is unchanged; the wording is in `LEAD-contract-015.md`.
5. CAP-38.d: `close/nightly.py` gained `--optin`, but the cron lines are still commented, so it is "none" in practice (A-29).
6. CAP-25.a and the envelope's tool-installs rule: the new registry lines (`e03dd938b`) read `ok: false` in doctor until 015b F2.
7. In-flight branches by diff:
   - `e2/l2-4-queue` has two queue fixes and the proving evidence, not the move;
   - `e2/models-rubric`, `e2/d1-verdict` and `e2/w2-207-runtime` hold only ticket text on the branch;
   - `e2/d5-memaudit-strict` holds code;
   - `e2/contract-015` is empty.
8. A W3 row's "should be" is "code: when friction asks" (EMERGENCY-2 §8.4); a non-goal's is "—".
9. CAP-17.b ("the store is rebuilt after each land"): the automatic refresh runs, but at 13:53 today it failed with `EMBEDDER_UNAVAILABLE` and nothing retried it. The integration store is 23 commits behind HEAD with no alert (A-10).

### 4.2 The fields carried into the Contract

Add to `contract.yaml`, on every master rule, envelope rule and covers item:

```yaml
enforcement:
  built: yes | part | no
  class: code | code-off-path | checked-after-auto | checked-after-typed | judgement | none
  by: <check id | command | path:line>   # required unless class is judgement or none
  job: B1..B16                            # required when class is judgement
  until: 0.1.6 | wave-3 | non-goal | -    # when built is part or no
```

`CONTRACT_v5.md`'s generator prints them as one line per item. A G1 check refuses an item without the block, a `by:` that resolves to no check id or path, and a `judgement` item without a `job:` (A-23). §4.1's table is the first fill.

### 4.3 The Charter's rule

**Proposed sentence.** Change principle 4's title, and add one bullet after `CHARTER_v6.md:82`:

> 4. **Deterministic where it can be, specified where it cannot.**
>    - …(the three bullets as they stand)…
>    - Whatever can be decided or checked by code is decided or checked by code: at the launch, at the landing, or by a scheduled check, never by an agent's goodwill. Whatever must stay with an agent (writing code, tests and specs; reviewing; auditing; planning; researching) is a job with fixed inputs, an output in a fixed form, and a code check of that form. Every Contract item and every standing rule names which of the two it is and the check or job that holds it; Gov OS is assessed by that field (DEC-1233 (6)).

**Where it sits.** In the Charter, under §3 Principles, principle 4 (lines 79-82); principle 3 (lines 75-78) already says rules compile into code, and this says how far. In the Contract, a seventh envelope rule, `determinism`, carries the same sentence and names A-23's check as its acceptance. CLAUDE.md and AGENTS.md need no new line: the rule binds whoever writes rules (the CTO), and the basis check carries it at the decision commit.

---

## 5. Fixes, in order

Order: lost work and fail-open, then wrong results, then drift, then cost. Kinds:
- **fix** under the named ticket;
- **chore** (configuration or records, tests unchanged);
- **feature** (a new KPI line, so a new ticket by §4.6);
- **kernel** (text the CTO decides, §3.5);
- **owner** (decisions or Charter text).

| # | What | Where | Kind | Size | Place |
|---|---|---|---|---|---|
| 1 | Record DEC-1232 and DEC-1233 before the briefs that cite them are committed | `docs/DECISION_REGISTER.md` | chore (the CTO, DEC-861/463) | XS | now |
| 2 | Run the L2-4 proving landing; Gov OS lands only through `gov queue`; add `queue.yaml`; retire the hand-merge tools (A-1) | `e2/l2-4-queue`; `governance/project/queue.yaml`; scratch tools | fix under W2-115b (DAEO-j9z6) + chore | XS + chore | 0.1.5 (in flight) |
| 3 | Queue refuses a dirty worktree for the branch (A-2). Until #2, the CTO's hand-merge routine runs `git -C <worktree> status --porcelain` | `queue/checks.py`; the CTO's routine | fix under W2-115b (015b F8); interim chore | S | 0.1.5 |
| 4 | No claude.ai connectors anywhere; `start_cto.sh` gets the flag too; correct the 015a brief, which says Gov OS's settings already carry the key (A-4) | `template/governance/kernel/settings.json`, `.claude/settings.json`, `launcher.py`, `start_cto.sh` | fix under W2-201 (DAEO-k1us) and W2-17 (015a F1) | S | 0.1.5 |
| 5 | Pause stops every starter (A-5) | `start_lead.sh`, `run_tick.sh`, `dispatch/`, `pause/command.py` | fix under W1-28 (DAEO-9279) (015a F10) | S | 0.1.5 |
| 6 | Memory measure: Sonnet grading and the strict rule land; `FIGURES.json` stamps release, commit, models, rule and the forbidden count; `declare` refuses strict with no lists (A-9) | `memaudit/judge.py`, `figures.py`, `declare.py` | fix under W2-204 (DAEO-ma4q) and W2-201 R4 | S | 0.1.5, before EXAMIN's fresh 80 |
| 7 | Store refresh retries: the tick runs `gov rebuild --integration --when-due`; re-run it now, since the store is 23 commits behind (A-10) | crontab or the tick | chore now; the status line is a fix under W1-27 (DAEO-xw3k) | XS + S | 0.1.5 / 0.1.6 |
| 8 | Schedules: nightly back, doctor daily, memaudit weekly, basis `--week`, `spend check`; G1/G2 as reference-transaction notices or lefthook (the CTO decides) (A-29, A-8 cron) | crontab, `.git/hooks/reference-transaction` | chore | XS | 0.1.5 |
| 9 | Generated agent files without slots; `orchestrator.md` from `role-cto.md`; `independent-auditor.md` without the probe preamble; `start_cto.sh` appends `role-cto.md` (A-24) | `src/gov/adapters/`, `.rulesync/`, `start_cto.sh` | fix under W1-38 (DAEO-3ef2) (015a F11) + kernel | XS-S | 0.1.5 |
| 10 | SubagentStop forgiving (A-34) | `kernel/hooks/subagentstop.py` | fix under W1-29 (DAEO-zsvl) (015a F12) | S | 0.1.5 |
| 11 | Leads start by `gov launch lead --brief`: template, `GOV_TICKET` (checkpoints), pause, spend, claim, record, rubric; refuse an unfilled slot or an empty memory section (A-6) | `launcher.py`, `start_lead.sh` | fix under W2-21 (DAEO-1ahb) and W2-153 (DAEO-8s85) | M | 0.1.6 |
| 12 | The lead's return checked: 12 fields plus `branch`, `head`, `worktree_clean`; one return form in `role-lead.md` (A-7, B13) | `start_lead.sh` / `launcher.py`; `role-lead.md` | fix under W1-29 + kernel | S | 0.1.6 |
| 13 | Red on the base with a `pins` column (A-3) | `queue/command.py`; `test-design/test-kinds.md` | fix under W2-202 (DAEO-l2bd) + kernel | M | 0.1.6 |
| 14 | Backup age line in doctor (A-8) | `doctor/command.py` | fix under W1-27 | XS | 0.1.6 |
| 15 | The determinism fields in the Contract, with the G1 check and `Enforced-by:` in the basis check; the Charter sentence (A-23, §4.2, §4.3) | `contract.yaml`, its generator, `kernel/checks/`, `decisions/basis.py`; `CHARTER_v6.md` | feature (new ticket) + owner (Charter, Contract wording) | S | 0.1.6 |
| 16 | Bundle uncut; no `BUNDLE_BUDGET` for the brief (A-11) | `brief/memory.py`, `retrieval/retrieve.py` | fix under W2-197 (DAEO-3d3o) | S | 0.1.6 |
| 17 | Acceptance map at commit; mark the closed ticket folders that fail it `legacy: true` (A-12) | `accept/runner.py`, `kernel/checks/` | fix under W2-96 (DAEO-ouet) | S | 0.1.6 |
| 18 | Plain `gov release` needs a passing acceptance record (A-13) | `release/__init__.py` | fix under W2-209 (DAEO-a2h5) | S | 0.1.6 |
| 19 | Owner-approval check alive (A-14) | `check/authority.py:44` | fix under W1-11 (DAEO-be7u) | S | 0.1.6 |
| 20 | Fix section written by the queue; test-first notice (A-15) | `queue/fix.py` | fix under W2-115b | S | 0.1.6 |
| 21 | `gov queue --direct` for chores; `Task: chore` form (A-16, B5) | `queue/`; `LEAD-COMMON.md` | fix under W2-202 (L2-6) + chore | M | 0.1.6 |
| 22 | Reviewer verdict block named in `qa-review` and `audit`; QA findings parsed; a `cause:` line per queue red (A-17, B6) | kernel skills; `close/command.py` or `queue/` | kernel + fix under W2-202 | XS + S | 0.1.6 |
| 23 | Retire `gov close` (B1) or `ESCALATION_AT = 2` (A-18) | `close/state.py:17`, `cli/main.py` | fix under W2-115b / W2-202 | S | 0.1.6 |
| 24 | Spec-to-ticket KPI link in the ready check; `spec-writing` on product-spec's Skills line (A-23b, B1) | `brief/build.py`; `roles/product-spec.md` | fix under W2-197 + kernel | S | 0.1.6 |
| 25 | Decision package ten headings (A-19) | `decision-package.schema.json`; orchestration skill | fix under W1-34 (DAEO-egm9) + kernel | S | 0.1.6 |
| 26 | Kernel lint (retired phrases, memory line) after the kernel sweep (A-25; N-24, N-25) | `kernel/checks/`, `portability.py` | fix under W1-38 + kernel sweep | XS | 0.1.6 |
| 27 | Skill health: one regression declaration over all skills; bump check over `kernel/skills` and `kernel/roles`; copy version check (A-26) | `kernel/checks/`, `check/runner.py:57,305` | fix under W2-104 (DAEO-drhj) or the check runner's ticket (the CTO picks) | S | 0.1.6 |
| 28 | Kit carries `agent_model.py`; `defaultMode` in the kit; root `.rulesync/permissions.jsonc` aligned (A-27) | `template/.rulesync/hooks.jsonc`, kit settings | fix under W1-38 | S | 0.1.6 |
| 29 | Basis at the decision commit as a notice (A-28) | `.git/hooks/reference-transaction` | fix under W2-198 (DAEO-o5wi) | XS | 0.1.6 |
| 30 | Digest and status block by code (A-32) | `status/command.py` | fix under W1-32 (DAEO-8goq) | S | 0.1.6 |
| 31 | Doctor lines: deny lines, path-map matcher, tag, 365 days (A-31) | `doctor/command.py` | fix under W1-27 | XS each | 0.1.6 |
| 32 | `startup` in the SessionStart matcher (A-30) | `.claude/settings.json`, `template/.rulesync/hooks.jsonc` | fix under W1-29 (the CTO decides against §11) | XS | 0.1.6 |
| 33 | Forms List B names as missing: `return.schema.json`, a single research heading list, the wave file, `stream-handoff.schema.json`, one adoption verdict schema, the audit validator over `docs/emergency-2/audits/` | `template/governance/kernel/schemas/`, templates | kernel (product-spec writes, the CTO approves); checks as fixes under their tickets | S each | 0.1.6 (stream hand-off: later) |
| 34 | Helpers' retrieves with role; session cost line (A-35, A-36) | `.claude/hooks/agent_model.py`; `memory_use`; run-time tool | fix under W2-197; chore | S | 0.1.6 |
| 35 | Text contradictions: releases in CLAUDE.md, the kit head and `judging-work`; golden rule at the head; the in-force digest following EMERGENCY-2 supersessions; CLAUDE.md:5's re-baseline clause | CLAUDE.md, AGENTS.md, kit, `decisions/` digest | kernel (the CTO); the digest's supersessions are a fix under W2-198 | S | 0.1.5 (N-26) / 0.1.6 |
| 36 | Auditor session checked against a launch record (A-20); containment per commit (A-33); weekly measures (A-37) | `adopt/`, `queue/checks.py`, `status/` | fixes | S-M | later |

### Summary for the owner

I classed every element of Gov OS as enforced by code before the act, checked by code after it, or left to an agent's judgement. That is the commands, each step of the flow, the roles, skills, templates and hooks, and every standing rule.

Counted over the 188 live Contract items by their weakest part:
- a fifth are enforced on the path sessions actually take;
- an eighth are enforced only inside `gov queue` and `gov launch`, which Gov OS bypasses (it lands by hand merge and starts leads by script);
- a third are checks that exist but run only when typed;
- a fifth are judgement;
- a sixth are not built.

Three ordinary mistakes are caught by nothing today:
- uncommitted work left behind at the land;
- a mis-trailered or all-green acceptance folder merged by hand;
- a memory figure with no release or model stamp.

The fixes for the first and third are already briefed for 0.1.5. List A turns 39 more elements into code, most of them S or XS for 0.1.6, ordered by what they protect. The two biggest moves are landing Gov OS through `gov queue` and starting leads through `gov launch`.

List B specifies the sixteen agent jobs that must stay with agents: what each receives, what it produces and in what form, and which code checks it. Today only four of the sixteen have both a form and a check on the path. Each hand-off may rely only on what code checked.

To make your rule part of the Contract and the Charter, I propose one sentence for Charter principle 4 and an `enforcement:` field on every Contract item, with a check that refuses an item without it. §4.1's 320 rows are its first fill, so Gov OS can be assessed by it from 0.1.6.

Before anything cites them further, DEC-1232 and DEC-1233 need recording: the briefs already cite them, and the register has neither.
