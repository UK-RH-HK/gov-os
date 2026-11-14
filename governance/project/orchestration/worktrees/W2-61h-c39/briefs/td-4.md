# Independent test designer: W2-61h (DAEO-h2k3) — the S4/F3 check judged at each source's own commit (DEC-1178 (1))

You are a fresh independent test designer. Headless: only your last message is read.

## Where you work
- Your tree (write here only): /home/usain/gov-os-worktrees/W2-61h-c39-tests, branch w2/W2-61h-c39-tests (at w2/integrate e0381969c).
- Files you may change: `tests/acceptance/W2-61h/w2_61h_support.py`, `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py`,
  `tests/acceptance/W2-61h/test_w2_61h_visible_new.py`, `tests/acceptance/W2-61h/README.md`. Nothing else
  (not `test_w2_61h_families.py`, not `tests/optin-lifted*.txt`, not the question files).
- Scratch: the sandbox's own `$TMPDIR` for every planted repository and planted sets root.

## The decision you implement
DEC-1178 (1) (`docs/DECISION_REGISTER.md`, grep `### DEC-1178`, read item (1) only) and the ticket's reworded S4 and F3
lines (`.tickets/DAEO-h2k3.md` `kpis:`, the 4th success line and the 4th failure line; also its last paragraph,
"Reopened 2026-11-14"). The background: `governance/project/orchestration/packages/P-W2-61H-HEAD-1.md`.

**Why:** the owner's operator's walled run of 2026-11-14 gave 6 passed, 1 failed: one hidden question's cited lines
changed at HEAD; six others whose blocks moved unchanged had been re-anchored by hand before. `source_faults()`
(`w2_61h_support.py:204-246`) judges every line-cited block against **HEAD**, so ordinary work on a cited file turns the
check red. W2-134 (closed) now re-anchors in memory when the measure runs (`tests/acceptance/W2-134/README.md` states
the rule: the block read at the source's own commit, found once at the measured root).

## The revision (hidden and visible cases alike)
1. **Each gold source is judged at its own commit** (the source alternative's `commit`, else the question's `commit`):
   the path is a file there, and its heading or lines are a span there (the measure's span rule, `span_of`). For the
   visible q21-q24 the span at the own commit also holds the designer's anchor (`ANCHORS`); for the hidden half, that
   the span holds the answer is the operator's cross-check, not a test.
2. **At HEAD, a cited block that moved unchanged is no fault**: the own commit's block is found again at HEAD (at the
   same lines, or exactly once elsewhere, as W2-134's measure and `repin_gold.py` find it).
3. **A cited block whose lines changed at HEAD is listed by question id and entry number only.** Never failed; never
   blocks a close. The list is the case's output: file names (or ids) and entry numbers only, never a question, an
   answer, a path, a category or span text. Your call, stated in the README: what counts as "changed" (the block
   found nowhere at HEAD, found more than once, the path no longer a file at HEAD, a heading no longer found at HEAD;
   say which and why), and how the list is shown in a passing run so the owner's operator's record can quote it (a
   warning in the default summary, or printed with a flag named in the README's walled command; the list must be
   visible in the command's own output with no extra file written).
4. **A source that does not hold its answer at its own commit stays red** (path not a file there, span does not
   resolve there; for q21-q24 also the anchor missing from the span there), naming the file name and entry number only.

Everything else in both modules keeps its point and its failure wording rules (`_fail`, untraced, file names and
entry numbers only). **Keep every existing test function's name** (the ticket's KPI lines and
`governance/project/orchestration/packages/` cite them; `tests/optin-lifted-breadth.txt` holds
`rep: tests/acceptance/W2-61h/test_w2_61h_visible_new.py`, so in the full run **only the first row of a parametrised
function runs**). You may add functions; make each proof that must run in the full run a single non-parametrised
case (or put the row that matters first). The old message about "a re-anchor: repin_gold.py --write" goes: a moved
block is no longer a fault. The support functions that read git may take a `root` argument (default `REPO_ROOT`) so the
same rule runs on a planted repository.

## Prove it on planted data only
- **In the visible module, an always-run case** (no sets root, no hidden file) builds in `tmp_path` a planted git
  repository with two commits and a planted folder of question YAMLs (the "planted sets root") holding:
  (a) a source whose block moved unchanged at HEAD; (b) a source whose lines changed at HEAD; (c) a source that
  never held its answer at its own commit; (d) a control. Expected: (a) passes, not listed; (b) passes and is listed by
  id and entry number; (c) is red, naming file name and entry number only (assert the message holds no planted
  question, answer, path or span text); (d) passes, not listed. It must judge with the same support function the real
  hidden and visible cases use.
- **The hidden-form module against a throwaway sets root under `$TMPDIR`** (planted questions in the form the module
  expects, citing real commits and real non-evaluation files of this repository, e.g. a block of a visible question's
  source that moved or changed since; never anything from `/home/usain/gov-os-eval`): show its S4 case gives (a) pass,
  (b) pass with the list, (c) red with file name and entry number only, (d) pass. Other hidden cases may be red on a
  synthetic plant for reasons of their own (count, S5); report the S4 case's outcomes. Also show the module still skips
  without `GOV_EVAL_SETS_ROOT` and under `GOV_ROLE=engineer`.
- **The visible module at HEAD** (q21-q24 against the repository) must pass in an ordinary run.

## Check your change
Every pytest through heavy_slot.sh (a resource gate's refusal is a wait, not a refusal):
```
mkdir -p /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-61h-c39-tests && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39-tests/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
For the throwaway sets root run, add `GOV_EVAL_SETS_ROOT=<your $TMPDIR root>` and `-rA` (or your list's flag) and run
only `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py`. Report counts and outcomes only.

## README
Update the KPI map (S4 and F3 rows: the new rule, the list, where the list shows), the "How to run" walled command
(the form the owner's operator runs: `env -u GOV_ROLE -u GOV_TICKET GOV_EVAL_SETS_ROOT=<root> python3 -m pytest
tests/acceptance/W2-61h/test_w2_61h_hidden_form.py -p no:cacheprovider <flags>`), and add a dated section "DEC-1178 (1):
judged at each source's own commit" recording the planted proofs by outcome only. Correct any older sentence the
revision makes false (e.g. "the measure ... re-anchors nothing").

## Commit
Your paths only; trailers in one final paragraph (no blank line between them):
```
git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests commit -m "<subject>" --trailer "Rewrite-Reason: DEC-1178 (1)" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-828, DEC-820, DEC-1084, DEC-1178" -- tests/acceptance/W2-61h/w2_61h_support.py tests/acceptance/W2-61h/test_w2_61h_hidden_form.py tests/acceptance/W2-61h/test_w2_61h_visible_new.py tests/acceptance/W2-61h/README.md
```
Check with `git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests log -1 --format='%(trailers)'` that all four read as trailers.

## Rules
- **Never open `/home/usain/gov-os-eval` or any hidden, retired-hidden or memory-verdict folder; read no hidden content.**
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No hidden question, answer or gold path in any commit message, file, log or your return.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context` in the sandbox); search again once, in other words.
- You may read `src/gov/retrieval/measure.py` and `tests/acceptance/W2-134/` for the span and re-anchor rules.

## Return (your last message; nothing else is read)
Twelve labelled lines, "none" where nothing: task / status (DONE or PACKAGES) / work_completed / files_changed /
evidence / tests (the visible run's counts; the planted case's four outcomes; the throwaway-root S4 outcomes; the skip
checks) / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then
`commits: <hash12> <subject>` and `guard_refusals: none | - <form> | <reason>`.
PACKAGES: each as question, options with cost, recommendation, confidence, what it blocks.

## The ticket's context packet (gov context DAEO-h2k3 --role independent-test-designer --budget 36000)

```
{
  "ticket": "DAEO-h2k3",
  "ticket_text": "---\nid: DAEO-h2k3\nstatus: in_progress\ndeps: [DAEO-m1u3]\nlinks: []\ncreated: 2026-10-29T15:55:50Z\ntype: task\npriority: 1\nassignee: independent-test-designer\nexternal-ref: W2-61h\ntags: [wave-2, audit, evaluation, held-out, standard, keystone-4]\nwbs_id: W2-61h\ntitle: 'W2-61''s enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session'\nclass: audit\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\ndepends_on: [DAEO-m1u3]\nallowed_paths:\n- fixtures/evaluation/memory-retrieval/visible/q21.yaml\n- fixtures/evaluation/memory-retrieval/visible/q22.yaml\n- fixtures/evaluation/memory-retrieval/visible/q23.yaml\n- fixtures/evaluation/memory-retrieval/visible/q24.yaml\n- src/gov/retrieval/measure.py\n- tests/unit/retrieval/test_w2_61h_families*\n- tests/unit/retrieval/test_w2_61h_anchor*\n- governance/project/path-map.yaml\n- tests/acceptance/W2-61h/test_w2_61h_hidden_form.py\n- tests/acceptance/W2-61h/test_w2_61h_visible_new.py\n- tests/acceptance/W2-61h/w2_61h_support.py\n- tests/acceptance/W2-61h/README.md\nkpis:\n  success:\n  - 'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner''s operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084] [changed, DEC-1171 (2)] Verify: tests/acceptance/W2-61h/test_w2_61h_visible_new.py''s S1 cases (q21 to q24 exist in measure.py''s question form and are the recorded seeded stratified draw''s share by category, the README''s record) pass in an ordinary run, and the visible folder holds q01 to q40; test_w2_61h_hidden_form.py''s S1 cases (the hidden count, each file in the question form) are run only by the owner''s operator in a walled run with GOV_EVAL_SETS_ROOT set, whose record gives pass or fail and counts only: 39 hidden files while h10 sits in retired-hidden/ with its reason line, 40 once the walled writer''s replacement lands (DEC-1171 (2); the count case revised to 39 by a test designer under that item); no launched session reads a hidden file'\n  - 'Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61''s engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2] Verify: tests/acceptance/W2-61h/test_w2_61h_visible_new.py: test_s2_the_new_questions_and_these_tests_come_from_no_measured_role (every commit that writes q21 to q24 or these tests carries one Role, never one of the path map''s measures.roles) and test_s2_judges_the_role_on_a_planted_commit (red for a measured, other or missing role) pass, with the README''s record of the writer''s pruned commit c5c100729ce4 (Role: independent-test-designer); the hidden questions are refused to the retrieval roles by the measure and the guard, as S6 and F1 verify'\n  - 'The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40''s table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084] [changed, DEC-1171 (2)] Verify: the visible four''s draw-share case in test_w2_61h_visible_new.py passes; in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s3_the_hidden_40_spread_as_r5_s_quotas_state (R5''s table, the owner''s accepted shortfall of one in decision, callers and code-paraphrase and no other, no category outside the twelve, each multi-file question on two or more paths) passes, on the half as DEC-1171 (2) leaves it, pass or fail only; the parts no test judges (at least 2 whose naive answer is superseded; each governing domain at least 10 % of each half; no subsystem above 25 %) are judged by the operator''s unmeasured cross-check, recorded by counts only'\n  - 'Every gold source exists at its own commit and holds the answer there, cited by path and heading or line; at the head the auditor reads, a cited block that moved unchanged is no fault (the measure re-anchors it in memory, S8), and a cited block whose lines changed is listed by question id and entry number only, never failed and never blocking a close; the list goes to the walled writer in the weekly cycle (MEMORY-AUDIT''s G5 maintain pass, W2-187; the owner''s operator''s Monday slot until it lands) [DEC-828 item 4] [changed, DEC-1178 (1)] Verify: test_w2_61h_visible_new.py''s S4 and F3 cases, revised by a test designer under DEC-1178 (1), pass at the head the auditor reads: each new visible source resolves and holds its answer at its own commit; on planted data, a block moved unchanged at HEAD passes and a block whose lines changed is listed by question id and entry number and the case passes, while a source that does not hold its answer at its own commit is red; test_s4_no_new_visible_source_names_the_set_s_own_files passes; in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s S4 case judges the hidden sources the same way, its record giving pass or fail and the changed-lines list by file name and entry number only; that each hidden source holds its answer is judged by the operator''s unmeasured cross-check, recorded by counts only'\n  - 'The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8] Verify: in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root passes: the sets root lies outside every git worktree list path and in no git work tree, has mode 700, no worktree or run clone under ~/gov-os-runs holds fixtures/evaluation/memory-retrieval/hidden/*.yaml, and no hidden file''s bytes are an object of this repository''s store or a run clone''s; for the quoting rule, the same walled run matches each hidden question''s and answer''s text against every commit message on every ref, the returns and logs under .gov-runtime/ and the .tickets/ files, and records the count of matches only, 0'\n  - 'The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)] Verify: in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure passes (measure.py --sets-root <root> --part hidden, run as each measured role, exits 1 with a refusal and no output before any retriever is asked); a run of test_w2_61h_hidden_form.py against a throwaway sets root of planted faulty questions turns each case red for its fault with output holding no planted question, answer, category or gold path (file names and entry numbers only), and the whole module skips without GOV_EVAL_SETS_ROOT or under a measured GOV_ROLE'\n  - 'S7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract''s `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source''s family counts as a hit on that source when its text holds the gold span''s text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure''s per-question line; with no family declared, every score is as today; a run''s kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)] Verify: tests/acceptance/W2-61h/test_w2_61h_families.py''s 13 cases pass on planted data (a member holding the gold span''s normalised text is a hit named by its path and the word family; a member whose text does not hold it, or a file outside the family, is no hit even on the same lines or with the same bytes; with no family declared every score is today''s; --kept re-scores a run''s kept outputs with families, asking no retrieve, to a fresh run''s figures), with tests/unit/retrieval/test_w2_61h_families.py; governance/project/path-map.yaml at HEAD declares evaluation_families: with the contract, kernel and agents families as member glob lists'\n  - 'S8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source''s block again in the commit it measures (the block read at the source''s own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]'\n  failure:\n  - 'A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work. Verify: in the owner''s operator''s walled run, test_w2_61h_hidden_form.py''s test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root and test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure pass, and the hidden-form cases skip under a measured GOV_ROLE; a probe read by an engineer and by a research session of a non-existent file under the sets root''s hidden folder is refused by the guard, recorded without content'\n  - 'A measure that writes a label file or the sets root, or scores a commit against another commit''s lines. Verify: tests/acceptance/W2-134/ (W2-61h S8''s cases on a planted two-commit repository and a planted sets root hashed before and after): two measures on the two commits, one after the other, leave every label file and the sets root byte-identical and score each commit against its own lines'\n  - 'A question copied from or paraphrasing lens B''s visible 20. Verify: test_w2_61h_visible_new.py''s test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one passes, and in the owner''s operator''s walled run test_w2_61h_hidden_form.py''s test_f2_no_hidden_question_repeats_a_visible_one passes (case, spacing and punctuation aside); a paraphrase is judged by the operator''s unmeasured cross-check of each new question against lens B''s 20, recorded as a count only, 0'\n  - 'A gold source that does not hold its answer at its own commit [changed, DEC-1178 (1)]. Verify: as S4: the visible S4 and F3 cases, and in the owner''s operator''s walled run the hidden S4 case, pass; a block that moved or changed at HEAD is no failure (S4''s list); the hidden sources'' holding of their answers is judged by the operator''s cross-check, counts only'\n  - 'A family hit counted on a member whose text does not hold the gold span''s text. Verify: tests/acceptance/W2-61h/test_w2_61h_families.py''s test_s7_f4_a_member_whose_text_does_not_hold_the_gold_is_no_hit (a word changed, half the span, the same lines with other text, each no hit and not named, beside a control family hit) passes'\nprofile: STANDARD\nsources:\n- DEC-828\n- DEC-820\n- DEC-845\n- DEC-833\n- DEC-873\n- DEC-941\n- DEC-954\n- DEC-957\n- DEC-950\n- DEC-1052\n- DEC-1055\n- DEC-1068\n- DEC-1069\n- DEC-1070\n- DEC-1074\n- DEC-1078\n- DEC-1079\n- DEC-1083\n- DEC-1084\n- DEC-866\n- DEC-1097\n- DEC-1122\n- DEC-1123\n- DEC-1124\n- DEC-1171\n- DEC-1164\n- DEC-1178\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-61h/\n  author: independent-test-designer (MR-3); form only (count, fields, sources exist), never printing a question or an answer\ntrack: A\nlist_rows: []\n---\n# W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources\n\n**Re-scoped by DEC-954 Q9a; the size confirmed by DEC-957:** 48 questions with lens B's 20 (24 visible, 24 hidden); K9's \"memory proven\" is judged on the hidden half, at least 21 of 24 hit@5, against the owner's target of 95 %. Est. 12 to 14 lead-hours (MEMORY-SPEC-MAP B.2).\n\nCompanion to W2-61 (DEC-941). W2-61's engineer writes the measure and runs the visible half's baseline. The engineer is a measured role (`measures: roles: [engineer, research]` in the path map's `evaluation_sets.memory-retrieval`), so the hidden half is written here, by an independent auditor whose role is not measured, in a session the orchestrator starts, never a retrieval ticket's lead.\n\n- **Why:** a measure tuned on its own questions overstates itself. The hidden half keeps W2-61's figures honest across the memory chain (DEC-828 item 3, DEC-820 (d)).\n- **Form:** the auditor reads W2-61's script's input form once it is merged (`src/gov/retrieval/measure.py` and its README or docstring) and writes in that form. Before then, one YAML file per question with `question`, `gold_answer` and `sources` (path plus heading or line).\n- **After it:** the orchestrator, which no set measures, runs W2-61's script on the hidden half and records the scores only (never the questions or answers) beside the visible baseline in `docs/research/W2-61-baseline.md`.\n- **No path map change:** the hidden folder and its refusal are already in the path map (`evaluation_sets.memory-retrieval`, W2-58).\n\n**DEC-1069 (owner, 2026-11-04 ~13:00):** the set grows to about 40 per half (DEC-1009 amended); **this ticket's category quotas are amended to fit R5** (each governing domain, the plan, tickets, the Contract, decisions and code, at least 10 % of each half; no subsystem above 25 %; at least 3 on failure and lesson memory, at least 2 on the kernel's skills or roles), as stated in `docs/research/memory-measure-audit/RUBRIC.md`'s R5 for a 40-question half; R11 (no answer that changes with ordinary work unless its gold is computed at the measured head) and R1.3 (test-harness code never governs a code fact, except for a question about the harness) apply. The hidden 16 new questions and the corrections of h03 and h08 are written by the owner's operator as the independent checker (ACT-HLABEL-2, ACT-HNEW-1), outside the guard; nothing about them reaches the CTO's session.\n\n**DEC-1079 placed here (CTO, 2026-11-06):** S7, the source families, is DEC-1078 (4)'s rubric row built into the\nmeasure's code, here because W2-61 (the measure's ticket) is closed and this ticket holds the measure's sets. Tests\nfirst (an independent test designer from S7's text, on a planted repository and planted sets), then an engineer; the\nCTO re-scores every kept run (`~/gov-os-eval/runs/`) once it lands, counts only.\n\n**S7's interface (CTO, 2026-11-06, delegated P3, from the designer's choices):** (1) `evaluation_families:` is a\ntop-level key of the path map: a map of a family's name to the list of its member path globs; (2) kept outputs are\nre-scored with `python3 -m gov.retrieval.measure <set> ... --kept <dir>`, where `<dir>` holds the kept ranked outputs\nin call order (`00001.json` \u2026, beside `.n` and `.n.lock`), and the output is the measure's own; (3) a family hit is\nnamed in the question's line by the member's path and the word \"family\", the line keeping its present pattern.\n\n**Role changed to engineer (CTO, 2026-11-06, delegated P3):** W2-61h's remaining work is S7's code; `gov launch`\nstarts an engineer only on an engineer's ticket, and a test designer launches on an engineer's ticket as before. The\nguard so keeps S7's engineer from this ticket's own acceptance tests (DEC-1056).\n\n**Role restored to independent-test-designer (CTO, 2026-11-06, the same day):** S2 requires this ticket's questions to\ncome from no measured role, and its acceptance case checks the ticket's role front matter; the engineer role broke it.\nS7's code was built under this ticket's id while the role read engineer (`ab18f6f5`, launched 09:40); the role is\nback, and the case passes again. Any later engineering on the measure goes under a ticket of its own.\n\n**S8 placed here (CTO, 2026-11-06, DEC-1084):** the measure re-anchors in memory, never rewriting the sets root\n(h23 was re-anchored on 11-05 at 14:40 to another clone's commit by `repin_gold.py` and so misjudged on the score-once\nclone). Tests first, from S8's text, by an independent test designer. The code, by the note above, goes under an\nengineer's ticket of its own, which the CTO asks the owner to file.\n\n**Reopened 2026-11-14 (the owner, DEC-1178 (1), P-W2-61H-HEAD-1 Q1 (A), under DEC-1164 (18)):** a test revision of\nthe F3 check, hidden and visible cases alike. The walled run of 2026-11-14 ~12:05 gave 6 passed and 1 failed: h03's\ncited lines changed at HEAD; six questions whose blocks moved unchanged had been re-anchored by hand before. The check\njudged every question against HEAD, so ordinary work on cited files turned it red. Now: (1) each source is judged at\nits own commit (the path a file there; the heading or lines a span there that holds the answer); (2) at HEAD, a block\nthat moved unchanged is no fault (W2-134's measure re-anchors it in memory); (3) a block whose lines changed is listed\nby question id and entry number only, never failed; the list goes to the walled writer in the weekly cycle. S4 and F3\nare reworded to match. The order: an independent test designer revises `test_w2_61h_hidden_form.py`,\n`test_w2_61h_visible_new.py`, `w2_61h_support.py` and the README (`Rewrite-Reason: DEC-1178 (1)`), proving each\nrevised case on planted data (a moved block, a changed block, a source that never held its answer); a narrow\nindependent check of the revision (DEC-1154); then the owner's operator's walled re-run, expecting 7 passed with h03\non the list. The hidden half is never read by any launched session; its cases are proven on planted sets roots only.\n",
  "authority": [
    {
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    },
    {
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-873",
      "sha256": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "reason": "declared in sources",
      "tokens": 627
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-954",
      "sha256": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "reason": "declared in sources",
      "tokens": 1888
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-950",
      "sha256": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "reason": "declared in sources",
      "tokens": 571
    },
    {
      "id": "DEC-1052",
      "sha256": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "reason": "declared in sources",
      "tokens": 1880
    },
    {
      "id": "DEC-1055",
      "sha256": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "reason": "declared in sources",
      "tokens": 759
    },
    {
      "id": "DEC-1068",
      "sha256": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "reason": "declared in sources",
      "tokens": 983
    },
    {
      "id": "DEC-1069",
      "sha256": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "reason": "declared in sources",
      "tokens": 1134
    },
    {
      "id": "DEC-1070",
      "sha256": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "reason": "declared in sources",
      "tokens": 1245
    },
    {
      "id": "DEC-1074",
      "sha256": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "reason": "declared in sources",
      "tokens": 903
    },
    {
      "id": "DEC-1078",
      "sha256": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-1097",
      "sha256": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "reason": "declared in sources",
      "tokens": 1535
    },
    {
      "id": "DEC-1122",
      "sha256": "010a77f5f492ab94e1857bf07c34ebe64757f3e3f85e40888a8263ad638d3966",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "010a77f5f492ab94e1857bf07c34ebe64757f3e3f85e40888a8263ad638d3966",
      "reason": "declared in sources",
      "tokens": 417
    },
    {
      "id": "DEC-1123",
      "sha256": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "reason": "declared in sources",
      "tokens": 603
    },
    {
      "id": "DEC-1124",
      "sha256": "165d2b2a19db01d44acde8a1ab64c6fe329a61dfdb58ef9c67bf25f923822da2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "165d2b2a19db01d44acde8a1ab64c6fe329a61dfdb58ef9c67bf25f923822da2",
      "reason": "declared in sources",
      "tokens": 257
    },
    {
      "id": "DEC-1171",
      "sha256": "015d14db84c73c0ce5137f0acec8baedf45e1b1d8c6ad1c51aeb216cabc076e4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "015d14db84c73c0ce5137f0acec8baedf45e1b1d8c6ad1c51aeb216cabc076e4",
      "reason": "declared in sources",
      "tokens": 768
    },
    {
      "id": "DEC-1164",
      "sha256": "8d6b0fb6c83d56bc7a554d7c30fc97893cc1261e761cca1e07e5c130ab3026cf",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "8d6b0fb6c83d56bc7a554d7c30fc97893cc1261e761cca1e07e5c130ab3026cf",
      "reason": "declared in sources",
      "tokens": 4230
    },
    {
      "id": "DEC-1178",
      "sha256": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "reason": "declared in sources",
      "tokens": 1413
    },
    {
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "mandatory": [
    {
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    },
    {
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-873",
      "sha256": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "reason": "declared in sources",
      "tokens": 627
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-954",
      "sha256": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "reason": "declared in sources",
      "tokens": 1888
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-950",
      "sha256": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "reason": "declared in sources",
      "tokens": 571
    },
    {
      "id": "DEC-1052",
      "sha256": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "reason": "declared in sources",
      "tokens": 1880
    },
    {
      "id": "DEC-1055",
      "sha256": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "reason": "declared in sources",
      "tokens": 759
    },
    {
      "id": "DEC-1068",
      "sha256": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "reason": "declared in sources",
      "tokens": 983
    },
    {
      "id": "DEC-1069",
      "sha256": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "reason": "declared in sources",
      "tokens": 1134
    },
    {
      "id": "DEC-1070",
      "sha256": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "reason": "declared in sources",
      "tokens": 1245
    },
    {
      "id": "DEC-1074",
      "sha256": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "reason": "declared in sources",
      "tokens": 903
    },
    {
      "id": "DEC-1078",
      "sha256": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-1097",
      "sha256": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "reason": "declared in sources",
      "tokens": 1535
    },
    {
      "id": "DEC-1122",
      "sha256": "010a77f5f492ab94e1857bf07c34ebe64757f3e3f85e40888a8263ad638d3966",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "010a77f5f492ab94e1857bf07c34ebe64757f3e3f85e40888a8263ad638d3966",
      "reason": "declared in sources",
      "tokens": 417
    },
    {
      "id": "DEC-1123",
      "sha256": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "reason": "declared in sources",
      "tokens": 603
    },
    {
      "id": "DEC-1124",
      "sha256": "165d2b2a19db01d44acde8a1ab64c6fe329a61dfdb58ef9c67bf25f923822da2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "165d2b2a19db01d44acde8a1ab64c6fe329a61dfdb58ef9c67bf25f923822da2",
      "reason": "declared in sources",
      "tokens": 257
    },
    {
      "id": "DEC-1171",
      "sha256": "015d14db84c73c0ce5137f0acec8baedf45e1b1d8c6ad1c51aeb216cabc076e4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "015d14db84c73c0ce5137f0acec8baedf45e1b1d8c6ad1c51aeb216cabc076e4",
      "reason": "declared in sources",
      "tokens": 768
    },
    {
      "id": "DEC-1164",
      "sha256": "8d6b0fb6c83d56bc7a554d7c30fc97893cc1261e761cca1e07e5c130ab3026cf",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "8d6b0fb6c83d56bc7a554d7c30fc97893cc1261e761cca1e07e5c130ab3026cf",
      "reason": "declared in sources",
      "tokens": 4230
    },
    {
      "id": "DEC-1178",
      "sha256": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "reason": "declared in sources",
      "tokens": 1413
    },
    {
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "supplementary": [
    {
      "id": "e9f3138c8e10ad28c26531bc",
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "text": "- **W2-61** (rep): Success1: `test_w2_61_visible_half.py`; Success2: `test_w2_61_hidden_half_refused.py`; Success3: `test_w2_61_scores.py`; Success4: `test_w2_61_scores.py`; Success5: `test_w2_61_stacked.py`; Success6: `test_w2_61_any_set.py`; Success7: `test_w2_61_baseline.py`; Failure2: `test_w2_61_hidden_never_shown.py`; Failure4: `test_w2_61_governing_source.py`\n- **W2-61h** (rep): S1: `test_w2_61h_visible_new::test_s1_the_four_new_visible_questions_are_in_the_question_form`; S2: `test_w2_61h_visible_new::test_s2_the_new_questions_and_these_tests_come_from_no_measured_role`; S3: `test_w2_61h_hidden_form::test_s3_the_28_new_questions_spread_as_s3_states`; S4: `test_w2_61h_visible_new::test_s4_f3_every_new_visible_gold_source_resolves_at_head`; S5: `test_w2_61h_hidden_form::test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root`; S6: `test_w2_61h_hidden_form::test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure`; F1: (not placed); F2: `test_w2_61h_visible_new::test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one`; F3: (not placed)\n",
      "tokens": 272
    },
    {
      "id": "7fed2f9350a9e5325ff85821",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "Cases: 15 in the full run, 9 in `breadth`, 0 in `lifted` (S2's planted case added by the CTO's decision of 2026-11-03, P2: its engineer's row in the full run, its six others in `breadth`).\n\n| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |\n|---|---|---|\n| S1: Twenty-eight new questions about this repository's governance and code, each with its gold answer and the governing source or sources an answer... | `test_w2_61h_visible_new.py::test_s1_the_visible_four_are_the_stratified_draw_s_share`, `test_w2_61h_visible_new.py::test_s1_the_four_new_visible_questions_are_in_the_question_form`, `test_w2_61h_hidden_form.py::test_s1_the_hidden_half_holds_40_question_files` | the ticket's words |\n| S2: Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61's engineer, W2-64, W2... | `test_w2_61h_visible_new.py::test_s2_the_new_questions_and_these_tests_come_from_no_measured_role`, `test_w2_61h_visible_new.py::test_s2_judges_the_role_on_a_planted_commit` (1 of 7: the engineer's row) | the ticket's words (the planted case added by the CTO's decision of 2026-11-03, P2) |\n",
      "tokens": 297
    },
    {
      "id": "e27fe3f7a9fca543f110f294",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| F1: A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work. | `test_w2_61h_hidden_form.py::test_s1_the_hidden_half_holds_40_question_files`, `test_w2_61h_hidden_form.py::test_s1_every_hidden_question_is_in_the_question_form`, `test_w2_61h_hidden_form.py::test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure` | the ticket's words |\n| F2: A question copied from or paraphrasing lens B's visible 20. | `test_w2_61h_visible_new.py::test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one`, `test_w2_61h_hidden_form.py::test_f2_no_hidden_question_repeats_a_visible_one` | the ticket's words |\n| F3: A gold source that does not hold its answer. | `test_w2_61h_visible_new.py::test_f3_each_new_visible_gold_source_holds_its_answer`, `test_w2_61h_hidden_form.py::test_s4_f3_every_hidden_gold_source_resolves_at_head`, `test_w2_61h_visible_new.py::test_s4_f3_every_new_visible_gold_source_resolves_at_head` | the ticket's words |\n\n",
      "tokens": 252
    },
    {
      "id": "9094e37f2ce6c6dd6af5250e",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| S2 | V `test_s2_the_new_questions_and_these_tests_come_from_no_measured_role`, `test_s2_judges_the_role_on_a_planted_commit`; the record below | Every commit that writes q21-q24 or these tests has exactly one `Role`, `independent-test-designer`, `owner` or `orchestrator` (which landed the designer's draw, 6dca09f0), never one of the path map's `measures.roles`; the `Task` is not judged (the CTO's decision of 2026-11-03, P2: D-4's cut rewrote these tests under the coordination ticket's `Task: DAEO-sdxk`, DEC-1063); the ticket's role and assignee are not measured roles. On a planted repository the rule is red on an engineer's, research's, another role's or a role-less commit, whatever its `Task` |\n",
      "tokens": 177
    },
    {
      "id": "61ddd9d66a31f8cfe4bee3f0",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| F1 | H `test_s5_f1_...`; H `test_s6_...`; the measured-role skip | As S5 and S6: no route by a tree, a commit, a run clone or the measure; a measured session's own run of these tests reads nothing hidden |\n| F2 | V `test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one`; H `test_f2_no_hidden_question_repeats_a_visible_one` | No new question equals, case, spacing and punctuation aside, one of lens B's 20 or another of the set. A **paraphrase** is not judged by a test: it rests on the writer's independence (S2's record) and the brief it wrote to |\n| F3 | as S4 | A gold source that does not resolve, or whose cited lines changed since the question's commit, is red |\n\n**Not covered by a test, named:** S3's \"at least 2 whose naive answer is superseded\" (a fact of the hidden text\nthat only an unmeasured reader can judge); R5's items 2 to 5 beyond the category table (each governing domain at\nleast 10 %, no subsystem above 25 %, the kernel template's 2 roles or skills, the 3 failure records cited): each\n",
      "tokens": 259
    },
    {
      "id": "3b2b3955b7c7675fa0082913",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| S5: The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no ... | `test_w2_61h_hidden_form.py::test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root` | the ticket's words |\n| S6: The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by t... | `test_w2_61h_hidden_form.py::test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root`, `test_w2_61h_hidden_form.py::test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure` | the ticket's words |\n| F1: A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work. | `test_w2_61h_hidden_form.py::test_s1_the_hidden_half_holds_40_question_files`, `test_w2_61h_hidden_form.py::test_s1_every_hidden_question_is_in_the_question_form`, `test_w2_61h_hidden_form.py::test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure` | the ticket's words |\n",
      "tokens": 257
    },
    {
      "id": "0923ed0a62703c2277f4ef82",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| S4 | V `test_s4_f3_every_new_visible_gold_source_resolves_at_head`; V `test_f3_each_new_visible_gold_source_holds_its_answer`; V `test_s4_no_new_visible_source_names_the_set_s_own_files`; H `test_s4_f3_every_hidden_gold_source_resolves_at_head` | Each gold source is a file at HEAD outside `fixtures/evaluation/` and the set's report; its heading is found by the measure's rule, or its stated lines are a span of the file; **a source cited by lines alone (or by a heading no longer found) has the same lines at HEAD as at the question's `commit`** (the measure reads spans at the measured root, so lines that drifted no longer hold the answer). This is the measure's own span rule (`_span`, and `repin_gold.py`'s: a source's own `commit`, else the question's); the measure reads the stated lines as written and re-anchors nothing, so a block that **moved unchanged** to other lines is red too, reported apart as a re-anchor for `repin_gold.py --write` (which writes the DEC-1069 (6) reason line). For q21-q24 the designer also checks that each resolved span holds a string from its answer |\n",
      "tokens": 274
    },
    {
      "id": "912a01e1126c4384f1cceec4",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| S7 | `test_w2_61h_families.py::test_s7_normalised_text_still_matches` | Four cases, each a family hit at rank 1, named: `whitespace` (the same Markdown, wrapped, indented, two spaces and a tab), `markdown-prose-against-yaml-value` (prose with `**` emphasis against the quoted YAML value under its key), `yaml-value-against-markdown-prose` (a folded block value's lines against one line of prose with emphasis), `heading-level` (a `##` section against the generated page's `#` heading, body wrapped otherwise) |\n| S7, F4 | `test_w2_61h_families.py::test_s7_f4_a_member_whose_text_does_not_hold_the_gold_is_no_hit` | A member whose item does not hold the gold span's text is no hit (hit@5 no, no rank, full evidence 0 of 1) and is not named: `a-word-changed` (write to read), `half-the-span`, `same-lines-other-text` (the member's item on the gold span's own line numbers, other text: never by path alone). Each run carries a control question with a family hit, so the case is red until families are counted |\n",
      "tokens": 253
    },
    {
      "id": "c6782e747307ba1e5ab2abd6",
      "path": "tests/acceptance/W2-61h/test_w2_61h_families.py",
      "text": "def test_s7_f4_a_member_whose_text_does_not_hold_the_gold_is_no_hit(world, case):\n    member, (first, last) = NOT_HELD[case]\n    w = world\n    w.question(\"q01\", [G7], [[w.item(CAP7, 1, 3)]])                      # the control: a family hit\n    w.question(\"q02\", [G7], [[w.item(member, first, last)]])\n    doc, text = w.run()\n    q = by_id(doc)\n    assert figures(q[\"q01\"]) == (True, 1, True, True, 1, 1), \"the control: families are not counted at all\"\n    assert figures(q[\"q02\"]) == (False, None, False, False, 0, 1), f\"{case}: a family hit counted on a member \" \\\n                                                                   \"whose text does not hold the gold span's text\"\n    assert member not in line_of(text, \"q02\"), line_of(text, \"q02\")\n",
      "tokens": 188
    },
    {
      "id": "3f55d1d9e96f8a7d1606a822",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py",
      "text": "def test_s4_no_new_visible_source_names_the_set_s_own_files(name):\n    \"\"\"No gold source of a new question is the set's declared report or under ``fixtures/evaluation/`` (an item from\n    there is never a hit).\"\"\"\n    data = _new()[name]\n    declared = set(s.path_map_entry().get(\"visible\") or [])\n    bad = [a[\"path\"] for e in s.entries(data) or [] for a in e\n           if a[\"path\"].removeprefix(\"./\") in declared or a[\"path\"].removeprefix(\"./\").startswith(\"fixtures/evaluation/\")]\n    assert not bad, f\"{name}: {bad}\"\n",
      "tokens": 131
    },
    {
      "id": "0f9e0698cbff75ff5b5c2272",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| S5 | H `test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root` | The sets root is outside every `git worktree list` path and in no git work tree; its mode is 700 (no group or other bits); no worktree and no run clone under `~/gov-os-runs` has `fixtures/evaluation/memory-retrieval/hidden/*.yaml`; no hidden file's bytes are an object of this repository's store (every branch, stash and worktree shares it) or of a run clone's |\n| S6 | H `test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure`; the hidden module's design (skip, untraced, file names only) | The sets root's path map declares the set, covers the hidden folder and measures at least this tree's measured roles; `measure.py --sets-root <root> --part hidden`, run as each measured role, exits 1 with a refusal and no output, before any retriever is asked |\n| F1 | H `test_s5_f1_...`; H `test_s6_...`; the measured-role skip | As S5 and S6: no route by a tree, a commit, a run clone or the measure; a measured session's own run of these tests reads nothing hidden |\n",
      "tokens": 261
    }
  ],
  "supplementary_query": "W2-61's enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session\nTwenty-eight new questions about this repository's governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner's operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084] [changed, DEC-1171 (2)] Verify: tests/acceptance/W2-61h/test_w2_61h_visible_new.py's S1 cases (q21 to q24 exist in measure.py's question form and are the recorded seeded stratified draw's share by category, the README's record) pass in an ordinary run, and the visible folder holds q01 to q40; test_w2_61h_hidden_form.py's S1 cases (the hidden count, each file in the question form) are run only by the owner's operator in a walled run with GOV_EVAL_SETS_ROOT set, whose record gives pass or fail and counts only: 39 hidden files while h10 sits in retired-hidden/ with its reason line, 40 once the walled writer's replacement lands (DEC-1171 (2); the count case revised to 39 by a test designer under that item); no launched session reads a hidden file\nWritten by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61's engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2] Verify: tests/acceptance/W2-61h/test_w2_61h_visible_new.py: test_s2_the_new_questions_and_these_tests_come_from_no_measured_role (every commit that writes q21 to q24 or these tests carries one Role, never one of the path map's measures.roles) and test_s2_judges_the_role_on_a_planted_commit (red for a measured, other or missing role) pass, with the README's record of the writer's pruned commit c5c100729ce4 (Role: independent-test-designer); the hidden questions are refused to the retrieval roles by the measure and the guard, as S6 and F1 verify\nThe spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40's table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084] [changed, DEC-1171 (2)] Verify: the visible four's draw-share case in test_w2_61h_visible_new.py passes; in the owner's operator's walled run, test_w2_61h_hidden_form.py's test_s3_the_hidden_40_spread_as_r5_s_quotas_state (R5's table, the owner's accepted shortfall of one in decision, callers and code-paraphrase and no other, no category outside the twelve, each multi-file question on two or more paths) passes, on the half as DEC-1171 (2) leaves it, pass or fail only; the parts no test judges (at least 2 whose naive answer is superseded; each governing domain at least 10 % of each half; no subsystem above 25 %) are judged by the operator's unmeasured cross-check, recorded by counts only\nEvery gold source exists at its own commit and holds the answer there, cited by path and heading or line; at the head the auditor reads, a cited block that moved unchanged is no fault (the measure re-anchors it in memory, S8), and a cited block whose lines changed is listed by question id and entry number only, never failed and never blocking a close; the list goes to the walled writer in the weekly cycle (MEMORY-AUDIT's G5 maintain pass, W2-187; the owner's operator's Monday slot until it lands) [DEC-828 item 4] [changed, DEC-1178 (1)] Verify: test_w2_61h_visible_new.py's S4 and F3 cases, revised by a test designer under DEC-1178 (1), pass at the head the auditor reads: each new visible source resolves and holds its answer at its own commit; on planted data, a block moved unchanged at HEAD passes and a block whose lines changed is listed by question id and entry number and the case passes, while a source that does not hold its answer at its own commit is red; test_s4_no_new_visible_source_names_the_set_s_own_files passes; in the owner's operator's walled run, test_w2_61h_hidden_form.py's S4 case judges the hidden sources the same way, its record giving pass or fail and the changed-lines list by file name and entry number only; that each hidden source holds its answer is judged by the operator's unmeasured cross-check, recorded by counts only\nThe hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8] Verify: in the owner's operator's walled run, test_w2_61h_hidden_form.py's test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root passes: the sets root lies outside every git worktree list path and in no git work tree, has mode 700, no worktree or run clone under ~/gov-os-runs holds fixtures/evaluation/memory-retrieval/hidden/*.yaml, and no hidden file's bytes are an object of this repository's store or a run clone's; for the quoting rule, the same walled run matches each hidden question's and answer's text against every commit message on every ref, the returns and logs under .gov-runtime/ and the .tickets/ files, and records the count of matches only, 0\nThe hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)] Verify: in the owner's operator's walled run, test_w2_61h_hidden_form.py's test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure passes (measure.py --sets-root <root> --part hidden, run as each measured role, exits 1 with a refusal and no output before any retriever is asked); a run of test_w2_61h_hidden_form.py against a throwaway sets root of planted faulty questions turns each case red for its fault with output holding no planted question, answer, category or gold path (file names and entry numbers only), and the whole module skips without GOV_EVAL_SETS_ROOT or under a measured GOV_ROLE\nS7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract's `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source's family counts as a hit on that source when its text holds the gold span's text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure's per-question line; with no family declared, every score is as today; a run's kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)] Verify: tests/acceptance/W2-61h/test_w2_61h_families.py's 13 cases pass on planted data (a member holding the gold span's normalised text is a hit named by its path and the word family; a member whose text does not hold it, or a file outside the family, is no hit even on the same lines or with the same bytes; with no family declared every score is today's; --kept re-scores a run's kept outputs with families, asking no retrieve, to a fresh run's figures), with tests/unit/retrieval/test_w2_61h_families.py; governance/project/path-map.yaml at HEAD declares evaluation_families: with the contract, kernel and agents families as member glob lists\nS8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source's block again in the commit it measures (the block read at the source's own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]\nA hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work. Verify: in the owner's operator's walled run, test_w2_61h_hidden_form.py's test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root and test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure pass, and the hidden-form cases skip under a measured GOV_ROLE; a probe read by an engineer and by a research session of a non-existent file under the sets root's hidden folder is refused by the guard, recorded without content\nA measure that writes a label file or the sets root, or scores a commit against another commit's lines. Verify: tests/acceptance/W2-134/ (W2-61h S8's cases on a planted two-commit repository and a planted sets root hashed before and after): two measures on the two commits, one after the other, leave every label file and the sets root byte-identical and score each commit against its own lines\nA question copied from or paraphrasing lens B's visible 20. Verify: test_w2_61h_visible_new.py's test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one passes, and in the owner's operator's walled run test_w2_61h_hidden_form.py's test_f2_no_hidden_question_repeats_a_visible_one passes (case, spacing and punctuation aside); a paraphrase is judged by the operator's unmeasured cross-check of each new question against lens B's 20, recorded as a count only, 0\nA gold source that does not hold its answer at its own commit [changed, DEC-1178 (1)]. Verify: as S4: the visible S4 and F3 cases, and in the owner's operator's walled run the hidden S4 case, pass; a block that moved or changed at HEAD is no failure (S4's list); the hidden sources' holding of their answers is judged by the operator's cross-check, counts only\nA family hit counted on a member whose text does not hold the gold span's text. Verify: tests/acceptance/W2-61h/test_w2_61h_families.py's test_s7_f4_a_member_whose_text_does_not_hold_the_gold_is_no_hit (a word changed, half the span, the same lines with other text, each no hit and not named, beside a control family hit) passes",
  "further_batch": [
    {
      "id": "cb30c899557341d833a29067",
      "path": "tests/acceptance/W2-61h/README.md"
    },
    {
      "id": "08b17cf044ed8df1a0cb469b",
      "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-narrow-count-floor.md"
    },
    {
      "id": "fe462554c4007cfe9ffe3532",
      "path": "tests/acceptance/W2-61h/README.md"
    },
    {
      "id": "045f0268785178ddcf844c91",
      "path": "tests/acceptance/W2-61h/test_w2_61h_hidden_form.py"
    },
    {
      "id": "7f6829967a333e01383c2d25",
      "path": "tests/acceptance/W2-61h/test_w2_61h_hidden_form.py"
    },
    {
      "id": "0234d71726076751d8799869",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
    },
    {
      "id": "04d6231fc37f17ef61eadd81",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
    },
    {
      "id": "82ee35f6e1e162b656e794db",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
    },
    {
      "id": "a8c2845e657a956b4eae797e",
      "path": "tests/acceptance/W2-61h/test_w2_61h_hidden_form.py"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "e9f3138c8e10ad28c26531bc",
          "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md"
        },
        {
          "id": "7fed2f9350a9e5325ff85821",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "e27fe3f7a9fca543f110f294",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "9094e37f2ce6c6dd6af5250e",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "61ddd9d66a31f8cfe4bee3f0",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "3b2b3955b7c7675fa0082913",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "0923ed0a62703c2277f4ef82",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "912a01e1126c4384f1cceec4",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "c6782e747307ba1e5ab2abd6",
          "path": "tests/acceptance/W2-61h/test_w2_61h_families.py"
        },
        {
          "id": "3f55d1d9e96f8a7d1606a822",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "0f9e0698cbff75ff5b5c2272",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "cb30c899557341d833a29067",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "08b17cf044ed8df1a0cb469b",
          "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-narrow-count-floor.md"
        },
        {
          "id": "fe462554c4007cfe9ffe3532",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "045f0268785178ddcf844c91",
          "path": "tests/acceptance/W2-61h/test_w2_61h_hidden_form.py"
        },
        {
          "id": "7f6829967a333e01383c2d25",
          "path": "tests/acceptance/W2-61h/test_w2_61h_hidden_form.py"
        },
        {
          "id": "0234d71726076751d8799869",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "04d6231fc37f17ef61eadd81",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "82ee35f6e1e162b656e794db",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "a8c2845e657a956b4eae797e",
          "path": "tests/acceptance/W2-61h/test_w2_61h_hidden_form.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0234d71726076751d8799869",
      "reason": "budget exceeded"
    },
    {
      "id": "045f0268785178ddcf844c91",
      "reason": "budget exceeded"
    },
    {
      "id": "04d6231fc37f17ef61eadd81",
      "reason": "budget exceeded"
    },
    {
      "id": "08b17cf044ed8df1a0cb469b",
      "reason": "budget exceeded"
    },
    {
      "id": "7f6829967a333e01383c2d25",
      "reason": "budget exceeded"
    },
    {
      "id": "82ee35f6e1e162b656e794db",
      "reason": "budget exceeded"
    },
    {
      "id": "a8c2845e657a956b4eae797e",
      "reason": "budget exceeded"
    },
    {
      "id": "cb30c899557341d833a29067",
      "reason": "budget exceeded"
    },
    {
      "id": "fe462554c4007cfe9ffe3532",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-h2k3): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 35990,
  "budget": {
    "limit": 36000,
    "used": 35990
  },
  "hash": "eb3a746c92004103bfd1322c0b150dbb181e486228333640afda6530e56f3045"
}

```
