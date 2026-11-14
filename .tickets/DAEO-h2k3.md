---
id: DAEO-h2k3
status: in_progress
deps: [DAEO-m1u3]
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-61h
tags: [wave-2, audit, evaluation, held-out, standard, keystone-4]
wbs_id: W2-61h
title: 'W2-61''s enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session'
class: audit
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: [DAEO-m1u3]
allowed_paths:
- fixtures/evaluation/memory-retrieval/visible/q21.yaml
- fixtures/evaluation/memory-retrieval/visible/q22.yaml
- fixtures/evaluation/memory-retrieval/visible/q23.yaml
- fixtures/evaluation/memory-retrieval/visible/q24.yaml
- src/gov/retrieval/measure.py
- tests/unit/retrieval/test_w2_61h_families*
- tests/unit/retrieval/test_w2_61h_anchor*
- governance/project/path-map.yaml
- tests/acceptance/W2-61h/test_w2_61h_hidden_form.py
- tests/acceptance/W2-61h/test_w2_61h_visible_new.py
- tests/acceptance/W2-61h/w2_61h_support.py
- tests/acceptance/W2-61h/README.md
kpis:
  success:
  - 'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner''s operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084] [changed, DEC-1171 (2)] Verify: tests/acceptance/W2-61h/test_w2_61h_visible_new.py''s S1 cases (q21 to q24 exist in measure.py''s question form and are the recorded seeded stratified draw''s share by category, the README''s record) pass in an ordinary run, and the visible folder holds q01 to q40; test_w2_61h_hidden_form.py''s S1 cases (the hidden count, each file in the question form) are run only by the owner''s operator in a walled run with GOV_EVAL_SETS_ROOT set, whose record gives pass or fail and counts only: 39 hidden files while h10 sits in retired-hidden/ with its reason line, 40 once the walled writer''s replacement lands (DEC-1171 (2); the count case revised to 39 by a test designer under that item); no launched session reads a hidden file'
  - 'Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61''s engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2] Verify: tests/acceptance/W2-61h/test_w2_61h_visible_new.py: test_s2_the_new_questions_and_these_tests_come_from_no_measured_role (every commit that writes q21 to q24 or these tests carries one Role, never one of the path map''s measures.roles) and test_s2_judges_the_role_on_a_planted_commit (red for a measured, other or missing role) pass, with the README''s record of the writer''s pruned commit c5c100729ce4 (Role: independent-test-designer); the hidden questions are refused to the retrieval roles by the measure and the guard, as S6 and F1 verify'
  - 'The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40''s table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084] [changed, DEC-1171 (2)] Verify: the visible four''s draw-share case in test_w2_61h_visible_new.py passes; in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s3_the_hidden_40_spread_as_r5_s_quotas_state (R5''s table, the owner''s accepted shortfall of one in decision, callers and code-paraphrase and no other, no category outside the twelve, each multi-file question on two or more paths) passes, on the half as DEC-1171 (2) leaves it, pass or fail only; the parts no test judges (at least 2 whose naive answer is superseded; each governing domain at least 10 % of each half; no subsystem above 25 %) are judged by the operator''s unmeasured cross-check, recorded by counts only'
  - 'Every gold source exists at its own commit and holds the answer there, cited by path and heading or line; at the head the auditor reads, a cited block that moved unchanged is no fault (the measure re-anchors it in memory, S8), and a cited block whose lines changed is listed by question id and entry number only, never failed and never blocking a close; the list goes to the walled writer in the weekly cycle (MEMORY-AUDIT''s G5 maintain pass, W2-187; the owner''s operator''s Monday slot until it lands) [DEC-828 item 4] [changed, DEC-1178 (1)] Verify: test_w2_61h_visible_new.py''s S4 and F3 cases, revised by a test designer under DEC-1178 (1), pass at the head the auditor reads: each new visible source resolves and holds its answer at its own commit; on planted data, a block moved unchanged at HEAD passes and a block whose lines changed is listed by question id and entry number and the case passes, while a source that does not hold its answer at its own commit is red; test_s4_no_new_visible_source_names_the_set_s_own_files passes; in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s S4 case judges the hidden sources the same way, its record giving pass or fail and the changed-lines list by file name and entry number only; that each hidden source holds its answer is judged by the operator''s unmeasured cross-check, recorded by counts only'
  - 'The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8] Verify: in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root passes: the sets root lies outside every git worktree list path and in no git work tree, has mode 700, no worktree or run clone under ~/gov-os-runs holds fixtures/evaluation/memory-retrieval/hidden/*.yaml, and no hidden file''s bytes are an object of this repository''s store or a run clone''s; for the quoting rule, the same walled run matches each hidden question''s and answer''s text against every commit message on every ref, the returns and logs under .gov-runtime/ and the .tickets/ files, and records the count of matches only, 0'
  - 'The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)] Verify: in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure passes (measure.py --sets-root <root> --part hidden, run as each measured role, exits 1 with a refusal and no output before any retriever is asked); a run of test_w2_61h_hidden_form.py against a throwaway sets root of planted faulty questions turns each case red for its fault with output holding no planted question, answer, category or gold path (file names and entry numbers only), and the whole module skips without GOV_EVAL_SETS_ROOT or under a measured GOV_ROLE'
  - 'S7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract''s `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source''s family counts as a hit on that source when its text holds the gold span''s text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure''s per-question line; with no family declared, every score is as today; a run''s kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)] Verify: tests/acceptance/W2-61h/test_w2_61h_families.py''s 13 cases pass on planted data (a member holding the gold span''s normalised text is a hit named by its path and the word family; a member whose text does not hold it, or a file outside the family, is no hit even on the same lines or with the same bytes; with no family declared every score is today''s; --kept re-scores a run''s kept outputs with families, asking no retrieve, to a fresh run''s figures), with tests/unit/retrieval/test_w2_61h_families.py; governance/project/path-map.yaml at HEAD declares evaluation_families: with the contract, kernel and agents families as member glob lists'
  - 'S8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source''s block again in the commit it measures (the block read at the source''s own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]'
  failure:
  - 'A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work. Verify: in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root and test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure pass, and the hidden-form cases skip under a measured GOV_ROLE; a probe read by an engineer and by a research session of a non-existent file under the sets root''s hidden folder is refused by the guard, recorded without content'
  - 'A measure that writes a label file or the sets root, or scores a commit against another commit''s lines. Verify: tests/acceptance/W2-134/ (W2-61h S8''s cases on a planted two-commit repository and a planted sets root hashed before and after): two measures on the two commits, one after the other, leave every label file and the sets root byte-identical and score each commit against its own lines'
  - 'A question copied from or paraphrasing lens B''s visible 20. Verify: test_w2_61h_visible_new.py''s test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one passes, and in the owner''s operator''s walled run test_w2_61h_hidden_form.py''s test_f2_no_hidden_question_repeats_a_visible_one passes (case, spacing and punctuation aside); a paraphrase is judged by the operator''s unmeasured cross-check of each new question against lens B''s 20, recorded as a count only, 0'
  - 'A gold source that does not hold its answer at its own commit [changed, DEC-1178 (1)]. Verify: as S4: the visible S4 and F3 cases, and in the owner''s operator''s walled run the hidden S4 case, pass; a block that moved or changed at HEAD is no failure (S4''s list); the hidden sources'' holding of their answers is judged by the operator''s cross-check, counts only'
  - 'A family hit counted on a member whose text does not hold the gold span''s text. Verify: tests/acceptance/W2-61h/test_w2_61h_families.py''s test_s7_f4_a_member_whose_text_does_not_hold_the_gold_is_no_hit (a word changed, half the span, the same lines with other text, each no hit and not named, beside a control family hit) passes'
profile: STANDARD
sources:
- DEC-828
- DEC-820
- DEC-845
- DEC-833
- DEC-873
- DEC-941
- DEC-954
- DEC-957
- DEC-950
- DEC-1052
- DEC-1055
- DEC-1068
- DEC-1069
- DEC-1070
- DEC-1074
- DEC-1078
- DEC-1079
- DEC-1083
- DEC-1084
- DEC-866
- DEC-1097
- DEC-1122
- DEC-1123
- DEC-1124
- DEC-1171
- DEC-1164
- DEC-1178
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-61h/
  author: independent-test-designer (MR-3); form only (count, fields, sources exist), never printing a question or an answer
track: A
list_rows: []
---
# W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources

**Re-scoped by DEC-954 Q9a; the size confirmed by DEC-957:** 48 questions with lens B's 20 (24 visible, 24 hidden); K9's "memory proven" is judged on the hidden half, at least 21 of 24 hit@5, against the owner's target of 95 %. Est. 12 to 14 lead-hours (MEMORY-SPEC-MAP B.2).

Companion to W2-61 (DEC-941). W2-61's engineer writes the measure and runs the visible half's baseline. The engineer is a measured role (`measures: roles: [engineer, research]` in the path map's `evaluation_sets.memory-retrieval`), so the hidden half is written here, by an independent auditor whose role is not measured, in a session the orchestrator starts, never a retrieval ticket's lead.

- **Why:** a measure tuned on its own questions overstates itself. The hidden half keeps W2-61's figures honest across the memory chain (DEC-828 item 3, DEC-820 (d)).
- **Form:** the auditor reads W2-61's script's input form once it is merged (`src/gov/retrieval/measure.py` and its README or docstring) and writes in that form. Before then, one YAML file per question with `question`, `gold_answer` and `sources` (path plus heading or line).
- **After it:** the orchestrator, which no set measures, runs W2-61's script on the hidden half and records the scores only (never the questions or answers) beside the visible baseline in `docs/research/W2-61-baseline.md`.
- **No path map change:** the hidden folder and its refusal are already in the path map (`evaluation_sets.memory-retrieval`, W2-58).

**DEC-1069 (owner, 2026-11-04 ~13:00):** the set grows to about 40 per half (DEC-1009 amended); **this ticket's category quotas are amended to fit R5** (each governing domain, the plan, tickets, the Contract, decisions and code, at least 10 % of each half; no subsystem above 25 %; at least 3 on failure and lesson memory, at least 2 on the kernel's skills or roles), as stated in `docs/research/memory-measure-audit/RUBRIC.md`'s R5 for a 40-question half; R11 (no answer that changes with ordinary work unless its gold is computed at the measured head) and R1.3 (test-harness code never governs a code fact, except for a question about the harness) apply. The hidden 16 new questions and the corrections of h03 and h08 are written by the owner's operator as the independent checker (ACT-HLABEL-2, ACT-HNEW-1), outside the guard; nothing about them reaches the CTO's session.

**DEC-1079 placed here (CTO, 2026-11-06):** S7, the source families, is DEC-1078 (4)'s rubric row built into the
measure's code, here because W2-61 (the measure's ticket) is closed and this ticket holds the measure's sets. Tests
first (an independent test designer from S7's text, on a planted repository and planted sets), then an engineer; the
CTO re-scores every kept run (`~/gov-os-eval/runs/`) once it lands, counts only.

**S7's interface (CTO, 2026-11-06, delegated P3, from the designer's choices):** (1) `evaluation_families:` is a
top-level key of the path map: a map of a family's name to the list of its member path globs; (2) kept outputs are
re-scored with `python3 -m gov.retrieval.measure <set> ... --kept <dir>`, where `<dir>` holds the kept ranked outputs
in call order (`00001.json` …, beside `.n` and `.n.lock`), and the output is the measure's own; (3) a family hit is
named in the question's line by the member's path and the word "family", the line keeping its present pattern.

**Role changed to engineer (CTO, 2026-11-06, delegated P3):** W2-61h's remaining work is S7's code; `gov launch`
starts an engineer only on an engineer's ticket, and a test designer launches on an engineer's ticket as before. The
guard so keeps S7's engineer from this ticket's own acceptance tests (DEC-1056).

**Role restored to independent-test-designer (CTO, 2026-11-06, the same day):** S2 requires this ticket's questions to
come from no measured role, and its acceptance case checks the ticket's role front matter; the engineer role broke it.
S7's code was built under this ticket's id while the role read engineer (`ab18f6f5`, launched 09:40); the role is
back, and the case passes again. Any later engineering on the measure goes under a ticket of its own.

**S8 placed here (CTO, 2026-11-06, DEC-1084):** the measure re-anchors in memory, never rewriting the sets root
(h23 was re-anchored on 11-05 at 14:40 to another clone's commit by `repin_gold.py` and so misjudged on the score-once
clone). Tests first, from S8's text, by an independent test designer. The code, by the note above, goes under an
engineer's ticket of its own, which the CTO asks the owner to file.

**Reopened 2026-11-14 (the owner, DEC-1178 (1), P-W2-61H-HEAD-1 Q1 (A), under DEC-1164 (18)):** a test revision of
the F3 check, hidden and visible cases alike. The walled run of 2026-11-14 ~12:05 gave 6 passed and 1 failed: h03's
cited lines changed at HEAD; six questions whose blocks moved unchanged had been re-anchored by hand before. The check
judged every question against HEAD, so ordinary work on cited files turned it red. Now: (1) each source is judged at
its own commit (the path a file there; the heading or lines a span there that holds the answer); (2) at HEAD, a block
that moved unchanged is no fault (W2-134's measure re-anchors it in memory); (3) a block whose lines changed is listed
by question id and entry number only, never failed; the list goes to the walled writer in the weekly cycle. S4 and F3
are reworded to match. The order: an independent test designer revises `test_w2_61h_hidden_form.py`,
`test_w2_61h_visible_new.py`, `w2_61h_support.py` and the README (`Rewrite-Reason: DEC-1178 (1)`), proving each
revised case on planted data (a moved block, a changed block, a source that never held its answer); a narrow
independent check of the revision (DEC-1154); then the owner's operator's walled re-run, expecting 7 passed with h03
on the list. The hidden half is never read by any launched session; its cases are proven on planted sets roots only.

**N2 (b), 2026-11-14 (the owner, DEC-1180 (1)):** the changed-lines list also holds a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head is listed too, though its heading is still found; an entry is listed once even when two of its alternatives changed (row N1, fixed in the same flow, DEC-1180 (4)). One more test revision by an independent test designer (`w2_61h_support.py`, the README, the case files only where needed; `Rewrite-Reason: DEC-1180 (1)`), proved on planted data, then a narrow independent check (`docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md`). W2-61h closes on this revision and the owner's operator's walled re-run. (The merge queue closed it at c1cb5285c with the F3 land; it stays open for this, status in_progress.)
