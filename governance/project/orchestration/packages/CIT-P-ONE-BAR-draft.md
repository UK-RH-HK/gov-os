---
id: DEC1131-ONE-BAR-CIT-P
type: change-impact-proposal
status: PROPOSED
state_class: EVIDENCE
date: 2026-11-11
author: product-spec helper of the CTO (orchestrator DAEO-sdxk), class C2
decisions_read: [DEC-1131, DEC-1010, DEC-096, DEC-916, DEC-957, DEC-801, DEC-802, DEC-803, DEC-808, DEC-1105, DEC-1106, DEC-1107, DEC-1112, DEC-1116, DEC-1121, DEC-1128]
decisions_carried: [DEC-1131, DEC-1010, DEC-957, DEC-801, DEC-808, DEC-1112]
review: one fresh read-only independent reviewer, at most two rounds, by the rule itself (CAP-33)
proposed_destination: docs/changes/DEC-1131-CIT-P.md (the CTO commits it; the product-spec ticket that makes the edits cites it)
state: draft, for the CTO's check
---

# One bar, two rounds for every role: change-impact proposal (CIT-P)

Plain words first. The owner decided on 2026-11-11 (DEC-1131) that every role is judged against the ticket's KPI
lines and nothing else, and that every role gets two rounds per ticket. This record lists every text that changes, with
the new words, who may change each file, how the CTO keeps the round count by hand, what it leaves alone, and how it
could go wrong. **No edit is made by this record.** The edits are made by one product-spec ticket after the owner
approves this record (CAP-33).

---

## 1. What and why

### 1.1 The rule, as the owner adopted it (DEC-1131 (1), (2), (4))

DEC-1131 (1): adopt "one bar, two rounds" for every role (DEC1010-REVIEW section 4.1), **option A**: the text first by
this CIT-P; the CTO keeps the round ledger by hand; the counting code follows after two weeks of use.
DEC-1131 (2): **an engineer pass that only fixes the findings the review marked blocking belongs to the same round.**
DEC-1131 (3): the two code gaps are fixed now by their own routes (not in this record, section 4).

The rule in the words this record proposes (call it **Text R**; the same words go into four files, section 2.1):

> - **One bar, two rounds (owner, standing, DEC-1131, widening DEC-1010 item 1; in force for the CTO, every lead and every role: test designer, engineer, product-spec, reviewer, auditor):**
>   - **The bar is the ticket's KPI lines and its stated specification** (sources, interface, non-goals), and nothing else. Every session is judged on it: the designer's tests, the engineer's code, the product-spec text, the reviewer's verdict. A KPI line is named by its id: `S1`, `S2` ... in the `success` list, `F1`, `F2` ... in the `failure` list.
>   - **Every finding names the id of the KPI line it fails, or it is a row** for the list or Wave 3. A row starts no round, in any role. **A KPI line marked fail blocks**, whatever the number of findings under it and whatever their consequence. A line marked pass carries no finding. A finding that needs a deliberate construction (DEC-801) is a row and fails no line.
>   - **A round is one judgement of a role's work against the KPI lines, with the pass of work before it:** the red check for a test designer, the acceptance run for an engineer, the review for product-spec and for the whole ticket. **At most two rounds per ticket and role.** The CTO counts them from the ticket's id in `governance/project/orchestration/ROUND-LEDGER.md`; a rename, a rebuild, a declared "round 2a" or a follow-up that reopens the same KPI lines does not restart the count. No worker is told the count (DEC-096).
>   - **A pass that only fixes findings a review marked blocking belongs to the round that found them:** each commit names the finding's id and changes nothing else. A pass that carries anything else (a row, a new test, a new behaviour) is a round of its own.
>   - **A KPI line still failed after round two goes to the owner,** once, with each line's state, the evidence of both rounds and the options: narrow the line, split the ticket, defer, or one more round with its reason. Only the owner gives a third round, in a decision that names it; the CTO's P2 power (DEC-1112 (3)) does not reach it.
>   - **The bar changes only by a recorded decision made before the round starts** (a KPI line inside the approved spec is a P2, the spec itself a P1, DEC-957). A fact the machine shows later is brought to the owner as the cause of the stop. A ticket that needs more than two rounds is split before it starts: each part is a ticket with its own count.
>   - **A fail-open an honest agent can hit, with no KPI line covering it, goes to the owner at once** as a P1 package (DEC-957, DEC-818), in any round: it is not a round and it is not held for a third.
>   - **READY is computed by code,** from the reviewer's `verdict` block: no KPI line marked fail and no finding that blocks. Until `verdict.py` is fixed (DEC-1131 (3)), the CTO reads a line marked fail as not READY by hand. A lead never writes a verdict over a reviewer's.

### 1.2 The open point, decided (DEC1010-REVIEW 4.4 point 1; DEC-1131 (2))

The worry was a real fail-open found in review 1, whose fix needed a third engineer pass. Decided as the owner said:
the fix pass belongs to the same round **if and only if** (a) every change in it fixes a finding the review marked
blocking, (b) each commit names that finding's id, and (c) it adds nothing else. The CTO checks (b) and (c) from the
commits (`git show --stat` per commit; the finding id is in the commit body). The review that follows the fix pass is
the next review round, so **reviews stay at two**; after review 2 no fix pass is made without the owner (or, for a
fail-open, the P1 route). What is counted is the judgement, so a fix pass cannot be a loophole: its judge is the
second review, and the second review is the last.

### 1.3 Evidence (CAP-33 step 1)

| # | Evidence | Source | Measured |
|---|---|---|---|
| E1 | DEC-1010 binds the review round only; no text caps a designer's, an engineer's or a product-spec session's passes | DEC1010-REVIEW sections 1 and 2.2 | 5 kinds of session, 1 carries a rule on findings |
| E2 | Seven tickets went past two rounds in some role this week; the owner was asked for two of them | DEC1010-REVIEW 3.1 | W2-20, W2-148, W2-149, W2-128, W2-153, W2-56, ACT-W2-149-INSTALL-1 |
| E3 | Most extra rounds were scope or interface, not reviewers who would not stop | DEC1010-REVIEW 3.3 | scope added after round two 4; interface read two ways 1; environment 3; real fault 3; rebuild 1 |
| E4 | Nine places let a round open new scope (a declared round, a ride-along, "would make the verdict wrong", a finding becoming a test, a KPI fail that does not block, the CTO's P2, a per-manifest count, a feature-gated risk, a re-probe) | DEC1010-REVIEW 2.5 | 9 rows |
| E5 | Two texts contradict a decision: `role-reviewer.md` line 24 tells the reviewer to hold two rounds although DEC-096 says no session is told its count; `role-lead.md` line 42 says "three iterations" and line 48 "never a third round" | DEC1010-REVIEW 2.2 | 2 contradictions |
| E6 | A KPI line has no id in the ticket or its schema; ids exist by position only | DEC1010-REVIEW 2.3; `src/gov/brief/build.py` `kpi_rows` lines 109-126 | S<n>/F<n> by position |

### 1.4 Corroboration (CAP-33 step 2)

The week's counts are a second method on the first: DEC1010-REVIEW cross-checked review-record verdict blocks against
commit subjects. This record adds one more check by a different route: W2-20's labels in `git log` (the
engineer's "W2-20 round 3" at 15:24 and "round 4" at 16:09, the designer's "round 8" at 15:59 on 2026-11-09) agree
with the review's table (engineer 4, designer 7 by commits and 8 by the launch log). **A limit, said plainly:** both
counts rest on labels the CTO wrote, and the spend log names tickets and roles only from 2026-11-10 11:47. The
independent reviewer of this record should recount W2-20 from `git log` and the review records before trusting 3.1.

### 1.5 Decisions this record takes where DEC-1131's text is silent

Each is flagged for the reviewer and the owner. None widens anything; each is the narrowest reading.

| # | Where the text was silent | Taken here | Why |
|---|---|---|---|
| D-1 | What a finding that needs a deliberate construction does to a KPI line | It is a row and fails no line (DEC-801 stays inside the KPI rule) | The threat model (ADR-0001) bounds what a line can mean; without it every adversary-only case blocks a line |
| D-2 | A finding with "ordinary work: yes" and "consequence: other" that names a KPI line | It fails that line and blocks. This replaces DEC-1010's three-part test for findings on a line | "Judged against the KPI lines" is the owner's principle (DEC-1128 (5)); W2-20's S16 was such a case |
| D-3 | DEC-802 (accepted fixes ride along in a resume that happens anyway) | A pass that carries a row beside blocking fixes is not a blocking-only pass: it is a round | DEC-1131 (2) allows only the blocking-only pass inside the same round; this is the same text read the other way |
| D-4 | Tickets open on the promotion date | The count starts at promotion. Earlier rounds are in the ledger for information only. DEC-1010's old cap on reviews (two) still holds for a ticket whose reviews are already two | A rule cannot reach back; a ticket already at two reviews gets no third |
| D-5 | What the round counts | The judgement. A worker pass counts through the judgement it precedes | A pass is hard to define (a resume, a batch); a judgement is a record |
| D-6 | DEC-916's "per declared round" | Retired. A multi-phase ticket is split before it starts | A declared "round 2a" and "2b" gave W2-128 three reviews |
| D-7 | Red-fix work in other tickets' tests caused by this ticket (W2-20's "D-10 red fix" commits, W2-153's 58 reds) | It counts on the ticket it is filed under, never on the cause's | Else a ripple eats the cause's two rounds; the cause is told to the owner under clause "bar changes by decision" |
| D-8 | Whether the ticket's KPI id is written or derived | Derived by position now (`S<n>`, `F<n>`); an optional written `id:` that must equal the position until `gov brief` reads it | Needs no edit to a reviewed ticket; section 2.5 |
| D-9 | The w2 prompt says "Only the owner changes it" | The owner's approval of this record is the package the prompt asks for (line 7); the CTO commits the section 14 change on that approval | One approval, not two |

---

## 2. Every change, by file, as the exact new text

**Kernel** means a file under `template/governance/kernel/` or its copy under `template/.rulesync/`. A kernel change
follows CAP-33: this record (proposal), an independent review, the owner's approval, and a version. The generated
copies in `.claude/{agents,skills,templates}/` are installed by the owner's operator as an ACT, class (b)
(`class-rules.yaml` row `agents-skills-kernel`), as ACT-CLAUDE-COPIES-1 and -2 were. **Project** means a file under
`governance/project/`; it follows the owner's approval of this record and the CTO commits it.

Line numbers are the files as they stand at `625aa084fa02` on 2026-11-11. The "before" is quoted from that file; where a
line is long I quote the part that changes and mark it with "...".

### 2.1 Text R's four homes (project files; Text R is the same words in each)

| # | File | Kind | Lines | Before | After |
|---|---|---|---|---|---|
| 1 | `governance/project/briefs/JUDGEMENT.md` | project | 3 | "Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. ..." | "Every brief you write carries the bar in `brief.md`; every reviewer, probe and auditor brief carries this whole section, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines." |
| | | | 9 | "**Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (...) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically." | "**A finding marked "no" on the first question is a row automatically.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a round (DEC-801). A finding with "yes" on both questions that names no KPI line goes to the owner as a P1 package at once (DEC-957, DEC-1131); a finding that names a KPI line it fails fails that line." |
| | | | 11 | "**No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802)." | "**No extra round on its own:** a ticket that resumes anyway carries only the findings its review marked blocking, each named by id; anything else in the pass makes it a round (DEC-802, DEC-1131)." |
| | | | 12 | "**Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803)." | "**Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on: it becomes a KPI line of that ticket by a decision before its first round, never a finding of an earlier one (DEC-803, DEC-1131)." |
| | | | 14 | "These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47)." | unchanged |
| | | | 18 | "...only "yes" with "fails open" or "loses work" fails the probe." | "A finding marked "no" is a row for the Wave 3 hardening pass, never a round. A finding that names a KPI line it fails, with "yes", fails that line and the probe; one that names none is a row, or a P1 package if it fails open." |
| | | | 19-23 | the five bullets "How reviews converge ... (DEC-1010 item 1 ...)": moderator; "blocks only if in scope, reachable in ordinary work, and fails open or loses work"; "At most two review rounds"; "READY is computed by code ..." | **Text R** (section 1.1), followed by this one bullet that keeps DEC-1010's moderator and the verdict form: "**The moderator** (the QA engineer or the Senior Engineer; until the three layers start, the CTO) checks each finding's KPI id against that line's words and moves any finding whose line it does not fail to a row. **The verdict block** is unchanged: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`, one entry per KPI line, a finding written under the line it fails (its scope is `in`); rows go in the record's `## Rows`, not in the block." |
| 2 | `governance/project/briefs/LEAD-w2-common.md` | project | 122-126 | the "How reviews converge for your ticket" bullet and its four sub-bullets | **Text R**, with the heading's first words kept: "**One bar, two rounds for your ticket (owner, standing, DEC-1131, widening DEC-1010 item 1 ...)**" |
| | | | 127 | "**For you as lead:** you hold at most the two review rounds your plan declares; you send every finding to the moderator's triage in your return (scope, ordinary work, consequence), never decide a FAIL away yourself, and never start a third round." | "**For you as lead:** you hold the count of rounds per role for your ticket (n of 2, never told to a worker), tell the CTO each judgement for its ledger as you meet it, send every finding to the moderator in your return with the KPI id it fails or "row" (and ordinary work, consequence), never decide a FAIL away yourself, and never start a round the owner has not given. After a role's second round a failed KPI line goes to the CTO as ESCALATION with each line's state and both rounds' evidence." |
| | | | 132 (last sentence) | "A reviewer's second pass is the last (DEC-413); a ticket run in rounds declared in its plan before they start gets up to two reviews per declared round, and undeclared rounds earn none (DEC-916); a third is only the owner's exception." | "A reviewer's second pass is the last (DEC-413, DEC-1131); a declared "round 2a" or a new name does not restart the count, and a ticket that needs more rounds is split before it starts (DEC-1131, replacing DEC-916's per-declared-round half); a third round is only the owner's." |
| | | | 162 (step 4, last bullet) | "if red: a fresh implementer with the failing output only. You hold the loop count and tell nobody (DEC-096); after three consecutive iterations that don't converge, return ESCALATION." | "if red: a fresh implementer with the failing KPI lines' ids and their output only. You hold the count and tell nobody (DEC-096); a KPI line still failed after the engineer's second round: return ESCALATION (DEC-1131). Three consecutive iterations that do not converge stay the rule for a loop with no KPI line, such as a refused close (DEC-096, DEC-487)." |
| | | | 163 (step 5, last sentences) | "...then a fresh engineer, then a second and last review (DEC-413; per declared round, DEC-916). The rest are residuals you return." | "...then a fresh engineer given the blocking findings' ids only (the same round, DEC-1131 (2)), then a second and last review (DEC-413, DEC-1131). The rest are rows you return." |
| 3 | `governance/project/briefs/AUDITOR-common.md` | project | 28 | same as JUDGEMENT line 9 | as JUDGEMENT line 9 after |
| | | | 30, 31 | as JUDGEMENT lines 11, 12 | as JUDGEMENT lines 11, 12 after |
| | | | 38 | "...only "yes" with "fails open" or "loses work" fails the audit's item." | "... A finding that names a Contract item or decision whose row it fails, with "yes", fails that item; one that names none is a row, or a P1 package if it fails open." |
| | | | 39-43 | the five "How reviews converge" bullets | **Text R**, with "KPI line" read as "the Contract item or decision in scope" for an audit, and the moderator bullet as in row 1 |
| 4 | `governance/project/prompts/w2-orchestrator.md` | project, **owner's file** (line 7) | 173 | "...The lead holds the loop count and never discloses it (DEC-096); after three consecutive iterations that don't converge, it returns an escalation package." | "...The lead holds the count per role and never discloses it (DEC-096); a KPI line still failed after a role's second round: it returns an escalation package (DEC-1131). Three consecutive iterations that do not converge stay the rule for a loop with no KPI line (DEC-096)." |
| | | | 310 | as JUDGEMENT line 9 | as JUDGEMENT line 9 after |
| | | | 312 | as JUDGEMENT line 11 | as JUDGEMENT line 11 after |
| | | | 313 | "**Reviews per round (owner, standing, DEC-916):** a ticket run in rounds gets up to two reviews per round ..." | deleted; its place is taken by Text R's third and sixth bullets (DEC-916's per-declared-round half is retired by DEC-1131) |
| | | | 314 | feature-gated (as JUDGEMENT line 12) | as JUDGEMENT line 12 after |
| | | | 316-320 | the five "How reviews converge" bullets | **Text R** and the moderator bullet |

The prompt's section 14 is a word-for-word copy of JUDGEMENT.md plus the DEC-916 bullet (line 313), which JUDGEMENT.md
lacks. After this change both hold Text R and neither holds DEC-916's bullet.

### 2.2 The brief envelope and the role templates (kernel; version 1.0.0 to 1.1.0 each)

Every added line ends with a decision id in brackets, an ACCEPTED one (DEC-1073's rule in `role-product-spec.md`
line 6). The prose budgets in `facts.yaml` (3,500 characters for each role template, 8,000 for the lead's, 4,000 for
the brief) leave room: each added block below is under 500 characters; the CTO runs `prose_size` over each file in the
product-spec ticket. No worker template gives a count (DEC-096).

| File | Line | Before | After |
|---|---|---|---|
| `templates/brief.md` | after 21 ("Non-goals ...") | none | "The bar is these KPI lines and nothing else: a test, a change or a finding names the id it serves or fails; one that names none is a row for the list, not work for this assignment [DEC-1131]." |
| | 27 | "{REPAIR: the failing output, verbatim, and nothing else of earlier rounds}" | "{REPAIR: the failing KPI lines' ids and their output, verbatim, and nothing else of earlier rounds}" |
| `templates/role-reviewer.md` | 3 front matter | `version: 1.0.0` | `version: 1.1.0` |
| | 12 | "3. Look first for lost work, a role writing outside its scope, an implementer able to change acceptance tests, a guard or gate failing open [DEC-137]." | unchanged (the open hunt stays; what it may raise is bounded below) |
| | after 22 | none | "- Mark a fail-open an honest agent can hit that no KPI line covers `P1` on the first line of your return; it is not a row [DEC-957, DEC-1131]." |
| | 23 | "- Block only on a finding in scope (the KPI lines, not the non-goals), reachable in ordinary work, that fails open or loses work; every other finding lands as a recorded row [DEC-1010]." | "- Name on every finding the id of the KPI line it fails and mark that line `fail`, which blocks; a line marked `pass` carries no finding. A finding that names no line, or needs a deliberate construction, is a row under `## Rows`, never a blocker [DEC-1131, DEC-801]." |
| | 24 | "- Hold at most two review rounds; then the owner once, with options [DEC-1010]." | "- Never count or ask for a round: the CTO counts them and no session is told the number [DEC-096, DEC-1131]." (this is the fix for the contradiction with DEC-096) |
| | 25 | "- Start no round of its own for accepted fixes when the ticket resumes anyway [DEC-802]." | unchanged |
| | 28 | "- Leave READY to code: it is computed from your verdict block, and no lead writes a verdict over yours [DEC-1010]." | "- Leave READY to code: it is computed from your verdict block (a line marked `fail` is not READY), and no lead writes a verdict over yours [DEC-1010, DEC-1131]." |
| | 35 (end) | "Describe each finding as behaviour ..." | adds: "Put each row after the block under `## Rows`, with its two lines [DEC-808]." |
| `templates/role-test-designer.md` | 3 | `version: 1.0.0` | `version: 1.1.0` |
| | after 23 | none | "Write tests only for KPI lines and the stated interface, each case naming its KPI id; a review finding that names no KPI line is a row for the list, never a test [DEC-1131]." |
| `templates/role-engineer.md` | 3 | `version: 1.0.0` | `version: 1.1.0` |
| | 13 | "4. Write no code for cases beyond the KPI lines; a refusal KPI must still refuse, so never make a guard or gate fail open [DEC-135]." | "4. Write no code for cases beyond the KPI lines, and cite the KPI id each change serves in your commit body; a refusal KPI must still refuse, so never make a guard or gate fail open [DEC-135, DEC-1131]." |
| | after 20 | none | "A fix pass given review findings carries those findings only: name each finding's id in the commit body and change nothing else [DEC-1131]." |
| `templates/role-product-spec.md` | 3 | `version: 1.0.0` | `version: 1.1.0` |
| | after 21 | none | "A change after a review cites the finding's id and the KPI line or Contract item it serves; a finding that names none is a row, not a change [DEC-1131]." |
| `templates/role-research.md` | 3 | `version: 1.0.0` | `version: 1.1.0` |
| | after 19 | none | "Your bar is the question and stop rule you stated in step 2. At the stop rule write the verdict you have and what stays unmeasured, and stop: a second pass is a new ticket by a decision [DEC-1131]." |
| `templates/role-lead.md` | 3 | `version: 1.0.0` | `version: 1.1.0` |
| | "Every run", after 29 | none | "- Keep this ticket's rounds per role (n of 2) in {CHECKPOINT_FILE}; tell no worker the number, and give the CTO each judgement for its ledger as you meet it [DEC-096, DEC-1131]." |
| | 42 | "4. Red: a fresh implementer given the failing output only. Three iterations that do not converge: return ESCALATION [DEC-096]." | "4. Red: a fresh implementer given the failing KPI lines' ids and their output only. A KPI line still failed after the engineer's second round: return ESCALATION with each line's state and both rounds' evidence [DEC-1131]. A loop with no KPI line, such as a refused close, escalates at three [DEC-096]." |
| | 47 | "3. Fail: put the triage of every finding in your return; a fix starts with a test-design batch given the finding as a described behaviour [DEC-136]." | "3. Fail: put every finding in your return with the KPI id it fails or \"row\"; a fix starts with a test-design batch given the finding as a described behaviour [DEC-136], then an engineer given the blocking findings' ids only, in the same round [DEC-1131]." |
| | 48 | "4. Never decide a FAIL away; never a third round [DEC-1010]." | "4. Never decide a FAIL away, and never open a round the owner has not given; after the second review a failed KPI line goes up as ESCALATION [DEC-1010, DEC-1131]." |
| | 68 (hand-over) | "Rounds: converged or in progress (no count)" | "Rounds: per role, n of 2 and each verdict (never told to a worker)" |
| `templates/role-cto.md` | 3 | `version: 1.0.0` | `version: 1.1.0` |
| | "Returns and decisions", after 23 | none | "- Keep the round ledger by hand ({LEDGER}): one row per judgement, before you read the next worker's return; launch no worker for a ticket and role already at two judged rounds without the owner's decision naming a third [DEC-1131]." |

`{LEDGER}` is a new key; it is added to `templates/keys.yaml` and to `facts.yaml`'s `paths` (`ledger:
governance/project/orchestration/ROUND-LEDGER.md`), both in the same ticket. `facts.yaml` is project-owned.

The generated copies of these seven templates are inside `template/.rulesync/subagents/*.md` (each is the role
template followed by the role file). The mapping is: `independent-auditor` carries `role-reviewer`;
`independent-test-designer` carries `role-test-designer`; `engineer` carries `role-engineer`; `product-spec` carries
`role-product-spec`; `orchestrator` carries `role-lead`; `research` carries `role-research`. Each is regenerated in
the same commit as its source (W2-128 did the same) and carries the same words.

### 2.3 The role files (kernel; they state what the guard and launcher decide, so each gets one line in "Authority level", no permission)

| File | Line | Before | After (appended to the Authority level bullet) |
|---|---|---|---|
| `roles/independent-auditor.md` | 18-19 | "...Its findings are recommendations; contested and owner-level findings go to the owner as decision packages (MR-4)." | "... It is judged on the ticket's KPI lines and its findings name the line they fail or are rows; the CTO counts at most two rounds per ticket (DEC-1131). This is guidance, not a permission." |
| `roles/independent-test-designer.md` | 17-18 | "...a dispute goes to the orchestrator as a decision package." | "... It is judged on the ticket's KPI lines alone; the CTO counts at most two rounds per ticket (DEC-1131). This is guidance, not a permission." |
| `roles/engineer.md` | 16-17 | "...the dispute goes to the orchestrator as a decision package." | "... It is judged on the ticket's KPI lines alone; a fix pass for blocking findings is part of the round that found them; the CTO counts at most two rounds per ticket (DEC-1131). This is guidance, not a permission." |
| `roles/product-spec.md` | 18-19 | "...a gap, a dispute or an ambiguous KPI goes back to the orchestrator as a decision package with a recommendation and a confidence." | "... It is judged on the ticket's KPI lines alone; the CTO counts at most two rounds per ticket (DEC-1131). This is guidance, not a permission." |
| `roles/research.md` | 15-16 | "...a finding that changes the plan goes to the orchestrator as a recommendation." | "... Its bar is its question and stop rule; a second pass is a new ticket by a decision (DEC-1131). This is guidance, not a permission." |
| `roles/orchestrator.md` | 45-47 | "It holds the ticket's loop count and never discloses it (DEC-096)." | "It holds the ticket's rounds per role (two at most, DEC-1131) and never discloses the count (DEC-096)." |
| | 59-60 | "ESCALATION: what does not converge after three consecutive iterations, with the evidence (DEC-096)." | "ESCALATION: a KPI line still failed after a role's second round, with each line's state and the evidence of both rounds (DEC-1131); a loop with no KPI line escalates at three consecutive iterations that do not converge (DEC-096)." |

Each is mirrored in `template/.rulesync/subagents/<role>.md` (the role file is the second half of that file).

### 2.4 The kernel skills (kernel; versions bump)

| Skill | Lines | Before | After |
|---|---|---|---|
| `skills/test-design/SKILL.md` 1.2.0 to **1.3.0** | 26 | "3. Keeps each assertion traceable to a specific KPI line (CAP-38.b)." | "3. Keeps each assertion traceable to a specific KPI line, named by its id (CAP-38.b, DEC-1131)." |
| | 33 | "2. The test designer decides from the specification whether each finding becomes an acceptance test (DEC-136)." | "2. A finding becomes an acceptance test only if it states the behaviour of a KPI line and names its id; any other finding is a row for the list and no test is written for it (DEC-136, DEC-1131)." |
| | 34 | "3. A finding that reveals a specification gap is reported to the orchestrator so the specification can be amended before testing proceeds (...)." | unchanged (a line missing or wrong is a gap; it goes to the CTO, who changes the bar only by decision, DEC-1131) |
| `skills/audit/SKILL.md` 1.1.0 to **1.2.0** | after 49 | none | "- **One bar, two rounds (DEC-1131):** the bar is the Contract items and decisions in scope, one row each. A finding cites the row it fails; one that cites none is a row for the list, class SCOPE_CREEP when it asks for work no source asks for. A re-audit of the same milestone is at most one more round; an item still not OK after it goes to the owner as a decision package." |
| `skills/change/SKILL.md` 1.0.0 to **1.1.0** | after 32 | none | "## Rounds of a change\n\nA CIT-P's independent review is at most two rounds. Each finding cites the section of the proposal, the Contract item or the decision it fails; one that cites none is a row. A proposal still failing after round two goes to the owner with the options (DEC-1131). This skill grants no permission." |
| `skills/orchestration/SKILL.md` 1.2.0 to **1.3.0** | 31 | "- For a FULL ticket a second review is the last. After it only fail-open holes and losses of work are fixed (DEC-413 names silent changes to tests or ticket files); the rest are residuals (DEC-413)." | "- For a FULL ticket a second review is the last (DEC-413, DEC-1131). After it only fail-open holes and losses of work are fixed, and a fail-open an honest agent can hit goes to the owner at once as a P1 (DEC-957); the rest are residuals, as rows (DEC-413 names silent changes to tests or ticket files)." |
| | 33 | "- The loop count is held by the lead and never disclosed; three consecutive iterations that do not converge end in an escalation (DEC-096)." | "- The lead holds each role's round count (two at most) and never discloses it; a KPI line still failed after a role's second round ends in an escalation (DEC-1131). For a loop with no KPI line, three consecutive iterations that do not converge end in an escalation (DEC-096)." |

A check made while writing this: `tests/acceptance/W1-35/w1_35_orchestration_support.py` lines 164-173 read the
orchestration skill with regular expressions: "a second review is the last", "only fail-open holes and losses of work
are fixed", "the rest are residuals", "loop count ... never disclosed", and "escalat" with "three|3" and "converg".
Every one of those clauses is kept in the new words, so W1-35 stays green without a test revision. (If the reviewer
finds a clause lost, the remedy is a test designer's revision under DEC-866 with `Rewrite-Reason:`, as W2-128's
CIT-P section 4 did.)

Each skill is mirrored in `template/.rulesync/skills/<name>/SKILL.md` (byte copy), and `.claude/skills/<name>/SKILL.md`
by ACT. The `discovery`, `planning`, `retrieval`, `adopt` and `checkpoint` skills state no round and do not change.

### 2.5 The ticket template and schema: a KPI id (kernel; template 1.0.1 to **1.1.0**)

**The form.** A KPI line's id is `S<n>` for the n-th line of `kpis.success` and `F<n>` for the n-th line of
`kpis.failure`, counted from 1. This is already what `gov brief` prints (`kpi_rows`, `src/gov/brief/build.py` lines
109-126), what test designers' READMEs use, and what the verdict block's `"kpi"` carries. The rule makes it the one
name, and fixes it: **ids are never renumbered or reused after a ticket's first round**; a line that must go is changed
by a recorded decision (the bar changes only by decision) and its id is retired with it.

**How existing lines get one without editing a reviewed ticket.** They have it already, by position. A ticket with no
written `id:` is read with the position ids; nothing in any reviewed or closed ticket is edited, and the records
`gov.check.schema` validates (974 at W2-128's round 2a) stay valid because the field is optional (the same route the `non_goals` and
`{line, verify}` additions took in W2-128). A ticket still in flight may be given written ids by the CTO in one ticket
commit before its next round, each equal to its position, so no reader's id changes.

**Template text.**

`templates/ticket.md`, front matter line 3 `version: 1.0.1` to `version: 1.1.0`. The fenced block, lines 38-44:

Before:
```
kpis:
  success:
  - line: <one observable outcome, present tense> [DEC-n]
    verify: <a command and its expected result, or a file and what it shows>
  failure:
  - line: <what must never happen>
    verify: <the case that shows it refused>
```
After:
```
kpis:
  success:
  - id: S1                         # S<n> in success, F<n> in failure, counted from 1; the line's name in tests, findings and verdicts
    line: <one observable outcome, present tense> [DEC-n]
    verify: <a command and its expected result, or a file and what it shows>
  failure:
  - id: F1
    line: <what must never happen>
    verify: <the case that shows it refused>
```
"Filling it in", after line 59: "- Give each KPI line its `id` (`S1`, `S2` ... in `success`, `F1`, `F2` ... in `failure`). It must equal the line's place in its list. After the ticket's first round never renumber or reuse an id; a line that must change changes by a recorded decision [DEC-1131]."
After line 63: "- A test, a finding and a verdict name a KPI line by its id; a finding that names none is a row [DEC-1131]."

`schemas/ticket.schema.json`, `$defs.kpi_line`, object form (lines 9-18 of the file's `$defs`): add one optional property
and keep `additionalProperties: false`:

```json
"id": {"type": "string", "pattern": "^[SF][1-9][0-9]*$",
       "description": "The KPI line's name: S<n> in success, F<n> in failure, counted from 1; equal to its place until `gov brief` reads it (DEC-1131)."}
```
and the schema's top `description` gains: "A written KPI id is optional; a line without one is named by its position (DEC-1131)." The string form of a line has
no place for an id and is named by position.

**One code line this needs, not made here:** `kpi_rows` in `src/gov/brief/build.py` reading a written `id` over the
position and refusing a duplicate. Until it does, the template's rule "must equal the position" keeps both readings the
same. It goes in the counting-code ticket (section 4) as one of its parts. The text half does not wait for it.

### 2.6 Files that state nothing to change (checked)

`governance/project/operator/reviewer-brief.md` already holds the rule: "Every KPI line passes or the ACT is refused ...
a third round goes to the owner" (lines 46-47), is hashed and approved once, and is an (O) path. **Unchanged.** The
other kernel templates (`checkpoint.md`, `decision-*.md`, `failure.md`, `lesson.md`, `research.md`) state no round.
`CLAUDE.md`'s role line "engineer ... until its acceptance tests pass" and `template/.rulesync/rules/governance.md`
line 19 repeat DEC-957's superseded wording; that is a separate row (listed in section 6), not part of this change.

### 2.7 The register's notes at approval (the CTO's, DEC-851, not part of the ticket)

DEC-916: `Changed by: DEC-1131 (item 1): the per-declared-round half`. DEC-096: `Changed by: DEC-1131`. DEC-802:
`Changed by: DEC-1131`. DEC-1010 already carries its note. The decisions-in-force list and RESUME HERE state the new rule once, in
the CTO's own record (DEC-1073), not copied.

---

## 3. The round ledger, by hand (DEC-1131 (1), (4))

**Where:** `governance/project/orchestration/ROUND-LEDGER.md` (a new project file; the CTO's). Not a kernel file, not a
control path (`class-rules.yaml`: no row names it, so it is the catch-all, not an ACT's business).

**Who writes it:** the CTO, one row per judgement, in the same step as reading the return that carries it (a review
verdict, an acceptance run's result, a red check). A lead tells the CTO each judgement as it meets it (`role-lead.md`
"Every run"). The count is never put in a worker's brief (DEC-096): the ledger is a record the CTO reads, not text a
brief copies. (Reads are open under DEC-820, so a worker could read the file. DEC-096's rule is that sessions inside the
loop are not told; no brief names the file. This is named as a risk in section 5.)

**Columns:**

| Column | Holds |
|---|---|
| ticket | the ticket's id (`W2-20`) |
| role | `test-designer`, `engineer`, `product-spec`, `reviewer`, `auditor`, `act-reviewer`, `research` |
| round | 1 or 2; `3 (owner, DEC-n)` only with a decision id; `fix` for a blocking-only pass inside its round |
| date | the day of the judgement |
| what was judged | one line: what, and the head or hash (12 digits) |
| verdict | `pass`, `fail`, or `P1 (not a round)` |
| KPI lines failed | the ids (`S16, F2`), or `-` |

**Rules written at the top of the file** (so the CTO and a reader see them with the rows): the count for a ticket and
role is the number of rows with a round number; a `fix` row does not add one; a rename, a rebuild or a "2a" is not a new
ticket; a follow-up that reopens the same KPI lines uses the same ticket id; red-fix work in another ticket's tests is
that ticket's row; before launching any worker for a ticket and role whose count is 2 and whose last verdict is `fail`,
the CTO writes the escalation package instead (clause 5 of Text R); a third round row needs the owner's decision id.
An ACT reviewer's rows use the ACT id until ACT-OPERATOR-ROUNDS-1 makes the code count that way.

**Seeded with this week's counts** (DEC1010-REVIEW section 3.1 and 3.2, 11-04 to 11-11). These are *counts to date*,
not per-round rows: the review's own limits apply (labels from commit subjects; "~" may be one off; the spend log names
tickets and roles only from 11-10). The rule counts from promotion (D-4), so these rows are for information.

| ticket | role | round (to date) | date | what was judged | verdict | KPI lines failed |
|---|---|---|---|---|---|---|
| W2-20 | test-designer | 8 by the launch log (7 by commits) | 11-09 | red checks; S2, S10, S13 (interface), S16 (per CPU, DEC-1105), the CPU double count | past two; round 8 by DEC-1105 | S2, S10, S13, S16 |
| W2-20 | engineer | 4 | 11-09 | build; to the stated interface; F1 (race) and four ride-alongs; R2-F1 | past two; round 4 by DEC-1105 | not recorded |
| W2-20 | reviewer | 3 | 11-09 | r1 not READY (F1); r2 READY; narrow review of DEC-1105's two points | third by DEC-1105 | not recorded |
| W2-148 | test-designer / engineer / reviewer | ~4 / 5 / 5 | 11-09 | F15 (loses work), F21, the replay feature | past two; DEC-1106, DEC-1107, DEC-1108 | not recorded |
| W2-149 | test-designer / engineer / reviewer | ~4 / 6 / 6 | 11-09 to 11-10 | r1 not READY; r2 READY; F11; wiring review (13, none blocking); F18-F23; F36, F38 | past two; no exception asked | not recorded |
| ACT-W2-149-INSTALL-1 | act-reviewer | 5 reviews on 4 builds | 11-10 | v2, v3, v4 each READY by code with one KPI line failed | past two by manifest count | K7, K8, K7 |
| W2-128 | product-spec / designer / reviewer | 4 (+2) / 5 / 3 (+2, +1) | 11-09 to 11-10 | round 1; declared "2a" and "2b"; template 1.0.1; D-10 | past two by declaring | not recorded |
| W2-153 | test-designer / engineer / reviewer | ~8 batches / ~6 / 3 | 11-09 to 11-10 | R1's ~110 cases red in nine folders (ripple), a merge conflict | past two | not recorded |
| W2-56 | test-designer / engineer / reviewer | 4 / 2 (+1) / 2 | 11-09 | the D-13 socket fact (environment) | owner decided, DEC-1114 | not recorded |
| W2-96 | test-designer / engineer / reviewer | 3-4 / 2 / 3-4 | 11-09 to 11-10 | r1 F1; r2 READY; probe-r3 (DEC-895's re-probe); lift maps | past two by labels | not recorded |
| W2-141 | test-designer / engineer / reviewer | 3 / 3 / 2 | 11-09 | review 1: four real blockers; READY at review 2 | within the rule if the engineer's third pass was blocking-only (it was a fix pass) | the guard-bypass lines |
| W2-145, W2-152, W2-129, W2-55, W2-135, W2-116 | reviewer | 2 each | 11-04 to 11-10 | | READY | - |
| W2-142, W2-147, W2-150, W2-151 | reviewer | 1 each | 11-04 to 11-10 | | READY | - |

---

## 4. What this does not change

1. **The two code fixes of DEC-1131 (3), each by its own route, now, separate from this record:**
   - `verdict.py` (`governance/project/operator/verdict.py`, an (O) operator path, so by the owner's ACT; and the CTO's
     copy in `tools/`): READY needs no KPI line marked fail (the docstring's lines 9-10 and the code at 38-39 now say a failed
     line with no blocking finding does not block). Text R's last bullet says the CTO reads a failed line as not READY by hand until it lands.
   - `operator_run.py` (lines 308-320 and 448-453): count verdict blocks by ACT id, not by manifest
     (ACT-OPERATOR-ROUNDS-1).
2. **The counting code, after two weeks of use.** Proposed ticket: **W2-180** (the CTO files it; W2-170 to W2-179 are
   reserved by the memory-audit brief, and W2-174 is the adopted-repository `Verify:` ticket). Its parts: a counter that
   reads the ledger (or the spend log's `ticket` and `role` fields) at `gov launch` and refuses a third round without a
   recorded override with a decision id (the launch already has one, DEC-1088 (5)); `kpi_rows` reading a written
   `id:` (section 2.5); a ready-check warning for a KPI id that differs from its position. Start: two weeks after the
   promotion date (for example, promoted 2026-11-12, the ticket may start 2026-11-26), with the ledger's rows as its
   evidence. The counter is not a guard rule, so DEC-1128 (2)'s 100 % bar is not what governs it; DEC-1047's basis (5)
   is ("a practice enters the product only after it has proven itself in use").
3. **`src/gov/close/state.py` `ESCALATION_AT = 3`, `src/gov/close/command.py`:** left alone. They count refused
   closes, a mechanical loop (DEC-487); lowering them would turn environment reds into owner stops. The new text says so
   where it matters (`role-lead.md` line 42; the lead brief step 4).
4. **The ACT reviewer's brief** (`reviewer-brief.md`): left alone (section 2.6).
5. **DEC-1112 (3) otherwise:** every other P2 is still the CTO's. Only a third round, and a change of a standing
   decision, are the owner's by this rule.
6. **The threat model, the two questions, the `Ordinary work` and `Consequence` lines, DEC-801, DEC-803, DEC-809:**
   kept. They now decide whether a finding is a row, a P1, or a failed line; they no longer decide alone whether a
   round happens.

---

## 5. Risks and the review

### 5.1 What could break, and the answer

| # | Risk | Answer in this change | What stays open |
|---|---|---|---|
| R1 | **A real fail-open found late** (DEC-957's P1 route). It is found in review 2, or after it | Clause 7 of Text R: it goes to the owner at once, in any round; it is not a round | The CTO's discipline: a fail-open written as a "row" to save a round. The reviewer's first-line `P1` mark and the owner's digest are the check |
| R2 | The blocking-only fix pass becomes a loophole (a "fix" that adds a test) | Three conditions in 1.2; a pass with anything else is a round; the CTO reads `git show --stat` per commit | The CTO reads the commits by hand until W2-180 |
| R3 | More work for the owner: seven tickets this week would have reached the owner at round two, about one decision a day (DEC1010-REVIEW 4.3) | Each is a short package: narrow, split, defer or one more round | If the owner finds the volume too high, the owner changes the rule by a decision, not the CTO by a finding |
| R4 | A badly written KPI line blocks and no one may judge it away | The remedy is a decision that changes the line before the next round (clause 6), a P2 inside the approved spec | A line wrong in the approved spec is a P1 |
| R5 | An environment fact found late (W2-56's socket, W2-153's ripple) stops a ticket at round two | Brought to the owner as the cause of the stop (clause 6); red-fix work counts on its own ticket (D-7) | The owner may see an unlucky ticket stop; that is the owner's principle |
| R6 | An old ticket with no `id:` has an id that differs from the one in a test designer's README | Both are position ids today; nothing is renumbered after round one | A reorder before round one: the template says do not |
| R7 | The skills and templates are copied into `.claude/` and `template/.rulesync/`; a copy left stale tells a session the old rule | The edits and their copies are one commit; the `.claude/` copies by ACT (ACT-CLAUDE-COPIES-3, class (b)) | A launched session reads `.claude/` copies: until the ACT runs, an old copy is live |
| R8 | The ledger is readable by a worker (reads are open, DEC-820), against DEC-096's "never disclosed" | No brief names the file or copies a count; the count lives only with the CTO and lead | A worker that goes and reads it learns its count; DEC-096 is kept in the briefs, not in file permissions |
| R9 | DEC-916's half is retired by an owner who did not say so in words | DEC1010-REVIEW 2.5 row 1 and DEC-1131 (1) name the declared-round door; D-6 lists it for the owner to confirm | Confirm D-6 at approval |
| R10 | A test elsewhere reads a text word for word (W1-35's orchestration clauses; W2-128's template cases; unit tests in `tests/unit/brief`, `tests/unit/launch`) | Section 2.4's check of W1-35; the product-spec ticket runs `select_tests.py` for its scoped set and the template suites | A case found red is named, not fixed outside the ticket |

### 5.2 Dry run on past cases (a check of the rule against the week, by the same table)

| Case | What the rule does |
|---|---|
| **W2-141** (four real blockers in review 1, READY at review 2) | Review 1 marks the four guard-bypass lines `fail`; the designer batch and the engineer's pass fix those findings only, each commit naming its id: same round. Review 2 is READY. Nothing stops. Without the 1.2 clause the engineer's third pass would have been round 3. This is the open point doing its job. |
| **W2-20** (designer to round 8) | Round 2 ends with the designer and engineer reading S2, S10, S13 differently and S16 failing on the machine's background load: four KPI lines failed after round two. The CTO writes one package (the four lines, both rounds' evidence, the options) instead of four rulings and DEC-1105. The real race (F1) is a review-1 finding on a line, fixed in the same round. |
| **W2-149** (engineer to round 6) | After review 2 the live-run finding, the wiring review's 13 and F18-F23 name no KPI line: rows, no round. If the owner wants them done (DEC-1112 (3)'s wiring scope) that is a bar change by decision before a round. |
| **ACT-W2-149-INSTALL-1** | The second review marks K7 fail: the owner is asked then, not after a fifth review (the code count follows with ACT-OPERATOR-ROUNDS-1; by hand in the ledger until then). |
| **W2-128** ("2a", "2b") | The declared rounds do not restart the count; review 2a's five findings named no KPI line, so they are rows; no 2b. |

### 5.3 The independent review (CAP-33 step 4)

One fresh read-only reviewer who did not write this record, under the rule itself: at most two rounds, each finding
naming the section of this record, the Contract item or the decision it fails, or a row. The CTO briefs it with
`role-reviewer.md` and this record's path only. **Its checks:**

1. **Verbatim "before" text:** every quoted "before" in section 2 is in the file at that line (Grep).
2. **Nothing left behind:** after the edits, no kernel or project text states "three iterations" or "three consecutive"
   for a role's rounds (only for the loop with no KPI line), nor "per declared round", nor the three-part test as the
   only block, nor `role-reviewer.md` line 24's old words. (Grep over `template/`, `governance/project/`, `.claude/`.)
3. **Text R is one text:** the four copies (JUDGEMENT.md, the lead brief, the auditor brief, prompt section 14) are
   identical but for the stated "KPI line" reading in the auditor brief (diff).
4. **Contradictions closed:** DEC1010-REVIEW's two (`role-reviewer.md` 24 against DEC-096; `role-lead.md` 42 against 48)
   are gone, and no new one is made (the mechanical loop at three against the roles' two is stated in each place).
5. **Budgets and form:** each role template's prose within the `facts.yaml` budget (`prose_size`); each added rule line ends with an
   ACCEPTED decision id; `python3 -m gov.check.schema` still validates every record with the optional `id`; the new
   `{LEDGER}` key is in `keys.yaml` and `facts.yaml`.
6. **Tests that read the text:** W1-35's orchestration clauses and W2-128's template cases hold (a scoped run by the
   product-spec ticket, never the full suite, DEC-968).
7. **Recount** of W2-20 from `git log` and its review records (section 1.4's limit), and of one ticket the table says
   kept to two (W2-141).
8. **D-1 to D-9** (section 1.5): does each stay inside DEC-1131's words? The reviewer names any it reads as wider.
9. **Ledger seed:** each row matches DEC1010-REVIEW 3.1 and 3.2.

### 5.4 Versions and the route to promotion

| Step | State |
|---|---|
| Evidence | Section 1.3 |
| Corroboration | Section 1.4 (with its limit) |
| Proposal | This record |
| Independent review | Section 5.3, at most two rounds |
| Owner's approval | The owner approves the bytes by hash, as DEC-1116 (templates 1.0.0 at `1bf23a0b3e77`) and DEC-1121/1122 (ticket template 1.0.1) did; the CTO brings the table of hashes (a TEMPLATES-APPROVAL-2) after the review |
| Versioned promotion | The kernel template set 1.0.0 to **1.1.0**: the seven role templates, `brief.md` and `ticket.md` each 1.1.0; the skills `test-design` 1.3.0, `audit` 1.2.0, `change` 1.1.0, `orchestration` 1.3.0; the roles and the schema change with the set (they carry no version of their own). One commit for the kernel half, with `Task:` the product-spec ticket and `Implements: DEC-1131` |
| Generated copies | `.claude/{agents,skills,templates}/`: ACT-CLAUDE-COPIES-3, class (b), by the operator agent on the owner's yes |
| Project half | JUDGEMENT.md, the lead and auditor briefs, prompt section 14, `ROUND-LEDGER.md`, `facts.yaml`: committed by the CTO on the owner's approval of this record (D-9); the register's notes (section 2.7) in the CTO's decision-record commit |
| Order | Ledger and project half can start on approval; the kernel half after the review and the owner's hash approval; the `verdict.py` and `operator_run.py` ACTs are independent of this order |

### 5.5 The three options (DEC-105; DEC-1131 chose A)

| Option | What it means | Cost |
|---|---|---|
| **A, chosen: the text now, the ledger by hand, the code after two weeks** | Sections 2 and 3 | The product-spec ticket (about 15 lines in about 14 files, one schema field), a reviewer's two rounds, the CTO's by-hand ledger |
| B (not chosen) | Text only, no code ever | The two code gaps stay |
| C (not chosen) | Only the two code gaps and KPI ids | Designer and engineer rounds stay uncapped |

---

## 6. Rows noticed while writing (not part of this change)

- `CLAUDE.md` line 13 and `template/.rulesync/rules/governance.md` line 19 still say the engineer "implements one
  ticket until its acceptance tests pass", against DEC-957 and `role-engineer.md` line 8 ("never to make the tests pass").
- JUDGEMENT.md is described as the prompt's section 14 "word for word" but lacks the DEC-916 bullet that section 14 has;
  after this change both hold the same Text R.
