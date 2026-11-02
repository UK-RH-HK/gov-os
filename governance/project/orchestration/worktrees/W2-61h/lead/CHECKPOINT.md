# Lead checkpoint — DAEO-h2k3 (W2-61h), resume for the scoped run only (P-W2-61h-A5 option (a), delegated)

- State: branch w2/W2-61h at ac7dfa1790c7 (the CTO's merge of w2/integrate: DEC-1009 now resolves here), tree clean. Revision 6cc469cd66cf and checkpoint record 776d0ca4d335 stand. No worker this run.
- Rebuild 5 (09:24:21-10:14, slot wait 0 s): exit 75, REBUILD INCOMPLETE: semantic not_recreated "Ollama did not embed with qwen3-embedding:0.6b" (semantic_s 2659); lexical and codeintel recreated. Shared Ollama contended (probes 133 s, 24 s, 3 s at 10:14-10:17; client timeout 120 s).
- Done: select_tests once (log/select-3.json: scoped, core_changed [], unplaced = 24 hidden files, 31 targets, 283 pytest_options, base e639b83908c8, head ac7dfa1790c7); gov.__file__ in this tree; trailer_gate 12 commits, 0 lacking, 0 not resolving; keyword_warn 0.
- Rebuild 6 (10:17:30, slot wait 0): exit 0, lexical/semantic/codeintel recreated, total 580 s.
- Parallel (log/parallel.xml, parallel-3.exit): 4172 passed, 1 skipped (govbridge import, tests/unit/retrieval/test_lexical.py:54), 0 failed, 1059.6 s. Serial: no serial-only case selected (exit 0).
- gov context DAEO-h2k3 --json (CTO request, DEC-1027 H): ok true, not refused; tokens 3,573,359 vs budget limit 6000; mandatory 10 (9 DEC + DAEO-m1u3), supplementary 0, dropped 20. All 9 DEC entries carry the sha256 of the whole docs/DECISION_REGISTER.md (1,592,278 bytes): each decision loads the whole register. Log log/context-1.json. Orphan retrieve_check pid 3794318 (started 10:38:21, cwd this tree) left alive.
- gov check: first try (check-3) stopped by me at about 11:00 (foreground cap; blocked in retrieve_check); re-run check-4 in the background (log/check-4.json, exit check-4.exit).
- Next: read check-4; DONE at ac7dfa1790c7.
- Rule: no W2-61 failure message's question text in logs copied out or in the return; node ids and counts only.
- Loop count: 0.
- Brief gaps (running): DEC-1009 absent from the register in run 1 (resolved by the merge); gov retrieve on W2-00-store timed out inside the sandbox (ollama.com); heavy-job queue held a rebuild 88 min in run 2.
- Temp: /tmp/gov-os-lead-W2-61h (6.9M, 29 inodes at 09:24).
