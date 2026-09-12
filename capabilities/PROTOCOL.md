# Capability Plugin Protocol v1 (`gov-capability/1`)

Authoritative contract: [spec/interfaces/API-0001.yaml](../spec/interfaces/API-0001.yaml).

The Rust core spawns a plugin command, writes exactly one JSON request to its stdin, closes stdin, and reads exactly
one JSON response from stdout. Plugins may be written in any language. Shipped plugins:

| Plugin | Language | Capability | Purpose |
|---|---|---|---|
| `capabilities/python/govos_capabilities/code_intel_python_ast.py` | Python | `code_intel` (python) | High-fidelity Python symbols/imports/calls/structural chunks via the stdlib AST |
| `capabilities/python/govos_capabilities/embedder_hashed_ngram.py` | Python | `embed` | Reference implementation of the core's built-in baseline embedder (cross-implementation determinism test) |
| `capabilities/shell/echo_embedder.sh` | bash | `embed` | Protocol proof in a non-Python language |

Built-in fallbacks inside the core (no plugin needed): hashed-ngram embedder, generic multi-language symbol extractor,
ecosystem detection. A missing or failing plugin never crashes the core: it degrades to the fallback and records the
degradation in capability memory.
