{
  "ticket": "DAEO-neam",
  "ticket_text": "---\nid: DAEO-neam\nstatus: in_progress\ndeps: [DAEO-g0ip]\nlinks: []\ncreated: 2026-10-16T16:35:12Z\ntype: task\npriority: 4\nassignee: engineer\nexternal-ref: W2-45\ntags: [wave-2, implementation, standard]\nwbs_id: W2-45\ntitle: gov check runner semantics and scale\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\nallowed_paths:\n- src/gov/check/runner.py\n- src/gov/check/commands.py\n- src/gov/decisions/checker.py\n- tests/unit/check/**\nkpis:\n  success:\n  - 'The decision checker runs within the gov check budget on a 200-decision, 20k-commit repository Verify: a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget''s value printed beside it) [W2-H018].'\n  - 'A check that exits 0 with findings, or with \"unmeasured\" in its result, is not green Verify: planted checks, one exiting 0 with a finding and one exiting 0 with \"unmeasured\" in its result: both are reported not green; a planted clean check exiting 0 is green [W2-M129, W2-M212].'\n  - 'An absent tool of a hard-block check is red, not yellow Verify: a planted hard-block check whose tool is absent from the path: its result is red, never yellow [W2-M130, W2-M265].'\n  - 'A hard-block key is covered only by a check of hard-block tier Verify: a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted [W2-M211, W2-M259].'\n  - 'The time limit is stated and tested Verify: the limit''s value is printed in the runner''s result, and a planted check that runs past it is stopped and reported as timed out, by a unit test [W2-M151].'\n  failure: []\nprofile: STANDARD\nsources:\n- DEC-729\nest_loc: 160\nacceptance_tests:\n  path: tests/acceptance/W2-45/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- W2-H018\nlist_rows:\n- W2-H018\n- W2-L096\n- W2-L098\n- W2-L104\n- W2-L118\n- W2-L167\n- W2-L168\n- W2-L169\n- W2-L171\n- W2-L223\n- W2-M063\n- W2-M128\n- W2-M129\n- W2-M130\n- W2-M131\n- W2-M132\n- W2-M144\n- W2-M146\n- W2-M151\n- W2-M170\n- W2-M211\n- W2-M212\n- W2-M259\n- W2-M265\n- W2-M268\n- W2-M315\n---\n# W2-45 gov check runner semantics and scale\n\n**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** K8 (DEC-941); W2-26 found no trigger (indexing about 30 % of the envelope).\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-45), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/check/runner.py`, `src/gov/check/commands.py`, `src/gov/decisions/checker.py` (speed only), `tests/unit/check/**`.\n- **KPIs:**\n  - The decision checker runs within the `gov check` budget on a 200-decision, 20k-commit repository [W2-H018].\n  - A check that exits 0 with findings, or with \"unmeasured\" in its result, is not green [W2-M129, W2-M212].\n  - An absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].\n  - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].\n  - The time limit is stated and tested [W2-M151].\n\n## Interface (DEC-1052; P-W2-45-1 accepted as a whole, item 5 as written: an absent tool of a hard-block check is RED, openspec included; the CTO, 2026-11-12 12:58)\n\nProposal (all in src/gov/check/runner.py unless named):\n\n1. **Tier = the declaration's `severity`.** \"Hard-block tier\" means `severity: hard-block`. `tier:` (G0-G5) is not read.\n2. **Time fields (S1, S5).** Every check result gains `elapsed_s` (wall seconds, float) and `time_limit_s` (the limit\n   applied: its `timeout-seconds`, else `TIMEOUT_S`). The runner's result gains top-level `time_limit_s` (= `TIMEOUT_S`,\n   60, DEC-595). Built-in checks carry both too.\n3. **S1, the budget.** The `gov check` budget of the decision checker is the time limit of the check that runs it,\n   core-authority: 60 s (TIMEOUT_S; its declaration states none). Verified by a planted repository of 200 decision\n   records and 20,000 commits (built with `git fast-import`) holding the core-authority declaration: `gov check --json`\n   exits, and core-authority's entry has `elapsed_s` < `time_limit_s`, both printed. Speed work only in\n   `src/gov/decisions/checker.py`.\n4. **S2, not green.** A check is GREEN only when it exits 0 with no finding. Exit 0 also yields findings when: the\n   success form `{\"ok\": true, \"result\": R}` has a non-empty `R.findings`; or any JSON mapping in the output (top level\n   or R) has `\"unmeasured\": true` -> finding `CHECK_UNMEASURED` with its `reason`; or non-JSON output contains the word\n   \"unmeasured\" -> `CHECK_UNMEASURED`. Status from findings as now: RED if hard-block, YELLOW if warning.\n5. **S3, absent tool.** Exit code 127, or OSError on start -> finding `CHECK_TOOL_ABSENT` naming the command's first\n   word; RED when hard-block (never YELLOW), YELLOW when warning. The built-in `openspec-validate` (hard-block) follows\n   the same rule: `OPENSPEC_ABSENT` becomes RED. (Cost: a machine without openspec gets a red `gov check`; openspec\n   and gitleaks are installed here. Alternative (b): leave openspec YELLOW, named as a residual against S3.)\n6. **S4, tier coverage.** A path-map policy key of strength hard-block whose covering declarations (`enforces`) are all\n   of severity warning -> a `policy-<key>` result, severity hard-block, RED, finding `POLICY_TIER_TOO_LOW` with\n   `policy`, `checks` (the covering ids) and a message naming the key. \"Refused\" = that RED result and `gov check`'s\n   non-zero exit (unchanged). One hard-block declaration covering it -> no policy result (accepted). An uncovered key\n   keeps `POLICY_NOT_COVERED`.\n7. **S5, time limit.** A check past its limit is stopped with its whole process group (`start_new_session=True`,\n   `killpg` on timeout, so a grandchild holding the pipe cannot keep the runner waiting) -> finding `CHECK_TIMED_OUT`\n   (was `CHECK_FAILED`) carrying `time_limit_s`; status by severity. Unit test in `tests/unit/check/` (engineer): a\n   planted check `sleep 30` with `timeout-seconds: 1` -> `CHECK_TIMED_OUT`, `time_limit_s` 1 printed, ends in < 10 s.\n8. **Unchanged:** family roll-up, `gov check`'s exit code rule, the not-applicable (exit 2) path, `commands.py`\n   (W2-159's line kept; touched only if a module list needs it).\n",
  "authority": [
    {
      "id": "DEC-729",
      "sha256": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "reason": "declared in sources",
      "tokens": 358
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    }
  ],
  "mandatory": [
    {
      "id": "DEC-729",
      "sha256": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "reason": "declared in sources",
      "tokens": 358
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    }
  ],
  "supplementary": [],
  "supplementary_query": "gov check runner semantics and scale\nThe decision checker runs within the gov check budget on a 200-decision, 20k-commit repository Verify: a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget's value printed beside it) [W2-H018].\nA check that exits 0 with findings, or with \"unmeasured\" in its result, is not green Verify: planted checks, one exiting 0 with a finding and one exiting 0 with \"unmeasured\" in its result: both are reported not green; a planted clean check exiting 0 is green [W2-M129, W2-M212].\nAn absent tool of a hard-block check is red, not yellow Verify: a planted hard-block check whose tool is absent from the path: its result is red, never yellow [W2-M130, W2-M265].\nA hard-block key is covered only by a check of hard-block tier Verify: a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted [W2-M211, W2-M259].\nThe time limit is stated and tested Verify: the limit's value is printed in the runner's result, and a planted check that runs past it is stopped and reported as timed out, by a unit test [W2-M151].",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 2412,
  "budget": {
    "limit": 6000,
    "used": 2412
  },
  "hash": "491f410d0781524a54992ad3ddf581a5a749306d5aacf1c5f7b442c3c1483123"
}
