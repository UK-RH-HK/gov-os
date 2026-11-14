{
  "ticket": "DAEO-zlog",
  "ticket_text": "---\nid: DAEO-zlog\nwbs_id: W2-188\nexternal-ref: W2-188\ntitle: \"The adopt skill's step 6 and the practice record say the verdict set becomes the standing set, judged every week at 95 %, counts only, checked monthly against a fresh set; A9's weekly cron line named (MEMORY-AUDIT G6 and G4's text; CIT-P)\"\ntype: task\nclass: spec\nrole: product-spec\nprofile: STANDARD\nstatus: open\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-14\ndeps: [DAEO-pg6i]\nallowed_paths:\n- template/governance/kernel/skills/adopt/SKILL.md\n- .rulesync/skills/adopt/SKILL.md\n- template/.rulesync/skills/adopt/SKILL.md\n- docs/research/W2-88-memory-practice.md\n- docs/changes/W2-188-CIT-P.md\n- docs/probes/DAEO-zlog/**\nreads:\n- .gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md\n- .gov-runtime/scratch/orchestrator/governance/project/orchestration/packages/MEMORY-AUDIT-P1.md\n- .gov-runtime/scratch/orchestrator/drafts/memory-scope-20261113/MEMORY-AUDIT.md\n- docs/changes/W2-88a-CIT-P.md\n- docs/changes/W2-98-CIT-P.md\n- tests/acceptance/W2-88a/**\n- tests/acceptance/W2-11/**\n- governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md\n- governance/project/orchestration/packages/LIFT-1/E3-RESULT.md\nneeds:\n- template/governance/kernel/skills/adopt/SKILL.md\nwaits_on:\n- ref: DAEO-0cd2\n  reason: 'the promotion and the copies ACT follow W2-187''s merge, so the generated copy never states a mode the product lacks; the text itself names no subcommand and is written in parallel'\nest_loc: 60\nkpis:\n  success:\n  - 'S1 A9''s step 6 in the adopt skill says, in its own words: the verdict set is declared and measured once at Wave 0 as the first verdict; from then on it is the repository''s standing set, judged end to end every week on the same questions (monthly once the repository is stable, under the package''s O3 (b)) as Gov OS''s memory is judged (the standard''s bundle read whole by the reader, search again once), against 95 %, behind the walls, with only counts leaving its run; it never chooses or judges a fix (fixes chosen on the tuning set and the fresh sets'' misses); a fresh set each month checks it for fitting and a fitted set is replaced; a miss is never re-run in the same week and never re-scored; it cites DEC-1179 [DEC-1179 (1)-(4), DEC-1176 (1), DEC-1098 (1)] Verify: a string test on step 6''s stretch of the three copies finds each of these statements (standing set, every week, same questions, 95 %, counts only, never chooses a fix, fresh set monthly, fitted replaced, DEC-1179); W2-88a''s step matcher (`check_steps`) returns no problem on A9''s section'\n  - 'S2 After A9''s seven steps, one paragraph says the weekly audit runs from one cron line that A9''s ACT package gives the repository''s owner''s operator beside the walls, never installed by adoption, and that a fall below 95 % is handled as the practice record''s section 9 states [DEC-1179 (4), (5), DEC-1101 (2)] Verify: a string test finds the paragraph between step 7 and the `## Verify clauses for adopted tickets` heading in all three copies, with \"cron\", \"ACT\", \"operator\", \"never installs\" (or \"never installed\") and \"95 %\"'\n  - 'S3 The practice record states the standing set: \u00a73''s confirmation line, \u00a75 item 6''s practice lines and \u00a76 step 6 re-worded as the CIT-P quotes, and a new \u00a79 \"The standing set (DEC-1179)\" with what it is, the method (the reader ranking the whole bundle and searching again once, A2, with the E2 and E3 figures), the bar, the walls (counts only, no id read by anyone), fixes never chosen on it, staleness by count, the monthly check against fitting with its two 5-point rules, and DEC-1179 (4)''s rule below 95 % word for word [DEC-1179, DEC-1074 (1), DEC-1074 (4), DEC-1072 (2)] Verify: a string test on each named place of `docs/research/W2-88-memory-practice.md`; \u00a76 still passes W2-88a''s step matcher; \u00a79''s below-95 text equals DEC-1179 (4)''s as recorded'\n  - 'S4 The three copies of the skill are byte-equal; the version goes from \"1.0.0\" to \"1.1.0\" in all three (the next minor if W2-88a''s promotion has taken 1.1.0 by then); nothing else in the skill changes but step 6, the new paragraph, the governing sources line (adding DEC-1101, DEC-1125 and DEC-1179) and the version [CAP-33, DEC-832 item 2, DEC-981] Verify: sha256 of the three copies equal; `git diff` of the kernel copy against the base touches only those four places; `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0'\n  - 'S5 The CIT-P record `docs/changes/W2-188-CIT-P.md` gives the skill''s sha256 before and after, the lines added and removed, the old and new text of each changed place, the impact table (W2-11''s body case red until the copies ACT; W2-88a''s cases unchanged), the independent review''s verdict and the owner''s approval line of the bytes before the merge [CAP-33, DEC-105] Verify: the record holds both hashes (the after equal to the kernel copy at the ticket''s last commit), the counts, a `verdict: PASS` as the last verdict and an `owner_approval:` line naming the sha256'\n  failure:\n  - 'F1 Any other step, section or rule of the adopt skill changes, or the skill grants a permission, names a `gov.memaudit` subcommand or states a mode the product lacks. Verify: the S4 diff; a grep of the three copies for `gov.memaudit` and `standing declare` finds nothing'\n  - 'F2 The ticket writes `.claude/skills/adopt/SKILL.md` or any test under `tests/acceptance/`. Verify: the close''s diff names neither; the copies ACT regenerates the `.claude` copy after the owner''s approval'\n  - 'F3 The text says the standing set may be used to choose, judge, adopt or reject a fix, prints or reads a question id, or calls the reader a second reranking model. Verify: a string test on step 6 and \u00a79 for \"never chooses or judges a fix\" and \"counts only\"; \u00a79 says W2-88 S10''s second reranker stays forbidden'\nnon_goals:\n- 'no code: the standing mode, the bar, the per-repository state, the maintenance pass and the cron line in the ACT package''s text are W2-187'\n- 'no `.claude/` copy (the copies ACT) and no acceptance test (the test designer)'\n- 'no change to A9''s other six steps, to the Verify section or to W2-88''s closed ticket (its lines are re-baselined by the CTO''s record edit under DEC-1179 (7))'\n- 'no change to W2-88 S10''s standard or the forbidden second reranking model'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1074, DEC-1071, DEC-1072, DEC-105, DEC-974, CAP-33, DAEO-pg6i, DAEO-2bdu]\nacceptance_tests: {path: tests/acceptance/W2-188/}\n---\n\n# W2-188 The adopt skill's step 6 and the practice record: the standing set\n\n**Problem.** The adopt skill's A9 step 6 (`template/governance/kernel/skills/adopt/SKILL.md:58`, and the two `.rulesync`\ncopies) says: \"Declare and measure the verdict set once. A miss stands as it is: the set is never run again.\" The\npractice record says \"measured once\" in three places (`docs/research/W2-88-memory-practice.md:91-92, 190-191, 221`).\nDEC-1176 (1) kept them standing until the weekly re-measure was decided. The owner decided it on 2026-11-14 (DEC-1179,\nprovisional): the verdict set stays as each repository's standing set, judged every week at 95 %, counts only, checked\nmonthly against a fresh set.\n\n**Approach.** Re-word step 6 and add one paragraph after the seven steps, as `drafts/memory-audit-p1/W2-188-CIT-P.md`\n\u00a72.1 quotes. The proposed step 6 keeps \"declare\", \"measure\", \"the verdict set\" and \"once\", so W2-88a's matcher passes\nunrevised; this was checked on the draft's text. Re-word the practice record's three places and add its \u00a79 (\u00a72.2). Bump\nthe version and write the CIT-P. The skill names no subcommand, so the text does not wait for W2-187. Its promotion and\nthe `.claude` copies ACT come after W2-187 merges (W2-88a's finding F4).\n\n**Rabbit holes.**\n- Do not restate the method's figures in the skill: they belong in the practice record.\n- Do not touch step 5's 5 points or \u00a73's 3 points (a known older wording, left as is).\n- Do not write the below-95 rule before DEC-1179 (4) is recorded. Copy it word for word.\n\n**Filed 2026-11-14 on the owner's decision (DEC-1179, MEMORY-AUDIT-P1), by the CIT-P route (W2-188's CIT-P draft: `.gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md`).** The kernel bytes need the owner's approval of the CIT-P before the merge (DEC-1166 (4)); the `.claude` copy follows by a copies ACT.\n",
  "authority": [
    {
      "id": "DEC-1179",
      "sha256": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "reason": "declared in sources",
      "tokens": 6606
    },
    {
      "id": "DEC-1176",
      "sha256": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "reason": "declared in sources",
      "tokens": 1994
    },
    {
      "id": "DEC-1101",
      "sha256": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "reason": "declared in sources",
      "tokens": 884
    },
    {
      "id": "DEC-1125",
      "sha256": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "reason": "declared in sources",
      "tokens": 954
    },
    {
      "id": "DEC-1126",
      "sha256": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "reason": "declared in sources",
      "tokens": 667
    },
    {
      "id": "DEC-1098",
      "sha256": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "reason": "declared in sources",
      "tokens": 886
    },
    {
      "id": "DEC-1097",
      "sha256": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "reason": "declared in sources",
      "tokens": 1535
    },
    {
      "id": "DEC-1074",
      "sha256": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "reason": "declared in sources",
      "tokens": 903
    },
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-974",
      "sha256": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    },
    {
      "id": "DAEO-pg6i",
      "sha256": "fc5d8cbc94b01d18f6e1bb9c75f1500a9282eda9ff6f2b6464928a1240de0adb",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "fc5d8cbc94b01d18f6e1bb9c75f1500a9282eda9ff6f2b6464928a1240de0adb",
      "reason": "declared in sources",
      "tokens": 476
    },
    {
      "id": "DAEO-2bdu",
      "sha256": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "reason": "declared in sources",
      "tokens": 13611
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1179",
      "sha256": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "reason": "declared in sources",
      "tokens": 6606
    },
    {
      "id": "DEC-1176",
      "sha256": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "reason": "declared in sources",
      "tokens": 1994
    },
    {
      "id": "DEC-1101",
      "sha256": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "reason": "declared in sources",
      "tokens": 884
    },
    {
      "id": "DEC-1125",
      "sha256": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "reason": "declared in sources",
      "tokens": 954
    },
    {
      "id": "DEC-1126",
      "sha256": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "reason": "declared in sources",
      "tokens": 667
    },
    {
      "id": "DEC-1098",
      "sha256": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "reason": "declared in sources",
      "tokens": 886
    },
    {
      "id": "DEC-1097",
      "sha256": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "reason": "declared in sources",
      "tokens": 1535
    },
    {
      "id": "DEC-1074",
      "sha256": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "reason": "declared in sources",
      "tokens": 903
    },
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-974",
      "sha256": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    },
    {
      "id": "DAEO-pg6i",
      "sha256": "fc5d8cbc94b01d18f6e1bb9c75f1500a9282eda9ff6f2b6464928a1240de0adb",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "fc5d8cbc94b01d18f6e1bb9c75f1500a9282eda9ff6f2b6464928a1240de0adb",
      "reason": "declared in sources",
      "tokens": 476
    },
    {
      "id": "DAEO-2bdu",
      "sha256": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "reason": "declared in sources",
      "tokens": 13611
    }
  ],
  "supplementary": [
    {
      "id": "66b15001fc9e12b19a4b57be",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "text": "# MEMORY-AUDIT-P1: the standing hidden set, two tickets and the adopt skill's CIT-P, for the owner's decision\n\n> **Decided 2026-11-14 (DEC-1179):** the owner's yes, with O3 (b) (\"weekly while a repository is actively worked on, monthly once it is stable, back to weekly at once on a miss, a retrieval change or churn of 10 % or more\"). The draft's \"DEC-1177\" reads DEC-1179 throughout (DEC-1177 went to P-W2-184-1). W2-187 is DAEO-0cd2, W2-188 is DAEO-zlog.\n\n2026-11-14. Drafted by a helper of the CTO (orchestrator DAEO-sdxk). Nothing is filed, recorded or committed. No sets root,\nrun folder or hidden file was opened.\n\nThe decision is numbered DEC-1179 here, provisionally. DEC-1176 is the W2-88b decision: the owner said yes at 00:33, and\nit is not yet recorded. The tickets are W2-187 and W2-188, the next free W2 numbers after W2-186. Their tk ids are\nassigned at filing; the drafts use DAEO-NEW1 and DAEO-NEW2.\n\nBeside this file:\n- `W2-187-ticket.md`: the memaudit ticket.\n- `W2-188-ticket.md`: the adopt skill and practice record ticket.\n- `W2-188-CIT-P.md`: the skill's CIT-P draft.\n\n",
      "tokens": 274
    },
    {
      "id": "aa9e808019587c5a0103570b",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "text": "  fitting and DEC-1179 (4)'s rule word for word.\n- **Why it goes by CIT-P:** a kernel skill path, so the CIT-P, one independent review, the owner's approval of the\n  bytes, a version bump to 1.1.0, and the `.claude` copy by the copies ACT after W2-187 merges.\n- **W2-88a's cases stay unrevised:** the new step keeps \"declare\", \"measure\", \"the verdict set\" and \"once\", so its\n  matcher passes. This was checked on the draft text with `check_steps`, with no problems.\n- **One departure from the brief:** G4's cron line in A9's ACT package is code (`src/gov/adopt/memory_sets.py`,\n  `walls_act`), which the product-spec role cannot write. That code moves to W2-187 (S11), and W2-188 carries only its\n  text.\n\n",
      "tokens": 177
    },
    {
      "id": "239aeefa22c2862dfe4efa61",
      "path": "tests/acceptance/W2-88a/test_w2_88a_matchers.py",
      "text": "def _problems(text):\n    regions = support.a9_regions(text)\n    assert regions, \"no A9 region found\"\n    joined = \"\\n\\n\".join(regions)\n    return support.check_steps(joined) + support.check_pointer(joined)\n",
      "tokens": 52
    },
    {
      "id": "28cd0ae53c1e57d2df81b9a9",
      "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py",
      "text": "def test_s1_step_5_until_the_halves_agree_within_5_points():\n    \"\"\"Step 5: until the tuning set's halves agree within 5 points.\"\"\"\n    problems = [p for p in support.check_steps(_a9_text())\n                if p.startswith(\"step 5\") and (\"halves\" in p or \"5 points\" in p or \"is missing\" in p\n                                               or \"out of order\" in p)]\n    assert not problems, \"A9's step 5 is wrong: \" + \"; \".join(problems)\n",
      "tokens": 109
    },
    {
      "id": "54db7a7b252967561bab5d59",
      "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py",
      "text": "def test_s1_step_5_fixes_only_the_structure_never_a_named_question():\n    \"\"\"Step 5: fix only the structure, never a named question (the KPI's words or the same meaning).\"\"\"\n    problems = [p for p in support.check_steps(_a9_text())\n                if p.startswith(\"step 5\") and (\"named question\" in p or \"structure\" in p or \"is missing\" in p\n                                               or \"out of order\" in p)]\n    assert not problems, \"A9's step 5 is wrong: \" + \"; \".join(problems)\n",
      "tokens": 122
    },
    {
      "id": "840aba4a9eff928470855bb5",
      "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py",
      "text": "def test_s1_a9s_step_states_the_seven_steps_in_the_kpi_order():\n    \"\"\"Assess and plan; census the links and build the graph; build the store with the standard and its refresh;\n    the verdict set and the tuning set written; measure the tuning set; declare and measure the verdict set once;\n    record every method and figure: all seven, in that order.\"\"\"\n    problems = support.check_steps(_a9_text())\n    assert not problems, \"A9's step does not state the seven steps in order: \" + \"; \".join(problems)\n",
      "tokens": 126
    },
    {
      "id": "dc6337202417aebe943505eb",
      "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py",
      "text": "def test_s1_step_6_declares_and_measures_the_verdict_set_once():\n    \"\"\"Step 6: declare and measure the verdict set, once.\"\"\"\n    problems = [p for p in support.check_steps(_a9_text()) if p.startswith(\"step 6\")]\n    assert not problems, \"A9's step 6 is wrong: \" + \"; \".join(problems)\n",
      "tokens": 71
    },
    {
      "id": "e2eee04e9e4c32b6fbd7d478",
      "path": "tests/acceptance/W2-88a/w2_88a_support.py",
      "text": "def check_steps(region_text):\n    \"\"\"Problems of the seven steps in ``region_text`` (``[]`` when each stands, in order, with its content).\n\n    Anchors are found left to right: step k is the first match after step k-1's anchor. A step whose anchor exists\n    only earlier is out of order; one that exists nowhere is missing.\"\"\"\n    text = flat(region_text)\n    problems, anchors, cursor = [], [], 0\n    for number, label, anchor, checks, lead in STEPS:\n        found = re.compile(anchor, re.S).search(text, cursor)\n        if found:\n            anchors.append((number, found.start(), found.end()))\n            cursor = found.end()\n            continue\n        anywhere = re.compile(anchor, re.S).search(text)\n        if anywhere:\n            problems.append(f\"step {number} ({label}) is out of order: it stands before step \"\n                            f\"{anchors[-1][0] if anchors else '1'}'s\")\n        else:\n            problems.append(f\"step {number} ({label}) is missing\")\n        anchors.append((number, None, None))\n    for index, (number, label, _anchor, checks, lead) in enumerate(STEPS):\n        start = anchors[index][1]\n        if start is None:\n            continue\n",
      "tokens": 295
    },
    {
      "id": "DEC-1178",
      "path": "docs/DECISION_REGISTER.md",
      "text": "  - (2) **W2-100 and W2-101:** `yes W2-100-CIT-P 7bb4f1ac`, `yes ACT-CLAUDE-COPIES-10 f535215e`, `yes W2-101-CIT-P 42c1cc38`, `yes ACT-CLAUDE-COPIES-11 3b4e462f`. The CIT-Ps' kernel bytes are approved (DEC-1166 (4)'s form: `owner_approval` in each CIT-P, a row per kernel file in the kernel gate's list); the CTO hand-merges each and queues each copies ACT for the operator agent.\n  - (3) **P-RELEASE-1, the first numbered, frozen release:**\n    - (a) **`yes P-RELEASE-1`:** commit point (B), the integrate head after W2-100's, W2-101's and P-1's lands; version 0.1.0; the owner's steps and trailers as its \u00a74 (a plain terminal; `gov release 0.1.0`; the record committed with `Role: owner`, `Task: DAEO-sdxk`, `Implements: DEC-772, DEC-1089, DEC-1178`; the annotated, unsigned tag `v0.1.0` on the record commit); the re-pin from the release as its \u00a76. The CTO's hold: nothing lands on `w2/integrate` from \"release ready at <C>\" until the re-pin is done.\n    - (b) **P-1 (a):** A9's `parents[3]` reads (fabric.py, memory_sets.py, safety.py) are fixed before the release, in W2-88's closed scope (DEC-1164 (18)), with a narrow independent check.\n",
      "tokens": 286
    },
    {
      "id": "W2-100-CIT-P",
      "path": "docs/changes/W2-100-CIT-P.md",
      "text": "---\nid: W2-100-CIT-P\ntype: change-impact-proposal\nstatus: PROPOSED\ndate: 2026-11-14\nbranch: w2/W2-100\nbase: 627bcaa19351\nhead: f7637bd03e25\nticket: DAEO-uw5h (W2-100)\nauthor: orchestrator (the ticket lead of W2-100), for seven product-spec sessions and two test-designer sessions\nreview: 'two narrow independent checks by fresh read-only auditors (independent-auditor, Opus, high): check 1 PASS on f8e7c0fad6c6 (all twelve KPI lines; rows F1, F3-F5; F2 out of scope, package P-W2-100-F2), check 2 PASS on f7637bd03e25 (the follow-up to F1 and F3; rows N1-N4) (docs/probes/DAEO-uw5h/)'\ndecisions_carried: [DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112, DEC-1157]\nowner_approval: '\"W2-100 CIT-P approved at 7bb4f1ac\" (the owner, chat, 2026-11-14; DEC-1178 (2))'\nstate_class: EVIDENCE\n---\n\n",
      "tokens": 201
    },
    {
      "id": "W2-101-CIT-P",
      "path": "docs/changes/W2-101-CIT-P.md",
      "text": "---\nid: W2-101-CIT-P\ntype: change-impact-proposal\nstatus: PROPOSED\ndate: 2026-11-14\nbranch: w2/W2-101\nbase: 2748a2b19622\nhead: 1ef54a70037a\nticket: DAEO-6icv (W2-101)\nauthor: orchestrator (the ticket lead of W2-101), for five product-spec sessions and one test-designer session\nreview: 'two narrow independent checks by fresh read-only auditors (independent-auditor, Opus, high): round 1 FAIL on 0b0d4cb3053d (F1, the harness would show scenario-summaries.md to the session under test; fixed in W2-104 under DEC-1164 (18)), round 2 PASS on 1ef54a70037a (F1 and the lead''s L1 fixed; rows F2-F9) (docs/probes/DAEO-6icv/)'\ndecisions_carried: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-315, DEC-1112, DEC-1157, DEC-1164]\nowner_approval: '\"W2-101 CIT-P approved at 42c1cc38\" (the owner, chat, 2026-11-14; DEC-1178 (2))'\nstate_class: EVIDENCE\n---\n\n",
      "tokens": 211
    },
    {
      "id": "W2-98-CIT-P",
      "path": "docs/changes/W2-98-CIT-P.md",
      "text": "---\nid: W2-98-CIT-P\ntype: change-impact-proposal\nstatus: PROPOSED\ndate: 2026-11-13\nbranch: w2/W2-98\nbase: 6c2c3ed93bee\nhead: f0259229e2b5\nticket: DAEO-wi46 (W2-98)\nauthor: orchestrator (the ticket lead of W2-98), for three product-spec sessions\nreview: 'two rounds by fresh read-only reviewers (independent-auditor, Opus); round 1 FAIL on 384c92b8b429, fixed; round 2 FAIL on c530a0a1a236 (F1-F3); the owner''s P-W2-98-R2 (a): one fix batch, then a narrow independent check, PASS on f0259229e2b5 (docs/probes/DAEO-wi46/PR-DAEO-wi46.md)'\ndecisions_carried: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-1083, DEC-1084, DEC-315, DEC-1112, DEC-1156]\nowner_approval: '\"W2-98 CIT-P approved at 3a86f11c3981\" (the owner, chat, 2026-11-13; DEC-1163 (8))'\nstate_class: EVIDENCE\n---\n\n",
      "tokens": 193
    },
    {
      "id": "W2-98-CIT-P",
      "path": "docs/changes/W2-98-CIT-P.md",
      "text": "## 6. Independent review and approval\n\nTwo fresh read-only reviewers probed the branch. Their record, with the lead's triage, is\n`docs/probes/DAEO-wi46/PR-DAEO-wi46.md`:\n\n- Round 1 failed on F1 and F2; they were fixed through a test-design batch and a fix batch.\n- Round 2 failed on three near variants of round 1's findings: a placeholder failure line, an unbulleted KPI id line, and owner placeholders outside the list. That was the last round, so the next step was the owner's decision.\n- The owner chose P-W2-98-R2 (a) (2026-11-13): one test-design batch and one fix batch (C1-C3: a placeholder class, unbulleted KPI-id lines refused), then a narrow independent check of exactly that fix. The check (a fresh read-only Opus session) passed on `f0259229e2b5`: all 29 round 2 reproductions refused, the class held on about 230 variants, nothing from round 1 broken; four rows (N1-N4) recorded for a later wave.\n\nThe owner's approval line (CAP-33) is written here before the merge: `owner_approval:` in the front matter.\n",
      "tokens": 256
    },
    {
      "id": "W2-100-CIT-P",
      "path": "docs/changes/W2-100-CIT-P.md",
      "text": "## 7. Independent review and approval\n\nTwo fresh read-only auditors probed the branch; their records, with the lead's triage, are\n`docs/probes/DAEO-uw5h/PR-DAEO-uw5h-check1.md` and `PR-DAEO-uw5h-check2.md`:\n\n- Check 1 (`f8e7c0fad6c6`): PASS on all twelve KPI lines; no blocking finding. Rows F1 (run 5 not clean) and F3 (api\n  scenario 2 borderline), acted on in the same round (DEC-802); F4 and F5 rows; F2 out of scope, a package to the CTO.\n- Check 2 (`f7637bd03e25`): PASS; F1 and F3 settled; rows N1 to N4.\n\nThe owner's approval line (CAP-33) is written here before the merge: `owner_approval:` in the front matter.\n",
      "tokens": 156
    },
    {
      "id": "W2-101-CIT-P",
      "path": "docs/changes/W2-101-CIT-P.md",
      "text": "## 7. Independent review and approval\n\nTwo fresh read-only auditors probed the branch. Their records, with the lead's triage, are\n`docs/probes/DAEO-6icv/PR-DAEO-6icv.md` (round 1) and `PR-DAEO-6icv-r2.md` (round 2):\n\n- **Round 1 (`0b0d4cb3053d`): FAIL on F1.** The harness copied `scenario-summaries.md` into the session (fails open).\n  The CTO fixed it in the product by reopening W2-104 (DEC-1164 (18)). Rows F2 to F6. The lead added L1: W2-11's\n  output-class case refused the skills' `output:` value.\n- **Round 2 (`1ef54a70037a`): PASS, the last round (DEC-1010).** F1 and L1 are fixed. F2 to F6 keep their\n  classification. F7 to F9 are new rows; none of them blocks.\n\nThe owner's approval line (CAP-33) is written here before the merge, in `owner_approval:` in the front matter.\n",
      "tokens": 197
    },
    {
      "id": "4f809868f35e07a278a840f2",
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "text": "| 192 | DEC-1178 (1): W2-61h reopened for F3's test revision (each source at its own commit; moved-unchanged no fault; changed lines listed by question id and entry, not failed; KPI reworded); the list to the walled writer in G5's sixth item (W2-187), the operator's Monday slot until then | NOT STARTED: next: the CTO reopens DAEO-h2k3 and briefs a TD revision, narrow check, the operator's walled re-run |\n| 193 | DEC-1178 (1) Q2 (i): W2-134 closes on its fresh accept (28/0 at c451c2180) and the walled run's six passes | NOT STARTED: next: the close record and tk close, today |\n| 194 | DEC-1178 (2): W2-100/W2-101 CIT-Ps approved (7bb4f1ac, 42c1cc38); COPIES-10/-11 (f535215e, 3b4e462f) | NOT STARTED: next: owner_approval lines, kernel-approved rows, hand merges, the two .req files, closes on fresh accepts |\n| 195 | DEC-1178 (3): P-RELEASE-1, 0.1.0 at commit point (B); P-1 (a) in W2-88's reopen; setup (a); W2-81 (b) on the release; the EXAMIN CTO brief 995d0dcf with date and DEC | WAITS: P-1 (W2-88's reopen) and W2-100's/W2-101's lands; then \"release ready at <C>\", the re-pin bundle, the owner's evening sitting |\n",
      "tokens": 282
    },
    {
      "id": "W2-11-CIT-P",
      "path": "docs/changes/W2-11-CIT-P.md",
      "text": "## 4. Tests\n\n- **Acceptance:** `tests/acceptance/W2-11/` by the independent test designer (632e708b), and W1-35's revised cases,\n  with the resume's revisions (\u00a72.2). The KPI map is its README, which the author did not read (DEC-820 (c)); the\n  author runs the tests only through `gov accept`, once after its commit, and reports its per-line result in its\n  return.\n- **The skill validator** (`gov.check.skill_validator --both-layouts`): no finding on the nine kernel skills this\n  round touches, nor on the skill template read as a skill.\n- **The adapter check** (`gov.adapters.portability`): green once the generated copies are written (\u00a76). Before them,\n  it reports exactly the 16 copies this round regenerates as `GENERATED_DIFFERS`, and nothing else.\n- **The six scenarios** (qa-review's three, the skill template's three; F6): run on 2026-11-01 as dry runs, each\n  by a fresh in-session session that read only the skill or the template under test (not its `scenarios.md`),\n  was given the scenario's inputs as fictional facts and wrote nothing; the lead judged each by its pass line, and\n",
      "tokens": 274
    },
    {
      "id": "4244dbbb269fa0e17b2c8d2c",
      "path": "governance/project/orchestration/reviews/w2-128-r2b.md",
      "text": "  - Read how `gov links` judges records and kernel lines (`check.py:515-648`), the checkpoint schema, and how `gov brief` uses templates.\n  - Compared the kernel skills and role with their template rulesync copies.\n  - Ran the cases and the skills validator.\n- **files_changed:** none. `git status --porcelain` is empty. My only write was an empty `HOME` folder in the sandbox's TMPDIR.\n- **evidence:**\n  - Cases: `121 passed in 12.54s`, through `heavy_slot.sh`.\n  - Skills validator (`--both-layouts`, orchestration and test-design): `{\"findings\": []}`.\n  - `git diff --no-index template/governance/kernel/skills template/.rulesync/skills` lists only the openspec and superpowers folders. Orchestration, test-design, discovery and retrieval are byte-equal.\n  - `template/.rulesync/subagents/orchestrator.md:47-48` has the same text as `roles/orchestrator.md:39-40`.\n  - Scratch use: 4.0K, 1 folder.\n- **tests:**\n  - Ran only `tests/acceptance/W2-128`, with an empty `HOME`, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider`, `-o tmp_path_retention_policy=failed` and `PYTHONDONTWRITEBYTECODE=1`.\n",
      "tokens": 277
    },
    {
      "id": "883dfc569f09b0c23afe5fb1",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "text": "  `layout.py:77-79`).\n- **Old questions come back for retrieval only.** They are re-run in the pool for retrieval figures, never against\n  the end-to-end bar (`pool.py:3-7`).\n- **The bar is judged at 85 %.** 95 % is printed beside it, not judged (`declare.py:32-33`).\n- **There is one state folder per machine,** and it watches Gov OS's retrieval paths only (`schedule.py:18-22, 48-55`).\n- **Nothing is scheduled yet.** ACT-MEMORY-AUDIT-CRON-1 is not written.\n- **There is no weekly maintenance job.**\n- **The adopt skill measures once.** It tells every adopted repository to measure its verdict set once and never run it\n  again (`template/governance/kernel/skills/adopt/SKILL.md:58`).\n\n**Why \"used once\" exists** (the contamination concern):\n- Once every fix was judged on all 80, both halves of the first set became tuning sets.\n- The hidden half then scored 84.6 % against 67.8 % on a fresh blind set (DEC-1074 (1);\n  `docs/research/W2-88-memory-practice.md:186-191`).\n- The standing set meets this concern with four walls, all decided: walled measurement, counts only, never choosing a\n  fix, and a fresh set checking it each month.\n\n",
      "tokens": 285
    },
    {
      "id": "72a92dfbecacb739d0e1d37a",
      "path": "docs/changes/W2-138-evidence.md",
      "text": "| S3: `CONTINUATION_INVALID` names the token's commit and the store's commit now | `s` in the token; `_same_store` in `_decode_continuation` | unit `test_s3_a_token_carries_its_store_commit_and_pages_on_the_same_store`, `test_s3_a_token_replayed_on_another_store_names_both_commits`, `test_s3_the_command_refuses_it_through_the_envelope`, `test_s3_a_token_made_before_w2_138_is_refused_as_such`, `test_s3_a_token_that_is_no_object_is_refused[2 rows]`; acceptance success-3 3/3 |\n| S4: each item's sha256 is the sha256 of exactly its lines at `result.store.commit` | unchanged hashing over the store folder's lines, which the index holds at that commit (above) | unit `test_s4_every_item_s_sha256_is_its_lines_at_the_named_commit` (`git show <commit>:<path>`, a CRLF file and a file with no final newline among the items); acceptance success-4 2/2, failure-3 1/1 |\n| S5: the retrieval skill's step 5 gains the line; the skills check | the line added under step 5 | `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/retrieval ...` (the `skill-regression-b1` check): no findings; acceptance success-5 5/5 |\n\n",
      "tokens": 286
    },
    {
      "id": "108880130183469a90b4776f",
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "text": "  - `git status --porcelain` lists 11 untracked dotfiles (`.bashrc`, `.idea` \u2026). These are the sandbox's own masks, as round 1 also found; I did not write them.\n  - My only write was an empty `HOME` folder in my scratchpad.\n- **evidence:**\n  - Cases: `113 passed in 10.77s`.\n  - Skills validator (`--both-layouts`, on orchestration, test-design, discovery and retrieval): `{\"findings\": []}`.\n  - Schema check: `\"records_validated\": 974`, ok. This matches the new CIT-P row.\n  - Rulesync: `git diff --no-index` of the kernel skills against `template/.rulesync/skills` shows no difference in the four named skills.\n  - Scratch use: 8.0K and 2 inodes.\n- **tests:**\n  - Ran only `tests/acceptance/W2-128`, with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` so pytest still loads), `-p no:cacheprovider`, `-o tmp_path_retention_policy=failed` and `PYTHONDONTWRITEBYTECODE=1`.\n  - The exclusion `-m \"not local_only\" -k \"not real and not green_here and not time_limit\"` left out nothing: 113 of 113 ran.\n  - Also ran `gov.check.skill_validator` and `gov.check.schema`, both read-only.\n- **discoveries:**\n",
      "tokens": 276
    },
    {
      "id": "7da4a1c265a3fde9377e4026",
      "path": "tests/acceptance/W2-142/README.md",
      "text": "## How they run\n\n    PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-142 -q -p no:cacheprovider \\\n      -o tmp_path_retention_policy=failed\n\nUnder 1 s. No model, network or store. The skills check runs as a process (`python3 -m gov.check.skill_validator\n--both-layouts <skill folder>`) from the repository's root, on the tree `PYTHONPATH` names (else the repository's\nown `src`). The failure-line tests need `git` and the reference commit in the repository's history.\n\n- **The reference** (`w2_142_support.REFERENCE_COMMIT`): `8bb10a68366c`, this branch's base and an ancestor of\n  `w2/integrate`; integrate's head `1d49ca867188` (2026-11-09) holds the same two blobs: the retrieval skill\n  `1496eecd88db`, the discovery skill `c2cf6cadaaa7`. The tests read them with `git cat-file` after checking the\n  blob ids, so a moved integrate never changes what they compare against.\n- **Step 7** is the paragraph from the line starting `7.` to the blank line after it. S1 asks that it sit right\n  after step 6 and before `## Key constraints`, and that its text, read case-insensitively with white space\n",
      "tokens": 278
    },
    {
      "id": "2d716c26906d50d693a7e86d",
      "path": "docs/changes/W2-142-evidence.md",
      "text": "## The KPI lines and how each is met\n\n| KPI | How it is met | Verify |\n|---|---|---|\n| S1: the retrieval skill's step 7 (the practice, the \"does not answer\" list in short, the cap of two searches), W2-138's step-5 line kept, version 1.1.0, under the size budget | \u00a73.1's step 7 inserted after step 6; steps 1-6 untouched; front matter `version: \"1.1.0\"` | `PYTHONPATH=src python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/retrieval template/governance/kernel/skills/discovery`: `{\"findings\": []}`; `gov accept W2-142` |\n| S2: the discovery skill's line 55 gains one sentence (search again once before routing a question as unanswered); version 1.1.0 [DEC-1097 (8)] | \u00a73.2's sentence appended to line 55; front matter `version: \"1.1.0\"` | the same validator run; `gov accept W2-142` |\n",
      "tokens": 205
    },
    {
      "id": "51b3adfdbf8d01dab5bf4710",
      "path": "src/gov/check/skill_validator.py",
      "text": "\"\"\"Generic skill-file validator (DEC-439, CAP-24.c / CAP-38.b).\n\nValidates skill files (.md with YAML frontmatter) for required fields,\ntoken limits, and gov-command references.\n\nUsage::\n\n    python3 -m gov.check.skill_validator <skill-folders-or-files...>\n    python3 -m gov.check.skill_validator --both-layouts template/<kernel-skill-folders...>\n\nWith ``--both-layouts`` (DEC-521) a path under ``template/`` names a kernel skill in both places it can lie:\nas the template holds it, and as an installed kernel holds it (the same path without ``template/``). Each\nplace whose skills folder exists is measured, and a skill absent from such a folder is unmeasured.\n\nThe front matter is closed (DEC-995, DEC-996 item 4, DEC-1156 (2); W2-120). On every copy read, a permission key\n(``allowed-tools``, ``permissions``, ``paths``, ``sandbox``, ``network``, ``model``, ``effort``) or any key outside\nthe skill template's list is one finding naming the file and the key. The list is ``name``, ``version``,\n``description``, ``output`` and ``metadata`` (with ``metadata.version`` its one carried key) for the kernel source and\n",
      "tokens": 280
    },
    {
      "id": "58cf081a2e8776ad69dbc4de",
      "path": "template/governance/kernel/checks/skill-regression-a.yaml",
      "text": "id: \"skill-regression-a\"\nfamily: \"skill regression\"\ntier: \"G1\"\nseverity: \"hard-block\"\ncommand: \"python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/discovery template/governance/kernel/skills/planning template/governance/kernel/skills/test-design template/governance/kernel/skills/change\"\n",
      "tokens": 81
    },
    {
      "id": "1b87684d032fc417cddf00eb",
      "path": "template/governance/kernel/checks/skill-regression-b1.yaml",
      "text": "id: skill-regression-b1\nfamily: skill regression\ntier: G1\nseverity: hard-block\ncommand: python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/retrieval template/governance/kernel/skills/audit template/governance/kernel/skills/checkpoint template/governance/kernel/skills/adopt\n",
      "tokens": 78
    },
    {
      "id": "d057c8a710f2e4c4fff4ebb4",
      "path": "template/governance/kernel/checks/skill-regression-orchestration.yaml",
      "text": "id: \"skill-regression-orchestration\"\nfamily: \"skill regression\"\ntier: \"G1\"\nseverity: \"hard-block\"\ncommand: \"python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/orchestration\"\n",
      "tokens": 53
    },
    {
      "id": "a3c6b78bb10b65acb687553b",
      "path": "tests/acceptance/W2-120/README.md",
      "text": "## How \"gov check refuses\" is judged (I1, I3)\n\n`gov check` runs the `command:` of a check file from the project's root (`python3 -m gov.check.skill_validator\n--both-layouts template/governance/kernel/skills/<skill> ...`, `src/gov/check/runner.py`, `cwd` the root). The cases run\nexactly that form: the support module reads the `command:` of `skill-regression-a.yaml` from the repository, asserts it\nstill starts `python3 -m gov.check.skill_validator --both-layouts`, and swaps only the folder list for the planted\nskill's folder (run by this interpreter with `-P`, as `gov check` runs it). One case\n(`test_i3_gov_check_runs_the_check_file_and_refuses_the_planted_key`) runs `gov check --json` itself on a planted project\nholding one skill-regression check file, and reads the check's entry: red, a finding naming the generated file and the key.\n\n- **Refusal** = exit 1 and a finding of four fields (`code`, `file`, `key`, `message`, I1) whose `file` is the planted\n  file and whose `key` is the planted key, and whose `code` is not `SKILL_VENDORED_KEY` (a named-only finding is not a\n  refusal, I4). **Pass** = exit 0 and `{\"findings\": []}`.\n",
      "tokens": 286
    },
    {
      "id": "31a53b73f78da2c15b39d5c1",
      "path": "tests/acceptance/W2-120/test_w2_120_i3_copies.py",
      "text": "    copies = sup.plant_clean(tmp_path, \"alpha\")\n    planted = sup.plant_with(tmp_path, sup.CLAUDE, \"alpha\", {\"allowed-tools\": \"Bash(git:*)\"})\n    declared = yaml.safe_load((sup.CHECKS / \"skill-regression-a.yaml\").read_text(encoding=\"utf-8\"))\n    declared[\"command\"] = f\"python3 -m gov.check.skill_validator --both-layouts {sup.KERNEL}/alpha\"\n    checks = tmp_path / \"template\" / \"governance\" / \"kernel\" / \"checks\"\n    checks.mkdir(parents=True)\n    (checks / \"skill-regression-a.yaml\").write_text(yaml.safe_dump(declared, sort_keys=False), encoding=\"utf-8\")\n    env = sup.env_for()\n    done = subprocess.run([sys.executable, \"-P\", \"-m\", \"gov.cli.main\", \"check\", \"--json\"], cwd=tmp_path, env=env,\n                          capture_output=True, text=True, timeout=300, check=False)\n    assert done.returncode == 3, f\"gov check ends with 3 on a red hard-block check: {done.returncode} {done.stderr[:300]}\"\n    payload = json.loads(done.stdout)\n    entries = [entry for entry in _walk(payload) if entry.get(\"id\") == \"skill-regression-a\"]\n    assert entries, f\"gov check printed no entry for skill-regression-a: {done.stdout[:600]} {done.stderr[:300]}\"\n    entry = entries[0]\n",
      "tokens": 293
    },
    {
      "id": "9b66cffa2f315af354d49cb6",
      "path": "tests/acceptance/W2-120/w2_120_support.py",
      "text": "\n\nCHECK_HEAD = [\"python3\", \"-m\", \"gov.check.skill_validator\", \"--both-layouts\"]\n\n\n",
      "tokens": 21
    },
    {
      "id": "b03a647afcbeec4098925ba0",
      "path": "tests/acceptance/W2-120/w2_120_support.py",
      "text": "def argv_for(folders: list[str]) -> list[str]:\n    \"\"\"The command of ``skill-regression-a`` with its folder list swapped for ``folders``: the check file's words\n    (``python3 -m gov.check.skill_validator --both-layouts <kernel skill folders>``) run by this interpreter, with\n    ``-P`` as ``gov check`` runs it, and the switch's module in place of the real one when it is set.\"\"\"\n    head = check_command(\"skill-regression-a\")[:4]\n    assert head == CHECK_HEAD, f\"skill-regression-a no longer runs the validator in its --both-layouts form: {head}\"\n    return [sys.executable, \"-P\", \"-m\", MODULE, \"--both-layouts\", *folders]\n",
      "tokens": 157
    },
    {
      "id": "7920083d426a40726cb56670",
      "path": "tests/acceptance/W2-128/README.md",
      "text": "  `DAEO-t8mp` and any other `{KEY\u2026}` with a plain word, and no other substitution. No `UNKNOWN_ID` may name it.\n  `gov links` reads `task:`, not `inputs`, so the string case covers the `inputs` id.\n- **The skills validator** runs as `python3 -m gov.check.skill_validator --both-layouts\n  template/governance/kernel/skills/{orchestration,test-design}` from the tree root and must exit 0. It refuses an\n  unknown `gov` subcommand in code. `gov brief` is not one of its commands on integrate (W2-152 is not merged), so a\n  skill naming `` `gov brief` `` in code fails it today.\n- **A check of the cases** (a scratch worktree, removed): a stand-in 2a passed all 113 (92 + 21). Each of 19 wrong\n  changes then failed the case meant for it, among them:\n  - `src/` barred outright; the ticket bar dropped;\n  - \"word for word\" kept; no template named; \"each step in full\" kept;\n  - the glob or the settings bar kept; the held-out bar dropped;\n  - `brief-engineer.md` named in the role file; JUDGEMENT copied into T-7; `task: DAEO-9999` in the checkpoint;\n  - a stale rulesync copy; version `1.0.1`; an unknown `gov` command;\n",
      "tokens": 280
    },
    {
      "id": "ba22f49adb32e12b9cd6ec36",
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "text": "def test_s11_skills_validator_passes_on_both_skills(tmp_path):\n    done = subprocess.run([sys.executable, \"-m\", \"gov.check.skill_validator\", \"--both-layouts\",\n                           str(SKILLS.relative_to(s.REPO) / \"orchestration\"),\n                           str(SKILLS.relative_to(s.REPO) / \"test-design\")],\n                          cwd=s.REPO, capture_output=True, text=True, env=s.sealed_env(tmp_path), timeout=60)\n    assert done.returncode == 0, f\"the skills validator fails: {done.stdout.strip()[-400:]} {done.stderr.strip()[-200:]}\"\n",
      "tokens": 137
    },
    {
      "id": "341361677f6d358569dabaf1",
      "path": "tests/acceptance/W2-142/test_w2_142_skills_check.py",
      "text": "def test_guard_the_skills_check_finds_nothing(skill):\n    env = dict(os.environ)\n    env[\"PYTHONPATH\"] = env.get(\"PYTHONPATH\") or str(support.REPO / \"src\")\n    folder = f\"template/governance/kernel/skills/{skill}\"\n    done = subprocess.run(\n        [sys.executable, \"-m\", \"gov.check.skill_validator\", \"--both-layouts\", folder],\n        cwd=support.REPO, env=env, capture_output=True, text=True, timeout=60, check=False)\n    assert done.returncode == 0, f\"the skills check on {folder}: exit {done.returncode}: {done.stdout}{done.stderr}\"\n    assert json.loads(done.stdout.strip().splitlines()[-1]) == {\"findings\": []}, done.stdout\n",
      "tokens": 158
    }
  ],
  "supplementary_query": "The adopt skill's step 6 and the practice record say the verdict set becomes the standing set, judged every week at 95 %, counts only, checked monthly against a fresh set; A9's weekly cron line named (MEMORY-AUDIT G6 and G4's text; CIT-P)\nS1 A9's step 6 in the adopt skill says, in its own words: the verdict set is declared and measured once at Wave 0 as the first verdict; from then on it is the repository's standing set, judged end to end every week on the same questions (monthly once the repository is stable, under the package's O3 (b)) as Gov OS's memory is judged (the standard's bundle read whole by the reader, search again once), against 95 %, behind the walls, with only counts leaving its run; it never chooses or judges a fix (fixes chosen on the tuning set and the fresh sets' misses); a fresh set each month checks it for fitting and a fitted set is replaced; a miss is never re-run in the same week and never re-scored; it cites DEC-1179 [DEC-1179 (1)-(4), DEC-1176 (1), DEC-1098 (1)] Verify: a string test on step 6's stretch of the three copies finds each of these statements (standing set, every week, same questions, 95 %, counts only, never chooses a fix, fresh set monthly, fitted replaced, DEC-1179); W2-88a's step matcher (`check_steps`) returns no problem on A9's section\nS2 After A9's seven steps, one paragraph says the weekly audit runs from one cron line that A9's ACT package gives the repository's owner's operator beside the walls, never installed by adoption, and that a fall below 95 % is handled as the practice record's section 9 states [DEC-1179 (4), (5), DEC-1101 (2)] Verify: a string test finds the paragraph between step 7 and the `## Verify clauses for adopted tickets` heading in all three copies, with \"cron\", \"ACT\", \"operator\", \"never installs\" (or \"never installed\") and \"95 %\"\nS3 The practice record states the standing set: \u00a73's confirmation line, \u00a75 item 6's practice lines and \u00a76 step 6 re-worded as the CIT-P quotes, and a new \u00a79 \"The standing set (DEC-1179)\" with what it is, the method (the reader ranking the whole bundle and searching again once, A2, with the E2 and E3 figures), the bar, the walls (counts only, no id read by anyone), fixes never chosen on it, staleness by count, the monthly check against fitting with its two 5-point rules, and DEC-1179 (4)'s rule below 95 % word for word [DEC-1179, DEC-1074 (1), DEC-1074 (4), DEC-1072 (2)] Verify: a string test on each named place of `docs/research/W2-88-memory-practice.md`; \u00a76 still passes W2-88a's step matcher; \u00a79's below-95 text equals DEC-1179 (4)'s as recorded\nS4 The three copies of the skill are byte-equal; the version goes from \"1.0.0\" to \"1.1.0\" in all three (the next minor if W2-88a's promotion has taken 1.1.0 by then); nothing else in the skill changes but step 6, the new paragraph, the governing sources line (adding DEC-1101, DEC-1125 and DEC-1179) and the version [CAP-33, DEC-832 item 2, DEC-981] Verify: sha256 of the three copies equal; `git diff` of the kernel copy against the base touches only those four places; `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0\nS5 The CIT-P record `docs/changes/W2-188-CIT-P.md` gives the skill's sha256 before and after, the lines added and removed, the old and new text of each changed place, the impact table (W2-11's body case red until the copies ACT; W2-88a's cases unchanged), the independent review's verdict and the owner's approval line of the bytes before the merge [CAP-33, DEC-105] Verify: the record holds both hashes (the after equal to the kernel copy at the ticket's last commit), the counts, a `verdict: PASS` as the last verdict and an `owner_approval:` line naming the sha256\nF1 Any other step, section or rule of the adopt skill changes, or the skill grants a permission, names a `gov.memaudit` subcommand or states a mode the product lacks. Verify: the S4 diff; a grep of the three copies for `gov.memaudit` and `standing declare` finds nothing\nF2 The ticket writes `.claude/skills/adopt/SKILL.md` or any test under `tests/acceptance/`. Verify: the close's diff names neither; the copies ACT regenerates the `.claude` copy after the owner's approval\nF3 The text says the standing set may be used to choose, judge, adopt or reject a fix, prints or reads a question id, or calls the reader a second reranking model. Verify: a string test on step 6 and \u00a79 for \"never chooses or judges a fix\" and \"counts only\"; \u00a79 says W2-88 S10's second reranker stays forbidden",
  "further_batch": [
    {
      "id": "4934c63ab137446ea6b41677",
      "path": "tests/acceptance/W2-142/test_w2_142_skills_check.py"
    },
    {
      "id": "ceb7505fccf8e2ee1d5a9d7d",
      "path": "tests/acceptance/W2-88a/README.md"
    },
    {
      "id": "be0e487772d0a34d5d56e6be",
      "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py"
    },
    {
      "id": "8dba4fabfb485b570da405ae",
      "path": "tests/acceptance/W2-88a/w2_88a_support.py"
    },
    {
      "id": "W2-27-CIT-P",
      "path": "docs/changes/W2-27-CIT-P.md"
    },
    {
      "id": "W2-49-CIT-P",
      "path": "docs/changes/W2-49-CIT-P.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "66b15001fc9e12b19a4b57be",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md"
        },
        {
          "id": "aa9e808019587c5a0103570b",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md"
        },
        {
          "id": "239aeefa22c2862dfe4efa61",
          "path": "tests/acceptance/W2-88a/test_w2_88a_matchers.py"
        },
        {
          "id": "28cd0ae53c1e57d2df81b9a9",
          "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py"
        },
        {
          "id": "54db7a7b252967561bab5d59",
          "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py"
        },
        {
          "id": "840aba4a9eff928470855bb5",
          "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py"
        },
        {
          "id": "dc6337202417aebe943505eb",
          "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py"
        },
        {
          "id": "e2eee04e9e4c32b6fbd7d478",
          "path": "tests/acceptance/W2-88a/w2_88a_support.py"
        },
        {
          "id": "DEC-1178",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "W2-100-CIT-P",
          "path": "docs/changes/W2-100-CIT-P.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "W2-101-CIT-P",
          "path": "docs/changes/W2-101-CIT-P.md"
        },
        {
          "id": "W2-98-CIT-P",
          "path": "docs/changes/W2-98-CIT-P.md"
        },
        {
          "id": "W2-98-CIT-P",
          "path": "docs/changes/W2-98-CIT-P.md"
        },
        {
          "id": "W2-100-CIT-P",
          "path": "docs/changes/W2-100-CIT-P.md"
        },
        {
          "id": "W2-101-CIT-P",
          "path": "docs/changes/W2-101-CIT-P.md"
        },
        {
          "id": "4f809868f35e07a278a840f2",
          "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
        },
        {
          "id": "W2-11-CIT-P",
          "path": "docs/changes/W2-11-CIT-P.md"
        },
        {
          "id": "4244dbbb269fa0e17b2c8d2c",
          "path": "governance/project/orchestration/reviews/w2-128-r2b.md"
        },
        {
          "id": "883dfc569f09b0c23afe5fb1",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md"
        },
        {
          "id": "72a92dfbecacb739d0e1d37a",
          "path": "docs/changes/W2-138-evidence.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "108880130183469a90b4776f",
          "path": "governance/project/orchestration/reviews/w2-128-r2a.md"
        },
        {
          "id": "7da4a1c265a3fde9377e4026",
          "path": "tests/acceptance/W2-142/README.md"
        },
        {
          "id": "2d716c26906d50d693a7e86d",
          "path": "docs/changes/W2-142-evidence.md"
        },
        {
          "id": "51b3adfdbf8d01dab5bf4710",
          "path": "src/gov/check/skill_validator.py"
        },
        {
          "id": "58cf081a2e8776ad69dbc4de",
          "path": "template/governance/kernel/checks/skill-regression-a.yaml"
        },
        {
          "id": "1b87684d032fc417cddf00eb",
          "path": "template/governance/kernel/checks/skill-regression-b1.yaml"
        },
        {
          "id": "d057c8a710f2e4c4fff4ebb4",
          "path": "template/governance/kernel/checks/skill-regression-orchestration.yaml"
        },
        {
          "id": "a3c6b78bb10b65acb687553b",
          "path": "tests/acceptance/W2-120/README.md"
        },
        {
          "id": "31a53b73f78da2c15b39d5c1",
          "path": "tests/acceptance/W2-120/test_w2_120_i3_copies.py"
        },
        {
          "id": "9b66cffa2f315af354d49cb6",
          "path": "tests/acceptance/W2-120/w2_120_support.py"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "b03a647afcbeec4098925ba0",
          "path": "tests/acceptance/W2-120/w2_120_support.py"
        },
        {
          "id": "7920083d426a40726cb56670",
          "path": "tests/acceptance/W2-128/README.md"
        },
        {
          "id": "ba22f49adb32e12b9cd6ec36",
          "path": "tests/acceptance/W2-128/test_w2_128_round2a.py"
        },
        {
          "id": "341361677f6d358569dabaf1",
          "path": "tests/acceptance/W2-142/test_w2_142_skills_check.py"
        },
        {
          "id": "4934c63ab137446ea6b41677",
          "path": "tests/acceptance/W2-142/test_w2_142_skills_check.py"
        },
        {
          "id": "ceb7505fccf8e2ee1d5a9d7d",
          "path": "tests/acceptance/W2-88a/README.md"
        },
        {
          "id": "be0e487772d0a34d5d56e6be",
          "path": "tests/acceptance/W2-88a/test_w2_88a_skill_order.py"
        },
        {
          "id": "8dba4fabfb485b570da405ae",
          "path": "tests/acceptance/W2-88a/w2_88a_support.py"
        },
        {
          "id": "W2-27-CIT-P",
          "path": "docs/changes/W2-27-CIT-P.md"
        },
        {
          "id": "W2-49-CIT-P",
          "path": "docs/changes/W2-49-CIT-P.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "4934c63ab137446ea6b41677",
      "reason": "budget exceeded"
    },
    {
      "id": "8dba4fabfb485b570da405ae",
      "reason": "budget exceeded"
    },
    {
      "id": "W2-27-CIT-P",
      "reason": "budget exceeded"
    },
    {
      "id": "W2-49-CIT-P",
      "reason": "budget exceeded"
    },
    {
      "id": "be0e487772d0a34d5d56e6be",
      "reason": "budget exceeded"
    },
    {
      "id": "ceb7505fccf8e2ee1d5a9d7d",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 39897,
  "budget": {
    "limit": 40000,
    "used": 39897
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-045",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "07608979763f6064908e15fc9d561c03ed7167e6875277b017bee099d7bb6d86"
}
