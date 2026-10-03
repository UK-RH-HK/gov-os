"""The minimal path-map schema (DEC-185), until W1-08 supplies the real one and replaces this file.

The top level of ``governance/project/path-map.yaml`` is a map. Each entry below
is one top-level key: whether it is required, its type, and the type of each of
its values. Keys not listed here are left alone.
"""

from __future__ import annotations

PATH_MAP_SCHEMA = {
    "namespaces": {"required": True, "type": dict, "values": dict},
}
