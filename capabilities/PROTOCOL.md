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

Plugins are governed executables (TOOL_POLICY.plugins). The descriptor must validate against the kernel
`plugin-descriptor` schema (identity + version pin required), the program must resolve, the acting role must be at or
above `plugins.min_authority` (L2) and in the registry's `approved_roles`, and every `required_permission_classes`
entry must be held by the role. `gov capabilities plugins` lists usable / denied / rejected descriptors with reasons.

**Registration is what lets a plugin run** (Phase-2 repair iteration 1, WS-7; Contract v3 F4:426-431, ARCH-0003 §9):

- The host runs a plugin as an ordinary child process of the invoking account; nothing confines it, so a descriptor's
  `permissions` and `required_permission_classes` are declarations the OS cannot enforce. Whether a plugin needs
  approval therefore never depends on them: **every executable plugin** (a script, an interpreter running a module or
  inline code, a binary) runs only with a registration written by `gov plugins register` and approved by a Human
  Decision Gate raised for exactly that plugin identity, version, implementation and permission set, answered A by the
  product owner through the human channel. The approval is re-verified at every execution: revoking the gate, changing
  a bound byte, editing the descriptor or the registry entry stops the plugin.
- The only plugins that run hand-declared are this `gov` binary's own capability server
  (`["<path to gov>", "capabilities", "serve-embed", ("--id", "<id>")?, ("--reverse")?]`), whose effects are the
  release's own.
- The registration binds every byte the command executes, as the OS derives it: the program (resolved on `PATH`), every
  script argument, the whole top-level package of a `python3 -m <module>` command (including `__pycache__`), inline
  code (inside the descriptor), and any extra files or directories listed under `implementation:` (helpers the entry
  point loads that the command does not name). A symlink inside a bound tree binds where it points and the bytes it
  resolves to; a symlinked directory is followed. A command whose implementation cannot be located is refused.
- An `embed`/`rerank` plugin declares the model and inference runtime it loads from outside its own directory:
  `model: {id?, revision?, artefacts: [paths]}` and `runtime: {id?, artefacts: [paths]}` (project-relative or
  absolute; `{project_root}` / `{plugin_dir}` substituted). Every declared path must exist; for an executable plugin
  their bytes are bound by the registration (roles `model` / `runtime`, shown in the registration gate), so a changed
  model or runtime byte stops the plugin until a new approval, and the retrieval profile identifies the model and
  runtime from the same files.
- Unchanged files are not re-hashed at every authorisation within one `gov` process: a digest is reused only while
  the file's device, inode, size, modification time, status-change time, mode and owner are exactly what they were
  when it was hashed, and only when the file had not changed for a few seconds before it was read, no process held
  it open for writing (Linux read-lease probe) and it lives on a kernel-maintained local filesystem. A bound file's
  digest never leaves the process that computed it; only the digest labelling the running `gov` executable (used
  where a plugin's program is that very file) is kept across processes, in the machine's protected state.
- The plugin runs without the caller's loader variables (`PYTHONPATH`, `NODE_OPTIONS`, `LD_PRELOAD`, `BASH_ENV`, ...)
  and with `PYTHONDONTWRITEBYTECODE=1`; a module plugin must be importable from its working directory (`cwd:`) or the
  interpreter's own search path.
- The registry (`governance/registry/plugin-registry.json`, tracked OS-written state; not among the regenerable views of
  `governance/generated/`, so deleting those never drops a registration) is written only by `gov plugins register` /
  `unregister`. Its entries are sealed by the registering operation on this machine; a hand-written, edited or foreign
  entry is never honoured, and a fresh clone re-registers (a new gate whose package states whether the implementation
  differs from the tracked registration). A registry an earlier release kept at
  `governance/generated/plugin-registry.json` is read — entry by entry, under the same seal rule — until the next
  registry write moves it there unchanged; once moved, a file at the old location is ignored and reported.

To register: `gov plugins register --descriptor <file>` (as an install-authority role) returns `human_gate`; render it
with `gov gate present <gate>`; the product owner answers it (owner-signed answer, `gov decide <gate> --option A
--answer-file <doc>`); run the same `gov plugins register` again. A pending gate is returned instead of a new one; a
declined gate ends the request. `gov plugins health --ping` never executes a plugin the acting role may not run, and
records health failures in failure memory.
