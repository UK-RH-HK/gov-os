# Lead brief: release-rule, releases by code again: DEC-1235 (2)'s rule for approved bigger releases (I-34), W2-209 settled so a fix like RP-1 rides a patch, and `Class: Q` dropped (plan 2-12); under W2-209 (DAEO-a2h5, in progress)

You are a lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`.

## Why
The owner (DEC-1251 D-01, his note): "make releases by code again: build the rule for approved bigger releases (I-34), and settle
W2-209 so a fix like RP-1 can ride a patch." DEC-1235 (2): "you cut every release whose content I have already approved (features I
approved as P1, Contract changes I approved), only when the release acceptance passes, with the re-pin's self-rollback and a push
to me each time"; "W2-209's release rule changes accordingly: a release whose new features and Contract or Charter changes each
name the owner's approving decision passes P1." Today (I-34) `gov release <v> --patch --check` refuses P3 for any feature or for a
fix under an open ticket, so 0.1.8 (the bundle) is "bigger" and only the owner builds it. Read: FINDINGS I-31 (corrected) and I-34;
DEC-1223 RB-1, DEC-1226, DEC-1235, DEC-1251 in `docs/DECISION_REGISTER.md`; `src/gov/release/patch.py` (rules P1 to P5, `evaluate`,
`kind_record`); `.tickets/DAEO-a2h5.md`; `governance/project/release-authority.yaml`; plan row 2-12 of
`docs/emergency-2/integration/INTEGRATION-PLAN.md`.

## What (K-lines added to `.tickets/DAEO-a2h5.md`, the open ticket, each with its verify; the CTO approves them by this brief)
- **RR-1 Approved content passes.** A release whose every feature ticket closed since N and every commit under an open ticket name
  the owner's approving decision passes the rule as a third kind, `approved` (beside `patch` and `bigger`), and `gov release <v>`
  cuts it by code under the authority file exactly as a patch (the same gates, the full regression record, the re-pin with
  self-rollback, the push). "Names the owner's approving decision": a decision id that the register holds as `ACCEPTED (owner ...`
  (read the register by code; never trust a trailer's word alone). Choose where the name lives (the ticket's front matter, a
  trailer, or both), the smallest form the existing tickets can carry, and say why.
- **RR-2 What still refuses.** A feature or a Contract or Charter change naming no decision, or a decision not accepted by the
  owner, keeps the release `bigger`, and the refusal names each ticket or commit and what it lacks.
- **RR-3 W2-209 settled.** RP-1 (`81cdd48b4`, the re-pin writes `gov`'s registry entry) and every W2-209 KPI line are met; bring the
  ticket to closed in your branch with its evidence, so a later fix under it is a fix under a closed ticket and rides a patch.
- **RR-4 (plan 2-12) `Class: Q` dropped.** The patch rule requires `Fix:` or `Class: C`; a commit with `Class: Q` and no `Fix:` makes
  the rule say it is not a patch, naming the commit; no `Class: Q` left in `src` and docs.
- Prove it on the real repository, read-only: `gov release 0.1.8 --patch --check` (or the new kind's check) on `e2/bundle-a` (the
  bundle's batch A: D1 W2-210, W2-211, D3 W2-212, usage under W2-207, models-by-role) says which kind it is and why, per ticket.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-release-rule`, branch `e2/release-rule` from `w2/integrate`. Code area: `src/gov/release/`,
`tests/acceptance/W2-209/` (the independent test designer only), `tests/unit/release/`, `.tickets/DAEO-a2h5.md`. Others work meanwhile
in `src/gov/memaudit/`, the timing tests and the bundle-b merges (W2-207, W2-204, W2-208): do not edit those. Never cut a release,
never re-pin, never edit `governance/project/release-authority.yaml`: the CTO does.

## Green
RR-1 to RR-4 red on the base, green after; `gov accept W2-209` green; then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-a2h5=e2/release-rule --onto w2/integrate --select`), through the heavy
slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; where the approving decision is named and why; RR-1 to RR-4 with tests and result; the read-only check of
`e2/bundle-a` (kind and the per-ticket reasons); the selected run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: c1e81afd3e75 (/home/usain/Dynamic-Agentic-Engineering-OS), store behind HEAD, head 763d18528026, 32 stale path(s)
{
  "store": {
    "commit": "c1e81afd3e7560e7a8f769bb51de083b07d72158",
    "head": "763d18528026573bae99bb7ac906d8377532ff62",
    "stale": [
      ".claude/agents/orchestrator.md",
      ".claude/templates/role-cto.md",
      ".rulesync/subagents/orchestrator.md",
      ".tickets/DAEO-d3sr.md",
      ".tickets/DAEO-esl1.md",
      ".tickets/DAEO-j9z6.md",
      ".tickets/DAEO-l2b2.md",
      "docs/DECISION_REGISTER.md",
      "docs/checkpoints/DAEO-sdxk/CP-DAEO-sdxk-3337.md",
      "docs/emergency-2/CTO-HANDOVER.md",
      "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "docs/emergency-2/briefs/LEAD-bundle-b.md",
      "docs/emergency-2/briefs/PRODUCT-CTO-HANDOVER-METHOD.md",
      "docs/emergency-2/integration/FINDINGS.md",
      "governance/project/orchestration/tools/start_cto.sh",
      "governance/project/test-map.yaml",
      "src/gov/_shipped/template/governance/kernel/templates/role-cto.md",
      "src/gov/close/select.py",
      "src/gov/queue/command.py",
      "src/gov/queue/dry.py",
      "template/.rulesync/subagents/orchestrator.md",
      "template/governance/kernel/roles/orchestrator.md",
      "template/governance/kernel/templates/role-cto.md",
      "tests/acceptance/W2-115b/README.md",
      "tests/acceptance/W2-115b/test_w2_115b_sel.py",
      "tests/acceptance/W2-115b/test_w2_115b_unwritten_paths.py",
      "tests/acceptance/W2-115b/w2_115b_sel_support.py",
      "tests/acceptance/W2-206/README.md",
      "tests/acceptance/W2-206/test_w2_206_sel4.py",
      "tests/unit/queue/test_queue_select_sel.py",
      "tests/unit/queue/test_queue_select_unwritten.py",
      "tests/unit/queue/test_queue_w2_206_flags.py"
    ],
    "root": "/home/usain/Dynamic-Agentic-Engineering-OS"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-a2h5",
      "sha256": "cf7dea706d4155a2e085bcbbc7333dba7a4ff4488c67c880f85d78d536acf951",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 35,
      "end_line": 35,
      "text": "  - 'S1 The patch rule, read by code from the last release N to the release commit C (RELEASE-ON-BEHALF \"What a patch release is\"; DEC-1223 RB-7 keeps P2 third path and P5): `gov release <X> --patch --check`, run by the CTO (`GOV_ROLE=orchestrator`) at C = HEAD, prints a result with `kind` (`patch` or `bigger`) and, for each of P1 to P5, `pass` and a `detail`, and writes nothing; when one planted change is in the range the answer is `bigger` and names exactly that rule and what failed it. P1: `pyproject.toml` at C is not N''s version with only the last number raised, or has a pre-release part. P2: any path changed between N and C under `docs/contract`, `docs/charter` or `docs/emergency-2/EMERGENCY-2.md`. P3: a ticket closed at C that was not closed at N (named by id), or a non-merge commit N..C touching `src/gov` or `template` that carries neither a `Fix:` trailer whose `Task:` ticket was closed at N, nor `Class: Q`, nor `Class: C` (named by commit). P4: the set of command names the CLI knows differs between N and C (the names added or removed are given). P5: a file added to or removed from `template/governance/kernel/schemas` (named). A range of fix commits and chores only answers `patch` with all five passing. N is the newest tag `v<X>` whose record is in `docs/releases/`. Verify: a built repository with two release tags and, between them, one planted change per rule (a contract path, the Charter, EMERGENCY-2, a ticket closing, a feature commit with neither trailer, a new command module, a schema added, a schema removed, a version bumped by more than the last number, a pre-release version) and then a clean range of two `Fix:` commits and a `Class: Q` chore: the check names exactly the planted rule for each, answers `patch` for the clean range, and the tree, the refs and `docs/releases/` are byte for byte the same before and after. [RELEASE-ON-BEHALF K1; DEC-1223]'\n",
      "chunk_id": "9e368d59fbc18c0acb4f97a9",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "59f1a33a109544350b552195d4f41b49ebd13b27ca3605809dba13f97e1c94bf",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 51,
      "end_line": 53,
      "text": "  - 'F5 The plain `gov release` and the pushes stay as they were: `gov release <X>` (no `--patch`) from any session is refused as DEC-772 has it and a bigger release is only ever built by it; nothing is pushed to any remote (no `git push` or remote is called by `--patch` or the re-pin, checked with a planted `origin` that records any contact); the authority file is not written by any command (`patch_releases` is changed only by a commit of the owner''s decision). Fails if any tag of a bigger release appears without the owner''s typed code, a remote is contacted, or the authority file changes in a run. Verify: the W2-16 owner-terminal cases stay green; the planted `origin` and the authority file compared before and after a full cut and re-pin. [RELEASE-ON-BEHALF K5; DEC-772]'\nnon_goals:\n- 'Slice (b): the automatic update (`gov update --auto`, the quiet point, the lock, the hold records, the update''s check after and its morning-brief line, W2-207''s pass); its KPI lines (K7 to K10) are added when W2-207 allows (DEC-1224 (3)).'\n",
      "chunk_id": "716a954bf5da8aebfdbc610e",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "50bd6cf3cca034cc0931ba2e",
      "sha256": "809a9f4d3faa0e418f6380a442f1bb6d523bfaac2beb729d97315cc022e36c47",
      "path": "src/gov/release/patch.py",
      "start_line": 1,
      "end_line": 23,
      "text": "\"\"\"The patch rule of a release (W2-209, RELEASE-ON-BEHALF \"What a patch release is\"; DEC-1223 RB-7).\n\nA release is a **patch release** when five rules hold, each read by code from the last release N to the release\ncommit C, never by judgement:\n\n- P1 version: ``pyproject.toml`` at C is N's version with only the last number raised and no pre-release part;\n- P2 owner's text: no path changed under ``docs/contract``, ``docs/charter`` or ``docs/emergency-2/EMERGENCY-2.md``;\n- P3 no feature: no ticket closed at C that was not closed at N, and every non-merge commit N..C that touches\n  ``src/gov`` or ``template`` carries a ``Fix:`` trailer with a ``Task:`` ticket closed at N, or ``Class: Q``, or\n  ``Class: C``;\n- P4 no new command: the command names the CLI knows are the same at N and at C;\n- P5 no new record kind: no file added to or removed from ``template/governance/kernel/schemas``.\n\nAnything else is a **bigger** release, which only the owner builds (``gov release``, DEC-772). ``evaluate`` reads git\nobjects only and writes nothing. A rule whose input cannot be read fails (it never passes).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport re\nimport subprocess\nimport tomllib\n",
      "chunk_id": "50bd6cf3cca034cc0931ba2e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "f06900c453f61873f983392d",
      "sha256": "f409aefbf2d2b0f041569b6504cac2cdf33268ce817f9fd61fca2590f3e41056",
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "start_line": 55,
      "end_line": 72,
      "text": "## What a patch release is\n\nLet N be the newest release tag whose record is in `docs/releases/`, and C the release's version commit (the commit that sets the version, as `1d4e6a875` did for 0.1.3). The release is a **patch release** when all five rules hold, each read by code from N to C. Anything else is a **bigger release**, and goes to the owner.\n\n| Rule | Reads | Fails when |\n|---|---|---|\n| P1 version | `pyproject.toml` at C | it is not N's version with only the last number raised, or has a pre-release part |\n| P2 owner's text | `git diff --name-only N C -- docs/contract docs/charter docs/emergency-2/EMERGENCY-2.md` | any path changed |\n| P3 no feature | `.tickets/*.md` at N and at C; the non-merge commits N..C that touch `src/gov` or `template` | a ticket is closed at C and was not at N; or such a commit carries neither `Fix:` (with a `Task:` ticket closed at N) nor `Class: Q` nor `Class: C` |\n| P4 no new command | the command names the CLI knows at N and at C | the sets differ |\n| P5 no new record kind | the files under `template/governance/kernel/schemas` | one added or removed |\n\nP2's third path and P5 are mine; you may drop them (RB-7). `Class:` alone cannot tell a feature from a fix: `F` is on 263 commits since `v0.1.2`, ticket merges and test-only commits alike. So P3 reads the ticket status and the `Fix:` trailer (which `gov queue` already uses for fixes, W2-201 X6), and uses `Class: Q` and `C` only for the CTO's direct work.\n\n**What it says today.** Run on `v0.1.3` to the head: P2 fails (320 paths under `docs/contract`, the Charter), P3 fails (15 tickets closed; 47 ticket commits touch code, none carries `Fix:`), P5 fails (`memory-audit.schema.json` added), P4 passes. So 0.1.4 is a bigger release in content, and stays yours. From then on a bigger release is a minor number (0.2.0); only fixes and chores move the last number.\n\nThe result is written as `docs/releases/<X>/kind.json` (each rule, pass or fail, the offending ticket, commit or path). `gov release <X> --patch --check` prints it and writes nothing.\n\n",
      "chunk_id": "f06900c453f61873f983392d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "0291b447165c6e9c1de0782f",
      "sha256": "336a32c27b59be93b6f2efd43c6697360eddfd38452d03497d1be150fdcd5896",
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "start_line": 129,
      "end_line": 141,
      "text": "     \"New since this page first went out: the patch rule refuses a 0.1.8 carrying RP-1 (P3: RP-1 sits under W2-209, still open), so it is a <b>bigger</b> release only you build; DEC-1235 (2)'s rule for approved bigger releases is not built (I-34). The bundle is bigger too.\",\n     \"Your own re-pin script never runs <code>doctor</code> and writes the registry entry itself, so I-31 cannot hit it. A 0.1.7 copy is ready: <code>docs/emergency-2/release-0.1.7/repin.sh</code>. It checks the tag and the record, uses the kept cut wheel (its sha256 equals the record's), reuses the installed 0.1.7 pin, switches the link, runs the help, launch, search and hook checks, rolls back by itself on a failure, commits the registry entry as yours, and refreshes the stores.\",\n     \"Meanwhile EXAMIN measures on the 0.1.7 pin through PATH.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Re-pin 0.1.7 by your hand now: in a plain terminal, <code>bash docs/emergency-2/release-0.1.7/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.7.log</code>\",\n      \"About 15 minutes of yours; no new release; 0.1.7 goes live; RP-1 rides the next release you build.\",\n      1\n     ],\n     [\n      \"b\",\n",
      "chunk_id": "0291b447165c6e9c1de0782f",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "c1a523e2135a7f3282569643",
      "sha256": "64a0aed20a21b6f2e3dcd58c9d30dc57d21c0d6ca30be7e77303ba0032a39381",
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "start_line": 120,
      "end_line": 129,
      "text": "  \"intro\": \"What it takes to put 0.1.7's content live on the machine, and the release suite's flakes.\",\n  \"qs\": [\n   {\n    \"id\": \"D-01\",\n    \"from\": \"I-31 \u00b7 DEC-1248, DEC-1250\",\n    \"title\": \"Putting 0.1.7 live on the machine: your re-pin by hand, or a release you build\",\n    \"found\": [\n     \"0.1.6 and 0.1.7 were both cut (records and tags exist); both automatic re-pins rolled back on <code>gov doctor</code>'s <code>tools</code> part.\",\n     \"Cause (I-31, corrected): <code>tool-registry.yaml:236</code> pins the tool <code>gov</code> at 0.1.5, and the automatic re-pin never wrote the new entry before its check. The fix (RP-1, W2-209) is landed (<code>81cdd48b4</code>).\",\n     \"New since this page first went out: the patch rule refuses a 0.1.8 carrying RP-1 (P3: RP-1 sits under W2-209, still open), so it is a <b>bigger</b> release only you build; DEC-1235 (2)'s rule for approved bigger releases is not built (I-34). The bundle is bigger too.\",\n",
      "chunk_id": "c1a523e2135a7f3282569643",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "b866b1c7a01c212d7d9dd8a8",
      "sha256": "65d6f2378137d932fffa3f3412047fecb9a5a46937b62df43625abe4219ec2ab",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 151,
      "end_line": 157,
      "text": "| 1234 | a capacity assessment when W2-207 lands | \u2013 | N | `capacity_sampler.py` (scratch) collects; the assessment waits | `e2/w2-207-runtime` | \u2013 |\n| 1235 (1) | nothing ahead of 0.1.5; push the moment it is green | \u2013 | H\\* | \u2013 | \u2013 | \u2013 |\n| 1235 (2) | after 0.1.5 the CTO cuts every release whose content the owner approved; the release rule names the owner's approving decision | release on behalf | N | `release/patch.py` P2 and P3 refuse any feature or Contract change (patch only); the change is a fix under W2-209 after 0.1.5 | \u2013 | A-13 |\n| 1235 (3) | decisions by page | the owner answers by page | N | proposal only | \u2013 | \u00a73 below |\n| 1235 (4) | the week's usage explained | \u2013 | H | `usage-breakdown-2026-11-22.md` | \u2013 | \u2013 |\n| 1236 (1) | decisions by page DB-1 to DB-5 | \u2013 | N | feature in two slices, the release after 0.1.5 | \u2013 | \u00a73 |\n| 1236 (2) | leads at medium effort | rubric | P\\* | `start_lead.sh:3` `EFFORT=${EFFORT:-medium}`. **In the product, `launcher.py:176-177, 766` refuses `--effort medium` where the table says high** (the floor, DEC-1120 (3)) | F14 (015a, no branch) | \u00a72 below |\n",
      "chunk_id": "b866b1c7a01c212d7d9dd8a8",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "8a21beebdb491efcfade2a82",
      "sha256": "21cc7abd4f3a8f7f8996424850bb3f7e38a42ad7d8c734f7e9fe34c03859d7ee",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 392,
      "end_line": 398,
      "text": "### SQ-7: Rubric P1.10 says a release and a re-pin are the owner's own hand; DEC-1235 (2) and golden rule 8 say the CTO cuts a release whose content he approved\n- **Found:** `T2-ESCALATION-RUBRIC.md` \u00a72 item 10 (\"a release, a re-pin, a push, sudo\u2026 your own hand\") was approved in DEC-1219 (2); DEC-1235 (2) changed releases (EMERGENCY-2 2.5, 8.3) after it; the T2 file and `CLAUDE.md:9`, the kit head and `judging-work:23-24` still say \"owner's\"; golden rule 8 lists \"a release whose content he has not approved\" under P1.\n- **Options:** (a) amend T2 \u00a72 item 10 to the golden rule's form, and the kit text with it (cost: a kernel-text change, the CTO's, plus the owner's yes to the rewording); (b) leave T2 and read the golden rule as overriding (cost: two rubrics in force, one in the code design).\n- **Recommendation:** (a), in the same kernel sweep as N-25. Confidence: high.\n- **Sources:** `T2-ESCALATION-RUBRIC.md` \u00a72; DEC-1235 (2); `GOLDEN-WORKFLOW.md` rule 8; audit 4 \u00a71.7 \"Contradictions\".\n- **Stops work:** no.\n\n",
      "chunk_id": "8a21beebdb491efcfade2a82",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ec21869454609bf741ce5f8c",
      "sha256": "7190ce0478f52e8b212fd20d3d9c91685a70f3bce704b2573cfbd00f0ab5ce76",
      "path": "docs/emergency-2/integration/ANSWERS-B-2026-11-25-cto.txt",
      "start_line": 1,
      "end_line": 15,
      "text": "GOV-ANSWERS 1\nbatch: B-2026-11-25-cto\nhash: sha256:28e6ddabf3aab90e676d1008326acfee640b3bbc18f0bee5fb16f1c379457628\nanswered: 2026-11-25T21:55:15Z\ncount: 8\nD-01: a | note: Then make releases by code again: build the rule for approved bigger releases (I-34), and settle W2-209 so a fix like RP-1 can ride a patch.\nD-03: a | note: Use (b) to carry the next release until (a) lands.\nD-02: a | note: Give me the exact command line to paste.\nD-04: a | note: And a fresh CTO session every morning (rule 10), once I approve the handover method.\nD-05: a\nD-06: b\nD-07: a\nD-08: a\nEND\nThe owner, with the sheet: \"D-06 (b) means: every recommendation on the practice-first page, all 31 cards, including gov findings collect and the one pass classing the 162 older decisions. For D-01: tell me when to run the 0.1.7 re-pin, and commit nothing while it runs.\"\n",
      "chunk_id": "ec21869454609bf741ce5f8c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "28fc95c687864b164f9bee37",
      "sha256": "fcdc183832b3b8a9fc9b9bcc0c194ed613b02162165539003992f6545f846505",
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "start_line": 8,
      "end_line": 11,
      "text": "## What (a K-line RP-1 in the `## Fix:` section of `.tickets/DAEO-a2h5.md`; the CTO approves it by this brief)\n- **RP-1** The automatic re-pin writes the new pin's `gov` entry in the tool registry (version, sha256 of the release wheel, the install and uninstall lines in the form of the 0.1.5 entry, the date, the approving decision) before its post-pin checks, so `gov doctor`'s `tools` part reads the new gov as pinned; it commits that entry with the re-pin's record (as the owner's re-pin did), and a rollback restores the previous entry and commits nothing (or reverts it). Prove it on a planted machine (a temporary HOME, a planted registry and two planted pins): the switch passes the doctor check with the entry written, and a planted genuine tool mismatch still rolls back. Failing test first (the test designer), then the engineer.\n- Say whether anything else the post-pin checks read is pinned to the old release in the same way (hooks, the facts file, the role table), and fix any you find under RP-1.\n\n",
      "chunk_id": "28fc95c687864b164f9bee37",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "b833bf67dcb46c910cf5887b60a63a9dd1f18d2255140e74f9e3321d3e766852",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 92,
      "end_line": 105,
      "text": "## Interface (the test designer fixes the remaining names in the acceptance README; the engineer follows them)\n\n- `gov release <X> --patch --check`, `gov release <X> --patch [--suite <file>] [--kept <run folder>] [--push <cmd>]`, run\n  from the repository root, `GOV_ROLE=orchestrator`. Errors: `RELEASE_REFUSED` with details `gate` (`G0` to `G4`), `rule`\n  (`P1` to `P5`, for G1) and `reason`. `--check` answers `kind: patch` with exit 0, and the refusal `RELEASE_REFUSED`\n  (exit as other refusals) with details `kind: bigger`, the rules and the failed ones, for a bigger range.\n- The seams, beside the real functions: `release._patch_test(root, version, *, suite=None, rehearse=None, repin=None,\n  push=None, caller=...)` for the cut with G3, the re-pin and the push stood in; `proving.rehearse(root, commit, version,\n  kept, run=None, judge=None)`; `repin.repin(repo, version, home, *, push=None, check=None)` (home is the scratch\n  `$HOME`); `repin.burned(home)`.\n- Files: `<home>/.local/share/gov-os/{repin.json, rollback.sh, burned, pin-<C>, wheels/<C>/}`, `<home>/.local/bin/gov`;\n  `docs/releases/<X>/{manifest.json, manifest.sha256, kind.json, gates.json, suite.json, NOTE.md}`.\n- The authority file: `patch_releases: off|on`, `decision: DEC-1223`, `bake_hours: 4`.\n\n",
      "chunk_id": "f15d0eb706cf5326e0e09ce7",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "efa44597b8fc1d5db1b7786c6af28119ad8ceecc9799dad169a7e5494b8994d5",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 83,
      "end_line": 91,
      "text": "## Approach\n\nAll new code in `src/gov/release/`: `patch.py` (P1 to P5, `kind.json`), `gates.py` (G0 to G4, `GateRefused` with the gate\nnamed), `proving.py` (G3), `repin.py` (the general re-pin, `rollback.sh`, `burned`, the push text, `NOTE.md`), the cut in\n`src/gov/release/__init__.py` (`build` is reused, never loosened) and `command.py` (the flags `--patch`, `--check`,\n`--suite`, `--kept`, `--push`; no new command, DEC-1217). The CLI path never passes a stand-in: the seams are test\nfunctions beside the real ones, as `_release_test` is (an agent cannot pass a gate by a flag). `gov.close.nightly`\ngains `--optin`. `governance/project/release-authority.yaml` is committed with `patch_releases: off`.\n\n",
      "chunk_id": "ea4aa3333481b8a2efdd0e83",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "648d88b77bf90615c9b6f2b494646ce5be16822559dc3ed942d028e18f81638e",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 1,
      "end_line": 34,
      "text": "---\nid: DAEO-a2h5\nstatus: in_progress\ndeps: [DAEO-49o5, DAEO-sdhj]\nlinks: [DAEO-sdhj, DAEO-49o5, DAEO-k1us]\ncreated: 2026-11-20T15:30:00Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-209\ntags: [release, repin, patch-release, emergency-2]\nwbs_id: W2-209\ntitle: \"Releasing on the owner's behalf, slice (a), the patch release: the patch rule, the five gates, gov release --patch, the general re-pin with its rollback and the burned mark, the pushes and NOTE.md, the nightly's weekly-tier option, the authority file (off)\"\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on:\n- DAEO-49o5\n- DAEO-sdhj\nwaits_on: []\nallowed_paths:\n- src/gov/release/**\n- src/gov/close/nightly.py\n- src/gov/update/pending.py\n- governance/project/release-authority.yaml\n- docs/plan/wave-2/w2-209-rehearsal/**\n- tests/unit/release/**\n- tests/unit/close/**\n- tests/unit/update/**\n- tests/acceptance/W2-209/**\nest_loc: 600\nkpis:\n  success:\n",
      "chunk_id": "675efcdfebb9fe058528f043",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "7469ecdb23b023825bfede2d2c8742bc9dd4142be8c394fbdc06ee416b68342a",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 64,
      "end_line": 75,
      "text": "# W2-209: releasing on the owner's behalf, slice (a), the patch release\n\nA new feature (the owner, DEC-1223 and DEC-1224 (3); DEC-1219 (6): a new ticket only for a new feature; RB-6 (a)). The\nspec is `docs/emergency-2/proposals/RELEASE-ON-BEHALF.md` (approved, DEC-1223); this ticket is **slice (a)** of it:\n\"the patch rule, the gates, `gov release --patch`, the general re-pin with its rollback, and the push\". Slice (b), the\nautomatic update, is a later slice of the same ticket; its KPI lines are added when W2-207 allows (DEC-1224 (3)). The\nticket extends W2-16 (release) and W2-17 (update) and replaces neither; both stay closed. `src/gov/release/**` and\n`src/gov/close/**` are C3: the test designer runs Opus, the engineer Sonnet (the C3 trial, DEC-1222 (2)).\n\nThe K lines of the design map here: K1 to S1 and S2, K2 to S5, S6 and F1, K3 to S4 and F3, K4 to S9 and F4, K5 to S3, S7,\nF2 and F5, K6 to S10. K7 to K10 are slice (b) and the two W2-17 fixes (landed).\n\n",
      "chunk_id": "e854055689abe37eb0b03894",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "3696072903e71aa8f40dff919a9f49a60758ef8f7b7c8bafa67fe28a4de68502",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 36,
      "end_line": 36,
      "text": "  - 'S2 The result is written as the release''s `docs/releases/<X>/kind.json` at the cut, in the form `{\"version\", \"kind\", \"from\", \"commit\", \"rules\": {\"P1\": {\"pass\", \"detail\"}, ...}}`; `gov.update.pending` and `gov doctor`''s part `updates` (W2-17) read its `kind` key and need nothing else. Verify: a cut in the planted repository (S8) writes the file; a planted release record carrying it makes `gov.update.pending.pending` answer kind `patch`, and one carrying `bigger` answers `bigger`. [DEC-1224 (3); DAEO-sdhj S5]'\n",
      "chunk_id": "21782acc14e165f1c5cdef35",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "2dc6c7df123866061abc2fc969c77764f35192c247af109446f62098f0c5004f",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 128,
      "end_line": 142,
      "text": "## Fix: the automatic re-pin writes gov's tool-registry entry before its post-pin checks (RP-1; I-31 corrected; the CTO's brief of 2026-11-25)\n\nFound 2026-11-25: `gov release <v> --patch` cut 0.1.6 and 0.1.7 and each re-pin rolled back (`newly unhealthy: tools`):\n`repin.py` wrote and committed the `gov` entry of `governance/project/tool-registry.yaml` (step E) only after the post-pin\nchecks passed, so `gov doctor`'s `tools` part found the new gov against the entry still pinning 0.1.5. The owner's manual\nre-pin of 0.1.5 (`8346b9a30`) wrote that entry itself, so it passed.\n\n- **RP-1** The re-pin writes the new pin's `gov` entry (version, sha256 of the release wheel, install and uninstall lines in\n  the form of the 0.1.5 entry, date, approving decision) into the repository's `tool-registry.yaml` after the switch and\n  before the post-pin checks, so `gov doctor`'s `tools` part reads the new gov as pinned; on a pass the entry is committed\n  with the re-pin's record (`Role: orchestrator`, `Decided-by: owner (standing, <decision>)`); on any failing check, a failed\n  commit or an error the file is restored to its previous bytes and nothing is committed. Verify: on a planted machine (a\n  temporary HOME, a planted registry, two planted pins) the switch passes the doctor check with the entry written, the\n  registry commit holds the entry, and a planted genuine tool mismatch (another tool's entry) still rolls back with the\n  registry file byte-equal to before and HEAD unchanged. Failing test first (`tests/acceptance/W2-209/test_w2_209_rp1.py`).\n",
      "chunk_id": "e0683c56a8f08c211ee83d15",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "342ec2ae10b15c1e3b68be164b7d147c1051e2db97b364e2dd1a835d7f154ae2",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 46,
      "end_line": 48,
      "text": "  failure:\n  - 'F1 No release record, tag, pin or link change after any gate is red, missing or stale: for each of G0 to G4, one planted red, missing or stale input makes `gov release <X> --patch` exit non-zero with the gate named, and the record folder, the tags, the branches, the pin folders and the link are byte for byte as before (compared before and after). Fails if a record, a tag, a commit or a pin appears after a red gate, or the answer names no gate. Verify: the planted repository with the full tree compared before and after for each gate. [RELEASE-ON-BEHALF K2]'\n  - 'F2 A release the rule calls bigger is never cut: with any one of the planted changes of S1 in the range, the cut is refused at G1 naming the rule, whatever the other gates say (every other gate planted green), and with the authority file `off` it is refused at G0 for the same range. Fails if a patch release is cut with a Contract, Charter or EMERGENCY-2 change, a closed feature ticket, a new command or a kit schema added or removed in range, or a commit that has none of the allowed trailers. Verify: the cut with each planted change and every other gate green. [RELEASE-ON-BEHALF K1, K5]'\n",
      "chunk_id": "7cc063e64d3c3d569e32358e",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "d4eb2b5dc5994aaae38c96d1",
      "sha256": "b8202cf8e698b9e0ce9ea48a44e8859985e537d52e18ee2852b5fb817ae0eead",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 399,
      "end_line": 406,
      "text": "### SQ-8: What is `Class: Q` in the patch rule?\n- **Found:** `release/patch.py:10, 169, 246` accepts `Class: Q` and `Class: C` beside a `Fix:` trailer as a non-feature, but no document defines Q (RELEASE-ON-BEHALF names `F`, `Q`, `C` in passing: \"F is on 263 commits\").\n- **Options:** (a) define Q as \"a quick fix with no owning ticket\" and make it a chore (cost: none, it is already a chore under the rubric); (b) drop Q and require `Fix:` or `Class: C` (cost: a patch of old commits fails); (c) leave it undefined.\n- **Recommendation:** (b) once SQ-1 settles the chore definition. Confidence: low (the definition of Q may exist in a commit message I did not read).\n- **Sources:** `release/patch.py:10, 162-169, 237-246`; `RELEASE-ON-BEHALF.md:63-69`.\n- **Stops work:** no.\n\n**Stoppers: none.** Nothing found stops 0.1.5 or the step three plan; SQ-4 and SQ-6 should be answered before F14 and the decisions-by-page ticket's spec are filled.\n",
      "chunk_id": "d4eb2b5dc5994aaae38c96d1",
      "routes": [
        "semantic"
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
    "duplicates": 50,
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
      "chunk_id": "f06900c453f61873f983392d",
      "parent_id": "65a9e4edffaeadf7cd7672d0",
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "start_line": 55,
      "end_line": 72
    },
    {
      "chunk_id": "f15d0eb706cf5326e0e09ce7",
      "parent_id": "cd34e23d6667f3608ce207d1",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 92,
      "end_line": 105
    },
    {
      "chunk_id": "e0683c56a8f08c211ee83d15",
      "parent_id": "5b3861ab141c88fef5c468be",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 128,
      "end_line": 142
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "DAEO-057v",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0mab",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-b926",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-g0ip",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-h4rh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ha8z",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kmcr",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kt8e",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-nn1s",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-rpfv",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "464529ee331d8da1a4f92002",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "904263f6486ac037752b80db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "7e351db18fa76005fa8f3c4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "bf1d36d1ff6840de51c587b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "faefec5ab700bf0e5ffb7c72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/__init__.py",
      "chunk_id": "2d53ebc206d32c7fa170b631",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "688288fc3880be6904dad8fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "beab1afa4e0cc77c57269446",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "591a7290798003ac1b405b81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "42227fc1e0e087d6460f5458",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/command.py",
      "chunk_id": "6146d37d041796ff9109f467",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "411fad9acacee52dbff7817d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "c5eab5220fc9b3676b0a8f6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "fcc72bc41c3607f4f36cbbfa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "af02008b167b9ebf530283e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "3c01efe502dcba97ad55c9a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/command.py",
      "chunk_id": "c84ff7b5f4ae0b58e9b23eff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "5bec9d5056548dee69c240d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "75c90c746a7ce37e666c58cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "114c461d4a542d5ac2ecee01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "ee0fa7abc9a24be4a3593c07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/command.py",
      "chunk_id": "5feb072a7d4239634274c294",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "f54741930d20853052e6d7c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "a8f6d781f1696577c1188880",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "c1eea98a7eb390978bee9ae5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "90092e47293f0650c598f675",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/command.py",
      "chunk_id": "8cd2d220179cf600e1aa7521",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "3a897b078c4448c5307edc21",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "1180baf27d8f36e2d4c21ec7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "6d3510272710313e33965dd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/rerank_service.py",
      "chunk_id": "24110f0ac3f182cefae3e4ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "7ca07bca84761079d14b2510",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "5cce15743faf0877077a33ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/command.py",
      "chunk_id": "611975077d12eabec4039050",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "76369390b064ca0ee9b4085b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "9bd0d4387487a0e89b37fac2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "cfe7f7b8811acf669a762ec6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "dd9e492740567a1388bcc0f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "18d104769f127fefe82d4e16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "9bc40d2cf2607ad2184597b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/REHEARSAL.md",
      "chunk_id": "49a1729c0970ea1c12ad78f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "4067665e11e8015dba5ed1fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/tasks/claims.py",
      "chunk_id": "e398f89fffe58d930dd8b460",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "27808e5f8cca7606583e025e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "365df54baba14ba904103504",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "fd84a9769b15301785428821",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "d6567b9c995e6b72b240fac6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "f6c7036650c494a76b6f1701",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "ca9988b377946dc81de04c84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "24f63b0a22e1cb173e3ad8e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "69fa41850853e23fb0ff92ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/command.py",
      "chunk_id": "c9155d60fceac02e2d4813e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "chunk_id": "534664021f54a94d464458ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f72583b4da4f3249d6d93cc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "4426ffbf35b682fd716aeafe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "79d16e81828ee13063c1a447",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "9183a1b039df4cedfad56b97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "9883ec5a63f37e7d3560fa2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "2906e7538f90b3b7b4b9b168",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/pause/command.py",
      "chunk_id": "e65c34a102510a4b0f2a4f11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e37a0b68a40c71c2f54a50ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "5b9084daf410c16f152644fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/rerank_service.py",
      "chunk_id": "64ce1e2a1f24adf7545c0e24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/REHEARSAL.md",
      "chunk_id": "0846a0a506e5aa23d523db16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "02f38b7bb0a1220f26795588",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "1ce900930a9cff3cce5332d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "5f7be2dae704b375063dfa6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "806fdbff8e0bcc21ba86a8a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.c.md",
      "chunk_id": "034c8a63eedb66b845b9c47c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "8caf826a9486feae07693018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "fa117f08c00e8defc5a846a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "e8d3d9743b3832978e519dc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-02.c.md",
      "chunk_id": "e3a2226614b4e97e94055785",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "ef203f715df3114d11a5a6fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-02.c.md",
      "chunk_id": "a7869efeebcb0c078a6384ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.md",
      "chunk_id": "bf01deaf748b88f164835c70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "5d1ca236f7234e630984da94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/tasks/claims.py",
      "chunk_id": "723c8ac18af21dd1eb087575",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "b23bb268ca9cb837c62307d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.md",
      "chunk_id": "0ca1516d96c74aee2507717c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "704f4acef8085556c398945c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.b.md",
      "chunk_id": "50f65616da68125631acb1ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.b.md",
      "chunk_id": "762df4427e42067ab45664c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/release-authority.yaml",
      "chunk_id": "a9087a13bf8ae56bbd2f2a81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "606b078f7ff14ef497f4b9ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/charter/CHARTER_v6.md",
      "chunk_id": "6549cd06cf4753c7eca9bb68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "08a284e1904a83866bea5bb0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/cli/errors.py",
      "chunk_id": "2fab0638d1a25bdfddbe8b36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "ae9443084a287a548823b3c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "f22fa199d139728506da0237",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "116a9bd92e2127aa8789eecf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/cli/errors.py",
      "chunk_id": "2ee0ef097deb52488e914a86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "52e91b4e0a29fdd985cdd09a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "99f6ee8f5301e6fbfe0a0e91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "46fceeb40f98e5bccf1f6794",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "f7a19a0a8efab0be6ec98a2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "753dea6d9d52d1f1bcbf3c30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "8ab8b875dd392b4497f5d7cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/dispatch/balancer.py",
      "chunk_id": "d61c9c5a0589f6e78d7cfd79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "9d4be6f0f20e8ad96fff16d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/tasks/claims.py",
      "chunk_id": "cf2fb941099a8bd02f833f6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "61735a19f499c64d4962f084",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/layout.py",
      "chunk_id": "d060b469a5fc07411ccce37d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/test_w2_209_rp1.py",
      "chunk_id": "858fe2445f5b7adbf3404da9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "31fb9141e20deead83928f8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "4942bf3e57fa37f24bc72210",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "52040e39f4874a711595f891",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "9a1ccd2787a59bed485bf840",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d922fb7824eb5e5166663467",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "11e94af0a591dfc5863ee083",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "d88e1472dee2be26299e37da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "6c2bae0a25cdc663c0c55f99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "73cac540990444cb479643be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "595d8795e17af7130158d6b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e8950a8c24a066f172087c9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9b0ebfe72ee53d6ed08dd309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "0c2d3bea847aba40be3d4127",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "30bd9b74e9c6cf279ec9a473",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "197c213909e7a67669a2730c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "79a3b3630be3d83065db679a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ff6fbdb63b14a9be55c93082",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cf99cd773ecf6cf6e1ed0830",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "9e75ebe87831dee3725120cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6a9dee6e838a6b4ead5fa878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "75912f657554f6ccbbcd6dc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/test_w2_209_authority.py",
      "chunk_id": "9d289422cd0d1aef3e7120c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "00c0f6e9432037c075b2caab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "5620b67a6c6cc2eba591c209",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ccd2f7a9ecfe2fee02880502",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "17b3e20e8a3f79a9abb62207",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/patch.py",
      "chunk_id": "defcc79eef19e2176c8a8e13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "86ea8a181a25a7895649e41a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "19d2aedb81bc8e0748f94400",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "1f0365fbdaf6fe263cab52d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "d796afda5c3a0444f1166df1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "521b56c8695d9acde5e29163",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "72eb71313070586fa223d0a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "9a91b1c1728374221f9e6568",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "19f49b00a88a8f0fb42c62e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "013aea19af229d7674a7dd90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "ab9771642ca766903198d8b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "975f8e076948ebe4c3587bd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "65c283bcd2b3019e32b836f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "da95153b81e9843b4be1848e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "ace58381a586b5bdffce5be8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "fb679667ef03ffe0bd5d1368",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "a38b59da867ec95e73ab5242",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "a71973ff578f06807b16230c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2ba24528da4b2f9d4dd537f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "0666e62db410e736fc7cdb2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/rehearse.py",
      "chunk_id": "1c35a1c829168647e6e671e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f6e1281369f69cb2610c7ecc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "95d54152233c480b4e89101b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "bb0a0494038dee153ad01617",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "eed7a7f8e651d444ece99d31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "5837412cd26aa8ee9c189e9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "0de09af609d4567ed69086ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "57d19219d2986abddf9ac9f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/STEPS.md",
      "chunk_id": "5c492ae67b0cacece89c46e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "82497daab714537dccd10313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "21c3b617cf9381b643b36313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "c54d2c06ee954a88f5147938",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "e8545b24e888085bf271bf5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "83850893cc262225a7df4a02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "79b7aee9706b1ef29de0931e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "bb0cad643373c29e65688775",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "be1d8a59c79892aaf1db4bac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "702622ead12f4fea80275cc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "1839ab757b7d3418b9607cbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "9b0916c16871115cf16ff614",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "1708afd60aaaed2c929e9710",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1bf642f128c3a3738d7c2db2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "d7824e1d7e7c00703c9d198c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "69225e84725cebdeaf8fdb13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e907addc279069820b67d534",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "3c8ce200d91a3e56ccd7d750",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "c4a1b0753bb0adc84280c977",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "50c846d8a96b49522f1f29b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7627761395e44046a981467a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "d084c1548fcbfae916c6df12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/pending.py",
      "chunk_id": "2cb735583c55dc14fce4e9d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "3438f4bd6b4650515a1fc178",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015b.md",
      "chunk_id": "db74c33232eca63a0eceb7ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "ceddcce85c7b7b383e5dd147",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "547e916d3689e7b443ca0da5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "67035189e50697aa8a0b7a29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "115d634d7725938669caf9f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-11-02.md",
      "chunk_id": "a77d9160a481f18e7757138b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "22773e524fb237a672953390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "d30e078c8c527be4f02531dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "c83bb3e628194633332fd94a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/EMERGENCY-2.md",
      "chunk_id": "e61a66545d87e2d921af7fbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6a46eeccf9563eae98a04efb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "c441b1ddc9f3c25e7ce9e6f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "94049821b8d30b65cc014973",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_rg_driver.py",
      "chunk_id": "eb81454e000f213274ce3b2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4f91669cddb962309aaded40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/nightly.py",
      "chunk_id": "116befc6c57f5124bc6cc32a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-fu3n.md",
      "chunk_id": "858090f58e77bf9df3a75e6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/EMERGENCY-2.md",
      "chunk_id": "d1e2bea80d072938c080c14c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "f269b49d897f8b77354681c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "320db0ca38365e2e330681a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "20b137c4796e0acf02694159",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/EMERGENCY-2.md",
      "chunk_id": "0d2f45cd4724d270a5eae2ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "8a6e46f4154e615748350033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-COMMON.md",
      "chunk_id": "a684d3e3fe8ca85e7d9957fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8b3b2cb98b771b71cb142165",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "05ac76a01d53e8bf1383330d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/__init__.py",
      "chunk_id": "6f6b25838fd7a59ca8a654f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "34f9f0257038ff605d6ef64a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "5c7817551da9b5a24b484e76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/STEPS.md",
      "chunk_id": "110e7afb74d52807825219f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "b65eb3195c1e050011d7866e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_driver.py",
      "chunk_id": "514178d6922423b1dd70cd0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "bb82f321c622726043eadeee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9f78a531a985c7c40ff3b892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "c366d10eae340b4e13b00a98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "7577b800fd3d8c81e4c4de68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "4544debf12383346c0acf0da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e3f050f7c7f6d3f33560cf2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/test_w2_209_nightly.py",
      "chunk_id": "2da4ceb1d06e5c4d8c2e6aa9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "2fa48d6bb7e011d5cc5200d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "c4a13d20bc3cebbe644871e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1879d875a44a02135a1da4b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "53a9a28610162f9f0418ddba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "f559b0d55e39366b316b68ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "372f9343cbf4a4fe8995d452",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "9bccaf7f817954c2d551f5f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cc22f8ec310fe1d07afc7ff9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "ae02a78287148d71db59f621",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6f9b535ccb4346d30ddb02eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "chunk_id": "3afec7806cf2fc33ab0f5d7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_standins.py",
      "chunk_id": "0933a3d0dad9fb6e17c137a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "9cfbfdaa02fc1d33ed603b42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "0c2963d25c3bd54f72a47e3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015b.md",
      "chunk_id": "0410037a176231e4dab8fe8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "f53872190ee70350ce2a26f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "21fd351fef32c4fe4d0a723f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "744ecdc3f75115cda64605bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "647c32a2ef48f7687a64caf9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015b.md",
      "chunk_id": "90c06584132aec6c60174c0b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/nightly.py",
      "chunk_id": "9873e7bb68bfe4c0b1d9c0d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "baf719bf85e3e0360ca1d462",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/pending.py",
      "chunk_id": "4a4766ad52c0a0acc0954d4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "55ed978831ba3411df0d74ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "083cde2866aa8f2db93b2222",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "69a8d765659806f8b6e9e720",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/gates.py",
      "chunk_id": "ab07c58b9b6ecb654ac2ac62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "ab0c83d9437860c71140384c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/test_w2_209_remote.py",
      "chunk_id": "63236f3fa8b2b24c15cedcaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "ab037a4bb63ce3708f483188",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/nightly.py",
      "chunk_id": "89441ed984928defd72a9c4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/cut.py",
      "chunk_id": "a3fa0d33bfc840a92a573f94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "08c3a6ab1bb6dbed0868b515",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "12f15e0f67508902ca324b7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "cbcba0cedb99e85575e5b7bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "1836698ab582a3276c8cad72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "af0d2d63353babfeda2edd56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "9193bcefcb729afa083b197f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/proving.py",
      "chunk_id": "f1e8440f8a7b1a959d043829",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "407a032f6d0c133d3f2ec47c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "1d54d4f0c80723fbde7452b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/repin.py",
      "chunk_id": "2722cdee410480eadf4e8f81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "c32b0a05a84f20f298cd3519",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "4d71c4aed654a12b076fe703",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "4fa133624ea2591fb972fe87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "4e36798cfa2caf8693170906",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/conftest.py",
      "chunk_id": "eb3527f7c96cfd6f117e4df3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "3f0521e85bffc04663a6d326",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/repin.sh",
      "chunk_id": "6350e9c4e46d76f009898705",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-015a-fallout.md",
      "chunk_id": "3e99e9879f7f97aa1943d2b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "27202fce017348c1350aacc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "a1369156084a82117ff0f1ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "286d7b21b199d34c5fc01f80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.7/repin.sh",
      "chunk_id": "596a5afcd4c01a01c3f7a4b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "addb11de450f0004ac80eec1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "d907cbbec9206dabbdb60738",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "ad57692f6058cad6f81b4ceb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/STEPS.md",
      "chunk_id": "a26cced7486894fe263f6519",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "baab709dfa75efe08c08c6bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "a85eb6c77e5b71c155532e1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/test_w2_209_regression.py",
      "chunk_id": "154c8181719c28d796378f2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/memory-measure-new-visible.md",
      "chunk_id": "2dae25c3e2c55fec543d2f22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/REHEARSAL.md",
      "chunk_id": "878da78beb2fb289000f11df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/rehearse.py",
      "chunk_id": "87b744cc987ddcf585060d8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-77/w2_77_support.py",
      "chunk_id": "0f7a8fcaa5cdf2b2418e1373",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "a49d05b33c4ac5cb5b5310db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/results.json",
      "chunk_id": "bdb365892cb7a56e8dbfee82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_support.py",
      "chunk_id": "5826dba38a1d312b65d366c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "de4528c3f23c0b44cdb26438",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "ea7a19b96ba508cec815c8c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "69b809bc63880526463dc410",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/w2_209_rg_standins.py",
      "chunk_id": "2e4c3a4a1573cbc4f774da10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "2161cb2c3b193f10d873d2cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "0622cb11d9e713c2a28303f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "d1d28ab1a6036dd902509d78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "0e1a0c62aa3efae3f6a0d6da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "337142d67ac7ebd3bff84640",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "66b63050af6439f52024a13d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/results.json",
      "chunk_id": "79eedbced469b3a3671e02dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "50d9590c2b1b7d66fc4d5683",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "ac3c10e83e0c8344172e86ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "4fad9125035369d26812cfd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "fe143d09afa4b08b08f8409c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "228dedc732d546291ca9caba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "a06231d0094e918eac330784",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "34adc2836135f84328cac5a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "4201d30a216d5ac0bcc21812",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "6babacf96d1ceab83e950a74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "f73ef7153d58c01a0f3fc920",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "f23cadcb636357f376e42210",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/REHEARSAL.md",
      "chunk_id": "8e3e53f64ff7eb272f3f6045",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "2090195887c54cdc447c963f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "b3df0533e3a8dfe5252d7e5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "80b047e6d35b244e34459a83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/REHEARSAL.md",
      "chunk_id": "0ec9c6ecb5ae18f83723dcda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/release/test_burned_pending.py",
      "chunk_id": "1cbeee451ff8604d9b2a88c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "b5026f7e4e9c00a513d467b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "ceb6ffcc61fd27cfac61a1cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "73605d727eada536a5af2360",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "2e18f799917f7ed97af6122f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-77/w2_77_support.py",
      "chunk_id": "0be63f38b6896fc53a23ff55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "961a32216755dc042ab566c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "84ef1456b2d18eb5167c7116",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "96eac80a276d6d155832cc07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "a7d3b7376effb4a325c78cdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/REHEARSAL.md",
      "chunk_id": "b4a819bb6ffa786cb8a9acda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/close/test_nightly_optin.py",
      "chunk_id": "a7b50766884b2847b67e6136",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/release/test_patch_text_units.py",
      "chunk_id": "b7e2fd4b250753dc59a88c00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/release/test_proving_units.py",
      "chunk_id": "84da89892018bb80e839f3fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/release/test_gates_units.py",
      "chunk_id": "d0e84a13dec9b8407f50cd46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/test_w2_136_plan_output.py",
      "chunk_id": "1f71e5130a39dd0db5e45797",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "be58eb69862ecba89c067738",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "144fdea3bd2ad663418c997e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "e940edd235a1d80cfebef334",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "97979bc1b979c80f8182d01e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "87fa2c149c8a34648df954af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/test_w2_209_rule.py",
      "chunk_id": "6cebe10e23e5bc693a81fdf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "56368ff4447acd918625da4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "6fbb39fbd8e832cb19c3e81e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "ca9bd6a7e76b926de492b976",
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
          "DEC-772",
          "DEC-1220",
          "DEC-1222",
          "DEC-1223",
          "DEC-1224",
          "DEC-1226",
          "DEC-1232",
          "DEC-1225",
          "DEC-1238",
          "CAP-02.c",
          "CAP-43",
          "CAP-43.b"
        ],
        "left": 1
      },
      "changed_by": {
        "DEC-772": [
          "DEC-1223"
        ],
        "DEC-1222": [
          "DEC-1225",
          "DEC-1223"
        ],
        "DEC-1223": [
          "DEC-1235",
          "DEC-1224"
        ],
        "DEC-1225": [
          "DEC-1236"
        ],
        "DEC-1232": [
          "DEC-1238"
        ],
        "DEC-1238": [
          "DEC-1244",
          "DEC-1240",
          "DEC-1239"
        ]
      }
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5221
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLWEyaDUubWQiLDEsMzQsIjY3NWVmY2RmZWJiOWZlMDU4NTI4ZjA0MyJdLFsiLnRpY2tldHMvREFFTy1hMmg1Lm1kIiwyOCwzNCwiNGEwZDM4ODQwMGNlZTZlYTk0Y2ZhNjg2Il0sWyIudGlja2V0cy9EQUVPLWEyaDUubWQiLDM1LDM1LCI5ZTM2OGQ1OWZiYzE4YzBhY2I0Zjk3YTkiXSxbIi50aWNrZXRzL0RBRU8tYTJoNS5tZCIsMzYsMzYsIjIxNzgyYWNjMTRlMTY1ZjFjNWNkZWYzNSJdLFsiLnRpY2tldHMvREFFTy1hMmg1Lm1kIiw0Niw0OCwiN2NjMDYzZTY0ZDNjM2Q1NjllMzIzNThlIl0sWyIudGlja2V0cy9EQUVPLWEyaDUubWQiLDUxLDUzLCI3MTZhOTU0YmY1ZGE4YWViZmRiYzYxMGUiXSxbIi50aWNrZXRzL0RBRU8tYTJoNS5tZCIsNjQsNzUsImU4NTQwNTU2ODlhYmUzN2ViMGIwMzg5NCJdLFsiLnRpY2tldHMvREFFTy1hMmg1Lm1kIiw4Myw5MSwiZWE0YWEzMzMzNDgxYjhhMmVmZGQwZTgzIl0sWyIudGlja2V0cy9EQUVPLWEyaDUubWQiLDEwMiwxMDUsImVlNzllMTQ3M2ViMmViMWViNjJjOTdkYSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1maXgtcmVwaW4tcmVnaXN0cnkubWQiLDgsMTEsIjI4ZmM5NWM2ODc4NjRiMTY0ZjliZWUzNyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9BTlNXRVJTLUItMjAyNi0xMS0yNS1jdG8udHh0IiwxLDE1LCJlYzIxODY5NDU0NjA5YmY3NDFjZTVmOGMiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vREVDSVNJT05TLUhFTEQubWQiLDE1MSwxNTcsImI4NjZiMWM3YTAxYzIxMmQ3ZDlkZDhhOCJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9ERUNJU0lPTlMtSEVMRC5tZCIsMzkyLDM5OCwiOGEyMWJlZWJkYjQ5MWVmY2ZhZGUyYTgyIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0RFQ0lTSU9OUy1IRUxELm1kIiwzOTksNDA2LCJkNGViMmI1ZGM1OTk0YWFhZTM4Yzk2ZDEiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vR09WLU9TLURFQ0lTSU9OUy0yMDI2LTExLTI1Lmh0bWwiLDEyMCwxMjksImMxYTUyM2UyMTM1YTdmMzI4MjU2OTY0MyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9HT1YtT1MtREVDSVNJT05TLTIwMjYtMTEtMjUuaHRtbCIsMTI5LDE0MSwiMDI5MWI0NDcxNjVjNmU5YzFkZTA3ODJmIl0sWyJzcmMvZ292L3JlbGVhc2UvcGF0Y2gucHkiLDEsMjMsIjUwYmQ2Y2YzY2NhMDM0Y2MwOTMxYmEyZSJdXSwiZiI6Ii9ob21lL3VzYWluL0R5bmFtaWMtQWdlbnRpYy1FbmdpbmVlcmluZy1PUyIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiZDU5N2ViOTU3ZTViNTIwNCIsIm8iOlsxNywzMywzLDIsMjYsMTQsMTYsOCwxMCwzOSwzNyw1LDAsMSwxOCw5LDExLDMyLDI5LDcsMTMsMTUsMTIsMzYsMjgsMjEsNCwxOSwzOCwyNywzMSwzMCwyMywyNSwyNCw2LDM1LDM0LDIyLDIwXX0sInEiOiJ0aGUgcGF0Y2ggcmVsZWFzZSBydWxlIFAxIHRvIFA1IGluIHJlbGVhc2UvcGF0Y2gucHksIERFQy0xMjM1ICgyKSBhcHByb3ZlZCBiaWdnZXIgcmVsZWFzZXMgYnkgY29kZSwgVzItMjA5IHJlbGVhc2UgYXV0aG9yaXR5LCBSUC0xIHJlLXBpbiByZWdpc3RyeSBmaXgsIENsYXNzIFEiLCJyIjowLCJzIjoiYzFlODFhZmQzZTc1NjBlN2E4Zjc2OWJiNTFkZTA4M2IwN2Q3MjE1OCIsInQiOm51bGwsIngiOlsiNWIzODYxYWIxNDFjODhmZWY1YzQ2OGJlIiwiNjVhOWU0ZWRmZmFlYWRmN2NkNzY3MmQwIiwiY2QzNGUyM2Q2NjY3ZjM2MDhjZTIwN2QxIl19",
  "routing": {
    "code": [],
    "named": [
      "9e368d59fbc18c0acb4f97a9",
      "716a954bf5da8aebfdbc610e"
    ],
    "phrasings": [
      "the patch release rule P1 to P5 in release/patch.py, DEC-1235 (2) approved bigger releases by code, W2-209 release authority, RP-1 re-pin registry fix, Class Q",
      "patch release rule P1 P5 release/patch.py DEC-1235 2 approved bigger releases code W2-209 release authority RP-1 re-pin registry fix Class Q",
      "the patch release rule P1 to P5 in release/patch.py, DEC-1235 (2) approved bigger releases by code, W2-209 release authority, RP-1 re-pin registry fix, Class Q DAEO-a2h5"
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
        "chunk_id": "ee79e1473eb2eb1eb62c97da",
        "path": ".tickets/DAEO-a2h5.md",
        "start_line": 102,
        "end_line": 105
      },
      {
        "chunk_id": "4a0d388400cee6ea94cfa686",
        "path": ".tickets/DAEO-a2h5.md",
        "start_line": 28,
        "end_line": 34
      }
    ]
  }
}
