"""govbridge.lexical -- the lexical route: one SQLite FTS5 table over B1's chunks (ARCHITECTURE.md section 4.3,
DAG node B2). Reads the store B1 already built (``blob``, ``occurrence``, ``chunk``) and never re-implements Git
access, corpus classification or chunk identity (govbridge.core owns all of that).

This package registers itself with govbridge.core at IMPORT TIME -- exactly the extension point
``govbridge.core.manifest`` and ``govbridge.core.freshness`` document and test for every later layer
(``register_layer``/``register_layer_builder``, called "at import time of the layer's own package", per both
modules' own docstrings and ``tests/core/test_manifest.py::test_a_new_layer_can_register_without_editing_core``).
Nothing in ``govbridge.core`` is ever edited to learn this package's name.

Nothing here special-cases Review 8, F1-F6, Phase 2 or any particular file (OC-BR-02): the FTS5 table indexes
whatever chunk rows core already decided belong in the corpus; the tokenizer and BM25 ranking are generic
full-text-search mechanics that apply to any repository, any corpus, any query.
"""
from govbridge.lexical import fts as fts  # noqa: F401  (import triggers the registration at the bottom of fts.py)

__all__ = ["fts", "query"]
