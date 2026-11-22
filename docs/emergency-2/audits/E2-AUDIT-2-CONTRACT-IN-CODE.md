# Audit 2: the Contract in code (DEC-1230)

Date 2026-11-22 · Gov OS `w2/integrate` at `3ab01e94b`; EXAMIN at `44fd59d` (read only) · auditor: fresh, read-only, Opus (DEC-1225 (2)), with three Sonnet helpers for the wide reading (each row below was traced to a file and line; the strongest helper claims were re-checked by hand: `ci.yml:28-30`, `check/authority.py:44`, `close/state.py:17`, `retrieval/retrieve.py:48`, `launch/launcher.py:784-789`, the basis check's absence from `kernel/checks/`, `queue/after.py:41`).
Sources: EMERGENCY-2.md (whole); DEC-1225, DEC-1230; `docs/contract/CONTRACT_v5.md` (whole; `contract.yaml` holds the same items); audit 01 (17 Nov) as the starting point; the code named in each row; the live crontab; `.claude/settings.json`; `.git/hooks/`; the memory-use log; launch records; lead logs.
Memory: `gov retrieve` on 2 questions, each read whole (the store was 9 paths stale and Ollama was down, so FTS only). They returned the Contract's own capability records, audit 01's §1–§3 rows, and the 20 Oct sweep. Audit 01 was the useful find. Everything else came from the code.
Nothing was run but read-only commands. No test suite was run.

## 0. The answer in six lines

1. **Little is enforced at the moment of action, and most of that sits in two tools that today's sessions do not go through.** `gov queue` (the landing) and `gov launch` (the launcher) refuse the right things. But Gov OS lands by a hand `git merge` (e.g. `cc857b977`), and since 18 Nov no session in Gov OS or EXAMIN was started by `gov launch` (0 launch records in each `.gov-runtime/launches/`; 23 in the W2-81 proving runs only).
2. **What does run by itself:** the two deny lines; four Claude Code hooks (the checkpoint hooks, the helper-model rule, the 12-field return check for helpers); the hourly backup; the store refresh after each update of `w2/integrate`; and the minute dispatcher tick (a watcher; it starts no leads today).
3. **Most checks are "typed only".** `gov check`, `gov doctor`, `gov telemetry`, the basis-line check, the fresh-80 measure, the transcript scan and the nightly regression run only when someone types them. Lefthook is not installed, CI runs only when started by hand (`.github/workflows/ci.yml:28-30`), and the nightly cron lines are commented out.
4. **Briefs and templates are asked, not made.** Leads start from hand-written briefs. The only check is "file not empty" (`start_lead.sh:11`). No role template is appended, `gov brief` is not called, and nothing checks for unfilled slots. `gov brief`, which refuses an unready ticket and an unfilled slot, ran once since the log began (1 of 153 memory-use lines). One template *is* filled under code: the helpers' 12-field return (SubagentStop hook).
5. **The generated role files carry unfilled slots.** In both Gov OS and EXAMIN, every in-session helper reads its role file as its system prompt, and those files hold literal `{CMD:retrieve}`, `{ID}`, `{TREE}`: 10 slots for engineer, 46 for orchestrator.
6. **The biggest single fix is already built:** land `e2/l2-4-queue` and move Gov OS's own landing onto `gov queue` (L2-4). That one change turns MR-3, CAP-23.c, 38.c, 39.c and 63.a–c from instruction into code in Gov OS. Next comes putting `gov launch` + `gov brief` on the lead and worker start paths.

## 1. How to read the tables

| Mark | Meaning |
|---|---|
| **E** | Enforced: code refuses or blocks at the moment of action, on a path today's sessions actually take. |
| **E·q** | Enforced, but only inside `gov queue` or `gov launch` (or `gov brief` / `gov adopt`), which today's Gov OS and EXAMIN sessions do not go through (§2). On the path once they do. |
| **C·auto** | Checked after by code that runs by itself (hook, cron, git hook, the queue's after-step). |
| **C·typed** | Checked after by code that runs only when someone types the command. |
| **I** | Instruction only (text in a skill, template, role file, brief, EMERGENCY-2). |
| **N** | Not built. |
| — | Non-goal (wave NONE) or W3 by design. |

"Fix" gives the smallest code that would enforce or check the item (for I and N, and for E·q / C·typed where it matters). The sizes and kinds are in §6.

## 2. What runs by itself today (the ground every row stands on)

| Mechanism | What it does | Where | Runs |
|---|---|---|---|
| Deny lines | refuse `git push`, `sudo` in every permission mode | `.claude/settings.json:75-80`; EXAMIN the same | every call |
| PreToolUse(Agent\|Task) | refuses a fork and any non-Sonnet helper without an exception | `.claude/hooks/agent_model.py:1-20` | every helper spawn (Gov OS, EXAMIN) |
| SubagentStop | blocks a helper's stop until the 12 return fields are present | `template/governance/kernel/hooks/subagentstop.py:40-57` | every helper stop |
| PreCompact, SessionStart(compact\|clear\|resume), Stop | checkpoint write, resume injection, unread-wake block | `kernel/hooks/precompact.py`, `sessionstart.py`, `stop.py`; `.claude/settings.json:29` | those events (not a fresh start) |
| PostToolUse(Bash) | context watch | `kernel/hooks/context_watch.py` | every Bash call |
| `.git/hooks/reference-transaction` | after any update of `w2/integrate`: store refresh, and the scratch `landing_select.sh` on commits outside a ticket that touch settings, the tool registry or the test map | `.git/hooks/reference-transaction:13-16` | every landing (Gov OS only; EXAMIN has no git hooks) |
| cron, every minute | scratch dispatcher tick: stall wake, embedding-server health; no `ready.txt`, so it starts no leads | `governance/project/orchestration/tools/dispatch/run_tick.sh`; `dispatch.log` | always |
| cron, hourly | `gov backup` of Gov OS and EXAMIN | crontab line `7 * * * *` | always |
| **Not running** | lefthook (no `pre-commit` in `.git/hooks`), CI on push (`ci.yml:28-30` manual), nightly (cron lines commented), memaudit cron, `gov dispatch` (product run-time tool) | — | — |
| **How sessions start (18–22 Nov)** | CTO: `start_cto.sh`. Leads: `start_lead.sh <name> <hand brief>` (37 runs). Workers: Agent-tool helpers. **Not** `gov launch`: 0 records in Gov OS and EXAMIN since 18 Nov | `start_lead.sh:17-24`; `.gov-runtime/launches/` | — |
| **How work lands** | Gov OS: the CTO's hand `git merge` (`cc857b977`, `31cecdce6`). `gov queue` used only in the W2-81 proving run; EXAMIN has its `queue.yaml` (`e609ee0`) and no landing yet | `CTO-HANDOVER.md:57-59` | — |

## 3. Master rules and the envelope

| Item | Today | Evidence | Fix (smallest first) |
|---|---|---|---|
| MR-1 Spec first; READY by code | E·q / C·typed | `gov brief` refuses an unready ticket (`brief/build.py:157-186`: empty allowed paths, KPI with no verify, open dependency, missing reads/needs/waits_on). `gov.tasks.queue` holds it out of the READY view (`tasks/queue.py:76-85`). `gov readiness` (typed). `tk ready` does not read readiness. `gov brief` ran once since 18 Nov | the lead start (`start_lead.sh` / `gov launch lead`) refuses unless `gov brief`'s ready check passes |
| MR-2 Closed spec generates tickets with all fields; gap tickets linked | C·typed; notice at the land (q) | `core-claims` (`check/claims.py:15`) under typed `gov check`. `gov queue` names a new ticket that is not a feature, never refuses (`queue/checks.py:111-136`, by DEC-1219 (5)). `gov discover` typed | run `core-claims` on the ticket files a branch adds, as a queue notice |
| MR-3 Builder never writes its acceptance tests | E·q; I in Gov OS | `gov queue` refuses a commit touching `tests/acceptance/` (or the ticket's folder) without `Role: independent-test-designer`/`owner`, merges included (`queue/checks.py:50-71`; `queue/command.py:276-284`). Missing folder refused at the land (`NO_ACCEPTANCE_TESTS`, `checks.py:150-181`). **Not built:** "red on the base". Gov OS hand merges run none of it. The Role trailer is text the committer types | (1) Gov OS lands through `gov queue` (L2-4); (2) the queue runs the acceptance folder on the base and refuses a folder that is all green there |
| MR-4 Audit/discovery/impact distinct; fresh auditor at release and A5/AS/A7/A10; review only on triggers | mixed: E·q / N / I | Each function has its own command (by construction). Fresh auditor at A5, A7, A10: `adopt/stages.py:541-565`, `adopt/lite_gates.py:80-90` (the session id is a typed string). AS: no auditor check (`adopt/spec_audit.py`). Release acceptance: no gate in `gov release` (`release/__init__.py:172-197`). "Review only on triggers": `skills/judging-work/SKILL.md:42` (I) | AS takes a verdict held to `lite_gates._auditor`; `gov release` refuses without an acceptance record |
| MR-5 Roles as generated subagent files | C·typed | `adapters/portability.py:277` compares `.claude/agents` with kernel roles (G1, typed `gov check`; a queue after-notice when roles change). **Gap:** the generated files hold unfilled slots (engineer 10, test designer 9, orchestrator 46; EXAMIN identical) | portability check refuses a `{UPPER}` slot in a generated agent file; the generator fills or drops them |
| MR-6 Owner questions as 8/10-field packages, ≤5, each answer a record | I | `decision-package.schema.json` checks only id, type, status. `skills/orchestration/SKILL.md:45` says "six parts (DEC-818)" against the Contract's ten. Nothing counts open packages | schema requires the ten body headings; reconcile the skill (kernel text, the CTO's) |
| §2 Token budget ≤15 %; AGENTS.md ≤1.5k | C·typed / N | `gov telemetry` (`telemetry/command.py:32`), typed. No 15 % breach finding. AGENTS.md 4,432 bytes with no size check | a `gov status` line red over 0.15; a core check on AGENTS.md size |
| §2 Boundary | E (deny lines), C·auto (backup) | `.claude/settings.json:75-80`; hourly backup. "Sessions apart by brief, nothing enforces it": as written. G3/CI advisory on push: not running (lefthook absent, CI manual) | `lefthook install` |
| §2 Loop budget: two rounds, then one package | E·q, contradicts | `gov launch` refuses a third auditor round (`launcher.py:784-789`, FULL only; `--owner-named` checked for form only). `gov close` escalates at **3** (`close/state.py:17`). `role-lead.md:49` "Three iterations … DEC-096". No package to chat | `ESCALATION_AT = 2`; role-lead text to two |
| §2 Tool installs: CTO approves and records | C·typed / I | Registry schema (`kernel/schemas/tool-registry.schema.json:12-20`: no need, disk or RAM fields); `gov doctor` drift (`doctor/command.py:289-311`), typed. No check that an installed tool has a row | `gov doctor` lists tools on PATH/venv with no row; schema adds need, disk, RAM |

## 4. Capabilities, item by item

W3 items take one line each; non-goals are grouped at the end of their capability.

### Memory and retrieval (CAP-01 to CAP-21)

| Item | W | Today | Evidence | Fix |
|---|---|---|---|---|
| CAP-01.a precedence | W1 | E | `retrieval/authority.py:258`, called `retrieve.py:449,662`; superseded dropped `:630` | — |
| CAP-01.b approvals are owner git facts | W1 | C·typed, defeated | `decisions/checker.py:401-424` flags; **`check/authority.py:44` skips `ACTIVE_UNAPPROVED`**; register entries are not checked | delete the skip; check new ACCEPTED register entries for `Decided-by: owner` |
| CAP-01.c research/lessons cannot become authority | W1 | C·typed | `check/authority.py:56-78` (gov check, gov close) | — |
| CAP-01.d mandatory inputs outrank retrieval | W1 | E | `retrieval/authority.py` | — |
| CAP-02.a lock MATCH/DRIFT | W1 | C·typed | `doctor/command.py:628` → `lock/__init__.py:162-213`; Gov OS has no `framework.lock` | `gov doctor` in the queue's after-step |
| CAP-02.c signed tag | W3 | — | by design | — |
| CAP-03.a secret classes out of every index | W1 | E | `secrets/__init__.py:496-506` | — |
| CAP-03.a one scan before going public | W1 | N | no gitleaks in `release/command.py` | `gov release --public` runs one full scan and records it |
| CAP-03.a no scan while private | W1 | contradicted in the kit | template CI runs gitleaks on every push (`template/.github/workflows/ci.yml.jinja:73`; EXAMIN `ci.yml:28,73`); `secrets_scan_on` defaults on when `secrets.yaml` is absent (`rebuild/command.py:224-228`). Latent: EXAMIN has no remote | gate the CI step on `secrets.yaml`; default off |
| CAP-03.b, .d, .e class filters on every route | W1 | E | `secrets/__init__.py:496`; `retrieval/lexical.py:6`; `rebuild/command.py:475` | — |
| CAP-03.c namespace fields | W1 | E (presence) | `config/loader.py:106-123` | — |
| CAP-04 runaway brake | W2 | E·q at launch / marker C·typed | `launcher.py:1167` `SPEND_BRAKED`; marker written only by typed `gov spend check` (`spend/command.py:70`) | `gov spend check` in the minute tick |
| CAP-04.a, .d budgets, limit package | W3 | — | by design | — |
| CAP-04.b governance share weekly | W1 | C·typed | `gov telemetry` | weekly cron line |
| CAP-04.c no packet ceiling | W1 | contradicted | `retrieval/retrieve.py:48` `BUNDLE_BUDGET = 6000` ("DEC-004's packet ceiling"); named when hit (`:798`) | no ceiling for the brief's retrieval |
| CAP-05.a pause: launch | W1 | E·q | `launcher.py:351-362`, called `:1112,:1141` | — |
| CAP-05.a pause: landing | W1 | E·q | `queue/command.py:162-176`, `:596` | — |
| CAP-05.a pause: dispatcher, lead start, hand merge | W1 | N | scratch dispatcher, `launch_now.sh:46`, `start_lead.sh` read no flag | `run_tick.sh` and `start_lead.sh` exit while the freeze flag exists |
| CAP-05.a stop message to running sessions | W1 | N | `pause/command.py` sends none | `_freeze` writes one `gov msg` stop per live session |
| CAP-05.b cancel, release claims | W1 | E (narrow) | `pause/command.py:128`; stops no process | — |
| CAP-05.c rollback recorded | W1 | E | `pause/command.py:139,173` | — |
| CAP-05.d owner-gated | W1 | E | `pause/command.py:212-231,286` | — |
| CAP-06.a no unclassified path | W1 | C·typed, blind | `check/pathmap.py:43`; `gov doctor` uses fnmatch, so `path-map.yaml:9` `["*"]` hides every path (`doctor/command.py:547`) | reuse `check/pathmap._matches` in doctor |
| CAP-06.b, .c, .d target actions; unknown blocks migration | W1 | E·q (gov adopt) | `adopt/stages.py:28,252-253`; `adopt/refactor_plan.py:301` | — |
| CAP-06.e overlay floor | W1 | E | `update/core.py:138` | — |
| CAP-07.a, .b authoritative vs derived | W1 | E / C·typed | `.gitignore:18`; `common.schema.json:54` | — |
| CAP-08.a exact queries | W1 | E (library) | `records/queries.py:42-46` | — |
| CAP-09.a, .b edges; dangling ids | W1 | E / C·typed | `store/loader.py:49`; `check/graph.py:57` | — |
| CAP-10 fresh 80 at 95 % end to end | W1 | C·typed | `memaudit/fresh.py`, `memaudit/declare.py:36`; `memaudit_cron.sh` not in crontab | install the weekly line |
| CAP-10.a, .b pinned, replaceable embedder | W1/W2 | E | `retrieval/semantic.py:179,555,729` | — |
| CAP-11.a exact strings | W1 | E | `retrieval/lexical.py:23` | — |
| CAP-12.a, .b code graph; secrets out | W1 | E | `retrieval/code_route.py`; `rebuild/command.py:475` | — |
| CAP-13.a trailers resolved | W1 | E / C·typed | `store/loader.py:26,68-69` | — |
| CAP-13.b checkpoints and close records | W1 | E | `kernel/hooks/stop.py:72`; close record by the queue | — |
| CAP-14.a failures surfaced first | W1 | E (when linked) | `retrieve.py:60,575`; nothing writes failure records | a failure-record writer at a red landing |
| CAP-15 the brief | W2 | see §5 | — | — |
| CAP-16.a batches, continuation | W1 | E | `retrieve.py:274,334` | — |
| CAP-16.b facets → merge → follow-up | W1 | I | retrieval skill; `retrieval/validate.py` has no caller in `src/` | call `validate()` at the end of `gov retrieve` |
| CAP-16.c radius-scaled rounds | W1 | E | `closure/__init__.py:22` | — |
| CAP-17.a stale never returned as current | W1 | E | `retrieve/command.py:32-34`; `lexical.py:15` | — |
| CAP-17.b store rebuilt after each land | W2 | C·auto | `.git/hooks/reference-transaction:13-15`; `queue/after.py:41-59` | — |
| CAP-17.c canaries after reindex | W1 | C·typed | `retrieval/canary.py` via `gov doctor`; not at the end of `gov rebuild` | run canaries at the end of `gov rebuild` |
| CAP-18.a, .b fusion, hierarchy | W1 | E | `retrieval/fusion.py:31`; `retrieve.py:64-65` | — |
| CAP-19.a fail-closed model pin | W2 | E | `retrieval/semantic.py:541-572,179` | — |
| CAP-19.b bake-off | W3 | — | by design | — |
| CAP-19.c a miss → root cause → fix | W2 | N (library unused) | `retrieval/learning.py` has no caller | `gov memaudit` records each miss through it |
| CAP-20.a rebuild digest; fresh agent resumes | W1 | C·typed | `recovery-rebuild`, `fresh-agent-reconstruction` checks (G1) | — |
| CAP-21.a owner approval facts; kernel text needs the CTO | W1 | C·typed, defeated / I | as CAP-01.b; "kernel text needs the CTO" has no code | as CAP-01.b; for kernel text see CAP-24.c |
| non-goals | — | — | CAP-02.b, CAP-15.d, CAP-15.g, CAP-21.b: nothing built | — |

### Roles, flow, tests (CAP-22 to CAP-42)

| Item | W | Today | Evidence | Fix |
|---|---|---|---|---|
| CAP-22.a roles as subagent files | W1 | C·typed | `adapters/portability.py:277`; unfilled slots (MR-5) | as MR-5 |
| CAP-22.b return reaches the lead's inbox | W2 | C·auto (partly) | `launcher.py:878` `_end_message` sends "ended, exit N" only for `gov launch` sessions; `start_lead.sh:22-23` sends a wake naming the return file | `_end_message` names the worker's last-message file |
| CAP-22.c test-execution and integration roles | W3 | — | none | — |
| CAP-22.d research role, paths judged as a notice | W1 | I + E·q notice | `kernel/roles/research.md`; `queue/checks.py:80` | — |
| CAP-23.a claim lock names the holder | W1 | N in practice | `tasks/claims.py:42` `claim()` has no caller outside tests; `tasks/queue.py:27,76` read a lock nobody writes. One writer per worktree: `launcher.py:1151` (E·q) | `gov launch` calls `claims.claim` |
| CAP-23.b slots from the machine | W2 | E (scratch tool, constants) | `dispatcher.py:2612-2625` with fixed `config.json`; product `dispatch/limits.py` unscheduled | run cron on `gov dispatch tick` (run-time tool) |
| CAP-23.c parallel tickets; landing merges, selects, checks paths and authorship | W2 | E·q; I in Gov OS | `queue/command.py:259-284`, step 3 `select.scoped` | Gov OS lands through `gov queue` |
| CAP-24.a skill versions recorded | W1 | C·auto (queue) / partly blind | close record lists skill versions (`close/command.py:277`); bump check reads only `kernel/vendor` (`check/runner.py:57,305`) | point the bump check at `kernel/skills` and `kernel/roles` |
| CAP-24.b skills hold no permissions | W1 | C·typed | `check/skill_validator.py:15-16,58` | — |
| CAP-24.c kernel text by the CTO; landing checks kernel bytes | W1 | I; landing check N | `EMERGENCY-2.md:104`. No kernel-bytes check exists (the scratch `kernel_gate.py` retired with `land.py`). EMERGENCY-2 §2.10 retires "approved lists", against the Contract's wording | a queue notice when a ticket branch changes kernel-text paths without an `Approved-by: cto` trailer; decide the Contract's wording |
| CAP-25.a registry pins; doctor drift | W1 | C·typed | `doctor/command.py:289-311,707` | `gov doctor` in a daily cron line |
| CAP-25.b CTO approves every install | W1 | I (+ sudo deny E) | registry header; `launcher.py:461` | as §2 Tool installs |
| CAP-25.d Claude Code pin | W1 | C·typed | `doctor/command.py:26` | — |
| CAP-27.a read commands never mutate | W1 | C (tests only) | `cli/main.py:140-144` declares; W1-07, W1-32 acceptance tests | — |
| CAP-28.a status from `gov status` | W1 | I | `skills/orchestration/SKILL.md:98` | — |
| CAP-28.b operations as gov commands | W1 | E | `cli/main.py:93` | — |
| CAP-29.a, .b lineage | W3 | — | not built | — |
| CAP-30.a 26 rows, no silent N/A | W1 | C·typed | `readiness/checker.py`; `check/runner.py:475` | — |
| CAP-30.b gaps generate linked tickets | W1 | E·q (view) | `tasks/queue.py:76-85`; `brief/build.py:157` | the lead start refuses a ticket the READY rule holds |
| CAP-30.c generation in `gov discover` | W2 | C·typed | `discover/command.py` | — |
| CAP-30.d data provenance; CAP-30.g UX row | W3 | — | not built | — |
| CAP-30.e taxonomy | W1 | C·typed | schema check | — |
| CAP-30.f order: tests before implementation | W1 | I | spec-writing, test-design skills; only `NO_ACCEPTANCE_TESTS` is code | queue notice when the first `src/` commit precedes the acceptance commit |
| CAP-31.a task contract fields | W1 | C·typed + queue notice | `core-schema`; `queue/checks.py:122` | — |
| CAP-31.b a fix is no ticket; failing test first | W1 | E·q (fix landing) / N (test first) | `queue/checks.py:140`, `queue/fix.py`; no test-first check anywhere | in a fix landing, a test-adding commit must come before the source change (notice) |
| CAP-31.c dependency order | W1 | E (view) | `tasks/queue.py:77` | — |
| CAP-31.d not READY with an input absent | W1 | E·q | `brief/build.py:170-174`; `tasks/queue.py:76-85` | as MR-1 |
| CAP-32.a, .b research lifecycle | W3 | — | `check/authority.py:13,60` partial | — |
| CAP-32.c experiments in their own folder, with a record | W1 | I | discovery skill; research role | — |
| CAP-32.d `gov discover` | W2 | C·typed | `discover/command.py` | — |
| CAP-33.a CIT-P / CIT-E records | W1 | I | change skill | — |
| CAP-33.b computed impact | W2 | C·typed | `impact/command.py` | — |
| CAP-33.c staleness propagation | W3 | — | not built | — |
| CAP-33.d Charter/Contract change by CIT-P and owner approval | W1 | I | change skill; nothing refuses an edit of `docs/contract/**` | queue notice on `docs/contract/**`, `docs/charter/**` without `Approved: DEC-n` |
| CAP-33.e, .f, .g CIT-P on contradiction; plain-language impact | W1/W2 | I | change skill lines 36-52 | — |
| CAP-34.a, .c contradiction routing; ranked, ≤5 | W1 | I | `skills/orchestration/SKILL.md:41-45` | — |
| CAP-34.b ten-field package | W1 | I | as MR-6 | as MR-6 |
| CAP-34.d dead gates cannot authorise | W1 | C·typed | `decisions/checker.py:61,447` (close, gov check) | — |
| CAP-34.e non-global blocking | W1 | E (view) | `tasks/queue.py:61,84` | — |
| CAP-35.a, .b, .c model and effort from the rubric; another refused | W2 | E·q (gov launch); E (helpers); N (leads, CTO) | `launcher.py:677-798`; `agent_model.py:149-200` (helpers, Sonnet; effort not judged); `start_lead.sh:19`, `launch_now.sh:46` hard-code Sonnet/high, not read from the rubric. Lead `models-rubric` (DEC-1225) not landed | lead start through `gov launch lead` |
| CAP-36.a per-model telemetry | W3 | — | not built | — |
| CAP-37.a structured checkpoint | W1 | E | `checkpoint/record.py` | — |
| CAP-37.b triggers: transition, compaction, stop | W1 | E (compaction, stop) / I (start) | `precompact.py`, `stop.py`; close writes the transition (`close/command.py:1436`) | `gov launch` writes the start checkpoint |
| CAP-37.c one state file, one wake rule | W1 | partly | `stop.py` blocks on an unread wake; stale-session marking (`dispatch/runtime.py`) unscheduled | run-time tool (audit 3) |
| CAP-37.d worker return contract | W1 | E (helpers) / N (leads, launched workers) | `subagentstop.py:40-57`; a lead's or `claude -p` worker's return passes the Stop hook unchecked; `dispatch/returns.py` reads 3 fields | same field check on a lead's JSON return in `start_lead.sh` (a missing list in the wake) |
| CAP-37.e model switch | W3 | — | not built | — |
| CAP-37.f, .g resume after crash; auto-resume hooks | W1 | E | `sessionstart.py:160`; on compact, clear, resume only | add `startup` where a checkpoint exists |
| CAP-38.a product test families | W1 | I | the ticket's acceptance tests | — |
| CAP-38.b governance families RED/YELLOW/GREEN | W1 | C·typed | `check/runner.py:26-43` | — |
| CAP-38 `gov accept` per KPI line | W1 | E·q at the land; typed otherwise | `accept/runner.py`; the queue runs each folder through it (`queue/acceptance.py`, `command.py:618-633`) | — |
| CAP-38.c independent authorship | W1 | E·q; I in Gov OS | as MR-3 | as MR-3 |
| CAP-38.d suite currency (nightly) | W1 | N in practice | `close/nightly.py`; cron lines commented | restore the nightly line |
| CAP-38.e missed case to the next test batch as behaviour | W1 | I | test-design, orchestration skills | — |
| CAP-39.a tiers G1–G5 | W1 | C·typed | `lefthook.yml` not installed; `ci.yml:28-30` manual | `lefthook install` (G1, G2) |
| CAP-39.b proving run | W2 | C·typed | W2-81 | — |
| CAP-39.c impact-selected tests at the land | W2 | E·q; I in Gov OS | queue step 3 | Gov OS lands through `gov queue` |
| CAP-39 acceptance: a stale index fails the land | W2 | N | `queue/after.py:2,41` refreshes as a notice; no `STORE_STALE` in `src/gov/queue/` (only `close/batch.py:818`) | queue calls `batch.refresh` in its clone before the run and refuses on `STORE_STALE` |
| CAP-39.d result provenance | W1 | E | `check/runner.py:58,68` | — |
| CAP-39.e scheduler | W3 | — | not built | — |
| CAP-40.a per-ticket telemetry record | W1 | partly C·typed | `launch/session_record.py:45-62` (gov launch only); `telemetry/counter.py:38` lists fields with no source; leads leave no record | leads launched by `gov launch` get session records |
| CAP-40.b organisational questions | W3 | — | not built | — |
| CAP-40.c the weekly measures | W1 | N (partial) | `gov spend sum`, `gov memory-use` exist; owner messages per day, product share and landing time have no code | `gov status --weekly` from launch and queue records |
| CAP-41.a, .d lifecycle; carried lessons | W1 | I | change skill; `docs/lessons/` | — |
| CAP-41.b, .c, .f decision vs lesson; scope and severity | W1 | C·typed | `check/authority.py:13,60`; `lesson.schema.json` | — |
| CAP-41.g, .h, .i, .j lesson packets and inbox | W3 | — | not built | — |
| CAP-42.a, .b, .c legacy retirement, archive | W1 | E·q (gov adopt A8) | `adopt/legacy.py` | — |
| non-goals | — | — | CAP-25.c, .e, .f, .g; 27.b; 38.f; 40.d; 41.e: nothing built | — |

### Release, adoption, landing, run-time (CAP-43 to CAP-69)

| Item | W | Today | Evidence | Fix |
|---|---|---|---|---|
| CAP-43.a canonical repo; lock at install | W1 | E at install / C·typed | `release/command.py:92-108`; `doctor/command.py:628` | — |
| CAP-43.b release manifest and hashes | W2 | E (owner-only build) | `release/__init__.py:172-197`; `release/command.py:55-97`; `update/core.py` re-verifies. A released tag is not protected from `git tag -f` | a tag-immutability line in `gov doctor` |
| CAP-43.c release certified by the acceptance | W2 | I | no gate in `release/__init__.py:172-197` | `gov release` refuses without `docs/releases/<v>/acceptance.json` all-pass |
| CAP-43.d fuller release contents | W3 | — | not built | — |
| CAP-44.a gov init | W1 | E | `copier.yml:14-15` | — |
| CAP-44.b, .d, .e A0–A4, A6, A8 | W1 | E·q (gov adopt) | `adopt/stages.py:61-80,682,717`; `adopt/project.py:99-107`; `adopt/safety.py:230-291` | — |
| CAP-44.c A5 fresh auditor | W1 | E·q (self-declared session) | `adopt/stages.py:541-589` | compare the session id with a launch record of the auditor role |
| CAP-44.f A7, A10 fresh auditor; AS | W2 | E·q (A7, A10) / N (AS) | `adopt/lite_gates.py:80-90`; `adopt/spec_audit.py` has none | AS takes a verdict held to `_auditor()` |
| CAP-44.h lite verdict | W2 | C·typed (shape only) | `adoption-verdict.schema.json`; nothing checks the verdict against its conditions | a VERDICT stage that refuses a "not met" condition with no accepted decision |
| CAP-44.j native layout kept | W1 | E·q (partly) | `adopt/stages.py:33` | — |
| CAP-44.m AS before A3 | W2 | E·q | `adopt/spec_audit.py:271-323`, called first in `a3` (`stages.py:475`) | — |
| CAP-44.g, .i, .k, .l remediation; recovery; A9/A11; full verdict | W3 | — | A9 built (`stages.py:718`), A11 not | — |
| CAP-45.a gov update | W2 | E | `update/core.py:1-60,527-595,699` | — |
| CAP-45.b pending update at session start | W2 | C (not at a fresh start) | `sessionstart.py:20-27`; matcher `compact\|clear\|resume` (`.claude/settings.json:29`); `doctor/command.py:872,913` | add `startup` to the matcher |
| CAP-46.a clone + doctor + rebuild | W1 | C·typed | `rebuild/command.py:295-330` | — |
| CAP-47.b fresh session, bounded pack | W1 | E·q (fresh session) / N (bounded) | `launcher.py:423-450` | — |
| CAP-47.d audit triggers | W1 | I (E·q at A5, A7, A10) | `judging-work/SKILL.md:42` | — |
| CAP-47.a, .c adoption roles, evidence tree | W3 | — | partly (records under `governance/adoption/`) | — |
| CAP-48.a, .b health SLOs | W3 | — | no `gov health` | — |
| CAP-49.a oracle, scorecard, scan | W2 | C·typed | W2-81; `gov memaudit scan` | — |
| CAP-50.a stable identity | W1 | C·typed | `check/claims.py:15` | — |
| CAP-50.c consumption receipt (trailers) | W1 | E·q (gov close) / N (queue) | `close/command.py:504-523`; `gov queue` checks no trailers | trailer notice in `queue/checks.py` |
| CAP-50.b, .d, .e, .f, .g contracts, staleness, orphans, metrics, scheduler | W3 | — | not built | — |
| CAP-51.a supersession checker | W1 | C·typed (+ queue after-notice) | `decisions/checker.py:137-178` via `check/authority.py:40`; the 1,200-entry register is not in the checker's form | run the decision checker from the reference-transaction hook as a notice |
| CAP-51.b superseded filtered in retrieval | W1 | E | `retrieval/authority.py` | — |
| CAP-52.a one source; CI fails on drift; deny lines present | W1 | C·typed | `adapters/portability.py:1-40` (G1); CI manual; no check that the two deny lines exist | add a deny-lines assertion to portability |
| CAP-52.b Claude Code first | W1 | E | built | — |
| CAP-53.a feature/fix/chore; profile; rubric | W1 | E·q (model/effort) / C·typed (profile) / I (chore in the digest) | `launcher.py:677-798`; `ticket.schema.json:68` | — |
| CAP-53.c governance budget per profile | W1 | C·typed (measured, no limit) | `telemetry/counter.py` | — |
| CAP-54.a, .b day one | W1 | C·typed | `doctor/command.py` `_check_adoption_level` | — |
| CAP-55.a stopping reasons; validator rejects | W1 | E (producer) / N (validator unused) | `retrieve.py:795-814`; `retrieval/canary.py:29-54`; `retrieval/validate.py:15-21` has no caller | call `validate()` in `gov retrieve` |
| CAP-56.a retrieval in a disposable subagent | W1 | I | `skills/retrieval/SKILL.md:17` | — |
| CAP-57.a deterministic closure; synthesis citations | W1 | E / N | `closure/__init__.py:17,90`; `retrieval/synthesis.py:67` uncalled | — |
| CAP-58.h containment by commit trailers, a notice; authorship refused | W1 | E·q, differs | queue judges paths against the ticket's `allowed_paths`, not each commit's own `Role`/`Task` (`queue/checks.py:80-93`); `gov close` still *refuses* on containment (`containment/commits.py:488`; `close/command.py:559-575`) | per-commit trailers in `path_notices`; `gov close` containment as a notice |
| CAP-59.a two rounds, then one package | W1 | E·q (narrow), contradicts | as §2 Loop budget | as §2 Loop budget |
| CAP-59.b count never shown to the looper | W1 | partly | the counter file `.gov-runtime/iterations/<ticket>.json` is readable | — |
| CAP-59.c anti-snowball | W1 | I | none | — |
| CAP-61.b gov launch with role file, template, rubric | W1 | E·q (not used since 18 Nov) | `launcher.py:395-404` refuses a missing template; `:677-798` | lead and worker starts go through it |
| CAP-61.d per-session temp folder | W1 | E·q | `launcher.py:1223-1224` | — |
| CAP-61.e Claude Code version | W1 | C·typed | `doctor/command.py:26` | — |
| CAP-63 the landing | W2 | see §5.4 | — | — |
| CAP-64.a RT-1 no ready ticket waits >10 min | W2 | C·typed | `gov dispatch waits` | (audit 3) |
| CAP-64.b RT-2 message within 2 min | W2 | E·q / C·auto (leads) | `launcher.py:872-889`; `start_lead.sh:22-23` sends a wake at the end | — |
| CAP-64.c RT-3 slots from the machine | W2 | N in what runs | scratch `config.json` constants; product `dispatch/limits.py` unscheduled | cron `gov dispatch tick` |
| CAP-64.d RT-4 no GPU spill | W2 | C·auto | scratch dispatcher GPU alert | — |
| CAP-64.e RT-5 resume at the next step | W2 | E (hooks) / N (crash relaunch unscheduled) | `sessionstart.py`; `dispatch/relaunch.py` | — |
| CAP-64.f RT-6 inbox files, no owner relay | W2 | E (by construction) / I | `gov msg`, `~/.gov-os/inbox/<addr>/` | — |
| CAP-64.g RT-7 one watcher | W2 | N | cron tick + `cto_watch.sh` + unscheduled `gov dispatch watch` | pick one (audit 3) |
| CAP-64.h RT-8 launcher states the rubric | W2 | E·q / N for leads | `launcher.py:855-861`; `start_lead.sh:19` hard-coded | as CAP-35 |
| CAP-64.i stall detected without a model | W2 | C·auto | `dispatcher.py:1364-1435` (the push calls Haiku) | — |
| CAP-64.j push the owner when the CTO needs him | W2 | I | orchestration skill | — |
| CAP-65 memory by construction | W2 | see §5 | — | — |
| CAP-66.a transcript scan voids a measure | W2 | C·typed | `memaudit/command.py:1-8`; run as the last step of `fresh` (`memaudit/fresh.py:18`) | — |
| CAP-66.b reader has only the memory tool | W2 | E | `memaudit/claude.py:3,31` (`--tools ""`) | — |
| CAP-67.a hourly bundle, < 1 h old | W2 | C·auto (no freshness check) | cron `7 * * * *`; 41 h gap 20–22 Nov (machine down) | a `gov doctor` line, newest bundle < 70 min |
| CAP-68.a basis line checked at the commit | W2 | C·typed only | `decisions/basis.py`, `gov decisions basis` (`decisions/command.py:43-50`); in no `kernel/checks/*.yaml`, hook or queue family | a G1 check over `HEAD^..HEAD`, run from the reference-transaction hook as a notice |
| CAP-68.b weekly basis review | W2 | C·typed | `gov decisions basis --week` | weekly cron line |
| CAP-69.a transcripts 365 days | W1 | E (setting) | `~/.claude/settings.json:36` | a `gov doctor` line |
| dropped (CAP-26, 49.b-c, 58.a-g, 60, 61.a/c/f, 62) | NONE | — | no guard, sandbox, break-glass or plugin code; `src/gov/guard/` and `src/gov/context/` hold only `__pycache__`; guard-era `containment/scope.py decide()` still used by `gov close` | — |

**Count (W1 and W2 rows of §3–§4, about 170):** E about 45, mostly retrieval and adoption internals. E·q about 30, refusing in tools today's sessions do not go through. C·auto about 10. C·typed about 45. I about 30. N about 15.

## 5. Briefs and templates: made, or only asked?

### 5.1 The four ways a session starts today, and what each makes it read or fill

| Path | Used 18–22 Nov | Made to read (by code) | Made to fill (by code) | Only asked |
|---|---|---|---|---|
| **CTO**: `start_cto.sh` (tmux, Opus) | every morning | CLAUDE.md (the harness loads it); the checkpoint, on compact/clear/resume only (`sessionstart.py`) | nothing | read EMERGENCY-2 first (CLAUDE.md); memory first; open every subagent prompt with the memory block (`role-cto.md:19`) |
| **Lead**: `start_lead.sh <name> <hand brief>` | 37 runs; 32 hand briefs `docs/emergency-2/briefs/LEAD-*.md` | the brief file, as the prompt (`start_lead.sh:20`, `< "$2"`); only check: not empty (`:11`) | nothing: its return goes to a JSON log, unchecked; the Stop hook does not judge it | read LEAD-COMMON; memory first; flow; trailers; return form (`LEAD-COMMON.md`). **No role template is appended** (no `--append-system-prompt-file`), unlike `gov launch` and the old `launch_now.sh` |
| **Worker** (in a lead or the CTO): Agent tool, `subagent_type: engineer` etc. | all workers | the role file `.claude/agents/<role>.md` as system prompt (by the harness, but only when the lead names a `subagent_type`; nothing requires it). **These files carry unfilled slots**: engineer 10 (`{CMD:retrieve}`, `{ID}`, `{TREE}`, `{CMD:accept}` …), test designer 9, orchestrator 46; EXAMIN the same | **the 12-field return**: the SubagentStop hook blocks the stop until each field is labelled (`subagentstop.py:40-57`) | everything in the lead's hand-written prompt; the role template (`role-engineer.md` etc.) is never delivered on this path |
| **`gov launch <role> <ticket>`** | 0 in Gov OS and EXAMIN since 18 Nov (23 in the W2-81 proving runs) | role file + skills + the role template, appended (`launcher.py:28-34,395-404`: refused if the template is missing); its sha256 in the launch record | nothing at the end (`dispatch/returns.py` reads 3 fields) | — |
| **`gov brief <role> <ticket>`** | 1 run (memory-use log: 1 `brief` line of 153) | — | fills the T-0 envelope and role template from the ticket and `facts.yaml`; **refuses** an unready ticket (`build.py:157-186`) and any unfilled `{UPPER}` slot (`build.py:382`); logs its retrieval | its output is not required by any start path |

### 5.2 Templates under `template/governance/kernel/templates/`

| Template | Who fills it | Checked by code? |
|---|---|---|
| `brief.md` (T-0) and `role-*.md` (7) | `gov brief` (off the path); hand otherwise | by `gov brief` only (slots, ready check); W2-197 acceptance tests check the text (memory line, no sandbox split), run when selected |
| return section (12 fields, `template:`, `commits:`, `brief_gaps:`) | the worker | 12 fields: **E** for helpers (SubagentStop). `template:`, `commits:`, `brief_gaps:` lines: nothing reads them (`role-cto.md:29` asks the CTO to route `brief_gaps`) |
| `ticket.md` | lead or CTO | `gov brief` ready check (off path); `gov queue` `NEW_TICKET_NOT_FEATURE` notice (`queue/checks.py:111-136`); `core-schema`, `core-claims` typed |
| close record | `gov queue` writes it itself (`queue/command.py:381-413`) | made by code, when the queue lands; in Gov OS the CTO writes records by hand (e.g. "W2-204's record", `49e7fa070`) |
| `checkpoint.md` | hooks and `gov checkpoint` | made by code |
| `decision-record.md` / register entry | the CTO | basis line: `gov decisions basis`, typed only; owner fact: skipped (`check/authority.py:44`) |
| `decision-package.md` (ten headings) | the CTO | schema checks id, type, status only; the skill says six parts |
| `lesson.md`, `research.md`, `failure.md` | worker / research | required fields by schema, `gov check` typed |
| `skill.md` | product-spec | `skilleval` typed; frontmatter keys by `check/skill_validator.py` |
| `brief-engineer.md` … `brief-test-designer.md` | — | one-line "replaced by" stubs |

### 5.3 Is reading checked anywhere?

No. No hook, landing step or `gov accept` run checks that a session read its brief, its memory block or its role template. The only trace is the memory-use log (C·typed, `gov memory-use`). Since 18 Nov it has 152 retrieves (95 with role orchestrator, i.e. leads and the CTO; 57 with no role, i.e. helpers, whose `GOV_ROLE` is unset) and 1 brief. A helper's retrieve is logged without a role, so "did the engineer ask memory?" cannot be answered from the log.

### 5.4 The landing as the check of last resort (CAP-63)

| CAP-63 part | `gov queue` | Gov OS today (hand merge) |
|---|---|---|
| .a merge, impact-selected tests on the merged result | E (`queue/command.py` steps 3–4, `select.scoped`, `batch.isolate`) | the CTO's own runs (e.g. "18,245 passed on 49e7fa070", `ca11a92a7`) |
| .a acceptance folder through `gov accept` | E (`queue/acceptance.py`; refused with no folder, `checks.py:150-181`) | asked (LEAD-COMMON step 4) |
| .a test authorship | E (`checks.py:50-71`) | not run |
| .a containment, as a notice | E notice, per ticket not per commit (`checks.py:80-93`) | not run |
| .a trailers | **N** (only `gov close` checks them, `close/command.py:504-523`) | `landing_select.sh` reads `Role`/`Task` only to find commits outside a ticket |
| .a committed tree | **N** (the queue merges the branch tip; uncommitted work in a lead's worktree is silently left behind) | asked (`role-lead.md:59`) |
| .a store freshness | **N** as a refusal (`queue/after.py` refreshes after, a notice) | C·auto (reference-transaction refresh) |
| .a disk | **N** | — |
| .b close record and close at the land | E (`command.py:381-413`) | by hand |
| .c red fixed by its cause; fix with no new ticket; known base red named | E (`checks.py:140`, `queue/fix.py`; `command.py:28-31,718-720`) | asked |
| .d exists in an adopted repository | built (product); EXAMIN's `queue.yaml` committed (`e609ee0`), no landing yet | — |
| "in minutes" on one EXAMIN feature | not measured yet | — |

### 5.5 Text the templates still carry that EMERGENCY-2 retired

- `brief.md:38` "No merge inside the sandbox".
- `brief.md:40` "Forms that work (the guard and the harness accept these)".
- `brief.md:62` `guard_refusals:` return line.
- `role-lead.md:13-14,21` `w2/{W2}` branch form.
- `role-lead.md:49` "Three iterations … DEC-096" (two rounds by DEC-1204).
- `role-lead.md:51-52` a FULL review run (no review of green, §3.6).
- 6 of 19 kernel skills carry no memory-first line: adopt, change, judging-work, orchestration, planning, test-design (grep for `gov retrieve` or "memory first" in each `SKILL.md`), against CAP-65.b.

### 5.6 What code would make the briefs and templates "made, not asked" (smallest first)

1. **`start_lead.sh` → `gov launch lead <ticket> --brief <file>`.** This one change brings pause, the rubric's model, the appended role template, a launch record and a session record to every lead. It is ~20 lines in the script plus a `--brief` flag in `launcher.py`.
2. **`gov launch` refuses a brief with an unfilled `{UPPER}` slot or an empty memory section** (reuse `brief.build.PLACEHOLDER`). A hand-written part is still allowed. ~20 LOC.
3. **Fill or strip the slots in the generated `.claude/agents/*.md`**, and have the portability check refuse a slot. This fixes the helpers' system prompt in both repositories. ~30 LOC.
4. **The lead's return checked like a helper's:** at the end, `start_lead.sh` runs the SubagentStop field check on `result` in the JSON and puts the missing list into the wake. ~10 LOC.
5. **The SubagentStop hook made forgiving:** accept a value on the next line, and exit 0 when `stop_hook_active` is set. It blocked a helper of this audit twice (helper 2's report), which costs tokens for every helper in Gov OS and EXAMIN. ~10 LOC.
6. **Helpers' retrieves logged with their role:** the Agent hook writes `GOV_ROLE`/ticket into the spawn, or `gov retrieve` reads `CLAUDE_AGENT_TYPE` if the harness gives it. Then "memory first" becomes countable per role. ~15 LOC.
7. **Memory block uncut** (CAP-15, CAP-65.a): `brief/memory.py:113-126` writes an index line per item, not the bundle. Either carry the bundle's text, or re-word the Contract to "the index and the command for the whole bundle". The CTO decides; ~10 LOC either way.

## 6. Fixes, in order

Ordered by the golden rule: first what fails open or loses work in ordinary work, then what turns written rules into code cheaply, then contradictions, then the rest. Sizes are my estimates.

| # | What | Where | Kind | Size |
|---|---|---|---|---|
| 1 | Land `e2/l2-4-queue` through `gov queue` as the proving landing; from then on Gov OS lands only through `gov queue`; retire the scratch landing tools | `e2/l2-4-queue`; `.gov-runtime/scratch/orchestrator/tools/` | fix under W2-115b (in flight, L2-4); the retirement is a chore | done on the branch; chore ~0 LOC |
| 2 | Leads start through `gov launch` (pause, rubric, role template, records), and `gov launch` refuses a brief with an unfilled slot | `start_lead.sh`, `launch_now.sh`, `src/gov/launch/launcher.py` | fix under W2-153 (template at launch) and W2-136 (lead launch) | ~40 LOC + tests |
| 3 | `gov queue` adds the missing CAP-63.a checks. Refusals: a dirty worktree for the branch (work would be left behind), `STORE_STALE` in the clone, a disk floor. Notice: missing `Task`/`Role` trailers | `src/gov/queue/checks.py`, `command.py` | fix under W2-115b | ~100 LOC + tests |
| 4 | Generated `.claude/agents/*.md` without unfilled slots; portability refuses a slot | `src/gov/adapters/`, `.rulesync/`; Gov OS and EXAMIN copies | fix under W1-38 | ~30 LOC |
| 5 | SubagentStop hook: next-line values and a `stop_hook_active` exit; the same field check on a lead's return in `start_lead.sh` | `kernel/hooks/subagentstop.py`, `src/gov/hooks/subagentstop.py`, `start_lead.sh` | fix under W1-29 | ~20 LOC |
| 6 | Loop budget to two: `ESCALATION_AT = 2`; `role-lead.md:49` to two rounds; drop the FULL review run and the guard/sandbox lines of `brief.md` (§5.5) | `src/gov/close/state.py:17`; kernel templates (the CTO's text, §3.5) | fix under W1-30; template lines a chore by the CTO | 1 LOC + text |
| 7 | Pause honoured everywhere: `run_tick.sh`, `start_lead.sh` exit while frozen; `gov pause` sends a stop message to live sessions | dispatch scripts; `src/gov/pause/command.py` | fix under W1-28 (the Contract names it) | ~30 LOC |
| 8 | Acceptance tests red on the base: the queue runs the folder at the base and refuses one that is all green there | `src/gov/queue/command.py` | fix under W2-202 | ~40 LOC |
| 9 | Schedule what is built: `gov doctor` daily (with backup age and the 365-day setting), `gov spend check` in the tick, memaudit weekly, `gov decisions basis --week`, the nightly; `lefthook install` for G1/G2 | crontab, `.git/hooks` | chore (configuration) | ~10 lines |
| 10 | Basis line at the commit: a G1 check over `HEAD^..HEAD`, run from the reference-transaction hook as an inbox notice and in the queue's structural families | `kernel/checks/`, `.git/hooks/reference-transaction`, `src/gov/check/structural.py` | fix under the A-8 basis-line work (CAP-68) | ~30 LOC |
| 11 | Owner approval check alive: drop the skip at `check/authority.py:44`; check new ACCEPTED register entries for `Decided-by: owner` | `src/gov/check/authority.py`, `src/gov/decisions/` | fix under W1-11 | ~40 LOC (expect old findings at first) |
| 12 | Kit CI: no gitleaks on push while `secrets.yaml` says off; the scan default off; one scan in `gov release --public` | `template/.github/workflows/ci.yml.jinja`, `src/gov/rebuild/command.py`, `src/gov/release/` | fix under W2-17 (kit) | ~30 LOC |
| 13 | Containment per commit trailer (CAP-58.h); `gov close` containment as a notice, not a refusal | `src/gov/queue/checks.py`, `src/gov/close/command.py` | fix under W1-50 | ~30 LOC |
| 14 | Memory block: carry the bundle uncut, or re-word CAP-15/65.a; helpers' retrieves logged with a role; the 6 skills get the memory line | `src/gov/brief/memory.py`; `src/gov/memory_use`; kernel skills | fix under W2-197; skills a chore by the CTO | ~25 LOC + text |
| 15 | Decision package: schema requires the ten headings; the skill's "six parts" reconciled | `decision-package.schema.json`, orchestration skill | fix under W1-34 | ~15 LOC + text |
| 16 | Claim lock wired: `gov launch` calls `claims.claim` | `src/gov/launch/launcher.py` | fix under W1-09 | ~15 LOC |
| 17 | `gov release` refuses without a passing release-acceptance record; a released tag checked by `gov doctor` | `src/gov/release/`, `src/gov/doctor/` | fix under W2-81 / the release tooling (the owner's tool) | ~30 LOC |
| 18 | CAP-24.c: decide between the Contract's "landing checks kernel bytes against the CTO-approved list" and EMERGENCY-2 §2.10. Smallest code: a queue notice for kernel-text paths without `Approved-by: cto` | `src/gov/queue/checks.py`, or a Contract re-wording | the CTO's decision, then a fix under W2-115b | ~25 LOC |
| 19 | Run-time tool: cron the product `gov dispatch tick`/`watch`, retire the scratch dispatcher (RT-1, 3, 7, 8) | `src/gov/dispatch/`, crontab | the run-time tool's tickets (W2-121c/d); see audit 3 | larger |
| 20 | Smaller wiring: `validate()` at the end of `gov retrieve`; canaries at the end of `gov rebuild`; `gov doctor` path-map matcher; SessionStart `startup` matcher; skill-version check over `kernel/skills` | as in §4 rows | fixes under W1-21, W1-22, W1-27, W1-49, W1-35 | ~10 LOC each |

## 7. Summary for the owner

The Contract is mostly built, but little of it stops a mistake when it happens. What is enforced runs in two places: the landing (`gov queue`) and the launcher (`gov launch`). Both refuse the right things: tests written by the builder, a missing acceptance folder, a paused project, a model the rubric does not give. Today neither is on the path. Gov OS's own work is merged by hand, and since 18 November every lead was started by a script that only checks its brief file is not empty, and every worker as an in-session helper. So the test-authorship rule, the impact-selected tests and the close at the land are, in Gov OS today, things the CTO and the leads are asked to do. Most other checks exist as commands nobody runs by themselves: no lefthook, CI only by hand, the nightly switched off. Briefs and templates are asked, not made. Leads get hand-written briefs with no template, `gov brief` (which refuses an unready ticket and an unfilled slot) ran once in five days, and the role files every helper reads still hold unfilled slots like `{CMD:retrieve}` in Gov OS and EXAMIN alike. The one template filled under code is the helpers' twelve-field return. The fixes are small and mostly built already. First, land L2-4 so Gov OS lands through `gov queue`. Then start leads through `gov launch` with a brief that has no unfilled slot. Then add the landing's four missing checks (clean tree, fresh store, disk, trailers). With those three, about thirty Contract items move from "asked" to "made", without a guard and in line with "catch and correct" (EMERGENCY-2 §2.1).
