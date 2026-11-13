"""Role separation from the path map, for what the product hands a caller (DEC-1065 (2), DEC-1052 G-14; W2-13 S5).

Moved whole to ``gov.util.role_paths`` by W2-150 (DEC-1109 (2)), so that memory's search (``gov retrieve``, ``gov
context``'s supplementary block) filters by role without importing the guard.

This name is that same module object (``gov.guard.role_paths is gov.util.role_paths``): every name of it is the same
under both names, and a name set on one (a test's stand-in for ``WORKTREES``, ``changed`` or ``engineer_side``) is
set on the other.
"""

from __future__ import annotations

import sys

from gov.util import role_paths as _moved

sys.modules[__name__] = _moved
