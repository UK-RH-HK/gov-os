# DEC-1010 and one rule for every role: a read-only investigation (DEC-1128 (5))

Written 2026-11-11 for the owner. Read-only: nothing in the repository was changed; no test was run. Sources are the
register (`docs/DECISION_REGISTER.md`), the role files and templates under `template/governance/kernel/`, the briefs
under `governance/project/briefs/`, the operator's reviewer brief, the review records, `log/spend.jsonl` and the
commit subjects since 2026-11-04.

## The answer in six lines

- DEC-1010 binds **reviewers and the people who judge them** (the CTO, the leads, QA). It says at most two review
  rounds, then the owner once. It says nothing about test designers, engineers or product-spec.
- Of the five kinds of session, only the reviewer is told "judge against the KPI lines, block only in scope". The
  other three are told to build to the KPI lines, but no text caps their passes or says a finding outside a KPI line
  is a row.
- This week (11-04 to 11-11) the two-round rule held for most tickets. It broke on seven: W2-20, W2-148, W2-149,
  W2-128, W2-153, W2-56 and the ACT for W2-149. The owner was asked for only two of them (W2-20, W2-148).
- W2-20's test designer did reach round 7 by the commit labels (round 8 by the launch log). The reasons were
  mostly **not** reviewer findings: an interface the tests and the code read differently, and a CPU test that
  measured the machine's background.
- The ways a round opens new scope are specific and few. They are listed in section 2.5 and are the real cause.
- My recommended rule (section 4): the ticket's KPI lines are the only bar; every finding cites a KPI line or is a
  row; two rounds per ticket for every role, counted by the CTO, not reset by a rename or a rebuild; a KPI line
  still not met after two goes to the owner with the evidence. Confidence: medium-high on the rule, medium on the
  counting details.

---

## 1. DEC-1010 today

**Where:** `docs/DECISION_REGISTER.md`, entry DEC-1010 (line 12644), "Reviews converge; W2-81 lands; ...".

**Status line (word for word, the relevant part):** "ACCEPTED (owner, 2026-11-01, in the chat; ... standing) ·
Under: DEC-096, DEC-916, DEC-801 to DEC-803, DEC-1003, DEC-1007, DEC-1008 · Changes: DEC-916's 'a third review is the
owner's exception' (now: at most two rounds, then the owner once, with options); DEC-096 for reviews".
The entry has **no "Changed by" note of its own**. Nothing has amended it.

**Item 1, the rule (word for word):**
"How reviews converge (in force now, for the CTO, the leads, every reviewer and QA engineer): a moderator (the QA
engineer or the Senior Engineer; the CTO until the three layers) triages every finding against the ticket's own scope
and KPIs; a finding outside the scope, or needing an unusual construction, becomes a Wave 3 row, never a round; a
finding blocks only if in scope, reachable in ordinary work, and failing open or losing work; at most two review
rounds, then the owner once with options, no more routine exceptions; READY is computed by code from each reviewer's
structured verdict per KPI (pass or fail, each finding's scope and classification)."

**The other items** are not about rounds: item 2 maps the rules into the product (the round cap "enforced by the
queue and the dispatcher", READY from structured verdicts, as KPI proposals); item 3 a research session; items 4 to
7 are W2-81, W2-93, W2-117, the dispatcher in the repository, and the slots. Items 6 and 7 are cited by code
(`dispatcher.py`, `gate.py`); item 1 is cited by the briefs.

**Exceptions since (all by the owner, all recorded as exceptions "to DEC-1010"):**

| Decision | Date | What |
|---|---|---|
| DEC-1105 | 11-09 | W2-20: one exception round (S16's per-CPU measure, R2-F1's stale readings) |
| DEC-1106 | 11-09 | W2-148: F15 fixed in one exception round |
| DEC-1107 | 11-09 | W2-148: F21 in one tiny extra round |

**Used as a stop since:** DEC-1078 (2) (the memory-verdict set's cross-check ended at round 2: "no third round
(DEC-1010's two-round rule; the owner's decision)"; five majors left open); DEC-1097 (3) (the seven-reviewer
readiness review, "at most two rounds, the rest become rows (DEC-1010)"); DEC-1047's basis (2) uses its
"fails open or loses work" test as the test of what to keep.

**Related rules it touches:**
- DEC-096 (loop policy): escalate after three non-converging iterations; "the iteration count ... never disclosed to
  the sessions inside the loop". DEC-1010 changed it for reviews.
- DEC-916 (up to two reviews **per round declared in the ticket's plan**, a third is the owner's exception).
  DEC-1010 changed only the "third review" half. The "per declared round" half is still written in the lead brief
  (`LEAD-w2-common.md` line 132 and step 5 at line 163) and the w2 prompt §14 (line 313). This is the open door
  described in 2.5.
- DEC-1112 (3): "Every other P2 is the CTO's". DEC-1010 says "no more routine exceptions" (the owner's). Whether an
  extra round is a P2 (the CTO's) or a P1 (changes a standing decision, DEC-957's rubric) is not written down.

**Scope, in plain words.** It binds the review round. It is written for "the CTO, the leads, every reviewer and QA
engineer". It does not mention a designer's or an engineer's pass. It never says what a "round" is when a ticket has
a test designer, an engineer and a reviewer taking turns.

---

## 2. What each role is judged against today

### 2.1 Where the rules live (found)

| Text | Path | What it holds |
|---|---|---|
| Role files (what the guard and launcher decide) | `template/governance/kernel/roles/{engineer, independent-test-designer, independent-auditor, product-spec, research}.md` | Purpose, paths, tools, permissions. **No rule on KPIs, findings or rounds.** |
| Role templates (what each session is told) | `template/governance/kernel/templates/role-{reviewer, test-designer, engineer, product-spec, research, lead, cto}.md` | The working rules. Only `role-reviewer.md` carries the judgement rules. |
| JUDGEMENT.md (the canonical text) | `governance/project/briefs/JUDGEMENT.md` (copies under scratch and in clones; the w2 prompt §14 is a word-for-word copy) | Threat model, the two questions, DEC-1010 item 1, the verdict block |
| Lead brief | `governance/project/briefs/LEAD-w2-common.md` | The loop, "how reviews converge" (lines 122-127), DEC-916 (line 132) |
| Auditor brief | `governance/project/briefs/AUDITOR-common.md` | Same judgement text, lines 22-43 |
| Kernel skills | `template/governance/kernel/skills/{audit, test-design, change}/SKILL.md` | Method only; no round rule |
| Operator reviewer brief | `governance/project/operator/reviewer-brief.md` | Six fixed checks; code enforces two rounds |
| Ticket template | `template/governance/kernel/templates/ticket.md` and `schemas/ticket.schema.json` | KPI lines with `verify`, `non_goals` |

### 2.2 Role by role

| Role | Judged against | Works to known KPI lines and a specification? | How findings are bounded | Round limit in its own text |
|---|---|---|---|---|
| **Independent reviewer / auditor (QA)** | `role-reviewer.md`: "against the ticket's KPI lines and non-goals" (line 8); the two questions (lines 19-20); block only "in scope (the KPI lines, not the non-goals), reachable in ordinary work, fails open or loses work" (line 23); verdict block per KPI line (lines 31-34) | Yes, in the template. The brief gives the KPI table and non-goals. | Strong on paper: each finding carries `Ordinary work` and `Consequence`; the verdict gives `scope: in/out`. Everything else is a row. **But step 3 (line 12) tells it to look first for lost work, a role out of scope, a gate failing open, "behaviour the acceptance tests miss" (line 8): an open hunt, bounded only at triage.** | "Hold at most two review rounds" (line 24), though DEC-096 says the count is never disclosed to the session. It cannot know its round. |
| **Wave-exit auditor** (`audit` skill) | The Contract items and decisions in scope: "one row per contract item and decision in scope"; six classes, one is SCOPE_CREEP (SKILL.md lines 28-39) | Yes, to the Contract, not to ticket KPI lines. | A row per item, classified. Findings go to the owner as packages. | None. |
| **Independent test designer** | `role-test-designer.md`: tests from the ticket's KPI lines and sources, "at least one test per KPI line" (line 14); an ambiguous KPI "is never guessed" (line 23) | Yes: KPI lines and sources, never the implementation. | **No upper bound.** "At least one test per KPI line" has no "only". The `test-design` skill (lines 28-34) says a probe finding is taken "as a described behaviour" and the designer "decides from the specification whether each finding becomes an acceptance test". So a review finding that is outside a KPI line can still become a test, and a round. | None. |
| **Engineer** | `role-engineer.md`: "build the code to fulfil the spec and its KPIs, never to make the tests pass" (line 8); "Write no code for cases beyond the KPI lines" (line 13); runs acceptance once, pass or fail per KPI line (line 15) | Yes. The best-bounded role. | Item 4 bounds it. A repair pass gets "the failing output, verbatim, and nothing else" (`brief.md` line 27). | None. The lead's rule counts non-converging iterations at 3 (DEC-096; `role-lead.md` line 42). |
| **Product-spec** | `role-product-spec.md`: writes the KPI lines and specs; "take the simplest reading ... never widen the scope" (line 21); a kernel change only under the ticket's CIT-P (line 13) | It writes the specification. Its own KPI is the ticket's. | The simplest-reading rule bounds interface points. Nothing says a review finding must cite a KPI line before it changes a spec. | None. |
| **The ACT reviewer** (operator) | Six fixed checks (`reviewer-brief.md` lines 10-29); every check "passes or the ACT is refused: a fail refuses even without a blocking finding" (line 46) | **Yes, the best example in the repository:** a closed list, fixed by hash, approved once. | Findings sit inside the six checks. | "A second round appends a second block; ... a third round goes to the owner" (line 47). **Enforced in code:** `operator_run.py` lines 448-453 refuse a third verdict block and notify the owner. |
| **Probe** (record under `docs/probes/`) | Same as the reviewer; the A3 brief | As the reviewer. | As the reviewer. | As the reviewer; DEC-895 adds a re-probe after a merge that touched probed files. |
| **Research** | `role-research.md`: runs an experiment and leaves an evidence record | The question is its brief, not KPI lines. | None. | None. It has no rounds in the ticket loop. |
| **Lead** (`role-lead.md`) | "to the Definition of Done"; the loop | Yes. | "Put the triage of every finding in your return"; "Never decide a FAIL away; never a third round [DEC-1010]" (line 48) | Says "three iterations that do not converge: ESCALATION [DEC-096]" (line 42) and "never a third round" (line 48): two different counts in one file. |

### 2.3 Do the roles work to KPI lines and a specification?

Yes for the engineer and the test designer: the ticket template (`ticket.md` lines 38-44) gives each KPI line a
`verify`; the generic brief (`brief.md` lines 19-22) hands the worker a KPI table, the non-goals and the DoD.
The ticket states the interface (line 63). That is a specification a worker can be held to.

**One gap in the form:** a KPI line has **no id** in the ticket or its schema (`ticket.schema.json` lines 9-18: a
string, or `line` and `verify`). The ids "S1 to S21" and "F1 to F6" are made by the test designer's README, by
position. The verdict block cites `"kpi": "<line id>"`. So "every finding cites a KPI line" works today only by
convention, and a reorder of the lines changes the ids.

### 2.4 How findings are bounded today

For a reviewer the bound is `JUDGEMENT.md` lines 19-23. In practice the bound has two weak points this week:

1. **READY looks at findings, not at KPI lines.** `verdict.py` (lines 11-12) says "A KPI line marked fail with no
   blocking finding does not block on its own". So a ticket can be READY while a reviewer marks a KPI line failed.
   The owner's principle (DEC-1128 (5)) is "judged against the KPI lines". For an ACT the rule is the opposite and
   matches the principle (`reviewer-brief.md` line 46). The two paths disagree.
   Example: the review of ACT-W2-149-INSTALL-1 at its v2, v3 and v4 builds was READY by code each time, with one KPI
   line marked fail each time (K7, K8, K7). Each time the CTO rebuilt and re-reviewed.
2. **"Ordinary work: yes, Consequence: other" is not blocking, yet gets fixed.** W2-149's wiring review (F18 to
   F23) had six such findings. None blocked. The CTO put them in the ticket and ran a round "before the owner is
   asked" (DEC-1112 (3)), because they would make the experiment's verdict wrong. That test is in DEC-1097 (3) ("only
   what fails open or would make the verdict wrong") but is not in DEC-1010's three-part test or in `JUDGEMENT.md`.

### 2.5 The rules that let a round open new scope (found)

| # | Rule or practice | Where | Effect seen this week |
|---|---|---|---|
| 1 | **DEC-916, "per declared round"**: a round declared in the ticket's plan before it starts gets its own two reviews | `LEAD-w2-common.md` 132 and 163; w2 prompt §14 line 313 | W2-128 declared "round 2a" and "round 2b" (ticket lines 157 and 170, "stated 2026-11-09, DEC-1112 (3)"): three reviews on one ticket. Round 2a had 5 findings, none blocking; round 2b fixed four of them. |
| 2 | **DEC-802, "accepted fixes ride along in a resume that happens anyway"** | `JUDGEMENT.md` 11 | W2-20 round 3 fixed F2, F4, F6, F8 (non-blocking) beside the blocking F1. |
| 3 | **"Would make the verdict wrong"** (DEC-1097 (3)) | register | W2-149 F18-F23 above. |
| 4 | **Test-design skill: a finding "becomes an acceptance test" if the designer decides so** | `test-design/SKILL.md` 28-34 | A finding outside every KPI line can still start a designer round. |
| 5 | **verdict.py: a failed KPI line does not block** | `verdict.py` 11-12 | See 2.4 (1). |
| 6 | **DEC-1112 (3): "every other P2 is the CTO's"**, and an extra round not being named a P1 | register | Rounds on W2-128, W2-149, W2-153, W2-96 were the CTO's. Only W2-20 and W2-148 went to the owner. |
| 7 | **The operator's cap counts per manifest**, so a rebuilt ACT starts at zero | `operator_run.py` 308-320, 448-453 | ACT-W2-149-INSTALL-1: five reviews on four builds. |
| 8 | **DEC-803, feature-gated risks become the entry criterion of the ticket that switches the feature on** | `JUDGEMENT.md` 12 | Moves a risk into a ticket's scope. Reasonable, but it is scope, not a finding. |
| 9 | **DEC-895, a re-probe after a merge** | lead brief 71 | W2-96 had "probe-r3" on the merged head. Not a round by its own rule; labelled like one. |

---

## 3. Rounds actually taken this week (about 11-04 to 11-11)

**How I counted (and its limits).** `log/spend.jsonl` holds named launches only from 11-07; it has `ticket` and `role`
fields only from 11-10 11:47. Before that, a round is recognised by the review record's verdict blocks, commit
subjects ("round 2", "READY at round 2") and the spend log's free text. I cross-checked the heaviest tickets against
their review records and commits. Numbers marked "~" are from labels and may be one off. `dispatch/started.txt` ends on 11-02 and
adds nothing for the week.

**Count of the week.** About 95 review records carry a verdict block and a file date from 11-04 on (five are
duplicates in two folders; the file date is the last edit, so a few are older). About 77 hold one verdict block, about
17 hold two, and two hold three (W2-20, with DEC-1105's exception; the fresh-80 scripts, whose third block is a
diffs-only delta read at the pre-flight). The rows below are the tickets that went beyond two in any role.

### 3.1 The tickets that went past two

| Ticket | Role | Rounds | Why past two | Owner asked? |
|---|---|---|---|---|
| **W2-20** (the resource gate) | test designer | **8 by the launch log** (labelled "round 8"); the commit subjects name "round 7" for the one merged at 15:02 on 11-09, because the log counts the first revision launch as round 1 | Rounds 1-3: the designer's first writing and two answers to settled points (one hour). **4-5: the engineer built to the stated interface and found three cases where the interface and a case disagree (S2, S10, S13); S16's planted program forked one process per CPU.** **6: review F3 (S16 judged against the slot's real share).** **7: review F2 (the servers' CPU counted twice).** **8: DEC-1105 (S16 per CPU; R2-F1).** Cause by kind: interface read two ways (rounds 4-5); a measurement that picked up the machine's background (S16, rounds 5-8: environment); one real fault, the CPU double count (round 7). | Round 8 yes (DEC-1105). **Rounds 4-7 no:** the CTO's rulings, no exception asked. |
| W2-20 | engineer | 4 | Round 1: the build. Round 2: to the stated interface. Round 3: review F1 (a **real** race: two launches at once pass the memory check) and F2/F4/F6/F8 riding along. Round 4: DEC-1105's R2-F1 (stale readings). | Round 4 yes. |
| W2-20 | reviewer | 3 | r1 not READY (F1 blocks); r2 READY; third a narrow review of DEC-1105's two points. Its own text says "never a new round" for R3-F1, which it recorded as a row. | Third yes. |
| **W2-148** (operator agent) | designer ~4, engineer 5, reviewer 5 | r1 not READY on F15 (the agent could undo another's change: **loses work, real**); r2; narrow review of F15; narrow review of F21 (a success code that could hide someone else's change); a narrow review of the replay feature | The two exceptions were the owner's. The fifth round is the replay feature the owner chose to build (DEC-1108 (2)). | Yes: DEC-1106, DEC-1107, DEC-1108. |
| **W2-149** (set-up A's briefs and wiring) | designer ~4, engineer 6, reviewer 6 | r1 not READY (1 blocker); r2 READY; F11 follow-up (found by the live run); the wiring review (13 findings, none blocking); F18-F23; F36 and F38 | After round 2 each pass was new scope: a live-run finding; the D-10 wiring (DEC-1112 (3)); six "ordinary, consequence other" rows made a round because they would make the experiment's verdict wrong; F36/F38 came from the owner's own change (DEC-1113 (2): blind disputes). | No exception asked. The scope was the owner's (DEC-1112, DEC-1113). The rounds were the CTO's (DEC-1112 (3)). |
| **ACT-W2-149-INSTALL-1** | ACT reviewer | 5 reviews on 4 builds (r1, r2, then v2, v3, v4) | Each build followed a finding that was **not blocking**; each review was READY by code with one KPI line marked fail. The operator's two-round cap is per manifest, so each rebuild reset it. | The owner is asked for the final yes only. |
| **W2-128** (kernel templates, D-5) | product-spec 4 (+2 for the template 1.0.1), designer 5, reviewer 3 (+2 for 1.0.1, +1 D-10) | Round 1 (text), then "2a" and "2b" | The ticket declared the rounds (DEC-916, "stated by the CTO", DEC-1112 (3)). Round 2a's review had 0 blocking findings; round 2b fixed its findings F1-F4 (three of them wording in skills and a rulesync copy). | No exception: the rounds were declared. |
| **W2-153** (launch templates) | designer ~8 batches, engineer ~6, reviewer 3 | Review r1, then the W1-46 follow-up, then the S3 amendment | **Environment/ripple:** the launcher's new template-copy requirement turned about 58 tests in other tickets red (R1: ~110 cases in nine acceptance folders), plus a merge conflict with W2-128 round 2b. The batches are many and small; each reviewed round was one. | No. Under DEC-1112 (3). |
| **W2-56** (guard alone sandbox) | designer 4, engineer 2 (+1 follow-up pair R3/R5), reviewer 2 (both READY on first pass) | | **Environment:** the Linux fact found by running it (D-13: a one-path socket allow leaves connect refused). Owner decided (DEC-1114, DEC-105). | Yes: DEC-1114. |
| W2-96 (D-10 accept) | designer 3-4, engineer 2, reviewer 3-4 | r1 (1 blocker F1), r2 READY; then "probe-r3" at max effort; then the "lift maps" pair | "probe-r3" is DEC-895's re-probe on the merged head; the lift maps are a separate small scope (the runaway brake tripped once on W2-96 and the CTO cleared it). | No. |

### 3.2 Tickets that kept to two (examples, for scale)

W2-141 (3 designer batches, 3 engineer, 2 reviews; the first review found **four real blockers**, the guard bypassed by
`git grep`, a `for` loop, `zgrep -r`, brace options: a true fail-open, fixed in round 3 of the engineer's passes and
READY at review 2). W2-145 (reviews 2), W2-152 (2), W2-129 and W2-55 (D-6 F2: 2), W2-135, W2-116 (2 each), W2-142,
W2-147, W2-150, W2-151 (1 each). The memory-verdict-2 cross-check and the seven readiness reviews (DEC-1078 (2),
DEC-1097 (3)): at most two each; readiness-5 was still NOT READY on F2 at round 2 and was closed by ACT-GUARD-SETS-1,
not a third round. The fresh-80 scripts had 2 rounds and a delta read (diffs only) at the pre-flight.
The D-10 red-fix list on 11-09 and 11-10: about 25 small tickets, one pass and one review each.

### 3.3 Why rounds went past two (the sums)

Of the nine rows above, by main cause (some have two):
- **Scope added after round two** (new feature, new row promoted, declared round): W2-149, W2-128, W2-148's replay,
  W2-96's lift maps: 4.
- **Interface or KPI read two ways** (the designer and the engineer disagree): W2-20 rounds 4-5: 1.
- **Environment or ripple** (a fact the machine showed later, or another ticket's change): W2-56, W2-153, W2-20's S16: 3.
- **A real fault found after round two** (loses work or fails open): W2-148's F15 and F21, W2-20's F1 (found in
  round 1 and fixed in round 3), W2-141's four blockers: 3 (all of them were in round one or two of the review, but
  the fix needed a third pass by the engineer).
- **A rebuild that reset the count** (ACT manifest): 1.

The honest reading: **most extra rounds this week were not about a reviewer who could not stop.** They were
scope the ticket's KPI lines did not hold (new rows, new features), tests and code that read the interface
differently, and the machine changing under the work. A rule that only tightens the reviewer's end would have
changed very little.

---

## 4. One rule for all roles: my recommendation (confidence medium-high)

### 4.1 The wording

> **One bar, two rounds.**
> 1. **The bar is the ticket's KPI lines and its specification** (sources, interface, non-goals). Every session is
>    judged on them and on nothing else: the designer's tests, the engineer's code, the product-spec text and the
>    reviewer's verdict.
> 2. **Every finding names the KPI line it fails** (its id). A finding that names none is a row for the list or
>    Wave 3. It starts no round, in any role. A KPI line marked fail blocks, whatever the finding count.
> 3. **A round is one pass by a worker and one judgement against the KPI lines** (the red check for a designer, the
>    acceptance run for an engineer, the review for product-spec and for the whole ticket). **At most two rounds per
>    ticket, counted by the CTO from the ticket's id and role, never by a session.** A rename, a rebuild, a declared
>    "round 2a" or a re-opened follow-up does not restart the count.
> 4. **A KPI line still not met after round two goes to the owner,** with each line's state, the evidence of both
>    rounds, and the options (narrow the line, split, defer, one more round with a reason). The owner alone gives a
>    third round, and says so in a decision.
> 5. **What changes the bar is a decision, not a finding:** a KPI line or the specification changes only by a
>    recorded decision made before a round starts. A fact the machine shows later (an environment change) is that
>    case: the CTO brings it to the owner as the cause of the stop.
> 6. **A fail-open that an honest agent can hit goes to the owner at once** as a P1 package (as DEC-957 already
>    says for an emergency). It is not a round and it is not held for round three.

It is DEC-1010's rule, widened from the review round to every role, with three added closes: the count is per
ticket and by id, a KPI fail blocks, and the bar changes only by decision.

### 4.2 What it would change, by file

I list the files and the lines; I propose no edit.

| File | Lines | Change |
|---|---|---|
| `governance/project/briefs/JUDGEMENT.md` | 3, 14, 19-23 | Say "every role" not "reviewer, probe and auditor"; replace "moderator triages" by "every finding cites a KPI line id or is a row"; add "a KPI line marked fail blocks"; drop "feature-gated risks" (line 12) to a ticket-entry rule; one-line definition of a round |
| `governance/project/briefs/LEAD-w2-common.md` | 122-127, **132** (DEC-916 "per declared round"), **162** (loop of three), 163 (step 5) | One text. Retire the "per declared round" clause. The loop count is two, not three. |
| `governance/project/briefs/AUDITOR-common.md` | 39-43 | Same text |
| `governance/project/prompts/w2-orchestrator.md` | §14, lines 313, 316-320 | Same text; the word-for-word copy of JUDGEMENT.md |
| `template/governance/kernel/templates/role-reviewer.md` | 23-24, 28 | The "hold at most two rounds" line leaves the reviewer (it cannot know its round, DEC-096) and moves to the lead; "block only on a finding in scope" becomes "name the KPI line id or write a row" |
| `.../templates/role-test-designer.md` | after line 14 | Add: "write tests only for KPI lines and the stated interface; a finding that names no KPI line is a row for the list" |
| `.../templates/role-engineer.md` | line 13 | Already holds "no code beyond the KPI lines"; add "a repair pass carries the failing KPI lines only" |
| `.../templates/role-product-spec.md` | line 21 | Add: "a change after a review cites the KPI line it serves" |
| `.../templates/role-lead.md` | 42, 44-48 | Two rounds, not three; count by ticket and role |
| `.../templates/ticket.md` and `schemas/ticket.schema.json` | `ticket.md` 38-44; schema 9-18 | **Give each KPI line an `id` (S1..., F1...)**, so a finding can cite one by name |
| `.../skills/test-design/SKILL.md` | 28-34 | "A finding becomes a test only if it states the behaviour of a KPI line" |
| `.../skills/audit/SKILL.md` | 45-49 | Each finding cites a KPI line or the Contract item, else a row |
| `governance/project/operator/verdict.py` and the CTO's copy `tools/verdict.py` | 11-12 | READY also needs no KPI line marked fail (the ACT reviewer's rule already says so) |
| `governance/project/operator/operator_run.py` | 448-453 | Count verdict blocks by ACT id, not by manifest, so a rebuild keeps the count |
| `src/gov/close/state.py` (line 17, `ESCALATION_AT = 3`), `src/gov/close/command.py` (154-159) | | **Leave as it is.** It counts refused closes (a mechanical loop, DEC-487), not review rounds. Lowering it would turn environment reds into owner stops. |
| Round counter (new) | none today | No code counts rounds per ticket and role. The spend log has `ticket` and `role` only from 11-10 and the round lives in free text. A counter in `gov launch` or the dispatcher, with the "one recorded override with a decision id" the launch already has (DEC-1088 (5)), is the natural place. |

Kernel changes (the role templates, the skills, the ticket template and schema, JUDGEMENT.md if it is promoted)
follow CAP-33: evidence, independent review, owner approval and a version. Controls (`operator_run.py`, `verdict.py`,
the launcher) are by ACT (class-rules). The counter is **not** a guard rule, so DEC-1128 (2)'s 100 % bar is not
what stops it; DEC-1047's basis (5) ("a practice enters the product only after it has proven itself in use") is.

### 4.3 What it costs

- **Owner time.** This week seven tickets went past two in some role; under the rule each would have reached the
  owner at the end of round two: about one decision a day. Most would be "narrow it" or "split it", a few lines
  each. Against that, W2-20's eight designer rounds and W2-149's six reviews would have been stopped after two.
- **A change of habit for the CTO:** no more "round 2a", "round 2b" and rows promoted by the CTO's own judgement.
  Anything promoted needs a decision id.
- **Work:** a text change of about 15 lines in 10 files, one schema field, one small code change in each of
  `verdict.py` and `operator_run.py`, and, later, the counter.

### 4.4 What it could break

1. **A real fail-open found in round three.** Clause 6 sends it to the owner at once; it is not blocked by the
   count. This week's real faults were found early (W2-141's four blockers and W2-20's F1 were in review 1), but the
   engineer needed a third pass to fix them. Under clause 3 that third pass is round 3. **Fix:** count a pass that
   only fixes the findings the review marked blocking as part of the same round. I recommend this wording and state
   it here as the main open point.
2. **Environment changes** (W2-56's socket fact, W2-153's ripple) would stop at round two and reach the owner. That is
   right under the owner's principle: the KPIs are not met and the cause is outside the ticket. Clause 5 names them.
3. **A KPI line that is badly written** would block with no one allowed to "judge it away". The remedy is a
   decision that changes the line (clause 5), not another round.
4. **A designer and an engineer who read the interface differently** (W2-20 rounds 4-5). A ticket whose interface
   is already stated (`ticket.md` line 63) should not have that; where it happens, it is a KPI-ambiguity package, not
   a round. Clause 2 sends it there.
5. **Rebuilt ACTs.** Counting by ACT id would stop ACT-W2-149-INSTALL-1 at its second review and ask the owner. That
   is what the owner's principle asks.
6. **Probes that look beyond the tests.** The reviewer's job is to find what the acceptance tests miss
   (`role-reviewer.md` line 8). Under the rule it keeps that job, but each finding it raises must name a KPI line
   or be a row. A true "nothing in the KPI lines covers it, and it fails open" is clause 6.

### 4.5 Options, if you want less than the full rule

| Option | What changes | Cost | Risk |
|---|---|---|---|
| **A (recommended)** | The full rule, text first (JUDGEMENT.md, lead brief, templates, ticket template with ids), code later after two weeks of use | About 10 files by CIT-P; the CTO keeps the ledger by hand until then | Medium: the CTO's own discipline holds it until the counter exists |
| B | Text only for the roles; no code ever | Smallest | The two code gaps in 2.4 (READY and the per-manifest count) stay; this week's ACT pattern repeats |
| C | Only fix the two code gaps (`verdict.py` KPI-fail, `operator_run.py` count by ACT id) and the ticket's KPI ids | 3 files, 2 ACTs | The roles' text stays as is; designer and engineer rounds stay uncapped |

### 4.6 Not found or not done

- The week's counts before 11-07 come from review records and commit subjects only; the spend log does not name
  those launches. A ticket with two rounds and no review record may be missed.
- I did not read the held-out folders (none was needed). I ran no test.
- The per-ticket "round" labels in the log are the CTO's; where a label and a commit differ (W2-20: "round 8" by the
  log, "round 7" by the commit) I give both.
- I did not check whether `.claude/agents/` copies (generated) match `template/.rulesync/subagents/` today; the
  source is the template.
