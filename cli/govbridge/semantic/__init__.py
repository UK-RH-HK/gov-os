"""govbridge.semantic -- semantic/vector retrieval on the existing replaceable D-0006 architecture (node B4;
ARCHITECTURE.md section 4.5, SEMANTIC_ROUTE.md).

Importing this package registers the "semantic" freshness-layer builder and the "vector" build-manifest layer
digest with ``govbridge.core`` (the extension points ``govbridge/core/freshness.py`` and
``govbridge/core/manifest.py`` document for exactly this: B2-B5 register from their own package's ``__init__.py``,
without ``govbridge/core`` ever being edited to know their names).

That import must actually happen before it has any effect. ``govbridge.core.freshness``'s own CLI
(``python -m govbridge.core.freshness ...``) does not import sibling layer packages, so it does not know the
"semantic" layer exists until something imports this package first -- there is no generic layer-discovery hook in
core today. This node cannot add one (``govbridge/core/**`` is outside its ``mutation_scope``); it is recorded as
an open issue in ``AGENT_RUNS/BR-AR-0006.report.yaml`` for I1 (which wires the whole package together) or a future
core change to resolve generically. The workaround used for this node's own checkpoint commands is to import this
package explicitly before invoking ``govbridge.core.freshness``'s ``main()`` -- see the checkpoint's recorded
commands for the exact invocation.
"""
from govbridge.semantic import freshness_layer  # noqa: F401  (import side effect: the two register_* calls above)
