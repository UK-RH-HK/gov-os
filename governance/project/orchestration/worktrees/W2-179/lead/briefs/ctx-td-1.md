{
  "ticket": "DAEO-c9n8",
  "ticket_text": "---\nid: DAEO-c9n8\nstatus: in_progress\ndeps: []\nlinks: [DAEO-61vm]\ncreated: 2026-11-12T05:40:00Z\ntype: task\npriority: 2\nassignee: independent-test-designer\nexternal-ref: W2-179\ntags: [wave-2, test-revision, memory, audit, nightly, lite]\nwbs_id: W2-179\ntitle: 'W2-170''s F3 file-access case counts the repository''s own files as runs-folder opens when the repository lives under ~/gov-os-runs (the nightly''s clone); red in the nightly of 11-12'\nclass: test-revision\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\nprofile: LITE\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- tests/acceptance/W2-170/test_w2_170_s4_map.py\n- tests/acceptance/W2-170/README.md\nest_loc: 15\nkpis:\n  success:\n  - 'S1 `test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders` judges only opens of the true sets root and of the runs folders outside the repository under test: an open of a file of the repository itself (its own source, tests and stores) is not a runs-folder open, wherever the repository lives. Verify: the case passes in a clone under ~/gov-os-runs/<x>/ (as the nightly runs it) and in a clone elsewhere; a planted open of a file under the true runs folder outside the repository still fails it [DEC-820 (b), (d), DEC-866]'\n  failure:\n  - 'A real runs-folder or sets-root open let through. Verify: the planted open of a runs-folder file outside the repository fails the revised case, in both clone places'\n  - 'Any change outside the paths above, or a case removed, skipped or loosened beyond the repository''s own files. Verify: `git diff` of the case shows only the exclusion of the repository''s own root; `git diff --name-only` lists only the allowed paths'\nnon_goals:\n- the memory audit's code (W2-170, closed)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-820, DEC-866, DEC-966, DEC-1101]\nacceptance_tests:\n  path: tests/acceptance/W2-170/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C1): the revision with a Rewrite-Reason (DEC-866)'\ntrack: B\nreads:\n- src/gov/memaudit/preflight.py\n- tests/acceptance/W2-170/conftest.py\nneeds:\n- tests/acceptance/W2-170/test_w2_170_s4_map.py\n---\n# W2-179 W2-170's F3 case and the nightly's clone\n\nThe nightly of 11-12 (run 20261112-0404, head 9bbef27f1d05) is red on\n`tests/acceptance/W2-170/test_w2_170_s4_map.py::test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders`\n(red alone too): its `reached` list holds 100-odd paths, every one a file of the repository under test, because the nightly's\nclone lives at `~/gov-os-runs/W2-00/nightly/<run>/`, inside the runs folder the case watches. The code is not at fault (W2-170\nclosed with the case green in its worktree). A test revision: exclude the repository's own root from \"the runs folders\".\nClass C1. The hidden-half rule holds: the revised case plants its own sets root and runs folder.\n",
  "authority": [
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
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
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
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    }
  ],
  "mandatory": [
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
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
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
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    }
  ],
  "supplementary": [
    {
      "id": "77b4474a8223c91ef2b0f202",
      "path": "tests/acceptance/W2-153/w2_153_support.py",
      "text": "# The kernel role file -> its template, for the six kernel roles (the orchestrator's is the lead's).\nKERNEL_ROLE_TEMPLATE = {role: ROLE_TEMPLATE[role] for role in SKILLS}\n\n# S4: the eight copies under .claude/templates/ (ticket.md and the rest of the kernel's templates are not copied).\nTEMPLATE_STEMS = (\"brief\", \"role-research\", \"role-product-spec\", \"role-test-designer\", \"role-engineer\",\n                  \"role-reviewer\", \"role-lead\", \"role-cto\")\n\nKERNEL = REPO / \"template\" / \"governance\" / \"kernel\"\nKERNEL_TEMPLATES = KERNEL / \"templates\"\nTEST_DESIGN_SKILL = KERNEL / \"skills\" / \"test-design\" / \"SKILL.md\"\nDISPATCH_REL = \"governance/project/orchestration/tools/dispatch/launch_now.sh\"\n\n# F2's baseline (DEC-1112 (3)): the integrate commit W2-153 is built on, `git merge-base w2/W2-153 w2/integrate`\n# (2026-11-10). Its launcher is integrate's as of the W2-56 merge (cf23e9f8dc1f: S5's cleaned env, the runs-folder and\n# reranker sandbox entries). Moved from 1ef1a7a48c53 (launcher 5ecd20c0d252), which predates W2-56.\nBASELINE_COMMIT = \"f73e72d4a43b14ba598bac4829ced555842907ea\"\nBASELINE_BLOBS = {\n    \"src/gov/launch/launcher.py\": \"91033723374d9dff0d97e4a36934cc09fa00d16b\",\n",
      "tokens": 296
    },
    {
      "id": "DAEO-61vm",
      "path": ".tickets/DAEO-61vm.md",
      "text": "  - 'A set measured twice, or measured without `DECLARATION.json` and `USED` written first. Verify: S3''s planted runs: the file times and the ledger line show `DECLARATION.json` before `USED` before any search, and a second run on the same audit exits with the refusal and starts no search'\n  - 'The repository''s path map, the guard, the hook, `.claude/` or the walls'' template written; the real sets root or run folders opened by a test. Verify: S4''s `git status` in the planted repository shows no change, and a run of the tests with the planted roots under TMPDIR leaves no open of the real sets root or run folders in the tests'' file-access log'\n  - 'A dropped question deleted; a VOID audit that wrote `USED`. Verify: S2''s planted notes with 3 drops (the 3 files are found under `dropped/`) and with 5 drops (VOID: no `USED` and no `DECLARATION.json` in the audit''s run folder)'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: FULL\nsources:\n- DEC-1101\n- DEC-1125\n- DEC-1098\n- DEC-1097\n- DEC-1069\n- DEC-820\n- DEC-896\n- DEC-1050\n- DEC-1073\n- DEC-1052\n",
      "tokens": 298
    },
    {
      "id": "64c5c6c3e4b4514824737b3a",
      "path": "tests/acceptance/W2-170/test_w2_170_s4_map.py",
      "text": "\"\"\"S4 and F3: the set is declared in the sets root's own path map (Interface 7), as one ``evaluation_sets.<A>`` entry\nof ``memory-verdict-2``'s shape with its five roles, every other byte kept, so that ``gov.retrieval.measure`` accepts\nit; the planted repository is never written (``git status`` empty after every subcommand); a run's file-access log\nshows no open of the true home's ``gov-os-eval`` or ``gov-os-runs``.\n\nThe file-access log: ``w2_170_open_log.py`` installs ``sys.addaudithook`` for ``open``, ``os.*`` and\n``subprocess.Popen`` events, writes them to a file, then runs ``gov.memaudit`` with ``runpy``.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport shutil\nimport subprocess\nimport sys\nimport textwrap\n\nimport pytest\nimport yaml\n\nimport w2_170_world as W\n\nENTRY = {\"visible\": [], \"hidden\": [f\"fixtures/evaluation/{W.AUDIT}/hidden/**\"], \"measures\": {\"roles\": list(W.ROLES)}}\nFLOW_ENTRY = (f\"  {W.AUDIT}: {{visible: [], hidden: [\\\"fixtures/evaluation/{W.AUDIT}/hidden/**\\\"], \"\n              f\"measures: {{roles: [engineer, research, product-spec, independent-test-designer, \"\n              f\"independent-auditor]}}}}\\n\")\n\n\n",
      "tokens": 284
    },
    {
      "id": "bf342a61ee9c0ada7b0e5309",
      "path": "tests/acceptance/W2-170/README.md",
      "text": "  `indep/AUDITS.log` and `indep/SEEDS.log` (and, per case, a planted `selection.json`); a pool\n  `fixtures/evaluation/memory-pool/hidden/`; a store file with a `fingerprints` row whose `head` is the audit commit;\n  a `gov` link into a folder `pin-0123456789ab`; a clean 40-question set (and 36\u201339 variants) and `XCHECK-r<n>.md`\n  notes. One template world per variant is built per session and copied whole into each test's `tmp_path`.\n- **`HOME`** of every child process is a planted folder under `tmp_path`; `PYTHONUSERBASE` is kept as the test\n  process has it, so the planted home changes no imported package. The true home's `~/gov-os-eval` and\n  `~/gov-os-runs` are never opened (F3): `w2_170_world.TRUE_HOME` is used only to check the file-access log.\n- **The file-access log (F3, S1's \"no real ~/gov-os-eval is opened\"):** `w2_170_open_log.py` installs\n  `sys.addaudithook` for `open`, `os.*` and `subprocess.Popen` events, writes them to a file, then runs `gov.memaudit`\n  with `runpy` as `__main__`. The case runs `preflight` (its default runs folder `~/gov-os-runs`, planted in the planted\n",
      "tokens": 275
    },
    {
      "id": "018424a72df7369d4d82b5fc",
      "path": "tests/acceptance/W2-170/test_w2_170_s4_map.py",
      "text": "def test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders(world, tmp_path):\n    # the default runs folder is ~/gov-os-runs: a planted home holds one, so the run needs it and finds it there\n    home = tmp_path / \"home-with-runs\"\n    shutil.copytree(world.launch, home / \"gov-os-runs\")\n    world.write_set(W.clean_specs(), selection=False)\n    done, entries = _logged_run(world, home, tmp_path / \"preflight.log\", \"preflight\", world.pf_flags(runs_dir=False))\n    assert done.returncode == 0, (done.stdout, done.stderr)\n    world.write_notes(2, {\"q27\": (\"reject\", \"R1-WRONG\")})\n    done2, entries2 = _logged_run(world, home, tmp_path / \"void.log\", \"void\", world.void_flags())\n    assert done2.returncode == 0, (done2.stdout, done2.stderr)\n    done3, entries3 = _logged_run(world, home, tmp_path / \"declare.log\", \"declare\", world.dc_flags())\n    assert done3.returncode == 0, (done3.stdout, done3.stderr)\n    every = entries + entries2 + entries3\n    reached = [p for _, p in every if W.at_or_under(p, W.TRUE_SETS) or W.at_or_under(p, W.TRUE_RUNS)]\n    assert reached == [], reached\n",
      "tokens": 277
    },
    {
      "id": "DAEO-p8tv",
      "path": ".tickets/DAEO-p8tv.md",
      "text": "  - 'S9 The cron wrapper `memaudit_cron.sh` runs `due` and starts the cycle only when an audit is due, with the pinned interpreter; it does nothing and exits 0 when none is due, appends one line per run to the audits'' cron log, and does not start the measure steps while the dispatcher holds a full run or a rebuild (the gate''s own check), waiting at most 60 minutes and then stopping with `gate busy`. It contains no crontab edit (the crontab is class (O), an ACT). Verify: planted `due` outputs and gate states: not due (no start, exit 0), due and idle (starts), due and busy for 61 minutes (stops `gate busy`); `grep -c crontab` of the wrapper is 0 [DEC-1125 (2), DEC-1038]'\n  failure:\n  - 'A wall, a set, the approved list or a run folder opened by the driver other than through the launch script, W2-170''s or W2-171''s code; a command line naming a folder under the sets root. Verify: S1''s planted run: the call ledger''s printed command lines hold no `fixtures/`, `runs/` or `indep-walls/`, and a file-access spy over the driver''s own process shows no open of those folders'\n",
      "tokens": 272
    }
  ],
  "supplementary_query": "W2-170's F3 file-access case counts the repository's own files as runs-folder opens when the repository lives under ~/gov-os-runs (the nightly's clone); red in the nightly of 11-12\nS1 `test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders` judges only opens of the true sets root and of the runs folders outside the repository under test: an open of a file of the repository itself (its own source, tests and stores) is not a runs-folder open, wherever the repository lives. Verify: the case passes in a clone under ~/gov-os-runs/<x>/ (as the nightly runs it) and in a clone elsewhere; a planted open of a file under the true runs folder outside the repository still fails it [DEC-820 (b), (d), DEC-866]\nA real runs-folder or sets-root open let through. Verify: the planted open of a runs-folder file outside the repository fails the revised case, in both clone places\nAny change outside the paths above, or a case removed, skipped or loosened beyond the repository's own files. Verify: `git diff` of the case shows only the exclusion of the repository's own root; `git diff --name-only` lists only the allowed paths",
  "further_batch": [
    {
      "id": "0825333e6a23fa1afb72a9e9",
      "path": "tests/acceptance/W2-170/README.md"
    },
    {
      "id": "1dbf392fb200e1fc25b797a4",
      "path": "tests/acceptance/W2-170/README.md"
    },
    {
      "id": "369f1b4289084e4bd0f76400",
      "path": "tests/acceptance/W1-15/test_w1_15_parallel_scan.py"
    },
    {
      "id": "DAEO-1k7y",
      "path": ".tickets/DAEO-1k7y.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "77b4474a8223c91ef2b0f202",
          "path": "tests/acceptance/W2-153/w2_153_support.py"
        },
        {
          "id": "DAEO-61vm",
          "path": ".tickets/DAEO-61vm.md"
        },
        {
          "id": "64c5c6c3e4b4514824737b3a",
          "path": "tests/acceptance/W2-170/test_w2_170_s4_map.py"
        },
        {
          "id": "bf342a61ee9c0ada7b0e5309",
          "path": "tests/acceptance/W2-170/README.md"
        },
        {
          "id": "018424a72df7369d4d82b5fc",
          "path": "tests/acceptance/W2-170/test_w2_170_s4_map.py"
        },
        {
          "id": "DAEO-p8tv",
          "path": ".tickets/DAEO-p8tv.md"
        },
        {
          "id": "0825333e6a23fa1afb72a9e9",
          "path": "tests/acceptance/W2-170/README.md"
        },
        {
          "id": "1dbf392fb200e1fc25b797a4",
          "path": "tests/acceptance/W2-170/README.md"
        },
        {
          "id": "369f1b4289084e4bd0f76400",
          "path": "tests/acceptance/W1-15/test_w1_15_parallel_scan.py"
        },
        {
          "id": "DAEO-1k7y",
          "path": ".tickets/DAEO-1k7y.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0825333e6a23fa1afb72a9e9",
      "reason": "budget exceeded"
    },
    {
      "id": "1dbf392fb200e1fc25b797a4",
      "reason": "budget exceeded"
    },
    {
      "id": "369f1b4289084e4bd0f76400",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-1k7y",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 5112,
  "budget": {
    "limit": 6000,
    "used": 5112
  },
  "left_out": {
    "count": 7,
    "superseded": [
      "DEC-038",
      "DEC-045",
      "DEC-047",
      "DEC-048",
      "DEC-049",
      "DEC-636",
      "DEC-875"
    ],
    "done": []
  },
  "hash": "8aec8e327d4f71b0657be8c8c78962320e06d8f3d41c4a0c66987528682fe863"
}
