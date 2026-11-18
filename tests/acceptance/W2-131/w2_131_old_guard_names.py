"""The retired package ``gov.guard`` as the historical blobs of W2-131, W2-133, W2-135 and W2-147 import it.

Those suites load a source file as ``w2/integrate`` held it (``git cat-file blob``) and compare today's code with it.
The blobs name ``gov.guard`` (``from gov.guard import role_paths``, ``from gov.guard import decide``), which was retired
with the guard (EMERGENCY-2 6.1, DAEO-gr7t) and whose names live in ``gov.util`` now. ``old_guard_names()`` serves them
from there for the length of a ``with`` block (the blobs bind the names when they load) and takes them away after:
nothing else in the process can import ``gov.guard``.
"""

from __future__ import annotations

import contextlib
import sys
import types

NAMES = ("gov.guard", "gov.guard.decide", "gov.guard.role_paths")


@contextlib.contextmanager
def old_guard_names():
    from gov.util import patterns, role_paths, tickets

    package = types.ModuleType("gov.guard")
    package.__path__ = []
    decide = types.ModuleType("gov.guard.decide")
    for name in ("_match_pattern", "_has_glob", "ACCEPTANCE", "_is_under_acceptance"):
        setattr(decide, name, getattr(patterns, name))
    decide._load_ticket = tickets._load_ticket
    decide._parse_frontmatter = tickets._parse_frontmatter
    package.decide = decide
    package.role_paths = role_paths
    served = {"gov.guard": package, "gov.guard.decide": decide, "gov.guard.role_paths": role_paths}
    before = {name: sys.modules.get(name) for name in NAMES}
    sys.modules.update(served)
    try:
        yield
    finally:
        for name, module in before.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
