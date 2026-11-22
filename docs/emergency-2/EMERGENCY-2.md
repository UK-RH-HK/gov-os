# Emergency 2: the strategy

`docs/emergency-2/EMERGENCY-2.md` · Status: **v3, in force from 17 November, when the owner launched the fresh CTO with it; amended by §13 (2026-11-22); the owner may still amend it** · 2026-11-17

Every Gov OS session reads this file first. Once the owner approves it, it supersedes anything that contradicts it (11.2).

**How to read it**
- A line that ends in a source in brackets is decided. Quotations are the owner's words of 16 November 2026, spelling corrected, nothing else changed.
- **A-n** was the advisor's proposal; the owner approved all fourteen on 17 November.
- **B-n** was a question the owner kept for himself; all four are answered.
- Both kinds are listed in §12.
- Lines marked *Facts* report the audits; they decide nothing.

**Sources**

| Code | Source |
|---|---|
| O-0 | The owner's request for the analysis of the emergency's reports (2026-11-16) |
| O-1 to O-8, O-end | The owner's comments on the advisor's analysis: points 1 to 8 and the closing paragraph (2026-11-16) |
| O-9 | The owner's answers on the draft, the handover's three must-fix items and B-1 to B-4 (2026-11-17) |
| HO §n | `docs/emergency-2/HANDOVER.md`, the retiring CTO's handover (2026-11-16 22:09) |
| F-1 to F-11 | The owner's outline for this file, items 1 to 11 (2026-11-16) |
| EX §n | The owner's advisor export, `advisor-memory-export-2026-11-16.md` |
| P1 to P5, SL, RR, PA | `docs/audit/emergency-2026-11/`: retro-P1-usage, retro-P2-lifecycle (with retro-P2-perticket.csv), retro-P3-lifts, retro-P4-ceremony, retro-P5-memory-use, retro-SHORT-LIST, rubric-research, permissions-audit |
| WS | `docs/audit/emergency-2026-11/context/waves-summary.md` |
| DEC-n | `docs/DECISION_REGISTER.md` |
| Contract | `docs/contract/CONTRACT_v4.md`, version 4.3 |

---

## 1. The aim, and why Emergency 2 exists

**1.1 The aim (standing).** The Gov OS "stops drift and makes the owner's agents work, and record their work, as a good software company does; not a security battle, not a rule battle". It needs four things:
- memory;
- help with the spec and the KPIs;
- roles that keep conflicting work apart;
- governance of the WBS and of tickets' launching and closing, "governing the traffic, not governing a city".

"What matters is tests and code that match the KPIs and the spec and pass green; everything else must justify itself." [DEC-1047; kept by DEC-1158]

**1.2 How roles stay apart now.** They stay apart through the landing, the templates, the briefs, the skills and the path map, not through permissions. "if their, briefs, templates, path map on planning stage, landing code together wouldn't lead the agents to do the right work, nothing else will force it." [O-1]

**1.3 Emergency 2.** Emergency 2 is DEC-1209, declared on 2026-11-16 at 17:26 "to break a cycle of ceremony". [O-0; DEC-1209]

**1.4 The evidence, in five lines.**
1. **Spend, 16 Oct to 16 Nov:** product 4 %; Gov OS building 22 %; coordination 32 %; ceremony 24 %; security 19 %. The weekly plan limit hit 100 % and then 97 %. [P1 §2, §3, F1, F3]
2. **EXAMIN's first ticket, a +7 −1 line fix:** the workers cost $1.10 and about 3 minutes. The ticket took 2 h 30 and about $22, and still did not close. [P2 §4]
3. **The owner as relay:** 544 owner messages in 31 days, of which 134 were relays, 140 were package answers and 33 were yes lines [P1 §2]. 780 permission prompts in 16 days, none from a rule the owner wrote [PA F2].
4. **Memory barely used:** 48 question retrieves in two weeks across 1,749 sessions. 835 of 848 worker sessions made no retrieve. 143 of the leads' 373 `gov context` calls were refused. [P5 §1, table B, F1, table C]
5. **Creep:** 16 of 50 lifted items came back, and 1 of them earned its place. New rules arrived at 3.5 a day; 19 of 82 carried a basis line. [P3 §4, F11]

---

## 2. How we work now: trust, catch and correct

**2.1 The principle.** Trust, then catch and correct; do not prevent. [F-2] "the gov os is to catch and correct these not to prevent it using guard and permissions limitations. this have to end now, no more guard, instead we make the landing deterministic code, with the templates, briefs to agents with skills and decision log, more coherent using code to guide workers and engineers rather than limiting them." [O-1]

**2.2 What goes.** No guard, no sandbox, no box, no permission prompts, no permission editing. [F-2] "no more sandboxing, only work trees, for parallel working." [O-3] "no more prompting, no more permission editing." [O-4]

**2.3 Agents' permission.** Agents have full permission in the repositories they work in, their worktrees and their run folders. [F-2]
- **Where it applies:** the no-prompt mode is set in the Gov OS repository's and EXAMIN's project settings, so it covers their sessions and worktrees, never the whole machine; the owner's user default is restored. [O-9; HO §4: the switch-off put it in the user settings]
- **How sessions stay apart:** by where each session starts and the folders it is given, and by its brief; nothing enforces it. A shell command can reach anywhere the owner can; that is caught by the transcript scan (2.7), not prevented. [O-9; 2.1]
- **The CTO's four extra places:** the evaluation sets (for the question writers it launches), the machine state in `~/.gov-os` (the launcher and dispatcher), the crontab (the run-time tool) and EXAMIN APP (the merge back). Leads, workers and product CTOs get only their own repository, worktree and run folder. [O-9; HO §10]

**2.4 Two denies only.** `git push` and `sudo` stay the owner's. [F-2] They are carried as two Claude Code settings deny lines, which hold in every permission mode. [PA §7 W8]

**2.5 Releases.** Releases stay the owner's. [F-2] He types the release code in his own plain terminal. [EX §5]

**2.6 The operator.** The owner's operator (his own interactive session) stays as his hand, with full permission across WSL. [F-2]
- **B-4, decided:** the CTO has no operator. It gets the four places of 2.3 directly; what remains outside them is the owner's own: releases, re-pins, pushes, sudo and his machine's settings. [O-9; HO §10]
- **The operator agent retires** with the ACT pipeline (2.10): its cron launcher, its gates and its lock. OWNER-OPERATOR-FULL-1, which widened that agent, is superseded. [O-9]

**2.7 Hidden question sets.**
- They are detected by a transcript scan; if a set was read, the measure is void. [F-2]
- The memory reader runs with only the memory tool, and the gold sits outside the index. [F-2]
- **A-12:** the scan reads every transcript written between the set's writing and the end of its measure, looking for the set's path and its question ids.

**2.8 Backups.** An hourly `git bundle` of each repository, kept outside the tree. [F-2]

**2.10 The ACT pipeline retires.** With no guard, control files (settings, hooks, crontab lines, generated copies) change by ordinary commits. The ACTs, the class rules, the approved lists and the operator agent's cron launcher go; kernel and instruction text follows 3.5. "a simple two lines act is going in full loop of decision making which we don't need." [O-9]

**2.11 Gitleaks.** No gitleaks scan for any private repository, Gov OS and EXAMIN included. When a repository is to go public or be shared with a third party, one full scan runs before that push. This replaces EXAMIN's weekly scan before its push. [O-9 (B-3); EX §5 superseded]

**2.9 What 2.1 to 2.8 contradict.** Read from the register titles; audit 8 confirms each.
- DEC-1205 and DEC-1207 (2): the box and full permission inside it.
- DEC-1203 (1): the box as an exception.
- DEC-820: "reads open, writes closed".
- DEC-313: `gov launch` refuses permission bypass.
- DEC-1082 and DEC-1128: the guard's rules and their bar.
- The emergency's security fixes: GF-8, GF-9, the box and the no-prompt start lines. [WS]

---

## 3. The golden rule, as it now applies

**3.1 Threat model, unchanged.** Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work. It is not a guard against a same-privilege adversary. [DEC-1204 (1); DEC-039 / ADR-0001]

**3.2 What may block, unchanged.** A finding blocks only if it is within the change's scope, an honest agent can hit it in ordinary work, and it fails open or loses work. A finding that needs a deliberate construction is a Wave 3 row, never a new round. [DEC-1204 (2)]

**3.3 Where a review happens, unchanged.** A moderator triages the findings. There are at most two rounds, then the owner once, with options. READY is computed by code. [DEC-1204 (3)]

**3.4 When a review happens (new).** Only when the landing turns red, a merge fails, or a cause is unclear. Most problems are found and fixed by the CTO, a senior engineer or the engineer, without review. [F-3] "reviewing what green is like reaching the moon, just double checking did we reach or not." [O-5]

**3.5 B-1, the owner's answer: kernel and instruction text is the CTO's call.** The files every agent is steered by (role files, brief and role templates, skills, CLAUDE.md and AGENTS.md) change only when the CTO decides a change is needed, approves it and makes it itself, so the landing is never upset by them; this matters most for a skill or a file every role uses. Nothing in this reaches the owner. [O-9]
- *Facts:* the kernel gate earned its place: kernel bytes were merged before approval (DEC-1147, DEC-1148) [P3 §3; P4 Q12]. The CTO's approval now carries that gate; no CIT-P session.

**3.6 B-2, the owner's answer.** No ticket gets a reviewer. A review happens when something is not working as needed, not only when a test is red; most of the time the CTO, a senior engineer or the engineer finds and fixes the cause, and then no review is needed. Bugs that land silently are found by friction, as EXAMIN's adoption found many. Where review is worth it, it is batched: one review of several issues together, for example after the nightly run. [O-9]
- *In short:* a review is called only for a red test, a failed landing or merge, or a feature that does not work as intended. A ticket that went through smoothly needs none. [O-9]

**3.7 A-13.** The `judging-work` skill (W2-195, DEC-1204 (5)) and the golden-rule section in CLAUDE.md and AGENTS.md (ACT-GOLDEN-RULE-1) are trimmed to 3.4 in the same change.

---

## 4. The ticket model

**4.1 A ticket is a feature.** It has a spec and KPIs; for example `gov update`, `gov adopt`, memory. [F-4] "a ticket have to be a feature, which have KPIs for success" [O-5]

**4.2 A known bug is a fix, not a ticket.**
- A known bug in an existing feature is fixed without a ticket and recorded in its owning ticket's record. [F-4]
- When no test caught the bug, the failing test is written first. [F-4]
- "that's not a ticket, that's a bug fix for current running or closed tickets ... records are kept in the same ticket" [O-5]
- *Effect:* DEC-1088's "closed tickets are never edited" no longer holds for fixes. [DEC-1088; EX §3]

**4.3 The flow.** [F-4; O-5]
1. The independent test designer writes the acceptance tests, red on the base.
2. The engineer builds until `gov accept` is green. That run is the acceptance.
3. The deterministic landing, by code, in minutes: it merges, runs the impact-selected tests, and checks the paths and who wrote the tests.
4. If the landing is red, a quality auditor (Sonnet can do it [O-5]) or an engineer finds and fixes the cause. Then the change lands.
5. The ticket closes at the land.

The CTO orchestrates the flow, or the senior engineer of a stream when several streams run under the three layers. [O-5]

**4.4 The landing today, as the starting point.** *Facts:*
- It merges, then runs the selected tests on the merged result.
- It refuses an acceptance-test commit that lacks the test designer's role (G-1).
- It checks trailers, containment, a committed tree, store freshness and disk.
- It computes READY from the verdict blocks.
- Sources: P4 S2, Q4, Q11, Q13, Q14.
- The median land takes 21 min; p90 is 50 min. [P4 counts]
- Most ejections were for paperwork, not code: the allowed-path form, the probe-record form and the path map. [P2 §3; P3 F10]
- Templates with READY and DONE computed by code were decided [DEC-1052; DEC-1116]. Audit 1 reports what was built.

**4.5 The rubric.** It is measured from the data, with the CTO's help. [F-4] "need to agree on the rubrics, and set a real categorization method for it. maybe from existing data in the gov os repo and CTO help." [O-5]
- *Inputs:*
  - the 141 worked tickets [P2 CSV];
  - the CTO's 335 direct commits, 87 % of them touching three files or fewer [RR M3];
  - the research's decision table [RR §7.3].
- 4.1 and 4.2 supersede the provisional rubric [DEC-1208] where the two differ. Its classes for features stay until the measured rubric replaces them.

**4.6 A-6.**
- A third kind of work, the **chore**: records, docs, configuration, or a tidy-up with the tests unchanged and green. It is a direct commit, listed in the digest, with no ticket.
- A new KPI line on a closed feature is a new ticket, never a reopen. [SL row 7]

---

## 5. Memory

**5.1 The standard.** "we developed the best memory practice to be used by agents which reached 98.7% and it did include, hit@10 or hit@20 retrieval and ranking with semantic and lexical searching and graphs etc, while second reranking by the agent and second search by the agent. that's my target memory to be build, and used" [O-1]
- The configuration is the one DEC-1097 and DEC-1098 made the standard. [EX §3, 2026-11-08]
- The 98.7 % measure's record is cited from the retiring CTO's handover.

**5.2 hit@k is not a target.** "hit@5 I DON'T CARE if it's even 10%" [O-1]. hit@k is not a target or a floor anywhere. [F-5]
- *Effect:* these come out:
  - the Contract's CAP-10 acceptance (mean hit@5 85);
  - DEC-1210 (4)'s "a diagnostic against CAP-10's floor of 85";
  - W2-15a's and W2-15b's hit@k measure lines.

**5.3 Each measure.**
- A fresh 80 questions: 40 visible, 40 hidden.
- Written and measured at once, on a pinned snapshot.
- Judged end to end at 95 %: the reader reads the whole ranked bundle and searches once more in its own words; Opus grades and Sonnet checks agreement; both the answer and its citation must be right. [DEC-1210 (1)]
- The release needs 95 % or more. [F-8]

**5.4 Used by construction.** `gov brief` puts the ticket's retrieval into every brief. Every template and every skill says memory first. [F-5] "if there is no deterministic way to enforce using the memory when needed, then we can build the memory using approach and enforcement into these briefs and skills, so everyone uses them always." [O-7]

**5.5 `gov context` is switched off.** [F-5] "if its making problems take it out" [O-7]
- *Facts:* 143 of the leads' 373 calls were refused, 103 of them for being over its ceiling; 18 briefs were then built by hand. [P5 table C]

**5.6 A memory-use log.** [F-5] P5 F6 proposes its fields.

**5.7 The gaps 5.4 must close.** *Facts:*
- The brief says "No `gov retrieve` in the sandbox". [SL §1; P5 F1]
- Workers' retrieves were degraded in the sandbox. [P5 F1]
- The CTO asked memory a question 6 times in two weeks, against about 100 greps where memory fitted [P5 F5]. Its subagents asked 3 times, against about 1,290 [P5 F2].
- `role-reviewer.md` has no memory line. [P5 F8]
- The EXAMIN CTO made 0 retrieves. [P5 F7]
- Leads cut bundles with `head`. [P5 F4]
- `{QUESTION}` was left unfilled in 23 briefs. [P5 F9]
- The store lacks recent decisions until it is rebuilt. [P5 F3]

**5.8 No CPU fallback** for embeddings or reranking. [DEC-1065; EX §3]

**5.9 The weekly maintenance.** A fresh 80 measure, a clean-up and a refactor. [F-5; O-1] W2-187 and W2-188 reopen for it when DEC-1209 lifts. [DEC-1210 (8)]
- **B-3, decided:** no gitleaks while a repository is private; one full scan before it goes public or is shared (2.11). [O-9]

**5.10 Question writers.** They are launched automatically in their own sessions [EX §3, 2026-11-09]. Without the guard, a set is protected as 2.7 says.

---

## 6. Kept running, switched off, retired, built

### 6.1 Decided

| Item | Disposition | Source |
|---|---|---|
| Checkpoints and compaction (PreCompact, SessionStart and Stop checkpoint hooks); full window, compacting with checkpoint and handover | keep | O-6; DEC-1183; EX §3 |
| Dispatcher and load balancer | keep, then rebuild as the run-time tool (6.3) | O-6; O-3 |
| Watch and sentinel | keep, folded into the run-time tool | O-6 |
| Independent test designer; `gov accept` | keep | O-5; F-4 |
| The landing (`land.py`, merge queue) | keep, made deterministic | O-1; F-4 |
| The owner's operator; OWNER-OPERATOR-FULL-1 | keep | F-2; DEC-1207 (6) |
| Releases and pinning | keep (the owner's) | F-2; O-1 |
| The guard (PreToolUse hook, its rules and parser) | switched off now; retired | O-1; F-2 |
| The sandbox (SANDBOX-1 in `gov launch`); the box | switched off now; retired | O-3; F-2 |
| Permission prompts; permission editing; the quiet-hours PermissionRequest hook | switched off; retired | O-4; F-2; PA F12 (the hook exists only to queue prompts) |
| `gov context` | switched off | F-5; O-7 |
| GF-8, GF-9, P-BOX-EXCEPTION-1, ACT-PERMISSIONS-4 | retired (follow from the rows above) | O-1; O-3; F-2 |
| W2-186 (reranker into the sandbox); W2-42 (guard: roles, links, late paths, atomic saves) | retired (follow from the rows above) | O-1; O-3 |
| Review of work that is already green | retired | O-5; F-3 |
| **First:** `gov launch` without the guard and the sandbox (it refuses every worker launch today: `src/gov/launch/launcher.py:371-413`, `:440`, `:279-284`), then release 0.1.2, cut and re-pinned by the owner | build first; nothing else can be built before it | HO §4; O-9 |
| The 29 tests that went red after the switch-off (they assert the guard and `gov context`) | update or retire with what they assert | HO, the CTO's last message (log `log/landing-select/20261116-220824-3649974`) |
| EXAMIN's copy: its guard switched off as Gov OS's was, with the no-prompt mode in its project settings | do with the 0.1.2 re-pin | O-1; O-9 |
| The sentinel and the dead-man; the CTO's inbox wakes | stopped (2026-11-16, with the retiring CTO); their jobs go to the run-time tool | O-6; HO §4 |
| The operator agent's cron launcher and its lock | disabled with the ACT pipeline (2.10) | O-9; HO §3, §4 |
| W2-17 `gov update` | build for the release | O-3; F-7 |
| W2-36 `gov discover` | build | O-3 |
| W2-121c, W2-121d (dispatch health; watch and launch lead); the machine-agnostic load balancer | build, as the run-time tool | O-3; O-6 |
| Minimal, file-based agent-to-agent messages | build, inside the run-time tool | O-6; F-6 |
| Memory by construction; the memory-use log; the weekly maintenance | build | F-5; O-7 |
| The deterministic landing, with the templates, briefs and skills | build | O-1 |
| W2-192 (adoption stage AS, the spec audit) | finish | DEC-1200 |
| W2-193, W2-194 (close against the base; accepted reds in scoped mode) | build | DEC-1203; DEC-1206 |
| W2-195 (the `judging-work` skill) | finish (see A-13) | DEC-1204 (6) |
| W2-187, W2-188 (weekly fresh-80 audit; adopt skill step 6) | reopen at the lift | DEC-1210 (8) |
| W2-19 language-agnostic test commands | Wave 3, with ASMO and UPIM | O-3 |

### 6.2 Approved by the owner on 17 November (A-1 to A-14 in §12)

| Id | Item | Decided | Why |
|---|---|---|---|
| A-1 | The nightly full regression; the spend brake; heavy slots and `mem_guard`; the dead-man | keep running until the run-time tool replaces them | they catch reds the scoped runs miss, protect capacity and the machine, and wake a stalled CTO [P4 Q16, C7, C3, C4, C8] |
| A-2 | The idle-check and waiter Stop hooks; the structural, idle-headroom and harvest inbox items | fold into the run-time tool; notices become one daily digest line | four watcher layers; 1,219 inbox items [P4 C9, Q15, R12, C2] |
| A-3 | Hand-written version rows and next-free-id lines (check first that no tool reads them); the `scratch_measure` step; the `.pre-*` tool copies; the nightly's clean-tree and head-age checks and the 03:55 freeze; `pgrep land.py` before every commit; the inert local allow list | lift now | no ordinary-work protection [P4 R2, Q24a, R14, C6; P3 F1; PA F4] |
| A-4 | W2-145, W2-155 (merged); W2-156, W2-191 (built) | finish: land and close | built and approved [WS] |
| A-4 | W2-115b `gov queue` (the product's merge queue) | build for the release | the landing must exist in adopted repositories, not only in Gov OS's own tools [WS; P4 Q13] |
| A-4 | W2-18 pinned install | build with W2-17 | `gov update` installs a pinned release |
| A-4 | W2-34 `gov readiness --generate` | fold into W2-36 | the aim's spec-and-KPI pillar [DEC-1047] |
| A-4 | W2-82 Definition of Ready | fold into the templates (READY by code) | DEC-1052; DEC-1116 |
| A-4 | W2-15b memory pass 2 | retire, unless the first fresh 80 on today's repository is below 95 % | 5.1, 5.3 |
| A-4 | W2-00 coordination record | retire | no role in the model of §4 |
| A-4 | W2-46, W2-47 exit run and exit audit | replaced by the release acceptance (§8) | F-8 |
| A-4 | W2-81 (the 0.1.1 re-run) | close on its record; its six synthetic repositories become the release's proving run | F-8; DEC-1202 |
| A-4 | W2-35 UX readiness row; Docker image; empirical model routing (CAP-36) | Wave 3, driven by friction | O-end |

### 6.3 The run-time tool

**Decided scope:**
- Dispatch, a machine-agnostic load balancer, watch, checkpoints, and minimal file-based agent-to-agent messages, scoped with KPIs. [F-6]
- Its purpose: "to keep the work going and reminding the agents or knowing when agents finish" [O-6], working "agnostically of machine size" [O-6].
- The GPU never spills. Embedders and rerankers stay on the GPU, even if that limits parallel leads. [EX §3; DEC-1158 (3) keeping DEC-1039 (1b)]
- Every launch takes its model and effort from the owner's rubric. [DEC-1120; EX §3]

**A-5: KPI lines, each with its verify.**

| KPI | Line | Verify |
|---|---|---|
| RT-1 | No ready ticket waits more than 10 minutes while the machine has room for it. | A week of the tool's log. |
| RT-2 | The orchestrating session gets a message within 2 minutes of any lead, worker or job finishing. | Finish times against message times. |
| RT-3 | Slots come from the CPU, RAM and GPU detected at start, with no machine-specific constant. | One configuration runs on two simulated machine profiles. |
| RT-4 | Zero GPU spill events. | The GPU log. |
| RT-5 | After a compaction, restart or crash, a session resumes at the recorded next step without the owner restating it. [Contract CAP-37] | A forced compaction and a killed session. |
| RT-6 | Messages between CTOs, leads, workers and the operator go through per-session inbox files with a read mark; none passes through the owner. | A week of owner messages carries no relays. |
| RT-7 | One state file and one wake rule replace today's watcher layers. [P4 C9] | One watcher process. |
| RT-8 | The launcher picks the model and effort from the rubric and states them. [P4 Q20] | The launch log. |

---

## 7. EXAMIN

**7.1 The owner's words.** "I would continue EXAMIN memory building same as GOV OS, and using the GOV adopt, so when the new release comes with new release updated the memory is ready and EXAMIN repo is refactored to continue the work under the new release. but I wouldn't execute tickets and start waves other than wave 0 yet before the release, as the tickets themself, need categorization in the refactoring stage, which the new release will assess and execute based on the agree rubrics later." [O-2]

**7.2 How Wave 0 runs.** Wave 0 is direct work: the refactor, and memory via `gov adopt`. No tickets and no later waves before the release. [F-7] No deadline: "no need to set deadlines for EXAMIN adoption" [O-8].

**7.3 Wave 0's approved steps.** [EXAMIN CTO brief 2ec48c78 §3; WS]
1. The target layout.
2. A full audit of every file.
3. The spec audit.
4. An independent check of the dispositions.
5. The refactor, behind characterization tests.
6. The merge back into EXAMIN APP, with its 46 uncommitted files committed there first. [EX §5]

Steps 1 and 2 are done. [WS]

**7.4 EXAMIN's memory.** It is built and measured as Gov OS's is: a fresh 80, end to end, at 95 % or more. [DEC-1210 (5); F-8] "same approach with gov os 98% memory" [O-8]

**7.5 No customer data.** Everything under `product/data/` is virtual trial data. [EX §4]

**7.6 Moving to the release.** `gov update` ships in the release, so EXAMIN moves to it without re-adopting. [F-7]

---

## 8. The release acceptance

**8.1 What the lean release is.** "lean release is finishing all GOV OS tools as described, assess what can be kept, what removed and archived etc, and make sure EXAMIN repo memory is build and measured as we already successfully did and measured same approach with gov os 98% memory, then the release will be on finished gov os." [O-8]

**8.2 The acceptance.** [F-8]
1. The re-baselined Contract's checks pass (audit 7).
2. The proving run on the synthetic repositories passes.
3. EXAMIN's copy is adopted on the release, with memory at 95 % or more end to end on a fresh 80.
4. One EXAMIN feature ticket goes through the flow of 4.3.

**8.3 The release and re-pin.** Then the owner cuts the release and re-pins. [F-8] "need to do another re-pin and release of the clean version" [O-1]

**8.4 After the release.** Gov OS changes only from friction. "close GOV OS development and keep it only doing updates each time we find a bug or see a new feature needed to be added based on friction with adopted repos." [O-end]

---

## 9. The first audits for the fresh CTO

**9.1 The audits.** Each returns a table. [F-9]

| # | Audit [F-9] | The table holds (A-9) |
|---|---|---|
| 1 | Landing, templates, briefs and skills | What each does today; what is built of DEC-1052 and DEC-1116; why briefs are written by hand [P5 table C; P2 §3]; what the landing needs to run by code, in minutes, in an adopted repository |
| 2 | Memory in use, and what depends on `gov context` | Every caller of `gov context`, `gov retrieve` and `gov brief`; the change for 5.4; each gap of 5.7, closed or open |
| 3 | The run-time tool | Today's parts (dispatcher, gates, slots, watchers, sentinel, dead-man, checkpoint hooks, inboxes) and a design meeting 6.3 |
| 4 | The ticket disposition and the rubric, from the data | Each open and Wave 3 ticket: keep, build, fold or retire; the 141 tickets and the CTO's commits classed as feature, fix or chore; the rubric that results |
| 5 | The Gov OS repository | Each top folder and scratch tree: stays in git and is pushed, archived, or deleted. The scratch area holds 321 tools, 2,297 log files and 378 drafts [P4 R14] |
| 6 | EXAMIN's assessment | Wave 0's status against its brief; what the release must give it |
| 7 | The Contract re-baseline | Each MR and CAP clause: kept, changed (and how), dropped, or moved; the starting list is in 9.2 |
| 8 | The decision register | About 1,200 decisions: code first on the change marks, then by theme in parallel. Each is kept, superseded, retired, or history, approved by the owner by group. The old register is then archived read-only and excluded from memory's index. [F-9] |

**A-9:**
- The audits run in parallel and read-only.
- Each writes its table under `docs/emergency-2/audits/`.
- The decisions the audits need come to the owner in one message.

**9.2 Contract clauses that contradict this file today.** *Facts* from the Contract's text; the dispositions belong to audit 7 and the owner.

| Clause | What it says today |
|---|---|
| MR-3, CAP-58 | Writes are refused by the guard |
| CAP-61, CAP-62 | Workers run in the OS sandbox |
| CAP-05 | `gov pause` works through the guard denying writes; it needs another carrier |
| CAP-10 | Mean hit@5 of 85 (5.2) |
| CAP-15 | A context packet of about 6k tokens from `gov context` (5.5) |
| CAP-31 | A failed close creates a repair ticket (4.2) |
| CAP-38.f | A FULL probe after green (3.4) |
| CAP-59, §2 Loop budget | Three iterations (DEC-1204: two rounds) |
| CAP-03 | A gitleaks filter before every indexer (gitleaks has been off since DEC-1045 [P4 Q11; P3 T-13]) |
| CAP-25, CAP-49.c | Installs and the oracle held by the guard |
| CAP-39.a | Tier G0 is the guard |
| CAP-45 | `gov update` in Wave 3 (now in the release, F-7) |
| CAP-30.c | `readiness --generate` in Wave 2 (moved to Wave 3 by DEC-1201) |
| CAP-35 | Model routing in Wave 3 (DEC-1120 applies it now) |
| §2 Boundary | The orchestrator unsandboxed, and the guard as a wall |

**A-14.** Audit 7 checks Charter v5 too: it sits above the Contract and is not in the evidence pack.

---

## 10. Keeping it from regrowing

**10.1 The basis line.** No new rule without a basis line naming an incident. [F-10]
- **A-8:** the basis line is checked by code at the decision-record commit, with a weekly basis review. [SL row 4; P3 F11]

**10.2 The weekly measures, with their baselines.** [F-10]

| Measure | Baseline | Source |
|---|---|---|
| Product share of spend | 4 % over the month; 13 % in its last four days | P1 §2, §3 |
| Governance share, under the Contract's 15 % | Coordination plus ceremony: 56 % | Contract CAP-04.b; P1 F1 |
| Owner messages per day | 18 (30 in the last four days); 104 at night over the month | P1 §2 |
| Time per ticket | Claim to merge, median 0.25 / 0.58 / 0.87 days (LITE / STANDARD / FULL) | P2 §1 |
| Cost per ticket | Lead and workers, median $6.71 / $18.88 / $51.19 | P2 §1 |
| Landing time | Median 21 min; p90 50 min | P4 counts |
| Memory use | 48 question retrieves in two weeks; 835 of 848 worker sessions made none | P5 §1, F1 |

**A-7.** The governance share is measured by P1's method until the Contract's own counter (CAP-04.b) exists. The two definitions differ: the Contract counts the tokens Gov OS injects; P1 counts spend by category.

**10.3 Precondition.** Transcripts are kept for 365 days. [EX §5; SL row 5]

**10.4 Capacity.** "capacity should be used to fix gov os as described and build examin memory as described above." [O-8] The weekly plan limit hit 100 % and 97 % in the two weeks before Emergency 2, and stood at 56 % 32 hours after the 11-15 reset. [P1 §3; SL §3] Nothing else takes capacity before these two: no watchers, Sonnet where it is enough, Opus where it matters.

---

## 11. The fresh CTO starts fresh

**11.1 What is archived.** The old MEMORY.md, CHECKPOINT, START-NEXT-SESSION, DECISIONS-IN-FORCE and prompt are archived. [F-11]
- *Facts:*
  - Rules lived in five places. [P3 F8]
  - MEMORY.md has 104 entries, at least 25 of them workarounds. [SL row 13; P4 H1]
  - CHECKPOINT is 337 KB. [P4 R11]

**11.2 Precedence.** This file supersedes anything that contradicts it, the Contract included until the Contract is re-baselined. [F-11]

**11.3 The old register.** After audit 8, the old register is archived read-only and excluded from memory's index. [F-9]

**11.4 DEC-1209.** DEC-1209 stays in force until the owner lifts it. [DEC-1209]
- **A-10:** DEC-1209 lifts for the build list of 6.1 as soon as the owner approves §6, so the release's tickets start without waiting for every audit.

**11.5 A-11.**
- The owner's approval of this file is recorded once in the register. [DEC-861]
- The advisor export is committed beside this file, so that EX citations resolve.

---

## 12. For the owner's approval

**Open, for the owner**
- [x] B-1: kernel and instruction text is the CTO's call: it decides, approves and makes the change itself; nothing reaches the owner (3.5) [O-9]
- [x] B-2: no reviewer per ticket; a review only for a red test, a failed landing or merge, or a feature not working as intended; batched when several issues come together, for example after the nightly (3.6) [O-9]
- [x] B-3: no gitleaks while private; one scan before going public or shared (2.11, 5.9) [O-9]
- [x] B-4: the CTO has no operator; it gets the four places of 2.3 (2.6) [O-9]
- [x] The ACT pipeline retires (2.10) [O-9]

**Advisor proposals, all approved by the owner on 17 November [O-9]**
- [x] A-1: keep running until the run-time tool replaces them: the nightly, the spend brake, heavy slots and `mem_guard`, the dead-man (6.2)
- [x] A-2: fold the watcher hooks and the inbox notices into the run-time tool and a daily digest line (6.2)
- [x] A-3: the quick lifts (6.2)
- [x] A-4: the ticket dispositions in 6.2
- [x] A-5: the run-time tool's KPI lines RT-1 to RT-8 (6.3)
- [x] A-6: chores without tickets; a new KPI line is a new ticket (4.6)
- [x] A-7: the governance share by P1's method until the Contract's counter exists (10.2)
- [x] A-8: the basis line checked by code, plus a weekly basis review (10.1)
- [x] A-9: the audits' table contents, parallel runs, one folder, one decision message (9.1)
- [x] A-10: DEC-1209 lifts for the build list once §6 is approved (11.4)
- [x] A-11: approval recorded once; the export committed beside this file (11.5)
- [x] A-12: the transcript scan's window and targets (2.7)
- [x] A-13: `judging-work` and the CLAUDE.md section trimmed to 3.4 (3.7)
- [x] A-14: audit 7 checks the Charter too (9.2)

---

## 13. Changed since v3 (dated; the owner's decisions win over the text above where they differ)

Written by the CTO for N-28 (DEC-1233 (1)); **approved by the owner on 2026-11-22, with two rows he added** (DEC-1237). Each row names the section it changes.

| Date | Section | What changed | Decision |
|---|---|---|---|
| 2026-11-19 | §4.1-4.6 | A new ticket is opened only for a new feature; the launcher accepts a fix under its owning ticket and a chore with no ticket | DEC-1219 (5), (6) |
| 2026-11-19 | §2.11 | One real-gitleaks case is kept in the weekly tier, for the scan before a repository goes public or is shared | DEC-1220 (1) TI-3 |
| 2026-11-19 | §3, §7 | Gov OS's golden rules and "value first" stand at the head of every adopted repository's CLAUDE.md and AGENTS.md, carried by the kit through `gov adopt` and `gov update` | DEC-1217 (7), DEC-1219 (4) |
| 2026-11-20, 2026-11-22 | §2.5, §8.3 | 0.1.5 is the owner's last manual cut. After it the CTO cuts every release whose content the owner has already approved (features he approved, Contract and Charter changes he approved), by code, once `governance/project/release-authority.yaml` is on, only when the release acceptance passes, with the re-pin's self-rollback and a push to the owner each time. Pushes to GitHub and sudo stay the owner's | DEC-1223 RB-1, DEC-1224 (3)-(4), DEC-1226, DEC-1235 (2) |
| 2026-11-20 | §8.2 | Item 4 (one EXAMIN feature ticket through the flow) moves to EXAMIN's first planned wave; the release acceptance rests on the proving run (W2-81) and EXAMIN's fresh 80 | DEC-1224 (1)-(2) |
| 2026-11-20, 2026-11-22 | §5, §6.1 | The imports feature: what a repository brings in is classed use, absorb or study and placed in memory accordingly, MCP tools among them; code reconstructed with REA is study until an absorb assessment names a commercial licence | DEC-1221 (2), DEC-1222 (1), DEC-1223 (8), DEC-1228 (1)-(3) |
| 2026-11-22 | §4.5, §6.3 (RT-8), §10.4 | Models: Opus only for each app's CTO and a senior engineer; every other agent Sonnet, C3 work included; no Fable; one exception, a wide audit the owner asks for, on Opus; enforced by code | DEC-1225 |
| 2026-11-22 | §4.5, §6.3 (RT-8) | Ticket leads (and fix and chore leads) run Sonnet at medium effort | DEC-1236 (2) |
| 2026-11-22 | §3.5, §6.3 (RT-8) | A change to any role's model or effort comes to the owner first; nothing changes one in code, settings, scripts or briefs before his yes | DEC-1236 (3) |
| 2026-11-22 | §5.3 | The measure's reader and grader run Sonnet (the first fresh 80 graded on Sonnet is the new baseline); citing a forbidden (stale, superseded, legacy) source makes an answer wrong, in the product's measure as in W2-81's | DEC-1225 (4), DEC-1227 D5 |
| 2026-11-22 | §8.2 | The lite adoption verdict (CAP-44.h) rides the release after 0.1.5 | DEC-1231 |
| 2026-11-22 | §2.3 | No Gov OS or EXAMIN session loads the owner's claude.ai connectors; each session gets only the MCP tools its role needs; MCP tools are imports (registered, pinned, given by role) | DEC-1232 (6), DEC-1228 (2) |
| 2026-11-22 | §1, §11 | The owner's order: the model rubric in code; 0.1.5 then the automated release; W2-81 READY; EXAMIN's fresh 80 at 95 %; EXAMIN's planning stage; then EXAMIN's development under Gov OS. Everything else in parallel, never ahead | DEC-1232 (1) |
| 2026-11-22 | §9, §12 | Every decision that needs the owner is a structured record (question, findings, options with costs, recommendation, sources), batched into one interactive page (a card per decision, an option, a note, a copyable answer sheet) published privately for his phone; his answer sheet is written into the register by code; the escalation rubric routes every owner decision through it (built in the release after 0.1.5) | DEC-1235 (3), DEC-1236 (1) |
| 2026-11-22 | §5.9 | The weekly maintenance is a chore; W2-187 and W2-188 are not reopened | DEC-1233 (1) N-31 |
| 2026-11-22 | §10 (new rule) | **Whatever can be deterministic becomes code; what cannot is specified so** (what each agent type receives, what it produces and in what form, and how code checks it). The Charter states the rule; every Contract item carries whether it is built, how it is enforced today, if not built why and when, and what it should be; the release acceptance checks them | DEC-1233 (6) |
