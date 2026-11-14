# Independent test designer: W2-61h (DAEO-h2k3) — the hidden count case revised to 39 (DEC-1171 (2))

You are a fresh independent test designer. Headless: only your last message is read.

## Where you work
- Your tree (write here only): /home/usain/gov-os-worktrees/W2-61h-c39-tests, branch w2/W2-61h-c39-tests.
- Files you may change: `tests/acceptance/W2-61h/w2_61h_support.py` and `tests/acceptance/W2-61h/README.md`. Nothing else.
- Scratch: /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/ ; use the sandbox's own `$TMPDIR`.

## The decision you implement
Read DEC-1171 (2) in `docs/DECISION_REGISTER.md` (grep `### DEC-1171`, read item (2) only): h10 is retired from W2-61h's
hidden half (the owner's operator moved it to `retired-hidden/` with its reason line), so the hidden half counts **39**
until a fresh question brings it back to 40. "W2-61h's count case is revised to 39 by a test designer under this item."

## What to change
1. `w2_61h_support.py` line 33: `HIDDEN_COUNT = 40` becomes 39, its comment saying why (DEC-1171 (2): h10 retired, 39 until
   the walled writer's replacement lands).
2. h10's category minimum and the twelve categories' sum follow the retirement: R5's minimums (`R5_QUOTAS`, line ~49,
   whose comment says the twelve sum to 40), less h10's one place, recorded **the same way as the operator's accepted
   shortfall** (`R5_SHORT`, line ~55: a named constant in the same form, with its decision cited), and the S3 case's
   floors honouring it. Keep the comment about the sum true.
3. `README.md`: the count lines (the S1 row's "**40** hidden `*.yaml`", the S3 row's "The hidden 40 alone ... save the
   owner's accepted shortfall ...", and any other line stating the hidden count) change to match, citing DEC-1171 (2).
4. No other case changes or loses its point. Keep every test function's name as it is (the ticket's KPI lines cite
   them, e.g. `test_s1_the_hidden_half_holds_40_question_files`, `test_s3_the_hidden_40_spread_as_r5_s_quotas_state`).
   Do not edit the test modules unless a message string must state the count; prefer the support file.

## h10's category: the one thing you may not have
h10's category is stated in the retirement's reason line on the owner's operator's record, inside the sets root. **You
never open `/home/usain/gov-os-eval` or any hidden or retired-hidden folder, and you read no hidden content.** The lead
searched the repository's public records (DEC-1171, `docs/research/memory-measure-audit/HIDDEN.md`, the EXP-003 measure
records, `docs/audit/memory-*-hidden.md`, the CTO's digest) and found no line naming h10's category. Search once more
yourself with Grep if you wish (public files only). If you cannot know h10's category:
- Still make changes 1 and 3's count lines (they hold whatever h10's category was), commit them, and
- return **status PACKAGES** with one package: the question (h10's R5 category, one word from the reason line, given by the
  owner's operator), options with cost, your recommendation, confidence, and what it blocks (change 2). Leave no
  placeholder or guess in the code; name in the README that change 2 waits on that word.
Never guess the category.

## Check your change
Run the visible side only (the hidden-form module skips without `GOV_EVAL_SETS_ROOT`; never set that variable):
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39-tests/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
(create the empty-home folder first). Every pytest through heavy_slot.sh. A resource gate's refusal is a wait, not a
refusal. To show your S1/S3 change works, you may plant a throwaway sets root of **synthetic** files under `$TMPDIR` (39
files with the accepted shortfall: green; 40 or 38: red) and run only `test_w2_61h_hidden_form.py` against it with
`GOV_EVAL_SETS_ROOT=<that throwaway root>` — never the real one. Report the counts only.

## Commit
Your paths only; trailers in one final paragraph:
```
git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests commit -m "<subject>" -m "Rewrite-Reason: DEC-1171 (2), h10 retired, 39 until the replacement" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1069, DEC-954, DEC-957" -- tests/acceptance/W2-61h/w2_61h_support.py tests/acceptance/W2-61h/README.md
```
(DEC-1171 is not in the ticket's `sources:`: name it in `discoveries`, never in `Implements:`.) Check with
`git log -1 --format=%B` that Task, Role and Implements read as trailers (`git log -1 --format='%(trailers)'`).

## Rules
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No hidden question, answer, category or gold path in any commit message, file, log or your return.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context` in the sandbox); search again once, in other words.

## Return (your last message; nothing else is read)
Twelve labelled lines, "none" where nothing: task / status (DONE or PACKAGES) / work_completed / files_changed /
evidence / tests (counts, and the throwaway-root counts if run) / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then `commits: <hash12> <subject>` and `guard_refusals: none | - <form> | <reason>`.
PACKAGES: each as question, options with cost, recommendation, confidence, what it blocks.

## The ticket's context packet (gov context DAEO-h2k3 --role independent-test-designer)

### Ticket text

```
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
kpis:
  success:
  - 'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner''s operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084]'
  - 'Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61''s engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2]'
  - 'The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40''s table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084]'
  - 'Every gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4]'
  - 'The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8]'
  - 'The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)]'
  - 'S7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract''s `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source''s family counts as a hit on that source when its text holds the gold span''s text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure''s per-question line; with no family declared, every score is as today; a run''s kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)]'
  - 'S8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source''s block again in the commit it measures (the block read at the source''s own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]'
  failure:
  - A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work.
  - 'A measure that writes a label file or the sets root, or scores a commit against another commit''s lines.'
  - A question copied from or paraphrasing lens B's visible 20.
  - A gold source that does not hold its answer.
  - 'A family hit counted on a member whose text does not hold the gold span''s text.'
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

```

### Mandatory inputs (packet hash 71bb6b781c8ad45ffc2f0746590cb473d681fe7465bf7d2c2917ca05085a5ec7)

```json
[
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
  "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
  "authority": "decision",
  "lifecycle": "ACCEPTED",
  "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
  "reason": "declared in sources",
  "tokens": 1881
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
  "sha256": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
  "authority": "decision",
  "lifecycle": "ACCEPTED",
  "constraint": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
  "reason": "declared in sources",
  "tokens": 900
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
  "id": "DAEO-m1u3",
  "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
  "authority": "task",
  "lifecycle": "closed",
  "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
  "reason": "declared in sources",
  "tokens": 763
 }
]
```
