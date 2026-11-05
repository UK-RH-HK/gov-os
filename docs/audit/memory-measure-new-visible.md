# Cross-check of the visible half's 16 new questions, q25 to q40 (DEC-1069 (8))

- **Audited:** `fixtures/evaluation/memory-retrieval/visible/q25.yaml` to `q40.yaml` on branch `emg/new-visible`,
  commit `c17dba7d803f`, with the writer's account `docs/research/memory-measure-audit/NEW-VISIBLE.md` (same commit).
- **Judged at:** the head of `w2/integrate`, `62906aa86656`, read-only. The measure resolves sources at the measured
  root, so each source was resolved there with a copy of `measure.py`'s `_span` rule (the first line equal to the
  heading; a `#` heading spans to the next heading of the same or a higher level; any other heading spans the
  stated number of lines from where it is found). Each path was placed with `governance/project/path-map.yaml` at
  that head.
- **Rubric:** `docs/research/memory-measure-audit/RUBRIC.md`, version 2 (R1 to R11).
- **R9 against:** `visible/q01.yaml` to `q24.yaml` at integrate's head (with DEC-1069 (1) to (3)'s label fixes
  applied), and the 16 against each other.
- **Auditor:** an independent session that wrote none of the audited files and none of the retrieval work. Blind:
  no measure record, no EXP-003 folder, no run folder, no D4B package, no draft, no review and no hidden half was
  read, and no search was run. No fixture was changed.

## 1. Summary

| Verdict | Questions |
|---|---|
| May enter as written | q25, q26, q27, q28, q29, q30, q31, q32, q33, q34, q35, q37, q38, q39, q40 (15). Some have advisory notes (section 3) |
| Enter after a fix | q36 (1): re-word it (R4) and add the Contract's CAP-38.e as alternatives (R1 item 1, which also moves its R5 domain) |
| Drop | none |

- All 29 alternatives across the 16 questions resolve at integrate's head.
- Every heading is found, and is the only line in its file equal to itself.
- Every span holds its answer.
- Every path is in an embedded namespace.
- No source is test-harness code, a report, an evaluation document or a PROPOSED record.
- The 16 merge without touching q01 to q24. The writer's branch is based on `cc9c94d4`, before the label fixes, but
  `c17dba7d` only adds q25 to q40 and `NEW-VISIBLE.md`.

## 2. Counts per item (the 16)

| Item | PASS | FAIL (major / minor) | Advisory notes |
|---|---|---|---|
| R1 Correct, governing | 16 | 0 / 0 | q36 (the governing CAP-38.e is not an alternative), q34 (the rule is still in force as CAP-59.c) |
| R2 Searchable | 16 | 0 / 0 | none. Any entry keyword-only: 0. All entries keyword-only: 0 |
| R3 Unambiguous | 16 | 0 / 0 | q27 (two reasons, both needed by the gold) |
| R4 Real agent question | 15 | 0 / 1 (q36) | q25, q37 (some echo of the source's wording); q37, q35 (the fact also sits in a file sessions load) |
| R6 Span holds the answer | 16 | 0 / 0 | q29, q39, q40 (the deciding code check is outside a docstring span); q38, q28 (the span takes in nearby text) |
| R7 Well formed | 16 | 0 / 0 | q40 (the ticket alternative states only the "no"; the gold adds detail) |
| R8 No evaluation source | 16 | 0 / 0 | none |
| R9 Distinct | 16 | 0 / 0 | none |
| R10 Record and form | 16 | 0 / 0 | none |
| R11 Stable | 16 | 0 / 0 | none |
| R5 (set level) | PASS for the 40 | none | plan at the 4 minimum; retrieval and the context packet at the 10 maximum (section 4) |

## 3. Per question

Each entry gives every item's result, a code where one applies, and the reason in one sentence.

### q25 (plan): new work in Wave 2, a list row or to the owner first

**Verdict: enter as written.**

- **R1 PASS.** WAVE_2_WBS.md §6, the "finish line", is ACCEPTED (DEC-729). DEC-584 is Wave 1's version of the rule,
  so no decision outranks §6. The gold answer restates §6 faithfully.
- **R2 PASS.** The source is in `docs` (embedded).
- **R3 PASS.** The question has one reading and asks one fact.
- **R4 PASS (advisory).** A lead asks this before opening work. The opening "Before I start new work in Wave 2"
  echoes the source's "Before opening any new work in Wave 2". The rest is paraphrased, so this is not a fail.
- **R6 PASS.** The heading is found at 1875 and spans 1875 to 1877: the classification and both outcomes.
- **R7 PASS.** One entry, and it holds the whole piece.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It is a plan rule that changes only by a decision.

### q26 (plan): the exit criterion on the hooks

**Verdict: enter as written.**

- **R1 PASS.** Exit criterion 2 of WBS revision 4 has no "History" line and no later amendment.
- **R2 PASS.** The source is in `docs`.
- **R3 PASS.** Criterion 2 is the only exit criterion on the hooks.
- **R4 PASS.** A lead or the orchestrator checks this for W2-06 or the exit.
- **R6 PASS.** The span is 1850 to 1854: the criterion's title and its four lines, stopping before criterion 3.
- **R7 PASS.** One entry holds the whole list.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** This is distinct from Q08 (which ticket builds the commit-time re-index).
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It changes only by a decision.

### q27 (plan): W2-41 in Wave 2, and why not

**Verdict: enter as written.**

- **R1 PASS.** Both plans are ACCEPTED, and every claim holds: the card's DEC-953/954 reason, and §8's row with
  W2-H022/24/25/33 and W2-H023 in W2-57. DEC-841 item 4 decides the move itself and points to "the plan's reasons",
  so the plan is the only record that holds the asked "why".
- **R2 PASS.** Both sources are in `docs`.
- **R3 PASS (advisory).** The "why" has two reasons from two dates, and the gold needs both as two entries. Neither
  is superseded.
- **R4 PASS.** An auditor or lead asks whether close-integrity rows are in scope. W2-41's ticket (DAEO-s694) is
  tagged both `wave-2` and `wave-3`, which is exactly why an agent would ask.
- **R6 PASS.** The card's line 995 and §8's row 462 are found and hold their pieces.
- **R7 PASS.** There are two entries for two pieces in two files.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It moves only by a decision.

### q28 (plan): the triage's "named in" against "fits"

**Verdict: enter as written.**

- **R1 PASS.** WAVE_2_TRIAGE.md is ACCEPTED (DEC-729), and the gold answer quotes its "How to read it" faithfully.
- **R2 PASS.** The source is in `docs`.
- **R3 PASS.** One reading.
- **R4 PASS.** The question uses the triage's own two terms. They appear in 384 and 153 of its rows, so an agent
  who meets them would type them.
- **R6 PASS (advisory).** The span is one line (14), and that line also carries the triage's revision notes. It
  cannot be made narrower.
- **R7 PASS.** One entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It is a reading rule of an accepted plan.

### q29 (ticket): W2-77, when the nightly cannot remove its clone

**Verdict: enter as written.**

- **R1 PASS.** DAEO-b6hm is closed, and its KPI line is the governing statement of what W2-77 requires. The code
  agrees: `_remove_clone` falls back to `_own_entry`, then `rmtree`, and returns the failure.
- **R2 PASS.** The sources are in `tickets` and `gov-source`.
- **R3 PASS.** One reading.
- **R4 PASS.** A test designer or engineer on the nightly asks this.
- **R6 PASS (advisory).** The ticket alternative (25) holds the requirement whole. The code alternative (301 to
  302) is the `def` line and docstring only, and the deciding check (309 to 315) is outside it. **Recommended
  (optional) re-anchor:** code alternative `lines: [301, 315]`.
- **R7 PASS.** One entry with two alternatives.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** The ticket is closed and the code is settled.

### q30 (ticket): the ticket for gitleaks' remembered verdicts, and where the record is kept

**Verdict: enter as written.**

- **R1 PASS.** DAEO-kiar (W2-107) is closed. The code's `DEFAULT_REL = ".cache/gov-os/secrets-scan.sqlite"` and its
  docstring match the gold answer's location, sharing and keys.
- **R2 PASS.** The sources are in `tickets`, `docs` and `gov-source`.
- **R3 PASS.** The question asks two facts, one per entry.
- **R4 PASS.** An engineer on rebuild speed asks this.
- **R6 PASS.** Each of the four alternatives' spans holds its piece.
- **R7 PASS.** Each alternative holds its entry's whole piece.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** It has the same form as Q08 ("which ticket builds X") but asks a different fact.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** The ticket is closed and the code is settled.

### q31 (contract): what an owner question holds, and how many at once

**Verdict: enter as written.**

- **R1 PASS.** The Charter, Contract v4.2 and DEC-093 are ACCEPTED. DEC-220 amends DEC-093 only as to which
  packages reach the owner; the cap and the P1 bypass stand. `master-rules/MR-6.md` is PROPOSED and is rightly left
  out.
- **R2 PASS.** The sources are in `docs`.
- **R3 PASS.** The question asks two facts.
- **R4 PASS.** A lead or the orchestrator asks this while preparing a package.
- **R6 PASS.** The Charter span (115 to 118) holds the eight fields, and the other three alternatives hold the cap.
- **R7 PASS.** There are two entries for two pieces. The Contract's two forms and DEC-093 are rightly alternatives
  of one entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** This is distinct from q37 (what a contradiction's package proposes).
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It changes only by a decision.

### q32 (failure-memory): why the Phase 1 write guard let new paths through

**Verdict: enter as written.**

- **R1 PASS.** L-0074 is ACTIVE and the gold answer restates it faithfully. DEC-041 is PROPOSED and is rightly
  left out. CAP-58 carries the principle but not the incident.
- **R2 PASS.** The source is in `docs`.
- **R3 PASS.** It asks two facts, both in one span.
- **R4 PASS.** An engineer changing the guard asks this.
- **R6 PASS.** The span (12 to 16) holds the cause and the lesson.
- **R7 PASS.** One entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** This is distinct from Q19 (MR-3).
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It is a lesson.

### q33 (failure-memory): what a wait loop must have

**Verdict: enter as written.**

- **R1 PASS.** L-0075 is ACTIVE. No Contract item or decision states the bounded-wait rule more highly; CAP-41.d
  only carries the lesson.
- **R2 PASS.** The source is in `docs`.
- **R3 PASS.** One reading.
- **R4 PASS.** An engineer writing a script asks this.
- **R6 PASS.** The span (12 to 16) holds the rule and the incidents.
- **R7 PASS.** One entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It is a lesson.

### q34 (failure-memory): what the anti-snowball rule required before code changed

**Verdict: enter as written.**

- **R1 PASS (advisory).** L-0077 is ACTIVE and the gold answer is faithful. The rule is still in force as the
  Contract's CAP-59.c ("finding → whole-system context → one disposition before code"). CAP-59.c does not list the
  six dispositions, so it cannot be an alternative. **Optional re-word of the gold answer:** add "carried in the
  Contract as CAP-59.c".
- **R2 PASS.** The source is in `docs`.
- **R3 PASS.** The past tense presupposes nothing false.
- **R4 PASS.** A lead deciding how to answer a review finding asks this.
- **R6 PASS.** The span (14 to 29) holds the sequence, the six dispositions and the "only after" line.
- **R7 PASS.** One entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It is a lesson.

### q35 (kernel-template): does an independent auditor fix what it finds

**Verdict: enter as written.**

- **R1 PASS.** The role file at the head says so, and no higher record states it.
- **R2 PASS.** The source is in `kernel-template`.
- **R3 PASS.** One reading.
- **R4 PASS (advisory).** The orchestrator, deciding who repairs a finding, is the role that needs this. An
  auditor already has its own role file loaded.
- **R6 PASS.** The span (18 to 19) holds the authority line whole.
- **R7 PASS.** One entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** This is distinct from Q15 (the two lines a finding carries).
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It changes only by a ticket about the role file.

### q36 (kernel-template): how a probe finding reaches the test designer

**Verdict: enter after a fix.**

- **R1 PASS (minor note).** DEC-136 and the test-design skill are ACCEPTED and faithful. However, the highest
  current record that states the rule, by R1 item 1's order, is the Contract's `CAP-38.e` (ACCEPTED: CONTRACT_v4.md
  line 605, `contract.yaml`'s `- id: CAP-38.e`, `capabilities/CAP-38.e.md`), and it is not an alternative. A hit on
  the governing source would therefore be scored a miss.
  - **Recommended re-label:** add those Contract records as alternatives of the one entry.
  - **R5 effect:** count q36 under the Contract domain, not decisions, as the writer did for q37 (CAP-33.e with
    DEC-105).
- **R2 PASS.** The sources are in `docs` and `kernel-template`.
- **R3 PASS.** It asks two facts. "My acceptance tests" leans to the test designer's reading, and the gold answer
  serves the engineer's reading too.
- **R4 FAIL (`R4-PHRASED-FROM-ANSWER`, minor).** "When the orchestrator's review finds a case my acceptance tests
  miss" is DEC-136's and CAP-38.e's own clause, nearly word for word. **Recommended re-word**, for example: "A
  reviewer found a behaviour that no acceptance test covers. How is it handed to the test designer, and what do I
  decide about it?"
- **R6 PASS.** The DEC-136 `###` span (1238 to 1247) and the skill's `##` section (28 to 35) each hold the answer.
- **R7 PASS.** One entry with two whole alternatives.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** This is distinct from Q19.
- **R10 PASS.** `kernel-template` is on the category list.
- **R11 PASS.** It changes only by a decision.

### q37 (contract): what goes to the owner when a finding contradicts a closed specification

**Verdict: enter as written.**

- **R1 PASS.** CAP-33.e is ACCEPTED in both of the Contract's forms, and DEC-105 and the change skill agree.
- **R2 PASS.** The sources are in `docs` and `kernel-template`.
- **R3 PASS.** One reading.
- **R4 PASS (advisory).**
  - "A finding contradicts a closed specification" is CAP-33.e's wording, but it is also the project's standing
    term (it appears in `CLAUDE.md`).
  - The three options are stated in `CLAUDE.md`, which every session loads. `CLAUDE.md` is not a whole alternative,
    since it lacks the CIT-E record and the versions kept, so it is rightly not listed.
- **R6 PASS.** All four spans hold the whole answer.
- **R7 PASS.** One entry with four whole alternatives.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** This is distinct from q31.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It changes only by a decision.

### q38 (decision): where the Task, Implements and Role trailers go

**Verdict: enter as written.**

- **R1 PASS.**
  - DEC-182 is ACCEPTED, and no later entry changes it: later entries only cite it under "Under".
  - The fallback for commits before 2026-10-03 holds in the code (`TRAILER_RULE_DATE` in `src/gov/store/loader.py`,
    and `src/gov/decisions/checker.py`).
  - No Contract item states the rule.
- **R2 PASS.** The source is in `docs`.
- **R3 PASS.** It asks two facts, held by one entry.
- **R4 PASS.** Any worker committing asks this.
- **R6 PASS (advisory).** The `###` span (1691 to 1703) runs into the register's version table (1700 to 1702).
  The row it reaches restates DEC-182, so this is not an overrun on unrelated text.
- **R7 PASS.** One entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It changes only by a decision.

### q39 (code-paraphrase): routing a serial-only entry to the nightly

**Verdict: enter as written.**

- **R1 PASS.**
  - The code at the head matches the docstring: `nightly()` takes the comment's first word before ":", `nightly`
    routes the entry, any other word keeps it, and the result is `routed - kept`.
  - `command.py:920` calls `serial.phase`.
  - The plugin is product code under `src/`, not test harness (R1.3).
- **R2 PASS.** The source is in `gov-source`.
- **R3 PASS.** It asks two facts.
- **R4 PASS.** An engineer adding a slow test to the list asks this.
- **R6 PASS (advisory).** The span is the module docstring (1 to 13), which states the whole rule. The deciding
  check (line 37) is outside it. The 24 already accept docstring spans (Q02, Q03), so this is not a fail.
- **R7 PASS.** One entry.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** This is distinct from Q23 (the close's test map).
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** W2-57 is closed and the code is settled.

### q40 (code-paraphrase): can a release version be built again

**Verdict: enter as written.**

- **R1 PASS.** DAEO-49o5 is closed, and the code refuses a known version (`_known`, then lines 174 to 176: "a
  release is immutable").
- **R2 PASS.** The sources are in `gov-source` and `tickets`.
- **R3 PASS.** One reading.
- **R4 PASS.** An engineer or the orchestrator cutting a release asks this.
- **R6 PASS (advisory).** The docstring span (1 to 9) states the rule, and the check (174 to 176) is outside it.
  **Optional:** add `src/gov/release/__init__.py` `lines: [174, 176]` as a third alternative.
- **R7 PASS (advisory).** The ticket alternative (34) holds the asked "no, refused". The gold answer's detail ("a
  record in the tree, any ref's history or a tag") is only in the code alternative.
- **R8 PASS.** No evaluation source.
- **R9 PASS.** No other of the 40 asks this.
- **R10 PASS.** Form and category are correct.
- **R11 PASS.** It is settled code and a closed ticket.

## 4. R5 for the visible 40 (the writer's table checked)

The 24 are taken at integrate's head; the writer's own count, Q04 under the Contract, is kept.

### Governing domains

| Governing domain | Writer | This check | Of 40 | At least 4 (10 %) |
|---|---|---|---|---|
| Decisions | 10 (with q36) | **9**: q36 moves to the Contract (CAP-38.e) | 22.5 % | yes |
| Code | 10 | 10 | 25 % | yes |
| Tickets | 6 | 6 (4 if Q07 and Q14, which fail R11, are retired) | 15 % | yes |
| Contract and Charter | 6 | **7** (with q36) | 17.5 % | yes |
| Plan | 4 | 4 (q25 to q28) | 10 % | yes, **at the minimum** |
| None of the five (q32 to q35) | 4 | 4 | | n/a |

Notes on the domains:

- **The plan sits exactly at the 4 minimum.** q27's "is it in Wave 2" is decided by DEC-841 item 4. A reader who
  places q27 under decisions leaves the plan at 3 of 40 (`R5-DOMAIN-THIN`). This check places it under the plan,
  because only the plan holds the asked reason.
- **Q03's main entry is code** (`ollama.py`), and the writer counted it under decisions. Either placement keeps
  every domain at or above 4.

### Tags and limits

| Tag or limit | Count | Met |
|---|---|---|
| Failure or lesson memory, citing a lesson | 3 (q32, q33, q34) | yes, at the minimum |
| Kernel roles or skills | q35 (role), q36 and q37 (skills as alternatives); Q19 (role files) | yes |
| Supersession with a superseded naive answer | 4 (Q03, Q05, Q16, Q21) | yes |
| Retrieval and the context packet, at most 10 | 10 (Q01 to Q04, Q09 to Q13, Q17); none of the 16 | yes, **at the limit** |
| Any other subsystem, at most 10 | the close and the nightly 4; the guard 3; the others 2 or fewer | yes |

On the retrieval limit: Q06 (W2-54, a context-packet ticket) and Q08 (the commit-time re-index) could be read as
retrieval, which would put the subsystem at 11 or 12 of 40. Their asked facts are a ticket's fields and a ticket's
ownership, so this check agrees with the writer's count of 10. There is no headroom.

### Category table

The writer's category table (R5 item 6, for information on the visible half) is correct: it sums to 40, with
`exact-string`, `callers`, `kernel-template`, `multi-file`, `history` and `nonexistent-id` short. With q36 kept as
`kernel-template`, the table is unchanged.

**R5 verdict: PASS for the 40, with no margin on the plan, lessons or retrieval.** The next visible additions should
be the writer's proposed 2 exact-string, 1 callers, 1 history and 1 nonexistent-id questions, plus one plan question
for headroom. None of them should be on retrieval.

## 5. Outside the 16 (for the visible labels' checker, not judged here)

- Q19, at integrate's head, lists `docs/contract/master-rules/MR-3.md` as an alternative, and that record's status
  is PROPOSED. By R1 item 2 a PROPOSED record is never a gold source. The writer of the 16 left out
  `master-rules/MR-6.md` for the same reason.
