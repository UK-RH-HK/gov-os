# W2-11 (`DAEO-k7hz`): the re-baseline of its brief KPI lines (DEC-1137 (1)), each changed line before and after

Draft for the CTO (helper, 2026-11-11 ~20:00 UTC). The patch is `ticket-rebaseline.patch` beside this file: a unified diff
with no context lines, so apply it with `git apply --unidiff-zero` (the CTO's commands are in the helper's return). It
changes `.tickets/DAEO-k7hz.md` in the front matter's KPI lines (six lines rewritten, one removed), `sources` (one
id) and the body (one paragraph). It was checked with `git apply --check --unidiff-zero` against the main tree and the
result parses (16 success lines, 2 failure lines; before: 17 and 2).

What the re-baseline rests on: W2-128 turned the five `brief-*.md` files into one-line pointers (the one line reads:
"Replaced by `role-<x>.md` (the role) and `brief.md` (the envelope) in this folder (DEC-1050, TPL-1)"), and DEC-1137 (1)
keeps them so. A line is rewritten to name the orchestration skill (or the skill or template the decision lists) or is
removed where its only subject was a brief template's content. No line that is not about the briefs is touched.

## 1. The changed lines (numbered as the README map of `tests/acceptance/W2-11/` numbers them: success-N, failure-N)

| line | before | after | why |
|---|---|---|---|
| success-2 | Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6]. | The orchestration skill carries the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6]. | the five templates are pointers; the skill half is kept whole; the role templates' half is W2-175's (DEC-1137 (2)) |
| success-3 | They also carry Policy 2's read rule (...) and the decision-record rule (...) [DEC-866]. | It also carries Policy 2's read rule (...) and the decision-record rule (...) [DEC-866]. | same; the rest of the sentence is byte for byte |
| success-4 | The audit brief states DEC-430 [F-m1, W2-L268]. | The orchestration skill's audit brief rule states DEC-430, as the audit skill's own wording does [F-m1, W2-L268]. | no `brief-audit` file exists; the case reads the orchestration skill; this names where the sentence is and keeps its meaning (DEC-1137 (1): "the audit's DEC-430 wording") |
| success-5 | The launcher command is stated as a command, not a code span [W2-L257]. | removed | its only case reads `brief-lead.md` (now a pointer; `role-lead.md` uses the `{CMD:launch_worker}` key, W2-128); the role file's half was already W2-33's (DEC-981) |
| success-6 | The five brief templates carry record frontmatter [W2-L258], and loose citations are fixed [W2-L256]. | Loose citations in the orchestration skill are fixed [W2-L256]. | the frontmatter half names the five pointers; the citations half is the skill's (DEC-183 for identity, DEC-486 for the stop's block) |
| success-7 | Supersession (DEC-866): the brief templates, the orchestration skill and its copies, and the orchestrator role file and its copies no longer teach a superseded rule: ... | Supersession (DEC-866): the orchestration skill and its copies, and the orchestrator role file and its copies no longer teach a superseded rule: ... | only "the brief templates, " is dropped; the rest of the line, the W1-35 sentence included, is byte for byte |
| success-13 | The kernel's lead brief template carries a `brief_gaps:` section (gap, where it belongs, its cost) after the twelve fields, and the orchestration skill states that the gaps are fixed in the template within the week (DEC-943, ROLES-SPEC-1 G14) [DEC-983, DEC-982] (to Wave 3, W3-P02, W-10) [re-scoped, DEC-1083] | The orchestration skill states that the gaps a worker names in `brief_gaps:` (the return of the brief envelope, W2-128) are fixed in the template within the week (DEC-943, ROLES-SPEC-1 G14) [DEC-983, DEC-982] (to Wave 3, W3-P02, W-10) [re-scoped, DEC-1083] | the `brief_gaps:` section now sits in `brief.md`'s return (W2-128 TPL-7); the second half is kept, with its Wave 3 tag |
| `sources` | ... DEC-1112 | ... DEC-1112, DEC-1137 | the decision under which the lines changed |
| body | (none) | one paragraph under the heading: DEC-1137 re-baseline; the five files stay pointers; where the card's older bullet list below names a brief template, the front matter holds; the role templates' rules are W2-175's | the one body line asked for (the older list in the body is the card as approved, DEC-729, and is left as it is) |

Numbering note: the README map (written before DEC-983 and DEC-1112 added lines to the ticket) calls the DEC-866 failure
line failure-1; in the ticket file today it is failure-2, after the round-2 permission-field line. The designer keeps the
README's own numbering unless the CTO's ticket and the README disagree after the merge, in which case the ticket's wins.

Unchanged on purpose: success-1, 8 to 12, 14 to 16 and failure-1 and failure-2 (failure-2, the DEC-866 line, says
"a template, skill or role file" and stays as it is).

## 2. Three things the CTO decides (not in the patch, because the brief says never to weaken or widen)

1. **success-17 (the approvals section)** says "the orchestrator brief template carries it". No file of that name exists
   (the five are engineer, lead, product-spec, reviewer, test-designer). The nearest is `role-cto.md`, which is not in
   W2-11's `allowed_paths` and is W2-128's, approved text. The line is round 2's and has no case yet. I left it as it
   is. Options: (a) leave it and let the round-2 session ask; (b) rewrite it to "the orchestration skill has an approvals
   section" only, dropping the template half (the half would then be W2-175's scope or a new line there).
   Recommendation (b), confidence low; it is the one line left that names a template W2-11 cannot write.
2. **`allowed_paths` still lists `template/governance/kernel/templates/brief-*.md`.** The five pointers stay as integrate
   has them (DEC-1137 (1)), so the entry only lets a session overwrite a pointer. Remove it in the same edit: one line,
   `- template/governance/kernel/templates/brief-*.md`. Not done here (a paths line is not a KPI line).
3. **`list_rows` still lists W2-L257 and W2-L258**, whose subjects (the launcher command in `brief-lead.md`, record
   frontmatter on the five briefs) fall with the briefs. At W2-11's close they are "no longer applicable, W2-128 retired
   the files", with DEC-1137 as the reason, rather than "done". W2-L256 and W2-L268 stay (the skill's citations; DEC-430).

## 3. The W2-11 acceptance cases that test the removed or narrowed lines (read-only list; the designer retires or re-points them)

Folder `tests/acceptance/W2-11/` on `w2/W2-11`. "Retire" means the case (or those parameters) leaves the suite;
"re-point" means the same check on the files that remain.

| KPI line | file, test | action |
|---|---|---|
| success-2 | `test_w2_11_briefs.py::test_the_twelve_fields_come_first_payload_after_and_two_refusals_stop` | retire the five `brief-*.md` parameters; keep the orchestration skill's (re-point `RETURN_FILES` to the skill alone) |
| success-3 | `test_w2_11_briefs.py::test_policy_2_reads_open_with_its_refusals` | same: skill parameter stays; the five brief parameters go (the `counterpart` dictionary, which names two brief files, goes with them) |
| success-3 | `test_w2_11_briefs.py::test_the_owners_decisions_are_recorded_by_decision_record_commits` | same |
| success-5 | `test_w2_11_briefs.py::test_the_launcher_command_is_a_command_not_a_code_span` | retire |
| success-6 | `test_w2_11_briefs.py::test_the_brief_template_carries_record_frontmatter` (5 parameters) | retire |
| success-6 | `test_w2_11_briefs.py::test_identity_through_the_settings_argument_is_not_cited_to_dec_183`, `::test_dec_486_is_not_cited_for_the_stops_short_block` | keep (they read the skill) |
| success-7 | `test_w2_11_supersession.py::test_every_swept_file_is_there` | re-point: drop `*s.BRIEF_RELS` from `expected` |
| success-7 | `test_w2_11_supersession.py::test_the_file_teaches_no_superseded_rule` | re-point through `w2_11_support.py::supersession_files` (drop `*BRIEF_RELS` from `rels`) |
| success-7 | `test_w2_11_supersession.py::test_dec_460s_citation_for_naming_the_model_stays` | retire the `brief-lead.md` parameter; keep the skill's |
| failure-2 (the DEC-866 line, kept) | `test_w2_11_supersession.py::test_a_planted_file_that_still_teaches_the_old_rule_fails` | re-point: `PLANTED_IN[0]` is `brief-lead.md`, which the sweep no longer reaches; use a swept file (the orchestration skill's kernel path or a role file copy) so `supersession_files(tmp_path) == [rel]` still holds |
| success-13 | `test_w2_11_briefs.py::test_the_lead_brief_carries_the_role_independent_rule[brief_gaps in the return]` | retire (the line is now the skill's second half, Wave 3's; round 1 never had a case for it) |

Cases not under a ticket line (the README's list) that read a retired brief, and that go the same way:

| file, test | action |
|---|---|
| `test_w2_11_briefs.py::test_the_lead_brief_carries_the_role_independent_rule` (the other seven parameters: gov retrieve first, retrieval in batches, small code-graph queries, the code under test per command, the scratch budget and TMPDIR, a checkpoint at every handover, the work order in parallel) | retire; they read `brief-lead.md` only. `role-lead.md` and `brief.md` hold the live text and are W2-128's |
| `test_w2_11_briefs.py::test_the_judgement_rules_stand_word_for_word` | retire the `brief-reviewer.md` parameter; keep the audit skill's |
| `test_w2_11_briefs.py::test_the_kernel_states_the_distilled_decisions` | re-point the corpus to the orchestration skill's folder alone; a group no longer cited there goes back to the CTO as a finding (the card's DEC-791 (ii) wants the standing decisions in the kernel), never dropped quietly |
| `test_w2_11_briefs.py::test_no_id_or_path_of_this_repository_in_a_kernel_file` | retire the five brief parameters (`_kernel_files` drops `*s.BRIEF_RELS`) |
| `w2_11_support.py` | `BRIEFS`, `BRIEF_RELS` and the `*BRIEF_RELS` uses in `supersession_files` go once no case needs them |
| `README.md` (the KPI map) | rows success-2, 3, 5, 6, 7, 13 and failure-1's red reasons rewritten to follow; the "Notes" for success-5 and success-6 (W2-L258) removed; the count of cases updated |

Left alone: `test_w2_11_brief_gaps.py` (it reads the project's common brief, not a template), `test_w2_11_skills.py` (no brief
file), and everything under `tests/acceptance/W1-35/` (W2-128 and the designer's pre-merge commit settled it).

## 4. Correction, 2026-11-11 about 21:32 UTC (second helper): the numbers in section 1 and section 3 are the README's OLD numbers

The ticket's line numbers after DEC-1137 (success-5 removed) are: README success-6 is now **S5**, success-7 **S6**,
success-8 **S7**, success-9 **S8**, success-10 **S9**, success-11 **S10**, success-12 **S11**, success-13 **S12**,
success-14 to 16 **S13 to S15**, and the approvals line **S16**; the DEC-866 failure line is **F2**, the permission
field line **F1**. `gov accept` reads the n-th success and n-th failure line of the ticket by number, so the README map
must be renumbered in the same commit as the cases (`briefs/W2-11-A1-rebaseline.md`, step 3, has the table). Nothing
else in this file changes.
