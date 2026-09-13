# Output 10 — Reference retrieval profile trust integration

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 moves use-time integrity to host-side verification (RV-M7, CD-11), binds profiles to a purpose (`05`), and
> routes profile installs through the install transaction.

## 1. Constraints preserved

- **Framework §14.3 and D-0006.** No embedding or reranking model is a constitutional dependency. Selection is
  per-repository and evidence-driven; the kernel default stays the dependency-free `hashed-ngram` embedder.
- **D-0005.** Embed/rerank plugins fail closed; code intelligence degrades.
- **D-0007, restated in D-0008.** Plugin **authorisation** comes from the effective floor (authority, permission classes)
  and the OS-written plugin registry. A profile signature is **provenance and integrity**, never authorisation.

The kernel defines only the *verification contract*. Which model a reference profile uses is profile content,
replaceable by publishing another profile statement. That is how the selected embedding/reranker profile (Qwen, BGE or
another) joins the same supply-chain model without becoming constitutional:
**signed pinned identity → host-verified integrity → governed install → local use**.

## 2. Current gap (4.1.5)

`capabilities/python/govos_capabilities/embed_sentence_transformers.py` is invoked with
`--model sentence-transformers/all-MiniLM-L6-v2` and loads by hub **name**: no revision, no file digests, no package
pins, network download permitted. The plugin registry pins descriptor and command files, not the model or the Python
environment.

## 3. Profile statement

payloadType `retrieval-profile.v1+json`, purpose `retrieval-profile`. Schema: `schemas/profile-statement.schema.json`.

| Field | Semantics |
|---|---|
| `_type`, `trust_profile`, `trust_root_id` | as every statement (`07` §4) |
| `profile_id`, `profile_version` | e.g. `retrieval-reference/sentence-embedding`, `1.0.0` |
| `capability` | `embed` \| `rerank` |
| `compatibility` | `{framework_min, framework_max_exclusive, capability_protocol: "gov-capability/1"}` |
| `plugin.descriptor`, `plugin.implementation_files[]` | `{path, digest, size}` for the descriptor and every executed file |
| `runtime` | `{kind, requires, lock {path, digest}, packages[] {name, version, digests[]}}` — installable only with hash checking |
| `model` | `{id, source_kind, revision (immutable id), licence, dimensions, normalised, files[] {path, digest, size}}` |
| `evidence` | `{benchmark_record_digest, heldout_set_digest, metrics}` — the research record justifying publication |
| `offline` | const `true` |

## 4. Installation (`gov profile install <bundle>`, may ship in a later MINOR release)

1. Read the bundle through the secure reader into buffers where size allows. Model files larger than the in-memory
   limit are streamed and digested incrementally into a staging object.
2. Authenticate the statement under the `retrieval-profile` purpose (`05` SV-1…SV-10); check compatibility with the
   current snapshot.
3. Verify every plugin, runtime-lock, package and model digest.
4. Materialise into a **content-addressed store** `.governance-runtime/profiles/cas/<sha256>`, written from verified
   buffers or streams with exclusive creation, read-only permissions and, where the platform supports it, fs-verity
   enabled on each object. The runtime environment is built only from hash-verified package archives into
   `.governance-runtime/profiles/env/<profile statement digest>/`.
5. Register through `gov plugins register` (authority, permission classes and registration gate unchanged). The registry
   entry additionally binds `profile_id`, `profile_version`, `profile_statement_digest`, and the CAS digests of
   implementation and model files.
6. Selection stays `gov memory benchmark` → research record → gated decision → `gov memory select`. The pin in
   `PROJECT_POLICY.yaml` gains `MEMORY_POLICY.embedding.profile_statement_digest`.
7. The profile statement envelope is written to `governance/trust/profiles/<profile_id>.dsse.json` **through the install
   transaction** (operation `profile_install`), because `governance/trust/**` is a Protected Path (`18` §8).

## 5. Use-time verification — host-side

The plugin is a separate process whose outputs are T6. **Digests reported by the plugin are informational and never
establish integrity.** The host verifies.

| When | Host check | Failure |
|---|---|---|
| Registration, `rebuild-memory`, `memory verify`, `plugins health` | statement verifies; registry binds the same statement digest; host recomputes full digests of implementation files, runtime lock, environment files and model files | `PROFILE_STATEMENT_INVALID`, `PROFILE_DIGEST_MISMATCH`, `MODEL_DIGEST_MISMATCH` → embedding fails closed (D-0005); no index build; no fallback |
| Plugin start (every invocation) | host fully re-digests implementation files and the runtime lock (small); for model files: fs-verity measurement check where enabled, otherwise a full digest when size, inode or mtime changed since the last host verification, and otherwise a digest of host-chosen random ranges | mismatch → invocation refused |
| **After any invocation that feeds a persistent write** (index build, rebuild) | host fully re-digests model and implementation files **after the plugin exits and before committing index writes**; the index manifest records the profile statement digest and the kernel CI | mismatch → index writes discarded; `MODEL_DIGEST_MISMATCH` |
| Kernel update | profile compatibility re-checked against the new snapshot | `PROFILE_INCOMPATIBLE` → pin stale; queries refused until reselected |

## 6. What stays outside framework trust

- Third-party or project-authored plugins keep working under D-0007 governance (registry, authority floor, gates). They
  can never display or record `profile_statement_digest`. Doctor distinguishes “reference profile (signed)” from
  “project plugin (governed, unsigned)”.
- Remote embedding APIs (D-0006 class 3) cannot be digest-pinned. They are recorded as unsigned project plugins with the
  existing sensitivity restrictions.

## 7. Residual (VR-4, explicit)

A same-user process can modify CAS or environment files while a plugin is running and restore them before the post-use
check. Where fs-verity is enabled, the kernel refuses modified reads, closing this. Where it is not, the window is
limited to query-path invocations: persistent index writes are always bracketed by full host verification. The residual
is recorded in `01` §5 and `18` §11.
