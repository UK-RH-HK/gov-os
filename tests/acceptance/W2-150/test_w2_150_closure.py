"""W2-150 S1: memory's static import closure holds none of the gates (DAEO-ijf5; DEC-1039 (2), DEC-1040 (1)).

The walk (``w2_150_walk``) reads ``src/gov`` as data only. Start set: every module of ``gov.retrieval``,
``gov.retrieve``, ``gov.store`` and ``gov.secrets``. Forbidden: every module of ``gov.close`` and ``gov.guard``, and
``gov.decisions.checker``. A failure prints the import path that reaches each forbidden module.
"""

from __future__ import annotations

import w2_150_walk as walker
from w2_150_walk import GATE_MODULES, GATE_PACKAGES, MEMORY_PACKAGES, Walk, in_package, is_gate


def test_s1_memory_closure_reaches_no_gate():
    walk = Walk()
    starts = walk.in_packages(MEMORY_PACKAGES)
    reached = walk.closure(starts)
    hits = walk.report(reached, is_gate)
    assert not hits, (
        f"memory's import closure ({len(starts)} start modules, {len(reached)} modules reached) reaches the gates "
        f"{GATE_PACKAGES} / {GATE_MODULES}; the import path to each:\n{hits}")


def test_s1_the_start_set_is_every_module_of_the_memory_packages():
    """Guard on the instrument: the start set is not empty and holds the four modules E-2 names."""
    walk = Walk()
    starts = walk.in_packages(MEMORY_PACKAGES)
    files = [p for pkg in MEMORY_PACKAGES for p in (walker.SRC / pkg.replace(".", "/")).rglob("*.py")
             if "__pycache__" not in p.parts]
    assert len(starts) == len(files) >= 20
    for name in ("gov.store.loader", "gov.retrieve.command", "gov.secrets", "gov.retrieval.measure"):
        assert name in starts
    assert all(any(in_package(m, p) for p in MEMORY_PACKAGES) for m in starts)


def _plant(root, files: dict[str, str]):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_s1_the_walk_follows_every_import_statement_form(tmp_path):
    """Guard on the instrument, on a planted tree: function- and method-level imports, relative imports, a
    ``from pkg import submodule``, parent packages' ``__init__``, and no false edge for a name that is not a module."""
    src = tmp_path / "src"
    _plant(src, {
        "gov/__init__.py": "",
        "gov/mem/__init__.py": "",
        "gov/mem/a.py": "def f():\n    from gov.gate import deep\n",
        "gov/mem/b.py": "class C:\n    def m(self):\n        from .. import other\n",
        "gov/mem/c.py": "from . import sib\nfrom .sib import NAME\n",
        "gov/mem/sib.py": "NAME = 1\n",
        "gov/mem/d.py": "if True:\n    import gov.pkg.leaf\n",
        "gov/mem/e.py": "from gov.helpers import thing\n",
        "gov/gate/__init__.py": "",
        "gov/gate/deep.py": "",
        "gov/other.py": "from gov.gate2 import x\n",
        "gov/gate2.py": "",
        "gov/pkg/__init__.py": "from gov.gate3 import y\n",
        "gov/pkg/leaf.py": "",
        "gov/gate3.py": "",
        "gov/helpers.py": "thing = 1\n",
    })
    walk = Walk(src)
    assert walk.closure(["gov.mem.a"]).keys() >= {"gov.gate", "gov.gate.deep"}
    assert "gov.gate2" in walk.closure(["gov.mem.b"])
    assert "gov.mem.sib" in walk.closure(["gov.mem.c"])
    reached = walk.closure(["gov.mem.d"])
    assert {"gov.pkg", "gov.pkg.leaf", "gov.gate3"} <= reached.keys()
    assert walk.path_to(reached, "gov.gate3") == (
        "gov.mem.d -> gov.pkg [src/gov/mem/d.py:2] -> gov.gate3 [src/gov/pkg/__init__.py:1]")
    assert "gov.helpers.thing" not in walk.closure(["gov.mem.e"])
    assert "gov.helpers" in walk.closure(["gov.mem.e"])
