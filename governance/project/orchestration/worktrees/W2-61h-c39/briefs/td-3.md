# Independent test designer: W2-61h (DAEO-h2k3) — h10's retirement off the callers floor (DEC-1171 (2), the owner's (b))

You are a fresh independent test designer. Headless: only your last message is read.

## Where you work
- Your tree (write here only): /home/usain/gov-os-worktrees/W2-61h-c39-tests, branch w2/W2-61h-c39-tests.
- Files you may change: `tests/acceptance/W2-61h/w2_61h_support.py`, `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py`
  (only the S3 case's floor line and its docstring/message, if the floor must be computed there) and
  `tests/acceptance/W2-61h/README.md`. Nothing else.
- Scratch: /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/ ; use the sandbox's own `$TMPDIR`.

## The decision you implement
- DEC-1171 (2) in `docs/DECISION_REGISTER.md` (grep `### DEC-1171`, read item (2) only): h10 is retired from W2-61h's
  hidden half, so the half counts 39 (already done at `00a2f3e25`: `HIDDEN_COUNT = 39`).
- **The owner's answer (2026-11-13), option (b), to be recorded as DEC-1175 (not yet in the register; name it
  "DEC-1175 (to be recorded)" in comments):** h10's R5 category is **callers** (given by the owner's operator from h10's
  retirement reason line). The callers floor drops by one with the count. The CTO confirms the callers floor is **two
  short** of R5's stated minimum: one for the operator's earlier accepted shortfall (`R5_SHORT`, DEC-1069) and one for
  h10's retirement.

## What to change (three things; no other case changes)
1. In `tests/acceptance/W2-61h/w2_61h_support.py`, beside `R5_SHORT` (line ~57), add
   `R5_RETIRED = {"callers": 1}` with a comment naming DEC-1171 (2) and the owner's (b) (DEC-1175, to be recorded).
2. Make S3's floors honour it: in `test_s3_the_hidden_40_spread_as_r5_s_quotas_state` (`test_w2_61h_hidden_form.py`
   line ~113) the floor for each category is `R5_QUOTAS[name] - R5_SHORT.get(name, 0) - R5_RETIRED.get(name, 0)`, so
   callers' floor is 2 (4 less 2), decision's 5 and code-paraphrase's 2 as before, and every other category at its full
   minimum. The failure message should still show counts per category only, and say which floors carry a reduction.
   Keep the test function's name as it is (the ticket's KPI lines cite it).
3. Keep the comments about the twelve categories' sum true: R5's twelve minimums sum to 40; less h10's retired place
   the half's minimums sum to 39 (matching `HIDDEN_COUNT`). Say so where the sum is stated.
4. README.md: the S3 row and the "DEC-1171 (2)" section (lines ~33 and ~72-77) still say change 2 "waits" on h10's
   category; make them state the change as made (`R5_RETIRED = {"callers": 1}`, callers' floor two short: the accepted
   shortfall and h10's retirement), citing DEC-1171 (2) and the owner's (b) (DEC-1175, to be recorded). Name no hidden
   question, answer or gold path; the category word "callers" is given by the owner and may be written.

No other case changes or loses its point. Do not touch the visible cases.

## Check your change
Run the visible side (the hidden-form module skips without `GOV_EVAL_SETS_ROOT`; never set it to anything real):
```
mkdir -p /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-61h-c39-tests && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39-tests/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Every pytest through heavy_slot.sh. A resource gate's refusal is a wait, not a refusal.
Then show the S3 change works on a throwaway sets root of **synthetic** files under `$TMPDIR` only (never
`/home/usain/gov-os-eval`): plant 39 files that pass every other hidden case's form (copy the shape the module expects;
earlier designers did this, see README's record), with callers at 2 and decision 5 and code-paraphrase 2 → S3 green;
callers at 1 → S3 red; decision at 4 → S3 red. Run only `test_w2_61h_hidden_form.py` against it with
`GOV_EVAL_SETS_ROOT=<that throwaway root>` (other hidden cases may be red on a synthetic plant for reasons of their own,
e.g. S4/S5; report S3's result and the counts). Report counts only.

## Commit
Your paths only; trailers in one final paragraph (no blank line between them):
```
git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests commit -m "<subject>" -m "Rewrite-Reason: DEC-1171 (2), h10 retired (callers), the owner's (b)" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1069, DEC-954, DEC-957" -- tests/acceptance/W2-61h/w2_61h_support.py tests/acceptance/W2-61h/test_w2_61h_hidden_form.py tests/acceptance/W2-61h/README.md
```
(DEC-1171 and DEC-1175 are not in the ticket's `sources:`: name them in `discoveries`, never in `Implements:`.) Check with
`git log -1 --format='%(trailers)'` that Task, Role, Implements and Rewrite-Reason read as trailers. If
`Rewrite-Reason` does not read as a trailer as a separate `-m`, pass it as `--trailer "Rewrite-Reason: ..."` instead.

## Rules
- **Never open `/home/usain/gov-os-eval` or any hidden or retired-hidden folder; read no hidden content.**
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No hidden question, answer or gold path in any commit message, file, log or your return.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context` in the sandbox); search again once, in other words.

## Return (your last message; nothing else is read)
Twelve labelled lines, "none" where nothing: task / status (DONE or PACKAGES) / work_completed / files_changed /
evidence / tests (counts, and the throwaway-root counts) / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then `commits: <hash12> <subject>` and `guard_refusals: none | - <form> | <reason>`.
PACKAGES: each as question, options with cost, recommendation, confidence, what it blocks.

## The ticket's context packet (gov context DAEO-h2k3 --role independent-test-designer --budget 30000)

```json
{
  "ticket": "DAEO-h2k3",
  "ticket_text": "---\nid: DAEO-h2k3\nstatus: in_progress\ndeps: [DAEO-m1u3]\nlinks: []\ncreated: 2026-10-29T15:55:50Z\ntype: task\npriority: 1\nassignee: independent-test-designer\nexternal-ref: W2-61h\ntags: [wave-2, audit, evaluation, held-out, standard, keystone-4]\nwbs_id: W2-61h\ntitle: 'W2-61''s enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session'\nclass: audit\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\ndepends_on: [DAEO-m1u3]\nallowed_paths:\n- fixtures/evaluation/memory-retrieval/visible/q21.yaml\n- fixtures/evaluation/memory-retrieval/visible/q22.yaml\n- fixtures/evaluation/memory-retrieval/visible/q23.yaml\n- fixtures/evaluation/memory-retrieval/visible/q24.yaml\n- src/gov/retrieval/measure.py\n- tests/unit/retrieval/test_w2_61h_families*\n- tests/unit/retrieval/test_w2_61h_anchor*\n- governance/project/path-map.yaml\nkpis:\n  success:\n  - 'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner''s operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084]'\n  - 'Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61''s engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2]'\n  - 'The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40''s table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084]'\n  - 'Every gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4]'\n  - 'The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8]'\n  - 'The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)]'\n  - 'S7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract''s `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source''s family counts as a hit on that source when its text holds the gold span''s text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure''s per-question line; with no family declared, every score is as today; a run''s kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)]'\n  - 'S8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source''s block again in the commit it measures (the block read at the source''s own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]'\n  failure:\n  - A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work.\n  - 'A measure that writes a label file or the sets root, or scores a commit against another commit''s lines.'\n  - A question copied from or paraphrasing lens B's visible 20.\n  - A gold source that does not hold its answer.\n  - 'A family hit counted on a member whose text does not hold the gold span''s text.'\nprofile: STANDARD\nsources:\n- DEC-828\n- DEC-820\n- DEC-845\n- DEC-833\n- DEC-873\n- DEC-941\n- DEC-954\n- DEC-957\n- DEC-950\n- DEC-1052\n- DEC-1055\n- DEC-1068\n- DEC-1069\n- DEC-1070\n- DEC-1074\n- DEC-1078\n- DEC-1079\n- DEC-1083\n- DEC-1084\n- DEC-866\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-61h/\n  author: independent-test-designer (MR-3); form only (count, fields, sources exist), never printing a question or an answer\ntrack: A\nlist_rows: []\n---\n# W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources\n\n**Re-scoped by DEC-954 Q9a; the size confirmed by DEC-957:** 48 questions with lens B's 20 (24 visible, 24 hidden); K9's \"memory proven\" is judged on the hidden half, at least 21 of 24 hit@5, against the owner's target of 95 %. Est. 12 to 14 lead-hours (MEMORY-SPEC-MAP B.2).\n\nCompanion to W2-61 (DEC-941). W2-61's engineer writes the measure and runs the visible half's baseline. The engineer is a measured role (`measures: roles: [engineer, research]` in the path map's `evaluation_sets.memory-retrieval`), so the hidden half is written here, by an independent auditor whose role is not measured, in a session the orchestrator starts, never a retrieval ticket's lead.\n\n- **Why:** a measure tuned on its own questions overstates itself. The hidden half keeps W2-61's figures honest across the memory chain (DEC-828 item 3, DEC-820 (d)).\n- **Form:** the auditor reads W2-61's script's input form once it is merged (`src/gov/retrieval/measure.py` and its README or docstring) and writes in that form. Before then, one YAML file per question with `question`, `gold_answer` and `sources` (path plus heading or line).\n- **After it:** the orchestrator, which no set measures, runs W2-61's script on the hidden half and records the scores only (never the questions or answers) beside the visible baseline in `docs/research/W2-61-baseline.md`.\n- **No path map change:** the hidden folder and its refusal are already in the path map (`evaluation_sets.memory-retrieval`, W2-58).\n\n**DEC-1069 (owner, 2026-11-04 ~13:00):** the set grows to about 40 per half (DEC-1009 amended); **this ticket's category quotas are amended to fit R5** (each governing domain, the plan, tickets, the Contract, decisions and code, at least 10 % of each half; no subsystem above 25 %; at least 3 on failure and lesson memory, at least 2 on the kernel's skills or roles), as stated in `docs/research/memory-measure-audit/RUBRIC.md`'s R5 for a 40-question half; R11 (no answer that changes with ordinary work unless its gold is computed at the measured head) and R1.3 (test-harness code never governs a code fact, except for a question about the harness) apply. The hidden 16 new questions and the corrections of h03 and h08 are written by the owner's operator as the independent checker (ACT-HLABEL-2, ACT-HNEW-1), outside the guard; nothing about them reaches the CTO's session.\n\n**DEC-1079 placed here (CTO, 2026-11-06):** S7, the source families, is DEC-1078 (4)'s rubric row built into the\nmeasure's code, here because W2-61 (the measure's ticket) is closed and this ticket holds the measure's sets. Tests\nfirst (an independent test designer from S7's text, on a planted repository and planted sets), then an engineer; the\nCTO re-scores every kept run (`~/gov-os-eval/runs/`) once it lands, counts only.\n\n**S7's interface (CTO, 2026-11-06, delegated P3, from the designer's choices):** (1) `evaluation_families:` is a\ntop-level key of the path map: a map of a family's name to the list of its member path globs; (2) kept outputs are\nre-scored with `python3 -m gov.retrieval.measure <set> ... --kept <dir>`, where `<dir>` holds the kept ranked outputs\nin call order (`00001.json` \u2026, beside `.n` and `.n.lock`), and the output is the measure's own; (3) a family hit is\nnamed in the question's line by the member's path and the word \"family\", the line keeping its present pattern.\n\n**Role changed to engineer (CTO, 2026-11-06, delegated P3):** W2-61h's remaining work is S7's code; `gov launch`\nstarts an engineer only on an engineer's ticket, and a test designer launches on an engineer's ticket as before. The\nguard so keeps S7's engineer from this ticket's own acceptance tests (DEC-1056).\n\n**Role restored to independent-test-designer (CTO, 2026-11-06, the same day):** S2 requires this ticket's questions to\ncome from no measured role, and its acceptance case checks the ticket's role front matter; the engineer role broke it.\nS7's code was built under this ticket's id while the role read engineer (`ab18f6f5`, launched 09:40); the role is\nback, and the case passes again. Any later engineering on the measure goes under a ticket of its own.\n\n**S8 placed here (CTO, 2026-11-06, DEC-1084):** the measure re-anchors in memory, never rewriting the sets root\n(h23 was re-anchored on 11-05 at 14:40 to another clone's commit by `repin_gold.py` and so misjudged on the score-once\nclone). Tests first, from S8's text, by an independent test designer. The code, by the note above, goes under an\nengineer's ticket of its own, which the CTO asks the owner to file.\n",
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
  ],
  "supplementary": [],
  "supplementary_query": "W2-61's enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session\nTwenty-eight new questions about this repository's governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner's operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084]\nWritten by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61's engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2]\nThe spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40's table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084]\nEvery gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4]\nThe hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8]\nThe hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)]\nS7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract's `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source's family counts as a hit on that source when its text holds the gold span's text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure's per-question line; with no family declared, every score is as today; a run's kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)]\nS8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source's block again in the commit it measures (the block read at the source's own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]\nA hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work.\nA measure that writes a label file or the sets root, or scores a commit against another commit's lines.\nA question copied from or paraphrasing lens B's visible 20.\nA gold source that does not hold its answer.\nA family hit counted on a member whose text does not hold the gold span's text.",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 21995,
  "budget": {
    "limit": 30000,
    "used": 21995
  },
  "hash": "1d67d067963d45dee715356fe7f9cf9d6ad6b2cfd300daeba281058527319fa3"
}

```
