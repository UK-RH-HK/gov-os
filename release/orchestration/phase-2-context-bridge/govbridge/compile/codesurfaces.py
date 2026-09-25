#!/usr/bin/env python3
"""Config-driven "is this occurrence a code or test surface" check (ARCHITECTURE.md section 7.2's G row;
BR-HO-0015 defect 3: "Placement looks at (class, lifecycle, delivery) only... A retrieved hit whose canonical
occurrence is product code or a test lands in H, because section 5.1 classes such files as EVIDENCE"). A
RETRIEVED/DERIVED item whose occurrence path matches this small config list goes to G instead of H --
``govbridge.compile.packet`` applies it ONLY on the section == "H" fallback branch, so A/D.1/D.2/D.3/E/F placements
are never touched by this check (BR-HO-0015: "D.1/D.2/D.3/E/F placements are unchanged").

Generic (OC-BR-02): the rule list is a small, versioned config key (``config/budgets.yaml``'s own
``code_test_surfaces``), never a hand-picked file or path.
"""
from __future__ import annotations

from typing import Optional

from govbridge.core import pathrules
from govbridge.core.yamlutil import load_yaml_file

EMPTY_RULES = {"source_extensions": (), "source_dirs": (), "test_path_globs": ()}


def load_rules(path: Optional[str] = None) -> dict:
    from govbridge.compile.budgets import _default_budgets_path
    doc = load_yaml_file(path or _default_budgets_path())
    raw = doc.get("code_test_surfaces") or {}
    return {
        "source_extensions": tuple(raw.get("source_extensions") or ()),
        "source_dirs": tuple(raw.get("source_dirs") or ()),
        "test_path_globs": tuple(raw.get("test_path_globs") or ()),
    }


def is_code_or_test_surface(path: Optional[str], rules: dict) -> bool:
    if not path:
        return False
    if pathrules.any_glob_match(path, rules.get("test_path_globs", ())):
        return True
    if pathrules.top_level_dir_match(path, rules.get("source_dirs", ())) is not None:
        return True
    return path.endswith(tuple(rules.get("source_extensions", ())))
