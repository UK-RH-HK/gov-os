# W2-78 packages (draft for the return)

## P-W2-78-MIGRATION (DEC-818)
1. Context: the four lists are the owner's commits (DEC-757, DEC-766, DEC-862); the path map is owner-only; W2-78 reads them from governance/project/records/ only. The pinned judge reads the path map until the re-pin.
2. What happened: branch holds the four record files (engineer commit 6a3fd38062f2), each identical to the base's path map list (entry_check.py PASS: 24/0/47/1). Readers tolerate the path map's key only as the exact copy. W1-08's namespace case is red on the branch: no namespace maps governance/project/records/** (gov.check.pathmap does not see it: its namespaces must be a list, this path map's is a mapping).
3. Why it matters: a wrong order breaks closes. ACT-2 before the re-pin: the pinned judge reads no lists (accepted_history empty -> the 47 commits judged again; load_sensitive empty -> W1-46/W1-19 not excused). ACT-2 before command.py's fix: the per-test results stop, so load-sensitive reruns and accepted reds stop.
4. Options:
   (a) recommended: ACT-1 now (namespace line; harmless to the pin) -> merge W2-78 with the record files accepted by decision as the owner's entries moved unchanged (provenance: the ratchet's own rule keeps the original owner commits as adders; the move adds nothing) -> re-pin -> ACT-2 (remove the four lists) once command.py:234, the earlier suites and the outside readers are updated.
   (b) the owner commits the record files himself (ACT-1 with the four files and the namespace, Role: owner) before the merge; the branch's identical files merge as an identical add. Costs one more owner commit; provenance identical (the move adds nothing either way).
   (c) one ACT after the merge (namespace + removal): the branch's verification stays red on W1-08 until then, and the removal lands before the re-pin -> closes break. Not recommended.
5. Recommendation: (a), confidence medium-high. Decision text: "the four record files of W2-78 (6a3fd38062f2) are the owner's entries moved unchanged (DEC-941 item 5)".
6. Blocks: the merge (W1-08 red until ACT-1; decision on the files). Not the work.

## P-W2-78-COMMAND (command.py:233-234)
`told` is decided by `settings.get(accepted_reds|load_sensitive)` (the path map). After ACT-2 it is None: no per-test results, so the ratchet never runs on the reds: accepted reds stop being covered and load-sensitive reruns stop (fails closed, loses the quarantine). Fix: decide from the record files (e.g. `any(_ratchet.counted_entries(root, k)[0] ...)` or `history.record_list(root, k)[0]`). Owner of path: W2-68 / W2-57. Blocks ACT-2 only. Confidence high.

## P-W2-78-EARLIER-SUITES (from td-1 and eng-1)
Earlier suites plant the lists in temporary path maps, so under the one-source rule they go red: W2-01 (25), W2-07 (8), W2-53 (26), tests/unit/close test_history.py (13), test_ratchet.py (4), test_w2_07_decision_records.py (2) (W2-67's paths), W2-66 test_the_record_only_paths_are_dec_891_s_places_and_nothing_else (DEC-866: DEC-929 item 1 / DEC-941 item 5 widen DEC-891's places), W1-01's two live cases after ACT-2 (its support reads the path map). Options: (a) a test-designer batch revises them (fixtures write record files; W2-66 RECORD_PLACES widened with Rewrite-Reason: DEC-941 item 5; W1-01 support reads the record file), landing with or before the merge (recommended, high); (b) a transitional reading (a path-map key counts where the history never held its record file) — contradicts the brief's one-source rule and keeps two sources for every temp project; (c) accept the reds until a later batch — W2-53 is in record_reading, so every close would be red. Blocks the merge (the full regression).

## Outside readers (the orchestrator, with ACT-2)
nightly_alone.py (accepted_reds), tools: validate_entry.py (patch keys -> record files), trailer_gate.py, queue gate (e), check_exemption_pin.py, draft_* tools.
