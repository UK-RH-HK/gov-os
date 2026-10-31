# ROLES-SPEC-1 — Roles and briefs for the three layers

For the owner's review and approval (DEC-954, "the roles spec, before building").
Drafted 2026-10-30 by the CTO's helper. Read-only sources; nothing is built on it until you approve.

**State legend** (used in every table):
- **BT** = built and tested (merged)
- **B** = built only (on a branch, or merged without its close)
- **D** = drafted (text exists, not in force)
- **S** = sketched (a line or a plan row)
- **M** = missing

---

## 1. Summary (one screen)

**The roles** (owner's names; the agents keep their role names, DEC-954 Q13a):

| Layer | Role | Role id |
|---|---|---|
| 1 | CTO (master orchestrator) | `orchestrator` |
| 2 | Senior Engineer (one per stream) | `senior-engineer` (new) |
| 3 | Ticket lead | `orchestrator` today; `ticket-lead` with W2-21 |
| workers | Independent test designer | `independent-test-designer` |
| workers | Implementer: engineer (code) | `engineer` |
| workers | Implementer: product-spec (specs, docs) | `product-spec` |
| workers | Research | `research` |
| workers | Independent reviewer (FULL probe) | `independent-reviewer` (new file) |
| checks | Independent auditor | `independent-auditor` |
| helpers | CTO helper; synthesiser | no role of their own (§3.10) |

**What exists:** six Wave 1 role files; ten kernel skills; five brief templates;
the project's common lead brief (174 lines) and judgement rules; an 80 KB prompt.
W2-60a (role, skills, model and effort loaded at launch) is built, not merged.
The five-rule guard hook is committed, not wired until ACT 1.

**The main gaps:**
- no role file for the CTO's duties, the Senior Engineer, the ticket lead or the reviewer;
- no machine-readable defaults in any role file (W2-60a reads three lines that no role file carries yet);
- no Senior Engineer skill, brief or playbook; no coordination ticket per stream;
- no watcher of the Senior Engineers' state;
- no typed handoff record (CAP-22.b was moved to Wave 3 by DEC-832/DEC-841);
- no generated skill copy carries a version, so W2-60a would refuse any role that names a skill.

**Who fills them** (§6):
- **W2-33, re-scoped:** every role file with its defaults; four role files new or rewritten; the typed handoff.
- **W2-11, widened by one round:** the skills and brief templates for the three layers.
- **W2-60b, widened a little:** roles, effort and network read from the role files.
- **W2-83a, W2-83b (re-scoped):** the playbook form, then one playbook per stream.
- **New:** W2-89 (the CTO's watchers, `gov streams`); W2-00a/b/c (a coordination ticket per stream).
- **CTO + owner:** prompt v4 (the CTO's brief) and `briefs/SE-common.md`, as one package.
- **After ACT 2:** W2-21 (`gov launch lead` and `senior-engineer`, the role path in an adopted repository).

**You are asked to approve:** this spec, and the twelve questions in §8.
Recommended answers are given for each.

---

## 2. (a) What exists and where

### 2.1 Contract, Charter and master rules

| Piece | Path | What it asks | State |
|---|---|---|---|
| MR-3 | Charter §4 | builder never writes its acceptance tests | BT (guard rule 1) |
| MR-4 | Charter §4 | fresh read-only auditor; audit ≠ impact ≠ discovery | BT (role), partly enforced |
| MR-5 | Charter §4, §6 | company of role agents: purpose, paths, tools, model tier, authority, handoff | BT for 6 roles (W1-33) |
| MR-6 | Charter §4, §6 | owner decides by packages; at most 5 open | BT (process) |
| Charter §5 | loop policy | 3 non-converging iterations → escalation; count never disclosed | BT (briefs) |
| Charter §6 | wave 2 role list | architecture … UX, test execution, integration, typed handoffs | 4 → skill packs, rest → W3 (DEC-832) |
| CAP-22.a | `contract.yaml` | roles as generated subagent definitions | BT (W1-33) |
| CAP-22.b | `contract.yaml` | typed handoff records a fresh agent can act on | M; moved to W3 (DEC-832 item 4, DEC-841) |
| CAP-22.c | `contract.yaml` | distinct test-execution and integration roles | M; moved to W3 (same) |
| CAP-22.d | `contract.yaml` | minimal research role | BT (W1-46) |
| CAP-24.a–c | `contract.yaml` | skills versioned; a skill grants nothing; changes via CIT-P | BT in kernel; generated copies carry no version |
| CAP-33 | `contract.yaml` | CIT-P before, CIT-E after; owner approval | partial (no `gov impact`; W2-37 held) |
| CAP-35.c | `contract.yaml` | role defaults: tier and reasoning per role | W3; lite form in W2-60a (B) |
| CAP-36.a | `contract.yaml` | per run: model, effort, cost, pass/fail | W3; lite in W2-60a/W2-60b |
| CAP-37.d | `contract.yaml` | the twelve-field worker return | BT (`hooks/subagentstop.py`) |
| CAP-47.a/b | `contract.yaml` | independent roles; fresh sessions | W3; W1 form BT |
| CAP-59 | `contract.yaml` | review-repair loop budget | BT (briefs, DEC-096) |
| CAP-61.a–e | `contract.yaml` | `gov launch`: strict sandbox, per-role network | BT (W1-46); W2-56 widens |
| CAP-61.f | `contract.yaml` | untested sandbox cases (EXP-002) | M (W2-40) |

### 2.2 Kernel role files (`template/governance/kernel/roles/`)

Generated through rulesync (`.rulesync/subagents/`, `template/.rulesync/subagents/`) into `.claude/agents/`.

| File | Lines | Covers | Gaps in it | State |
|---|---|---|---|---|
| `orchestrator.md` | 62 | one orchestrator + the ticket-lead section (DEC-236) | no CTO duties, no streams, no watchers; teaches LEAD_CHECKPOINT (superseded, DEC-838) | BT (W1) |
| `engineer.md` | 26 | implementer for code | prose "Model tier: standard", no default line, no skills | BT (W1) |
| `independent-test-designer.md` | 29 | MR-3 tests | same | BT (W1) |
| `product-spec.md` | 29 | specs, templates, docs; gap mode | same | BT (W1) |
| `research.md` | 19 | one experiment folder | same | BT (W1) |
| `independent-auditor.md` | 29 | read-only audit; report path | same; also used for reviewers today | BT (W1) |
| `ticket-lead.md` | — | — | named in W2-21's paths only | M |
| `senior-engineer.md` | — | — | — | M |
| `independent-reviewer.md` | — | — | the new guard hook already names the id | M |

Project roster `governance/project/roster.yaml` (36 lines): per role, its role file, agent,
launch form and network profile. Machine-read today by the session-start hook (the orchestrator's prompt). State: BT.

### 2.3 Skills (`template/governance/kernel/skills/`, generated as `.claude/skills/`)

| Skill | Version | Lines | Used by | State |
|---|---|---|---|---|
| orchestration | 1.0.0 | 97 | orchestrator, leads | BT; stale in parts (ceiling, LEAD_CHECKPOINT, DEC-508) |
| checkpoint | 1.1.0 | 50 | all orchestrators | BT; no stream checkpoint |
| retrieval | 1.0.0 | 30 | all | BT |
| test-design | 1.0.0 | 40 | test designer | BT; proportion rule committed 10-30 (`d52da393`); red-first still missing |
| audit | 1.1.0 | 57 | auditor | BT; no judgement rules (DEC-801..809) |
| planning | 1.0.0 | 46 | orchestrator, product-spec | BT |
| change | 1.0.0 | 58 | orchestrator, product-spec | BT |
| discovery | 1.0.0 | 55 | research, product-spec | BT |
| adopt | 1.0.0 | 45 | adoption | BT |
| superpowers (TDD 331, debugging 284, verification 122) | vendored | 737 | engineer | BT (vendored) |

**Finding:** none of the 18 generated copies under `.claude/skills/` carries a `version`.
W2-60a refuses a launch whose role names a skill without one (its CIT-E §D.2).

### 2.4 Brief templates (`template/governance/kernel/templates/`)

| Template | Lines | State | Gap |
|---|---|---|---|
| `brief-lead.md` | 140 | BT | lags the project's common brief; teaches LEAD_CHECKPOINT and a context limit; no `brief_gaps` |
| `brief-test-designer.md` | 76 | BT | no twelve-field rule (W2-11) |
| `brief-engineer.md` | 66 | BT | same |
| `brief-product-spec.md` | 76 | BT | same |
| `brief-reviewer.md` | 58 | BT | no judgement rules; says "write nothing" (fits rule 5) |
| `checkpoint.md`, `decision-package.md`, `decision-record.md` | 28–64 | BT | — |
| `brief-senior-engineer.md` | — | M | — |
| `handoff.md` + `schemas/handoff.schema.json` | — | M | CAP-22.b |
| `playbook.md` + schema | — | M | W2-83a |
| `schemas/role.schema.json` | — | M | §5 |

### 2.5 The project's briefs and prompt

| Piece | Path | State | Note |
|---|---|---|---|
| Common lead brief | `governance/project/briefs/LEAD-w2-common.md` (174 lines) | BT (in use) | 26 revisions; most of its machinery rules lift at ACT 1 |
| Judgement rules | `briefs/JUDGEMENT.md` (19) | BT | project only, not kernel |
| Auditor part | `briefs/AUDITOR-common.md` (38) | BT | project only |
| Orchestrator prompt | `prompts/w2-orchestrator.md` (381 lines, ~80 KB) | BT | §0 = DEC-953/954; Appendix A = briefs A1–A5 |
| Decisions in force | `orchestration/DECISIONS-IN-FORCE.md` (88) | BT | read at every resume |
| Brief builder | `.gov-runtime/scratch/orchestrator/tools/build_lead_brief.py` | B (untracked tool) | fills the common brief's 8 slots |
| Lead watchers | `tools/lead_return_watch.sh`, `interim_watch.sh` | B (untracked) | leads only; no stream state |
| Senior Engineer brief | `briefs/SE-common.md` | M | plan §5.4 called it `SUB-common.md` |

### 2.6 Code that applies roles

| Piece | Path | State | What it does with roles |
|---|---|---|---|
| Launcher | `src/gov/launch/launcher.py` (358) | BT | fixed `WORKER_ROLES` (5) and `OWN_TICKET_ROLES` (3); no role text, no model, no effort |
| Role reader | `src/gov/launch/role.py` (W2-60a) | B | reads `- **Version:**`, `- **Launch default:**`, `- **Skills:**` lines; appends role file + skills |
| Launch record | `src/gov/launch/record.py` (W2-60a) | B | one record per launch under `.gov-runtime/launches/` |
| Product guard | `src/gov/guard/decide.py` | BT | `KNOWN_ROLES` (7, incl. `ticket-lead` with no write scope, DEC-434); unknown role → every write refused |
| Five-rule hook | `.claude/hooks/pretooluse.py` (161, `f7533c61`) | B (not wired until ACT 1) | `TEST_DESIGNER`; `REVIEWERS` = auditor, independent-reviewer, reviewer, auditor; install `ask` only for `orchestrator` |
| Path map | `governance/project/path-map.yaml` | BT | `permitted_roles` (6); `evaluation_sets.measures.roles` = engineer, research |

### 2.7 The tickets' KPIs (as filed today)

| Ticket | tk | Status | KPIs | Note |
|---|---|---|---|---|
| W2-60a | cv58 | in_progress | 9 success, FULL | built; round 3 (fail-open fix) due; merges only when role files carry the default line |
| W2-60b | ecac | open | 8, STANDARD | session record; launchable roles from role files |
| W2-11 | k7hz | open | 7, STANDARD | twelve fields, Policy 2, supersession, test-design; paths hold `roles/orchestrator.md` only |
| W2-33 | lrre | open | 5, STANDARD | **stale:** still carries the test-execution, integration and UX roles that DEC-832 moved to W3; DEC-832's four skill packs are not in it |
| W2-83a | dy7j | open | 5, STANDARD | the playbook form; after W2-64 |
| W2-83b | mc6n | open | 3, STANDARD | nine keystone playbooks (plan: re-scope to streams) |
| W2-21 | 1ahb | open | 8, FULL | `gov launch lead`; `roles/ticket-lead.md` in its paths |
| W2-82 | 4k3l | open | 7, STANDARD | refuses a lead (`orchestrator` + ticket) on an unready ticket |
| W2-56 | wnnz | in_progress | 7, FULL | `gov launch` for every worker |
| W2-00 | sdxk | open | 1, LITE | the CTO's coordination ticket |

---

## 3. (b) Every role

### 3.0 What holds for every role

- **Model:** `claude-opus-5-5` for every role (DEC-839 item 1). Full window, no compaction threshold (DEC-838).
- **Effort:** DEC-839's table, per role below. From W2-60a/W2-60b the launcher sets it from the role file.
- **The guard after ACT 1 keeps five rules** (DEC-953 item 2, DEC-954):
  1. only the independent test designer writes `tests/acceptance/**`;
  2. no reads of the hidden half of an evaluation set (from any worktree) or the held-out material;
  3. no reads of secrets;
  4. no installs without the owner (`sudo` refused to all);
  5. reviewers and auditors write only their own review and audit records.
- **Kept by briefs, not the guard:** Policy 2 (c), the counterpart rule. The test designer never reads the ticket's
  implementation; the implementer never reads the ticket's acceptance-test code (it may run them).
- **Reads are otherwise open** (DEC-820).
- **Every return** starts with the twelve fields (CAP-37.d): task, status, work_completed, files_changed, evidence,
  tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action. Payload after.
- **Refused twice for the same call: stop and say so.** An authentication error: start nothing, return `AUTH_REQUIRED`.
- **Nobody but the CTO contacts the owner** (DEC-850, DEC-855). Packages go up in DEC-818's six parts.
- **Closes run on the audit's 10 practices** (AUDIT-GOV-FEATURES-1 §5); the CTO runs them.

**The common brief checklist** (every brief carries these; role sections add to it):

| # | Item |
|---|---|
| C1 | Identity check first: `GOV_ROLE`, `GOV_TICKET`, tree and branch; stop if different |
| C2 | The ticket (or stream): ids, profile, allowed paths, KPI lines |
| C3 | Sources and the decisions that apply, by id; DECISIONS-IN-FORCE lines for this role |
| C4 | The five guard rules, and Policy 2 (c) where it applies |
| C5 | What it writes, and what it never writes |
| C6 | Memory: `gov retrieve` first (DEC-836); batches (DEC-860); small code-graph queries (DEC-859) |
| C7 | Code under test: `PYTHONPATH=<worktree>/src` per command (DEC-732), where it runs tests |
| C8 | Machine: scratch budget and `TMPDIR` (DEC-898); disk check before heavy runs; full runs under the test lock (closes first, DEC-954); no tree copies |
| C9 | Commits: `Task:`, `Implements:` (ids only), `Role:`, final block; no amend, rebase or push |
| C10 | Packages go to whoever started it, six parts; never the owner |
| C11 | Checkpoint at every handover (DEC-837) |
| C12 | The return: the twelve fields first; two-refusal stop; `AUTH_REQUIRED` |

---

### 3.1 CTO (master orchestrator)

**Purpose and duties** (DEC-953 item 8b, DEC-954 Q13, plan §5.1):
- keeps the WBS and the dependency graph; releases tickets to streams by their dependencies;
- runs work in parallel and in series to what the machine holds (resource gate), without reminders;
- is the **only writer of the main tree's tracked files**: tickets and claims, the register, the WBS and plan,
  the briefs and prompt (owner-approved), the orchestration record (recommended, Q6);
- merges into `w2/integrate`; runs every close on the 10 practices (`close_build.py`);
- owns the nightly and its red investigations;
- records decisions: the owner's, and delegated ones (DEC-220, DEC-936 2.5); only the CTO and the owner record;
- packages, pings, the morning package, the status block (DEC-949, DEC-948);
- **watches every Senior Engineer's state** and acts or escalates (below).

**Reads:** everything, except the five rules' refusals (held-out, hidden halves it is measured by, secrets).
Reads a lead's return only through its Senior Engineer's handoff, once the layers start.

**Writes:** anywhere in the repository except `tests/acceptance/**` (MR-3) and `.gov-runtime/**` outside
`scratch/` (DEC-176). Under the five-rule guard only rule 1 binds it; the rest is its role file's rule.

**Skills:** `orchestration` (the CTO's part), `planning`, `checkpoint`, `change`, `retrieval`.

**Model and effort:** opus-5-5; `high`; `max` when it drafts an owner package (DEC-839).

**Launch:** started by the owner, each morning, as a fresh interactive session.
`GOV_ROLE=orchestrator`, `GOV_TICKET` = W2-00's id (`settings.local.json`). Never by `gov launch`.

**Its brief** (= prompt v4, owner-approved) must always contain:
- [ ] C1–C12;
- [ ] read first: RESUME HERE, DECISIONS-IN-FORCE, its checkpoint, every stream checkpoint, `gov streams`,
      `pings.log` and the nightly's `status.txt`;
- [ ] the streams, their Senior Engineers and coordination tickets;
- [ ] the watchers and their thresholds (below);
- [ ] the delegation rule (DEC-220) and what stays the owner's;
- [ ] the 10 close practices and `close_build.py`;
- [ ] the resource gate and the test lock (closes first);
- [ ] the morning sequence (§4.3); the status block (DEC-948); pings (DEC-949).
Target size: about a quarter of today's 80 KB (plan item 7).

**Return or handover:**
- to the owner: packages (six parts, saved under `packages/`) with `owner-ping`; ACT files; the 07:30 morning package;
  the status block on every report;
- to the next CTO: RESUME HERE and its checkpoint, committed to `record/w2` (Policy 1);
- down to each Senior Engineer: typed handoffs `RELEASED`, `DECISION`, `CLOSED`, `HOLD` (§4.2).

**Stops and escalation:** prompt §8's stops (owner packages, ESCALATION, LAUNCH_BLOCKED, owner acts, wave exit).
Never idle while a stream has ready work. A Senior Engineer's escalation goes to the owner as a package.

**The watchers.** The CTO keeps today's (mem, usage, OOM, lead returns, the 05:37/07:30/07:45 wakes).
It adds one watcher of the Senior Engineers, `gov streams --watch` (W2-89), which exits on the first signal:

| Signal | Meaning | Default threshold | The CTO acts |
|---|---|---|---|
| `working` | a lead runs in the stream, or the SE acted recently | — | nothing |
| `IDLE_WITH_WORK` | no lead running, a released or ready ticket waiting | 10 min | asks the SE, releases, or restarts it |
| `WAITING_ON_CTO` | the SE's open package or request to the CTO | 30 min | decides (delegated) or packages to the owner the same hour |
| `WAITING_ON_OWNER` | a package with the owner | per DEC-949 | listed in OWNER_ACTION; pinged once when it arose |
| `SILENT` | state says working, but no record or log change | 45 min | checks the process and the leads; restarts if dead |
| `GONE` | the SE's process ended without a stream checkpoint | at once | starts a fresh SE from the last checkpoint |
| `AUTH_REQUIRED` | an SE or lead hit an access error | at once | starts nothing more; P1 to the owner |
| `UNREADABLE` | a state record that cannot be read | at once | treats as `SILENT`; never as working |

Thresholds are project settings the owner sets; the defaults above are proposals, unmeasured.

**Morning handover:** §4.3.

---

### 3.2 Senior Engineer (stream sub-orchestrator)

**Purpose and duties** (DEC-953 item 8b, DEC-954 Q13a):
- runs its stream's tickets once the CTO releases them: writes each lead's ticket part, starts the lead,
  reads the lead's single return;
- checks a DONE return against the 10 practices before sending "ready to close";
- sends a lead back for a merge-back of `w2/integrate` when the CTO reports a conflict;
- keeps the stream moving: the next ticket ready, no lead idle on an answer it can give;
- proposes decisions up; decides none (only the CTO and the owner record decisions, W3-P09);
- keeps its stream checkpoint and its state current.

**Its stream, identity and coordination ticket:**

| Stream | Holds (plan §2, §5.2) | Coordination ticket |
|---|---|---|
| S1 Memory | W2-55, W2-04, W2-05, W2-06, W2-13, W2-15a, W2-32, W2-08, W2-61h, W2-15b, the Q9f ticket | W2-00a (new) |
| Agents (S2+S3) | W2-83a, W2-83b, W2-56, W2-21, W2-82, W2-40 (after the roles land) | W2-00b (new) |
| S4 Adoption | W2-52, W2-81, W2-23, W2-27 to W2-30 | W2-00c (new) |
| S0 Master | closes, held work, W2-24, W2-25, W2-46, W2-47 | W2-00 (the CTO's) |

Identity: `GOV_ROLE=senior-engineer`, `GOV_TICKET` = its coordination ticket. The guard, the launch record
and the CTO's watcher all key on that pair (DEC-954 Q13).

**Reads:** everything, except the five rules' refusals. Its leads' returns; never its workers' output (DEC-236).

**Writes (recommended, Q6):** no tracked file anywhere.
- its stream folder `.gov-runtime/scratch/streams/<stream>/` (briefs, logs, handoffs, checkpoint, state);
- each lead's brief there; the lead writes in its own worktree.
- Claims, ticket files, the register, merges and closes stay the CTO's. The SE asks for them by handoff.
- Under the five-rule guard, installs are refused to it (only `orchestrator` asks the owner): right, since it may not install.

**Skills:** `stream-orchestration` (new, W2-11), `checkpoint`, `retrieval`.
Plus its stream playbook (W2-83b), given in its brief, not as a skill.
(Plan §5.4 also listed `test-design`; not needed, since the lead writes the test designer's brief. Dropping it saves context.)

**Model and effort:** opus-5-5; `high` (no DEC-839 row yet; proposed as the orchestrator's).

**Launch:** by the CTO, headless, in the background, from the main tree.
- Until W2-21: the hand form (DEC-715's), with `GOV_ROLE=senior-engineer` and its ticket in `--settings`.
- After W2-21: `gov launch senior-engineer <coordination ticket>` (unsandboxed, like a lead).
- It waits for its leads in bounded foreground loops, as leads do; it never ends its turn while a lead runs.

**Its brief** (`briefs/SE-common.md` + the stream's part) must always contain:
- [ ] C1–C12;
- [ ] its stream, its coordination ticket, its tickets with their state and dependencies;
- [ ] its playbook (purpose, practices, ticket classes, roles and skills);
- [ ] its last stream checkpoint, if resuming;
- [ ] the lead brief: the common part's path, and how it writes the ticket's part;
- [ ] the handoff kinds it sends and receives (§4.2), and where it writes them;
- [ ] the state it must keep current, and when (every transition);
- [ ] the resource gate: it asks the CTO before starting a lead (one gate, held by the CTO);
- [ ] its morning stop: stream checkpoint and state `stopped` by 07:00.

**Return or handover:**
- up to the CTO: typed handoffs `READY_TO_CLOSE`, `PACKAGES`, `ESCALATION`, `STATE`, `STREAM_CHECKPOINT`,
  `LAUNCH_BLOCKED`, `AUTH_REQUIRED` (§4.2);
- down to each lead: the lead brief (ticket part + common part).

**Stops and escalation:**
- a lead's ESCALATION (three non-converging iterations) → `ESCALATION` up at once; the owner decides (Charter §5);
- a package it cannot settle → `PACKAGES` up; it keeps every unaffected ticket moving;
- nothing ready in its stream → state `idle`, which the CTO's watcher sees;
- an access error → `AUTH_REQUIRED` up, nothing more started;
- a path overlap with another stream → up to the CTO, never settled between streams.

---

### 3.3 Ticket lead

**Purpose and duties** (DEC-236, `brief-lead.md`): runs one ticket's loop in its worktree:
tests first by a fresh test designer, red checked; a fresh implementer; verification with the one selection tool;
for FULL, a fresh reviewer; a checkpoint at each round boundary; one return.
Holds the loop count and never discloses it (DEC-096). Never merges into the integration branch.

**Reads:** everything, except the five rules' refusals; never its workers' transcripts beyond their returns.

**Writes:**
- `.gov-runtime/scratch/lead/**` in its worktree (briefs, logs, CHECKPOINT.md);
- the probe record under `docs/probes/<ticket>/` (DEC-733), only a passing one;
- `gov checkpoint` records; merge commits of `w2/integrate` into its branch when told (DEC-436);
- never `src/`, `template/`, `tests/`, `docs/` otherwise; never tickets or the register.
- **Gap:** the product guard gives `ticket-lead` no write scope at all (DEC-434), which refuses the probe and
  checkpoint records. W2-21 reconciles it when leads switch to that id.

**Skills:** `ticket-loop` (new: the lead's part of today's orchestration skill, W2-11), `checkpoint`, `retrieval`.

**Model and effort:** opus-5-5; `high` (DEC-839).

**Launch:** by its Senior Engineer (by the CTO until the layers start), in its worktree, in the background.
- Until W2-21: the hand form (prompt §4), `GOV_ROLE=orchestrator`, `GOV_TICKET` = the ticket.
- After W2-21: `gov launch lead <ticket>`, as `ticket-lead`. W2-82's refusal must then accept that id too.
- Leads run detached and continue through the morning handover.

**Its brief** (ticket part + `LEAD-w2-common.md`, later the kernel's `brief-lead.md`) must always contain:
- [ ] C1–C12;
- [ ] why it starts now, the decisions staged for it, the run's order, the probe's focus (ticket part);
- [ ] the ticket's slots: id, W2 id, profile, paths, rows, sources, `Implements:` ids, estimate;
- [ ] the loop (tests first, red, implement, verify, FULL review, checkpoint);
- [ ] how it launches each worker (form, model, effort per role and profile), one writing worker at a time;
- [ ] the test selection command and the test lock;
- [ ] the judgement rules for its reviewer (JUDGEMENT.md, word for word);
- [ ] what goes into every worker brief (C1–C12, Policy 2 (c), DEC-732's line word for word);
- [ ] the return statuses and `brief_gaps:` (DEC-943).

**Return:** one message, to its Senior Engineer (the CTO until then).
The twelve fields; status DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED;
then `brief_gaps:`. DONE carries the branch head, commits, suites as run, the selection's scope and reasons,
the probe record, residuals and learning metrics (DEC-106).

**Stops and escalation:** three non-converging iterations → ESCALATION; a launch denied → LAUNCH_BLOCKED;
the scratch budget passed → PACKAGES; a run held past 90 min by the test lock → checkpoint and PACKAGES (DEC-943);
an access error → AUTH_REQUIRED.

---

### 3.4 Independent test designer

**Purpose:** writes the ticket's acceptance tests from its KPIs before implementation; shows them red for the
stated reason (MR-3). In proportion to the profile (DEC-221, DEC-951 item 5).

**Reads:** the ticket, its sources, the existing code as it stands on `w2/integrate`, anything else.
Never this ticket's implementation (Policy 2 (c), brief-kept). Drops unread any `gov retrieve` result under the
ticket's implementation paths, and names it (P-R1).

**Writes:** `tests/acceptance/<W2>/` (rule 1: the only role that may); an earlier ticket's tests only where the KPIs
name them, with `Rewrite-Reason:` (DEC-491, DEC-906); its README mapping each KPI line to tests and red reason.

**Skills:** `test-design`, `retrieval`.

**Model and effort:** opus-5-5; `high`; `xhigh` for FULL tickets (a measured trial, DEC-839).

**Launch:** by its lead, `gov launch independent-test-designer <ticket>`, sandboxed, empty network.

**Its brief** must always contain: C1–C12; behaviour and sources only, never names of code to be written (DEC-462);
the proportion rule; red first; the README; Policy 2 (c); how its tests exercise the worktree's code (DEC-732).

**Return:** twelve fields to the lead: test count, KPI and `covers` coverage, the red reason, rewrites, packages.
**Stops:** an ambiguous KPI → a package, never a guess.

---

### 3.5 Implementer: engineer

**Purpose:** implements one ticket until its acceptance tests pass; builder tests as regression evidence only.

**Reads:** everything but this ticket's acceptance-test code (it runs them and reads results only).
**Writes:** its ticket's `allowed_paths`, never `tests/acceptance/**` (rule 1); its run clone under `~/gov-os-runs/<W2>/`.

**Skills:** `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `retrieval`.
(DEC-832's four skill packs would add here; Q5 recommends Wave 3.)

**Model and effort:** opus-5-5; `high`.
**Launch:** by its lead, `gov launch engineer <ticket>` on a ticket whose role is engineer; sandboxed, empty network.
(Old form with the tripwire only for code-graph suites, until W2-56.)

**Its brief** must always contain: C1–C12; Policy 2 (c); the proportion rule (DEC-135); never make a guard decision
fail open; for a repair, only the failing output (DEC-096).

**Return:** twelve fields: files, tests run with counts, lines of code. **Stops:** a disputed test → a package; never edits it.

---

### 3.6 Implementer: product-spec

**Purpose:** writes what a ticket specifies: schemas, templates, skills, role files, documentation, CIT-Ps;
or drafts the answer to a specification gap (gap mode).

**Reads:** as the engineer. **Writes:** its ticket's `allowed_paths` (ticket mode); nothing (gap mode).
**Skills:** `planning`, `change`, `retrieval`.
**Model and effort:** opus-5-5; `high`.
**Launch:** by its lead, `gov launch product-spec <ticket>`, sandboxed, empty network.
**Its brief** must always contain: C1–C12; the mode; for a kernel change, that the CIT-P is approved before the edit.
**Return:** twelve fields; in gap mode, a draft answer with sources, recommendation and confidence.

---

### 3.7 Research

**Purpose:** a spike, bake-off or experiment, leaving an evidence record (question, method, commands, results,
verdict, residuals). Full lifecycle CAP-32 stays Wave 3.
**Reads:** as all. **Writes:** exactly one experiment folder; installs only into a venv inside it (DEC-163).
**Skills:** `discovery`, `retrieval`.
**Model and effort:** opus-5-5; `high`.
**Launch:** by its lead or the CTO, `gov launch research <ticket>`; the research allowlist (DEC-158, DEC-241).
**Its brief** must always contain: C1–C12; the question; the folder; the allowlist; the evaluation sets it must not read.
**Return:** twelve fields naming the evidence record.

---

### 3.8 Independent reviewer (FULL probe)

**Purpose:** a fresh session that wrote none of the code probes the final head for behaviour the tests miss:
lost work, writes out of scope, acceptance tests changed by an implementer, the guard failing open (DEC-137, DEC-498).
At most two reviews per declared round (DEC-413, DEC-916).

**Reads:** everything, tests and code alike (DEC-820). Runs the code; does not judge by reading alone.

**Writes:** under rule 5, only its own review record and its scratch (`docs/probes/`, `.gov-runtime/scratch/review/`).
Recommended: it keeps returning the record's content and its lead commits a passing one (DEC-733 unchanged),
so a failing review stays a draft.

**Skills:** `audit` (its review part, with the judgement rules, W2-11), `retrieval`.
**Model and effort:** opus-5-5; `max` (reviews are for FULL tickets; DEC-839 "max for FULL probes").

**Launch:** by its lead. Today as `independent-auditor` with read-only tools.
After W2-33 and W2-60b: `gov launch independent-reviewer <ticket>`, read-only tools (Bash, Read, Grep, Glob).

**Its brief** must always contain: C1–C12; the head to probe; JUDGEMENT.md word for word (two questions, two lines
per finding, DEC-801 to DEC-809); findings as described behaviour, never code (DEC-136).

**Return:** twelve fields: the head probed; each finding with `Ordinary work:` and `Consequence:`; what was sound.

---

### 3.9 Independent auditor

**Purpose:** audits finished work against the Contract, the sources and the owner's decisions, as a fresh read-only
session (MR-4): milestone audits, W2-25, W2-28, W2-30, W2-47, the features audit.
**Reads:** everything. **Writes:** under rule 5, its audit report path only (`docs/audit/**`, `docs/assessment/**`).
**Skills:** `audit`, `retrieval`.
**Model and effort:** opus-5-5; `max` (DEC-839).
**Launch:** by the CTO, `gov launch independent-auditor <audit ticket>`; or an in-session read-only subagent for a short check.
**Its brief** must always contain: C1–C12; `AUDITOR-common.md` and JUDGEMENT.md word for word; the yardstick
(sources plus accepted decisions); its scratch budget (30 GB, 2,000,000 files).
**Return:** the report committed alone (DEC-924 item 2), then twelve fields naming it and any packages; PARTIAL if over budget.

---

### 3.10 Others in use

| Who | What it is | Runs as | Effort | Note |
|---|---|---|---|---|
| CTO helper | an in-session subagent of the CTO (planning, drafts, this spec) | the CTO's session (`orchestrator`) | the CTO's | writes only scratch drafts; returns twelve fields; no role file needed |
| Synthesiser | merges lens or audit reports into one | `independent-auditor` with a synthesis brief | `max` (DEC-839) | a brief, not a role; writes under `docs/assessment/` (rule 5 allows) |
| Owner | customer and final authority (L5, MR-6) | human | — | approves, pushes, tags, installs |
| Operator | acts for the owner at a terminal (Charter §6) | human-run session | — | runs ACT files |
| Charter's other roles | architecture, frontend, DevOps/SRE, performance; test execution, integration, UX | — | — | Wave 3 (DEC-832); backend, data, API, security are skill packs (Q5) |

---

## 4. The handover chain, end to end

### 4.1 The chain

```
owner
  ↕  packages + ping · ACTs · morning package · answers in chat
CTO  (orchestrator · W2-00)
  ↕  typed handoffs: RELEASED, DECISION, CLOSED, HOLD  ↓
     READY_TO_CLOSE, PACKAGES, ESCALATION, STATE, STREAM_CHECKPOINT  ↑
Senior Engineer ×3  (senior-engineer · W2-00a/b/c)
  ↕  lead brief ↓ · one return (twelve fields + brief_gaps) ↑
ticket lead  (orchestrator → ticket-lead · its ticket · its worktree)
  ↕  worker brief ↓ · twelve fields + commits ↑
workers  (test designer · engineer · product-spec · research · reviewer)
```

### 4.2 Each link

| From → to | Form | Where it lands | When |
|---|---|---|---|
| Owner → CTO | chat answer | recorded in the register by the CTO | any time |
| CTO → owner | six-part package + `owner-ping`; ACT file | `orchestration/packages/` | as it arises, 07:30–24:00 (DEC-949) |
| CTO → owner | morning package | `packages/P1-MORNING-<date>.md` | 07:30 |
| CTO → SE | `RELEASED` (ticket claimed, worktree made, base, decisions) | stream folder `handoffs/` | on dependency met and gate open |
| CTO → SE | `DECISION` (answer to its package); `CLOSED` (close result); `HOLD` | same | as they happen |
| SE → CTO | `READY_TO_CLOSE` (the lead's DONE, checked against the 10 practices) | same | on a lead's DONE |
| SE → CTO | `PACKAGES`, `ESCALATION`, `LAUNCH_BLOCKED`, `AUTH_REQUIRED` | same | as they happen |
| SE → CTO | `STATE` (working, idle, waiting-decision, stopped) | same; read by `gov streams` | every transition |
| SE → next SE | `STREAM_CHECKPOINT` (leads running, returns pending, next 3 tickets, asks) | same | by 07:00, and at compaction |
| SE → lead | lead brief (ticket part + common) | stream folder `briefs/` | at release |
| lead → SE | one return | stream folder `log/<W2>-A5-*.json` | at the end of its run |
| lead → worker | worker brief from the kernel template | worktree `scratch/lead/briefs/` | per step |
| worker → lead | twelve fields + commits with trailers | worktree `scratch/lead/log/` | at the end |

Every handoff is one typed record (W2-33): kind, from (role, ticket, session), to, the subject ticket, time,
the twelve fields, and per kind: branch and head, packages, inputs, open questions, next step.
A fresh agent given only the record and the repository can state the task, inputs, open questions and next step (CAP-22.b).

### 4.3 The day, and the fresh session each morning

| Time | What happens |
|---|---|
| 02:00–05:00 | the nightly full run; leads run no heavy tests |
| 05:37 | the CTO investigates any red (DEC-953 item 3) |
| by 07:00 | each SE writes its `STREAM_CHECKPOINT` and `STATE stopped`, then ends |
| ~07:05 | **recommended (Q8):** the outgoing CTO starts a fresh SE per stream from its checkpoint, so no stream waits on the owner's morning |
| 07:30 | the CTO sends the morning package, writes RESUME HERE, commits its record, ends |
| owner's start | the owner starts a fresh CTO |
| all day | leads continue detached across the handover; their returns land in their SE's log folder |

### 4.4 What each reads first

| Session | Reads first, in order |
|---|---|
| CTO | prompt v4 §0 → RESUME HERE → DECISIONS-IN-FORCE → `gov streams` → each `STREAM_CHECKPOINT` → `pings.log`, nightly `status.txt` |
| Senior Engineer | its brief → its playbook → its last `STREAM_CHECKPOINT` → its open handoffs → its log folder's unread returns |
| Ticket lead | its brief → its worktree's `scratch/lead/CHECKPOINT.md` if present → the ticket file → the sources |
| Worker | its brief → the ticket file → the sources (through `gov retrieve`) |

---

## 5. Machine-readable defaults per role

### 5.1 Where they live, and the form

- **In each kernel role file** (`template/governance/kernel/roles/<id>.md`; in an adopted repository
  `governance/kernel/roles/`, W2-21). The file name is the role id.
- **Form (recommended, Q3):** W2-60a's line form, one field per line, `- **<Field>:** <value>`, each once and whole.
  W2-60a already reads three of these lines, and the same file text is appended to the session, so the agent and
  the launcher read the same value: one source, no drift.
- **Checked by a schema:** `template/governance/kernel/schemas/role.schema.json` describes the fields the reader
  returns; a test runs the reader over every kernel role file.
- **Project overrides:** `governance/project/roster.yaml` (exists), for network profile or model, by owner decision only.

### 5.2 The fields

| Field (line head) | Value | Required | Read by |
|---|---|---|---|
| `Version` | `<major>.<minor>.<patch>` | yes | launcher (record), gov check |
| `Launch default` | `model <id>, effort <low…max>` | yes | launcher (W2-60a) |
| `Effort by profile` | e.g. `FULL xhigh` | no | launcher (W2-60b), from the ticket's profile |
| `Skills` | names, comma-separated | no | launcher (W2-60a), brief builder |
| `Launch` | `gov-launch` · `hand-form` · `owner` | yes | launcher (W2-60b: launchable set) |
| `Ticket` | `own-role` · `any-in-progress` · `coordination` | yes | launcher (replaces `OWN_TICKET_ROLES`) |
| `Network` | `empty` · `research-allowlist` · `unsandboxed` | yes | launcher; roster may override |
| `Guard class` | `test-designer` · `implementer` · `reviewer` · `coordinator` · `research` | yes | a drift test against the guard's sets |
| `Writes` | a short pattern, e.g. `ticket allowed_paths` | yes | brief builder; documentation |
| `Tools` | e.g. `Bash, Read, Grep, Glob` | yes | adapter (agent front matter); launcher default `--allowedTools` |
| `Brief template` | e.g. `brief-engineer.md` | yes | brief builder |
| `Return` | `twelve-fields: DONE, PACKAGES, …` | yes | brief builder; `subagentstop` hook |

The guard keeps its own fail-closed sets in code (fast, no file read per tool call).
A test checks that each role file's `Guard class` matches them: a drift is a red, never a silent widening.

### 5.3 The values (proposed)

| Role id | Model | Effort (by profile) | Launch | Ticket | Network | Guard class |
|---|---|---|---|---|---|---|
| `orchestrator` (CTO) | opus-5-5 | high | owner | coordination | unsandboxed | coordinator |
| `senior-engineer` | opus-5-5 | high | hand-form → gov-launch (W2-21) | coordination | unsandboxed | coordinator |
| `ticket-lead` | opus-5-5 | high | hand-form → gov-launch (W2-21) | any-in-progress | unsandboxed | coordinator |
| `independent-test-designer` | opus-5-5 | high (FULL xhigh) | gov-launch | any-in-progress | empty | test-designer |
| `engineer` | opus-5-5 | high | gov-launch | own-role | empty | implementer |
| `product-spec` | opus-5-5 | high | gov-launch | own-role | empty | implementer |
| `research` | opus-5-5 | high | gov-launch | own-role | research-allowlist | research |
| `independent-reviewer` | opus-5-5 | max | gov-launch | any-in-progress | empty | reviewer |
| `independent-auditor` | opus-5-5 | max | gov-launch | any-in-progress | empty | reviewer |

Example, the engineer's block:

```
- **Version:** 1.1.0
- **Launch default:** model claude-opus-5-5, effort high
- **Skills:** test-driven-development, systematic-debugging, verification-before-completion, retrieval
- **Launch:** gov-launch
- **Ticket:** own-role
- **Network:** empty
- **Guard class:** implementer
- **Writes:** ticket allowed_paths, never tests/acceptance/**
- **Tools:** Bash, Read, Edit, Write, Grep, Glob
- **Brief template:** brief-engineer.md
- **Return:** twelve-fields: DONE, PACKAGES, AUTH_REQUIRED
```

**Cost note:** W2-60a appends each named skill's text at launch. The engineer's four skills are about 770 lines
(the three vendored ones are long). Measure the start cost on the first launches (W2-60b's record); trim if needed.

---

## 6. (c) The gaps, and the ticket that fills each

### 6.1 The gaps

| # | Gap | State | Filled by | Order vs ACT 2 |
|---|---|---|---|---|
| G1 | Ticket lead's role file | M | **W2-33 r2** (W2-21 drops the path) | before |
| G2 | Machine-readable defaults in every role file | S (W2-60a reads 3 lines no file has) | **W2-33 r1** writes (r2 the `Skills` lines); W2-60a reads; **W2-60b** reads the rest | before |
| G3 | The CTO's role (orchestrator.md rewritten for the CTO) | S (plan §5.1) | **W2-33 r2** | before |
| G4 | Senior Engineer role file | M | **W2-33 r2** | before |
| G5 | Independent reviewer role file | S (guard hook names it) | **W2-33 r2** | before |
| G6 | Typed handoff record (CAP-22.b) | M; in W3 by DEC-841 | **W2-33 r2**, if Q4 (a) | before |
| G7 | CTO, SE and lead skills (orchestration split in three) | S | **W2-11 r2** | before |
| G8 | SE brief: kernel template + project common part | M | **W2-11 r2** (template); **CTO + owner** (`SE-common.md`) | before |
| G9 | Stream checkpoint and morning handover in the checkpoint skill | M | **W2-11 r2** | before |
| G10 | Stream playbooks | M | **W2-83a** (form) → **W2-83b re-scoped** (one per stream) | before |
| G11 | A coordination ticket per stream | M | **new W2-00a, W2-00b, W2-00c** (CTO files with tk) | before |
| G12 | The CTO's watchers | M (leads only, untracked tools) | **new W2-89** | before |
| G13 | No generated skill copy carries a version | M | **W2-11 r1** (DEC-832 item 2) | before (blocks W2-60a) |
| G14 | Kernel lead brief lags the common brief; no `brief_gaps` (W3-P02) | S | **W2-11 r1** | before |
| G15 | Judgement rules not in the kernel | M | **W2-11 r1** (brief-reviewer, audit skill) | before |
| G16 | Launchable roles hard-coded; product guard lacks the new ids | S | **W2-60b** | before |
| G17 | Effort by profile set by hand | S | **W2-60b** | before |
| G18 | The CTO's prompt is 80 KB; no three-layer duties | S | **CTO drafts prompt v4, owner approves** | before |
| G19 | `gov launch lead` / `senior-engineer`; lead write scope (probe, checkpoint) | M | **W2-21** (KPIs added) | after (hand form until then) |
| G20 | Role file location in an adopted repository (P-W2-60a-4) | M | **W2-21** (option a) | after; before EXAMIN's copy |
| G21 | W2-82 knows a lead only as `orchestrator` + ticket | S | **W2-82** (accept `ticket-lead` too) | after |
| G22 | Stream-scoped context packet (W3-P10) | M | Wave 3 (SEs use `gov retrieve`) | — |
| G23 | Test-execution, integration, UX roles (CAP-22.c) | M | Wave 3 (DEC-832); role separation documented in role files | — |
| G24 | DEC-832's four skill packs | M | Wave 3, recommended (Q5) | — |
| G25 | W2-33's ticket file and WBS card are stale against DEC-832 | — | the CTO, with the re-scope (DEC-851) | now |

### 6.2 W2-33, re-scoped (DEC-954 Q6)

**Title:** "The roles for the three layers: each role's defaults, the CTO, Senior Engineer, ticket-lead and
independent-reviewer role files, and the typed handoff record."
**Class** role-definition · **role** product-spec · **profile** STANDARD · **est.** r1 ~2 h, r2 ~9 h (est.).
**Depends on:** none (W2-21 dropped, plan §6). **Rounds declared** before they start (DEC-916): r1, r2.

**Allowed paths:**
- `template/governance/kernel/roles/**`; `.rulesync/subagents/**`; `template/.rulesync/subagents/**`;
- `.claude/agents/**` (generated through the adapter);
- `template/governance/kernel/schemas/role.schema.json`, `…/schemas/handoff.schema.json`, `…/templates/handoff.md`;
- `governance/project/roster.yaml` (entries for the new roles);
- `docs/changes/K3-CIT-P.md` (the combined CIT-P, §7), `docs/changes/W2-33-CIT-E.md`.

**KPIs, success (outline):**
- **r1:** every one of the six role files carries the defaults block of §5 at §5.3's values, all but the `Skills`
  line; W2-60a's reader reads each whole; the prose "Model tier" line is gone [DEC-839 items 1, 2, 5; CAP-35.c lite].
- **r2:** each role file names its skills (`Skills` line, §3), once W2-11 r1 has versioned the generated copies
  [DEC-832 item 2, W2-60a's CIT-E §D].
- **r1:** each role file states its version, raised with each change [CAP-24.a for role files].
- **r2:** `orchestrator.md` states the CTO (role id kept); `senior-engineer.md`, `ticket-lead.md` and
  `independent-reviewer.md` exist; each states purpose, writes, tools, defaults, authority, launch, skills, return
  and stops, matching §3 [Charter §6, MR-5, DEC-954 Q13].
- **r2:** no role file teaches a superseded rule (LEAD_CHECKPOINT, a context limit, a fixed ceiling, listing
  refusals) [DEC-866, DEC-838, DEC-847, DEC-820].
- **r2:** each role's `Guard class` matches the five-rule hook's sets and the product guard's `KNOWN_ROLES`;
  a planted mismatch is red [DEC-953 item 2, DEC-954].
- **r2:** the typed handoff: schema and template; its kinds (§4.2); the twelve fields its required core; a record
  missing a required field is refused; one live case shows a fresh agent states task, inputs, open questions and
  next step as the record does [CAP-22.b, AR-6].
- **r2:** the agents under `.claude/agents/` are generated from the role files, never placed by hand [W2-M084].
- **r2:** nothing project-specific in a kernel role file (no W2 ids, no EXAMIN, no paths of this repository).
- **CIT-P first** (the combined one), approved before any kernel file changes; the CIT-E after [CAP-33.a].

**KPIs, failure:** a role file without its defaults block that still reads; a guard-class mismatch that passes;
a handoff record without a required field that validates; a hand-placed agent file; a kernel file changed before the CIT-P's approval.

**Dropped from the card** (to Wave 3, as DEC-832 decided): the test-execution and integration roles, the UX role.
**DEC-832's four skill packs:** Wave 3, recommended (Q5).

### 6.3 Other tickets changed (outline)

- **W2-11** (re-scoped, two declared rounds):
  - r1 = its card, plus: a version in every generated skill copy (G13); `brief-lead.md` brought to the common
    brief's role-independent rules after ACT 1, with `brief_gaps:` (G14); JUDGEMENT's rules in
    `brief-reviewer.md` and the audit skill (G15). Drops `roles/orchestrator.md` from its paths (now W2-33's);
    drops the dependency on W2-10 (plan §6).
  - r2 = the three-layer method: `orchestration` split into `orchestration` (CTO), `stream-orchestration` (SE)
    and `ticket-loop` (lead); `brief-senior-engineer.md`; the checkpoint skill's stream checkpoint and morning
    handover (G7–G9). Paths gain those two skill folders, their copies and `skills/checkpoint/**`. Est. r2 ~5 h.
- **W2-60b:** adds three KPIs: effort by profile applied and recorded (G17); `Ticket` and `Network` read from the
  role file, `OWN_TICKET_ROLES` and `WORKER_ROLES` removed; the product guard's `KNOWN_ROLES` gains
  `senior-engineer` and `independent-reviewer` (G16). Paths gain `src/gov/launch/role.py` and the one line in
  `src/gov/guard/decide.py`. Est. +2 h.
- **W2-60a:** unchanged. It merges after W2-33 r1 (the version and default lines its reader requires). No role
  names a skill until W2-33 r2, which follows W2-11 r1's skill versions, so no launch is refused for a missing
  version (Q10).
- **W2-83b:** re-scoped to one playbook per stream (S0, S1, Agents, S4) in W2-83a's form; annex D's practices placed.
- **W2-21** (after ACT 2): drops `roles/ticket-lead.md` from its paths; adds `gov launch senior-engineer <ticket>`,
  the lead's write scope (probe and checkpoint records), and the adopted-repository role path (P-W2-60a-4 (a)).
- **W2-82** (after ACT 2): a lead is `orchestrator` or `ticket-lead` with a ticket.

### 6.4 New tickets

| Proposed id | Title | Class · profile | Est. | Order |
|---|---|---|---|---|
| W2-00a | S1 Memory stream: the Senior Engineer's coordination | coordination · LITE | CTO, minutes | filed when the roles land, before ACT 2 |
| W2-00b | Agents stream (S2+S3): the Senior Engineer's coordination | coordination · LITE | same | same |
| W2-00c | S4 Adoption stream: the Senior Engineer's coordination | coordination · LITE | same | same |
| W2-89 | The CTO's watchers: each Senior Engineer's state (`gov streams`) | implementation · STANDARD | 9.2 h | before ACT 2 |

(W2-88 is left for DEC-954 Q9f's any-repository memory ticket; renumber if the CTO used it otherwise.)

**W2-00a/b/c KPIs (outline):** every session of that stream's SE runs with `GOV_TICKET` = this id; its
handoffs and state are under its stream folder; it closes after its stream's last ticket, before W2-00.
Paths: `.gov-runtime/scratch/streams/<stream>/**`.

**W2-89 KPIs (outline):**
- `gov streams` (read-only) shows each stream: its SE's state and since when, whether its process is alive
  (launch record), the leads running, released tickets not started, and the last return [DEC-954 Q13b];
- it derives the signals of §3.1 at thresholds read from a project setting;
- `gov streams --watch` waits and exits at the first new signal, so the CTO's background wait wakes it;
- fail closed: an unreadable record is `UNREADABLE`, never `working`;
- it reads W2-33's `STATE` handoffs; it writes nothing; it is pinned with ACT 2.
Product code only: CIT-E, no CIT-P. Depends on W2-33 r2 (the handoff schema).

### 6.5 Order (estimates, unmeasured)

1. You approve this spec. The combined CIT-P is drafted (~3 h), reviewed independently (~1 h), sent to you.
2. On approval: W2-33 r1 (~2 h) → W2-60a merges and closes. W2-11 r1, W2-60b and W2-83a run in parallel.
3. Then W2-33 r2, W2-11 r2, W2-83b, W2-89. The CTO drafts prompt v4 and `SE-common.md` (one package for you).
4. The CTO files W2-00a/b/c. The roles have landed when W2-60a, W2-60b, W2-11, W2-33, W2-83b and W2-89 have
   closed and prompt v4 is approved.
5. ACT 2 (one re-pin), with memory. Then the three layers start in new sessions.

Est. roles landed **11-04 to 11-06**, against the plan's 11-03: the spec, W2-89 and W2-83b add about one to two days.

---

## 7. The combined CIT-P for the K3 tickets (DEC-954 Q7)

One proposal, `docs/changes/K3-CIT-P.md`, written by a product-spec worker under W2-33 from this spec once
approved; reviewed by a fresh independent auditor at `max` with JUDGEMENT.md; approved by you before any kernel
file changes. Each ticket then writes its own CIT-E. What it changes in the kernel:

**W2-60a.** No kernel file. It makes the role files load-bearing: every launched worker starts with its role
file's text and its named skills appended, its model and effort from the role file's default line, connectors,
user-level agents and model-side memory kept out, and a launch record per session. Impact: a role file without
its default line refuses every launch, so it merges only after W2-33 r1. W1-46's and W1-28's launch projects
must copy `.claude/skills/` too once a role names skills (its CIT-E §D.3).

**W2-60b.** No kernel file. The launcher's set of launchable roles, ticket binding, network profile and effort by
profile come from the role files, so a new role is a file, not a code change. The product guard learns
`senior-engineer` and `independent-reviewer`. Each session gets one record (model, effort, tokens, cost, turns),
which also measures the SEs' memory and cost on day 1 (plan §5.3).

**W2-11.** The brief templates and skills. Every template and skill carries the twelve fields, the payload-after
rule, the two-refusal stop, Policy 2 and the decision-record rule; supersession is swept. Each generated skill copy
carries its kernel version. The test-design skill states proportion, red-first and the test kinds. The judgement
rules reach the kernel's reviewer brief and audit skill. The lead's brief template catches up with the common brief,
with `brief_gaps`. Round 2 splits orchestration into three skills, one per layer, adds the SE's brief template and
the stream checkpoint with the morning handover.

**W2-33.** The role files. All six gain the defaults block; `orchestrator.md` becomes the CTO's; three new role
files (Senior Engineer, ticket lead, independent reviewer); a role schema; the typed handoff schema and template;
the generated agents and roster entries. It restores CAP-22.b to Wave 2, if you choose Q4 (a).

**W2-83a, if you choose Q9 (yes).** The playbook form, its schema in `gov check`, and the adopt step: the same
owner turn instead of a second CIT-P.

---

## 8. Questions for the owner

| # | Question | Recommendation (confidence) |
|---|---|---|
| Q1 | Approve this spec as the basis for W2-60b, W2-11, W2-33 and W2-83? | Yes (high) |
| Q2 | Role ids: the CTO keeps `orchestrator`; the SE is `senior-engineer`; `ticket-lead.md` lands now and leads switch to it with W2-21; the reviewer gets its own `independent-reviewer` file? | Yes to all (high). Renaming the CTO's id would touch the guard, hooks, trailers and records for no gain |
| Q3 | Defaults in W2-60a's line form (one source, built and tested), or a YAML front matter? | Line form (medium). Front matter would rework W2-60a's reader and tests after its merge |
| Q4 | The typed handoff (CAP-22.b): DEC-832/DEC-841 moved it to Wave 3; the approved plan relies on it. (a) apply now in W2-33, with W2-49's Contract v4.2 note keeping CAP-22.b in Wave 2; (b) defer, using the twelve fields only; (c) re-baseline | (a) (medium-high): the SE-to-CTO handoff and the watchers need it. CAP-22.c and UX stay Wave 3 |
| Q5 | DEC-832's four skill packs (backend, data, API, security): Wave 3, or kept in W2-33? | Wave 3 (medium): neither the three layers nor EXAMIN's copy needs them |
| Q6 | The CTO is the only writer of the main tree (claims, tickets, register, merges, closes); an SE writes no tracked file and asks by handoff? | Yes (high). It differs from plan §5.1 ("SE claims"); one writer keeps closes clean |
| Q7 | The watchers as a product command, `gov streams`, pinned with ACT 2; or a project tool? | Product (medium): adopted products inherit it; about 9 h |
| Q8 | The outgoing CTO starts fresh SEs at about 07:05, so no stream waits for the owner's morning? | Yes (medium) |
| Q9 | Fold W2-83a's CIT-P into the combined one (one owner turn)? W2-89 is product code and needs a CIT-E only | Yes (medium) |
| Q10 | W2-33 and W2-11 each run in two declared rounds; W2-60a merges after W2-33 r1; `Skills` lines only after W2-11 r1 has versioned the skill copies? | Yes (high): W2-60a otherwise refuses every launch |
| Q11 | Coordination ticket ids W2-00a/b/c (three SEs: Memory, Agents, Adoption, as plan §5.3) and W2-89 for the watchers? | Yes (medium) |
| Q12 | The orchestration skill split into three (CTO, SE, lead), so each layer loads only its part? | Yes (medium): less context per session, clearer method |

---

## 9. Sources, discoveries and what is unmeasured

**Sources read:** the owner's texts (DEC-953, DEC-954); `contract.yaml` (CAP-22, 24, 33, 35, 36, 37, 47, 59, 61);
Charter v5 §4–§6; the six role files and `.claude/agents/`; the ten skills; the templates; the project briefs;
the prompt (§0–§15, Appendix A); `roster.yaml`; `path-map.yaml`; the ten tickets of §2.7; PLAN-W2-DEC953 §2, §5, §6;
the company map; DECISIONS-IN-FORCE; the register (DEC-832, DEC-839, DEC-841); `launcher.py`; `decide.py`;
the five-rule hook; W2-60a's branch (`role.py`, its CIT-E §A–§E); W3 parking (W3-P02, P09, P10).

**Discoveries:**
- W2-33's ticket file and WBS card still carry the scope DEC-832 removed; DEC-832's packs are not in it (DEC-851 miss).
- W2-60a's CIT-E §D gives W2-11 the six role files' default lines, but W2-11's paths hold only `orchestrator.md`.
- No generated skill copy carries a version: once a role names skills, W2-60a refuses its launches.
- W2-21's paths and W2-33's both cover `roles/ticket-lead.md`.
- The product guard's `ticket-lead` has no write scope, but leads commit probe and checkpoint records.
- The five-rule hook's install `ask` is keyed to `orchestrator`, so leads (today `orchestrator`) get an ask, not a refusal.
- `gov retrieve` answers `STORE_MISSING` in the main tree today; this spec was built from direct reads.

**Unmeasured (estimates):** an SE's memory and cost; the watcher thresholds; the start cost of appended skills;
the lead-hours of §6.4 and §6.5; the date the roles land.

END OF ROLES-SPEC-1


## 10. The owner's answers (DEC-957, 2026-10-30)

- Q1 to Q4, Q6, Q7, Q9, Q10 and Q11: approved as recommended. Q6 stands until the owner decides from the roles research session; the push stays the owner's.
- Q5: the domain skill packs come in Wave 2, as skills: frontend, backend, UI/UX, DevOps, security, API and the like are engineers, each loading the engineer role plus its domain skill.
- Q8: a fresh session every morning for every orchestrator, the CTO included.
- Q12: the CTO loads its own skill at launch and has every other role's skills on demand; Senior Engineers and leads load their own part.
- Effort: the CTO and the Senior Engineers at high; the highest effort only for reviewers and auditors, when needed.
- A research session now establishes a software company's roles and skills, from the CTO down (the QA engineer among them), who integrates and who may push, and benchmarking as a research skill; it reports to the owner, and the roles land in Wave 2.

- **DEC-957 (owner, standing, 2026-10-30): the work order, installs and the escalation rubric.**
  - **The work order, as in a software company:** product-spec develops the spec (with research, the Senior Engineer, the CTO and the owner); the spec's agreed KPIs drive the independent test designer, who builds the tests and never reads the code; the engineer, whatever its domain (frontend, backend, UI/UX, DevOps, security, API: the engineer role plus its domain skill), builds the code to fulfil the spec and its KPIs, never to make the tests pass: it may run the acceptance tests and see only pass or fail, never read them, and its test-driven development means its own unit tests; the QA engineer (today's independent auditor) alone reads both, changes neither, writes only its findings report in its allowed path, and escalates an unresolved bug to the Senior Engineer, then the CTO and the owner.
  - **Installs:** only the CTO's own session may ask the owner. Every other session, leads included, is refused by the guard and raises the install as a P1 escalation in its return.
  - **The escalation rubric:**
    - **P3, the Senior Engineer decides and logs it:** reversible; inside one ticket's scope and paths; no change to the spec, the KPIs or any standing decision; no effect on other streams; a delay under half a day.
    - **P2, the Senior Engineer decides, the CTO approves:** touches another stream or shared code; changes a ticket's scope or KPIs within the approved spec; changes the plan's order; delays a milestone by up to a day; revises older tests under an existing decision.
    - **P1, the lead and the Senior Engineer recommend, the CTO amends or escalates, the owner decides:** changes the spec, the Contract, the Charter or a standing decision; weakens any of the five guard rules or anything that fails open; irreversible or destructive; secrets or security; cost, installs or paid services; memory's target or acceptance; EXAMIN's go; any ACT; a milestone slipping more than a day.
    - **Emergency:** a secret exposed, a risk of losing data, the disk below its floor, or the guard failing open: stop the affected work at once, then P1.
    - Until the three layers start, the CTO (this orchestrator) holds the Senior Engineer's part.
