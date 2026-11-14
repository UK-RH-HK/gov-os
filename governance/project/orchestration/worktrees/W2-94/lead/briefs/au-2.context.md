{
  "ticket": "DAEO-g87r",
  "ticket_text": "---\nid: DAEO-g87r\nstatus: in_progress\ndeps: [DAEO-m1u3]\nlinks: []\ncreated: 2026-10-30T22:14:09Z\ntype: task\npriority: 1\nassignee: independent-auditor\nexternal-ref: W2-94\ntags: [wave-2, audit, evaluation, held-out, standard, examin-minimum]\nwbs_id: W2-94\ntitle: 'EXAMIN''s question set: memory questions with gold sources about the owner''s copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: [DAEO-m1u3]\nallowed_paths:\n- tests/acceptance/W2-94/**  # its acceptance tests, form only (CTO, DEC-1167 (3): the close)\n- fixtures/evaluation/examin/check_gold.py  # S4's counts-only script, by the independent test designer, run by the CTO with --sets-root\n- docs/probes/DAEO-g87r/**  # the probe record\n- fixtures/evaluation/examin/visible/**\n- fixtures/evaluation/examin/hidden/**\nkpis:\n  success:\n  - 'Between 10 and 20 questions about EXAMIN''s code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner''s release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]'\n  - 'Written by the walled writer from the wall''s tree, `git archive` of the CTO''s launch clone of the owner''s copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls'' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN''s real repository Verify: the record names the clone''s path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy''s commit; after the run `git status` in the workbench and in EXAMIN''s real repository shows no change, and the owner''s copy''s file times are unchanged [DEC-723, DEC-728]'\n  - 'Written by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls'' launch log names the approved brief''s sha256; the guard''s log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845]'\n  - 'Every gold source exists at the copy''s recorded commit and holds the answer Verify: a counts-only script, written by the ticket''s independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy''s recorded commit and holds the answer (\"n of n hold\"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4]'\n  - 'W2-61''s KPI 6 (\"the same split for EXAMIN''s set\") is met by this ticket; W2-61''s close record names it as moved here Verify: a grep of W2-61''s close record finds KPI 6 named as moved to W2-94; this ticket''s visible and hidden folders hold the split of S1 [DEC-954, DEC-957]'\n  failure:\n  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session''s sandbox (the guard''s path map) are refused or find it 0 times'\n  - 'A write in the workbench, the owner''s copy or EXAMIN''s real repository; a clone outside ~/gov-os-runs/W2-94/. Verify: `git status` in the workbench, the owner''s copy and EXAMIN''s real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none'\n  - 'A gold source that does not hold its answer. Verify: the S4 script on a planted source that does not hold its answer reports that question''s id as failing'\nprofile: STANDARD\nsources:\n- DEC-957\n- DEC-954\n- DEC-828\n- DEC-820\n- DEC-845\n- DEC-723\n- DEC-728\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-94/\n  author: independent-test-designer (MR-3); form only (count, fields, sources named), never printing a question or an answer\ntrack: B\nlist_rows: []\n---\n# W2-94 EXAMIN's question set\n\nCard: MEMORY-SPEC-MAP gap 7, resolved by the owner in DEC-957; W2-61's KPI 6 moves here. The set measures memory on EXAMIN's copy at W2-27 (with W2-88's tools) and W2-15b.\n\n- **Before it starts, the orchestrator adds an `evaluation_sets` entry** `examin` to the path map (`visible: fixtures/evaluation/examin/visible/**`, `hidden: fixtures/evaluation/examin/hidden/**`, `measures` by tickets: W2-26, W2-27, W2-88, W2-15b and the retrieval tickets), so the guard refuses the hidden half from every worktree (W2-84).\n- **The clone:** made by the orchestrator or the auditor by exact path, `git clone --no-hardlinks` from the owner's copy (DEC-723, DEC-728); removed at the end.\n- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.\n- **Verify re-worded (CTO, 2026-11-13, DEC-1157 (12), DEC-1167 (3)):** S3's brief path is where it is installed; S4's script is the test designer's, run by the CTO (the walled writer has no shell); the KPI text before each Verify unchanged except the brief's path.\n\n**Role changed 2026-11-13 (P-W2-94-GOLD-2 (A), the CTO):** class audit -> implementation and role independent-auditor -> engineer, so the launcher lets the engineer the owner's W2-94 GOLD (a) names change `check_gold.py`; the walled writers' delivery is done, and the narrow check stays independent.\n",
  "authority": [
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
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
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
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
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-723",
      "sha256": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "reason": "declared in sources",
      "tokens": 315
    },
    {
      "id": "DEC-728",
      "sha256": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "reason": "declared in sources",
      "tokens": 475
    },
    {
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "mandatory": [
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
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
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
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
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-723",
      "sha256": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "reason": "declared in sources",
      "tokens": 315
    },
    {
      "id": "DEC-728",
      "sha256": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "reason": "declared in sources",
      "tokens": 475
    },
    {
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "supplementary": [
    {
      "id": "593a9864fb07d41cc1e72a95",
      "path": "tests/acceptance/W2-94/test_w2_94_s1_split_form.py",
      "text": "\"\"\"W2-94, KPI success 1 (S1) -- the set's count, its fields, the recorded draw, the two halves and the release.\n\nS1: \"Between 10 and 20 questions ... after writing, a recorded seeded draw, stratified by category, splits the set into a\ndevelopment half (`hidden/visible/`) and a hidden half ... the owner's release step (`release_visible.sh`) then copies\nthe development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record\nholds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release\nstep copies exactly the development half into `visible/` and refuses a second release\".\n\nDriven through ``fixtures/evaluation/examin/check_gold.py`` on planted stand-ins (``w2_94_support``). The release\nstep's refusal of a second release is the owner's operator's record, not tested here (README).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport sys\nfrom pathlib import Path\n\nimport pytest\n\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n\nimport w2_94_cases as c  # noqa: E402\nimport w2_94_support as s  # noqa: E402\n\n\n",
      "tokens": 280
    },
    {
      "id": "d6ac0e20c58f37d56fe1191f",
      "path": "tests/acceptance/W2-94/README.md",
      "text": "# W2-94 (DAEO-g87r): EXAMIN's question set -- acceptance cases (form only)\n\nWritten by the independent test designer from the ticket's KPI lines and the approved writer brief\n(`governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`, sections 5 to 7), before and beside the check it tests.\n**Form only:** every case runs on a stand-in planted under pytest's `tmp_path` (made-up text about made-up files, each\ncarrying the word `zqxw94`). Nothing under `~/gov-os-eval`, `~/gov-os-runs`, a real `hidden` folder or any\n`fixtures/evaluation/examin/` folder of a tree was opened; no real question or answer is written anywhere.\n\nThe real set is checked by the CTO: `python3 fixtures/evaluation/examin/check_gold.py --sets-root <root> --copy <launch\nclone>` (written to this folder's cases; its docstring states the \"holds the answer\" rule and what it cannot catch).\n\nRun the folder with an empty HOME, through the heavy slot, `PYTHONPATH=<tree>/src`, and\n`-m \"not local_only\" -k \"not real and not green_here and not time_limit\"`. The exclusion leaves out nothing here: no case\nstarts a real model, embedder or network. `W2_94_CHECK_GOLD=<file>` runs another file in place of `check_gold.py` (the\n",
      "tokens": 300
    },
    {
      "id": "1458ca2c2ade3927c19b61cb",
      "path": "governance/project/orchestration/packages/P1-MORNING-20261112.md",
      "text": "### P1-7 ACT-EXAMIN-SETS-1: the owner's C1-C8 and two writer briefs\n1. **Question:** the choices in `.gov-runtime/scratch/orchestrator/drafts/examin-sets/FOR-THE-OWNER.md` and the briefs\n   `EXAMIN-writer.md`, `PROVING-GROUND-writer.md` beside it.\n2. **Options:** as in that file.\n3. **Costs:** as in that file.\n4. **Recommendation:** none here: the owner's, unread by the owner; the CTO's 08:00 advice to apply it by hand is withdrawn.\n5. **Confidence:** n/a.\n6. **Blocks:** EXAMIN-SETS-1, then ACCEPTED-REDS-1 and PATHMAP-EXP-1 (their befores), W2-93, W2-94, EXAMIN's copy.\n\n",
      "tokens": 145
    }
  ],
  "supplementary_query": "EXAMIN's question set: memory questions with gold sources about the owner's copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27\nBetween 10 and 20 questions about EXAMIN's code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner's release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]\nWritten by the walled writer from the wall's tree, `git archive` of the CTO's launch clone of the owner's copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN's real repository Verify: the record names the clone's path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy's commit; after the run `git status` in the workbench and in EXAMIN's real repository shows no change, and the owner's copy's file times are unchanged [DEC-723, DEC-728]\nWritten by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls' launch log names the approved brief's sha256; the guard's log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845]\nEvery gold source exists at the copy's recorded commit and holds the answer Verify: a counts-only script, written by the ticket's independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy's recorded commit and holds the answer (\"n of n hold\"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4]\nW2-61's KPI 6 (\"the same split for EXAMIN's set\") is met by this ticket; W2-61's close record names it as moved here Verify: a grep of W2-61's close record finds KPI 6 named as moved to W2-94; this ticket's visible and hidden folders hold the split of S1 [DEC-954, DEC-957]\nA hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times\nA write in the workbench, the owner's copy or EXAMIN's real repository; a clone outside ~/gov-os-runs/W2-94/. Verify: `git status` in the workbench, the owner's copy and EXAMIN's real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none\nA gold source that does not hold its answer. Verify: the S4 script on a planted source that does not hold its answer reports that question's id as failing",
  "further_batch": [
    {
      "id": "07a27bdd5e473e6bd212e5dc",
      "path": "tests/acceptance/W2-94/README.md"
    },
    {
      "id": "1770a92afc37ec88dee3af73",
      "path": "docs/probes/DAEO-g87r/PR-DAEO-g87r.md"
    },
    {
      "id": "e2f95944dfbf0265111efefb",
      "path": "governance/project/path-map.yaml"
    },
    {
      "id": "DEC-1152",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "DEC-1151",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "4e4fca8a170b9e4b344a1bc9",
      "path": "docs/probes/DAEO-g87r/PR-DAEO-g87r.md"
    },
    {
      "id": "f204ab3022a169e962b92ab3",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "593a9864fb07d41cc1e72a95",
          "path": "tests/acceptance/W2-94/test_w2_94_s1_split_form.py"
        },
        {
          "id": "d6ac0e20c58f37d56fe1191f",
          "path": "tests/acceptance/W2-94/README.md"
        },
        {
          "id": "1458ca2c2ade3927c19b61cb",
          "path": "governance/project/orchestration/packages/P1-MORNING-20261112.md"
        },
        {
          "id": "07a27bdd5e473e6bd212e5dc",
          "path": "tests/acceptance/W2-94/README.md"
        },
        {
          "id": "1770a92afc37ec88dee3af73",
          "path": "docs/probes/DAEO-g87r/PR-DAEO-g87r.md"
        },
        {
          "id": "e2f95944dfbf0265111efefb",
          "path": "governance/project/path-map.yaml"
        },
        {
          "id": "DEC-1152",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1151",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "4e4fca8a170b9e4b344a1bc9",
          "path": "docs/probes/DAEO-g87r/PR-DAEO-g87r.md"
        },
        {
          "id": "f204ab3022a169e962b92ab3",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "07a27bdd5e473e6bd212e5dc",
      "reason": "budget exceeded"
    },
    {
      "id": "1770a92afc37ec88dee3af73",
      "reason": "budget exceeded"
    },
    {
      "id": "4e4fca8a170b9e4b344a1bc9",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1151",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1152",
      "reason": "budget exceeded"
    },
    {
      "id": "e2f95944dfbf0265111efefb",
      "reason": "budget exceeded"
    },
    {
      "id": "f204ab3022a169e962b92ab3",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 8868,
  "budget": {
    "limit": 9000,
    "used": 8868
  },
  "left_out": {
    "count": 8,
    "superseded": [
      "DEC-038",
      "DEC-045",
      "DEC-047",
      "DEC-048",
      "DEC-049",
      "DEC-636",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "a4b42c9115203d5da80f39994db144080287dd00b837aca08e4a61f2306405e8"
}
