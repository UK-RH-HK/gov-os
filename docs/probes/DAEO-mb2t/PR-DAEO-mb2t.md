---
type: probe
task: DAEO-mb2t
reviewer_session: 1bfc7308-f36e-4287-b855-23682fdee16d
implementer_session: 25afed7d (eng-1-2), 50e4faf2 (eng-2-3); test designers e917181c (td-1), ba23c5dd-e10d-4539-9073-85f689c39f8f (td-2)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 7a3aecb38fb56260569b3acafbf0e089fd043499
decisions_applied: [DEC-1027, DEC-1015, DEC-1150, DEC-954, DEC-530, DEC-1083]
---

# Probe record: W2-124 (DAEO-mb2t)

STANDARD review, one round, by an independent auditor (Opus, high), read-only; the full return is in the lead's
records (`.gov-runtime/scratch/lead/log/rv-1.result.md`).

- **What was probed:** head `7a3aecb38fb5` of `w2/W2-124`, run, not only read; everything under the reviewer's TMPDIR.
  - S1, S2, S5, F1 through `gov rebuild` on planted projects: an embedded namespace with the embedder unavailable
    (exit 1, `REBUILD_FAILED`, `store: semantic`, no warm-base record), the same with `--no-embeddings` (exit 0), a
    namespace not embedded (exit 0, `requested: false`), no path map (exit 0, `complete: false`, `not_built` named),
    a healthy stand-in (exit 0, record written), a hung stand-in (exit 1 after about 221 s), a part-way stand-in
    (exit 1, a partial store left, no record), no `.gitleaks.toml` with `--no-embeddings` (exit 0, `not_built` named).
  - S4: `gov.close.rebuild_gate.semantic_failure` on 11 planted results (fails closed on absent, null, non-dict,
    error envelope, `not_recreated`, a string `"false"`; passes only `recreated` and `requested: false`, the rule of
    `rebuild_semantic_check.py`); `close.batch._rebuild` on a planted partial result refuses; `rebuild_slot.sh` with a
    stand-in envelope: `not_recreated` and `null` exit 75, `recreated` and `requested: false` exit 0.
  - S3, F2: adoption's refresh stage: a semantic refusal puts `SEMANTIC_NOT_RECREATED` (reason, `gov rebuild`) in the
    committed A6 record and in the report, nothing raised; any other refusal still `ADOPT_INDEX_REFRESH_FAILED`.
  - **The owner's check of P1-L (a) (DEC-1150 (3)):** the 20 earlier cases revised under `Rewrite-Reason: DEC-1027 C`
    (commit `bb6a068bd`) were run, 31 of 32 rows, against 21 breaks of the behaviour each guarded, one at a time, on a
    copy of the tree: every revised case turned red under the break of its own guard (pin check skipped, code dropped,
    lexical not built, CPU check skipped, canary indexed, stale search raising, stage key dropped, nondeterministic
    store, vectors deleted, words dropped, link switched, warm-base record written, seed not performed, cut dropped).
    Case 9 (`test_w2_13_latency`, local_only) was stated only by the reviewer; the lead ran it outside the sandbox at
    this head: 1 passed in 72.6 s. Only the 13 files changed, each change carries its Rewrite-Reason, no assertion was
    dropped and no bound widened.
  - Commits: the four ticket commits carry `Task: DAEO-mb2t`, roles matching their paths, `Implements:` within
    `sources:`, paths within `allowed_paths`.

- **What it found:** no blocking finding; three low, none needing a round.
  - **L-1 (low), revised case 13** (W1-41 `[every-namespace-not-embedded-full]`): its full row compares the stores
    only over those the refused reference built (lexical, semantic; the code index runs after the semantic check). A
    code-index difference confined to full mode for a non-embedded project would pass; the sibling `[…-no-embeddings]`
    row still catches one in both modes. The case keeps its point (ok, exit 0, lexical recreated, the words).
  - **L-2 (low), revised case 10** (W2-76 timings `[full]`), not a revision defect: an untimed semantic stage reads 0
    and passes, as before the revision; the revision added that the semantic store is recreated.
  - **L-3 (low), S3, out of scope:** with no embedder, A6's refresh stops at the semantic check, so the code index and
    the compaction are not refreshed and the finding names only the semantic store; nothing after A6 reads them, and
    the finding's `gov rebuild` repairs all of it.

- **Lead's verification at this head:** `lead_verify` 5492 tests, 5 red: 4 in `tests/unit/resources/test_w2_157_backstop.py`
  (green alone, load-sensitive) and `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`
  (red on w2/integrate's head `95c957ae9` too: a shared base red); serial 2/2 green; `gov accept W2-124` pass, 46 passed,
  0 failed, every KPI line pass.

- **Judgement:** PASS (the reviewer's verdict; the orchestrator's judgement concurs). L-1 to L-3 are proposed as rows.
