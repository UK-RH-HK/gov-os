{
  "ticket": "DAEO-ywb5",
  "ticket_text": "---\nid: DAEO-ywb5\nstatus: in_progress\ndeps: []\nlinks: [DAEO-ozyt, DAEO-weh2]\ncreated: 2026-11-12T08:52:00Z\ntype: task\npriority: 2\nassignee: independent-test-designer\nexternal-ref: W2-181\ntags: [wave-2, test-revision, resources, lite]\nwbs_id: W2-181\ntitle: 'W2-157''s F4 path case judges any branch against W2-157''s own paths: judged only on w2/W2-157, as W2-180 did for W2-170 and W2-173 (DECIDED-NOT-DONE row 171)'\nclass: test-revision\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\nprofile: LITE\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- tests/acceptance/W2-157/test_w2_157_nothing_else.py\n- tests/acceptance/W2-157/README.md\nest_loc: 15\nreads:\n- tests/acceptance/W2-170/test_w2_170_f5_paths.py\n- tests/acceptance/W2-173/test_w2_173_unchanged.py\nneeds:\n- tests/acceptance/W2-157/test_w2_157_nothing_else.py\nkpis:\n  success:\n  - 'S1 `test_f4_the_branch_changes_only_the_tickets_allowed_paths` judges only W2-157''s own branch: on any other branch, a candidate merge of the merge queue, w2/integrate or the nightly''s clone it is skipped with its reason (the branch found, or \"detached HEAD\"), never red; on `w2/W2-157` it judges as today. The same form as W2-180''s revision of W2-170''s F5. Verify: planted repositories: a branch named w2/W2-157 with a change outside W2-157''s paths fails it; the same change on a branch named w2/W2-121c and on a detached candidate merge skips it with the reason [DEC-866, DEC-253]'\n  failure:\n  - 'A change outside W2-157''s paths on W2-157''s own branch let through. Verify: S1''s planted w2/W2-157 branch fails the revised case'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the branch against its base lists only the allowed paths'\nnon_goals:\n- any other ticket's path case (W2-180 did W2-170's and W2-173's; new tickets are briefed to the own-branch form)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-866, DEC-253, DEC-966, DEC-989]\nacceptance_tests:\n  path: tests/acceptance/W2-157/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C1): the revision with a Rewrite-Reason (DEC-866)'\ntrack: B\n---\n# W2-181 W2-157's F4 case on other branches\n\nDECIDED-NOT-DONE row 171: a per-ticket path case that diffs any branch against its merge-base with w2/integrate and checks the\nresult against its own ticket's allowed_paths is red on the next ticket in the same area and on the merge queue's batches (W2-157\nitself was ejected at 07:46 in a batch with W2-121). W2-180 fixed W2-170's and W2-173's; this is the last one found on integrate\n(W2-157 closed 08:33). The next ticket in `src/gov/resources/` (W2-121c) would be red on it. Class C1.\n",
  "authority": [
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
      "id": "DEC-253",
      "sha256": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "reason": "declared in sources",
      "tokens": 202
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-989",
      "sha256": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "reason": "declared in sources",
      "tokens": 399
    }
  ],
  "mandatory": [
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
      "id": "DEC-253",
      "sha256": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "reason": "declared in sources",
      "tokens": 202
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-989",
      "sha256": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "reason": "declared in sources",
      "tokens": 399
    }
  ],
  "supplementary": [
    {
      "id": "e3bde09784c5080dfab352d5",
      "path": "tests/acceptance/W2-157/test_w2_157_nothing_else.py",
      "text": "def test_f4_the_branch_changes_only_the_tickets_allowed_paths(tmp_path):\n    \"\"\"``git diff --name-only <merge-base with w2/integrate>...HEAD`` lists only paths matched by the ticket's\n    ``allowed_paths`` or under ``tests/acceptance/W2-157/``. It is green only when the branch is clean: a change to\n    any other path (a ticket file, another module, a test of another ticket) makes it fail, and it fails, naming the\n    gap, where ``w2/integrate`` does not resolve.\"\"\"\n    env = {\"PATH\": support.SAFE_PATH, \"GIT_CONFIG_NOSYSTEM\": \"1\", \"GIT_CONFIG_GLOBAL\": \"/dev/null\", \"LC_ALL\": \"C\",\n           \"HOME\": str(tmp_path)}\n\n    def git(*args):\n        return subprocess.run([\"git\", \"-C\", str(ROOT), *args], env=env, capture_output=True, text=True, timeout=60)\n\n    base = git(\"merge-base\", \"HEAD\", \"w2/integrate\")\n    assert base.returncode == 0 and base.stdout.strip(), f\"w2/integrate does not resolve: {base.stderr}\"\n    diff = git(\"diff\", \"--name-only\", f\"{base.stdout.strip()}...HEAD\")\n    assert diff.returncode == 0, f\"git diff failed: {diff.stderr}\"\n    patterns = allowed_paths()\n    assert patterns, f\"no allowed_paths read from {TICKET}\"\n",
      "tokens": 286
    },
    {
      "id": "18bfdcb993ed3d0ac8eb6009",
      "path": "tests/acceptance/W2-157/README.md",
      "text": "| F4 (any change outside the paths) | `test_w2_157_nothing_else.py::test_f4_the_branch_changes_only_the_tickets_allowed_paths` | **green today**: it guards a clean branch (the diff against the merge-base with `w2/integrate` lists only this folder). It goes red on the engineer's branch only if a path outside `allowed_paths` and this folder changes |\n\n",
      "tokens": 88
    },
    {
      "id": "DAEO-5rgj",
      "path": ".tickets/DAEO-5rgj.md",
      "text": "---\nid: DAEO-5rgj\nstatus: open\ndeps: [DAEO-cb2b]\nlinks: [DAEO-cb2b]\ncreated: 2026-11-12T01:50:00Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-121c\ntags: [wave-2, dispatch, full]\nwbs_id: W2-121c\ntitle: \"gov dispatch, part c: health: heavy-job slots, the embedding servers health and GPU state, the busy-core band, overnight server errors, heartbeat alerts\"\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: [DAEO-cb2b]\nwaits_on: []\nallowed_paths:\n- src/gov/dispatch/**\n- src/gov/resources/slots.py\n- tests/unit/dispatch/test_w2_121c*\nest_loc: 600\nkpis:\n  success:\n  - 'Every heavy step takes a heavy-job slot (W2-20: test runs, rebuilds, full checks, retrieval measures), so peaks stay capped whenever they come; a heavy step found running outside a slot is named in the status as a finding Verify: a planted heavy step (test run, rebuild, full check, retrieval measure) is shown holding a slot; a planted one running with no slot is named in the status as a finding. [DEC-1008, DEC-979 D1]'\n",
      "tokens": 262
    },
    {
      "id": "DAEO-5rgj",
      "path": ".tickets/DAEO-5rgj.md",
      "text": "  - 'The morning report lists every crash or error in the servers'' logs overnight (CUDA errors, runner exits, model loads and their layers, failed and timed-out requests with their counts), beside the nightly''s tests [DEC-1030 item 3, DEC-1031 item 4] [lifted (was S17), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n  - 'The dispatcher alerts when the orchestrator''s session or its sentinel has no heartbeat for a configured time [DEC-1014 item 2, SMART-WORK-4 line 11] (to Wave 3, W3-P16, W-10) [re-scoped, DEC-1083] (was S12)'\nnon_goals:\n- the dispatcher core (W2-121, part a) and the other parts\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]\nacceptance_tests:\n  path: tests/acceptance/W2-121c/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\n---\n",
      "tokens": 262
    },
    {
      "id": "DAEO-5rgj",
      "path": ".tickets/DAEO-5rgj.md",
      "text": "# W2-121c gov dispatch, part c\n\nSplit from W2-121 (DAEO-cb2b) by the CTO's delegated decision on its run 1's P-W2-121-1 (a) and P-W2-121-3 (a), 2026-11-12: these KPI lines moved word for word; it builds on part a's Interface (in W2-121's ticket) and runs after it. The reference is the CTO's dispatcher (`governance/project/orchestration/tools/dispatch/`), never a target.\n",
      "tokens": 94
    },
    {
      "id": "DAEO-cb2b",
      "path": ".tickets/DAEO-cb2b.md",
      "text": "## Part a, the core (the CTO's delegated decision, DEC-1112 (3), 2026-11-12: run 1's P-W2-121-1 (a) to P-W2-121-4 (a))\n\nThis ticket is now part a: `gov dispatch tick` and `gov dispatch status` (the former S1, S2, S3, S5, S7, S8, S11, S12,\nS18, S20 and F1's start half). The other lines moved word for word: landing to W2-121b (DAEO-ifgf), health to W2-121c\n(DAEO-5rgj, with `src/gov/resources/slots.py`), watch and launch lead to W2-121d (DAEO-6w5n, with `src/gov/watch/**` and\n`src/gov/launch/**`). Each part is one FULL loop. Whether parts a and b together meet K9's \"a dispatcher\" entry criterion\nfor EXAMIN's copy is the owner's to say (09:30 digest of 11-12).\n\n",
      "tokens": 167
    },
    {
      "id": "DAEO-weh2",
      "path": ".tickets/DAEO-weh2.md",
      "text": "- tests/acceptance/W2-170/conftest.py\n- src/gov/close/select.py\nneeds:\n- tests/acceptance/W2-170/test_w2_170_f5_paths.py\nkpis:\n  success:\n  - 'S1 `test_f5_the_branch_changes_only_paths_the_ticket_allows` judges only W2-170''s own branch: on any other branch (another ticket''s worktree, the merge queue''s candidate merge, w2/integrate, the nightly''s clone) it is skipped with its reason, never red; on W2-170''s own branch (`w2/W2-170`) it judges as today. Verify: planted repositories: a branch named w2/W2-170 with a change outside W2-170''s paths fails it; the same change on a branch named w2/W2-171, and on a detached candidate merge of w2/W2-171 into w2/integrate, skips it with the reason; on w2/integrate it skips [DEC-866, DEC-253]'\n  failure:\n  - 'A change outside W2-170''s paths on W2-170''s own branch let through. Verify: S1''s planted w2/W2-170 branch fails the revised case'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the branch against its base lists only the allowed paths'\nnon_goals:\n- the other tickets'' F5 cases (each judged on its own merit when found)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\n",
      "tokens": 291
    },
    {
      "id": "DAEO-weh2",
      "path": ".tickets/DAEO-weh2.md",
      "text": "- the other tickets'' F5 cases (each judged on its own merit when found)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-866, DEC-253, DEC-966, DEC-989]\nacceptance_tests:\n  path: tests/acceptance/W2-170/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C1): the revision with a Rewrite-Reason (DEC-866)'\ntrack: B\n---\n",
      "tokens": 91
    },
    {
      "id": "ebfda29d9f080e3456ea9e94",
      "path": "tests/acceptance/W1-01/README.md",
      "text": "    what one of its other parents holds (the same content, or absent in both);\n  - every non-merge commit on the merged side (reachable from another parent and not from the first) that touches\n    `tests/acceptance/**` carries `Role: independent-test-designer`.\n- A merge commit on the merged side is judged by the same rule when the history walk reaches it.\n\nA merge commit that holds content under `tests/acceptance/` that none of its parents holds fails. This includes a\nconflict in an acceptance test resolved by hand in the merge commit, and a file that git merged from changes on both\nsides. The second case is stricter than DEC-253 requires. It needs no write to the repository to check, and it fails\nclosed: such a merge is made by a test designer, or the owner decides.\n\n`test_w1_01_integration_merges.py` shows both directions in small temporary repositories, and the real history:\n\n| Case | Test | Result |\n|---|---|---|\n| A merge of a ticket branch with a test-designer commit and an engineer commit | `test_a_merge_of_test_designer_commits_passes` | passes |\n",
      "tokens": 268
    },
    {
      "id": "DEC-255",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-255 \u2014 New ticket W1-50: containment attribution by commit trailers\n- **Status:** ACCEPTED (owner, 2026-10-04) \u00b7 **Basis:** OWNER \u00b7 **Under:** CAP-58, DEC-076, DEC-182, DEC-235 \u00b7 **Amends:** the Wave 1 ticket set (49 \u2192 50 tickets)\n- **Decision:**\n  - A new ticket, W1-50: role engineer, profile FULL, priority high, depends on W1-03.\n  - KPIs:\n    - a forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit: each\n      commit's paths against the allowed paths of its own `Role` and `Task` trailers, not against the caller;\n    - a merge commit itself is not a finding when every commit it brings passes that check;\n    - a worker's commit made during another actor's call is judged by its own trailers;\n    - a commit with no `Role` or `Task` trailer is judged against the caller, as today.\n  - Allowed paths: `src/gov/guard/containment*`, `template/governance/kernel/hooks/posttooluse*`,\n    `template/governance/kernel/hooks/pretooluse*`, `tests/unit/containment/**`.\n  - Its test design batch also carries the W1-01 revision of DEC-253.\n  - The Contract gets a covers item under CAP-58, in its own commit.\n",
      "tokens": 290
    },
    {
      "id": "08bfa689eed2e6c2081da02f",
      "path": "docs/changes/W2-116-evidence.md",
      "text": "## Tests\n\n- Unit (stand-in embedder and code-graph tool, planted git repositories, no model):\n  - `tests/unit/rebuild/test_w2_116_integration.py`: 25 passed (19 + 6 for the review's F1, F6, F8);\n  - `tests/unit/launch/test_w2_116_store.py`: 15 passed (13 + 2 for F2, F4).\n  - The 8 new tests were run against the code before the fix (a detached worktree at `e6724c208`): 8 failed.\n- `gov accept W2-116` (`HOME=/home/usain`, after the ride-along): **pass**, 20 passed, 0 failed, 0 skipped. Lines\n  success-1/3/4/5 and failure-1/2/3; S2 is not mapped in this pass.\n- Regression, `tests/unit/rebuild`, `tests/unit/launch`, `tests/unit/retrieve` with `GOV_TESTS_OPTIN=lifted,breadth`\n  and `-m \"not local_only\" -k \"not real and not green_here and not time_limit\"`, `HOME` an empty folder: **257\n  passed** (249 + the 8 new), none deselected: the real-model exclusion removes no case in these folders.\n- Every run went through `heavy_slot.sh`. No real embedder, reranker or model was started.\n",
      "tokens": 247
    },
    {
      "id": "DAEO-vhad",
      "path": ".tickets/DAEO-vhad.md",
      "text": "---\nid: DAEO-vhad\nstatus: closed\ndeps: []\nlinks: [DAEO-dtv3]\ncreated: 2026-11-02T12:06:59Z\ntype: task\npriority: 1\nassignee: independent-test-designer\nexternal-ref: W1-01b\ntags: [wave-2, test-revision, lite]\nwbs_id: W1-01b\ntitle: 'W1-01''s merge rule: a merge listed in acceptance_exemptions is exempt for its own changes too (DEC-1031 item 3, DEC-906)'\nclass: test-revision\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\ndepends_on: []\nallowed_paths:\n- tests/acceptance/W1-01/w1_01_support.py\n- tests/acceptance/W1-01/test_w1_01_integration_merges.py\n- tests/acceptance/W1-01/README.md\nkpis:\n  success:\n  - 'W1-01''s `merge_offences` treats a merge commit whose full id is listed in the path map''s `acceptance_exemptions` as exempt for the changes it makes itself (a conflict resolution), as it already treats a listed brought commit; every other merge is judged as strictly as today; with `0568d91baf56` listed, `test_the_integration_merges_of_this_repository_pass` is green on `w2/integrate`; the commit carries `Rewrite-Reason: DEC-1031 item 3` [DEC-1031 item 3, DEC-906, DEC-253]'\n",
      "tokens": 275
    },
    {
      "id": "01a6e52198d360065f62e9e8",
      "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md",
      "text": "## The one decision: W1-01's merge rule and `0568d91baf56`\n1. **Context:** DEC-253 (only the test designer commits acceptance tests) is judged on merges by W1-01's\n   `merge_offences`. A merge whose own tree changes an acceptance file beyond what git's own merge would hold is an\n   offence, unless the merge carries the test designer's role. `acceptance_exemptions` (DEC-906) exempts only the\n   commits a merge brings.\n2. **What happened:** `0568d91baf56` resolved one conflict in W1-30's acceptance file; the resolution was a test\n   designer's (td-9, sandboxed), committed by its lead with `Role: orchestrator`. It entered `w2/integrate` with W2-67's\n   merge, after the 10-31 baseline, so the red is new to the nightly. History is never rewritten (DEC-412).\n3. **Why it matters:** a permanent red that no ticket fixes is a standing accepted red, which DEC-968 forbids.\n4. **Options:**\n   - (a) W1-01's test designer extends `merge_offences` so a merge listed in `acceptance_exemptions` is exempt for its\n     own changes too (a test revision you name under DEC-906), and you commit one exemption entry for\n",
      "tokens": 278
    },
    {
      "id": "bff8a936fd2861d9168b2e93",
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "text": "## 6. The rest of the list: traced, fixed, or placed (2026-11-09 23:10 to 2026-11-10 UTC; FORECAST-W2-2 \u00a73 row 11 and the CTO's additions)\n\nBy the CTO's helper, for orchestrator DAEO-sdxk. Method:\n- each red reproduced by running only that case or file at integrate (a detached worktree);\n- the root cause found and measured;\n- the fix made by the right role (a test designer with `Rewrite-Reason:` under DEC-866, a product-spec worker for the\n  plan tool);\n- one independent review, READY by `verdict.py` (records in `reviews/D10-*.md`);\n- the affected cases re-run on the merge result in a scratch worktree, then a one-command `--no-ff` merge.\n\nFORECAST's two \"merged\" branches are merged: W1-06 in `dddf54782`, test_fusion in `56a1a554c`.\n\n",
      "tokens": 186
    },
    {
      "id": "DAEO-xnbx",
      "path": ".tickets/DAEO-xnbx.md",
      "text": "# W1-50 Containment attribution by commit trailers\n\nOwner decision DEC-255, after the first integration merge of the parallel run (DEC-235): the post-command containment\ncheck (W1-03) judged a HEAD move against the caller and flagged every move that contains a merge commit, and it\nattributed a worker's commit to the call of the lead that was waiting for it. With this ticket a forward HEAD move is\njudged commit by commit, each commit by its own `Role` and `Task` trailers (DEC-182).\n\n- **Test design first, alone (DEC-256).** The test design batch runs now in its own worktree and is merged on its\n  own. It also carries the revision of W1-01's `test_only_the_test_designer_commits_to_acceptance_tests` (DEC-253): an\n  integration merge commit passes when every change it brings under `tests/acceptance/` comes from commits on the\n  merged side carrying `Role: independent-test-designer`; every non-merge commit is checked as before. That revision\n  is a rewrite after implementation, reason \"owner decision: integration merges\".\n- **Implementation after W1-46 is merged (DEC-256)**, because both tickets touch `src/gov/guard/**` and the\n  PreToolUse hook.\n",
      "tokens": 290
    }
  ],
  "supplementary_query": "W2-157's F4 path case judges any branch against W2-157's own paths: judged only on w2/W2-157, as W2-180 did for W2-170 and W2-173 (DECIDED-NOT-DONE row 171)\nS1 `test_f4_the_branch_changes_only_the_tickets_allowed_paths` judges only W2-157's own branch: on any other branch, a candidate merge of the merge queue, w2/integrate or the nightly's clone it is skipped with its reason (the branch found, or \"detached HEAD\"), never red; on `w2/W2-157` it judges as today. The same form as W2-180's revision of W2-170's F5. Verify: planted repositories: a branch named w2/W2-157 with a change outside W2-157's paths fails it; the same change on a branch named w2/W2-121c and on a detached candidate merge skips it with the reason [DEC-866, DEC-253]\nA change outside W2-157's paths on W2-157's own branch let through. Verify: S1's planted w2/W2-157 branch fails the revised case\nAny change outside the paths above. Verify: `git diff --name-only` of the branch against its base lists only the allowed paths",
  "further_batch": [
    {
      "id": "DAEO-xnbx",
      "path": ".tickets/DAEO-xnbx.md"
    },
    {
      "id": "9393ebf7aeddcc9d45ceaa31",
      "path": "governance/project/bootstrap.md"
    },
    {
      "id": "DEC-256",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "DEC-906",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "54bb0ff22c6acec4e8ec98ca",
      "path": "governance/project/briefs/LEAD-w2-common.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "e3bde09784c5080dfab352d5",
          "path": "tests/acceptance/W2-157/test_w2_157_nothing_else.py"
        },
        {
          "id": "18bfdcb993ed3d0ac8eb6009",
          "path": "tests/acceptance/W2-157/README.md"
        },
        {
          "id": "DAEO-5rgj",
          "path": ".tickets/DAEO-5rgj.md"
        },
        {
          "id": "DAEO-5rgj",
          "path": ".tickets/DAEO-5rgj.md"
        },
        {
          "id": "DAEO-5rgj",
          "path": ".tickets/DAEO-5rgj.md"
        },
        {
          "id": "DAEO-cb2b",
          "path": ".tickets/DAEO-cb2b.md"
        },
        {
          "id": "DAEO-weh2",
          "path": ".tickets/DAEO-weh2.md"
        },
        {
          "id": "DAEO-weh2",
          "path": ".tickets/DAEO-weh2.md"
        },
        {
          "id": "ebfda29d9f080e3456ea9e94",
          "path": "tests/acceptance/W1-01/README.md"
        },
        {
          "id": "DEC-255",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "08bfa689eed2e6c2081da02f",
          "path": "docs/changes/W2-116-evidence.md"
        },
        {
          "id": "DAEO-vhad",
          "path": ".tickets/DAEO-vhad.md"
        },
        {
          "id": "01a6e52198d360065f62e9e8",
          "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md"
        },
        {
          "id": "bff8a936fd2861d9168b2e93",
          "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md"
        },
        {
          "id": "DAEO-xnbx",
          "path": ".tickets/DAEO-xnbx.md"
        },
        {
          "id": "DAEO-xnbx",
          "path": ".tickets/DAEO-xnbx.md"
        },
        {
          "id": "9393ebf7aeddcc9d45ceaa31",
          "path": "governance/project/bootstrap.md"
        },
        {
          "id": "DEC-256",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-906",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "54bb0ff22c6acec4e8ec98ca",
          "path": "governance/project/briefs/LEAD-w2-common.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "54bb0ff22c6acec4e8ec98ca",
      "reason": "budget exceeded"
    },
    {
      "id": "9393ebf7aeddcc9d45ceaa31",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-xnbx",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-256",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-906",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 5816,
  "budget": {
    "limit": 6000,
    "used": 5816
  },
  "left_out": {
    "count": 2,
    "superseded": [
      "DEC-636",
      "DEC-798"
    ],
    "done": []
  },
  "hash": "9d35db2eb9721353a6f1a493882b1221993e87b31ab4be529716784609ae38c4"
}
