# Lead brief: bundle-b-skill, the adopt skill back under its token limit on batch B (a fix under W2-212, DAEO-d3sr; W2-188's pins re-made)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Every `gov retrieve` you or a helper runs takes
`--root /home/usain/gov-os-worktrees/W2-00-store`.

## Why
`e2/bundle-b` (head `72ee89d0f`, worktree `/home/usain/gov-os-worktrees/E2-bundle-b`) merges W2-207's runtime, eval-roots and kit-head
onto batch A. After the merges the adopt skill is 2553 tokens against its limit of 2500, so four cases are red (W2-188, W2-88a, W1-36,
W1-26; they pass on `e2/bundle-a`). The bundle-b lead's return is `.gov-runtime/scratch/orchestrator/log/leads/bundle-b.json`.

## What (a `## Fix:` line in `.tickets/DAEO-d3sr.md`; the CTO approves it, and the skill's change, by this brief, EMERGENCY-2 §3.5)
- **BS-1** First merge `e2/bundle-a`'s head into `e2/bundle-b` (it has three record-only commits since; it merges clean). Then cut the
  adopt skill (`template/governance/kernel/skills/adopt/SKILL.md` and its copies, as batch A's lead did in `c17e20484`; find all four)
  to at most 2450 tokens by the tests' own count, keeping every rule it states: wording only, no rule dropped, D3's stale-class
  paragraph and kit-head's guide pointer both kept. The engineer helper makes the cut; name each sentence you shortened in the return.
- **BS-2** The independent test designer re-makes W2-188's pins on the skill's bytes and hunks to the cut text (as `2f2d77b83` did on
  batch A), with a `Rewrite-Reason` trailer citing this brief; nothing else in `tests/acceptance/` changes.

## Where
Work on branch `e2/bundle-b` in its worktree (the CTO's batch branch; commits with `Task: DAEO-d3sr`, `Fix:`, `Role:`). Code area: the
adopt skill and its copies; `tests/acceptance/W2-188/` (the test designer only); the ticket. Never merge into `w2/integrate`.

## Green
The four cases green; `gov accept W2-212` and `gov accept W2-188` green; then the folders the four cases live in plus W2-207, W2-204 and
W2-208, through the heavy slot. Check the trailers (LEAD-COMMON) and that no merge you make resolves anything under `tests/acceptance/`.

## Return
Head of `e2/bundle-b`; the skill's token count before and after; each sentence shortened; the runs' summaries; your retrieves (count,
queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: a455b00cf073 (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "a455b00cf0736d7a37d9e585e6430c455ef4fe60",
    "head": "a455b00cf0736d7a37d9e585e6430c455ef4fe60",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-zlog",
      "sha256": "b56a69a8bc584f4bf9a4b6e1fbec067a1580cfacd453de9f95e8597217a83c66",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 81,
      "end_line": 94,
      "text": "## Interface (the CTO at claim, DEC-1179 (8), DEC-1157 (3) and (12); listed for the owner's reading)\n\n- **I1, the skill's three copies and the four places (S1, S2, S4, F1).** `template/governance/kernel/skills/adopt/SKILL.md`\n  is edited. `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md` are then byte copies of it,\n  all three at base sha256 `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0`, 74 lines. Exactly four\n  places change:\n  - **Line 4:** `version: \"1.0.0\"` becomes `version: \"1.1.0\"` (W2-88a is closed and the kernel copy still reads 1.0.0\n    at `10c0ca52b`). If the version line reads anything other than 1.0.0 at claim, use the next minor after it (S4).\n  - **Line 58, step 6:** replaced in place by one numbered line, `6. Declare ...`.\n  - **A new paragraph** after line 59 (step 7), with one blank line before it, before line 61's\n    `## Verify clauses for adopted tickets`.\n  - **Line 74, the sources line:** adds DEC-1101, DEC-1125 and DEC-1179 in numeric order.\n\n  `git diff <base> -- template/governance/kernel/skills/adopt/SKILL.md` shows those four hunks and no other.\n",
      "chunk_id": "7f896a47f7335705d9a5f8f8",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-zlog",
      "sha256": "5acdb1e77504f0fd2488a201f2315d88d544f3178350d6c379b11720108bb926",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 43,
      "end_line": 43,
      "text": "  - 'S4 The three copies of the skill are byte-equal; the version goes from \"1.0.0\" to \"1.1.0\" in all three (the next minor if W2-88a''s promotion has taken 1.1.0 by then); nothing else in the skill changes but step 6, the new paragraph, the governing sources line (adding DEC-1101, DEC-1125 and DEC-1179) and the version [CAP-33, DEC-832 item 2, DEC-981] Verify: sha256 of the three copies equal; `git diff` of the kernel copy against the base touches only those four places; `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0'\n",
      "chunk_id": "3d15af55abfc9d9984470ab0",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "W2-188-CIT-P",
      "sha256": "630df736a6d3183cba56a707260351470e43bfef6c7eff006029d5ca34c5e31e",
      "path": "docs/changes/W2-188-CIT-P.md",
      "start_line": 149,
      "end_line": 160,
      "text": "## 5. Impact\n\n| Area | Impact |\n|---|---|\n| Kernel skills | One skill: one step re-worded, one paragraph added, the sources line and the version. No other skill, role file, hook or guard rule changes |\n| Generated copies | `.rulesync/skills/adopt/` and `template/.rulesync/skills/adopt/` byte-equal to the kernel copy. `.claude/skills/adopt/SKILL.md` (front matter without a version) comes from the copies ACT after the owner's approval; this ticket does not write it, so until then its body differs. The adapter-portability check (`python3 -m gov.adapters.portability`, a G1 hard-block check that `gov check`'s structural pass runs when a diff touches the kernel skills or `.rulesync/`) reports one finding, `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md` (\"is not what rulesync generates from its sources\"), from the merge of these bytes until the copies ACT regenerates that copy. Run on `b75472d48` it gives exactly that one finding (`compared`: `rulesync_version` true, 78 kernel files, 93 generated files; exit 1). So the copies ACT should ride in the same landing as this merge |\n| W2-11's cases | W2-11's body and version cases do not cover `adopt` and so stay as they are after the merge. The body case `test_every_copy_carries_the_kernel_skills_body` (`tests/acceptance/W2-11/test_w2_11_skills.py`) is parametrized over `test-design`, `orchestration`, `audit` and `qa-review` only (line 124), so there is no `[adopt]` case; the version case and its round-2 twin (`test_w2_11_round2.py`) exclude `adopt` too, so the bump does not touch them. W2-11 therefore stays green after the merge (`tests/acceptance/W2-11` and `tests/acceptance/W2-88a`: 276 passed, 1 skipped on `599fa2a22`), and the `.claude/skills/adopt/SKILL.md` copy's drift from the kernel body, from the merge until the copies ACT regenerates it, is caught by no W2-11 case (the adapter-portability check reports it, see \"Generated copies\") |\n| W2-88a's cases | Step 6's matcher (`tests/acceptance/W2-88a/w2_88a_support.py`: \"declar...\", \"measur...\", \"verdict set\", \"once\") passes on the new text, the seven steps in order: `check_steps` was run on A9's region of each of the three copies and on the practice record's \u00a76, and `check_pointer` on A9's region, all with no problem (`docs/probes/DAEO-zlog/checks.md`). The COPIES case diffs the base against the current kernel copy, so it passes while the three copies are byte-equal. The CIT-P cases read W2-88a's own record and fixed commits; unchanged. No W2-88a test is revised |\n| Skill check | `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0 on the new text |\n| W2-188's own acceptance | `tests/acceptance/W2-188/`, written by an independent test designer from the KPI lines |\n| Decisions | None changed by this record; it carries DEC-1179, which changes DEC-1101 (1), DEC-1125 (2), DEC-1098 (1), DEC-1126 (5), DEC-1074 (1) as the practice reads it, and DEC-1097 (1)(d) (a 95 % bar added beside it) |\n\n",
      "chunk_id": "a656de156a09db4d45758dc9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-ma4q",
      "sha256": "0ea784e30a2d9541798a0660296101f3865ed99a7924519e2339a62083a658fe",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 149,
      "end_line": 157,
      "text": "## What the evidence record holds (`docs/changes/W2-204-evidence.md`)\n\n- the diff of the generated Gov OS briefs against the approved `writer.md` and `checker.md` (the `by_area` change is expected);\n- EXAMIN's `memory-audit.yaml` as written from its proposal (domains decisions, tasks, specs, reports, code; features F00 to F06\n  by record key; the categories for 40; `control: none` or `baseline: first`; `exclude` its archive, wave 0 audits,\n  `.gov-runtime` and `product/data`);\n- the exact commands EXAMIN's CTO runs after `gov update`, from the briefs to the judged figure;\n- what W2-188's adopt skill step 6 and the practice record should now say (for the CTO).\n\n",
      "chunk_id": "15628aa8e61996932c88a484",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-ma4q",
      "sha256": "4d7ac7c8c20f0e5c231ba0dd76637c8bdd208620dbac0b64f91ab762557e160d",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 65,
      "end_line": 74,
      "text": "# W2-204 The memory measure runs on any adopted repository, by product commands\n\nEXAMIN's CTO found (its F-032, 2026-11-19 01:45) that `python3 -m gov.memaudit` holds Gov OS's own repository as\nconstants (`tables.py` DOMAINS, SUBSYSTEMS, QUOTAS; `measure.py` the control set and its fixed figure 34), so no adopted\nrepository can go from a question set to a judged figure; EMERGENCY-2 \u00a78.2 item 3 needs EXAMIN's copy at 95 % or better\nend to end on a fresh 80, measured as Gov OS's is. Gov OS's own first fresh 80 stopped on the same module\n(JOB-20261116-15; P-FRESH-80-1 \u00a76 F-1 and F-2). W2-187 (the weekly audit) and W2-188 (the adopt skill's step 6) are\nreopened by EMERGENCY-2 \u00a76.1; the fixes to W2-187's driver are recorded in `.tickets/DAEO-0cd2.md`, the new feature is\nthis ticket (EMERGENCY-2 4.6).\n\n",
      "chunk_id": "2f65a75befedb9dbace52acf",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-pg6i",
      "sha256": "9afac644c3c3104881b055f9c05fec431abc1421ea4d9ec52a066cbc38c8d6fb",
      "path": ".tickets/DAEO-pg6i.md",
      "start_line": 51,
      "end_line": 53,
      "text": "# W2-88a The adopt skill's kernel text (a child of W2-88)\n\nFiled by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the kernel skill text: W2-88's S17 (moved word for word) and W2-174's skill line (its S5, moved word for word, so the adopt skill is written once under one CIT-P). The two `test_w2_174_skill.py` and S17 string tests named in the moved lines are this ticket's acceptance tests, written by its test designer under `tests/acceptance/W2-88a/`. It can start now; the owner approves the skill's bytes before the merge (CAP-33).\n",
      "chunk_id": "db1289689cd3bf258bd8760b",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-pg6i",
      "sha256": "bc6f9a969715846a70563c5950b5989d66ee16bcd90a3a52d7ae4ea85bc5e899",
      "path": ".tickets/DAEO-pg6i.md",
      "start_line": 25,
      "end_line": 50,
      "text": "# .claude/skills/adopt/SKILL.md out of the paths: generated from the kernel skill by the copies ACT after the owner's approval (DEC-315)\n- docs/changes/W2-88a-CIT-P.md\n- docs/research/W2-88-memory-practice.md  # the practice record the skill points to, refreshed to S17's order (from W2-88)\nest_loc: 80\nreads:\n- .tickets/DAEO-2bdu.md\n- .tickets/DAEO-zmo4.md\n- docs/research/W2-88-memory-practice.md\n- template/governance/kernel/skills/\nneeds: []\nkpis:\n  success:\n  - 'S17 The Wave 0 order in the adopt skill: A9''s step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - line: \"The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083]\"\n    verify: \"tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section\"\n  - 'The CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill''s sha256 before and after, the lines added or removed, the independent review and the owner''s approval of the bytes before the merge; the two .rulesync copies equal the kernel copy in the changed sections Verify: the record holds both hashes and the review''s verdict; a diff of the three files shows the same changed sections [CAP-33, DEC-1116]'\n  failure: []\nnon_goals:\n- the adopt code (W2-88, W2-174) and the proofs (W2-88b); the .claude/ copy (the copies ACT)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33]\nacceptance_tests:\n  path: tests/acceptance/W2-88a/\n  author: independent-test-designer (MR-3); written before the text\ntrack: A\n---\n",
      "chunk_id": "50693ed17d3634461fe562ec",
      "routes": [
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "aa9e808019587c5a0103570b",
      "sha256": "24dd22261752dbb3712c87222c91d7e6b357b82a7f0bc71381a8effbd25532dd",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "start_line": 119,
      "end_line": 127,
      "text": "  fitting and DEC-1179 (4)'s rule word for word.\n- **Why it goes by CIT-P:** a kernel skill path, so the CIT-P, one independent review, the owner's approval of the\n  bytes, a version bump to 1.1.0, and the `.claude` copy by the copies ACT after W2-187 merges.\n- **W2-88a's cases stay unrevised:** the new step keeps \"declare\", \"measure\", \"the verdict set\" and \"once\", so its\n  matcher passes. This was checked on the draft text with `check_steps`, with no problems.\n- **One departure from the brief:** G4's cron line in A9's ACT package is code (`src/gov/adopt/memory_sets.py`,\n  `walls_act`), which the product-spec role cannot write. That code moves to W2-187 (S11), and W2-188 carries only its\n  text.\n\n",
      "chunk_id": "aa9e808019587c5a0103570b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "W2-88a-CIT-P",
      "sha256": "d1932ce0b8371c56b2503a895b9e912cc6084d7f324c0ccc3ea3dfe5c29da952",
      "path": "docs/changes/W2-88a-CIT-P.md",
      "start_line": 34,
      "end_line": 51,
      "text": "## 2. The kernel file: `template/governance/kernel/skills/adopt/SKILL.md`\n\n| | sha256 |\n|---|---|\n| before (`ba27e4c0d`) | `641a347b9b14101dde711f3550f087e714e404575f780be2a3cd91ff2925102d` |\n| after (`f1ae5fecbc52`) | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` |\n\nThe sha256 before is that of the file at the base `ba27e4c0d`; the sha256 after is that of the file as the latest commit of\nthis ticket that changes it holds it (`f1ae5fecbc52`).\n\n25 lines added, 2 removed (`git diff --numstat ba27e4c0d f1ae5fecbc52 -- template/governance/kernel/skills/adopt/SKILL.md`:\n`25 2 template/governance/kernel/skills/adopt/SKILL.md`).\n\nThe lines added:\n\n```markdown\nWave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, the full A9 (its lite form, the Wave 0 memory practice, is the section below), A11 (full audit) and the full verdict.\n\n",
      "chunk_id": "2c6b7d255c1cb922fe858e83",
      "routes": [
        "semantic"
      ],
      "batch": 1,
      "status": "PROPOSED",
      "in_force": false,
      "not_in_force": "PROPOSED"
    },
    {
      "id": "DAEO-zlog",
      "sha256": "74e4b72b68d428aa1f7ee40ff6d21dbff5c06fb04018eee3d931cdb737462eb0",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 135,
      "end_line": 148,
      "text": "  - `grep -c 'gov.memaudit\\|standing declare'` of the three copies: 0;\n  - the I1 `git diff --stat` and hunk count.\n\n  It runs no test suite.\n\n- **I6, the CIT-P record `docs/changes/W2-188-CIT-P.md` (S5).** Built from the draft\n  `.gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md`. It holds:\n  - the skill's sha256 before (`16fd341f...`) and after; the after equals the kernel copy at the ticket's last commit, so\n    the record is the last file changed;\n  - the lines added and removed;\n  - the old and new text of each changed place;\n  - the impact table: W2-11's body case `test_every_copy_carries_the_kernel_skills_body[adopt]` red until the copies ACT;\n    W2-88a's cases unchanged;\n    [Re-baselined 2026-11-14 (DEC-1157 (12), P-W2-188-S5 (a)), new beside the old: the impact table says W2-11's body and version cases do not cover `adopt` (parametrized over test-design, orchestration, audit and qa-review, `tests/acceptance/W2-11/test_w2_11_skills.py:124`); the hard-block check `adapter-portability` reports `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md` until the copies ACT; W2-88a's cases unchanged.]\n",
      "chunk_id": "2213b4f6d005dd6587b05bac",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-zlog",
      "sha256": "0301dd75c2e1fdbc242c01737cebd88e9ac3f784f5a68fc7f270d1cc8869679a",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 44,
      "end_line": 45,
      "text": "  - 'S5 The CIT-P record `docs/changes/W2-188-CIT-P.md` gives the skill''s sha256 before and after, the lines added and removed, the old and new text of each changed place, the impact table (W2-11''s body case red until the copies ACT; W2-88a''s cases unchanged) [Re-baselined 2026-11-14 by the CTO within purpose (DEC-1157 (12), P-W2-188-S5 (a)), new beside the old: the impact table (W2-11''s body and version cases do not cover `adopt` (parametrized over test-design, orchestration, audit and qa-review, `tests/acceptance/W2-11/test_w2_11_skills.py:124`); the hard-block check `adapter-portability` reports `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md` until the copies ACT; W2-88a''s cases unchanged)], the independent review''s verdict and the owner''s approval line of the bytes before the merge [CAP-33, DEC-105] Verify: the record holds both hashes (the after equal to the kernel copy at the ticket''s last commit), the counts, a `verdict: PASS` as the last verdict and an `owner_approval:` line naming the sha256'\n  failure:\n",
      "chunk_id": "281c225f9be74cd63a560c7a",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "W2-188-CIT-P",
      "sha256": "fd983ee0c90ff2665b6d47b326eeb0adaa529d99cc27f69935a6a69f2a5b79f0",
      "path": "docs/changes/W2-188-CIT-P.md",
      "start_line": 1,
      "end_line": 16,
      "text": "---\nid: W2-188-CIT-P\ntype: change-impact-proposal\nstatus: 'APPROVED: the owner approved the skill''s bytes 6a884cf1 (DEC-1181 (1)); merged by hand on w2/integrate at 5f9a9dedf after W2-187''s land; the copies follow by ACT-CLAUDE-COPIES-12 (DEC-1183 (3))'\ndate: 2026-11-14\nbranch: w2/W2-188\nbase: '5336a6fca (the adopt skill at sha256 16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0)'\nhead: 'd782640dee6b0ff547ea7254498c482f416a4e69 (the commit holding the skill''s final bytes, sha256 6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489)'\nticket: DAEO-zlog (W2-188)\nauthor: product-spec session of W2-188, from the CTO's draft (DAEO-sdxk)\nreview: 'PASS (round 1, docs/probes/DAEO-zlog/PR-DAEO-zlog.md)'\ndecisions_carried: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1074, DEC-1072, DEC-1071, DEC-105, CAP-33]\nowner_approval: '6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489 approved by the owner, 2026-11-14, DEC-1181 (1) (\"yes W2-188 adopt skill 6a884cf1\", chat, ~15:40)'\nstate_class: EVIDENCE\n---\n\n",
      "chunk_id": "8eba07fe3ffcefbd633807b5",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-zlog",
      "sha256": "145e64ce8c4d0df35ef616bdc2b9c6299ab60dc72609044a14dbfe23a55526ef",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 59,
      "end_line": 71,
      "text": "# W2-188 The adopt skill's step 6 and the practice record: the standing set\n\n**Problem.** The adopt skill's A9 step 6 (`template/governance/kernel/skills/adopt/SKILL.md:58`, and the two `.rulesync`\ncopies) says: \"Declare and measure the verdict set once. A miss stands as it is: the set is never run again.\" The\npractice record says \"measured once\" in three places (`docs/research/W2-88-memory-practice.md:91-92, 190-191, 221`).\nDEC-1176 (1) kept them standing until the weekly re-measure was decided. The owner decided it on 2026-11-14 (DEC-1179,\nprovisional): the verdict set stays as each repository's standing set, judged every week at 95 %, counts only, checked\nmonthly against a fresh set.\n\n**Approach.** Re-word step 6 and add one paragraph after the seven steps, as `drafts/memory-audit-p1/W2-188-CIT-P.md`\n\u00a72.1 quotes. The proposed step 6 keeps \"declare\", \"measure\", \"the verdict set\" and \"once\", so W2-88a's matcher passes\nunrevised; this was checked on the draft's text. Re-word the practice record's three places and add its \u00a79 (\u00a72.2). Bump\nthe version and write the CIT-P. The skill names no subcommand, so the text does not wait for W2-187. Its promotion and\n",
      "chunk_id": "980d137fb2c88a172a647136",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-zlog",
      "sha256": "297e81bdeee5e75d997739333cdf43e7638d28fdee8353fdb0d425ff72ba4f46",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 118,
      "end_line": 139,
      "text": "    - what the set is;\n    - the method: the reader ranking the whole bundle and searching again once, A2, with E2's 115 and 128 of 138 and\n      E3's 114 against 84;\n    - the bar, ceil(0.95 n);\n    - the walls, with the literal `counts only`;\n    - the literal `never chooses or judges a fix`;\n    - the sentence that W2-88 S10's second reranking model stays forbidden;\n    - staleness by count;\n    - the monthly check with its two 5-point rules;\n    - DEC-1179 (4)'s text as recorded, word for word: the bytes of the register's DEC-1179 line `  - (4) ...` after\n      `(4) `, from `**Below 95 %:**` to its closing `.`.\n\n- **I5, the checks the session runs and records under `docs/probes/DAEO-zlog/` (S1, S3, S4).**\n  - `check_steps` on A9's region of each copy (`a9_regions`) and on the practice record's \u00a76: no problems;\n  - `check_pointer` on A9's region: no problems;\n  - `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt`: exit 0;\n  - `sha256sum` of the three copies: equal;\n  - `grep -c 'gov.memaudit\\|standing declare'` of the three copies: 0;\n  - the I1 `git diff --stat` and hunk count.\n\n  It runs no test suite.\n\n",
      "chunk_id": "0fcaf5e6f960d178b3da4058",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "W2-188-CIT-P",
      "sha256": "7f78ae9da8bb1b30b40c2ed8b4e6ac8ef4fd907c10bc5421d476bb15c92c91ee",
      "path": "docs/changes/W2-188-CIT-P.md",
      "start_line": 133,
      "end_line": 140,
      "text": "| `template/governance/kernel/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` | 74 / 76 | 5 / 3 |\n| `.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` (equal to the kernel copy) | 74 / 76 | 5 / 3 |\n| `template/.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` (equal to the kernel copy) | 74 / 76 | 5 / 3 |\n| `docs/research/W2-88-memory-practice.md` | `f4628a01434b0fc1638b8aa8a2fc804c48cef5d0150abd4376bb751459f61158` | `76eaaeb5487739643cef6d79d8f736331ee5396756b1f123c5236c9bcb60d312` | 280 / 291 | 15 / 4 |\n\nThe skill's lines changed: 3 removed (version, step 6, governing sources) and 5 added (version, step 6, the blank line\nand the new paragraph, governing sources).\n\n",
      "chunk_id": "2c873ce2ea8f5429263e728b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "W2-188-CIT-P",
      "sha256": "273f7e0c2aaace2d5a1e1c870c12f3a9bdb9cb1c6e96645c0562febcba07bc28",
      "path": "docs/changes/W2-188-CIT-P.md",
      "start_line": 39,
      "end_line": 51,
      "text": "### 2.1 The adopt skill (three copies, byte-equal)\n\n**Front matter, line 4.** Old: `version: \"1.0.0\"`. New: `version: \"1.1.0\"`. (W2-88a is closed and left the kernel copy at 1.0.0; the\nnext minor is 1.1.0.)\n\n**A9, step 6 (line 58).** Old:\n\n> 6. Declare and measure the verdict set once. A miss stands as it is: the set is never run again. [DEC-1071 (1)-(3), DEC-1098 (1)]\n\nNew:\n\n> 6. Declare and measure the verdict set once, at Wave 0, as the first verdict. From then on it is the repository's standing set: judged end to end every week on the same questions (monthly once the repository is stable), as Gov OS's memory is judged (the standard's bundle read whole by the reader, which ranks it itself, and search again once), against 95 %, behind the walls, counts only: only counts leave its run. It never chooses or judges a fix: fixes are chosen on the tuning set and on the fresh sets' misses. Each month a fresh set, measured once, checks it for fitting, and a standing set found fitted is replaced. A miss stands as it is: it is never re-run in the same week and never re-scored. [DEC-1179 (1)-(4), DEC-1071 (1), DEC-1074 (1), DEC-1098 (1)]\n\n",
      "chunk_id": "ea3d8cc584f84c1e5a94c98c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-zlog",
      "sha256": "831b2365b9082a763e936764ce66fddea15554161e21005e0ce5933b41101eae",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 1,
      "end_line": 32,
      "text": "---\nid: DAEO-zlog\nwbs_id: W2-188\nexternal-ref: W2-188\ntitle: \"The adopt skill's step 6 and the practice record say the verdict set becomes the standing set, judged every week at 95 %, counts only, checked monthly against a fresh set; A9's weekly cron line named (MEMORY-AUDIT G6 and G4's text; CIT-P)\"\ntype: task\nclass: spec\nrole: product-spec\nprofile: STANDARD\nstatus: closed\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-14\ndeps: [DAEO-pg6i]\nallowed_paths:\n- template/governance/kernel/skills/adopt/SKILL.md\n- .rulesync/skills/adopt/SKILL.md\n- template/.rulesync/skills/adopt/SKILL.md\n- docs/research/W2-88-memory-practice.md\n- docs/changes/W2-188-CIT-P.md\n- docs/probes/DAEO-zlog/**\nreads:\n- .gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md\n- governance/project/orchestration/packages/MEMORY-AUDIT-P1.md\n- .gov-runtime/scratch/orchestrator/drafts/memory-scope-20261113/MEMORY-AUDIT.md\n- docs/changes/W2-88a-CIT-P.md\n- docs/changes/W2-98-CIT-P.md\n- tests/acceptance/W2-88a/**\n- tests/acceptance/W2-11/**\n- governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md\n- governance/project/orchestration/packages/LIFT-1/E3-RESULT.md\nneeds:\n",
      "chunk_id": "d02e6e122718f832594ac86a",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-zlog",
      "sha256": "c99c7114d57bcbf38a1c523c5f02f672aaa1722510f0829217643b33c9f802d3",
      "path": ".tickets/DAEO-zlog.md",
      "start_line": 92,
      "end_line": 105,
      "text": "  - **Line 74, the sources line:** adds DEC-1101, DEC-1125 and DEC-1179 in numeric order.\n\n  `git diff <base> -- template/governance/kernel/skills/adopt/SKILL.md` shows those four hunks and no other.\n  `.claude/skills/adopt/SKILL.md` is not touched (the copies ACT).\n\n- **I2, step 6's text constraints (S1, F1, F3; W2-88a's `check_steps` at `tests/acceptance/W2-88a/w2_88a_support.py:207`).**\n  - **The step-6 anchor:** step 6 opens with `Declare`, and no word starting `declar` stands earlier in steps 1 to 5.\n  - **The step-6 checks:** it says `measure`, `the verdict set` and `once`.\n  - **The step-7 anchor** (`record\\w*` then, within one sentence, `every|each|all` then `method`) must not occur in step 6.\n  - **No subcommand:** it names no `gov.memaudit` and no `standing declare`.\n  - **No second reranking model:** it never calls the reader one.\n  - **The literal phrases step 6 holds:** `standing set`, `every week`, `same questions`, `95 %`, `counts only`,\n    `never chooses or judges a fix`, `fresh set` with `month`, `fitted` with `replaced`, and `DEC-1179`. S1's\n    statement that a miss is never re-run in the same week and never re-scored is kept in words as well, though the\n",
      "chunk_id": "212585d8ee100d36bda9d82a",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 43,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "a656de156a09db4d45758dc9",
      "parent_id": "307bdb6716dc111e0f2dfa41",
      "path": "docs/changes/W2-188-CIT-P.md",
      "start_line": 149,
      "end_line": 160
    },
    {
      "chunk_id": "50693ed17d3634461fe562ec",
      "parent_id": "b324b2635f1d90a630326ae8",
      "path": ".tickets/DAEO-pg6i.md",
      "start_line": 25,
      "end_line": 50
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "DAEO-0cd2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "25941c2148944e76daecadca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "2a0fb9481b12b0ff845f8ff0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "63054488241b2b8406ce4219",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "ce3113e54f89d9e0f7b5078b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "b7894de69404ca4f4912e3d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "304896d9cd893916a0c9bfdf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-192-CIT-P.md",
      "chunk_id": "5aec403aafd264c2a8e75d15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "e88e7b8282c8eade61b1fd8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-188-DAEO-zlog.md",
      "chunk_id": "14d8e59ec3d9ee99dac71ce6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "81c82a924b141afa383a98f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-188-DAEO-zlog.md",
      "chunk_id": "a9a70080c999f59e3b424fce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "392dd4a90bba65ddf16aa8d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "4eda231fd75a78a9ae3167c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "d449d361b16aa9da8364b156",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "65c75ac501178cd3b8d63007",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "fcd033fe0b86db431bcf1963",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "04abca3a46d5c1b529e99f41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "026cb3b7b45c2d39e91908a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "e92e40ffe38fd4574168c135",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "3e20c58caa86a82bae4b4665",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qskx.md",
      "chunk_id": "4bbcb99707e022ad2d64dd3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "b8b77dadfa0132ae824210fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-pg6i.md",
      "chunk_id": "3d58c6f6a87def756719262c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88a-CIT-P.md",
      "chunk_id": "8c47925c74e17d1dff15ec3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "1550ccdf6bb7aa042bc0422f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "be25adda50d798e6b9dc5d9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "15006c6974b005849957fcce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "d5db9f697afcb8c3d1cedf47",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "ef73c009def7a4444f40b2dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "2576f08f538cd1f7a04ea934",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-188-DAEO-zlog.md",
      "chunk_id": "485eb4bd2c7d39f9eebd39aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zmo4.md",
      "chunk_id": "07556d927aea6ede71e7c4ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "f9ebff885281588860c1fde7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-hgv3.md",
      "chunk_id": "6d5ea52bcf386c831625819e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "6f3d6bfc7f7930e48cf50155",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261114.md",
      "chunk_id": "774b0577c4f63fc5ae8c33ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "e269fecb9476e08a32b0245e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "fcae15343f5aafca97a951ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e4c6e0314cedac58ac559f33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6icv.md",
      "chunk_id": "55d5adcbcada0e4c3131ebb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "9a06e13e20467b45ee55952d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "22c528bdbc664490a6a2e611",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88a-CIT-P.md",
      "chunk_id": "e4717cd3ff201b83d208b6fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "f10fe9be89a617a9c4881f33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "d3d31315cb990fee01dc06fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "0cf27b6a3273af55de87bcb2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "9dbf2797af19f9515995bd56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-uw5h.md",
      "chunk_id": "8517b622a0d25d22aa1103f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "9ec7687d88a4d88935dd5be1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88a-CIT-P.md",
      "chunk_id": "b862876348ef29bd51c078ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "6dcf22f3832e4bb8a67e3959",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rpfv.md",
      "chunk_id": "eb6682c28373c6d41a249388",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "dca8fcbdcf8f91278cc2ef02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "a852a482dc4b1ad328515b18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/superpowers/vendored.yaml",
      "chunk_id": "5bd6813456170245fa090421",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "e55085e6dbe0b22ec8c0ca84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-uw5h.md",
      "chunk_id": "8348abec337a4d55b62530d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "059dc7ee7fef233f027ec122",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "cd0784bf95e4805fcc400d04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88a-CIT-P.md",
      "chunk_id": "a0c70b2173f97fe2cf59d527",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.md",
      "chunk_id": "bd67db30fe765d46b4037c11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.md",
      "chunk_id": "91144f8645da5ea2a37f6b06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "b8194cd8d2bc7a5d62026fa2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "e1f675ad8a1fadb73739aec4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/adopt/SKILL.md",
      "chunk_id": "037259f196f1b33e04f47a10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "4a10edccb8708c063ec8badb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6icv.md",
      "chunk_id": "d432eae8ebb736e8b5a51fad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "17a3df86d492af5195cd565f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "9b610641ac94b70b9671d08f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3c9ba3a96bbacb78682c3c8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-s5.md",
      "chunk_id": "0675688dc4daf254761eec79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d8df.md",
      "chunk_id": "dcf78958cbcdac1519131e64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "9ba278bd27ef50575f95252a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "a7d85c37095210c81ae91b45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "90ce1a68de34943ae6ef4f5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "1d51cd9d8049175a9abae2b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "921a1d8aa7de066570c64134",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-24.md",
      "chunk_id": "27846c0ccb5fd57977f99386",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "cb8e73493beeffbc6c27e3ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "1dd8fc835f4f84411392dccd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e3277006fe60229b798f614d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "9d458105d64cfe7df724d57b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "41accb7e87167eca64319283",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "395d1b34c63864d042f8a821",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "87bf64df5eab6a90ef7e95e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-192-CIT-P.md",
      "chunk_id": "06f3f769a352ea084d069ec4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "4c461a8ad5eaa0c1b1907f64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b7f781ef6d5b47a3fc0fa821",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "1188e2995060bfd298f1aa67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88a-CIT-P.md",
      "chunk_id": "d69f8b0e1ca2c24d1d17a7ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "41ea866e016991006922172b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "9f924b82f70788421d0c6099",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "d69c098ca919dd70684ff5f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b439c327366f5e524d160805",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-192-CIT-P.md",
      "chunk_id": "3c7433e39c41177b0aca8a70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "f0a1f6b3d7f8f52ffa21db39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "a3cf356e7b4287e3a3eb4218",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-c12.md",
      "chunk_id": "642ad49b3e1c5d74938d2ba3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "cd8e5505017735f2b22e288a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "199385597b3a509db9e70799",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k7hz.md",
      "chunk_id": "bf963307679ecac9fbe58a10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "23af55bbaabb43c50dfb54f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "89c10a4db4b8415b8a20fdd9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-lxzn.md",
      "chunk_id": "58b5117c15fd457fd14c7639",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "290199afdd879cbc0a8614ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-c12.md",
      "chunk_id": "1796b0137df908b5e2cd709e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "6c83b2c610915e3e5015f13b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-uw5h.md",
      "chunk_id": "579b2d2190d2c3d64664e46e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "02e85df9d23d1ab4aa083ae2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wi46.md",
      "chunk_id": "09a22b06f018fd13f5123b39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "ca47f58b92c7f4f640544212",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-s5.md",
      "chunk_id": "e89792cc5d347569642178df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "013722cc19dac9683b3df113",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "50d350f54324d669ba95184b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "ec39e9e70690fbc1a425fadb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-c12.md",
      "chunk_id": "9c85d8199b99246ea1ae0df6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "ef26f9c061abf87a154a1932",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "ca1a118d9e2bc9554792a610",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-pg6i.md",
      "chunk_id": "295ca2e0170c40bae42028fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "55f23b7b029539c074a0e430",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "a32a225d874c46e4ba2724e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "5437f6438ba928c2d7fc9924",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-pg6i.md",
      "chunk_id": "a2bf0719e310f19802b006a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "7e8ca2de11e0f32e47ac9194",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/checks.md",
      "chunk_id": "3dee146525fec4435c669e44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "149da971de4a1187126ac108",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "badbbe2a8c63d5ba766b85e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "b3ebd8af79af7fe1148151cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/templates/skill.md",
      "chunk_id": "18a5f1799927b3dd774cecfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "d6ad84c1f8a76f80d2e1c960",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "df84b128cb438096fb998124",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "9a498af6813bbb9d98cea3e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-s5.md",
      "chunk_id": "0602257c4a8e84bce557a74d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c868dc69b9037ef165f95485",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "d57fceba172a8488c20265d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261115.md",
      "chunk_id": "30533d2c5e11fe2e72c2c008",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "613002508f5f634f58ec8458",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "73612eab79846d5296e742de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "104f2c7ed0f4f3c66abd41e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "70ad0d2e86f581056e6e4ec8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-reds-launch.md",
      "chunk_id": "bb4e2bdbbf13fba27e7ac851",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "680c99772f51f7d78d9c38da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wi46.md",
      "chunk_id": "9cbbbb674d05dde7d69a79e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "640b1ff623cab1c9b146b181",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "be331eb91c3cfc6241e0e0c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-192-CIT-P.md",
      "chunk_id": "1f6930a1c0c388b987d3c33d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "66b15001fc9e12b19a4b57be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "f1b479eec2a67ac453e6b9bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9f782709afa5e4ec6c375522",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88a-CIT-P.md",
      "chunk_id": "531e4e4a87a73ad2ae460a10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "7df23ff8e9ffcb4b6f0002ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "06f1c9e8bfc38c142995f06f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rpfv.md",
      "chunk_id": "bf185bc1b0dc6e98109d7ab7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "fb7a3a906cc09b816be5d9f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-reds-launch.md",
      "chunk_id": "6524c2dc1ccbc17e5bafaba6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-100-CIT-P.md",
      "chunk_id": "7b63da77e8d8607d68a15bc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "c0ea9299d9ea2bd942917183",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "e7ebeabfe712a6a038e026af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-uw5h.md",
      "chunk_id": "bede1ce55d7dd437b7f4a5cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "c1b69b9d7f703688993e098b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "1517bf7270400d40d00e29a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "2acaac8044619f1f6bbde9dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "7ff8dd965361d903c04e1dba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4b070cc25ea83a25d4c48a95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "0f0d6662a1c0897309190955",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/conftest.py",
      "chunk_id": "e3dd9f7b23d18868413f3aac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "621c005645b6d280e3dcd4e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/templates/skill.md",
      "chunk_id": "23859603d5229957ec00faf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "c8c3a8710a80a2c10fa3ffb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261115.md",
      "chunk_id": "e7fad9ede91826f9500af830",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "7955bd57e436df8a68344ab5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c2-ticket-lines.md",
      "chunk_id": "5e724331ee3793add8a92cf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zlog.md",
      "chunk_id": "3e9d5b0a4e0194d28482f74a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "91dc5583321075dec21ef826",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-c12.md",
      "chunk_id": "a090c3e47efe8c31d0c410be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/brief-gaps.md",
      "chunk_id": "f6fecec1f9fa58f63b7d51c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88a-CIT-P.md",
      "chunk_id": "df2f1246a8d5adb30b2ed6e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "6f34d383f980bf297090cc9e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-drhj.md",
      "chunk_id": "76c35f9bc20ee483d51733ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_copies.py",
      "chunk_id": "d80b84a21d7ed1b7e01f5418",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "de6a5abdb5480ff96039df58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/templates/skill.md",
      "chunk_id": "f70a516b23162a002c6e091b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-i89t.md",
      "chunk_id": "2e60c0a94706072da881482c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-c12.md",
      "chunk_id": "6db2dcebac8a7c2df232d817",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "37b0b788b7071778264b2d4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "32d06e9f2616be163c1aeb67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-uw5h.md",
      "chunk_id": "23955cee1e1502e13d034448",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/OWNER-BEFORE-1200-20261115.md",
      "chunk_id": "19453303c47e7f5d30628788",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-101-CIT-P.md",
      "chunk_id": "0986d3accd99c7b626284d6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "bb42e84e2c57e6ce175c2037",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-s5.md",
      "chunk_id": "ded7f15faae3ca2d2548cc99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "chunk_id": "5f34a805e74143d3586ba694",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "08c83ba4f80526331793fcf1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "670cd82d775c701c31574b68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_copies.py",
      "chunk_id": "933f0aec5f770d06bfaf2cd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r1.md",
      "chunk_id": "1ef2d2b73968cdd6003c906b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_copies.py",
      "chunk_id": "5b61ecfb3ed624c5a4a8aa56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-pg6i.md",
      "chunk_id": "81614704ba8bda78c612efa2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "1350f8f88f3e4081996ed269",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6icv.md",
      "chunk_id": "f0b31f0b41bb761c92b77269",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261115.md",
      "chunk_id": "e76d63f4d9ba4dba704e2065",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "8e541875fff221100bad54fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_skill.py",
      "chunk_id": "965de892b922bbd8484f1016",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/EMERGENCY-2.md",
      "chunk_id": "e61a66545d87e2d921af7fbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "d4db21e964997d9b1df3431a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_practice.py",
      "chunk_id": "0139eab0f556905c092d477c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "cdf3554f51d77545e6bf4cf4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-192-CIT-P.md",
      "chunk_id": "557357c4f403170fe3208262",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/OWNER-BEFORE-1200-20261115.md",
      "chunk_id": "dd625406f975aaedfa947f17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-drhj.md",
      "chunk_id": "e31d4f6eaacd5f5b1b46c4a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "a19ee06aacb1fad860afe2ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6icv.md",
      "chunk_id": "4db2d3eb6611ba62ddd646d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_copies.py",
      "chunk_id": "361462887e3e7858a8bcfabd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "0e1a75a66d6e6145aa04c137",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/checks.md",
      "chunk_id": "6b619a1fb64916dc6ea0c4d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "3a9f36ce237e810346ef9253",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "chunk_id": "e4437019a6f16ed077e9fee0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "cc7d14fca27d0e19419f7583",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_copies.py",
      "chunk_id": "7af048375e9ef0e6533cab98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "dc6e1c3e08ae20da806ebcf3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "17283cfd4aece642ca3a3636",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/EMERGENCY-2.md",
      "chunk_id": "d1e2bea80d072938c080c14c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "a40f05aa8a4c35229f10fde6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "bf0fd3cfe08dbdd46e4ff632",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/EMERGENCY-2.md",
      "chunk_id": "d0a3df19db76c109ac0a4a83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "451ec92885b7a1e1fa816602",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "f3eeb3f54c00358bedaf9124",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/w2_188_support.py",
      "chunk_id": "0b3fc02fed1e8db037c06488",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "1bf0de33d95d78eb854f4143",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "6745e7dbbcc289ecf882a2df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "b3bca8dc83c822a205aa2a4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "c6da1032993011b5af1860dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1210-fresh-80.md",
      "chunk_id": "96ecb074cbb7ed606bcadb81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "c1b939f827435d5bf9ae9c97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/EMERGENCY-2.md",
      "chunk_id": "dd31a28e7a00ec8bb46eaf99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "3313027705393f55a279d9b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "975f8e076948ebe4c3587bd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "efb86940ac3f162e62f4ec00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "7b58f157ad2751eeb64aa17e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-tickets-and-rubric.md",
      "chunk_id": "d1759615334fb0d1e65c65a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1210-fresh-80.md",
      "chunk_id": "1587099cc438d2b1b7cb2fe5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "61738a11f4c6e494bff95565",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0cd2.md",
      "chunk_id": "e581e9ff5f8be75890a5d820",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "c8be5bf3b50c2b232c5f31cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog.md",
      "chunk_id": "da4579f645d8a9cfee030b64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-ti-cuts.md",
      "chunk_id": "d91b2052af1e0d3524b95a27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "aa664d48f3ba7163fd257b58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2ca612f58d62f671e3aca3ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog.md",
      "chunk_id": "dc43359bd4b00c4ccb55754c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "8bcbe739828f7160b7bd835c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "0259af331d621c3357294645",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "de1731ff72231d060890730e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "c4341dddbceefad6bc74dff7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "2960ac2b8192985bc42c8edc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r3gx.md",
      "chunk_id": "57f159839006b595f4707085",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1210-fresh-80.md",
      "chunk_id": "788587ed475779e9663be83e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "d367c2cbf6f63746bc3288a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "a06d0574dd3bb0341ba39093",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "2fa177f06982abbb119be690",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "53d7a59f69ae4cba83e70765",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "696bf8db98d4b1d022a50c90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "2d7651d2ad13028b79135a1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "e030ee0bd9ced54cc81bb903",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "e2b215ddb3e4207183221eaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "c45fd5e7896101491a5532a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "7ef7065015b76c1d37fc4266",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "f37e36e9269bee578d249dfd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "8ffc1baa84ac5d77f271d4d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "6566e573aeef26b226ad3f50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "7e13d1acf7b5b842ec76f07a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "4d66948a7fee12d32b7c0288",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog.md",
      "chunk_id": "047c667acdda6e8b4351b183",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "5f0b4d91d4c0e0b1a07a08ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-188-CIT-P.md",
      "chunk_id": "9643d2affd98cad864a5bd14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "ce26c674b606d1bef91aefb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "9a366b23e8d5a0674bae78d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "e3a3686b277c6f72b5ba94cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog.md",
      "chunk_id": "c3d11f2a4e7cdd33227d42ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog.md",
      "chunk_id": "7b506aede696575cc59209f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/decisions-in-force.md",
      "chunk_id": "8e7962219ce82f012151a7aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1210-fresh-80.md",
      "chunk_id": "92b6303ddad326e0f5cb33da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1210-fresh-80.md",
      "chunk_id": "58d1eed712794654d63db7f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1210-fresh-80.md",
      "chunk_id": "b3e38fdf47e4b2998fc2ef71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "3e3cac935f0c3e246513ab37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "0344f080c27897be6fbc6719",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "b1297f1e81c9020a4a8ec4ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/checks.md",
      "chunk_id": "287d678863b704ab3a7e9c19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "ef2b57d91fdb01b7d57d3fe1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog-s5.md",
      "chunk_id": "f9ecaeb91b930db8ab6b5758",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "bda7b496ca9055a3fa1de5ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "f6b92c0f273447b745234402",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "59c8cf2f8d21e00d357d1517",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "4423d983b013631a4e02f57b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/PR-DAEO-zlog.md",
      "chunk_id": "3da6518d407feb216fec3a68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-195/test_w2_195_s4_shipped.py",
      "chunk_id": "4de9b800e4d863828d3887a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "bcb8263e97521f193658f065",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_copies.py",
      "chunk_id": "5e14ceee2fcd3d5cc324b5bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "be93eb2111941ac74367a18d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "26a27135e2efd522b2c25cdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "f670d0d1b2f3e34c4a7d9079",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88a/README.md",
      "chunk_id": "20b1a5c11840c7baf6520bb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88a/README.md",
      "chunk_id": "84b118834b213a6b6160210d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-195/README.md",
      "chunk_id": "9ff3905ee781ef48d41e3fe9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zlog/checks.md",
      "chunk_id": "21bd72f1ca23b8dc7bb40ab3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/test_w2_188_copies.py",
      "chunk_id": "269e4d92305b146d8f32aa6d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "c85b2c3c0ddd9d1a284a0bdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-188/README.md",
      "chunk_id": "a0849eeca30cb512e68ebf18",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    },
    "closure": {
      "available": true,
      "reason": null,
      "followed": {
        "records": [
          "CAP-33",
          "DAEO-2bdu",
          "DAEO-pg6i",
          "DEC-105",
          "DEC-136",
          "DEC-832",
          "DEC-1097",
          "DEC-1098",
          "DEC-1101",
          "DEC-1157",
          "DEC-1176",
          "DEC-1184"
        ],
        "left": 5
      },
      "changed_by": {
        "DEC-1098": [
          "DEC-1225"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5841
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLW1hNHEubWQiLDY1LDc0LCIyZjY1YTc1YmVmZWRiOWRiYWNlNTJhY2YiXSxbIi50aWNrZXRzL0RBRU8tbWE0cS5tZCIsMTQ5LDE1NywiMTU2MjhhYThlNjE5OTY5MzJjODhhNDg0Il0sWyIudGlja2V0cy9EQUVPLXBnNmkubWQiLDUxLDUzLCJkYjEyODk2ODljZDNiZjI1OGJkODc2MGIiXSxbIi50aWNrZXRzL0RBRU8temxvZy5tZCIsMSwzMiwiZDAyZTZlMTIyNzE4ZjgzMjU5NGFjODZhIl0sWyIudGlja2V0cy9EQUVPLXpsb2cubWQiLDQzLDQzLCIzZDE1YWY1NWFiZmM5ZDk5ODQ0NzBhYjAiXSxbIi50aWNrZXRzL0RBRU8temxvZy5tZCIsNDQsNDUsIjI4MWMyMjVmOWJlNzRjZDYzYTU2MGM3YSJdLFsiLnRpY2tldHMvREFFTy16bG9nLm1kIiw1OSw3MSwiOTgwZDEzN2ZiMmM4OGExNzJhNjQ3MTM2Il0sWyIudGlja2V0cy9EQUVPLXpsb2cubWQiLDgxLDk0LCI3Zjg5NmE0N2Y3MzM1NzA1ZDlhNWY4ZjgiXSxbIi50aWNrZXRzL0RBRU8temxvZy5tZCIsOTIsMTA1LCIyMTI1ODVkOGVlMTAwZDM2YmRhOWQ4MmEiXSxbIi50aWNrZXRzL0RBRU8temxvZy5tZCIsMTE4LDEzOSwiMGZjYWY1ZTZmOTYwZDE3OGIzZGE0MDU4Il0sWyIudGlja2V0cy9EQUVPLXpsb2cubWQiLDEzNSwxNDgsIjIyMTNiNGY2ZDAwNWRkNjU4N2IwNWJhYyJdLFsiZG9jcy9jaGFuZ2VzL1cyLTE4OC1DSVQtUC5tZCIsMSwxNiwiOGViYTA3ZmUzZmZjZWZiZDYzMzgwN2I1Il0sWyJkb2NzL2NoYW5nZXMvVzItMTg4LUNJVC1QLm1kIiwzOSw1MSwiZWEzZDhjYzU4NGY4NGMxZTVhOTRjOThjIl0sWyJkb2NzL2NoYW5nZXMvVzItMTg4LUNJVC1QLm1kIiwxMzMsMTQwLCIyYzg3M2NlMmVhOGY1NDI5MjYzZTcyOGIiXSxbImRvY3MvY2hhbmdlcy9XMi0xODgtQ0lULVAubWQiLDE0OSwxNTQsIjE2YjlhYzNhZmZkOTViNDFiODdhOTEzYiJdLFsiZG9jcy9jaGFuZ2VzL1cyLTE4OC1DSVQtUC5tZCIsMTU2LDE2MCwiYzZmM2M5OWYzNmJkYzYyOGY4YzIyMTVjIl0sWyJkb2NzL2NoYW5nZXMvVzItODhhLUNJVC1QLm1kIiwzNCw1MSwiMmM2YjdkMjU1YzFjYjkyMmZlODU4ZTgzIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9NRU1PUlktQVVESVQtUDEubWQiLDExOSwxMjcsImFhOWU4MDgwMTk1ODdjNWEwMTAzNTcwYiJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYSIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiNGEzN2FiMGRhNGE5NDI0ZiIsIm8iOls1LDIxLDIsMjAsMTgsMTksMjcsNiwzMiwzOCwxMCwxNSwxLDEyLDcsMTYsMjQsMyw5LDEzLDMxLDgsMCw0LDI1LDIyLDM2LDE0LDI2LDE3LDI5LDExLDIzLDMzLDI4LDMwLDM0LDM1LDM5LDM3XX0sInEiOiJ0aGUgYWRvcHQgc2tpbGwncyB0b2tlbiBsaW1pdCBhbmQgaXRzIGZvdXIgY29waWVzLCBXMi0xODggcGlucyBvbiB0aGUgc2tpbGwncyBieXRlcyBhbmQgaHVua3MsIEQzIHN0YWxlX2NsYXNzIHNlY3Rpb24gdHJpbW1lZCwga2l0LWhlYWQgZ3VpZGUgcG9pbnRlciIsInIiOjAsInMiOiJhNDU1YjAwY2YwNzM2ZDdhMzdkOWU1ODVlNjQzMGM0NTVlZjRmZTYwIiwidCI6bnVsbCwieCI6WyIzMDdiZGI2NzE2ZGMxMTFlMGYyZGZhNDEiLCJiMzI0YjI2MzVmMWQ5MGE2MzAzMjZhZTgiXX0=",
  "routing": {
    "code": [],
    "named": [
      "7f896a47f7335705d9a5f8f8",
      "3d15af55abfc9d9984470ab0"
    ],
    "phrasings": [
      "the adopt skill's token limit and its four copies, W2-188 pins on the skill's bytes and hunks, D3 stale_class section trimmed, kit-head guide pointer",
      "adopt skill s token limit four copies W2-188 pins skill s bytes hunks D3 stale_class section trimmed kit-head guide pointer",
      "the adopt skill's token limit and its four copies, W2-188 pins on the skill's bytes and hunks, D3 stale_class section trimmed, kit-head guide pointer DAEO-zlog"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": [
      {
        "chunk_id": "16b9ac3affd95b41b87a913b",
        "path": "docs/changes/W2-188-CIT-P.md",
        "start_line": 149,
        "end_line": 154
      },
      {
        "chunk_id": "c6f3c99f36bdc628f8c2215c",
        "path": "docs/changes/W2-188-CIT-P.md",
        "start_line": 156,
        "end_line": 160
      }
    ]
  }
}
