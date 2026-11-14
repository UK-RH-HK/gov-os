{
  "ticket": "DAEO-f58b",
  "ticket_text": "---\nid: DAEO-f58b\nstatus: in_progress\ndeps: [DAEO-lrre]\nlinks: []\ncreated: 2026-10-31T23:52:57Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-116\ntags: [wave-2, implementation, memory, standard, smart-work]\nwbs_id: W2-116\ntitle: 'The designers'' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer''s retrieval reads (SMART-WORK-1)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-lrre\nallowed_paths:\n- src/gov/status/**  # S2: the store's head and age in gov status (CTO, DEC-1157 (12))\n- docs/probes/DAEO-f58b/**  # the probe record\n- src/gov/rebuild/integration.py\n- src/gov/rebuild/command.py\n- src/gov/launch/store.py\n- src/gov/launch/launcher.py\n- src/gov/retrieve/command.py\n- docs/changes/W2-116-evidence.md\n- tests/unit/rebuild/test_w2_116*\n- tests/unit/launch/test_w2_116*\n- governance/project/rebuild.yaml  # S2, P-W2-116-S2-INTERFACE Q2 (b) (CTO, DEC-1157 (12)): this repository's integration_refresh line lands with the code that reads it\n- src/gov/retrieval/retrieve.py  # R2-F3, Q3 (a) (CTO): the continuation token carries the half it was made on (about 20 lines)\n- tests/unit/status/test_w2_116*\n- tests/unit/retrieval/test_w2_116*\n- tests/acceptance/W2-131/test_w2_131_unchanged.py  # R2-F3's `f` token key (Q3 (a)): the helper drops `f` beside `s` when it compares tokens from two folders; a test designer, Rewrite-Reason (CTO, DEC-1156 (7))\n- tests/acceptance/W2-133/test_w2_133_unchanged.py  # the same\n- tests/acceptance/W2-135/test_w2_135_unchanged.py  # the same\n- tests/unit/retrieval/test_w2_131_register_ids.py  # the same\n- tests/unit/retrieval/test_w2_133_gap_label.py  # the same\n- tests/unit/retrieval/test_w2_135_item_cap.py  # the same\n- tests/unit/status/test_status.py  # S2's new `integration_store` part in gov status's PARTS (the same route)\nkpis:\n  success:\n  - '`gov rebuild --integration <branch>` keeps a store of that branch''s head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] Verify: the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)]'\n  - 'It is refreshed after the nightly''s verdict and at a set second time each day (both in the project''s configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] Verify: pass 2''s cases: a planted configuration''s two refresh times are read and the refresh runs after the nightly''s verdict and at the second time; `gov status` names the integration store''s head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)]'\n  - '`gov launch independent-test-designer` points the session''s retrieval at it; a designer''s retrieval never reads a ticket worktree''s store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role''s plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]'\n  - 'The store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]'\n  - 'A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] Verify: the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)]'\n  - '`gov launch` points every worker session''s retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer''s; a designer''s retrieval never reads a ticket worktree''s store. Verify: a launcher unit test per worker role: the session environment names the integration store; a designer''s never names a worktree''s store [DEC-1087 (3), DEC-963] [added, the CTO''s note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)]'\n  failure:\n  - 'A designer''s retrieval answered from a ticket worktree''s store. Verify: tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)]'\n  - 'The link switched to a store whose build failed, or a search answered from a half-built store. Verify: the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)]'\n  - 'A re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] Verify: the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)]'\nprofile: STANDARD\nsources:\n- DEC-1109\n- DEC-1112\n- DEC-983\n- DEC-982\n- DEC-963\n- DEC-966\n- DEC-1014\n- DEC-1015\n- DEC-1083\n- DEC-1087\n- DEC-719\n- DAEO-kia7\nest_loc: 150\nacceptance_tests:\n  path: tests/acceptance/W2-116/\n  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); a planted branch, a build killed half-way, a search during a build\ntrack: B\nlist_rows:\n- W2-M088\n---\n# W2-116 The designers' store in the product\n\nThe owner's SMART-WORK-1 decision 2 (DEC-983): the designers' store (DEC-963, DEC-966 item 3) becomes the product's, not only the CTO's `refresh_integration_store.sh` and `store_refresh_daily.sh`.\n\n- **Why:** a test designer retrieves only from the integration branch's store, so its retrieval never serves a ticket's implementation. W2-33's role files and W2-83b's playbooks will tell an adopted product's designers so; nothing in the product builds that store.\n- **This repository's own configuration:** the place (`~/gov-os-worktrees/W2-00-store`) and the two times a day; the CTO's scripts are retired once this lands.\n- **Order:** after W2-60b (the launcher's files) and W2-33 (the rule it serves); before EXAMIN's copy (W2-27).\n\n**DEC-1087 (3) placed here (CTO, 2026-11-06, delegated P3 on the scope):** the owner orders the refresh after every\nmerge into integrate built, tested and reviewed before re-pin window 4, so the window puts it live. The worktrees get\nthe integration store's path, so workers can search.\n- **S2's interface (pass 2b; P-W2-116-S2-INTERFACE Q1 (a), the CTO, DEC-1157 (12), 2026-11-13).** A product tick that\n  watches a configured verdict file; the nightly does not change.\n  - **Config** in `rebuild.yaml`: `integration_refresh: {branch, after_nightly: {verdict: <glob>, latest: \"HH:MM\"},\n    second: \"HH:MM\"}`.\n  - **Command:** `gov rebuild --integration <branch> --when-due`. It refreshes when a verdict file is newer than the\n    last scheduled refresh, when `latest` passes without one, or once `second` passes; otherwise it builds nothing and\n    says `not_due`.\n  - **Record:** each scheduled refresh writes `<link>.refresh.json`. Tests plant the clock with `GOV_NOW`.\n  - **Error:** a missing or invalid time refuses `REBUILD_CONFIG_INVALID`, naming the key.\n  - **`gov status`** gains an `integration_store` part: head, branch head, built time, age, `stale` and the stale\n    reason. **Stale:** the store's head is behind the branch, or it was built before the last time a refresh fell due.\n  - **This repository's values** (Q2 (b), in this ticket's paths): `branch: w2/integrate`, verdict glob\n    `.gov-runtime/scratch/orchestrator/log/nightly/*/run.txt`, `latest: \"10:00\"`, `second: \"18:00\"`.\n  - **Cron:** a line every 5 minutes, in window 4's ACT next to the hook (not this ticket).\n  - **R2-F3 (Q3 (a)):** the continuation token carries a mark of the half it was made on, checked when it is used\n    (`src/gov/retrieval/retrieve.py`).\n- **This pass builds S1, S3 (widened, below), S4 and S5, and the three failure lines.** S2's two daily times and\n  `gov status` stay for the next pass. Until then the CTO's `store_refresh_daily.sh` runs as the backstop (DEC-1087\n  (3)).\n- **S3 widened:** `gov launch` points every worker session's retrieval at the integration store, not only a\n  designer's. A designer's retrieval still never reads a ticket worktree's store. A worktree has no store of its own\n  today, so a worker's search answers `STORE_MISSING` (checked 2026-11-06).\n- **S4's trigger:** \"after every landing\" covers every merge into the integration branch, by the merge queue or by\n  hand. The product offers the refresh as a command run after the merge (`gov rebuild --integration <branch>`, idempotent\n  at an unchanged head). The hook that calls it after a hand merge is installed by the owner's operator in re-pin window\n  4's ACT (hooks are the operator's). The design is the engineer's, stated in its evidence record.\n- **The deps W2-60b (the session record) and W2-33 (the roles) are not needed** for this pass: it touches neither the\n  session record nor the role files. They stay in `deps:` for S2 and the role rule's text.\n- **The rebuild uses the code it runs under.** The store at window 4's head is built by window 4's code, so the pinned\n  code and the store always match. The engineer states how the double buffer keeps the ready half answering while the\n  other builds (F2).\n\n**TESTS-READY and the designer's points settled (CTO, 2026-11-06, delegated P3):**\n- **The tests:** `tests/acceptance/W2-116/` on `w2/W2-116-tests`.\n- **The interface they assume:**\n  - `gov rebuild --integration <branch>`, its link at the path `rebuild.yaml`'s `integration_store` names (W2-122's\n    key);\n  - a seed from a store behind the head names the base's head commit (12 hex digits or more) and says `behind`.\n- **`allowed_paths` widened:** S3 needs a plain `gov retrieve` in a launched session to answer from the integration\n  store. So the launcher's session env (`src/gov/launch/launcher.py`) and the place `gov retrieve` picks its root\n  (`src/gov/retrieve/command.py`) are added, with the evidence record. Use an environment variable the launch sets and\n  `gov retrieve` reads when no `--root` is given.\n- **The refresh after a merge seeds from the ready half,** so it re-embeds only what changed (the designer's N-1).\n- **A build whose semantic store is not recreated counts as failed** (N-2), as the CTO's script counts it.\n- **Untested (N-4):** a search through the link writes its question-vector cache into the ready half. The engineer\n  states whether a sandboxed session may write there, or where the cache goes instead.\n\n**Pass 1 merged (CTO, 2026-11-06, `75acb0ff`; review READY in round 2, `reviews/w2-116.md`).** For the next pass (S2),\nriding along (DEC-802):\n- **R2-F1:** `gov retrieve --root <link>` still resolves the link once per facet. Resolve the root once in\n  `_store_root` in both branches. The plain form with `GOV_STORE` is fixed.\n- **R2-F3:** a continuation token carries no mark of the half it was made on. Page 2, asked after a switch, pages the\n  other half. The parallel-agents test after window 4 measures it (DEC-1087 (10)).\n- **F7:** the merge queue's promotion builds with the clone's code. Retire it, or make it build with the pinned gov,\n  once the hook is live.\n- **Window 4's ACT** installs the hook with `flock -o` (R2-F2), `env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u\n  GOV_REBUILD_LOCK` (F5), and the separate `W2-00-store.refresh.lock` taken before the heavy slot (F6).\n- **F3,** a stale `index.lock` after a refresh killed during its checkout, is a row (not ordinary work).\n\n[DEC-1087]\n- **W2-60b dropped from deps (CTO, 2026-11-13 16:00, a plan-order P2, DEC-957):** S2 needs no W2-60b code (the session record, the role set, KNOWN_ROLES); with DEC-1167 (3) moving W2-60b after the copy starts, the dependency made a cycle W2-27 -> W2-116 -> W2-60b -> after W2-27's start. W2-33's rule text is delivered (closed). `src/gov/status/**` added for S2's `gov status` line.\n",
  "authority": [
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
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
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
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
      "id": "DEC-1087",
      "sha256": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DEC-719",
      "sha256": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "reason": "declared in sources",
      "tokens": 655
    },
    {
      "id": "DAEO-kia7",
      "sha256": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "reason": "declared in sources",
      "tokens": 896
    },
    {
      "id": "DAEO-lrre",
      "sha256": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "reason": "declared in sources",
      "tokens": 1622
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
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
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
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
      "id": "DEC-1087",
      "sha256": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DEC-719",
      "sha256": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "reason": "declared in sources",
      "tokens": 655
    },
    {
      "id": "DAEO-kia7",
      "sha256": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "reason": "declared in sources",
      "tokens": 896
    },
    {
      "id": "DAEO-lrre",
      "sha256": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "reason": "declared in sources",
      "tokens": 1622
    }
  ],
  "supplementary": [],
  "supplementary_query": "The designers' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer's retrieval reads (SMART-WORK-1)\n`gov rebuild --integration <branch>` keeps a store of that branch's head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] Verify: the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)]\nIt is refreshed after the nightly's verdict and at a set second time each day (both in the project's configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] Verify: pass 2's cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict and at the second time; `gov status` names the integration store's head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)]\n`gov launch independent-test-designer` points the session's retrieval at it; a designer's retrieval never reads a ticket worktree's store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role's plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]\nThe store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]\nA re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] Verify: the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)]\n`gov launch` points every worker session's retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer's; a designer's retrieval never reads a ticket worktree's store. Verify: a launcher unit test per worker role: the session environment names the integration store; a designer's never names a worktree's store [DEC-1087 (3), DEC-963] [added, the CTO's note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)]\nA designer's retrieval answered from a ticket worktree's store. Verify: tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)]\nThe link switched to a store whose build failed, or a search answered from a half-built store. Verify: the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)]\nA re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] Verify: the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 13755,
  "budget": {
    "limit": 16000,
    "used": 13755
  },
  "hash": "a3f8e46fed170cc5b159c6463e0bf82d5fba77ef518af26be3bd706970fdd49a"
}
