{
  "ticket": "DAEO-g87r",
  "ticket_text": "---\nid: DAEO-g87r\nstatus: in_progress\ndeps: [DAEO-m1u3]\nlinks: []\ncreated: 2026-10-30T22:14:09Z\ntype: task\npriority: 1\nassignee: independent-auditor\nexternal-ref: W2-94\ntags: [wave-2, audit, evaluation, held-out, standard, examin-minimum]\nwbs_id: W2-94\ntitle: 'EXAMIN''s question set: memory questions with gold sources about the owner''s copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27'\nclass: audit\nstate_class: AUTHORITATIVE\nrole: independent-auditor\ndepends_on: [DAEO-m1u3]\nallowed_paths:\n- tests/acceptance/W2-94/**  # its acceptance tests, form only (CTO, DEC-1167 (3): the close)\n- fixtures/evaluation/examin/check_gold.py  # S4's counts-only script, by the independent test designer, run by the CTO with --sets-root\n- docs/probes/DAEO-g87r/**  # the probe record\n- fixtures/evaluation/examin/visible/**\n- fixtures/evaluation/examin/hidden/**\nkpis:\n  success:\n  - 'Between 10 and 20 questions about EXAMIN''s code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner''s release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]'\n  - 'Written by the walled writer from the wall''s tree, `git archive` of the CTO''s launch clone of the owner''s copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls'' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN''s real repository Verify: the record names the clone''s path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy''s commit; after the run `git status` in the workbench and in EXAMIN''s real repository shows no change, and the owner''s copy''s file times are unchanged [DEC-723, DEC-728]'\n  - 'Written by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls'' launch log names the approved brief''s sha256; the guard''s log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845]'\n  - 'Every gold source exists at the copy''s recorded commit and holds the answer Verify: a counts-only script, written by the ticket''s independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy''s recorded commit and holds the answer (\"n of n hold\"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4]'\n  - 'W2-61''s KPI 6 (\"the same split for EXAMIN''s set\") is met by this ticket; W2-61''s close record names it as moved here Verify: a grep of W2-61''s close record finds KPI 6 named as moved to W2-94; this ticket''s visible and hidden folders hold the split of S1 [DEC-954, DEC-957]'\n  failure:\n  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session''s sandbox (the guard''s path map) are refused or find it 0 times'\n  - 'A write in the workbench, the owner''s copy or EXAMIN''s real repository; a clone outside ~/gov-os-runs/W2-94/. Verify: `git status` in the workbench, the owner''s copy and EXAMIN''s real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none'\n  - 'A gold source that does not hold its answer. Verify: the S4 script on a planted source that does not hold its answer reports that question''s id as failing'\nprofile: STANDARD\nsources:\n- DEC-957\n- DEC-954\n- DEC-828\n- DEC-820\n- DEC-845\n- DEC-723\n- DEC-728\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-94/\n  author: independent-test-designer (MR-3); form only (count, fields, sources named), never printing a question or an answer\ntrack: B\nlist_rows: []\n---\n# W2-94 EXAMIN's question set\n\nCard: MEMORY-SPEC-MAP gap 7, resolved by the owner in DEC-957; W2-61's KPI 6 moves here. The set measures memory on EXAMIN's copy at W2-27 (with W2-88's tools) and W2-15b.\n\n- **Before it starts, the orchestrator adds an `evaluation_sets` entry** `examin` to the path map (`visible: fixtures/evaluation/examin/visible/**`, `hidden: fixtures/evaluation/examin/hidden/**`, `measures` by tickets: W2-26, W2-27, W2-88, W2-15b and the retrieval tickets), so the guard refuses the hidden half from every worktree (W2-84).\n- **The clone:** made by the orchestrator or the auditor by exact path, `git clone --no-hardlinks` from the owner's copy (DEC-723, DEC-728); removed at the end.\n- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.\n- **Verify re-worded (CTO, 2026-11-13, DEC-1157 (12), DEC-1167 (3)):** S3's brief path is where it is installed; S4's script is the test designer's, run by the CTO (the walled writer has no shell); the KPI text before each Verify unchanged except the brief's path.\n",
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
      "id": "cabc9e0ab23d11735d85296c",
      "path": "tests/acceptance/W2-94/test_w2_94_s1_split_form.py",
      "text": "\"\"\"W2-94, KPI success 1 (S1) -- the set's count, its fields, the recorded draw, the two halves and the release.\n\nS1: \"Between 10 and 20 questions ... after writing, a recorded seeded draw, stratified by category, splits the set into a\ndevelopment half (`hidden/visible/`) and a hidden half ... the owner's release step (`release_visible.sh`) then copies\nthe development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record\nholds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release\nstep copies exactly the development half into `visible/` and refuses a second release\".\n\nDriven through ``fixtures/evaluation/examin/check_gold.py`` on planted stand-ins (``w2_94_support``). The release\nstep's refusal of a second release is the owner's operator's record, not tested here (README).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport sys\nfrom pathlib import Path\n\nimport pytest\n\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n\nimport w2_94_cases as c  # noqa: E402\nimport w2_94_support as s  # noqa: E402\n\n\n",
      "tokens": 280
    },
    {
      "id": "cc322844f1785f009a319fc1",
      "path": "tests/acceptance/W2-94/README.md",
      "text": "# W2-94 (DAEO-g87r): EXAMIN's question set -- acceptance cases (form only)\n\nWritten by the independent test designer from the ticket's KPI lines and the approved writer brief\n(`governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`, sections 5 to 7), before and beside the check it tests.\n**Form only:** every case runs on a stand-in planted under pytest's `tmp_path` (made-up text about made-up files, each\ncarrying the word `zqxw94`). Nothing under `~/gov-os-eval`, `~/gov-os-runs`, a real `hidden` folder or any\n`fixtures/evaluation/examin/` folder of a tree was opened; no real question or answer is written anywhere.\n\nThe real set is checked by the CTO: `python3 fixtures/evaluation/examin/check_gold.py --sets-root <root> --copy <launch\nclone>` (written to this folder's cases; its docstring states the \"holds the answer\" rule and what it cannot catch).\n\nRun the folder with an empty HOME, through the heavy slot, `PYTHONPATH=<tree>/src`, and\n`-m \"not local_only\" -k \"not real and not green_here and not time_limit\"`. The exclusion leaves out nothing here: no case\nstarts a real model, embedder or network. `W2_94_CHECK_GOLD=<file>` runs another file in place of `check_gold.py` (the\n",
      "tokens": 300
    },
    {
      "id": "1458ca2c2ade3927c19b61cb",
      "path": "governance/project/orchestration/packages/P1-MORNING-20261112.md",
      "text": "### P1-7 ACT-EXAMIN-SETS-1: the owner's C1-C8 and two writer briefs\n1. **Question:** the choices in `.gov-runtime/scratch/orchestrator/drafts/examin-sets/FOR-THE-OWNER.md` and the briefs\n   `EXAMIN-writer.md`, `PROVING-GROUND-writer.md` beside it.\n2. **Options:** as in that file.\n3. **Costs:** as in that file.\n4. **Recommendation:** none here: the owner's, unread by the owner; the CTO's 08:00 advice to apply it by hand is withdrawn.\n5. **Confidence:** n/a.\n6. **Blocks:** EXAMIN-SETS-1, then ACCEPTED-REDS-1 and PATHMAP-EXP-1 (their befores), W2-93, W2-94, EXAMIN's copy.\n\n",
      "tokens": 145
    },
    {
      "id": "fce06ee36c37a4acc106478c",
      "path": "tests/acceptance/W2-94/README.md",
      "text": "## Not tested here (the CTO's and the operator's records)\n\n- **S2** (the clone made by exact path under `~/gov-os-runs/W2-94/examin/`; `COPY-HEAD.txt` names the copy's commit;\n  `git status` of the workbench and EXAMIN's real repository unchanged; the owner's copy's file times unchanged): the CTO's\n  record of the launch. `check_gold.py` reads `COPY-HEAD.txt` and the copy but never writes (`test_s4_the_check_writes_nothing`).\n- **S3** (the walled writer's independence: the launch log names the approved brief's sha256; the guard's log shows no\n  session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log\n  and ticket notes for a planted unique question word finds 0 hits): the CTO's record. The counts-only cases apply the\n  planted-word check to the script.\n- **The release step's refusal of a second release** (S1's last clause): the operator's record. `release_visible.sh` is\n  the owner's step and is not run here; the cases check its result (`visible/` equals `hidden/visible/`, the record names\n  each file with its sha256).\n",
      "tokens": 274
    },
    {
      "id": "e2f95944dfbf0265111efefb",
      "path": "governance/project/path-map.yaml",
      "text": "  # examin, EXAMIN's question set (W2-94; DEC-957, DEC-828 items 3-4, DEC-1130 (3)): 20 questions about the owner's copy,\n  # written blind by the walled writer (DEC-1101 (3); brief EXAMIN-writer), kept under the sets root (the measure's\n  # --sets-root), never in a tree. The ten visible-half questions are delivered with the hidden half and released to\n  # visible/ by the owner's one copy step; the ten measured ones stay in hidden/. Every role but the orchestrator is\n  # refused the hidden half (as memory-verdict-2); the CTO and leads by sets_root_hidden's fixtures/evaluation/*/hidden/**.\n  examin:\n    visible: [\"fixtures/evaluation/examin/visible/**\"]\n    hidden: [\"fixtures/evaluation/examin/hidden/**\"]\n    measures:\n      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]\n  # adoption-proving-ground, W2-81's held-out half (W2-93; DEC-957, DEC-941, DEC-1130 (3)): hidden questions and\n  # planted-problem variants per synthetic repository, written blind by the walled writer (brief PROVING-GROUND-writer),\n  # kept under the sets root. The visible half is W2-81's own questions folder; the runner reads the hidden half from\n",
      "tokens": 294
    },
    {
      "id": "DEC-1152",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1152 \u2014 EXAMIN's visible half released and final; the commit's pin kept in the run record, the decisions and W2-27's ticket; P1-M (a) a narrow check of W2-115's fix\n- **Status:** ACCEPTED (owner, 2026-11-12, in the chat ~19:20-19:35; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-12)`) \u00b7 **Under:** DEC-1143 (2)-(4), DEC-1151, DEC-1150 (2), DEC-1010\n- **Decision:**\n  - (1) **Step 7 done:** EXAMIN's development half released by the owner's operator (`release_visible.sh`, 10 files, exit 0, `.release-visible.record` written). **The ten questions stand:** the owner's operator checked each against EXAMIN's files at `0a82082495f5`, read only, each confirmed with file and lines. The released half is final.\n  - (2) **The pin:** EXAMIN's set and W2-27's adoption are at `0a82082495f52df068c3c6b518969b419f02fe95` (C1); recorded in the writer's run record, DEC-1143 (2), DEC-1151 (2) and W2-27's ticket; **no ACT pins it in the path map.**\n",
      "tokens": 257
    },
    {
      "id": "DEC-1151",
      "path": "docs/DECISION_REGISTER.md",
      "text": "  - (1) **`yes ACT-EXAMIN-WRITERS-INSTALL-1 8d1efb01`;** applied by the owner's operator as `ba27e4c0d` (the two briefs at `d37834e0...`, `57820503...`; the walls' approved list from `41e3969aa969`, 30 lines, to `9da7ff2055b0`, 32 lines); the bundle's commit line given its `--` pathspec afterwards (the operator's note).\n  - (2) **W2-94's copy:** the owner asked for one commit of the copy's 46 uncommitted files first; it already existed (`0a82082495f5`, made on the owner's word at 10:45, DEC-1143 (2)), and the copy is clean at it. The launch clone `~/gov-os-runs/W2-94/examin` at `0a82082` with one scaffold commit `48459935c435` (no code). Both walled writers delivered: W2-94 (run `20261112T185806Z-examin-r1`) 20 questions, schema ok; W2-93 (run `20261112T185824Z-adoption-proving-ground-r1`) 60 questions, schema ok; counts only to the CTO. The owner's step 7 (`release_visible.sh`) follows.\n  - (3) **W2-27's green-base line, (a), as the CTO wrote it:** before any scoped close in the copy, a full close at the adoption commit; every red fixed or listed in the copy's `accepted_reds` by an ACT the owner approves; that record is the copy's first green base.\n",
      "tokens": 292
    },
    {
      "id": "6ff478118f33d3c05cd82d34",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md",
      "text": "  6-hour reminder kept; the ticket table (W2-177 to W2-180 approved after the fact; W2-115b, W2-121c, W2-121d parked;\n  W2-181 parked, then returned by DEC-1156 (6)); **standing: no new ticket and no split is filed without the owner's\n  decision** (DEC-974); **standing: the two-refusal stop covers the same effect in another form** (a session refused\n  twice for an action stops and says so; it never reaches the same effect by another command, form or file). Basis:\n  questions 2 and 4.\n- DEC-1143 (2026-11-12): EXAMIN-SETS-1's answers: the two fixed writer briefs approved (`EXAMIN-writer.md` `d37834e08c86\u2026`,\n  `PROVING-GROUND-writer.md` `57820503b569\u2026`, `effort: high`); EXAMIN's copy is `~/gov-os-workbench/examin` at\n  `0a82082495f5` (the original `~/EXAMIN APP` untouched); the launch clone with one scaffold commit; 20 questions; the\n  release step kept; 10 per repository and 13 variants; the writer writes data only (the validator by an independent\n  test designer under W2-93); `measures` by roles; no checker for W2-94. Basis: questions 2 and 4.\n- DEC-1144 (2026-11-12): P1-A W2-11 merged by hand (`6f2234f40`, an exception to DEC-989); P1-B W2-157 reopened for the\n",
      "tokens": 295
    },
    {
      "id": "785b5e8a779cd7118899dc6e",
      "path": "tests/acceptance/W2-94/w2_94_support.py",
      "text": "**The planted sets root**: ``<root>/fixtures/evaluation/examin/{hidden, hidden/visible, visible}`` with ``qNN.yaml``,\n``DRAW.txt`` and ``.release-visible.record`` in the forms of the approved writer brief (sections 5 to 7) and of the\nowner's release step (``release_visible.sh``). ``build`` makes a good set of any count from 9 to 21: pairs of questions\nof the first categories, drawn by the brief's rule, plus one extra question when the count is odd.\n\n**The planted copy** (the CTO's launch clone): a temporary git repository whose first commit holds the made-up files the\nquestions cite, and whose second, the scaffold commit, adds ``governance/project/indep-walls/COPY-HEAD.txt`` naming the\nfirst. Planted beside the good files: a file that exists only in the scaffold commit, one that exists only in the working\ntree, one whose text changed in the scaffold commit, a binary file, and a scaffold-named path that the first commit also\nholds.\n\n**Planted words** begin with ``zqxw94``: one in every planted question, answer, heading and source path, so an output can\nbe searched for them.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport hashlib\nimport os\nimport re\nimport shutil\nimport subprocess\n",
      "tokens": 300
    },
    {
      "id": "DEC-1143",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1143 \u2014 EXAMIN-SETS-1's owner answers: the two writer briefs approved; C1 the workbench copy at one new commit; C2 the launch clone; C3 20; C4 the release step kept; C5 10 per repository and 13 variants; C6 the writer writes data only; C7 by roles; C8 no checker\n- **Status:** ACCEPTED (owner, 2026-11-12, in the chat ~10:40; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-12)`) \u00b7 **Under:** DEC-1130 (3), DEC-1101 (2)-(3), DEC-1082 (3), DEC-723 (3), DEC-736, DEC-757 (6), DEC-1136, DEC-1142 (8)\n- **Decision:**\n  - (1) **The two fixed writer briefs approved as they stand:** `EXAMIN-writer.md` (W2-94) sha256\n    `d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f` and `PROVING-GROUND-writer.md` (W2-93) sha256\n    `57820503b56948bf9e6ebe41abb2182c9a81db234e685218f21f71c69076549c`; both name `effort: high`, now passed to the session (W2-173 S1).\n  - (2) **C1:** EXAMIN's copy is `~/gov-os-workbench/examin`, after one new commit there of its uncommitted files, made on the owner's\n",
      "tokens": 272
    },
    {
      "id": "e14c0d3095270714af24ecd0",
      "path": "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-DECLARATION.md",
      "text": "## 4. The split by session\n- **How:** each session's half comes from an HMAC of its id under a 32-byte secret salt, stratified by role. Within\n  each role, sessions are sorted by their HMAC and given in turn to whichever half has fewer calls so far.\n- **What it guarantees:** about half the calls go to each half, and no session straddles the two.\n- **Where things are kept:** the salt and the held-out half are written only into the sealed folder, derived in code\n  from `--sets-root` (ACT-SANDBOX-SEAL-1). The tuning half goes to `~/gov-os-runs/SANDBOX-GUARD-EXP-1/tuning/`. The\n  tuner cannot recompute the split.\n- **Planted cases:** writer 1's cases join the tuning half, and writer 2's the held-out half.\n\n",
      "tokens": 178
    },
    {
      "id": "DAEO-h2k3",
      "path": ".tickets/DAEO-h2k3.md",
      "text": "- tests/unit/retrieval/test_w2_61h_families*\n- tests/unit/retrieval/test_w2_61h_anchor*\n- governance/project/path-map.yaml\nkpis:\n  success:\n  - 'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner''s operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084]'\n",
      "tokens": 254
    },
    {
      "id": "621f5faae9b6d6055c0c909e",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py",
      "text": "\"\"\"W2-61h (DAEO-h2k3): the 4 new visible questions, ``q21.yaml`` to ``q24.yaml`` -- KPI lines S1, S2, S3 (the\nvisible share), S4, F2 and F3.\n\nS1: \"Twenty-eight new questions ... in the form W2-61's visible half takes; after writing, a recorded seeded draw,\nstratified by category, sends 4 to the visible half ... (fixtures/evaluation/memory-retrieval/visible/q21.yaml to\nq24.yaml in the repository ...)\". S4: \"Every gold source exists at the commit the auditor reads and holds the answer,\ncited by path and heading or line\". F2: \"A question copied from or paraphrasing lens B's visible 20\". F3: \"A gold\nsource that does not hold its answer\". S2: \"Written by a session independent of the retrieval tickets\", judged from\nthe record: the commits' ``Role`` trailers (the CTO's decision of 2026-11-03, P2: by the role, not the ``Task``,\nsince D-4's cut rewrote these tests under the coordination ticket's id).\n\nThese cases read only this tree's tracked files and git record; they never open the sets root.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport pytest\nimport yaml\n\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n\n",
      "tokens": 296
    },
    {
      "id": "18fe8882286919acfd038ff2",
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "text": "| **W2-61h** (DAEO-h2k3) the hidden half | S1 28 questions, 4 visible and 24 hidden, a seeded stratified draw; S2 written by a session independent of the retrieval tickets; S3 the category spread; S4 every gold source exists and holds its answer; S5 nothing written outside `hidden/`; S6 the hidden half used only once refused from every tree (G-3 changes this to \"held outside every tree\") | `w2/W2-61h`, 7 commits at `ac7dfa17`; the 28 questions in `c5c10072`; W2-61's visible cases revised (DEC-1009); scoped run 4,172 passed | D-8 first (\u00a75); then only q21\u2013q24 and the test edits land; the form tests `tests/acceptance/W2-61h/` (never written); S1, S5, S6 re-worded to G-3 | test designer (form tests), the CTO (D-8's script and landing), reviewer |\n| **D-8** (G-3) the hidden half outside every worktree | (no ticket: G-3 as decided by DEC-1052) | \u2014 | \u00a75's steps; an owner ACT for the destructive part | the CTO, a test designer (W2-61's and W2-84's cases that expect the hidden half in the tree), reviewer |\n",
      "tokens": 254
    }
  ],
  "supplementary_query": "EXAMIN's question set: memory questions with gold sources about the owner's copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27\nBetween 10 and 20 questions about EXAMIN's code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner's release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]\nWritten by the walled writer from the wall's tree, `git archive` of the CTO's launch clone of the owner's copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN's real repository Verify: the record names the clone's path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy's commit; after the run `git status` in the workbench and in EXAMIN's real repository shows no change, and the owner's copy's file times are unchanged [DEC-723, DEC-728]\nWritten by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls' launch log names the approved brief's sha256; the guard's log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845]\nEvery gold source exists at the copy's recorded commit and holds the answer Verify: a counts-only script, written by the ticket's independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy's recorded commit and holds the answer (\"n of n hold\"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4]\nW2-61's KPI 6 (\"the same split for EXAMIN's set\") is met by this ticket; W2-61's close record names it as moved here Verify: a grep of W2-61's close record finds KPI 6 named as moved to W2-94; this ticket's visible and hidden folders hold the split of S1 [DEC-954, DEC-957]\nA hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times\nA write in the workbench, the owner's copy or EXAMIN's real repository; a clone outside ~/gov-os-runs/W2-94/. Verify: `git status` in the workbench, the owner's copy and EXAMIN's real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none\nA gold source that does not hold its answer. Verify: the S4 script on a planted source that does not hold its answer reports that question's id as failing",
  "further_batch": [
    {
      "id": "8513396a6dc1977021c56eae",
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md"
    },
    {
      "id": "ac979134f5029bf44ee005b6",
      "path": "tests/acceptance/W2-61h/README.md"
    },
    {
      "id": "80e4b756ce197f4cc6100775",
      "path": "governance/project/indep-briefs/examin-sets/EXAMIN-writer.md"
    },
    {
      "id": "994744ecfe3392ef2b8f6b57",
      "path": "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-1.md"
    },
    {
      "id": "935c7137849278d939a39183",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
    },
    {
      "id": "eaeed2c3b6f3a782ab5b5c1b",
      "path": "governance/project/orchestration/packages/ACT-ACCEPTED-REDS-1.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "cabc9e0ab23d11735d85296c",
          "path": "tests/acceptance/W2-94/test_w2_94_s1_split_form.py"
        },
        {
          "id": "cc322844f1785f009a319fc1",
          "path": "tests/acceptance/W2-94/README.md"
        },
        {
          "id": "1458ca2c2ade3927c19b61cb",
          "path": "governance/project/orchestration/packages/P1-MORNING-20261112.md"
        },
        {
          "id": "fce06ee36c37a4acc106478c",
          "path": "tests/acceptance/W2-94/README.md"
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
          "id": "6ff478118f33d3c05cd82d34",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "785b5e8a779cd7118899dc6e",
          "path": "tests/acceptance/W2-94/w2_94_support.py"
        },
        {
          "id": "DEC-1143",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "e14c0d3095270714af24ecd0",
          "path": "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-DECLARATION.md"
        },
        {
          "id": "DAEO-h2k3",
          "path": ".tickets/DAEO-h2k3.md"
        },
        {
          "id": "621f5faae9b6d6055c0c909e",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "18fe8882286919acfd038ff2",
          "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md"
        },
        {
          "id": "8513396a6dc1977021c56eae",
          "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md"
        },
        {
          "id": "ac979134f5029bf44ee005b6",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "80e4b756ce197f4cc6100775",
          "path": "governance/project/indep-briefs/examin-sets/EXAMIN-writer.md"
        },
        {
          "id": "994744ecfe3392ef2b8f6b57",
          "path": "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-1.md"
        },
        {
          "id": "935c7137849278d939a39183",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "eaeed2c3b6f3a782ab5b5c1b",
          "path": "governance/project/orchestration/packages/ACT-ACCEPTED-REDS-1.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "80e4b756ce197f4cc6100775",
      "reason": "budget exceeded"
    },
    {
      "id": "8513396a6dc1977021c56eae",
      "reason": "budget exceeded"
    },
    {
      "id": "935c7137849278d939a39183",
      "reason": "budget exceeded"
    },
    {
      "id": "994744ecfe3392ef2b8f6b57",
      "reason": "budget exceeded"
    },
    {
      "id": "ac979134f5029bf44ee005b6",
      "reason": "budget exceeded"
    },
    {
      "id": "eaeed2c3b6f3a782ab5b5c1b",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 11759,
  "budget": {
    "limit": 12000,
    "used": 11759
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
  "hash": "968380b15d67644ae413af391ddf8429c430c59398a713f1f09bd89f0c54de05"
}
