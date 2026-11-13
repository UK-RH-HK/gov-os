"""The register's tags, relations and what is in force (W2-55; DEC-791 item 1, DEC-825 items 2 and 4, DEC-866).

Moved whole to ``gov.util.register`` by W2-150 (DEC-1109 (2)), so that memory leaves out the register's superseded
and done entries (``leave_out``) without importing ``gov.decisions``, whose package pulls the decision checker.

This name is that same module object (``gov.decisions.register is gov.util.register``): every name of it is the same
under both names, and a name set on one (a test's stand-in for ``_read``) is set on the other.
"""

from __future__ import annotations

import sys

from gov.util import register as _moved

sys.modules[__name__] = _moved
