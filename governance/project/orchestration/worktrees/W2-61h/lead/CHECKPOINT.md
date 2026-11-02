# Lead checkpoint — DAEO-h2k3 (W2-61h), scoped run done — returned DONE at ac7dfa1790c7

- State: branch w2/W2-61h at ac7dfa1790c7 (verified head), tree clean; tests worktree and branch gone; no worker this run; no commit this run.
- Rebuild 5 (09:24-10:14, slot wait 0): exit 75, semantic not_recreated (Ollama did not embed; semantic_s 2659). Rebuild 6 (10:17:30, slot wait 0): exit 0, all three stores recreated, 580 s.
- select_tests (log/select-3.json): scoped, core_changed [], unplaced = the 24 hidden files, 31 targets, 283 pytest_options, base e639b83908c8.
- Parallel (log/parallel.xml): 4172 passed, 1 skipped, 0 failed, 0 errors, 1059.6 s. Serial: no serial-only case selected.
- gov check (log/check-4.json, exit 3): RED context-reproducibility (DAEO-i89t: AR-5 not in store), core-mutation (.tickets/DAEO-a3u2.md covers tests/acceptance/W2-86/...), retrieval-regression (600 s time limit); YELLOW core-decision-citations (209, warning), openspec-validate (no specs). Both red ticket files came from w2/integrate (7224a564, 1b3ba635); none from this ticket.
- gov context DAEO-h2k3 (DEC-1027 H): ok true; tokens 3,573,359 vs limit 6000; the 9 DEC mandatory entries each carry the whole register's sha256 (whole register per decision). log/context-1.json.
- trailer_gate: 12 commits, 0 lacking, 0 not resolving. keyword_warn 0. gov.__file__ in this tree.
- Left: orphan retrieve_check pid 3794318 (cwd this tree, from 10:38:21); /tmp/gov-os-lead-W2-61h 21M / 1543 inodes; log/serial.xml is run 1's (stale).
- Loop count: 0.
