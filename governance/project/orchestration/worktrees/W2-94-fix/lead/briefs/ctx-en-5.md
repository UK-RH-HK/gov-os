{
  "ticket": "DAEO-g87r",
  "ticket_text": "---\nid: DAEO-g87r\nstatus: in_progress\ndeps: [DAEO-m1u3]\nlinks: []\ncreated: 2026-10-30T22:14:09Z\ntype: task\npriority: 1\nassignee: independent-auditor\nexternal-ref: W2-94\ntags: [wave-2, audit, evaluation, held-out, standard, examin-minimum]\nwbs_id: W2-94\ntitle: 'EXAMIN''s question set: memory questions with gold sources about the owner''s copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: [DAEO-m1u3]\nallowed_paths:\n- tests/acceptance/W2-94/**  # its acceptance tests, form only (CTO, DEC-1167 (3): the close)\n- fixtures/evaluation/examin/check_gold.py  # S4's counts-only script, by the independent test designer, run by the CTO with --sets-root\n- docs/probes/DAEO-g87r/**  # the probe record\n- fixtures/evaluation/examin/visible/**\n- fixtures/evaluation/examin/hidden/**\n- governance/project/orchestration/tools/indep_launch.py  # the one-question fix flow (reopen 2026-11-14, DEC-1180 (3))\n- tests/unit/orchestration/test_w2_94_fix_flow_unit.py  # the engineer's unit tests of the fix flow\n- governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json  # S13: the optional fix object (rv P4, DEC-1180 (4))\n- tests/unit/orchestration/test_w2_149_indep_launch.py  # the one pin S13 meets, its optional map gains fix (P-W2-94-S13-1 (a), the CTO, DEC-1156 (7))\nkpis:\n  success:\n  - 'Between 10 and 20 questions about EXAMIN''s code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner''s release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]'\n  - 'Written by the walled writer from the wall''s tree, `git archive` of the CTO''s launch clone of the owner''s copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls'' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN''s real repository Verify: the record names the clone''s path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy''s commit; after the run `git status` in the workbench and in EXAMIN''s real repository shows no change, and the owner''s copy''s file times are unchanged [DEC-723, DEC-728]'\n  - 'Written by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls'' launch log names the approved brief''s sha256; the guard''s log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845]'\n  - 'Every gold source exists at the copy''s recorded commit and holds the answer Verify: a counts-only script, written by the ticket''s independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy''s recorded commit and holds the answer (\"n of n hold\"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4]'\n  - 'W2-61''s KPI 6 (\"the same split for EXAMIN''s set\") is met by this ticket; W2-61''s close record names it as moved here Verify: a grep of W2-61''s close record finds KPI 6 named as moved to W2-94; this ticket''s visible and hidden folders hold the split of S1 [DEC-954, DEC-957]'\n  - 'S6 A writer round 2 run with `--fix <id> --reason <code>` (`--kind writer --round 2` only; `<id>` matches `q` and two digits; `<code>` is one of check_gold.py''s per-question failure codes SOURCE_IS_SCAFFOLD, SOURCE_PATH_ABSENT, SOURCE_NOT_TEXT, SPAN_OUT_OF_FILE, HEADING_NOT_FOUND, ANSWER_NOT_IN_SPANS, NONEXISTENT_NAME_FOUND, NONEXISTENT_NO_NAME) is the one-question fix flow; either flag alone, another kind or round, a bad id or an unknown code refuses 17 with nothing built. Verify: planted runs of each wrong form, exit 17, no wall and no run folder made'\n  - 'S7 The fix flow stages exactly three inputs: `input/<id>.yaml` (a byte copy of the set''s `hidden/<id>.yaml`; absent or a link refuses 10), `input/verdict.txt` (the one line `<id> <code>`), and `input/sample.json` (`{\"sample\": [...]}`, the ordered `sample` list of the selection staged in the latest delivered round-1 writer run of the same set, read from that run''s own record; none found refuses 10); besides the wall''s fixed files, nothing else of the set or the sets root is staged (no `input/set/`, no `input/notes.md`). Verify: a planted set of several questions, the wall''s file list and bytes after staging'\n  - 'S8 The fix flow delivers only `out/<id>.yaml`: a plain file whose YAML parses to a mapping with `id` equal to `<id>`, else 20 and nothing lands; any file in `out/` other than it, `result.json` and `conflicts.md` refuses 20. On delivery it replaces `hidden/<id>.yaml` alone; every other file under the set''s folder (both halves, `DRAW.txt`, `hidden/dropped/`, any `XCHECK-r*.md`, the release record) is byte-unchanged; the replaced file is packed into the run''s archive and removed from the set. Verify: sha256 of every planted file before and after; the archive holds the old file'\n  - 'S9 The fix flow''s result is the writer schema''s (`questions`, `by_kind`, `by_area`, optional `stopped`) plus `action`, one of `corrected` or `replaced`; `questions` is 1 and each of `by_kind` and `by_area` sums to 1, else 20; a stopped result delivers nothing (21, as today). The counts object records `fix: {\"id\": <id>, \"code\": <code>, \"action\": <action>}` and nothing of the question''s content. Verify: planted results of each wrong form; the counts object''s keys'\n  - 'S10 The owner''s approved variant (`EXAMIN-writer-q02-fix.md`, sha256 0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173) launches through the fix flow end to end, byte for byte unchanged, on a planted sets root and launch clone with the fake session: its front matter is accepted as written. Verify: the planted end-to-end run, exit 0, the delivered file in place'\n  - 'S11 The script''s docstring gains the fix flow''s usage line; `governance/project/indep-walls/**` and `governance/project/indep-briefs/**` are unchanged (the owner''s class O). Verify: `git diff --stat` of the branch names only the ticket''s paths'\n  - 'S12 Without `--fix`, every existing flow behaves as before. Verify: the W2-149, W2-173 and W2-178 launcher unit suites pass unchanged'\n  - 'S13 The counts schema takes the fix flow''s `fix` key (rv P4, 2026-11-14): `indep-counts.schema.json` allows an optional `fix` object with exactly `id` (a question id), `code` (the reason code) and `action` (`corrected` or `replaced`), and nothing else; a fix run''s counts validate, so `finish()` no longer logs \"counts schema failed\" and `--counts-only` of a fix run no longer refuses with 17; every other flow''s counts validate as before [rv-fix P4, DEC-1180 (4)] Verify: a fix run''s counts with `fix` validate; a `fix` with an extra key or another action is refused; the W2-149 counts cases pass unchanged'\n  failure:\n  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session''s sandbox (the guard''s path map) are refused or find it 0 times'\n  - 'A write in the workbench, the owner''s copy or EXAMIN''s real repository; a clone outside ~/gov-os-runs/W2-94/. Verify: `git status` in the workbench, the owner''s copy and EXAMIN''s real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none'\n  - 'A gold source that does not hold its answer. Verify: the S4 script on a planted source that does not hold its answer reports that question''s id as failing'\n  - 'F4 A hidden file other than the fixed question reaches the fix flow''s wall, its result or its counts. Verify: S7''s planted wall listing; a grep of the counts object for planted content markers'\n  - 'F5 A fix run changes, moves or removes any set file other than `hidden/<id>.yaml`, or leaves the set changed after a refusal. Verify: S8''s sha256 comparison, also after a planted refusal at delivery'\n  - 'F6 The fix flow needs a change to the approved variant''s bytes or to the walls'' class O files to run. Verify: S10 runs the variant at its approved sha256; S11''s diff'\nprofile: STANDARD\nsources:\n- DEC-957\n- DEC-1175\n- DEC-1178\n- DEC-1180\n- DEC-954\n- DEC-828\n- DEC-820\n- DEC-845\n- DEC-723\n- DEC-728\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-94/\n  author: independent-test-designer (MR-3); form only (count, fields, sources named), never printing a question or an answer\ntrack: B\nlist_rows: []\n---\n# W2-94 EXAMIN's question set\n\nCard: MEMORY-SPEC-MAP gap 7, resolved by the owner in DEC-957; W2-61's KPI 6 moves here. The set measures memory on EXAMIN's copy at W2-27 (with W2-88's tools) and W2-15b.\n\n- **Before it starts, the orchestrator adds an `evaluation_sets` entry** `examin` to the path map (`visible: fixtures/evaluation/examin/visible/**`, `hidden: fixtures/evaluation/examin/hidden/**`, `measures` by tickets: W2-26, W2-27, W2-88, W2-15b and the retrieval tickets), so the guard refuses the hidden half from every worktree (W2-84).\n- **The clone:** made by the orchestrator or the auditor by exact path, `git clone --no-hardlinks` from the owner's copy (DEC-723, DEC-728); removed at the end.\n- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.\n- **Verify re-worded (CTO, 2026-11-13, DEC-1157 (12), DEC-1167 (3)):** S3's brief path is where it is installed; S4's script is the test designer's, run by the CTO (the walled writer has no shell); the KPI text before each Verify unchanged except the brief's path.\n\n**Role changed 2026-11-13 (P-W2-94-GOLD-2 (A), the CTO):** class audit -> implementation and role independent-auditor -> engineer, so the launcher lets the engineer the owner's W2-94 GOLD (a) names change `check_gold.py`; the walled writers' delivery is done, and the narrow check stays independent.\n\n**Reopened 2026-11-14 (DEC-1180 (3), the owner's P-Q02-RUN-1 (a): \"run today, as soon as it is built and reviewed\").** Hidden question q02 fails the gold check (ANSWER_NOT_IN_SPANS). The owner approved the writer's fix variant 0703aebf (DEC-1178 (5)), but the launch script's writer round 2 stages the whole set plus a checker's notes (EXAMIN's round 1 had none) and replaces the whole hidden folder, so the variant cannot run. S6-S12 add a one-question fix flow to `indep_launch.py`, which changes by a ticket (the class rules' catch-all), not an ACT; the walls' `kinds.yaml` and the briefs stay unchanged. After the land, the owner's operator installs the variant (its APPROVED line), commits it into the launch clone, runs the fix flow and `check_gold.py` (expected 20 of 20). No checker run: round 1 had none (FOR-THE-OWNER C8), and `check_gold` is the bar. The same flow can later carry the weekly re-anchor request (DECIDED-NOT-DONE row 203).\n\n**Kept open and reopened 2026-11-14 16:20 by the CTO (DEC-1180 (4), DEC-1157 (12); listed for the owner's reading):** the fix flow landed at 0b43625da (the queue closed the ticket in the same step). W2-94 stays open for q02's run with the owner's variant version 2 (DEC-1182 (5), sha 7aa6d88c, launch clone scaffold 3 6325d7ff17a3) and `check_gold` 20 of 20, and gains S13 for the review's P4 (the closed counts schema refuses the fix key). P1 was answered by the owner's v2; P8 is checked before the run; P2, P3, P5 stand as rows.\n\n**Path case 2026-11-14 18:05 (P-W2-94-S13-1 (a), the CTO under DEC-1156 (7); listed for the owner's reading):** S13 builds an optional root key `fix`. The W2-149 unit case `test_counts_schema_closes_every_object_and_string` (tests/unit/orchestration/test_w2_149_indep_launch.py, about lines 1088-1116) requires every root property to be required, except the keys in its hard-coded `optional` map. The ticket gains that one file. Its `optional` map gains `fix` for the whole schema, and nothing else in it changes. The revision is checked by a narrow independent check (DEC-1154). S12's and S13's \"the W2-149 cases pass unchanged\" read: unchanged except this one entry. S13's `action` may be `null` until the result has passed its checks; that is the reading built and judged correct by the narrow check (review R1). R2 (`$` accepts `\"q02\\n\"`) and R3 (the revised diff case passes with the schema deleted) are rows.\n",
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
      "id": "DEC-1175",
      "sha256": "0de5ab87eb9bb212c5b00657e36831c1e8ae9440514f62abb973c372bb72af8b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0de5ab87eb9bb212c5b00657e36831c1e8ae9440514f62abb973c372bb72af8b",
      "reason": "declared in sources",
      "tokens": 948
    },
    {
      "id": "DEC-1178",
      "sha256": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "reason": "declared in sources",
      "tokens": 1413
    },
    {
      "id": "DEC-1180",
      "sha256": "1aed4572bae57651e59b6436323003e665521b8c96c9e252984bc46c889d73cc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1aed4572bae57651e59b6436323003e665521b8c96c9e252984bc46c889d73cc",
      "reason": "declared in sources",
      "tokens": 916
    },
    {
      "id": "DEC-954",
      "sha256": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "reason": "declared in sources",
      "tokens": 1888
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
      "id": "DEC-1175",
      "sha256": "0de5ab87eb9bb212c5b00657e36831c1e8ae9440514f62abb973c372bb72af8b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0de5ab87eb9bb212c5b00657e36831c1e8ae9440514f62abb973c372bb72af8b",
      "reason": "declared in sources",
      "tokens": 948
    },
    {
      "id": "DEC-1178",
      "sha256": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "19b91069157fa779a6832a6c41a3d3773f65619dae435c2c1531c5501c9b0ebc",
      "reason": "declared in sources",
      "tokens": 1413
    },
    {
      "id": "DEC-1180",
      "sha256": "1aed4572bae57651e59b6436323003e665521b8c96c9e252984bc46c889d73cc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1aed4572bae57651e59b6436323003e665521b8c96c9e252984bc46c889d73cc",
      "reason": "declared in sources",
      "tokens": 916
    },
    {
      "id": "DEC-954",
      "sha256": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "902e04636b6455a405ed181006c9f27cffe75cb4b1b080e3cd3f1eef22bb0fbb",
      "reason": "declared in sources",
      "tokens": 1888
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
  "supplementary": [],
  "supplementary_query": "EXAMIN's question set: memory questions with gold sources about the owner's copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27\nBetween 10 and 20 questions about EXAMIN's code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner's release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]\nWritten by the walled writer from the wall's tree, `git archive` of the CTO's launch clone of the owner's copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN's real repository Verify: the record names the clone's path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy's commit; after the run `git status` in the workbench and in EXAMIN's real repository shows no change, and the owner's copy's file times are unchanged [DEC-723, DEC-728]\nWritten by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls' launch log names the approved brief's sha256; the guard's log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845]\nEvery gold source exists at the copy's recorded commit and holds the answer Verify: a counts-only script, written by the ticket's independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy's recorded commit and holds the answer (\"n of n hold\"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4]\nW2-61's KPI 6 (\"the same split for EXAMIN's set\") is met by this ticket; W2-61's close record names it as moved here Verify: a grep of W2-61's close record finds KPI 6 named as moved to W2-94; this ticket's visible and hidden folders hold the split of S1 [DEC-954, DEC-957]\nS6 A writer round 2 run with `--fix <id> --reason <code>` (`--kind writer --round 2` only; `<id>` matches `q` and two digits; `<code>` is one of check_gold.py's per-question failure codes SOURCE_IS_SCAFFOLD, SOURCE_PATH_ABSENT, SOURCE_NOT_TEXT, SPAN_OUT_OF_FILE, HEADING_NOT_FOUND, ANSWER_NOT_IN_SPANS, NONEXISTENT_NAME_FOUND, NONEXISTENT_NO_NAME) is the one-question fix flow; either flag alone, another kind or round, a bad id or an unknown code refuses 17 with nothing built. Verify: planted runs of each wrong form, exit 17, no wall and no run folder made\nS7 The fix flow stages exactly three inputs: `input/<id>.yaml` (a byte copy of the set's `hidden/<id>.yaml`; absent or a link refuses 10), `input/verdict.txt` (the one line `<id> <code>`), and `input/sample.json` (`{\"sample\": [...]}`, the ordered `sample` list of the selection staged in the latest delivered round-1 writer run of the same set, read from that run's own record; none found refuses 10); besides the wall's fixed files, nothing else of the set or the sets root is staged (no `input/set/`, no `input/notes.md`). Verify: a planted set of several questions, the wall's file list and bytes after staging\nS8 The fix flow delivers only `out/<id>.yaml`: a plain file whose YAML parses to a mapping with `id` equal to `<id>`, else 20 and nothing lands; any file in `out/` other than it, `result.json` and `conflicts.md` refuses 20. On delivery it replaces `hidden/<id>.yaml` alone; every other file under the set's folder (both halves, `DRAW.txt`, `hidden/dropped/`, any `XCHECK-r*.md`, the release record) is byte-unchanged; the replaced file is packed into the run's archive and removed from the set. Verify: sha256 of every planted file before and after; the archive holds the old file\nS9 The fix flow's result is the writer schema's (`questions`, `by_kind`, `by_area`, optional `stopped`) plus `action`, one of `corrected` or `replaced`; `questions` is 1 and each of `by_kind` and `by_area` sums to 1, else 20; a stopped result delivers nothing (21, as today). The counts object records `fix: {\"id\": <id>, \"code\": <code>, \"action\": <action>}` and nothing of the question's content. Verify: planted results of each wrong form; the counts object's keys\nS10 The owner's approved variant (`EXAMIN-writer-q02-fix.md`, sha256 0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173) launches through the fix flow end to end, byte for byte unchanged, on a planted sets root and launch clone with the fake session: its front matter is accepted as written. Verify: the planted end-to-end run, exit 0, the delivered file in place\nS11 The script's docstring gains the fix flow's usage line; `governance/project/indep-walls/**` and `governance/project/indep-briefs/**` are unchanged (the owner's class O). Verify: `git diff --stat` of the branch names only the ticket's paths\nS12 Without `--fix`, every existing flow behaves as before. Verify: the W2-149, W2-173 and W2-178 launcher unit suites pass unchanged\nS13 The counts schema takes the fix flow's `fix` key (rv P4, 2026-11-14): `indep-counts.schema.json` allows an optional `fix` object with exactly `id` (a question id), `code` (the reason code) and `action` (`corrected` or `replaced`), and nothing else; a fix run's counts validate, so `finish()` no longer logs \"counts schema failed\" and `--counts-only` of a fix run no longer refuses with 17; every other flow's counts validate as before [rv-fix P4, DEC-1180 (4)] Verify: a fix run's counts with `fix` validate; a `fix` with an extra key or another action is refused; the W2-149 counts cases pass unchanged\nA hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times\nA write in the workbench, the owner's copy or EXAMIN's real repository; a clone outside ~/gov-os-runs/W2-94/. Verify: `git status` in the workbench, the owner's copy and EXAMIN's real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none\nA gold source that does not hold its answer. Verify: the S4 script on a planted source that does not hold its answer reports that question's id as failing\nF4 A hidden file other than the fixed question reaches the fix flow's wall, its result or its counts. Verify: S7's planted wall listing; a grep of the counts object for planted content markers\nF5 A fix run changes, moves or removes any set file other than `hidden/<id>.yaml`, or leaves the set changed after a refusal. Verify: S8's sha256 comparison, also after a planted refusal at delivery\nF6 The fix flow needs a change to the approved variant's bytes or to the walls' class O files to run. Verify: S10 runs the variant at its approved sha256; S11's diff",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 13220,
  "budget": {
    "limit": 24000,
    "used": 13220
  },
  "hash": "98057debc78c7d2d1ddcc4a55198cf5883c8c5146d35bd47f22b68f3cc7c78f9"
}
