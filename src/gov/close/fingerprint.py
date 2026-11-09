"""The two fingerprints of a commit (W2-68; DEC-883 item 3, DEC-889 items 2 and 4, DEC-880, DEC-899).

- The **code fingerprint** is ``sha256:`` and the sha256 of the sorted lines of ``git ls-tree -r -z --full-tree``
  (``<mode> <type> <object>``, a tab, the path) of the commit, every path the commit's ``record_only`` list matches
  left out. The **records fingerprint** is the same over exactly the entries left out.
- The ``record_only`` list is read from the commit's own test map (never written), judged as ``select.load_map``
  judges the working tree's: YAML that parses to a mapping, valid by the test-map schema (Draft 2020-12). The schema
  is the commit's own kernel's, else the running package's (the design note, section 11, point B). Patterns are
  read with the ``allowed_paths`` grammar (``select.match``).
- The path map, the test map and the test-map schema are always code (DEC-880): a change to any of them, the
  ``record_only`` list included, changes the code fingerprint.
- Where the fingerprints cannot be computed (no test map, one that does not parse or fails its schema, no schema
  to judge it, a commit git cannot read) the answer is None, never an empty list: every caller reads it as "run
  fresh".

Everything is read from git objects of the commit, as ``gov.close.repo.git`` reads them; nothing from the working
tree. Since W2-150 (DEC-1109 (2)) the computation lives in ``gov.store.loader``, so that the record store computes
it without importing the close; every name stays a name of this module.
"""

from __future__ import annotations

from gov.store.loader import ALWAYS_CODE, PATH_MAP_REL, PREFIX, SCHEMA_RELS, of_commit  # noqa: F401
