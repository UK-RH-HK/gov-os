---
type: probe
task: DAEO-k7hz
reviewer_session: fd80e44c-3cce-4e9d-ab90-82ec65f42711
implementer_session: 0ffacb20-25c6-46db-a789-b43550056fdb
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 095167b86fe3d6fde417cc7ee4d62f6b641d0281
---

# CIT-P review, W2-11 (DAEO-k7hz) round 1: the briefs, the orchestration, audit, test-design and qa-review skills, the skill template, the skill versions; pass, seven findings, none fails open or loses work

- **Who.** A fresh independent reviewer (`independent-auditor`, launched sandboxed by `gov launch`, read-only tools, effort high), session `fd80e44c`. It wrote nothing; the lead commits this record (DEC-733). The implementer sessions were product-spec `0ffacb20` (batches 1 to 4), `e0d97698` (repair 1) and `5bec648c` (repair 2); the independent test designer was `58b8c27a`.
- **What was judged.** The CIT-P `docs/changes/W2-11-CIT-P.md` against the diff `4c064bab..095167b8` (64 files, 13 commits), on the lead's three questions: does any template, skill or role file still teach a superseded rule; does the skill template meet DEC-959 item 5; do the kernel files carry anything scoped to this repository. No suite re-run (DEC-959 item 1); single read-only commands only (the skill validator and the adapter check).
- **The lead's judgement.** Pass, by JUDGEMENT.md's rules: no finding is "yes" to "Can an honest agent hit this in ordinary work?" together with "fails open" or "loses work" to "Does it fail open or lose work?". F1 to F6 are text edits that ride along in this ticket's resume, which follows anyway (DEC-802); F7 is a row.

## Scope

The CIT-P judged against the diff 4c064bab..095167b8: the five brief templates, `templates/skill.md`, the orchestration, audit, test-design and qa-review skills with their reference files, the version lines of every kernel skill, the DEC-866 sentences of `roles/orchestrator.md`, and their rulesync sources. Read-only. The skill validator (all nine touched skills and the template: no finding) and the adapter check (exactly the 16 copies the CIT-P names as `GENERATED_DIFFERS`, nothing else). Judged under ADR-0001's threat model with the two questions.

## Question 1: superseded rules

Checked by id and by value: LEAD_CHECKPOINT and context-limit stops; listing or search refusals over the governance folder or `.claude/`; the held-out names; fixed ceilings; owner commits; "tests first / before implementation"; full-suite runs outside the nightly; entries marked SUPERSEDED or Changed by.

- None remains in the five briefs, the orchestration skill and its four reference files, the audit, test-design and qa-review skills, or the skill template: a checkpoint at every handover and the model's full window (DEC-837, DEC-838); Policy 2's four refusals with the held-out file names readable (DEC-820), DEC-508's and DEC-525's refusals removed; no fixed number of tickets in flight (DEC-847); decision-record commits, no `Role: owner` or `Decided-by:` from a worker or lead (DEC-861, DEC-862); the parallel work order, red against the ticket's base (DEC-959 item 7, DEC-963); never the full suite outside the nightly (DEC-968).
- DEC-430 is restated as "written by the independent test designer, not by the implementer" in the audit skill and the briefs-and-returns reference file, ahead of the register, which the CIT-P's P-1 asks to mark.
- In the role file, the sentence this round edited still says a lead's return "starts with one of these forms" and that `AUTH_REQUIRED` comes "as its first line" (F2). Its "tests first" and code-span launch in the lead section are known and given to W2-33.
- The orchestration skill's close step "a full regression runs (DEC-536): the nightly's" does not teach a full run outside the nightly but reads awkwardly; DEC-536 is not marked as changed by DEC-968 (F4).

## Question 2: the skill template (DEC-959 item 5)

`templates/skill.md` meets item 5 and ROLES-RESEARCH-1 §2's opening: front matter (`name`, `version`, a third-person `description` of what and when, `metadata.version`); When / not when; Inputs (with `gov retrieve` first); Steps as a checklist; Done when (check, fix, check again); Output and handover (the twelve fields and the typed handoff kind); Escalation (P3, P2, P1, Emergency, and to whom); Never ("reminders only: the guard decides"); Sources at the end; the body under about 150 lines, reference files one level deep; three scenarios with situation, expected behaviour and pass line, committed (`adeda5b88c69`) before the text (`99dd5ca5235d`); an imported skill adopted only with its source, version and licence recorded and its three scenarios passing.

qa-review follows the template: the same sections in order, a third-person description; its three scenarios (an untraced KPI line; a deliberate-construction hole classed as a row; an unresolved fail-open escalated as P1) committed before the text; trace, tests against the spec, code against the spec, probes in proportion to LITE/STANDARD/FULL, the two lines, severity tied to P3/P2/P1; it re-runs nothing; body 72 lines; the validator finds nothing.

Neither set of scenarios has been run on a fresh session yet (required before promotion); the CIT-P does not say so, nor that the revised orchestration, audit and test-design skills are not yet in the template's form (F6).

## Question 3: repository-scoped text in kernel files

Clean of W2 ticket ids, EXAMIN, `select_tests.py`, `verify_lock.sh`, `disk_gate.sh`, `close_build.py`, `~/gov-os-worktrees`, `w2/` branches and this repository's main-tree paths; a project's values stand as placeholders (DEC-539); the judgement rules point to `<the project's threat-model record>`. Edge cases: test-design's "2,980 test lines for 713 code lines" is a measured example of too much, without the ticket id, as the KPI requires (sound); test-design names `gov accept` and "the form its in-progress code reads" for the README map, a forward dependency on an unfinished format (F5); brief-lead's DEC-732 bullet fixes `/src` beside the placeholder setting (F7).

## The CIT-P against the diff

The evidence, the options (DEC-105), the impact, the rollback and §6 (round 2, the generated copies, the launcher reader, P-1 to P-7, the open rows) are truthful against the diff. §4's validator and adapter claims hold exactly. The skill versions are as stated: orchestration 1.0.0→1.1.0, audit 1.1.0→1.2.0, test-design 1.0.0→1.1.0, qa-review new at 1.0.0; the five other skills gain `metadata.version` equal to `version` and nothing else; adopt untouched (DEC-981). Not truthful at the head: the brief templates' version entry "template 2.0.0 (none before)" (now `<brief version>`), and repairs 2 and 3 are not described (F1). "Every kernel skill but adopt" leaves out the three vendored skills (F3).

## Findings

F1. **The CIT-P is stale against the head on the briefs' version and on repairs 2 and 3.** Where: `docs/changes/W2-11-CIT-P.md` §2 (the brief row, the repair paragraph). Severity: P2 (the owner approves stated before-and-after versions, CAP-33).
Ordinary work: yes, because an author who repairs files after writing the proposal easily leaves its table behind.
Consequence: other
Blocks the CIT-P: no; corrected before the K3 package goes to the owner (rides along, DEC-802).

F2. **The role file's edited lead-return sentence still puts the status first.** Where: `template/governance/kernel/roles/orchestrator.md` and its rulesync sources ("starts with one of these forms"; "`AUTH_REQUIRED` as its first line"), against the twelve fields first with `AUTH_REQUIRED` as the status (CAP-37). Severity: P3.
Ordinary work: yes, because a lead loads the generated role file and may put the status line first.
Consequence: other (the lead's return is checked and sent back, DEC-793; nothing fails open)
Blocks the CIT-P: no; fix the clause or name it in §6 for W2-33.

F3. **"Every kernel skill but adopt" leaves out the three vendored skills** (`superpowers/{test-driven-development,systematic-debugging,verification-before-completion}` and their copies carry no version; outside the paths, digests in `vendored.yaml`). Severity: P3.
Ordinary work: yes, because the launcher's implementer may read the CIT-P as covering every skill copy.
Consequence: other (the launcher's reader finds no version and refuses; it does not fail open)
Blocks the CIT-P: no; state it in §6 with its owner.

F4. **Formatting slips and one muddled sentence in the orchestration skill** (and its two rulesync copies): under Sessions a bullet run onto the previous one; "Temp hygiene and protected files" holds no protected-files rule and the next heading follows with no blank line; integration step 4's "a full regression runs (DEC-536): the nightly's". Every rule's text survives. Severity: P3.
Ordinary work: yes, because a session skimming the list can miss the merged rule.
Consequence: other
Blocks the CIT-P: no; rides along.

F5. **test-design teaches a README-map form tied to an unmerged runner's code in progress** (`skills/test-design/SKILL.md`, `test-kinds.md`), while this ticket's own README uses a YAML map. Severity: P3.
Ordinary work: yes, because a test designer follows the skill's table and the runner may read another form.
Consequence: other (a README with no map is refused: it fails closed)
Blocks the CIT-P: no; name the dependency in §6 and align when the runner merges.

F6. **The CIT-P's tests section is silent on the scenarios not yet run and on the revised skills' form.** Where: CIT-P §4 and §6. Severity: P3.
Ordinary work: yes, because a reader takes "three scenarios first" as also run.
Consequence: other
Blocks the CIT-P: no; one line each.

F7. **brief-lead fixes `/src` beside a placeholder** (`templates/brief-lead.md`, the code-under-test bullet). Severity: P3.
Ordinary work: no, because a project whose code is not under `src/` fills the bullet when it fills the placeholder, and the lead's quoted import line shows where the code was loaded from.
Consequence: other
Blocks the CIT-P: no; a row.

Classification: 7 findings; none is "yes" with "fails open" or "loses work"; six are "yes"/other (F1 to F6), one is "no" (F7, a row). The review passes.

## What was sound

The supersession sweep by value across all in-scope kernel files and both rulesync copies (byte-identical); the parallel work order with one writer per worktree and red against the base; Policy 2 rule (c) worded per role; the twelve-field block word for word in every brief; G14 (`brief_gaps:` in the lead brief); G15 (the judgement rules in the reviewer brief and the audit skill, word for word, kernelized to the project's threat-model record); the escalation rubric with placeholder thresholds; the three orchestration reference files kept generic (the merge queue fails closed, the nightly is the only full run, incident response stops and contains first); the skill template and qa-review with scenarios committed first; G13 versions on nine skills, adopt left out (DEC-981); §4's claims verified (the validator finds nothing; the adapter check shows exactly the 16 copies); the W1-35 cases revised by the test designer with `Rewrite-Reason`.
