{
  "ticket": "DAEO-7oxm",
  "ticket_text": "---\nid: DAEO-7oxm\nstatus: in_progress\ndeps: [DAEO-qz4p]\nlinks: [DAEO-qz4p, DAEO-61vm, DAEO-k1e2]\ncreated: 2026-11-12T05:03:31Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-178\ntags: [wave-2, memory, audit, full, held-out]\nwbs_id: W2-178\ntitle: 'The auditor''s copy of a set leaves out its dropped questions (W2-170''s Interface; W2-173 run 1''s P-2)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: [DAEO-qz4p]\nwaits_on: []\nallowed_paths:\n- governance/project/orchestration/tools/indep_launch.py\n- tests/unit/orchestration/test_w2_178*\n- docs/changes/W2-178-evidence.md\nest_loc: 40\nkpis:\n  success:\n  - 'S1 When the launch script builds an auditor''s wall, the auditor''s copy of a set holds every file of the set except those under its `hidden/dropped/` folder, as W2-170''s Interface states; every other kind''s copy is unchanged. Verify: a planted sets root (never the real one) with a set holding `hidden/dropped/` files: the auditor''s wall copy has none of them and every other file byte-identical; a writer''s and a checker''s walls built from the same set are byte-identical to the build before this change [DEC-1101 (2), DEC-820 (b), (d)]'\n  failure:\n  - 'A dropped question reaching an auditor, or any other kind''s wall changing. Verify: S1''s planted set: no path under `hidden/dropped/` in the auditor''s copy; the other kinds'' walls compared byte for byte'\n  - 'A session or test opening the real sets root, a hidden half or the held-out material. Verify: every test plants its own sets root under its temporary folder; a grep of the new tests for the real root''s path finds 0 lines'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nnon_goals:\n- the counts schema, the stop word and the delivery checks (W2-173)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1101, DEC-820, DEC-1052, DEC-1120]\nacceptance_tests:\n  path: tests/acceptance/W2-178/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines, before the engineer: planted sets root only'\ntrack: B\nreads:\n- governance/project/orchestration/packages/MEMORY-AUDIT-1.md\nneeds:\n- governance/project/orchestration/tools/indep_launch.py\n---\n# W2-178 The auditor's copy of a set leaves out its dropped questions\n\nW2-173 run 1's P-2 (2026-11-12): W2-173's body cites W2-170's Interface (the auditor's copy of a set excludes\n`hidden/dropped/`), but no KPI line of W2-173 carries it, and its S5 and F3 forbid it, so it was not built. This ticket\ncarries the line. It must land before the first memory audit run (Mon 11-23). It runs after W2-173 (the same file).\nClass C2. The held-out and hidden-half rules hold: tests plant their own sets root; no session opens the real one.\n",
  "authority": [
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
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
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
    },
    {
      "id": "DEC-1120",
      "sha256": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DAEO-qz4p",
      "sha256": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "reason": "declared in sources",
      "tokens": 1063
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
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
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
    },
    {
      "id": "DEC-1120",
      "sha256": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DAEO-qz4p",
      "sha256": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "reason": "declared in sources",
      "tokens": 1063
    }
  ],
  "supplementary": [],
  "supplementary_query": "The auditor's copy of a set leaves out its dropped questions (W2-170's Interface; W2-173 run 1's P-2)\nS1 When the launch script builds an auditor's wall, the auditor's copy of a set holds every file of the set except those under its `hidden/dropped/` folder, as W2-170's Interface states; every other kind's copy is unchanged. Verify: a planted sets root (never the real one) with a set holding `hidden/dropped/` files: the auditor's wall copy has none of them and every other file byte-identical; a writer's and a checker's walls built from the same set are byte-identical to the build before this change [DEC-1101 (2), DEC-820 (b), (d)]\nA dropped question reaching an auditor, or any other kind's wall changing. Verify: S1's planted set: no path under `hidden/dropped/` in the auditor's copy; the other kinds' walls compared byte for byte\nA session or test opening the real sets root, a hidden half or the held-out material. Verify: every test plants its own sets root under its temporary folder; a grep of the new tests for the real root's path finds 0 lines\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "03ad569aad0a2ce8dbc2fbcf",
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md"
    },
    {
      "id": "55b80e73a4c8de74156e96f3",
      "path": "tests/acceptance/W1-50/README.md"
    },
    {
      "id": "864de1ef5aa0a0be5cd856f6",
      "path": "governance/project/bootstrap.md"
    },
    {
      "id": "2c333deeea7c2bd3c85c1e5e",
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md"
    },
    {
      "id": "DAEO-wahn",
      "path": ".tickets/DAEO-wahn.md"
    },
    {
      "id": "6d8b85978cdad0cc3b23f91d",
      "path": "docs/changes/W2-170-evidence.md"
    },
    {
      "id": "144ff1fffb2e968c1d4e00b0",
      "path": "tests/acceptance/W2-173/test_w2_173_stopped.py"
    },
    {
      "id": "DAEO-xafn",
      "path": ".tickets/DAEO-xafn.md"
    },
    {
      "id": "592f784d1faf4b5cf74a764c",
      "path": "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-1.md"
    },
    {
      "id": "DEC-641",
      "path": "docs/DECISION_REGISTER.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "03ad569aad0a2ce8dbc2fbcf",
          "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md"
        },
        {
          "id": "55b80e73a4c8de74156e96f3",
          "path": "tests/acceptance/W1-50/README.md"
        },
        {
          "id": "864de1ef5aa0a0be5cd856f6",
          "path": "governance/project/bootstrap.md"
        },
        {
          "id": "2c333deeea7c2bd3c85c1e5e",
          "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md"
        },
        {
          "id": "DAEO-wahn",
          "path": ".tickets/DAEO-wahn.md"
        },
        {
          "id": "6d8b85978cdad0cc3b23f91d",
          "path": "docs/changes/W2-170-evidence.md"
        },
        {
          "id": "144ff1fffb2e968c1d4e00b0",
          "path": "tests/acceptance/W2-173/test_w2_173_stopped.py"
        },
        {
          "id": "DAEO-xafn",
          "path": ".tickets/DAEO-xafn.md"
        },
        {
          "id": "592f784d1faf4b5cf74a764c",
          "path": "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-1.md"
        },
        {
          "id": "DEC-641",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "03ad569aad0a2ce8dbc2fbcf",
      "reason": "budget exceeded"
    },
    {
      "id": "144ff1fffb2e968c1d4e00b0",
      "reason": "budget exceeded"
    },
    {
      "id": "2c333deeea7c2bd3c85c1e5e",
      "reason": "budget exceeded"
    },
    {
      "id": "55b80e73a4c8de74156e96f3",
      "reason": "budget exceeded"
    },
    {
      "id": "592f784d1faf4b5cf74a764c",
      "reason": "budget exceeded"
    },
    {
      "id": "6d8b85978cdad0cc3b23f91d",
      "reason": "budget exceeded"
    },
    {
      "id": "864de1ef5aa0a0be5cd856f6",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-wahn",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-xafn",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-641",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-7oxm): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 5978,
  "budget": {
    "limit": 6000,
    "used": 5978
  },
  "left_out": {
    "count": 2,
    "superseded": [
      "DEC-002",
      "DEC-045"
    ],
    "done": []
  },
  "hash": "cb60f4da7f4eb0dea07c54cc67a04edc347fede577f7962187cd5e3850cc854d"
}
