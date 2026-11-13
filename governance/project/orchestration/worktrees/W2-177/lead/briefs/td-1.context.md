{
  "ticket": "DAEO-1k7y",
  "ticket_text": "---\nid: DAEO-1k7y\nstatus: in_progress\ndeps: []\nlinks: [DAEO-ouet, DAEO-cb2b, DAEO-wnnz]\ncreated: 2026-11-12T05:03:31Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-177\ntags: [wave-2, accept, signals, full, shared-red]\nwbs_id: W2-177\ntitle: 'The six W2-96 signal reds: gov accept''s clean-up under a signal, red in every tree''s verify and in the nightly of 11-12'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- src/gov/accept/**\n- tests/unit/accept/test_w2_96_run2.py\n- tests/unit/accept/test_w2_96_review3.py\n- tests/unit/accept/test_w2_96_review4.py\n- tests/unit/accept/w2_96_reap.py\n- tests/unit/accept/test_w2_177*\n- docs/changes/W2-177-evidence.md\n- tests/acceptance/W2-96/w2_96_support.py  # P-W2-177-1 (a): _popen's signal start state, a test designer's revision (the CTO, 2026-11-12 07:05)\n- tests/acceptance/W2-56/w2_56_support.py  # P-W2-177-1 (a): start_launch's signal start state, the same revision\nest_loc: 80\nkpis:\n  success:\n  - 'S1 The cause is named with evidence before any change: why the six cases (`tests/unit/accept/test_w2_96_run2.py` four, `test_w2_96_review3.py` one, `test_w2_96_review4.py` one) and the W2-96 acceptance cases of the same family fail in the empty-HOME verify form, under the nightly''s cron start, and alone at load 18, yet passed in one W2-110 verify and alone with the real HOME; in particular whether the process under test starts with SIGINT ignored (the nightly''s red premise case R11 says the start form differs from the one the tests assume). Verify: docs/changes/W2-177-evidence.md names the cause, the start forms tried (empty HOME, real HOME, cron-like `setsid` with SIGINT ignored, a background job) and each one''s counts [DEC-1050]'\n  - 'S2 With the fix, the six cases pass in every start form S1 tried, ten runs each, with no timeout raised and no case skipped. Verify: the ten-run counts per form in the evidence; `skip_known.json` unchanged [DEC-966, DEC-1050]'\n  - 'S3 If the cause is the test''s own start form, not `gov accept`, the unit cases change and the W2-96 acceptance cases of the same family go to an independent test designer''s revision with a Rewrite-Reason (the CTO adds their paths then); if it is `gov accept`''s clean-up, the code changes and no test''s assertion is weakened. Verify: the diff: no unit assertion removed or loosened; a test change carries its reason in the commit [DEC-866, DEC-966]'\n  failure:\n  - 'A red hidden instead of fixed: a case added to skip_known.json, a timeout raised, a signal case skipped or deselected. Verify: the diff of skip_known.json, the cases'' timeouts and their markers is empty'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nnon_goals:\n- W2-56's two SIGINT ending cases (DAEO-wnnz, its own ticket), unless S1 finds the same cause, which the evidence then says\n- the latency reds of W1-19 and W2-13 (W2-155)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-966, DEC-1050, DEC-866, DEC-1010, DEC-953]\nacceptance_tests:\n  path: tests/unit/accept/\n  author: 'the existing W2-96 cases are the acceptance (S2); a new case in test_w2_177* for the cause S1 names, written red first'\ntrack: A\nreads:\n- tests/acceptance/W2-96/test_w2_96_at_run_2.py\n- tests/acceptance/W2-96/test_w2_96_at_no_leak.py\nneeds:\n- src/gov/accept/runner.py\n- src/gov/accept/command.py\n---\n# W2-177 The six W2-96 signal reds\n\nThe CTO's ruling P-W2-121-5 (2026-11-12 03:20, delegated P2): six cases in `tests/unit/accept/test_w2_96_{run2,review3,review4}.py`\n(signals and timeouts in `gov accept`'s clean-up) are red in 13 of the 14 most recent lead verifies across eight trees\n(W2-23, W2-11, W2-52, W2-176, W2-110, W2-115, W2-173, W2-121) and in the nightly of 11-12 (run 20261112-0404, `red-alone`,\nwith five W2-96 acceptance cases of the same family, among them the premise case R11). They are shared base reds: named\nin every return, not blocking. This ticket fixes them. Class C2. Diagnosis first (S1), then the smallest fix; a test\nrevision of the acceptance folder is a test designer's, not the engineer's.\n\n## P-W2-177-1 and P-W2-177-2 (the CTO, delegated P2, 2026-11-12 07:05)\n\n- **P-W2-177-1 (a):** an independent test designer's revision, with a Rewrite-Reason naming this ticket and DEC-866, of\n  `tests/acceptance/W2-96/w2_96_support.py`'s `_popen` and `tests/acceptance/W2-56/w2_56_support.py`'s `start_launch`: each of\n  SIGINT, SIGTERM and SIGHUP set to ignored when the case names it, otherwise to default, as `w2_96_reap.launch_gov` now does\n  (cause (B): a background start ignores SIGINT). Both paths are in allowed_paths for that revision only (dropped after the land).\n  No assertion is weakened. Not (b): the verify's and the nightly's start form stay as they are, so the tests own their start state.\n- **P-W2-177-2 (a):** done on w2/integrate (da6ba9c53): `type: task`.\n",
  "authority": [
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
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
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
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    }
  ],
  "mandatory": [
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
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
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
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    }
  ],
  "supplementary": [],
  "supplementary_query": "The six W2-96 signal reds: gov accept's clean-up under a signal, red in every tree's verify and in the nightly of 11-12\nS1 The cause is named with evidence before any change: why the six cases (`tests/unit/accept/test_w2_96_run2.py` four, `test_w2_96_review3.py` one, `test_w2_96_review4.py` one) and the W2-96 acceptance cases of the same family fail in the empty-HOME verify form, under the nightly's cron start, and alone at load 18, yet passed in one W2-110 verify and alone with the real HOME; in particular whether the process under test starts with SIGINT ignored (the nightly's red premise case R11 says the start form differs from the one the tests assume). Verify: docs/changes/W2-177-evidence.md names the cause, the start forms tried (empty HOME, real HOME, cron-like `setsid` with SIGINT ignored, a background job) and each one's counts [DEC-1050]\nS2 With the fix, the six cases pass in every start form S1 tried, ten runs each, with no timeout raised and no case skipped. Verify: the ten-run counts per form in the evidence; `skip_known.json` unchanged [DEC-966, DEC-1050]\nS3 If the cause is the test's own start form, not `gov accept`, the unit cases change and the W2-96 acceptance cases of the same family go to an independent test designer's revision with a Rewrite-Reason (the CTO adds their paths then); if it is `gov accept`'s clean-up, the code changes and no test's assertion is weakened. Verify: the diff: no unit assertion removed or loosened; a test change carries its reason in the commit [DEC-866, DEC-966]\nA red hidden instead of fixed: a case added to skip_known.json, a timeout raised, a signal case skipped or deselected. Verify: the diff of skip_known.json, the cases' timeouts and their markers is empty\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 6515,
  "budget": {
    "limit": 8000,
    "used": 6515
  },
  "hash": "625ac4678efc79657caccfe9d8289be84cd36fca5a7e7bd4c98067ea86d205a1"
}
