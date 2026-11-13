{
  "ticket": "DAEO-pg6i",
  "ticket_text": "---\nid: DAEO-pg6i\nstatus: in_progress\ndeps: []\nlinks: [DAEO-2bdu, DAEO-zmo4]\ncreated: 2026-11-12T16:55:43Z\ntype: task\npriority: 1\nassignee: product-spec\nexternal-ref: W2-88a\nparent: DAEO-2bdu\ntags: [wave-2, product-spec, adoption, memory, kernel-skill, standard]\nwbs_id: W2-88a\ntitle: 'W2-88a The adopt skill states Wave 0''s memory practice in order, and the Verify pass (W2-88''s and W2-174''s kernel skill text)'\nclass: specification\nstate_class: AUTHORITATIVE\nrole: product-spec\nprofile: STANDARD\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- template/governance/kernel/skills/adopt/SKILL.md\n- template/.rulesync/skills/adopt/SKILL.md\n- .rulesync/skills/adopt/SKILL.md\n# .claude/skills/adopt/SKILL.md out of the paths: generated from the kernel skill by the copies ACT after the owner's approval (DEC-315)\n- docs/changes/W2-88a-CIT-P.md\n- docs/research/W2-88-memory-practice.md  # the practice record the skill points to, refreshed to S17's order (from W2-88)\nest_loc: 80\nreads:\n- .tickets/DAEO-2bdu.md\n- .tickets/DAEO-zmo4.md\n- docs/research/W2-88-memory-practice.md\n- template/governance/kernel/skills/\nneeds: []\nkpis:\n  success:\n  - 'S17 The Wave 0 order in the adopt skill: A9''s step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - line: \"The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083]\"\n    verify: \"tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section\"\n  - 'The CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill''s sha256 before and after, the lines added or removed, the independent review and the owner''s approval of the bytes before the merge; the two .rulesync copies equal the kernel copy in the changed sections Verify: the record holds both hashes and the review''s verdict; a diff of the three files shows the same changed sections [CAP-33, DEC-1116]'\n  failure: []\nnon_goals:\n- the adopt code (W2-88, W2-174) and the proofs (W2-88b); the .claude/ copy (the copies ACT)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33]\nacceptance_tests:\n  path: tests/acceptance/W2-88a/\n  author: independent-test-designer (MR-3); written before the text\ntrack: A\n---\n# W2-88a The adopt skill's kernel text (a child of W2-88)\n\nFiled by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the kernel skill text: W2-88's S17 (moved word for word) and W2-174's skill line (its S5, moved word for word, so the adopt skill is written once under one CIT-P). The two `test_w2_174_skill.py` and S17 string tests named in the moved lines are this ticket's acceptance tests, written by its test designer under `tests/acceptance/W2-88a/`. It can start now; the owner approves the skill's bytes before the merge (CAP-33).\n",
  "authority": [
    {
      "id": "DEC-1150",
      "sha256": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "reason": "declared in sources",
      "tokens": 4054
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1130",
      "sha256": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "reason": "declared in sources",
      "tokens": 428
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1150",
      "sha256": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "reason": "declared in sources",
      "tokens": 4054
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1130",
      "sha256": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "reason": "declared in sources",
      "tokens": 428
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "supplementary": [],
  "supplementary_query": "W2-88a The adopt skill states Wave 0's memory practice in order, and the Verify pass (W2-88's and W2-174's kernel skill text)\nS17 The Wave 0 order in the adopt skill: A9's step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1099 (2); DEC-1098 (1)]\n{'line': \"The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083]\", 'verify': 'tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section'}\nThe CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill's sha256 before and after, the lines added or removed, the independent review and the owner's approval of the bytes before the merge; the two .rulesync copies equal the kernel copy in the changed sections Verify: the record holds both hashes and the review's verdict; a diff of the three files shows the same changed sections [CAP-33, DEC-1116]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 7810,
  "budget": {
    "limit": 20000,
    "used": 7810
  },
  "hash": "2e3dc599e4548581a2f8592777ca3c1b42a5fad788654f78f68e6e7c95fdc189"
}
