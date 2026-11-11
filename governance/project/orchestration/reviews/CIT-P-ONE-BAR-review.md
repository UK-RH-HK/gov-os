---
task: DEC1131-ONE-BAR-CIT-P
milestone: DEC-1131 one-bar CIT-P, independent review (CAP-33 step 4), round 1
commit: 74110bb3414403c2f785acbce1206f213c651f44
pack_sha256: none (briefed by message and the record's path; no gov context pack)
record_reviewed: .gov-runtime/scratch/orchestrator/drafts/citp-one-bar/CIT-P-ONE-BAR.md
line_base: the record cites 625aa084fa02; `git diff 625aa084fa02 HEAD` over every cited file is empty, so its line numbers hold at HEAD
decisions: [DEC-1131, DEC-1010, DEC-096, DEC-916, DEC-957, DEC-802, DEC-801, DEC-757, DEC-235, DEC-866, DEC-1112, DEC-413, DEC-136, MR-3, CAP-33]
reviewer: independent auditor (fresh, read-only; wrote none of the record)
verdict: READY WITH FIXES
---

# Review of the DEC-1131 CIT-P ("one bar, two rounds"), round 1

**Classification (DEC-809):** 9 fixes (FX1 to FX9), each a text change inside the record, no re-scope; 9 rows (R1 to R9);
none needs a deliberate construction. **Recommendation: READY WITH FIXES.** The record is sound in its shape. Text R
matches DEC-1131 and §4.1 in meaning, and almost every "before" quote is exact. The fixes are needed because three of
the record's own claims are false when checked: W1-35 stays green (it goes red), no brief names the ledger (Text R
names it in every reviewer brief), and nothing is left behind (three old sentences survive). The route also misses
W2-128, which is in flight on the same paths.

Each fix and row names the brief's check it fails: (1) rule text, (2) before/after, (3) contradictions, (4) split and
route, (5) ledger and DEC-096, (6) KPI ids and DEC-757 (6), (7) tests that read the files, or §5.3's check n.

## What I probed and found sound

- **(1) Text R against DEC-1131 and DEC1010-REVIEW §4.1:** all six §4.1 clauses are present, with the same meaning.
  The open point is stated as decided (but see FX6 on its bound). Clause 8 carries DEC-1131 (3)'s by-hand reading until
  `verdict.py` lands. The CTO's P2 not reaching a third round matches §4.1 clause 4 ("the owner alone") and
  DEC-1112 (3) ("anything that changes one of the owner's standing decisions").
- **(2) "Before" quotes:** every one was checked by reading the file at the named line. JUDGEMENT.md 3, 9, 11, 12, 14,
  18, 19-23; LEAD-w2-common.md 122-127, 132, 162, 163; AUDITOR-common.md 28, 30, 31, 38, 39-43; w2 prompt 7, 173,
  310, 312, 313, 314, 316-320; role-reviewer 3, 12, 22-25, 28, 35; role-test-designer 23 (end of file);
  role-engineer 13, 20; role-product-spec 21; role-research 19; role-lead 29, 42, 47, 48, 68; role-cto 23; brief.md 21
  and 27; ticket.md 3, 38-44, 59, 63; schema `kpi_line` lines 9-18; the six role files' Authority lines and
  orchestrator.md 45-47 and 59-60; audit skill 49; change skill 32; test-design skill 26, 33, 34; `kpi_rows` at
  build.py 109-126; verdict.py docstring 9-10 and code 38. **All exact, except one** (FX9).
- **(4) Route:** the precedent holds. The kernel templates, roles and both `.rulesync` trees were changed by
  product-spec and engineer ticket commits (W2-128 `9d95279c9`, `8df648cc9`; W2-153 `3cf6c4951`), and only `.claude/`
  went by ACT (`eb48fe2fd`, `2059048f2`). The project files fall to the (O) catch-all, which is not a control path
  (class-rules.yaml header). The CAP-33 steps in §5.4 are complete.
- **(5) Ledger:** the `{LEDGER}` key goes in role-cto only, and `facts.yaml`'s `paths` accepts the new key
  (facts.schema.json: any `^[a-z][a-z0-9_]*$` name). No worker template gives a count. (See FX2 for where the path
  leaks.)
- **(6) KPI id:** the field is optional and derived by position, so no closed or reviewed ticket must be edited. Old
  records stay valid (`additionalProperties: false` is kept and the property is only added).
- **Budgets (§5.3 check 5):** the prose sizes today are role-reviewer 2,635 of 3,500, role-lead 4,698 of 8,000 and
  brief 3,117 of 4,000; each addition fits. (role-cto has no budget in `facts.yaml`, which is not a fault.)
- **§5.3 check 7, the recount:** W2-20's labels in `git log` agree. The designer's merges are labelled rounds 1-3,
  4-5, 6, 7 and 8 (`a71d9670e`, `4125133f4`, `28fbcfebf`, `c90771b74`, `105699f8d`); the engineer's are rounds 1 to 4
  (`4be0bb81a`, `9f518fd56`, `b6c6dad61`/`2bb6f70b6`, `057926aa3`). (Small slip: the designer commit at 15:59 is not
  labelled "round 8"; the 16:02 merge is.) W2-141 had 3 engineer passes and 2 reviews (but see R1).
- **§5.3 check 9, the seed:** every seeded row matches DEC1010-REVIEW 3.1 and 3.2.
- W2-128's other template cases still hold under the proposed text. The verdict block keeps DEC-1010's form. The
  "Ordinary work:" and "Consequence:" marks stay in role-reviewer alone. The reverse-evidence step stays.

## Fixes (READY once these are made)

**FX1. W1-35 turns red: the record says it stays green.** Fails (7) and §5.3 check 6.
- What was done: the proposed orchestration-skill line 33 says "The lead holds each role's round count (two at most)
  and never discloses it". I ran W1-35's own `row_faults("the ticket loop", …)` on the corpus with the skill and
  role-lead edits applied (in my scratch).
- What happened: before the edits it returns `[]`; after them it returns
  `['not stated: the loop count is held by the lead and never disclosed']`. The clause needs "(loop|iteration) count"
  together with never/not and disclose/tell in one statement. "Round count" does not match. Skill line 62 has "loop
  count" but no disclose or tell word.
- What should happen: keep the words, for example "The lead holds the loop count, each role's rounds (two at most),
  and never discloses it; …". Or, if the wording must change, plan a test designer's revision under DEC-866 (MR-3)
  inside the route. Then correct §2.4's claim.
- Ordinary work: yes, because the product-spec ticket would write the record's words exactly.
- Consequence: other (a red suite and a false claim in the record).
- Reverse it: a run of W1-35's ticket-loop row on the proposed text that returns no fault.

**FX2. Text R names the ledger file in every reviewer and auditor brief, against §3 and R8's own answer.** Fails (5).
- What was done: Text R's third bullet says "The CTO counts them from the ticket's id in
  `governance/project/orchestration/ROUND-LEDGER.md`". Text R goes into JUDGEMENT.md and AUDITOR-common.md, which
  "go, word for word, into every reviewer, probe and auditor brief" (JUDGEMENT.md line 14, kept unchanged).
- What happened: every reviewer and auditor is handed the path of a file that holds its own count. Reads are open
  (DEC-820). §3 ("no brief names the file") and R8 ("No brief names the file") are untrue for the very text this
  record writes. DEC-096 says the count is never disclosed to the sessions inside the loop.
- What should happen: Text R says "the CTO counts them in its round ledger", with no path. The path lives only in
  role-cto (`{LEDGER}`) and `facts.yaml`.
- Ordinary work: yes, because a reviewer told a path routinely reads it.
- Consequence: other (DEC-096's non-disclosure weakened).
- Reverse it: Text R's copies naming no path, or an owner decision that the count may be readable.

**FX3. Old sentences survive that contradict Text R.** Fails §5.3 check 2 and (3).
- LEAD-w2-common.md line 132 keeps "Accepted fixes ride along in a resume that happens anyway (DEC-802)". The record
  changes only that line's last sentence, yet its new JUDGEMENT line 11 says anything beyond blocking findings makes
  the pass a round.
- LEAD-w2-common.md line 163 keeps "Findings an honest agent can hit in ordinary work that fail open or lose work are
  fixed". This is the three-part test as the only block, which D-2 replaces: a failed line blocks whatever the
  consequence.
- role-reviewer.md line 25 is kept "unchanged": "Start no round of its own for accepted fixes when the ticket resumes
  anyway [DEC-802]". It still implies non-blocking accepted fixes are worked in the resume.
- What should happen: add edits for those three sentences, stating that only blocking findings are fixed and the rest
  are rows (D-3).
- Ordinary work: yes, because a lead reads line 132 and 163 on every FULL ticket.
- Consequence: other (two readings of when a pass is a round).
- Reverse it: a reading of those three sentences under which they agree with Text R clause 4 and D-2.

**FX4. "Yes on both questions, no KPI line" has two meanings.** Fails (2) (the "after" says more than the rule) and
§5.3 check 3.
- What was done: the new JUDGEMENT line 9 (copied into AUDITOR line 28 and prompt line 310) sends a finding with "yes"
  to both questions and no KPI line to the owner as a P1. "Yes" to the second question includes "loses work".
- What happened: Text R clause 7, the new line 18 and the reviewer's new line after 22 send only a **fail-open** with
  no line to the owner as a P1. Line 18 makes a no-line "loses work" finding a row. §4.1 clause 6 is fail-open only.
- What should happen: one reading in all four places. Either fail-open only, as §4.1 says, or name "loses work" as
  DEC-957's emergency ("a risk of losing data") and add it to clause 7 for the owner to confirm.
- Ordinary work: yes. Consequence: other (a no-line lost-work finding may be either a P1 or a row).
- Reverse it: an owner reading under which line 9 and clause 7 are the same rule.

**FX5. The route misses W2-128, in flight on the same paths, and its pinned cases.** Fails (4) and (7).
- W2-128 (DAEO-t8mp) is `in_progress`. Its `allowed_paths` hold `template/governance/kernel/templates/**`, `roles/*.md`,
  the test-design and orchestration skills, `ticket.schema.json`, both `.rulesync/subagents/*.md` trees,
  `template/.rulesync/skills/*/SKILL.md` and `facts.yaml`. DEC-235: "no two tickets in flight have overlapping paths,
  and an overlapping ticket waits". §5.4's order does not say the product-spec ticket waits for W2-128's close, or
  that it goes in W2-128.
- W2-128's round-2a cases go red under the proposed edits:
  - `test_s11_skill_version_is_one_minor_above_integrates` requires exactly 1.2.0, against fixed baseline
    `a2576c6f`; the record proposes 1.3.0.
  - `test_s11_guard_test_design_skill_changes_only_its_read_rule` and
    `test_s11_guard_orchestration_skill_changes_only_the_named_parts` refuse changes outside named parts, against fixed
    baseline `61231e61`. The record changes test-design lines 26 and 33 and the ticket-loop lines.
- Only an independent test designer may revise those cases (MR-3, DEC-866, `Rewrite-Reason:`). The product-spec
  ticket cannot.
- What should happen: §5.4 says the kernel half waits for W2-128 to close (or is folded into it by a decision). Name
  the three W2-128 cases. Add a test-design batch under DEC-866 to the route.
- Ordinary work: yes. Consequence: other (red suites; two writers on one path).
- Reverse it: W2-128 closed before the kernel half starts, with its round-2a cases retired or revised.

**FX6. The blocking-only fix pass has no bound and is widened beyond "an engineer pass".** Fails (1) (the open point
as decided) and §5.3 check 8.
- DEC-1131 (2) says "**an** engineer pass … belongs to the same round". Text R clause 4 says "**A** pass that only
  fixes findings a review marked blocking". That covers any role's pass (the designer's DEC-136 batch, product-spec)
  and any number of passes.
- Under the new lead text the three-iteration bound applies only to "a loop with no KPI line". So a red acceptance run
  after a fix pass, followed by another fix pass naming the same finding, starts no round, and the text has no stop
  before review 2. The record's argument in §1.2 ("its judge is the second review") does not bound the passes before
  that review.
- What should happen: "One fix pass per review (the designer's batch for the findings, then one engineer pass) …".
  Name the widening from an engineer pass to the designer's batch as a D-point for the owner to confirm (the W2-141
  dry run needs it).
- Ordinary work: yes, because a lead following the text resumes fix passes on a red acceptance run.
- Consequence: fails open (the two-round cap, the rule's own control, does not stop).
- Reverse it: text showing that a red acceptance run after a fix pass counts as the role's next round.

**FX7. The edits tell every worker the round budget, so the E5 contradiction is moved, not closed.** Fails (3) and
§5.3 check 4.
- DEC-096: "The iteration count **and budget** … are never disclosed to the sessions inside the loop". The record
  removes "Hold at most two review rounds" from role-reviewer as a DEC-096 contradiction (E5).
- But it adds "the CTO counts at most two rounds per ticket" to the role files of the independent auditor, test
  designer, engineer and product-spec. Those role files are the second half of each worker's system prompt
  (`.rulesync/subagents`). Text R ("At most two rounds per ticket and role") goes into every reviewer brief.
- §2.7's note "DEC-096: Changed by: DEC-1131" names no part. DEC-1010 changed DEC-096 "for reviews" only.
- What should happen: either drop the cap from the worker role files (it is the CTO's to keep, not a guard fact) and
  from Text R's worker-facing copies, or name the part: "DEC-096's budget may be stated to every role, the count is
  never told", as a D-point for the owner. Then restate E5 truthfully.
- Ordinary work: yes. Consequence: other.
- Reverse it: an owner reading that DEC-096's "budget" means a time or token budget, not the round cap.

**FX8. Written ids on in-flight tickets edit reviewed ticket files.** Fails (6).
- §2.5: "A ticket still in flight may be given written ids by the CTO in one ticket commit before its next round".
  A ticket in flight that has had a review is a reviewed ticket.
- DEC-757 (6) is standing and is still cited as in force: DEC-1129 and DEC-1130 are owner exceptions to it, made by
  name. It says "never edit an open ticket's file on `w2/integrate` after its review".
- What should happen: "a ticket **not yet reviewed** may be given written ids …; a reviewed ticket keeps its position
  ids until it closes".
- Ordinary work: yes, because the CTO would follow §2.5. Consequence: other (the probe gate reads an edited ticket,
  as in DEC-757's PROBE_INVALID case).
- Reverse it: an owner exception to DEC-757 (6) named for this edit.

**FX9. Wrong line for the orchestration skill's "second review" sentence; root `.rulesync/` not named.** Fails (2) and
§5.3 check 1, and (4).
- The record says line 31. "- For a FULL ticket a second review is the last. …" is at **line 32**; line 31 is
  "- Tests first, by a fresh test designer …".
- §2.2, §2.3 and §2.4 name only `template/.rulesync/` as the mirror. W2-153 S3 (`test_w2_153_sources.py`, TREES =
  `.rulesync` and `template/.rulesync`) holds **both** `.rulesync/subagents/<role>.md` trees to "role template body +
  role file body". The repository-root `.rulesync/skills/{orchestration,test-design,audit,change}/SKILL.md` are byte
  copies today too. Editing the templates, roles and skills without the root copies turns W2-153 S3 red and leaves the
  source of `.claude/` stale. The root `.rulesync/**` is class-rules row `rulesync-other` (b), changed by ticket before
  (`3cf6c4951`), so the route needs only naming.
- What should happen: correct the line number, and name `.rulesync/subagents/*.md` and `.rulesync/skills/<name>/SKILL.md`
  beside the template copies.
- Ordinary work: yes. Consequence: other.
- Reverse it: W2-153 S3 reading only `template/.rulesync` (it reads both).

## Rows (recorded; no round)

- **R1. §5.2 and the seed misread W2-141.** Check 7. Review 1's verdict block (`W2-141-review.json` in the W2-141
  worktree's lead log) has F1-F4 in scope, ordinary work, fails open. F5 is ordinary work no; F6 to F8 are "other",
  with F7 and F8 under S3, which passed. The engineer's "round 3" (`7716610e2`) fixed "F1 to F8". Under Text R clause
  4 that pass carried rows, so it is a round of its own, and the claim "Nothing stops" is wrong in fact. Under the rule
  the lead would have had to narrow the pass to F1-F4 (and F6 by D-2). Restate the dry run. *Ordinary work: yes.
  Consequence: other.*
- **R2. Research is given one pass, not two.** Checks (1) and (2). The role-research and research.md lines say "a
  second pass is a new ticket by a decision". DEC-1131 says two rounds for every role. Either leave research out
  (it has no KPI lines or loop, DEC1010-REVIEW 2.2) or give it two. *Ordinary work: yes. Consequence: other.*
- **R3. D-3 changes DEC-802, and DEC-1131 never names it.** Check 3. DEC-1131's `Under:` lists DEC-096, DEC-916 and
  DEC-957, not DEC-802. D-3 follows from §4.1 clauses 2-3, but it should be put to the owner by name at approval, as
  R9 does for D-6. The new JUDGEMENT line 11 keeps the heading "No extra round on its own" over text that now makes
  a round; reword it. *Ordinary work: no (an approval step). Consequence: other.*
- **R4. "Split before it starts" is a taking not listed among D-1 to D-9.** Check 8. Text R adds "A ticket that needs
  more than two rounds is split before it starts: each part is a ticket with its own count". §4.1 lists a split only
  as the owner's option after round two. A pre-start split by the CTO is close to DEC-916's declared rounds. List it
  as D-10. *Ordinary work: yes. Consequence: other.*
- **R5. Narrowing a failed line after round two.** Check 1. Clause 6 makes a KPI line inside the spec a P2, while
  clause 5 makes "narrow the line" the owner's option after round two. Say that after a role's second round a line
  changes only by the owner. *Ordinary work: yes. Consequence: other.*
- **R6. The seed rows sit in the counted table.** Check 5 and §5.3 check 9. The rule at the top counts "rows with a
  round number". The seed rows carry numbers ("8 by the launch log"), but D-4 says they are for information only.
  Put them in a separate "before promotion" table that the counting rule excludes. *Ordinary work: yes.
  Consequence: other.*
- **R7. The audit skill uses SCOPE_CREEP for a finding.** Check 2. SCOPE_CREEP classifies *audited work* beyond the
  spec (audit skill line 39), not a finding that asks for work. Write "a row" without the class. *Ordinary work: yes.
  Consequence: other.*
- **R8. Small additions beyond the rule.** Check 2.
  - The engineer must cite a KPI id in every commit body (role-engineer step 4 after). DEC-1131 asks only for finding
    ids in a fix pass.
  - The reviewer line says "no session is told the number" while role-lead holds "n of 2"; say "no worker".
  - The prompt's version header needs its v3.x line for DEC-1131 (D-9).
  - "DEC-1073's rule in role-product-spec.md line 6" is step 6, at line 15.
  *Ordinary work: yes. Consequence: other.*
- **R9. Exposure that predates this record.** Check 5. The lead's CHECKPOINT.md, which now carries "n of 2", lies in
  the worktree the engineer works in. LEAD-w2-common.md line 170 already puts "the loop count" there. Not this
  record's fault; name it beside R8 of §5.1. *Ordinary work: yes. Consequence: other.*

## D-1 to D-9 (§5.3 check 8; the brief's check 3)

| D | Within DEC-1131? | Note |
|---|---|---|
| D-1 | within | DEC-801 kept; §4.1 clause 2 with the threat model |
| D-2 | within | §4.1 clause 2 "a KPI line marked fail blocks"; DEC-1010 already carries the Changed-by note |
| D-3 | within in substance; **owner to confirm by name** | DEC-802 is changed and DEC-1131 does not name it (R3) |
| D-4 | within | transitional, the narrowest reading |
| D-5 | within | §4.1 clause 3 "one pass and one judgement"; but see FX6 for fix passes |
| D-6 | within for the retirement | DEC-1131 is `Under:` DEC-916, and §4.1 clause 3 names "round 2a"; the added "split before it starts" needs listing (R4) |
| D-7 | within | a ledger detail, the CTO's under DEC-1131 (1); the same-id rule for follow-ups guards it |
| D-8 | within, **except** its in-flight clause | DEC-757 (6) (FX8) |
| D-9 | within | prompt line 7 asks for a package; the version line is missing (R8) |
| (missing) | **owner** | the widening of DEC-1131 (2) from an engineer pass to any pass, unbounded (FX6) |
| (missing) | **owner** | DEC-096's budget told to every role (FX7) |

## Table (audit form)

| item | class | evidence |
|---|---|---|
| (1) Text R matches DEC-1131 / §4.1 | OK | docs/DECISION_REGISTER.md, governance/project/orchestration/packages/DEC1010-REVIEW.md |
| (1) open point as decided | WEAKENED | docs/DECISION_REGISTER.md (FX6) |
| (2) before-text at file and line | WEAKENED | template/governance/kernel/skills/orchestration/SKILL.md (FX9) |
| (2) after says the rule and nothing more | WEAKENED | governance/project/briefs/JUDGEMENT.md, template/governance/kernel/templates/role-research.md (FX4, R2, R7, R8) |
| (3) no uncited contradiction | WEAKENED | governance/project/briefs/LEAD-w2-common.md, template/governance/kernel/templates/role-reviewer.md, template/governance/kernel/roles/engineer.md (FX3, FX7, R3) |
| (4) kernel/project split, CAP-33 route | WEAKENED | .tickets/DAEO-t8mp.md, tests/acceptance/W2-153/test_w2_153_sources.py (FX5, FX9) |
| (5) ledger keeps DEC-096 | WEAKENED | governance/project/briefs/JUDGEMENT.md (FX2) |
| (6) KPI id needs no reviewed-ticket edit | WEAKENED | docs/DECISION_REGISTER.md (FX8) |
| (7) tests that read the files | CONTRADICTS | tests/acceptance/W1-35/w1_35_orchestration_support.py, tests/acceptance/W2-128/test_w2_128_round2a.py (FX1, FX5) |
| §5.3 check 1 | WEAKENED | template/governance/kernel/skills/orchestration/SKILL.md |
| §5.3 check 2 | MISSING | governance/project/briefs/LEAD-w2-common.md |
| §5.3 check 3 | WEAKENED | governance/project/briefs/JUDGEMENT.md |
| §5.3 check 4 | WEAKENED | template/governance/kernel/roles/independent-auditor.md |
| §5.3 check 5 | OK | governance/project/facts.yaml, template/governance/kernel/schemas/facts.schema.json |
| §5.3 check 6 | CONTRADICTS | tests/acceptance/W1-35/w1_35_orchestration_support.py |
| §5.3 check 7 | OK | governance/project/orchestration/packages/DEC1010-REVIEW.md (with R1) |
| §5.3 check 8 | WEAKENED | docs/DECISION_REGISTER.md |
| §5.3 check 9 | OK | governance/project/orchestration/packages/DEC1010-REVIEW.md |

```verdict
{"kpis": [
 {"kpi": "C1", "verdict": "fail", "findings": [{"id": "FX6", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "C2", "verdict": "fail", "findings": [{"id": "FX4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "FX9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C3", "verdict": "fail", "findings": [{"id": "FX3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "FX7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C4", "verdict": "fail", "findings": [{"id": "FX5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C5", "verdict": "fail", "findings": [{"id": "FX2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C6", "verdict": "fail", "findings": [{"id": "FX8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C7", "verdict": "fail", "findings": [{"id": "FX1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
C1 to C7 are the brief's checks (1) to (7). §5.3's nine checks are folded into them as the table shows. Each fix is a
local text change in the record. Under the rule the record proposes, a failed check blocks until a second round
re-judges the fixed record; that round is the last.

Not done: I edited nothing and ran no suite. The W1-35 reproduction imported the test's support module from my
scratch and compiled no new bytecode (the `.pyc` predates this session). I did not read held-out or memory-verdict
folders. I read W2-141's review verdict from its worktree's lead log, read-only.
