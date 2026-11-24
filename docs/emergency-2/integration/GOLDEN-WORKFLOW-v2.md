# Gov OS: the golden workflow, v2

**Status:** approved by the owner as the spine (DEC-1244 WF (a), 24 November 2026); it replaces his draft,
`docs/emergency-2/GOLDEN-WORKFLOW.md` (22 November), which stays as he wrote it until item 5-3 of the integration plan
archives it with a pointer. This file is that draft with its "Today" column replaced by the corrected text of
`GOLDEN-WORKFLOW-CORRECTIONS.md` §1 (DEC-1241 C-ALL (a)), its rules corrected as §2 says, and the owner's answers
of 24 November applied (DEC-1241 P-1 to P-10, G-3, G-4, G-8; DEC-1242 where a card changes a step's text; DEC-1244
X-1 to X-3 and Q-1 to Q-14 where a card changes a step's or a rule's text). Every change has a line in the change log at
the end, with its card id.

This file is the spine of Gov OS: the Charter and the Contract are rebuilt around its
steps, and every document, role, skill, template and Contract item that says something else is brought into line or
archived. It extends the golden rule: the golden rule says how work is judged; this file says how work flows.

**How to read it:** each step says what happens, what code holds (deterministic), what stays with an agent (a job with
fixed inputs, a fixed output form and a code check of that form), where it stands today, and where it must be.
**"Today" is typed until the enforcement field exists (A-23); once it exists, the column is computed from that field and
no one types it (P-5).** Until then the CTO re-reads it at each release. The "Today" text below is the corrected text
of `GOLDEN-WORKFLOW-CORRECTIONS.md` §1, read at `5617f2e5e` (22 November). A bracket "[since ...]" marks a fact I
checked at HEAD `461c214a5` (24 November) that the merge of `e2/fixes-015a` changed after that reading.

**The code names in this file.** The landing is `gov land` (P-10); `gov queue` stays as an alias for one release and then
retires. "Queue" means only the dispatcher's work queue.

---

## 0. The rules everything below rests on

Each rule is followed by **Today**, the corrected claim about the code (CORRECTIONS §2). A rule with "verified" has no
correction.

1. **Value first.** The product's value is the work; governance serves it and is sized by it. Practicality and security
   work never become the core of the work.
   *Today: verified; no code claim.*
2. **The threat model.** Gov OS guards against honest mistakes and drift in ordinary work, not an adversary. It catches
   and corrects; it does not prevent. No guard, no sandbox, no permission prompts, set in each repository's settings
   (the kit carries the line, A-27); two denies only (git push and sudo, both the owner's).
   *Today: the two denies hold in Gov OS's settings and in the kit. "No permission prompts" holds only where the
   launcher passes `--permission-mode bypassPermissions` or Gov OS's `defaultMode` is set; the kit has no `defaultMode`,
   so an adopted repository's own sessions prompt (A-27).*
3. **The golden rule.** A finding blocks only if ordinary work hits it and it fails open or loses work. A review happens
   only for a red test, a failed landing or merge, or a feature that does not work as intended; **at most two rounds, in
   code (P-9)**, then the owner once, with options. Green work needs no review.
   *Today: the rule is right; the code has not caught up. `ESCALATION_AT = 3` (`close/state.py:17`) allows a third
   round, and the `qa-engineer` and `ticket-lead` role files still ask for a per-ticket review (A-18).*
4. **Deterministic where it can be, specified where it cannot.** Whatever can be decided or checked by code is decided
   or checked by code: at the launch, at the landing, or by a scheduled check run by the one scheduler (W15), never by an
   agent's goodwill. Whatever must stay with an agent is a job with fixed inputs, a fixed output form and a code check of
   that form. What cannot be code is the creative content (writing code, tests and specs, judging, planning); it stays with
   agents inside fixed forms that code checks (P-6).
   *Today: verified, with one note. The principle matches the code that is built. "A scheduled check" had no scheduler:
   the crontab holds no weekly or daily line. P-1 names the scheduler in W15.*
5. **Memory first.** Every agent asks memory before it greps or reads; the brief carries the memory bundle uncut; the
   agent searches once more in its own words.
   *Today: `gov retrieve` cuts its bundle at 6,000 tokens (`retrieval/retrieve.py:48`) and `brief/memory.py` carries
   index lines, not bundle text (A-11); memory use is a typed log, and helpers log no role (A-35). "Uncut" is a build item.*
6. **The work rubric.** A ticket is a feature: it has a spec and KPIs, and carries `kind: feature` (R-3). A known bug in
   an existing feature is a fix, recorded under its owning ticket, its failing test written first. Records, docs,
   configuration and kernel text are chores, committed directly; a chore that touches code lands through `gov land --direct`
   (T-2). **A chore is whatever changes no behaviour and keeps the tests unchanged and green; there is no time box (R-1).**
   A new KPI line on a closed feature is a new ticket.
   *Today: feature, fix and chore are named in code only for the fix record. The failing test first, the fix section and
   the chore are text: the fix section is by hand (`ticket.md:65` says the opposite, A-15), and `--direct` does not exist
   (A-16). The ticket has no `kind` field; its `class` is a free string.*
7. **The model and effort rubric.** Opus only for the long-running sessions that orchestrate: each product's CTO (the
   master orchestrator) and a senior engineer per stream (the sub-orchestrator). Every other agent runs Sonnet, critical
   work included. A wide audit the owner asks for runs on Opus. **Model and effort are set by role in one table, and
   criticality does not vary the model (R-4, R-5):** CTO and senior engineer high; ticket, fix and chore leads medium; every
   other role high; changed only by the owner. No session chooses its own model or effort; a change comes to the owner first. **One vendor and the owner's Claude Code
   plan only for now; API keys, other subscription plans and review by a second vendor are Wave 3 features (Q-8, Q-10;
   §4).**
   *Today: built in `gov launch` (the role files carry the table, the launcher takes the model by role and refuses Opus or
   Fable outside the owner's audits). The sessions the start scripts launch still choose their own (W8); until W8 the
   scripts must match the table exactly (T-10). A user-level setting also sets the helper model.
   [since: no model outside the rubric, leads at medium in `gov launch` and Sonnet written into every helper spawn are
   merged (015a F13, F14, F19); the effort table as one file is not built.]*
8. **Decisions, by the escalation rubric already approved.** Every decision is taken at its level, and the levels
   combine code and judgement:
   - **The lead (P3)** decides and records what is reversible, inside its ticket, and changes no spec, KPI or standing
     decision; a fix with its failing test.
   - **The CTO (P2)** decides shared code and work across streams, the order inside a planned wave, a red landing and
     whether a review is called, kernel text, and an install inside the work's scope and the machine's capacity.
   - **The owner (P1)** decides features, specs and KPIs; a ticket added to or removed from a planned wave; the
     Contract, the Charter and standing decisions; data and measurement; anything irreversible outside a worktree; a
     secret or a paid service; a model or effort exception; a review not converged after two rounds; a release whose
     content he has not approved. Pushes to GitHub and sudo stay his. Releases whose content he has approved are cut by
     the CTO, by code.
   - **An emergency** (a secret exposed outside the machine, a risk of losing data or work, the disk below its floor,
     the machine over its gate and not recovering) stops the work, then pushes the owner.
   - **What code holds:** each decision is a structured record. **The author states facts (what it touches, whether it is
     reversible, where it acts); code computes the level from them (R-6)**, refuses a decision taken below its level,
     routes owner decisions to the decisions page (a stopper at once, with a push, at any hour; the rest in the morning
     brief, which also lists every push), writes the owner's answers into the register, and requires the basis line and
     the enforcement field on every new rule.
   - **What stays with an agent:** framing the question, the options, their costs and the recommendation; and the lead's
     or the CTO's own choice at P3 and P2. Each is written in the record's fixed form, so code can check it.
   *Today: only the basis check (`gov decisions basis`, typed) and the in-force digest exist. Not built: levels computed
   from the record, refusal below the level, routing to a page, pushes, `gov decisions answer`, the enforcement field.
   The owner-approval check is switched off (`check/authority.py:44` skips `ACTIVE_UNAPPROVED`). The first slice (the
   record's fields, the computed level, the refusal, `gov decisions answer`) is approved (DEC-1236, T-1); page and push by
   hand meanwhile.*
9. **The machine.** Work is sized to the machine it runs on; **a machine too small to operate is refused with a reason
   at a launch, at adoption and at install (P-8).**
   *Today: a launch is refused with a reason when the resource gate is shut (exit 3), and an embedding job where there is
   no GPU. There is no check at adoption or at install.*
10. **Context.** Orchestrators start fresh each morning from a handover in the checkpoint form, which the launcher reads
    (P-3, T-13); helpers start from a written brief, never as a fork; old sessions are not resumed. Every session gets
    only the tools its role needs.
    *Today: never a fork, by code (`agent_model.py` refuses a fork). The handover and the role's tool list are text:
    the handover has no form or code check, and no per-role MCP list exists.
    [since: no claude.ai connectors in any session, merged in 015a F1.]*

---

## 1. The workflow, step by step

| # | Step | What happens | Held by code | Stays with an agent | Today (typed until A-23; then computed, P-5) | Must be |
|---|---|---|---|---|---|---|
| W1 | **Start or adopt a repository** | A new repository, or an existing one, goes through adoption: what it is, what it holds, what it brought in, its path map, its specs audited, its legacy retired, its memory built, its verdict. A machine too small is refused with its reason (P-8) | `gov adopt`'s stage chain (A0 to A10, AS, the verdict); **the path map as the one source: A3 refuses a map that leaves a tracked path in no namespace or in two, and adoption and `gov update` keep it current (G-8)**; the kit's settings (the two denies, no connectors, the no-prompt mode, the model hook) and the golden rules at the head of CLAUDE.md and AGENTS.md | The judged stages (A5, A7, A10, the spec audit's answers, the verdict) | Built, except the verdict stage (in flight on `e2/d1-verdict`, not merged; A-21) and the imports step (a fourth stream starts when EXAMIN's fresh 80 passes, X-3); three capabilities named as exceptions. The kit's settings carry the two denies; the connectors key, `defaultMode` and the model hook reach adopted repositories only after A-27. [since: the connectors key is in the kit, 015a F1.] | Every stage on the path; the verdict recorded; imports classed use, absorb or study; the kit complete (A-27); a machine too small refused (P-8). **Fully on by the integration's exit, imports included (X-3)** |
| W2 | **Build memory** | The repository's records, code and documents are indexed: words, meaning and the record graph; stale and legacy material kept out of default memory | Store build and rebuild; the graph's links from front matter; namespaces and their index policy | None | Built; the route that keeps stale and legacy documents out comes in 0.1.6. A path classed in two namespaces (W2-81's A4) is a fix under W1-41 (DEC-1238 (1c)) | As today, plus the route |
| W3 | **Keep memory current** | Every commit refreshes memory; a failed refresh retries and is checked; the embedder is always up. Same tool as W2 (P-4) | The refresh hook after commits, **installed by the product in Gov OS and through the kit (G-4)**; the retry; a check that the store is at HEAD; the embedder started at boot and brought back if down | None | The refresh runs; a failed refresh is still not retried; the embedder start at boot was added as a cron line, but it is a scratch script outside the product. The hook sits in `.git/hooks`, untracked, so it is in no repository | **First in the integration plan (G-1):** retry, the store checked current, before anything relies on memory; the hook and the boot start installed by the product; self-healing (W2-207) |
| W4 | **Measure memory** | Weekly, a fresh 80 questions (40 visible, 40 hidden) is written and judged end to end at 95 % or better; the figure is stamped with release, commit, models and rule | `gov memaudit`: declare, preflight, the hidden-set scan, the judge, the stamped figure; run by the scheduler (W15) | Writing and checking the questions; reading; grading (Sonnet), each with a fixed form | Built; typed by hand; the stamp comes in 0.1.5. No crontab line runs the measure. The reader and grader are Sonnet. [since: the stamp (release, commit, models, rule) is built, 015a F15.] | Scheduled weekly; stamped; the result in the digest |
| W5 | **Decide** | Every decision is taken at its level by the escalation rubric (rule 8): the lead, the CTO, the owner, or an emergency. Owner decisions are batched into one page; his answers are written into the register by code | The decision record's stated facts set its level by code (R-6); a decision taken below its level is refused; routing to the page and the pushes; `gov decisions answer` (fail-closed: a missing answer is no); the basis check; the owner-approval check; the enforcement field | Framing the question, options, costs and recommendation; the lead's and the CTO's choices at their levels, each in the record's fixed form | Built: the basis check (typed) and the in-force digest. Not built: levels computed from the record, refusal of a decision below its level, routing to a page, pushes, and `gov decisions answer`; the owner-approval check is switched off (`check/authority.py:44`) | Levels computed from the record's facts; refusal below the level; by page; every check on the path |
| W6 | **Trace impact** | A change to a decision, a spec or code shows which specs, tickets and tests it affects | The record graph, the path map, the code and test graph; `gov impact --changed` at the landing, into the close record (T-11), and in planning when the plan step is built; **with the path map and the code and test graph, the inputs of the landing's test selection, made trustworthy first (X-1)** | None | Partly. Code that traces a decision or a spec to the specs, decisions, tickets, tests and code it affects exists (`gov impact`) but nothing calls it and it exceeded 106 s on a record-only id; the landing's selection runs by code and traces code to tests only. No code compares a ticket's `[Kn]` lines with its spec's K-lines; no test-to-ticket trace exists | One trace, used by planning and by the landing |
| W7 | **Plan** | The Contract (features, behaviour, KPIs) first; then the WBS, the waves with a set list of tickets, and each ticket filled from its template, the path map and memory. A product's Contract and planning go ahead before the integration is complete, each for the owner's yes, in the forms below; only executing the plan waits (X-4) | The ready check (no unfilled slot; the ticket's KPIs match its spec; **its read and write paths fall in the path map, G-8**); the wave form; the rubric's class (`kind`) on every item; **a new feature ticket names its spec (`specification`; optional on old tickets, Q-2), starts each KPI line with a stable id (Q-4), copies the spec's line word for word with code named only in its `verify` field (Q-5), and a fingerprint of the list catches drift (Q-4)** | Writing the spec and KPIs; planning the waves (each with a fixed form). **The nine-part form is the spec and OpenSpec holds the living behaviour beside it, each K-line naming its requirement (Q-3; settled for good when EXAMIN's Contract is drafted)** | Partly: forms exist, the checks are typed or missing. The ready check exists in `gov brief` and `gov readiness`, `gov plan`, `gov discover` and `check_spec.py` exist; each is typed, and Gov OS plans by hand. "The ticket's KPIs match its spec" is not checked by anything | Every plan item checked by code before work starts, at `gov brief` and at launch (G-3) |
| W8 | **Launch** | The dispatcher picks the next work by its dependencies; the load balancer sizes it to the machine; each session starts from a filled brief, with the memory bundle uncut, its model and effort by the rubric, only its role's tools, a claim and a launch record | `gov launch` and the run-time tool (dispatcher, load balancer, pause, spend, claim, record). **Every brief, for a ticket, a fix or any agent, is generated by code at launch from its sources (the ticket's KPIs, spec, read and write paths; its template; the path map; memory; the commands map), never written or edited by hand; a launch is refused if a link is missing or broken; plan, brief, launch and landing read the same ticket fields (G-3).** The path map gives each job's paths (G-8) | None | Partly built, off the path for leads and the CTO. `gov launch` takes the model by role and refuses Opus or Fable outside the owner's audits, passes `--strict-mcp-config` and the resource gate; leads start from `start_lead.sh`, the CTO from `start_cto.sh`, audits from `start_audit.sh`; the cron runs the old scratch dispatcher, and `gov dispatch` is typed only. There is no per-role tool list and no launch record in Gov OS or EXAMIN since 16 November. [since: pause stops every starter; leads at medium and no model outside the rubric in `gov launch`; no connectors in any session; 015a F1, F10, F13, F14, F19.] | Every session started by `gov launch` from a generated brief (0.1.6); the run-time tool live (W2-207). Until then the start scripts' models and efforts match the rubric exactly (T-10) |
| W9 | **Test first** | The independent test designer writes the acceptance tests from the KPIs only; each KPI line has at least one test that is red on the base. A case that must stay green (a guard) is allowed only when it is marked `guard` (T-3). **Each acceptance test carries its KPI line's id in its code, a marker; the README map is generated from the markers, never written by hand (Q-12)** | Test authorship at the landing; red on the base; **the markers and the generated map; `gov accept` fails a ticket line no marker names, for tickets created from the change on, older ones exempt (Q-6)** | Designing the tests | Authorship checked at the land (when `gov queue` is used; hand merges bypass it); red on the base not checked | Both checked (0.1.6) |
| W10 | **Build** | The engineer builds until `gov accept` is green, then returns its result in the fixed form. **The same failure three times stops the loop (Q-7, W11)** | `gov accept`; the return checked (its fields, its branch, a clean worktree) | Writing the code | `gov accept` is typed by agents and runs at the land. The helper's 12-field return is checked by the SubagentStop hook (with its three bugs, 015a F12); the lead's return has no form or check (A-7). [since: F12 merged.] | The return checked by code (0.1.6), the lead's included |
| W11 | **Land** | `gov land` merges on a scratch copy, **runs the tests the product's impact selection picks on the merged result, never a hand-picked set, Gov OS's own hand merges included (X-1)**, checks paths, authorship and **that the path map still covers every path the change adds exactly once (G-8): a path it does not hold exactly once is refused, naming the exact line to add, and a record-only document inside an already-mapped folder passes with a notice (Q-1)**, refuses a dirty worktree, records base reds, lists the impact trace and writes the close. On a red it writes the red's record in the diagnosis form, one cause per red, and the CTO decides who fixes (T-12). **The whole suite runs only for a release and weekly; a red it finds that the selection missed is a selection bug, logged in the findings log and fixed (X-1). The same failure three times stops the build or fix loop: the CTO finds the root cause (the brief, the spec or KPIs, the path map, the test, the environment or a tool), fixes it at the root and records it in the findings log (Q-7).** `gov close` is retired and two review rounds are held in code (P-9) | `gov land` (`gov queue` an alias for one release, P-10); G1, G2 and G3 in the after-step (DEC-1242 T-9); a ticket outside the planned wave refused (R-2); **the selection and the three inputs that make it trustworthy, built first (the path map's exact coverage, the code and test graph current, `gov impact` at the landing; X-1); the stop at the third identical failure (Q-7)** | Diagnosing a red, in a fixed form (the CTO decides who, T-12); **the root cause at the third identical failure (Q-7)** | Built and first used: `4f779086f` (`batch: merge DAEO-j9z6`) is Gov OS's first landing through `gov queue`; the next, `models-rubric`, was landed by hand merge because the queue refused it on a target read from a README map row's notes (`FILE_GONE`; I-1, fixed in 0.1.5). No `governance/project/queue.yaml` exists in Gov OS. The dirty-worktree refusal is built (`QUEUE_WORKTREE_DIRTY`). No code calls an auditor on a red; the diagnosis has no form. **`fixes-015a` was merged by hand and tested on a hand-picked set, so the selection never ran and 95 reds followed in the full run (I-14).** | Every landing through `gov land`, proven on the scratch repository and in EXAMIN; Gov OS moves onto it when the owner decides (DEC-1239 (4)). **Until then every Gov OS landing still runs the product's selection (X-1)** |
| W12 | **Fix and chore** | A fix runs under its owning ticket, failing test first, and the landing writes its record and its `## Fix:` section. Records and docs are committed directly; a chore that touches code lands through `gov land --direct` (T-2) | `gov launch --fix`, `--chore`; the landing writing the fix record and section (A-15); `gov land --direct` with a notice when a chore changes `src/**` or `tests/**` (R-1) | Writing the fix | `gov launch --fix` and `--chore` exist and the queue writes a fix's record; **`gov queue --direct` does not exist** (the queue's flags are `--onto --timeout --dry-run --select --out --full`); nothing in Gov OS uses any of them | On the path (0.1.6) |
| W13 | **Release** | The release acceptance passes (the Contract's enforcement checks, the proving run, the adopted repositories' memory measures, the full regression record for the commit); the CTO cuts the release for content the owner has approved, re-pins with self-rollback, and pushes the owner. Every release prints the three measures (P-6); **until the exit none is refused for them, and from the exit a release below the baseline X % the owner sets stops for his decision, an exemption with its reason or a new X (Q-14)** | The release gates, the acceptance record, the re-pin, the authority file; `gov release --patch` calls the full regression run for the commit when it needs the record (P-2, T-8) | None | 0.1.5 is the owner's last manual cut. The acceptance is not built for a full release: `gov release` (full) has no acceptance gate (A-13); the gates G0-G4 are the patch release's only, switched off by `patch_releases: off`; G2 reads a nightly record while the nightly is off. The re-pin with self-rollback is built | Every approved release cut by code |
| W14 | **Update adopted repositories** | An adopted repository takes the new release at a quiet point, keeps its own edits, and can roll back in one command. A machine too small is refused at install (P-8). The update checks the path map's coverage | `gov update`: the three-way merge, the check after (doctor and the path-map coverage), the rollback | None | By hand: `gov update` is built with the three-way merge, the after check and rollback; it is typed by the owner; the session-start advice reaches only `compact`, `clear`, `resume` | Automatic at a quiet point (W2-207, W2-209 slice b) |
| W15 | **Run** | Under everything: the work is dispatched and sized, stalls are caught, the owner is pushed only when needed, usage and context are measured daily. **When nothing has moved for 3 hours the scheduler pushes the owner itself, by code and with no agent woken, saying what waits and on whom: on the owner (a decision, a cut, a push) or on stuck work (X-2).** **One scheduler in the product, `gov dispatch pass` run by one cron line, with its schedule in configuration, runs every scheduled check (P-1, T-5).** **Orchestrators hand over each morning: the handover is written in the checkpoint form (`gov checkpoint`) and the launcher reads it (P-3, T-13)** | The run-time tool and its scheduler; **the 3-hour stall push (X-2)**; the daily usage and context figures; the handover form checked by the launcher | The orchestrators' coordination; writing the handover | Slices 1 to 3 built; old watchers still live: the minute cron runs the old dispatcher and three scratch watchers run now. `deadman.py` is imported by the dispatcher with no cron line. **The 3-hour push is the CTO's cron rule (`tools/stall_check.sh`, DEC-1243 (4)) until the scheduler holds it** | One run-time tool live (W2-207), running every schedule, **with the stall push sent by code (built beside the scheduler, X-2; the finer thresholds for a looping session come later)** |
| W16 | **Weekly hygiene** | Once a week: the memory measure, the doctor, the basis review, the full regression record as a safety net (P-2; with a release, the only time the whole suite runs, X-1), the clean-up; a secrets scan only before a repository goes public or is shared | The schedule (W15) | None | Unscheduled: the crontab holds the minute tick, the hourly backup and `@reboot` only; every nightly, morning-check, sweep and operator line is commented out; lefthook is not installed | Scheduled |

---

## 2. The jobs that stay with agents

Every job is started by `gov launch` from a brief generated by code (G-3), receives only what its brief names plus the
memory bundle, returns a fixed form, and is checked by code before anything relies on it. Audit 4's List B (§3) specifies
each: spec and KPIs; test design; implementation; a fix; a chore; diagnosing a red; an auditor's verdict; research;
planning a wave; the memory measure's writing, reading and grading; the ticket lead; the CTO; the senior engineer;
adoption's judged stages. A hand-off may rely only on what code has checked.

---

## 3. How Gov OS is assessed against this workflow

- Every Contract item and every standing rule carries its enforcement: built or not; held by code on the path, by code
  off the path, checked after (by itself or only when typed), or by a named agent job; why not, and when.
- **Every release's acceptance prints three measures, each against the baseline of 22 November (P-6):**
  1. *Contract items by class:* 21 % on the path, 13 % off the path, 31 % checked after, 19 % judgement, 16 % not built.
  2. *Steps (the flow):* 1 of 16 fully held by code, 11 partly, 4 off; 41 % counting partly as half.
  3. *Tools (the tool map's rows):* 29 % on the path, 21 % partly, 49 % not (102 rows).
- **The aim is as much in code as can be.** The integration's exit needs **at least 90 % of the steps (the flow) held by
  code**: 15 of the 16 steps, since 90 % of 16 is 14.4. Judgement stays only where the work is creative, and then it is
  specified.
- **The release floor is a baseline the owner sets at the exit (Q-14).** Until the exit every release prints the three
  measures and none is refused for them (today 1 of 16 steps is fully on, so a refusing floor would block every release).
  At the exit the owner sets X % from what was reached (90, 95 or 88). From then a release below X % stops for his
  decision: an exemption for that release with its reason, or a new X. Code holds the comparison; he holds the exception.
- **A step held by an engine's graph counts as held by code only if the engine is pinned and its behaviour is checked by
  Gov OS's own test (Q-9).** A rule only: no engine is adopted (Q-13).

---

## 4. What this file changes

- It is the spine of the Charter and the Contract: both are rebuilt around these sixteen steps and ten rules.
- Every piece of information that says otherwise (roles, skills, templates, briefs, docs, the kit's head, old decisions
  still read as current) is brought into line or archived; nothing old and stale is left to be read as current.
- Every tool the work depends on is part of the product, so adopted repositories get it; tools outside the product are
  absorbed, replaced by the product's own, or retired.
- **The test for "outside the product" (P-7):** a file or setting is outside the product if `gov update` would not carry
  it to an adopted repository. Today that is Gov OS's one live git hook, every cron line, the start scripts, the model
  hook in some repositories, and the scratch folder. *Absorbed* means the release carries the tool's knowledge, not always
  its files. **Third-party programs** (Ollama and its models, Claude Code, Python, git, node, the binaries) are not
  shipped: the release pins their versions, checks them in `gov doctor`, starts them when needed and refuses with a reason
  if one is missing. **The release carries** the git hook, the scheduler and its one cron line, the model hook, the
  project settings and the start of every session. **Left out on purpose:** the owner's user-level settings, keys and
  secrets; Gov OS's own development records (its register, briefs, audits); the hidden question sets; the dead scratch
  files and the duplicated tools.
- **Each duplicated tool retires on the day its product tool takes over, and the plan lists that day (G-5).**
- The heads of CLAUDE.md and AGENTS.md point to this file beside the golden rule: whatever contradicts it is wrong.
- **Wave 3, not in this workflow (Q-8, Q-10).** Work runs on the owner's Claude Code plan and one vendor. Using API keys
  or other subscription plans, and review by a model from a second vendor, are two features for Wave 3, built and
  trialled then (how each session gets its key or plan, how its cost is counted, how a hidden-set run stays on the
  machine), each paid service approved by the owner. When they are built they are added to rules 7 and 8 and to W8.

---

## 5. The tool map

This file says what each step does. Which tool does it, and how the steps join, is in two files made from the code. This
section does not copy them.

- **`docs/emergency-2/integration/TOOL-MAP.md`:** one row per tool, script, hook, cron line or schedule that does Gov OS's
  work, inside the product or outside it (102 rows), with its disposition (absorb, replace, retire) and the five rules
  checked (§2 there).
- **`docs/emergency-2/integration/RECORDS-MAP.md`:** one row per record the tools pass along (its form, who writes it, who
  checks it and when, who reads it next), the 28 hand-offs between steps, and the path map (§3 there).

**Where each step's rows are** (one tool column for W2 and W3, because one tool builds and refreshes memory, P-4):

| Step | Tool-map rows | Main tools | Records-map rows |
|---|---|---|---|
| W1 | 1 to 4 | `gov adopt`, `gov adapters`, the kit's settings | §1.4 adoption records; §3 path map |
| W2, W3 | 5 to 13 | `gov rebuild` (builds and refreshes), the git hook, the embedders | §2 hand-offs 4, 5 |
| W4 | 14 to 16 | `gov memaudit` | §1.4 memory measure |
| W5 | 17 to 21 | `gov decisions`, decision templates | §1.3 decision, register entry, package |
| W6 | 22 to 29 | `gov impact`, the graph, the landing's selection, `gov links` | §2 hand-offs 9, 10 |
| W7 | 30 to 35 | `gov plan`, `gov readiness`, `gov discover`, `check_spec.py` | §1.1 spec, KPIs, ticket |
| W8 | 36 to 50 | `gov brief`, `gov launch`, `gov dispatch`, `gov resources` | §1.2 brief, maps, launch record |
| W9 | 51 to 53 | the authorship check, red on the base, the README map | §1.2 acceptance map |
| W10 | 54 to 57 | `gov accept`, the SubagentStop hook | §1.3 returns |
| W11 | 58 to 67 | `gov land`, `gov check`, the retired `gov close` | §1.3 close record |
| W12 | 68 to 71 | `gov launch --fix`, `--chore`, `gov land --direct` | §1.3 fix section, chore trailer |
| W13 | 72 to 74 | `gov release`, the re-pin | §1.4 release records |
| W14 | 75 to 77 | `gov update`, `gov install` | §1.4 update record |
| W15 | 78 to 88 | the scheduler (`gov dispatch pass`), `gov msg`, `gov backup`, `gov checkpoint` | §1.3 checkpoint, handover; §1.4 usage |
| W16 | 89 to 92 | `gov doctor`, the schedule | §2 hand-off 28 |
| none | 93 to 102 | candidates to retire | |

**The rules the map must meet:**
1. Every step W1 to W16 has at least one tool, and every hand-off between steps names its form and the code that checks
   it.
2. Agents never need to know every tool. A tool that runs automatically is triggered by code; a tool an agent must call
   is named, with its exact command, in the brief of the job that needs it (generated by code, G-3), and nowhere else is
   the agent expected to find it. Skills and role files describe the job, not the tool catalogue.
3. A tool outside the product (the test in §4) is absorbed into it, replaced by the product's own tool, or retired; none
   stays outside.
4. A tool that serves no step, or duplicates another, is retired, on the day the product's own tool takes over (G-5).
5. When no tool is needed (a step held entirely by an agent's job), the row says so, and names the job's form and its
   code check.

---

## Change log

Every change from the owner's draft, with its source. "CORR" is `GOLDEN-WORKFLOW-CORRECTIONS.md`.

| # | Where | Change | Card |
|---|---|---|---|
| 1 | Header, "How to read" | Today column replaced by the corrected text; marked typed until A-23, then computed from the enforcement field | DEC-1241 C-ALL (a); P-5 |
| 2 | Header | A "[since ...]" marker on facts checked at HEAD `461c214a5` that `e2/fixes-015a` changed after CORR's reading (W1 connectors key, W4 stamp, W8, W10, rule 7, rule 10). My addition, from the merge message and the files named; the CTO may strip it | CORR §1 note |
| 3 | W1 Today | The kit sentence corrected: two denies today; connectors key, `defaultMode`, model hook after A-27 | CORR §1 W1 |
| 4 | W2 Today | Adds W2-81's A4 as a fix under W1-41 | CORR §1 W2; DEC-1238 (1c) |
| 5 | W3 Today and Must be | Retry not built; boot start is a scratch script; hook untracked. First in the plan; hook and boot start installed by the product | CORR §1 W3; G-1; G-4 |
| 6 | W3 Held by code | The hook installed by the product in Gov OS and through the kit | DEC-1241 G-4 |
| 7 | W2, W3, §5 | One tool column for W2 and W3 | DEC-1241 P-4 |
| 8 | W4 | Adds the scheduler as the thing that runs the measure; the Sonnet reader and grader noted | CORR §1 W4; P-1 |
| 9 | W5 Today | Rewritten: only the basis check and the in-force digest exist | CORR §1 W5 |
| 10 | W5, rule 8 | The level computed from the author's stated facts; `gov decisions answer` fail-closed | DEC-1242 R-6 (a), T-1 (b) |
| 11 | W6 Today | Rewritten: `gov impact` exists, nothing calls it; no K-line comparison | CORR §1 W6 |
| 12 | W6 Held by code | `gov impact --changed` at the landing into the close record; in planning later | DEC-1242 T-11 (a) |
| 13 | W7 | The ready check runs at `gov brief`; ticket paths checked against the path map when planned | CORR §1 W7; DEC-1241 G-8 |
| 14 | W8 Held by code | Every brief generated by code at launch, refused on a broken link; plan, brief, launch and landing read the same ticket fields; retired commands swept | DEC-1241 G-3 |
| 15 | W8 Held by code | The path map gives each job's paths | DEC-1241 G-8 |
| 16 | W8 Today | Rewritten: partly built, off the path for leads and the CTO | CORR §1 W8 |
| 17 | W8 Must be | Start scripts match the rubric exactly until W8 replaces them | DEC-1242 T-10 (c) |
| 18 | W9 | Each KPI line has at least one red case; guards allowed when marked | DEC-1242 T-3 (b) |
| 19 | W11 | `gov land`, alias `gov queue` for one release; `gov close` retired; two rounds in code | DEC-1241 P-9, P-10 |
| 20 | W11 Today | Rewritten: first landing `4f779086f`, then a hand merge; no auditor called; no diagnosis form | CORR §1 W11 |
| 21 | W11 | On a red the landing writes the record; the CTO decides; replaces "a red calls a quality auditor (Sonnet)". Later decision (DEC-1242) over the draft | DEC-1242 T-12 (b) |
| 22 | W11 | Path-map coverage of added paths checked at every landing | DEC-1241 G-8 |
| 23 | W11 | Impact trace in the close record; G1, G2, G3 in the after-step; a ticket outside the planned wave refused | DEC-1242 T-11, T-9 (c), R-2 (c) |
| 24 | W11 Must be | Proven on the scratch repository and in EXAMIN; Gov OS moves when the owner decides | DEC-1239 (3), (4) |
| 25 | W12 | `--direct` named as not built; code-touching chores through it; records and docs direct; no time box | CORR §1 W12; DEC-1242 T-2 (c), R-1 (b) |
| 26 | W12, rule 6 | The fix section written by the landing | audit 4 A-15 |
| 27 | Rule 6 | `kind: feature` on the ticket; the sentence "a quick item that outgrows its time box becomes a fix or a feature" replaced by the chore definition and by the existing line "a new KPI line on a closed feature is a new ticket" (`CLAUDE.md`) | DEC-1242 R-3 (a), R-1 (b) |
| 28 | W13 Today and Held by code | Corrected: acceptance not built for a full release; gates patch-only and off | CORR §1 W13 |
| 29 | W13, W16 | The full regression on demand for a release, and weekly in W16 as a safety net | DEC-1241 P-2; DEC-1242 T-8 (b) |
| 30 | W13, §3 | Every release prints three measures | DEC-1241 P-6 |
| 31 | W14 | The path-map coverage check after an update; refused at install if too small | DEC-1241 G-8, P-8 |
| 32 | W15 | The scheduler named; one cron line; schedule in configuration | DEC-1241 P-1; DEC-1242 T-5 (a) |
| 33 | W15, rule 10 | The morning handover a step, in the checkpoint form the launcher reads | DEC-1241 P-3; DEC-1242 T-13 (b) |
| 34 | W16 | The scheduler runs it; the full regression record added; lefthook and the kit CI retired | P-2; DEC-1242 T-9 (c) |
| 35 | Rule 2 | Permission prompts set in each repository's settings; the kit lacks the line (A-27) | CORR §2 rule 2 |
| 36 | Rule 3 | Two rounds in code; the code still allows three | CORR §2 rule 3; DEC-1241 P-9 |
| 37 | Rule 4 | The scheduler named; creative content stays with agents in fixed forms | CORR §2 rule 4; P-1; P-6 |
| 38 | Rule 5 | The bundle is cut at 6,000 tokens today; uncut is a build item | CORR §2 rule 5 |
| 39 | Rule 7 | Effort table by role; criticality does not vary the model; scripts match until W8 | DEC-1242 R-4 (a), R-5 (a), T-10 (c); CORR §2 rule 7 |
| 40 | Rule 8 | Corrected: only the basis check exists | CORR §2 rule 8 |
| 41 | Rule 9 | Refused at adoption and at install too | DEC-1241 P-8 |
| 42 | Rule 10 | Corrected: handover and tool list are text | CORR §2 rule 10; P-3 |
| 43 | §3 | The three measures; the 90 % of steps is a floor, 15 of 16 | DEC-1241 P-6 |
| 44 | §4 | The test for "outside the product" and what ships; the retirement day for duplicates | DEC-1241 P-7, G-5 |
| 45 | §5 | Points to TOOL-MAP.md and RECORDS-MAP.md instead of an empty table; the step index; rule 3 and rule 4 amended | DEC-1241 G-6; P-7; G-5 |
| 46 | W1 to W16 | Rules 1 (verified) and the verified cells (W2, W4, W7, W9, W10, W14, W15, W16 Today) keep the owner's words, with the additions above | CORR §1, §2 |
| 47 | Status | Approved by the owner as the spine; replaces his draft | DEC-1244 WF (a) |
| 48 | W11 (what happens, Today, Must be) | Every landing, Gov OS's hand merges included, runs the tests the product's impact selection picks, never a hand-picked set; the selection's inputs (path map, code and test graph, `gov impact` at the landing) made trustworthy first; `fixes-015a`'s hand-picked set noted. Replaces "the full regression before a broad branch" (DEC-1243 (3)) | DEC-1244 X-1 (a) |
| 49 | W11, W16, W13 | The whole suite runs only for a release and weekly; a red the selection missed is a selection bug, logged and fixed | DEC-1244 X-1 (a); DEC-1242 T-8 |
| 50 | W6 Held by code | The path map and the code and test graph named as the selection's inputs, made trustworthy first | DEC-1244 X-1 (a) |
| 51 | W11 | A path the map does not hold exactly once is refused, naming the line to add; a record-only document in a mapped folder passes with a notice | DEC-1244 Q-1 (a); DEC-1239 (2) |
| 52 | W11, W10 | The same failure three times stops the loop; the CTO finds the root cause (brief, spec or KPIs, path map, test, environment, tool), fixes it at the root, records it in the findings log | DEC-1244 Q-7 (c) |
| 53 | W15 | The 3-hour stall push sent by the scheduler, by code, saying what waits and on whom; the CTO's cron rule meanwhile | DEC-1244 X-2 (a); DEC-1243 (4) |
| 54 | W1 | Imports built by a fourth stream when EXAMIN's fresh 80 passes; W1 fully on by the exit | DEC-1244 X-3 (a); DEC-1222 (1) |
| 55 | W7 | A product's Contract and planning go ahead before the integration is complete; only executing waits | DEC-1244 X-4 (a); changes DEC-1238 (4) |
| 56 | W7 | A new feature ticket names its spec (old ones optional); stable id as each KPI line's first token with a fingerprint; word-for-word copy of the spec's line, code only in `verify`; the nine-part form is the spec with OpenSpec beside it | DEC-1244 Q-2 (b), Q-3 (a), Q-4 (a), Q-5 (a) |
| 57 | W9 | Each acceptance test carries its KPI line's id in code (a marker); the README map is generated from the markers, never by hand; `gov accept` fails a line no marker names, for tickets created from the change on | DEC-1244 Q-12 (a), Q-6 (a) |
| 58 | Rule 7, §4 | One vendor and the Claude Code plan only; API keys, other plans and second-vendor review are Wave 3 features | DEC-1244 Q-8 (a), Q-10 (a) |
| 59 | §3, W13 | The floor is a baseline the owner sets at the exit; until then every release prints and none is refused; from then a release below X % stops for his decision | DEC-1244 Q-14 (a); changes DEC-1241 P-6's floor |
| 60 | §3 | A step held by an engine's graph counts only if the engine is pinned and its behaviour checked by Gov OS's own test | DEC-1244 Q-9 (a) |
