---
id: DAEO-wahn
status: in_progress
deps: []
links: [DAEO-t8mp, DAEO-k7hz, DAEO-h4rh]
created: 2026-11-11T20:00:00Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-175
tags: [wave-2, templates, kernel, cit-p, standard]
wbs_id: W2-175
title: 'The role templates carry Policy 2''s four refusals (DEC-820), DEC-861''s record rule and the stop after two refusals (DEC-1137 (2); a template delta through DEC-1116''s route)'
class: template
state_class: AUTHORITATIVE
role: product-spec
profile: STANDARD
depends_on: []
allowed_paths:
- template/governance/kernel/templates/role-*.md
- docs/changes/W2-175-CIT-P.md
# .claude/templates/role-*.md out of the paths: byte copies of the kernel templates, written only by the copies ACT after the owner's approval (DEC-315, as in W2-128)
reads:
- template/governance/kernel/templates/**
- governance/project/facts.yaml
- docs/changes/W2-128-CIT-P.md
- governance/project/orchestration/packages/LIFT-1/TEMPLATES-APPROVAL-1.md
- governance/project/orchestration/packages/P1-W2-11-BRIEFS.md
- tests/acceptance/W2-128/test_w2_128_templates.py
needs:
- template/governance/kernel/templates/role-engineer.md     # W2-128's text as approved (DEC-1116), version 1.0.0
- template/governance/kernel/templates/role-test-designer.md
- template/governance/kernel/templates/role-product-spec.md
- template/governance/kernel/templates/role-research.md
- template/governance/kernel/templates/role-reviewer.md
- template/governance/kernel/templates/role-lead.md
- template/governance/kernel/templates/role-cto.md
- template/governance/kernel/templates/brief.md             # its return section holds the stop sentence the role templates repeat word for word
waits_on:
- ref: DAEO-t8mp
  reason: W2-128 still holds template/governance/kernel/templates/** in its paths; it writes no role template again (its text is approved, DEC-1116), but the CTO confirms that before this ticket starts
est_loc: 60
kpis:
  success:
  - line: "Each of the seven role templates (role-cto, role-engineer, role-lead, role-product-spec, role-research, role-reviewer, role-test-designer) states, in one statement, that reads are open and that only four things are refused, in DEC-820 item 2's words: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); (c) the counterpart's work on the same ticket; (d) the hidden half of an evaluation set; the statement ends with [DEC-820]"
    verify: "tests/acceptance/W2-175/: for each of the seven files, one statement (a paragraph, a list item or a table row, whitespace collapsed) carries `read` with `open`, `secret`, `held-out`, `counterpart` and `hidden half` and ends with `[DEC-820]`; red on the base (no template cites DEC-820 for it)"
  - line: "The counterpart refusal (c) is stated in each role's own half: role-engineer says the engineer never reads this ticket's acceptance-test code and may run its cases and see names, pass or fail and failure messages; role-test-designer says the designer never reads this ticket's implementation (the branch's changes other than its own tests) and works from the specification, the KPI lines and the existing code; role-reviewer says a reviewer reads everything, tests and code alike [DEC-820 item 2 (c) and item 3, DEC-957, DEC-963]"
    verify: "tests/acceptance/W2-175/: three string tests, one per file, each on one statement carrying a negation (`never`, `not`) for the engineer's and the designer's, and `everything` with `tests` and `code` for the reviewer's; and tests/acceptance/W2-128/test_w2_128_templates.py::test_s3_engineer_template_holds_no_instruction_to_read_the_acceptance_tests still passes"
  - line: "Each of the six templates role-engineer, role-test-designer, role-product-spec, role-research, role-reviewer and role-lead states that the owner's decisions are recorded by the orchestrator's decision-record commits and that no worker or lead puts `Role: owner` or `Decided-by:` on a commit; role-cto keeps its decision-record commit line (`Task: decision-record`, `Role: orchestrator`, `Decided-by: owner (chat, {DATE})`) unchanged [DEC-861]"
    verify: "tests/acceptance/W2-175/: for each of the six, one statement carries `decision-record`, `owner` and `Role: owner`, and ends with `[DEC-861]`; for role-cto, the line of the base is still there byte for byte (a test reads it from `git show` of the base commit)"
  - line: "Each of the seven role templates carries, word for word, the stop sentence of the brief envelope's return section: \"Refused twice for the same call: stop and say so. Never work around a refusal: report it.\" [DEC-1137 (2)]"
    verify: "tests/acceptance/W2-175/: each of the seven files holds that sentence, and the sentence is a substring of brief.md too (one source of wording, so TPL-6 F1's conflict cannot arise)"
  - line: "Each changed role template's `version` goes from 1.0.0 to 1.0.1 (DEC-1121's step for a template delta); no other front matter key changes, and the prose of each stays within its budget in `governance/project/facts.yaml` (3500 characters, role-lead 8000, role-cto 6000) with every placeholder a key of `keys.yaml` [DEC-1050, DEC-1116, DEC-1121]"
    verify: "tests/acceptance/W2-175/: the front matter of each changed file parses with `version: 1.0.1` and the other keys equal the base's; tests/acceptance/W2-128/test_w2_128_templates.py::test_s2_prose_is_within_r3_budget and ::test_s5_every_key_placeholder_is_in_keys_yaml pass for all seven"
  - line: "The cases of W2-128, W2-152 and W2-153 that read the role templates still pass with the new text (the gov brief golden files, the template tests, the launch delivery) [DEC-1050, DEC-1116]"
    verify: "`PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-128 tests/acceptance/W2-152 tests/acceptance/W2-153 -q -p no:cacheprovider` exits 0 in the ticket's worktree, run through the heavy-job gate"
  - line: "The change goes through DEC-1116's route, recorded in docs/changes/W2-175-CIT-P.md: the template delta (each changed file, its base and new sha256, the lines added), the independent review's READY, and the owner's approval of the new bytes; the record's `status` is ACCEPTED only after that approval, and the kernel set is promoted at the approved bytes [CAP-33, DEC-1116, DEC-1137 (2)]"
    verify: "docs/changes/W2-175-CIT-P.md has a section per CAP-33 step (evidence, proposal, independent review, owner's approval, versioned promotion); the sha256 column equals `sha256sum` of each file at the ticket's head; the file's `decisions_read` and `decisions_carried` cite DEC-1137, DEC-820 and DEC-861"
  failure:
  - line: "A role template line that states a rule cites a PROPOSED or superseded decision for it, or states a stop rule that differs from brief.md's [DEC-1073, TPL-6 F1]"
    verify: "tests/acceptance/W2-128/test_w2_128_templates.py::test_f7_every_bracketed_decision_id_in_a_template_is_accepted passes for the seven files; the substring test of the stop sentence (success line 4) fails when one file's sentence is changed by a letter"
  - line: "The ticket's diff names any file beyond the seven role templates and docs/changes/W2-175-CIT-P.md: not brief.md, a `brief-*.md` pointer, keys.yaml, facts.yaml, a skill, a file under `roles/`, any `.claude/` or `.rulesync/` path [DEC-1137, DEC-315]"
    verify: "`git diff --name-only <base>..HEAD` of the ticket's branch lists only those paths (a close-time check; the guard refuses the rest at write time)"
non_goals:
- no change to brief.md, the five `brief-*.md` pointers (they stay as W2-128 left them, DEC-1137 (1)), keys.yaml, facts.yaml or the role files under roles/
- no change to the orchestration skill or any skill (W2-11 holds them)
- 'the `.claude/templates/role-*.md` copies are not written here: the copies ACT writes them after the owner''s approval (DEC-315)'
- no new rule beyond the three the owner named (DEC-1137 (2)); no rewording of the rules the templates already carry
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1137, DEC-820, DEC-861, DEC-1116, DEC-1050, DEC-1121, DEC-957, DEC-963, DEC-1073, DEC-315, CAP-33, DAEO-t8mp, DAEO-k7hz, DAEO-h4rh]
acceptance_tests:
  path: tests/acceptance/W2-175/
  author: independent-test-designer (MR-3), from these KPI lines
track: A
list_rows: []
---
# W2-175 The role templates carry Policy 2's four refusals, DEC-861's record rule and the stop after two refusals

**Problem.** W2-128 (templates 1.0.0, approved by DEC-1116) replaced the five `brief-*.md` files with one-line pointers
and gave each role one template. W2-11's brief text carried three live rules that the role templates do not state today:
Policy 2's four refusals (DEC-820: `role-engineer.md` and four others have none; `role-test-designer.md` holds only the
counterpart half in one line), DEC-861's rule that the orchestrator records the owner's decisions (only `role-cto.md`
has it), and the stop after two refusals (it is in `brief.md`'s return section, in no role template). A launched session
reads its role template as the system prompt (W2-153), so a rule in no template is a rule that session never sees. The
owner decided on 2026-11-11 (DEC-1137 (2), (3)) that a small ticket adds them before EXAMIN's copy; W2-27 depends on it.
The analysis is `governance/project/orchestration/packages/P1-W2-11-BRIEFS.md`.

**Approach (if known).** One product-spec session adds to each of the seven role templates the lines below, near each
template's existing rule lines, ending each with its decision id in brackets, then raises the `version` of each changed
file to 1.0.1 and writes the CIT-P record with the base and new sha256 of every file. The independent review reads the
delta only; the owner approves the new bytes (the route of DEC-1116); the CTO then runs the copies ACT for
`.claude/templates/`. Alternative, costed and set aside: put the rules in `brief.md` only (every session reads it, but a
role's system prompt would still lack them, and the owner asked for the templates).

**Interface (the lines, stated before the pair starts).** A template may shorten a line; it may not drop an idea.
- Policy 2, all seven: "Reads are open: the whole repository, other worktrees, git history and what your searches return.
  Refuse only four things: secrets and keys (never printed); the held-out qualification material's contents (its file
  names may be seen); the counterpart's work on the same ticket; the hidden half of an evaluation set [DEC-820]."
- (c), the engineer: "Never read this ticket's acceptance-test code; run its cases and read their names, pass or fail and
  failure messages [DEC-820, DEC-957]." The sentence must carry a negation: W2-128's TPL-1 S3 case refuses an
  engineer sentence that names the acceptance tests with a reading verb and no `never`, `not` or `no`.
- (c), the designer: "Never read this ticket's implementation (what its branch changes other than your own tests); work
  from the specification, the KPI lines and the existing code [DEC-820, DEC-963]." Line 4 of the base already says the
  first half; keep it and add what is missing.
- The reviewer: "You read everything, tests and code alike [DEC-820]."
- The record rule, the six non-CTO templates: "The owner's decisions are recorded by the orchestrator's decision-record
  commits; never put `Role: owner` or `Decided-by:` on a commit of yours [DEC-861]."
- The stop, all seven: "Refused twice for the same call: stop and say so. Never work around a refusal: report it."
  (the sentence of `brief.md`'s return section, copied, then `[DEC-1137]`).
- The base for the sha256 and the diff checks is the commit the ticket's branch starts from; the record names it.

**Rabbit holes.**
- Do not edit `brief.md`, a pointer, `keys.yaml` or `facts.yaml`; the stop sentence is copied from `brief.md`, never reworded.
- Do not cite DEC-849 or DEC-508 as the rule: DEC-849 stands only until W2-58 lands and DEC-820 replaced DEC-508.
- Do not add a placeholder that is not in `keys.yaml`; `{DATE}` and `{ID}` are keys, a literal date is not.
- `role-reviewer.md` is the tightest against its 3500-character budget: measure before the lines go in.
- Do not write `.claude/templates/`; `python3 -m gov.adapters.portability` reports those copies as differing until the
  copies ACT runs (as after W2-128), so the close of this ticket names that finding and does not fix it.
