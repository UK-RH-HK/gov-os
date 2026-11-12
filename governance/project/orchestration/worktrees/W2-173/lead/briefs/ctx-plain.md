{
  "ticket": "DAEO-qz4p",
  "ticket_text": "---\nid: DAEO-qz4p\nstatus: in_progress\ndeps: []\nlinks: [DAEO-52ku, DAEO-61vm, DAEO-k1e2, DAEO-p8tv]\ncreated: 2026-11-11T01:26:23Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-173\ntags: [wave-2, implementation, memory, audit, full, after-the-lift]\nwbs_id: W2-173\ntitle: 'The launch script''s follow-ups for the audit: the brief''s effort passed to the session, a stop word for writers and checkers, the notes'' and classes'' form checked at delivery (DEC-1120, DEC-1101 (2))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- governance/project/orchestration/tools/indep_launch.py\n- governance/project/orchestration/tools/indep-schemas/**\n- tests/unit/orchestration/test_w2_173*\n- docs/changes/W2-173-evidence.md\nkpis:\n  success:\n  - 'S1 A brief''s front matter may name `effort` (one of `low`, `medium`, `high`, `xhigh`, `max`), and the launch script passes it to the session as `--effort <value>` and records it in `WALL.json` and in `counts.json` (the counts schema gains one field, `effort`, a string or null). A brief with no `effort` runs as today, with no `--effort` flag and `effort: null`; a value outside the five refuses with code 10 before anything is built. Verify: planted briefs with `high`, no line, and `loud`: the stub `claude` receives `--effort high`, no `--effort`, and the third launch exits 10 with the wall folder unchanged; the five set-up A briefs (no `effort`) still pass stage 10 and build dry walls [DEC-1120 (2)-(3), DEC-1101 (2)]'\n  - 'S2 A writer''s or checker''s `result.json` may carry `stopped`, one of the closed words the labellers use (`none`, `input-missing`, `input-malformed`, `decisions-conflict`, `forbidden-read-needed`, `form-not-writable`, `not-sealed`); a result that says it stopped delivers nothing and ends with code 21 (`stopped`), with the word in `counts.json`, instead of the schema or missing-file code 20. The two result schemas gain `stopped` as an optional property. Verify: planted writer and checker results with each word: nothing delivered, exit 21, the word in the counts; a result with `none` and a set delivers as before; the first-version schemas still accept a result without `stopped` [DEC-1101 (2)]'\n  - 'S3 The checker''s `notes.md` is checked at delivery against the audit briefs'' fixed form: the heading `# Cross-check notes`, a `## Questions` section with one line per file of the set in id order (`<id> | accept|revise|reject | <codes or -> | also: <...> | <sentence>`), a `## The set` section with its five lines; and the three verdict counts in `result.json` equal the lines'' counts. A notes file that does not fit delivers nothing and ends with code 20. Verify: planted notes: well formed (delivered); a missing line, a fourth verdict word, an id not in the set, counts that disagree (each refused 20, nothing written to the set''s folder) [DEC-1101 (2)]'\n  - 'S4 The auditor''s `classes.json` is checked at delivery: one entry for each line of `input/misses.jsonl`, none for another id, each `class` one of the five, each `reason` one line of at most 200 characters, and the five counts of `result.json` equal the classes'' counts. Anything else delivers nothing and ends with code 20. Verify: planted classes: well formed (delivered); a missing id, an extra id, a sixth class, a two-line reason, counts that disagree (each refused 20) [DEC-1101 (2)]'\n  - 'S5 Nothing else about the launch script changes: every existing exit code, check and the five set-up A flows behave as at `2f98aecbc`. Verify: `gov accept W2-149`''s cases pass unchanged (206/0/3 passed, failed and skipped at the merge; the live cases run by the CTO), and a diff of the script outside the four changes above is empty [DEC-1112 (3), DEC-1113]'\n  failure:\n  - 'A session started without the effort its brief names; an invalid `effort` that builds a wall. Verify: S1''s planted briefs: with `high` the stub `claude` receives `--effort high`; with `loud` the launch exits 10 and the wall folder is unchanged'\n  - 'A stopped or malformed result delivered into a set''s folder or an audit''s folder. Verify: S2''s planted results with each stopped word, S3''s planted notes with a missing line and S4''s planted classes with a missing id: each is refused (21 or 20) and the set''s and the audit''s folders are byte-identical before and after'\n  - 'A change to the walls'' template files, the approved list, the path map or the guard; to a set-up A brief''s bytes; to any exit code''s meaning. Verify: `git diff --name-only` of the ticket''s branch against its base lists none of those files, and S5''s diff of the script outside the four changes is empty with `gov accept W2-149`''s cases unchanged'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: FULL\nsources:\n- DEC-1101\n- DEC-1120\n- DEC-1112\n- DEC-1113\n- DEC-1050\n- DEC-1073\nest_loc: 200\nacceptance_tests:\n  path: tests/acceptance/W2-173/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines and W2-149''s tests, before the engineer: planted sets root, HOME and repository, a stub `claude` on PATH; never the real ~/gov-os-eval, ~/gov-os-runs or ~/.claude'\ntrack: B\nlist_rows: []\nreads:  # declared by the CTO 11-11 (gov brief READS_MISSING; DEC-1121): what it reads that it does not write\n- governance/project/indep-walls/kinds.yaml\n- governance/project/orchestration/packages/MEMORY-AUDIT-1.md\nneeds:\n- governance/project/orchestration/tools/indep_launch.py\nwaits_on: []\n---\n# W2-173 The launch script's follow-ups for the audit\n\nFound while drafting the memory audit's fixed briefs (`packages/MEMORY-AUDIT-1.md`): the launch script builds the\nmemory kinds' walls, but three gaps stand between it and the audit. It passes no `--effort`, so RUBRIC-2's effort high\n(DEC-1120 (2)) is not enforced for an independent session. A writer or checker that must stop has no word for it (only\nset-up A's results have one), so its stop reads as a missing file. And the checker's notes and the auditor's classes are\ndelivered unchecked, though the next steps read them by their form.\n\n- **Base:** W2-149, merged at `2f98aecbc` (its ticket stays open for rows F37 and F40, which are not here). A change to\n  the script after the owner's approved list is applied runs under that list unchanged (ACT-W2-149-INSTALL-1 \u00a73, F34),\n  so no new yes is needed; the walls' template files are not touched.\n- **Alternatives (one line each):** put effort in the walls' `kinds.yaml` (rejected: a template change, so an ACT and\n  the owner's new hash); leave the notes unchecked and let W2-170 reject a malformed file (rejected: the delivery\n  would already have replaced the set's folder).\n- **From W2-170's Interface (row 147, the CTO's reading 1, 2026-11-11):** the auditor's copy of an audit's set excludes\n  `hidden/dropped/` (the dropped questions); every other file of the set is copied as today.\n- **Not here:** the briefs, the schedule, the measure.\n\n[DEC-1120 (2)-(3); DEC-1101 (2)]\n",
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
      "id": "DEC-1120",
      "sha256": "b8378fd74ee3dc964b53e23543a1e52430d9e27380711781f7b6d794442b5cff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b8378fd74ee3dc964b53e23543a1e52430d9e27380711781f7b6d794442b5cff",
      "reason": "declared in sources",
      "tokens": 798
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
      "id": "DEC-1113",
      "sha256": "0ac82541506e9e31f8425673b4695ff0e69fed0da9b139ee401698a930f32601",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0ac82541506e9e31f8425673b4695ff0e69fed0da9b139ee401698a930f32601",
      "reason": "declared in sources",
      "tokens": 420
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
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
      "id": "DEC-1120",
      "sha256": "b8378fd74ee3dc964b53e23543a1e52430d9e27380711781f7b6d794442b5cff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b8378fd74ee3dc964b53e23543a1e52430d9e27380711781f7b6d794442b5cff",
      "reason": "declared in sources",
      "tokens": 798
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
      "id": "DEC-1113",
      "sha256": "0ac82541506e9e31f8425673b4695ff0e69fed0da9b139ee401698a930f32601",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0ac82541506e9e31f8425673b4695ff0e69fed0da9b139ee401698a930f32601",
      "reason": "declared in sources",
      "tokens": 420
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    }
  ],
  "supplementary": [
    {
      "id": "44e7e9e078512dd052100a32",
      "path": "tests/acceptance/W1-49/README.md",
      "text": "    text. It also needs a rule for what such a line looks like, and no document gives one.\n  - (c) **A file the orchestrator keeps** (for example `.gov-runtime/scratch/orchestrator/PENDING_DECISIONS.md`),\n    which the hook copies. A real source, and a new duty for the orchestrator and a change to its prompt, which only\n    the owner changes.\n- **Impact.** (a): the tests stand. (b) or (c): `test_the_state_block_does_not_invent_the_pending_owner_decisions`\n  is rewritten to assert the copied lines; (c) adds a fixture file and a missing-file case.\n- **Reversibility.** High.\n- **Cost.** (a) one line; (b) about 5; (c) about 5, and the prompt change.\n- **Recommendation.** (a) now; (c) when W1-29 builds the full context packet, if the owner wants the decisions in\n  the block.\n- **Confidence.** Medium-high that (b) is wrong; medium on (a) against (c), because (a) reads DEC-264's \"holds the\n  pending owner decisions\" as \"has their line\".\n\n",
      "tokens": 237
    },
    {
      "id": "be5bcd346d47fac8fe9a9d01",
      "path": "tests/acceptance/W1-50/test_w1_50_freeze_records_file.py",
      "text": "\n\nLINK_TARGETS = {\n    \"an-acceptance-test-of-the-project\": _target_in_the_project,\n    \"a-file-outside-the-project\": _target_outside_the_project,\n    \"a-missing-file-outside-the-project\": _target_that_does_not_exist,\n}\n\n\n@pytest.mark.parametrize(\"target_kind\", sorted(LINK_TARGETS))\n",
      "tokens": 71
    },
    {
      "id": "4a7545ae78e97f536ef8b734",
      "path": "governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json",
      "text": "            \"integer\",\n            \"null\"\n          ],\n          \"minimum\": 0\n        },\n        \"instructions_ignored\": {\n          \"type\": [\n            \"integer\",\n            \"null\"\n          ],\n          \"minimum\": 0\n        },\n        \"stopped\": {\n          \"type\": [\n            \"string\",\n            \"null\"\n          ],\n          \"enum\": [\n            \"none\",\n            \"input-missing\",\n            \"input-malformed\",\n            \"decisions-conflict\",\n            \"forbidden-read-needed\",\n            \"form-not-writable\",\n            \"not-sealed\",\n            null\n          ]\n        }\n      },\n      \"description\": \"Every key of required is on every result; set-up A's flows (DEC-1112 (3), DEC-1113) add the numbers of their own result under the other keys, each only when the result gives it.\"\n    },\n    \"delivered\": {\n      \"type\": \"object\",\n      \"additionalProperties\": false,\n      \"required\": [\n        \"files\",\n        \"sha256\",\n        \"to\"\n      ],\n      \"properties\": {\n        \"files\": {\n          \"type\": [\n            \"integer\",\n            \"null\"\n          ],\n          \"minimum\": 0\n        },\n        \"sha256\": {\n          \"type\": [\n            \"string\",\n",
      "tokens": 296
    },
    {
      "id": "d98ddfbacbfd98021465b4eb",
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "text": "DISPUTE_ACTION = (\"role\", \"agent\", \"ticket\", \"wbs\", \"tool\", \"input\", \"cwd\")\nLABEL_PART = (\"label\", \"rule_class\", \"clauses\", \"reason\")\nLABELS = (\"allow\", \"refuse\", \"ask\")\nAUDIT_SPLIT = 40                  # the overlap auditor's cases per run (the CTO's delegated split)\nSGX_OUT = (\"round\", \"cases\", \"copies\", \"near_miss\", \"not_executable\", \"rules\", \"hand_labelled\", \"ask\", \"by_class\",\n           \"uncertain_seen\", \"sample\", \"decided\", \"agrees_x\", \"agrees_y\", \"neither\", \"cannot_settle\",\n           \"may_change_verdict\", \"instructions_ignored\", \"stopped\", \"labelled\", \"allow\", \"refuse\")\nSTOPPED = (\"none\", \"input-missing\", \"input-malformed\", \"decisions-conflict\", \"forbidden-read-needed\",\n           \"form-not-writable\", \"not-sealed\")\n# The confined rule script (S25): its caps; the prelude below sets them inside the sandbox before the script's code runs.\nRULES_WALL_S = 20                 # wall-clock seconds (at most 60)\nRULES_CPU_S = 15\nRULES_AS = 1 << 30                # address space, bytes\nRULES_NOFILE = 32\nRULES_OUT_BASE = 1 << 20          # stdout cap: this much plus RULES_OUT_PER_ID per staged id\nRULES_OUT_PER_ID = 4096\nFILE_BUDGET = 8000\n",
      "tokens": 289
    },
    {
      "id": "d9124e395d08107e006bfca7",
      "path": "tests/acceptance/W2-149/w2_149_setup_a.py",
      "text": "\n\n# S31: the refused forms of rule_class, as JSON text (the param id, the value).\nBAD_CLASS = {\"true\": \"true\", \"float-7.0\": \"7.0\", \"zero\": \"0\", \"fifteen\": \"15\", \"leading-zero\": '\"07\"',\n             \"leading-space\": '\" 7\"', \"plus-sign\": '\"+7\"', \"word\": '\"seven\"'}\n\n# S29: a stopped word each flow's brief allows (the briefs' result sections), other than none.\nSTOP_WORD = {\"writer-tuning\": \"form-not-writable\", \"writer-heldout\": \"not-sealed\", \"labeller-r1\": \"input-malformed\",\n             \"labeller-2-r1\": \"decisions-conflict\", \"labeller-2-r2\": \"forbidden-read-needed\",\n             \"labeller-r2\": \"input-missing\", \"overlap-auditor\": \"input-malformed\"}\nCONFLICTS = \"# Conflicts (planted)\\n- DEC-820 (4), DEC-1093 (2)\\n\"\n\n\n",
      "tokens": 181
    },
    {
      "id": "e84878d4efc576f149317f85",
      "path": "tests/acceptance/W2-149/w2_149_setup_a.py",
      "text": "        \"labeller\": (\"labeller\", \"sgx1/labeller\", \"sgx1-labeller\", \"sgx1-labeller-1\"),\n        \"labeller-2\": (\"labeller\", \"sgx1/labeller-2\", \"sgx1-labeller-2\", \"sgx1-labeller-2\"),\n        \"overlap-auditor\": (\"auditor\", \"sgx1/overlap-auditor\", \"sgx1-overlap-auditor\", \"sgx1-overlap-auditor\")}\nSCHEMA = {f: f\"sgx1-{f}-result.schema.json\" for f in FLOW}\nENTRY_MODEL = {\"writer-tuning\": \"claude-entry-writer-tuning\", \"writer-heldout\": None,\n               \"labeller\": \"claude-entry-labeller\", \"labeller-2\": \"claude-entry-labeller-2\",\n               \"overlap-auditor\": \"claude-entry-overlap-auditor\"}\nKIND_MODEL = {k: f\"claude-kind-{k}\" for k in support.KINDS}\nHALVES = (\"tuning\", \"held-out\")\nFIELDS = (\"id\", \"role\", \"agent\", \"ticket\", \"wbs\", \"tool\", \"input\", \"cwd\", \"executable\", \"strata\", \"source\")\nACTION7 = (\"role\", \"agent\", \"ticket\", \"wbs\", \"tool\", \"input\", \"cwd\")\nLABEL4 = (\"label\", \"rule_class\", \"clauses\", \"reason\")\nMERGED = (\"id\", \"label\", \"rule_class\", \"clauses\", \"reason\", \"how\")\nTO_WORDS = (\"cases\", \"round1\", \"labels\", \"decisions\")\nSTOPPED_WORDS = (\"none\", \"input-missing\", \"input-malformed\", \"decisions-conflict\", \"forbidden-read-needed\",\n                 \"form-not-writable\", \"not-sealed\")\n",
      "tokens": 300
    },
    {
      "id": "e3e76b67b475abf4fee5dae2",
      "path": "governance/project/indep-briefs/sgx1/labeller-2.md",
      "text": "## 6. Your result (counts only)\nYour last act in each round is `out/result.json`, holding numbers and fixed words only:\n- round 1: `{\"round\": 1, \"rules\": n, \"instructions_ignored\": n, \"stopped\": <word>}`;\n- round 2: `{\"round\": 2, \"sample\": n, \"labelled\": n, \"allow\": n, \"refuse\": n, \"ask\": n, \"by_class\": {\"1\": n, ...\n  \"14\": n}, \"instructions_ignored\": n, \"stopped\": <word>}`.\n\n`stopped` is one of `none`, `input-missing`, `input-malformed`, `decisions-conflict`, `forbidden-read-needed`. Never put\nan id, an action's text, a path or a reason in `result.json`. The launch script computes every file's sha256 itself.\n\n",
      "tokens": 155
    },
    {
      "id": "64f9bc9b4e172c9cb34f15a4",
      "path": "governance/project/indep-briefs/sgx1/labeller.md",
      "text": "## 7. Your result (counts only)\nYour last act in each round is `out/result.json`, holding numbers and fixed words only:\n- round 1: `{\"round\": 1, \"rules\": <lines in the rulebook>, \"instructions_ignored\": n, \"stopped\": <word>}`;\n- round 2: `{\"round\": 2, \"hand_labelled\": n, \"allow\": n, \"refuse\": n, \"ask\": n, \"by_class\": {\"1\": n, ... \"14\": n},\n  \"uncertain_seen\": n, \"sample\": n, \"instructions_ignored\": n, \"stopped\": <word>}`.\n\n`stopped` is one of `none`, `input-missing`, `input-malformed`, `decisions-conflict`, `forbidden-read-needed`. Nothing\nelse leaves your folder except what the launch script delivers. Never put an id, an action's text, a path or a reason\nin `result.json`. The launch script computes every file's sha256 itself.\n\n",
      "tokens": 185
    },
    {
      "id": "30fad5234d123c4658854041",
      "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-2-result.schema.json",
      "text": "              \"minimum\": 0\n            },\n            \"10\": {\n              \"type\": \"integer\",\n              \"minimum\": 0\n            },\n            \"11\": {\n              \"type\": \"integer\",\n              \"minimum\": 0\n            },\n            \"12\": {\n              \"type\": \"integer\",\n              \"minimum\": 0\n            },\n            \"13\": {\n              \"type\": \"integer\",\n              \"minimum\": 0\n            },\n            \"14\": {\n              \"type\": \"integer\",\n              \"minimum\": 0\n            }\n          }\n        },\n        \"instructions_ignored\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"stopped\": {\n          \"type\": \"string\",\n          \"enum\": [\n            \"none\",\n            \"input-missing\",\n            \"input-malformed\",\n            \"decisions-conflict\",\n            \"forbidden-read-needed\"\n          ]\n        }\n      }\n    }\n  ]\n}\n",
      "tokens": 225
    },
    {
      "id": "586837954ad6955a2058e284",
      "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-2-result.schema.json",
      "text": "{\n  \"$schema\": \"https://json-schema.org/draft/2020-12/schema\",\n  \"$id\": \"sgx1-labeller-2-result.schema.json\",\n  \"title\": \"SANDBOX-GUARD-EXP-1's second labeller: out/result.json, round 1 or round 2 (its brief's section 6: numbers and fixed words only; W2-149, DEC-1112 (3))\",\n  \"type\": \"object\",\n  \"additionalProperties\": false,\n  \"required\": [\n    \"round\"\n  ],\n  \"properties\": {\n    \"round\": {\n      \"type\": \"integer\",\n      \"enum\": [\n        1,\n        2\n      ]\n    },\n    \"rules\": {\n      \"type\": \"integer\",\n      \"minimum\": 0\n    },\n    \"instructions_ignored\": {\n      \"type\": \"integer\",\n      \"minimum\": 0\n    },\n    \"stopped\": {\n      \"type\": \"string\",\n      \"enum\": [\n        \"none\",\n        \"input-missing\",\n        \"input-malformed\",\n        \"decisions-conflict\",\n        \"forbidden-read-needed\"\n      ]\n    },\n    \"sample\": {\n      \"type\": \"integer\",\n      \"minimum\": 0\n    },\n    \"labelled\": {\n      \"type\": \"integer\",\n      \"minimum\": 0\n    },\n    \"allow\": {\n      \"type\": \"integer\",\n      \"minimum\": 0\n    },\n    \"refuse\": {\n      \"type\": \"integer\",\n      \"minimum\": 0\n    },\n    \"ask\": {\n      \"type\": \"integer\",\n      \"minimum\": 0\n    },\n    \"by_class\": {\n      \"type\": \"object\",\n",
      "tokens": 299
    },
    {
      "id": "98a59c87343910633deb71c7",
      "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-2-result.schema.json",
      "text": "          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"10\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"11\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"12\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"13\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"14\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        }\n      }\n    }\n  },\n  \"anyOf\": [\n    {\n      \"type\": \"object\",\n      \"additionalProperties\": false,\n      \"required\": [\n        \"round\",\n        \"rules\",\n        \"instructions_ignored\",\n        \"stopped\"\n      ],\n      \"properties\": {\n        \"round\": {\n          \"type\": \"integer\",\n          \"const\": 1\n        },\n        \"rules\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"instructions_ignored\": {\n          \"type\": \"integer\",\n          \"minimum\": 0\n        },\n        \"stopped\": {\n          \"type\": \"string\",\n          \"enum\": [\n            \"none\",\n            \"input-missing\",\n            \"input-malformed\",\n            \"decisions-conflict\",\n            \"forbidden-read-needed\"\n          ]\n        }\n      }\n",
      "tokens": 300
    }
  ],
  "supplementary_query": "The launch script's follow-ups for the audit: the brief's effort passed to the session, a stop word for writers and checkers, the notes' and classes' form checked at delivery (DEC-1120, DEC-1101 (2))\nS1 A brief's front matter may name `effort` (one of `low`, `medium`, `high`, `xhigh`, `max`), and the launch script passes it to the session as `--effort <value>` and records it in `WALL.json` and in `counts.json` (the counts schema gains one field, `effort`, a string or null). A brief with no `effort` runs as today, with no `--effort` flag and `effort: null`; a value outside the five refuses with code 10 before anything is built. Verify: planted briefs with `high`, no line, and `loud`: the stub `claude` receives `--effort high`, no `--effort`, and the third launch exits 10 with the wall folder unchanged; the five set-up A briefs (no `effort`) still pass stage 10 and build dry walls [DEC-1120 (2)-(3), DEC-1101 (2)]\nS2 A writer's or checker's `result.json` may carry `stopped`, one of the closed words the labellers use (`none`, `input-missing`, `input-malformed`, `decisions-conflict`, `forbidden-read-needed`, `form-not-writable`, `not-sealed`); a result that says it stopped delivers nothing and ends with code 21 (`stopped`), with the word in `counts.json`, instead of the schema or missing-file code 20. The two result schemas gain `stopped` as an optional property. Verify: planted writer and checker results with each word: nothing delivered, exit 21, the word in the counts; a result with `none` and a set delivers as before; the first-version schemas still accept a result without `stopped` [DEC-1101 (2)]\nS3 The checker's `notes.md` is checked at delivery against the audit briefs' fixed form: the heading `# Cross-check notes`, a `## Questions` section with one line per file of the set in id order (`<id> | accept|revise|reject | <codes or -> | also: <...> | <sentence>`), a `## The set` section with its five lines; and the three verdict counts in `result.json` equal the lines' counts. A notes file that does not fit delivers nothing and ends with code 20. Verify: planted notes: well formed (delivered); a missing line, a fourth verdict word, an id not in the set, counts that disagree (each refused 20, nothing written to the set's folder) [DEC-1101 (2)]\nS4 The auditor's `classes.json` is checked at delivery: one entry for each line of `input/misses.jsonl`, none for another id, each `class` one of the five, each `reason` one line of at most 200 characters, and the five counts of `result.json` equal the classes' counts. Anything else delivers nothing and ends with code 20. Verify: planted classes: well formed (delivered); a missing id, an extra id, a sixth class, a two-line reason, counts that disagree (each refused 20) [DEC-1101 (2)]\nS5 Nothing else about the launch script changes: every existing exit code, check and the five set-up A flows behave as at `2f98aecbc`. Verify: `gov accept W2-149`'s cases pass unchanged (206/0/3 passed, failed and skipped at the merge; the live cases run by the CTO), and a diff of the script outside the four changes above is empty [DEC-1112 (3), DEC-1113]\nA session started without the effort its brief names; an invalid `effort` that builds a wall. Verify: S1's planted briefs: with `high` the stub `claude` receives `--effort high`; with `loud` the launch exits 10 and the wall folder is unchanged\nA stopped or malformed result delivered into a set's folder or an audit's folder. Verify: S2's planted results with each stopped word, S3's planted notes with a missing line and S4's planted classes with a missing id: each is refused (21 or 20) and the set's and the audit's folders are byte-identical before and after\nA change to the walls' template files, the approved list, the path map or the guard; to a set-up A brief's bytes; to any exit code's meaning. Verify: `git diff --name-only` of the ticket's branch against its base lists none of those files, and S5's diff of the script outside the four changes is empty with `gov accept W2-149`'s cases unchanged\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "3289a20d9fbb4c27d6a0bfeb",
      "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-result.schema.json"
    },
    {
      "id": "6ee74cf84fb150305a7393b1",
      "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-result.schema.json"
    },
    {
      "id": "cbe8f988de3772527e2ae853",
      "path": "tests/unit/orchestration/test_w2_149_setup_a.py"
    },
    {
      "id": "7f2de125f29be72fe93353f0",
      "path": "tests/unit/orchestration/test_w2_149_setup_a.py"
    },
    {
      "id": "b68fc3ae74f148d4ce6662a0",
      "path": "governance/project/indep-briefs/sgx1/writer-heldout.md"
    },
    {
      "id": "a8c5139664431215efd59f7c",
      "path": "governance/project/indep-briefs/sgx1/writer-tuning.md"
    },
    {
      "id": "9f065cb13feeb0b28e0e171b",
      "path": "governance/project/orchestration/tools/indep-schemas/sgx1-writer-heldout-result.schema.json"
    },
    {
      "id": "bfb4d44a6cdc10ad4bfa4956",
      "path": "governance/project/orchestration/tools/indep-schemas/sgx1-writer-tuning-result.schema.json"
    },
    {
      "id": "97decb13b71ab9e511e280ca",
      "path": "governance/project/indep-briefs/sgx1/overlap-auditor.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "44e7e9e078512dd052100a32",
          "path": "tests/acceptance/W1-49/README.md"
        },
        {
          "id": "be5bcd346d47fac8fe9a9d01",
          "path": "tests/acceptance/W1-50/test_w1_50_freeze_records_file.py"
        },
        {
          "id": "4a7545ae78e97f536ef8b734",
          "path": "governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json"
        },
        {
          "id": "d98ddfbacbfd98021465b4eb",
          "path": "governance/project/orchestration/tools/indep_launch.py"
        },
        {
          "id": "d9124e395d08107e006bfca7",
          "path": "tests/acceptance/W2-149/w2_149_setup_a.py"
        },
        {
          "id": "e84878d4efc576f149317f85",
          "path": "tests/acceptance/W2-149/w2_149_setup_a.py"
        },
        {
          "id": "e3e76b67b475abf4fee5dae2",
          "path": "governance/project/indep-briefs/sgx1/labeller-2.md"
        },
        {
          "id": "64f9bc9b4e172c9cb34f15a4",
          "path": "governance/project/indep-briefs/sgx1/labeller.md"
        },
        {
          "id": "30fad5234d123c4658854041",
          "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-2-result.schema.json"
        },
        {
          "id": "586837954ad6955a2058e284",
          "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-2-result.schema.json"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "98a59c87343910633deb71c7",
          "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-2-result.schema.json"
        },
        {
          "id": "3289a20d9fbb4c27d6a0bfeb",
          "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-result.schema.json"
        },
        {
          "id": "6ee74cf84fb150305a7393b1",
          "path": "governance/project/orchestration/tools/indep-schemas/sgx1-labeller-result.schema.json"
        },
        {
          "id": "cbe8f988de3772527e2ae853",
          "path": "tests/unit/orchestration/test_w2_149_setup_a.py"
        },
        {
          "id": "7f2de125f29be72fe93353f0",
          "path": "tests/unit/orchestration/test_w2_149_setup_a.py"
        },
        {
          "id": "b68fc3ae74f148d4ce6662a0",
          "path": "governance/project/indep-briefs/sgx1/writer-heldout.md"
        },
        {
          "id": "a8c5139664431215efd59f7c",
          "path": "governance/project/indep-briefs/sgx1/writer-tuning.md"
        },
        {
          "id": "9f065cb13feeb0b28e0e171b",
          "path": "governance/project/orchestration/tools/indep-schemas/sgx1-writer-heldout-result.schema.json"
        },
        {
          "id": "bfb4d44a6cdc10ad4bfa4956",
          "path": "governance/project/orchestration/tools/indep-schemas/sgx1-writer-tuning-result.schema.json"
        },
        {
          "id": "97decb13b71ab9e511e280ca",
          "path": "governance/project/indep-briefs/sgx1/overlap-auditor.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "3289a20d9fbb4c27d6a0bfeb",
      "reason": "budget exceeded"
    },
    {
      "id": "6ee74cf84fb150305a7393b1",
      "reason": "budget exceeded"
    },
    {
      "id": "7f2de125f29be72fe93353f0",
      "reason": "budget exceeded"
    },
    {
      "id": "97decb13b71ab9e511e280ca",
      "reason": "budget exceeded"
    },
    {
      "id": "9f065cb13feeb0b28e0e171b",
      "reason": "budget exceeded"
    },
    {
      "id": "a8c5139664431215efd59f7c",
      "reason": "budget exceeded"
    },
    {
      "id": "b68fc3ae74f148d4ce6662a0",
      "reason": "budget exceeded"
    },
    {
      "id": "bfb4d44a6cdc10ad4bfa4956",
      "reason": "budget exceeded"
    },
    {
      "id": "cbe8f988de3772527e2ae853",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-qz4p): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 8889,
  "budget": {
    "limit": 9000,
    "used": 8889
  },
  "hash": "d7dbcbc203c22231b713b0c8d102d709c94ae450c3c12f0839802ce982e6a1ec"
}
