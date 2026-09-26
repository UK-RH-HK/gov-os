"""govbridge.code -- the code/symbol/reference route (ARCHITECTURE.md section 4.6, DAG node B3): a tree-sitter Rust
adapter (BUILD) plus the existing Python AST plugin (REUSE, run from its blob, unmodified), symbol/call/literal
tables, labelled resolution and lazy per-commit symbol history.

Importing this package registers the code layer with ``govbridge.core`` at IMPORT TIME -- the same extension point
``govbridge.core.manifest``/``govbridge.core.freshness`` document and test for every layer node
(``register_layer``/``register_layer_builder``, "called at import time of the layer's own package", per both
modules' own docstrings and ``tests/core/test_manifest.py::test_a_new_layer_can_register_without_editing_core``).
Nothing in ``govbridge.core`` is ever edited to learn this package's name.

Two registrations, both implemented in ``govbridge.code.build`` (its module docstring has the full design,
including BR-AR-0014/BR-HO-0014's fix for the code layer's original lazy, query-order-dependent build manifest):

* ``register_layer_builder("code", build.code_layer_builder)`` -- an EAGER build, during ``index rebuild``/
  ``update``, of every ``.rs`` blob reachable at each canonical-view ref whose role is not ``history``.
* ``register_layer("code", build.code_layer_digest)`` -- the build-manifest digest over the sorted
  ``code_symbol``/``code_call_site``/``code_literal`` rows for exactly that eager set, query-invariant against
  anything a lazy query (``stats``/``callers``/``reads-key``/``history diff``, including on a ``history`` commit)
  parses on top.

The route's QUERY surface (``govbridge.code.symbols``: ``stats``/``callers``/``reads-key``, and
``govbridge.code.history``) is unchanged by either registration -- both keep parsing and caching a commit's blobs
lazily, the first time any caller (a query, or now also the eager builder) asks for that commit
(``govbridge.code.symbols.ensure_indexed``, its own module docstring).
"""
from govbridge.code import build as build  # noqa: F401  (import triggers the two register_* calls below)
from govbridge.code import lineage_layer as lineage_layer  # noqa: F401 -- BR-AR-0019 (R1-RL reopening): registers
                                                            # the "lineage" layer (see its own module docstring for
                                                            # why it lives here rather than govbridge/graph/)
from govbridge.core.freshness import register_layer_builder
from govbridge.core.manifest import register_layer

register_layer_builder("code", build.code_layer_builder)
register_layer("code", build.code_layer_digest)
register_layer_builder("lineage", lineage_layer.lineage_layer_builder)
register_layer("lineage", lineage_layer.lineage_layer_digest)
