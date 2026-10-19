---
type: probe
task: DAEO-0rfi
reviewer_session: 71980794-2a49-4944-90b7-9cb37e5067a5
implementer_session: f6c6f6da-11ea-48fa-921b-69d0c5cf19e6
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 7661402c041b048d637977ef4c3be5f11a729aa3
---

# Probe record: W2-54 (DAEO-0rfi), the ticket's whole change, the one review (DEC-413)

- **What was probed.** Head `7661402c041b048d637977ef4c3be5f11a729aa3` of `w2/W2-54` (CP-DAEO-0rfi-0026), the
  ticket's whole change since its base `b644d28a`: the stable sort of the context packet's `dropped` list, the
  context-reproducibility check's declared time limit, the `audit-report` type, the query vector and its cache
  (DEC-773, DEC-782), and the CPU-only query embedder on its own port with the device in the cache key (DEC-798),
  with DEC-811's test rewrites (`75049714`) and builder-test fixture (`a0cb797e`). Implementers: round 4's engineer
  session `f6c6f6da-11ea-48fa-921b-69d0c5cf19e6` (`a93d5f72`, `a4801649`, `c53022d7`) and round 4c's engineer
  session `ae3c6158-158f-4a03-ada6-cb623d7dea9f` (`a0cb797e`).
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session
  `71980794-2a49-4944-90b7-9cb37e5067a5`, 2026-10-19), started through `gov launch` under its OS sandbox, with
  the reading tools alone; commissioned and judged by the orchestrator (DEC-137). It wrote nothing in the
  repository: the lead's tripwire before and after its session shows no change in this worktree, the main tree
  or any other worktree.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent
  mistakes and plausible accidents in ordinary work, not deliberate adversaries. A finding that needs a deliberate
  construction (a link planted at a protected name, git environment variables set by hand such as
  `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for
  the Wave 3 hardening pass, never a new round. Only a finding an honest agent can hit in ordinary work, and that
  fails open or loses work, justifies a round. Every finding below carries its two lines; none is marked
  `Ordinary work: yes` with `fails open` or `loses work`, so all six are rows and the judgement is pass.
- **What the sandbox could not reach** (the reviewer's last section) rests on the lead's runs at `a0cb797e`, in
  the lead's session: `gov check` exit 0 with context-reproducibility and core-schema green; W2-54 94 passed
  (the green-here cases and the `local_only` sandboxed-worker case included); the `shared_gpu` cases 2 passed (the CPU embedder at `127.0.0.1:11435`, size
  2371270737, `size_vram` 0; the shared runner's `size_vram` equal to its `size`, 2370652077, before, between and
  after); W1-21's hit@5 81.67 (pass line 80) with CPU query vectors against the GPU-built index.

The reviewer's record follows as returned.

Verdict: pass

**Head probed:** `7661402c041b048d637977ef4c3be5f11a729aa3` (branch `w2/W2-54`, base `b644d28a`).

**Step 0:** (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi` failed with "Read-only file system", as required. (b) `git hash-object -w --stdin` and `git update-index --refresh` both worked (rc 0). Role `independent-auditor`, ticket `DAEO-0rfi`, toplevel and branch as expected.

**`gov.__file__`:** `/home/usain/gov-os-worktrees/W2-54/src/gov/__init__.py`

## Probed and found sound

- **The dropped list and the hash.** A dropped entry holds only its id and its reason. Sorting on both is therefore a total order, and the list no longer depends on the order retrieval returns it in. Retrieval's own order is deterministic for equal scores: the fusion keeps first-seen order, the lexical route orders by path and line, and the semantic route by distance and chunk. The acceptance cases for reversed, rotated and shuffled orders, an empty retrieval and a missing index all pass. A context whose items differ still fails the check, naming the ticket.
- **The declared time limit.** Only the line `timeout-seconds: 600` was added. The change record §2, §4.4 and §5.6.4 record the run's seconds (128 to 130 s, 128.67 s, then 142.41 s after round 4), the 106 tickets measured, the load before and after, and 20 processors. 600 s is 4.2 times the latest run and what the sibling `retrieval-regression` check declares. A run past the limit is still red (that case passes). No other declaration changed.
- **The `audit-report` type.**
  - The schema file is byte for byte W2-02's (sha256 `bf5e10a9…`).
  - In `schema.py`, the type's map entry, its place among the standalone types and the two folder lines are W2-02's. The standalone-types line leaves out `adoption-verdict`, as the ticket says. Nothing of `close`, `adoption-verdict` or W2-02's nested-shape code was taken.
  - Core-schema on 12 edge records behaved as required:
    - A record outside `docs/audit/` without `type` fails, including under `docs/auditx/` (the folder is matched by path component, not by prefix) and under `.tickets/`.
    - A report missing `milestone`, `commit` or `pack_sha256` fails, naming that field, whether in the folder or typed explicitly.
    - An empty milestone, a milestone that is a number, a commit that is not hex, and `type: null` each fail.
  - Core-schema exits 0 on this worktree. The W1-43 audit report's sha256 is unchanged.
- **The query vector and its cache.**
  - Seven spellings of one question (case, doubled space, leading space, trailing newline, NFC and NFD) gave seven separate entries. Each key is the sha256 of the exact text sent, with the model, the revision and the device `cpu`. Repeating them sent no request and gave the same answers.
  - A failed (HTTP 500) or short embedding leaves no entry and changes no file.
  - At the CPU address, an embedder reporting the model on the GPU, half on the GPU, nothing loaded or another model gives no vector and no cache entry, sends nothing to the shared runner, and leaves the facet unavailable with a reason.
  - An unwritable runtime folder, a deleted cache, a cache file that is not a database and a read-only cache file all gave the same answer as a cold cache.
  - Six processes at once (25 shared and 10 own texts each) all exited 0 and agreed on every answer. The cache then held 85 entries out of 85 expected, with no duplicate, and `PRAGMA integrity_check` returned ok.
  - The bound holds: the file never grows past it, and bounds smaller than one entry store nothing.
  - `gov retrieve --json` and `gov context --json` change exactly one file, `.gov-runtime/query-vector-cache.db`.
- **The CPU-only embedder.**
  - Questions go only to `GOV_QUERY_OLLAMA_HOST` (default `127.0.0.1:11435`). The daemon is started with its own `OLLAMA_HOST` and `CUDA_VISIBLE_DEVICES=-1`, and is never stopped.
  - Chunks (build, refresh, rebuild) go only to `OLLAMA_HOST`. No request to the shared runner carries `options`.
  - There is no fallback to the shared runner when the CPU address is held or cannot be started.
  - Round 3's cache table, keyed without the device, is never read.
- **The acceptance tests.**
  - No engineer commit touches `tests/acceptance/**`, and every engineer commit stays inside the ticket's allowed paths. `tests/unit/semantic/test_semantic.py` was changed only after `4662871a` added it to them.
  - DEC-811's rewrites in `75049714`:
    - The lexical reads now ask a phrase the kiln note holds. The no-fallback check still sees a fallback, because the shared stand-in sends that phrase to the forge note.
    - Steps 5 and 6 ask new texts.
    - The hit@5 case now reads the headline figure, which is stricter than before. The pass line stays 80.
  - The W1 fixture changes only point the CPU address at the existing stand-in or dead port, and add `/api/ps`. W1-19 and W1-21 allow the one cache file. W1-46 widens what it strips to every `CLAUDE*` variable. Each has its `Rewrite-Reason:`, and no pass line or threshold moved.

## Findings (rows, not rounds)

**1. The CPU embedder's revision is not matched to the index's (probe 5, reproduced).**
- *What was done:* the stand-in at the CPU address reported another model build (`5ea155b9…`) than the one the index was built with (`ac6da0df…`).
- *What happened:* the search answered (`available` true), comparing a vector of one build with an index of another. The cache stored the entry under the CPU embedder's revision.
- *What should have happened:* a question's vector is used only when its revision is the index's; otherwise the facet is unavailable with a reason.
- *Severity:* low. Before this change the same gap existed with one daemon; two daemons add the case where they read different model stores.
  - Ordinary work: no, because both daemons are started from the same user's model store and report the same digest (the lead's measurement); a mismatch needs two model stores, which is a machine setup, not an agent's work.
  - Consequence: other (retrieval quality drops silently; both computations still agree, so no gate fails open).

**2. A lowered cache bound never shrinks the file (reproduced).**
- *What was done:* the cache grew to 204,800 bytes under the default bound, then reads ran with `GOV_QUERY_VECTOR_CACHE_MAX_BYTES=16384`.
- *What happened:* the file stayed at 204,800 bytes, and none of the 5 new questions was cached. Evicting the older half frees pages without shrinking the file.
- *What should have happened:* the next write brings the file within the bound, or replaces it.
- *Severity:* low.
  - Ordinary work: no, because it needs the setting lowered below the cache's size.
  - Consequence: other (the cache stops saving requests; answers are unchanged).

**3. A cache file that is not a database is never replaced (reproduced).**
- *What was done:* the cache file was overwritten with bytes that are not a database.
- *What happened:* every read answered correctly, but the file stayed as written, so nothing is ever cached again until someone deletes it.
- *What should have happened:* a write that finds an unreadable cache recreates it ("rebuildable from nothing").
- *Severity:* low.
  - Ordinary work: no, because the database's own journal prevents a torn file; it needs an outside write.
  - Consequence: other.

**4. On a GPU that `CUDA_VISIBLE_DEVICES` does not hide, the semantic facet is always unavailable (by reading, not reproduced).**
- *What was done:* read how the CPU embedder is started.
- *What happens:* on AMD (ROCm) or Apple (Metal) hardware, `CUDA_VISIBLE_DEVICES=-1` does not hide the GPU. The "CPU" daemon loads the model there, the CPU check refuses its vector, and every read falls back to lexical only.
- *What should have happened:* the daemon is started with the GPU hidden on every backend Ollama supports.
- *Severity:* low here, because this machine is NVIDIA under WSL. Could not be reproduced: no such hardware, and the sandbox hides the GPU.
  - Ordinary work: no, because it needs a non-CUDA machine.
  - Consequence: other (fails closed: semantic facet lost, no wrong vector used).

**5. The process that loses a write race answers with its own vector (by reading).**
- *What was done:* read how a vector is stored: an existing entry is never overwritten.
- *What happens:* when two processes compute the same key at once, the first entry wins in the cache, but the second process answers that read with the vector it computed itself, not the stored one.
- *What should have happened:* after storing, the process answers with what the cache holds.
- *Severity:* low. On one CPU embedder the two vectors are identical (the lead measured 0 differing across two processes).
  - Ordinary work: no, because it needs two different CPU embedders (other addresses or Ollama versions) on one store.
  - Consequence: other.

**6. The W1-19 and W1-21 write checks accept any single file (test weakness, by reading).**
- *What was done:* read the W1-19 `.gov-runtime` check and W1-21's `beyond_the_query_vector_cache`.
- *What happens:* they accept any one added or changed file under `.gov-runtime/` other than the store's, not the cache file by name.
- *What should have happened:* the checks name `query-vector-cache.db`.
- *Severity:* low. My probe 9 shows the code writes only the cache file.
  - Ordinary work: no, because the code under test writes only the cache file; only a future change could slip another file past these two cases.
  - Consequence: other.

## Not reproducible in this sandbox

- The sandboxed-worker case: `gov launch` could not reach the API through the proxy.
- The `shared_gpu` cases and the real-model W1-21 hit@5.
- `gov check` with context-reproducibility and core-schema green on this worktree (the `green_here` cases).
- Whether `CUDA_VISIBLE_DEVICES=-1` keeps the real GPU from the CPU embedder on this machine.

These rest on the lead's runs recorded in the change record §5.6.4.
