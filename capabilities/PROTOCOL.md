# Capability Plugin Protocol v1 (`gov-capability/1`)

Authoritative contract: [spec/interfaces/API-0001.yaml](../spec/interfaces/API-0001.yaml).

The Rust core spawns a plugin command, writes exactly one JSON request to its stdin, closes stdin, and reads exactly
one JSON response from stdout. Plugins may be written in any language. Shipped plugins:

| Plugin | Language | Capability | Purpose |
|---|---|---|---|
| `capabilities/python/govos_capabilities/code_intel_python_ast.py` | Python | `code_intel` (python) | High-fidelity Python symbols/imports/calls/structural chunks via the stdlib AST |
| `capabilities/python/govos_capabilities/embedder_hashed_ngram.py` | Python | `embed` | Reference implementation of the core's built-in baseline embedder (cross-implementation determinism test) |
| `capabilities/shell/echo_embedder.sh` | bash | `embed` | Protocol proof in a non-Python language |

Built-in baselines inside the core (no plugin needed): hashed-ngram embedder, generic multi-language symbol extractor,
ecosystem detection. Failure semantics are capability-specific (API-0001 v1.1, D-0005): a pinned **embed/rerank**
plugin that is missing, invalid, unauthorised, unhealthy, mis-pinned or failing is a typed error and the core never
substitutes the built-in embedder for it (fail closed); a failing **code_intel** plugin degrades to the built-in
extractor for that file and the degradation is recorded in capability memory; absent ecosystem tooling is a capability
gap. Never a crash.

Plugins are governed executables (TOOL_POLICY.plugins): the descriptor must validate against the kernel
`plugin-descriptor` schema (identity + version pin required), the executable must resolve, the acting role must be at
or above `plugins.min_authority` (L2) for hand-declared descriptors or in `approved_roles` for registered ones, every
`required_permission_classes` entry must be held by the role, elevated permissions need a presented and answered
registration gate (`gov plugins register`), and the implementation's content hash is pinned per version
(`PLUGIN_PIN_MISMATCH` on drift). `gov capabilities plugins` lists usable / denied / rejected descriptors with reasons.
