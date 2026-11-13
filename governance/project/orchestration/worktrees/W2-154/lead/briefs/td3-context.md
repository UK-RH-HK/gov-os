{
  "ticket": "DAEO-l4gf",
  "ticket_text": "---\nid: DAEO-l4gf\nstatus: in_progress\ndeps: []\nlinks: [DAEO-zqvn, DAEO-o5x1]\ncreated: 2026-11-10T12:05:36Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-154\ntags: [wave-2, implementation, standard, after-the-lift]\nwbs_id: W2-154\ntitle: 'The close''s serial plugin treats an entry its opt-in lists leave out as not in the run; nightly.sh reports the serial cases it ran'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/close/serial.py\n- src/gov/close/pytest_plugin/gov_close_serial_only.py\n- src/gov/close/command.py  # the serial-afterwards run's line only\n- governance/project/orchestration/nightly/nightly.sh\n- tests/unit/close/test_serial*\n- tests/acceptance/serial-only.txt  # S4 only: W1-16's ui_off line restored by a test designer with its Rewrite-Reason (the owner, DEC-1157 (12) route, 2026-11-13: S4 (a))\nkpis:\n  success:\n  - 'S1 An entry of tests/acceptance/serial-only.txt whose every case an opt-in list (tests/optin-lifted*.txt) leaves out of the run is \"not in this run\": the close''s serial plugin neither stops the serial phase on it (today exit 4, \"no case is named by the entry\") nor runs its cases elsewhere, and the run''s record names each such entry; an entry that names no case at all (no opt-in list explains it) still stops the phase, as today. Verify: a planted serial-only.txt with one entry whose every case an opt-in list leaves out, one entry that names no case and has no opt-in list, and the run''s record: the first run does not stop the serial phase and the record names the first entry; the second exits 4 with \"no case is named by the entry\" [DEC-1112 (3), DEC-1061, DEC-549]'\n  - 'S2 In a run that opts in to the list that holds such an entry''s cases, the entry is back in the serial phase: its cases run serially, never in the parallel phase. Verify: the planted run of S1 repeated with the opt-in list that holds the entry''s cases switched on: the run''s record shows those cases in the serial phase and none in the parallel phase [DEC-1112 (3), DEC-889 item 5]'\n  - 'S3 nightly.sh reports \"serial: N cases run\" for its serial phase, and a night whose serial phase ran no case (or ended with a collection error) is red, whatever its JUnit files say; a phase with nothing declared reads \"serial: 0 declared\" and is not red. Verify: planted nightly runs with a stub serial phase: one that runs 5 cases prints \"serial: 5 cases run\"; one that runs none, and one that ends in a collection error, are red though their JUnit files are green; one with nothing declared prints \"serial: 0 declared\" and is not red [DEC-1112 (3), the D-10 W2-13 review F1]'\n  - 'S4 Once S1 holds, W1-16''s ui_off entry returns to serial-only.txt (commented out on 2026-11-10 by the D-10 gate, b78f862a9), restored by a test designer with its Rewrite-Reason; the designer writes tests/acceptance/serial-only.txt, never the implementer. Verify: after S1 passes, `git log` on tests/acceptance/serial-only.txt shows the ui_off line restored in a commit with `Role: independent-test-designer` and a Rewrite-Reason, and no commit by the engineer role touches that file [DEC-1112 (3), MR-3]'\n  failure:\n  - 'An entry that names no case and no opt-in list explains passes silently. Verify: S1''s planted entry with no case and no opt-in list explanation: the serial phase stops with exit 4; a pass there is this failure'\n  - 'A night with a serial phase that ran nothing reads green. Verify: S3''s planted nightly with a serial phase that ran no case: it reads red; green there is this failure'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1112\n- DEC-1061\n- DEC-889\n- DEC-549\n- DEC-1109\nest_loc: 120\nacceptance_tests:\n  path: tests/unit/close/\n  author: 'independent-test-designer (MR-3), tests first: planted serial lists and opt-in lists, a planted nightly run'\ntrack: A\nlist_rows: []\nneeds: []\nreads:\n- src/gov/close/**\n- governance/project/orchestration/nightly/**\n- tests/acceptance/serial-only.txt\n- tests/optin-lifted*.txt\n- tests/unit/close/**\nwaits_on: []\n---\n# W2-154 The close's serial plugin and an entry out of the run; the nightly's serial count\n\nFiled by the CTO's D-10 helper, 2026-11-10, on the CTO's delegated decision (DEC-1112 (3)): build it **after the\nlift**, not now (the week's usage).\n\n- **Why:** D-4's cut (DEC-1061) moved every case of W1-16's ui_off file to the `breadth` opt-in suite. Its\n  serial-only.txt entry then named no case in a default run, and the close's serial plugin stopped the whole serial\n  phase at collection (exit 4; `gov_close_serial_only.py:54-60`). A full close refused; `nightly.sh` could read green\n  with no serial case run (the W2-13 D-10 review's F1, `governance/project/orchestration/reviews/D10-W2-13-review.md`).\n  The D-10 gate (option (a)) commented the entry out (`b78f862a9`); this ticket is option (b), the class fix.\n- **Riding along (after the lift too):** the `brief` citation in `src/gov/check/commands.py:15` and in the\n  docstrings of W1-07's, W1-26's and W1-32's command-list cases reads \"(W2-152, DEC-1088 (3))\"; it should read\n  \"W2-152 (W2-128 TPL-3; DEC-1052, DEC-1112 (3))\" (the D-10 command-list review's F1,\n  `reviews/D10-commands-review.md`). An engineer for the code comment, a test designer for the docstrings; recorded\n  here because no other open ticket holds those files.\n- **Sizes:** about 120 lines; one test designer, one engineer, one review.\n\n[DEC-1112 (3), DEC-1061, DEC-889 item 5, DEC-549]\n\n## Interface (DEC-1052; P-W2-154-1 (a), the CTO's delegated decision, DEC-1112 (3), 2026-11-12)\n\n- **I1 How the plugin knows (S1).** In the serial-afterwards run (its environment variable set), the plugin's\n  `pytest_collection_modifyitems` is `trylast=True` and records every item the run's other plugins (the project's conftest's\n  opt-in mechanism) passed to `pytest_deselected`. An entry with no collected case and at least one such deselected case is\n  \"not in this run\"; an entry with neither still raises `UsageError` \"no case is named by the entry\" (exit 4), as today. The\n  plugin stays standard-library only and never reads `tests/optin-lifted*.txt` itself.\n- **I2 What the run records (S1).** For each such entry the plugin prints `gov_close_serial_only: not in this run: <entry>`\n  and writes the entry, one per line, to the file named by `GOV_CLOSE_SERIAL_ONLY_OUT`; `command.py` reads that file after the\n  serial-afterwards run and its stated record (the serial run's entry) gains `\"not_in_this_run\": [<entry>, ...]`; `\"cases\"`\n  keeps only the entries that ran. When every given entry is out, the run ends exit 0 and the close counts a serial run of 0\n  cases, with no finding.\n- **I3 nightly.sh's serial lines (S3).** N is the number of `<testcase>` elements in `serial.xml`. With entries declared:\n  `serial: N cases run`. With nothing declared: `serial: 0 declared`, the serial phase skipped, not red (replacing today's\n  exit 2 \"no serial-only entry read\"). When N is 0, or the serial phase's exit is neither 0 nor 1 (a collection error),\n  nightly.sh appends `verdict: red serial: 0 cases run` or `verdict: red serial: collection error, exit E` after\n  `nightly_alone.py`'s line, so the final line reads red and the P1 ping follows (nightly_alone.py is not changed).\n- **I4 The test seam (S3).** With `NIGHTLY_SERIAL_STUB=<file>` set, nightly.sh skips the clone, the rebuild, the gate and both\n  suites, sources the stub (which sets `ENTRIES`, `s_exit` and writes `$JUNIT/serial.xml`), and runs only the serial count and\n  verdict steps. Tests run nightly.sh only with the stub; the real nightly is never run by a test.\n- **Out of this run:** the `--verify` path (`command.py:1572-1620`, the serial phase without the plugin) stays as it is (the\n  allowed path is the serial-afterwards run's line only); the riding-along citation in `src/gov/check/commands.py:15` is outside\n  the allowed paths and stays recorded here, not done.\n",
  "authority": [
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
      "id": "DEC-1061",
      "sha256": "a6d9604a1024d2b59e76ec5687f0d9e262889692921d1a1a0190c3dc314be58a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a6d9604a1024d2b59e76ec5687f0d9e262889692921d1a1a0190c3dc314be58a",
      "reason": "declared in sources",
      "tokens": 628
    },
    {
      "id": "DEC-889",
      "sha256": "555adc2f128673a6e5391f3c1ff191ccdbb8127e485e208220be491d87e48da3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "555adc2f128673a6e5391f3c1ff191ccdbb8127e485e208220be491d87e48da3",
      "reason": "declared in sources",
      "tokens": 3170
    },
    {
      "id": "DEC-549",
      "sha256": "669312f4c9f89eb0b8a394dcc34f8762cdcb9f0d174de8dda6032a37ea18f18a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "669312f4c9f89eb0b8a394dcc34f8762cdcb9f0d174de8dda6032a37ea18f18a",
      "reason": "declared in sources",
      "tokens": 663
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    }
  ],
  "mandatory": [
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
      "id": "DEC-1061",
      "sha256": "a6d9604a1024d2b59e76ec5687f0d9e262889692921d1a1a0190c3dc314be58a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a6d9604a1024d2b59e76ec5687f0d9e262889692921d1a1a0190c3dc314be58a",
      "reason": "declared in sources",
      "tokens": 628
    },
    {
      "id": "DEC-889",
      "sha256": "555adc2f128673a6e5391f3c1ff191ccdbb8127e485e208220be491d87e48da3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "555adc2f128673a6e5391f3c1ff191ccdbb8127e485e208220be491d87e48da3",
      "reason": "declared in sources",
      "tokens": 3170
    },
    {
      "id": "DEC-549",
      "sha256": "669312f4c9f89eb0b8a394dcc34f8762cdcb9f0d174de8dda6032a37ea18f18a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "669312f4c9f89eb0b8a394dcc34f8762cdcb9f0d174de8dda6032a37ea18f18a",
      "reason": "declared in sources",
      "tokens": 663
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    }
  ],
  "supplementary": [],
  "supplementary_query": "The close's serial plugin treats an entry its opt-in lists leave out as not in the run; nightly.sh reports the serial cases it ran\nS1 An entry of tests/acceptance/serial-only.txt whose every case an opt-in list (tests/optin-lifted*.txt) leaves out of the run is \"not in this run\": the close's serial plugin neither stops the serial phase on it (today exit 4, \"no case is named by the entry\") nor runs its cases elsewhere, and the run's record names each such entry; an entry that names no case at all (no opt-in list explains it) still stops the phase, as today. Verify: a planted serial-only.txt with one entry whose every case an opt-in list leaves out, one entry that names no case and has no opt-in list, and the run's record: the first run does not stop the serial phase and the record names the first entry; the second exits 4 with \"no case is named by the entry\" [DEC-1112 (3), DEC-1061, DEC-549]\nS2 In a run that opts in to the list that holds such an entry's cases, the entry is back in the serial phase: its cases run serially, never in the parallel phase. Verify: the planted run of S1 repeated with the opt-in list that holds the entry's cases switched on: the run's record shows those cases in the serial phase and none in the parallel phase [DEC-1112 (3), DEC-889 item 5]\nS3 nightly.sh reports \"serial: N cases run\" for its serial phase, and a night whose serial phase ran no case (or ended with a collection error) is red, whatever its JUnit files say; a phase with nothing declared reads \"serial: 0 declared\" and is not red. Verify: planted nightly runs with a stub serial phase: one that runs 5 cases prints \"serial: 5 cases run\"; one that runs none, and one that ends in a collection error, are red though their JUnit files are green; one with nothing declared prints \"serial: 0 declared\" and is not red [DEC-1112 (3), the D-10 W2-13 review F1]\nS4 Once S1 holds, W1-16's ui_off entry returns to serial-only.txt (commented out on 2026-11-10 by the D-10 gate, b78f862a9), restored by a test designer with its Rewrite-Reason; the designer writes tests/acceptance/serial-only.txt, never the implementer. Verify: after S1 passes, `git log` on tests/acceptance/serial-only.txt shows the ui_off line restored in a commit with `Role: independent-test-designer` and a Rewrite-Reason, and no commit by the engineer role touches that file [DEC-1112 (3), MR-3]\nAn entry that names no case and no opt-in list explains passes silently. Verify: S1's planted entry with no case and no opt-in list explanation: the serial phase stops with exit 4; a pass there is this failure\nA night with a serial phase that ran nothing reads green. Verify: S3's planted nightly with a serial phase that ran no case: it reads red; green there is this failure\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 7444,
  "budget": {
    "limit": 9000,
    "used": 7444
  },
  "hash": "b5a9ad2e192abddfb772f9dccec99d9b3d5dc1eb1c682e559583c150ba0c4d9f"
}
