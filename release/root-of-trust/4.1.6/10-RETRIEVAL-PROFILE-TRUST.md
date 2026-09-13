# Output 10 — Reference retrieval profile trust integration

## 1. Constraints preserved

- Framework §14.3 and D-0006: no embedding or reranking model is a constitutional dependency; selection is
  per-repository and evidence-driven; the kernel default stays the dependency-free `hashed-ngram` embedder.
- D-0005: embed/rerank plugins fail closed; code intelligence degrades.
- D-0007 (restated in D-0008): plugin **authorisation** comes from the authenticated kernel's authority floor and the
  OS-written plugin registry. A profile signature is **provenance and integrity**, never authorisation.

The kernel therefore defines only the *verification contract* for profiles. Which model a certified reference profile
uses is profile content, replaceable by publishing another profile statement.

## 2. Current gap

`capabilities/python/govos_capabilities/embed_sentence_transformers.py` is invoked as
`--model sentence-transformers/all-MiniLM-L6-v2` and loads by hub **name**: no revision, no file digests, no package
pins, network download permitted. The plugin registry pins the descriptor and command files, not the model or the Python
environment. Weights can change underneath a "pinned" profile (TH-20).

## 3. Profile statement (`schemas/profile-statement.schema.json`, payloadType `…profile-statement.v1+json`, role `profile`)

| Field | Semantics |
|---|---|
| `profile_id`, `profile_version` | e.g. `retrieval-reference/sentence-embedding`, `1.0.0` |
| `capability` | `embed` \| `rerank` |
| `trust_profile` | `production` \| `test` |
| `compatibility` | `{framework_min, framework_max_exclusive, capability_protocol: "gov-capability/1"}` |
| `plugin.descriptor` | `{path, digest}` of the descriptor YAML |
| `plugin.implementation_files[]` | `{path, digest}` for every file executed (module sources, entry scripts) |
| `runtime` | `{kind: python \| native \| container, requires, lock {path, digest}, packages[] {name, version, digests[]}}` — installable with hash-checking only |
| `model` | `{id, source_kind, revision (immutable commit id, never a branch/tag), licence, dimensions, normalised, files[] {path, digest, size}}` |
| `evidence` | `{benchmark_record_digest, heldout_set_digest, metrics {recall_at_k, mrr, …}}` — the RES record that justified publication |
| `offline` | `true`: the plugin must load from the verified local files only |

## 4. Installation flow (`gov profile install <bundle>`, future MINOR release)

1. Quarantine the bundle (same tree rules as releases).
2. Authenticate the statement under the `profile` role; check compatibility with the authenticated kernel.
3. Recompute every plugin, runtime-lock and model file digest in quarantine (`PROFILE_DIGEST_MISMATCH`,
   `MODEL_DIGEST_MISMATCH`).
4. Materialise into derived runtime state `.governance-runtime/profiles/<profile_id>/<profile_version>/` (rebuildable,
   never authoritative), installing packages only from the hash-locked set.
5. Register the plugin through the existing `gov plugins register` path (authority, permission classes, registration gate
   unchanged); the registry entry additionally binds `profile_id`, `profile_version`, `profile_statement_digest` and the
   model file digests.
6. Selection remains `gov memory benchmark` → research record → gated decision → `gov memory select`; the pin in
   `PROJECT_POLICY.yaml` gains `MEMORY_POLICY.embedding.profile_statement_digest`.
7. The profile statement envelope is copied to `governance/trust/profiles/<profile_id>.dsse.json` so other machines can
   re-verify offline and rebuild the derived runtime.

## 5. Use-time verification

| When | Check | Failure |
|---|---|---|
| `rebuild-memory`, `memory verify`, `plugins health` | statement verifies; registry entry binds the same statement digest; every plugin, runtime and model file digest recomputed | `PROFILE_STATEMENT_INVALID`, `PROFILE_DIGEST_MISMATCH`, `MODEL_DIGEST_MISMATCH` → embedding fails closed (D-0005), index not built, no fallback |
| every plugin start (query path) | host passes `model_pins {revision, files[] {path, digest, size}}` in the invocation; plugin verifies before loading, runs with network disabled for the hub (offline mode) and returns observed digests; host compares | `MODEL_DIGEST_MISMATCH` → query refused |
| cost control | full digests at install, registration and rebuild; at plugin start a full digest when size or mtime differ from the verified record, otherwise a sampled digest; a full check at least once per process lifetime of a long-running server | documented trade-off (model files may be hundreds of MB) |
| kernel update | profile compatibility re-checked against the new authenticated kernel | `PROFILE_INCOMPATIBLE` → pin marked stale, query refused until reselected |

## 6. What stays outside framework trust

- Third-party or project-authored plugins keep working under D-0007 governance (registry, authority floor, gates). They
  can never display or record `profile_statement_digest`, and doctor distinguishes "reference profile (signed)" from
  "project plugin (governed, unsigned)".
- Remote embedding APIs (D-0006 class 3) cannot be digest-pinned; they are recorded as unsigned project plugins with the
  existing sensitivity restrictions.
