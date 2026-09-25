"""govbridge.authority -- the hard authority invariant's foundations (ARCHITECTURE.md sections 2, 4.1, 5, node B5).

Every unit retrieval can return carries an authority class and a lifecycle status, assigned here from record
metadata and explicit, cited rules -- never from a score. ``resolver.py`` and ``lifecycle.py`` import nothing from
``govbridge.lexical``, ``.semantic``, ``.code``, ``.graph`` or ``.route`` (enforced by tests/authority/test_import_boundary.py).
"""

from govbridge.authority import layer as _layer  # noqa: F401  -- registers the "authority" build-manifest layer
