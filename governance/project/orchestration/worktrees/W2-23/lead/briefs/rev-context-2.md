{
  "ticket": "DAEO-kmcr",
  "ticket_text": "---\nid: DAEO-kmcr\nstatus: in_progress\ndeps: [DAEO-g0ip, DAEO-49o5]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-23\ntags: [wave-2, implementation, full]\nwbs_id: W2-23\ntitle: Adoption safety on a real repository\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-49o5\nallowed_paths:\n- src/gov/adopt/**\n- src/gov/adapters/**\n- template/governance/project/path-map.yaml\n- tests/unit/adopt/**\n- tests/unit/adapters/**\n- tests/acceptance/W1-41/test_w1_41_migration.py\n- fixtures/adopt/**\n- CLAUDE.md\n- AGENTS.md\n# .claude/settings.json out of the paths: a launched session cannot edit it (DEC-315), and a change to this repository's own file goes by ACT; the adapter code and the fixtures that merge such a file stay in the paths (the CTO's delegated decision, DEC-1112 (3))\nkpis:\n  success:\n  - 'Rollback never deletes an untracked file it did not create; it refuses or preserves. Verify: a planted fixture with one untracked file created by the user before an adoption batch and one created by the batch: after rollback the user''s file is present byte for byte (or the rollback refuses and names it) and the batch''s file is removed [W2-H036]'\n  - 'Adapter generation merges a programme''s own CLAUDE.md, AGENTS.md and .claude/settings.json instead of overwriting them, keeping their order. Verify: a planted programme whose three files each hold its own lines: after generation each file still holds every one of the programme''s lines in the original order plus the generated lines, and none is replaced by the generated file alone [W2-H050, W2-M232, W2-M312, W2-M229]'\n  - 'The A8 dependency proof finds every listed citation form. Verify: a planted set holding one citation of each listed form: the A8 proof prints every one of them as found, and a planted citation of an unlisted form is the only one not found [W2-H035, W2-M225]'\n  - 'A failed or interrupted batch leaves a resumable record and no half-staged state. Verify: a planted batch that fails at its third step, and one killed between steps: each leaves a record from which the resume command continues at the failed step, and `git status` shows nothing staged [W2-M219, W2-M220, W2-M224]'\n  - 'A project without .gitleaks.toml, or with a .gitignore that omits .gov-runtime/, is set up, not refused late. Verify: a planted project with neither the file nor the ignore line: adoption writes `.gitleaks.toml` and adds `.gov-runtime/` to `.gitignore` at set-up, and no later stage refuses for either [W2-M217, W2-M218, W2-M307]'\n  - 'Every command and hook works in a repository whose path contains a space (~/EXAMIN APP). Verify: a planted repository in a folder named `EXAMIN APP`: each `gov` command and each kernel hook run there exits as it does in a path without a space, and none prints a word-splitting or path error.'\n  - 'A move to a target that no namespace holds is refused before it runs. Verify: a planted move whose target path is in no namespace: the move is refused with a message naming the target, before any file is moved (the tree is unchanged) [W2-M216]'\n  failure:\n  - 'The fixture''s own instruction files and every untracked file survive an adoption and its rollback byte for byte. Verify: a planted fixture with instruction files and untracked files, sha256 listed before; after an adoption and its rollback the same listing is equal; any difference is named and fails.'\nprofile: FULL\nsources:\n- DEC-729\n- DEC-1052\n- DEC-954\n- DEC-315\n- DEC-1112\nest_loc: 220\nacceptance_tests:\n  path: tests/acceptance/W2-23/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\ncloses:\n- W2-H036\n- W2-H035\n- W2-H050\nlist_rows:\n- W2-H035\n- W2-H036\n- W2-H050\n- W2-I014\n- W2-L181\n- W2-L184\n- W2-L185\n- W2-L186\n- W2-L187\n- W2-L188\n- W2-L189\n- W2-L192\n- W2-L205\n- W2-L264\n- W2-L265\n- W2-M042\n- W2-M214\n- W2-M216\n- W2-M217\n- W2-M218\n- W2-M219\n- W2-M220\n- W2-M221\n- W2-M223\n- W2-M224\n- W2-M225\n- W2-M226\n- W2-M229\n- W2-M232\n- W2-M237\n- W2-M261\n- W2-M277\n- W2-M300\n- W2-M307\n- W2-M311\n- W2-M312\n- W2-M319\n---\n# W2-23 Adoption safety on a real repository\n\n**DEC-954:** depends on W2-16 (DAEO-49o5), not W2-18 (Wave 3). It shares src/gov/adopt/ with W2-52 and W2-88, split by file; whichever merges second merges back.\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-23), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/adopt/**`, `src/gov/adapters/**`, `template/governance/project/path-map.yaml`, `tests/unit/adopt/**`, `tests/unit/adapters/**`, `fixtures/adopt/**` (new: a repository with its own `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, untracked files, and a path with a space).\n- **KPIs, success:**\n  - Rollback never deletes an untracked file it did not create; it refuses or preserves [W2-H036].\n  - Adapter generation merges a programme's own `CLAUDE.md`, `AGENTS.md` and `.claude/settings.json` instead of overwriting them, keeping their order [W2-H050, W2-M232, W2-M312, W2-M229].\n  - The A8 dependency proof finds every listed citation form [W2-H035, W2-M225].\n  - A failed or interrupted batch leaves a resumable record and no half-staged state [W2-M219, W2-M220, W2-M224].\n  - A project without `.gitleaks.toml`, or with a `.gitignore` that omits `.gov-runtime/`, is set up, not refused late [W2-M217, W2-M218, W2-M307].\n  - Every command and hook works in a repository whose path contains a space (`~/EXAMIN APP`).\n  - A move to a target that no namespace holds is refused before it runs [W2-M216].\n- **KPIs, failure:** the fixture's own instruction files and every untracked file survive an adoption and its rollback byte for byte.\n\n## Interface (DEC-1052; the CTO's delegated decision, DEC-1112 (3), 2026-11-11: the lead's P-W2-23-2 as written, alternatives left out)\n\n1. S1 \"rollback\": the restore a failed stage or batch runs (`project.restore`, called by `project.commit` and `_batch`), not a new command. It deletes only paths the tool wrote and names in the call; every other untracked path stays byte for byte; an untracked directory does not raise. (Bootstrap.md 2393: \"A rollback deletes every untracked, non-ignored file; an untracked directory would make it raise.\")\n2. S4 \"resume command\": running `gov adopt --lite --stage A6` again resumes. A failed batch commits the A6 record with `status: failed`, `failed_batch: <n>`, the batches done with their commits and dispositions, and per-run rollback refs (`refs/gov/adoption/rollback/<run-id>/batch-<n>`); refusal code stays `ADOPT_BATCH_FAILED`. A killed batch (moves staged, no commit): the next A6 run finds the staged set equal to a recorded in-progress batch, unstages it to its rollback point and continues there; anything else staged is refused naming the paths (never reset).\n3. S5 \"set-up\": A0 writes `.gitleaks.toml` (the template's text) when absent and adds `.gov-runtime/` to `.gitignore` when not ignored, both in A0's record commit; an existing `.gitleaks.toml` is never touched; A3 and A8 then never refuse for either.\n4. S7: A3 refuses `ADOPT_TARGET_UNHELD`, naming each target no namespace holds, before its record is written (tree unchanged); A6 refuses the same before any batch.\n5. S2 \"adapter generation\": a new command `gov adapters generate` (src/gov/adapters/command.py; the CLI finds command modules by folder, so no change to src/gov/cli/main.py), which runs `rulesync generate` into a temporary folder and merges into the project: CLAUDE.md and AGENTS.md keep every programme line in order with the generated text in one marked block (`<!-- gov:generated begin -->` ... `end -->`) after them, replaced in place on the next run; `.claude/settings.json` is merged key by key, the programme's keys and list entries kept in their order, generated keys and hook entries added after, an `env` block merged with the programme's own entries first and no compaction threshold (DEC-838: every session uses its model's full window; W2-M229's 300k entry rests on DEC-636, which DEC-838 superseded; the CTO's P-W2-23-4 (b)).\n6. S3 \"listed citation forms\": the list of bootstrap.md line 2362: a word character or `-` directly before the path or id; backslashes; URL-encoding; another letter case; a path split across lines; a citation of only the store's folder or a glob; `../` followed by only the tail of the path; an id cited in a record's prose. The planted unlisted form (the one that must stay \"not found\") is the test designer's choice, named in the test.\n7. S6 \"each gov command and each kernel hook\": every name in `gov.cli.main` COMMANDS plus the discovered command modules, each with `--help` and with one real read invocation (status, doctor, retrieve, context --dry-run, adopt --lite --stage A0 on a clean fixture), and the six hooks of `template/governance/kernel/hooks/` fed a minimal event JSON, through the settings' own hook command lines, with `CLAUDE_PROJECT_DIR` holding a space. See P-W2-23-3 for where a fix would land.\n\n- **Delegated (the CTO, DEC-1112 (3), 2026-11-11), run 1's packages:** P-W2-23-1 (a): `src/gov/adopt/stages.py` (already\n  inside `src/gov/adopt/**`) may be edited for call sites only, in `a0`, `a3`, `_batch` and `a6` (about 20 lines), the logic\n  in a new `src/gov/adopt/safety.py`; W2-52's own change there (`run()` and `STAGE`) is not touched and no hunk overlaps;\n  whichever merges second merges back (DEC-954's rule). A narrowing of DEC-954's split by file to a split by function,\n  listed in the digest for the owner to overturn. P-W2-23-3 (a): S6 stays; a red whose fix lies outside the allowed paths\n  returns as a package naming the file and line.\n- **Delegated (the CTO, DEC-1112 (3), 2026-11-11), run 2's packages:** P-W2-23-4 (b): no compaction threshold in the\n  merged `env` block (`AUTO_COMPACT = {}`; DEC-838 standing), Interface item 5 reworded above; the S2 acceptance assertion\n  revised by the test designer under a Rewrite-Reason. P-W2-23-5 (a): `tests/acceptance/W1-41/test_w1_41_migration.py`\n  added to the paths for its one failed-batch case only, revised by W2-23's test designer to read the per-run rollback\n  refs (Rewrite-Reason: DEC-866, Interface item 2). P-W2-23-6 (b): the fixture programme moves under\n  `tests/unit/adapters/fixtures/programme/` (inside the paths), so no path-map change; `fixtures/adopt/**` stays unused.\n",
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
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
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
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
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
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DAEO-49o5",
      "sha256": "38642709ee0394471ddb1f59925facf9054a1c6d895f37dea382dae16f6b7759",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "38642709ee0394471ddb1f59925facf9054a1c6d895f37dea382dae16f6b7759",
      "reason": "declared in sources",
      "tokens": 259
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
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
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
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
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
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DAEO-49o5",
      "sha256": "38642709ee0394471ddb1f59925facf9054a1c6d895f37dea382dae16f6b7759",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "38642709ee0394471ddb1f59925facf9054a1c6d895f37dea382dae16f6b7759",
      "reason": "declared in sources",
      "tokens": 259
    }
  ],
  "supplementary": [],
  "supplementary_query": "Adoption safety on a real repository\nRollback never deletes an untracked file it did not create; it refuses or preserves. Verify: a planted fixture with one untracked file created by the user before an adoption batch and one created by the batch: after rollback the user's file is present byte for byte (or the rollback refuses and names it) and the batch's file is removed [W2-H036]\nAdapter generation merges a programme's own CLAUDE.md, AGENTS.md and .claude/settings.json instead of overwriting them, keeping their order. Verify: a planted programme whose three files each hold its own lines: after generation each file still holds every one of the programme's lines in the original order plus the generated lines, and none is replaced by the generated file alone [W2-H050, W2-M232, W2-M312, W2-M229]\nThe A8 dependency proof finds every listed citation form. Verify: a planted set holding one citation of each listed form: the A8 proof prints every one of them as found, and a planted citation of an unlisted form is the only one not found [W2-H035, W2-M225]\nA failed or interrupted batch leaves a resumable record and no half-staged state. Verify: a planted batch that fails at its third step, and one killed between steps: each leaves a record from which the resume command continues at the failed step, and `git status` shows nothing staged [W2-M219, W2-M220, W2-M224]\nA project without .gitleaks.toml, or with a .gitignore that omits .gov-runtime/, is set up, not refused late. Verify: a planted project with neither the file nor the ignore line: adoption writes `.gitleaks.toml` and adds `.gov-runtime/` to `.gitignore` at set-up, and no later stage refuses for either [W2-M217, W2-M218, W2-M307]\nEvery command and hook works in a repository whose path contains a space (~/EXAMIN APP). Verify: a planted repository in a folder named `EXAMIN APP`: each `gov` command and each kernel hook run there exits as it does in a path without a space, and none prints a word-splitting or path error.\nA move to a target that no namespace holds is refused before it runs. Verify: a planted move whose target path is in no namespace: the move is refused with a message naming the target, before any file is moved (the tree is unchanged) [W2-M216]\nThe fixture's own instruction files and every untracked file survive an adoption and its rollback byte for byte. Verify: a planted fixture with instruction files and untracked files, sha256 listed before; after an adoption and its rollback the same listing is equal; any difference is named and fails.",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 8037,
  "budget": {
    "limit": 10000,
    "used": 8037
  },
  "hash": "3a5c07b856e5c9fb466206ff0fd4a5d725dee82eb026054e190ea93ebcc8e8eb"
}
