"""W2-150's static import walk over ``src/gov`` (DAEO-ijf5, S1 and S2).

The walk reads ``src/gov`` only as data: it parses every ``.py`` file with ``ast`` and never imports any of them.
It follows every ``import`` and ``from ... import`` statement in a module, at module level and inside functions,
methods, classes and conditional blocks (``ast.walk`` over the whole tree). These are the KPI's "import statements";
a call such as ``importlib.import_module(...)`` is not one and is not followed (README N-2). Importing a module also
runs its parent packages' ``__init__``, so each module reached brings its parents with it
(``gov.decisions.register`` brings ``gov.decisions``).

Resolution:
- ``import a.b.c`` reaches ``a.b.c`` (and its parents);
- ``from a.b import y`` reaches ``a.b``, and ``a.b.y`` when ``y`` is a submodule under the source root;
- relative forms (``from . import y``, ``from ..x import y``) are resolved against the importing module's package;
- ``from a.b import *`` reaches ``a.b``.
Only modules under the source root are nodes; the standard library and third-party packages are left out.
"""

from __future__ import annotations

import ast
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"

# The memory modules (S1's start set) and the gates (what memory's closure must not reach).
MEMORY_PACKAGES = ("gov.retrieval", "gov.retrieve", "gov.store", "gov.secrets")
GATE_PACKAGES = ("gov.close", "gov.guard")
GATE_MODULES = ("gov.decisions.checker",)


def in_package(name: str, package: str) -> bool:
    return name == package or name.startswith(package + ".")


def is_gate(name: str) -> bool:
    return any(in_package(name, p) for p in GATE_PACKAGES) or name in GATE_MODULES


class Walk:
    """The import graph of the packages under ``src`` (a folder holding top-level packages)."""

    def __init__(self, src: Path = SRC, top: str = "gov"):
        self.src = Path(src)
        self.modules: dict[str, Path] = {}
        for path in sorted((self.src / top).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            parts = list(path.relative_to(self.src).with_suffix("").parts)
            if parts[-1] == "__init__":
                parts.pop()
            self.modules[".".join(parts)] = path
        self._direct: dict[str, tuple[tuple[str, int], ...]] = {}

    def is_package(self, name: str) -> bool:
        return self.modules[name].name == "__init__.py"

    def in_packages(self, packages) -> list[str]:
        return sorted(m for m in self.modules if any(in_package(m, p) for p in packages))

    def _with_parents(self, name: str) -> list[str]:
        """``name`` and each parent package of it that is a module here, outermost first."""
        parts = name.split(".")
        return [c for c in (".".join(parts[:i]) for i in range(1, len(parts) + 1)) if c in self.modules]

    def _resolve_base(self, importer: str, level: int, module: str | None) -> str | None:
        """The absolute dotted name a ``from`` statement's module part names."""
        if level == 0:
            return module
        package = importer if self.is_package(importer) else importer.rpartition(".")[0]
        parts = package.split(".") if package else []
        if level - 1 > len(parts):
            return None
        parts = parts[: len(parts) - (level - 1)]
        base = ".".join(parts)
        if module:
            base = f"{base}.{module}" if base else module
        return base or None

    def direct_imports(self, name: str) -> tuple[tuple[str, int], ...]:
        """The modules here that ``name``'s own statements import, each with its statement's line.

        A module reached brings its parent packages; the importer's own name is left out.
        """
        if name in self._direct:
            return self._direct[name]
        path = self.modules[name]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        targets: dict[str, int] = {}

        def add(target: str | None, line: int) -> None:
            for each in self._with_parents(target) if target else ():
                if each != name and (each not in targets or line < targets[each]):
                    targets[each] = line

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    add(alias.name, node.lineno)
            elif isinstance(node, ast.ImportFrom):
                base = self._resolve_base(name, node.level, node.module)
                if base is None:
                    continue
                add(base, node.lineno)
                for alias in node.names:
                    if alias.name != "*" and f"{base}.{alias.name}" in self.modules:
                        add(f"{base}.{alias.name}", node.lineno)
        self._direct[name] = tuple(sorted(targets.items()))
        return self._direct[name]

    def closure(self, starts) -> dict[str, tuple[str, int] | None]:
        """Breadth-first walk from ``starts`` (each with its parents): ``{module: (importer, line) or None}``.

        The value is the edge the walk first reached the module by, so a shortest path can be read back.
        """
        reached: dict[str, tuple[str, int] | None] = {}
        queue: deque[str] = deque()
        for start in starts:
            for each in self._with_parents(start):
                if each not in reached:
                    reached[each] = None
                    queue.append(each)
        while queue:
            current = queue.popleft()
            for target, line in self.direct_imports(current):
                if target not in reached:
                    reached[target] = (current, line)
                    queue.append(target)
        return reached

    def path_to(self, reached: dict, target: str) -> str:
        """``a -> b [a.py:12] -> c [b.py:40]``: the import path the walk reached ``target`` by."""
        steps = []
        current = target
        while (edge := reached[current]) is not None:
            importer, line = edge
            rel = self.modules[importer].relative_to(self.src.parent).as_posix()
            steps.append(f"{current} [{rel}:{line}]")
            current = importer
        steps.append(current)
        return " -> ".join(reversed(steps))

    def report(self, reached: dict, bad) -> str:
        """One line per forbidden module reached, with its import path; empty when none is."""
        return "\n".join(f"  {m}: {self.path_to(reached, m)}" for m in sorted(m for m in reached if bad(m)))
