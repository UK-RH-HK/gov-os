# Emergency task: W2-54's six CPU-only acceptance cases revised to DEC-1033 (independent test designer)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** independent test designer. **Worktree:** `/home/usain/gov-os-worktrees/EMG-w254`, branch
`emg/w2-54-dec1033` (from `w2/integrate` `3630679c`). **Ticket:** `DAEO-0rfi` (W2-54). TMPDIR `/tmp/gov-os-emg-w254`.

## Why
DEC-1033 item 2 (b) (the owner, 2026-11-02) replaced DEC-798 (the query embedder on the CPU only): a question's vector
is accepted from any device, and the query server now runs on the GPU (ACT-QUERY-GPU-2, done 18:30; the code since
`6ed6a5ae`, on `w2/integrate`). DEC-1033 item 3: "any acceptance test the patches turn red is revised afterwards by a
test designer." Six cases of `tests/acceptance/W2-54/test_w2_54_cpu_embedder.py` still enforce DEC-798 and are red on
`w2/integrate`; the merge queue refuses every landing on them (it stopped the W2-122 + W2-123 landing at 17:00):
- `test_an_embedder_at_the_cpu_address_that_does_not_report_the_model_on_the_cpu_gives_no_query_vector[gpu]` and `[partial]`
- `test_a_read_starts_the_cpu_embedder_at_its_address_with_no_gpu_and_never_stops_it[GOV_OLLAMA_BIN]`, `[PATH]`, `[HOME]`
- `test_two_reads_at_once_leave_one_cpu_embedder_serving_and_both_get_their_answer`

## The work
1. Read DEC-798, DEC-1033, DEC-1037 and DEC-1039 in `docs/DECISION_REGISTER.md`, the ticket `.tickets/DAEO-0rfi.md`,
   `tests/acceptance/W2-54/README.md` and the file above. The behaviour now in force is in the code on `w2/integrate`
   (`src/gov/retrieval/semantic.py`, `src/gov/retrieval/ollama.py`; the merged fix `6ed6a5ae` and its unit tests
   `tests/unit/retrieval/test_emg_query_device.py`): read them to state the behaviour precisely. This is a revision
   of older tests under the owner's named decision, not a ticket in progress, so reading that code is allowed.
2. Revise each of the six to the behaviour in force, keeping what each guarded that still holds (for example: a read
   starts the query embedder at its address and never stops it; two reads at once leave one serving and both get
   their answer; a server that does not report the model gives no vector, named). Remove only what DEC-1033 replaced
   (the CPU-only demand, the GPU hidden at start). Rename a case when its name states the old rule. Retire a case
   only if nothing in force replaces it, with the reason in the README. Stand-ins only: never the real servers.
3. Check the rest of `tests/acceptance/W2-54/` and the README for anything else that states DEC-798; revise it only if
   it is red for the same reason; list it either way.
4. Run the revised file (and the W2-54 suite) through the gate on this worktree's `src`: green now, since the
   behaviour exists. Show the six's old red and new green.
5. Commit only under `tests/acceptance/W2-54/`, with `--trailer "Rewrite-Reason: DEC-1033"`, `Task: DAEO-0rfi`,
   `Implements: DEC-1033`, `Role: independent-test-designer`.

Return with the head (12 digits), each case's old name -> new name and one line on what it now checks, and the run's
results. Estimate: 45 minutes.
