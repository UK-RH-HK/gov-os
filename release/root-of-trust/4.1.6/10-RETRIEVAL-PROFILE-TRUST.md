# Output 10 — Reference retrieval profile trust integration

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 6 amendment: none to the profile model; profile install runs only on an admitted binary on a protected
> installation for C3 (`31` GB-4′).
> Revision 5 amendment: profile install is C3 and needs a currency proof naming the selected Trust State (`24` §4.4); it runs
> only on an admitted binary (`31` GB-1). The profile model is otherwise unchanged.
> Revision 4 changes profile trust in two ways:
> - a profile install is C3, so it needs a currency proof (`24` §4.4);
> - plugin processes run under write confinement (`24` §3.5).
>
> Kept from revision 3: host-side verification, the content-addressed store, and the `governance/views/` registry path
> registered as a pinned value in TPS v1.

## 1. Constraints preserved

- **Framework §14.3 and D-0006.** No embedding or reranking model is a constitutional dependency. The kernel default stays
  `hashed-ngram`.
- **D-0005.** Embed and rerank plugins fail closed.
- **D-0007 restated in D-0008.** Plugin **authorisation** comes from the effective policy (floor-joined authority and
  permission classes) and the OS-written registry. A profile signature is provenance and integrity, never authorisation.

The model a profile uses is profile content, replaceable by publishing another profile statement:
**signed pinned identity → host-verified integrity → governed install → local use**.

## 2. Current gap (4.1.5)

The sentence-transformers plugin loads a model by hub name, with no revision, file digests or package pins; the registry
pins descriptor and command files only.

## 3. Profile statement

payloadType `retrieval-profile.v1+json`, purpose `retrieval-profile`. Schema: `schemas/profile-statement.schema.json`.
The fields are unchanged from revision 2:
- `profile_id`, `profile_version`, `capability`, `compatibility`;
- `plugin` files;
- `runtime` lock and packages;
- `model` (immutable revision, files, digests);
- `evidence`;
- `offline`.

## 4. Installation (`gov profile install <bundle>`, may ship in a later MINOR release)

1. Read the bundle through the secure reader; stream large model files with incremental digests.
2. Authenticate under `retrieval-profile`; check compatibility with the current snapshot.
3. Verify every plugin, runtime-lock, package and model digest.
4. Materialise into the content-addressed store `.governance-runtime/profiles/cas/<sha256>`: exclusive creation,
   read-only, fs-verity where available. Build the environment only from hash-verified archives.
5. **Freshness and authorisation.** Profile install is C3: it requires `ANCHORED` or `WITNESSED` freshness, a currency proof (`24` §4.3–§4.4), and the install authority from the effective policy.
   the install authority from the effective policy.
6. Register through `gov plugins register`. The registry entry binds `profile_statement_digest` and the CAS digests. The
   registry is written to the kernel-registered `TOOL_POLICY.plugins.registry_path`; for 4.1.6 that is
   `governance/views/plugin-registry.json`, a pinned value registered in TPS v1.
7. Selection stays benchmark → research record → gated decision → `gov memory select`. The pin lives in
   `governance/overlay/PROJECT_POLICY.yaml`.
8. The profile statement envelope is written to `governance/trust/profiles/<profile_id>.dsse.json` through the install
   transaction (operation `profile_install`). The PTR union rule applies.

## 5. Use-time verification — host-side

| When | Host check | Failure |
|---|---|---|
| Registration, `rebuild-memory`, `memory verify`, `plugins health` | statement verifies; registry binds the same digest; host recomputes full digests of implementation, runtime lock, environment and model files | `PROFILE_STATEMENT_INVALID`, `PROFILE_DIGEST_MISMATCH`, `MODEL_DIGEST_MISMATCH`; embedding fails closed |
| Plugin start | full digests of implementation and lock. Model: fs-verity measurement, or a full digest on metadata change, otherwise random ranges | invocation refused |
| After any invocation feeding a persistent write | full re-digest before committing index writes; the index manifest records the profile digest, CI and effective-policy digest (VU-8) | writes discarded |
| Kernel update | profile compatibility re-checked | `PROFILE_INCOMPATIBLE` |

## 6. What stays outside framework trust

- **Project-authored plugins** remain governed by D-0007-style rules, never profile-bound.
- **Remote embedding APIs** are unsigned project plugins.
- **Plugin subprocesses** run under write confinement (`24` §3.5 (3)) and are otherwise A3-equivalent (`18` VR-3):
  - they cannot write pins, the VTS or trust paths, and cannot authorise trust decisions (`27`);
  - their PPS writes are detected at the next unit of work;
  - their overlay weakenings are reported (`26` §6).

## 7. Residual (VR-4)

A same-user process can alter CAS or environment files during a plugin run and restore them before the post-use check.
fs-verity closes this where it is enabled. Elsewhere, persistent index writes are always bracketed by full host
verification.
