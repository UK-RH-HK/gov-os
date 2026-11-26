"""What a rule decides alone: the class of an item (hidden sets, secrets, evaluation sets, tool-fixed paths, generated
roots) and the one place the standard gives a class, a path and an import name (L1, L2)."""

from __future__ import annotations

import re

from gov.layout.standard import Standard

CHOICE = "<folder>"  # one folder of the agent's choice, below the research and the record place
_CHOSEN = ("docs/research", "docs/records")  # the destinations that take such a folder
_MANIFESTS = ("pyproject.toml", "setup.py", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle")


def under(path: str, top: str) -> bool:
    """Whether ``path`` is ``top`` or lies below it."""
    return path == top or path.startswith(top + "/")


def package_roots(tracked: list[str], imports: list[str]) -> set[str]:
    """The native package roots the manifests name: a subfolder's manifest, its folder; a root manifest, ``src`` when
    there is one. A manifest inside a path of ``imports`` is the import's own and pins nothing."""
    roots = set()
    for path in tracked:
        folder, _, name = path.rpartition("/")
        if name not in _MANIFESTS or any(under(path, top) for top in imports):
            continue
        if folder:
            roots.add(folder)
        elif any(each.startswith("src/") for each in tracked):
            roots.add("src")
    return roots


def destination(std: Standard, name: str, path: str, stale_class: str | None = None,
                import_name: str | None = None, root: str | None = None) -> str:
    """Where the standard puts ``path`` classed ``name``, no pin considered; ``root`` is the import's root."""
    template = std.classes[name]["destination"] if name in std.classes else "{path}"
    last = path.rsplit("/", 1)[-1]
    if template == "{path}":
        return path
    if std.stale(name):
        if under(path, f"archive/{stale_class}"):
            return path
        rest = path.removeprefix("archive/")
        return template.replace("{stale_class}", str(stale_class)).replace("{path}", rest)
    if std.whole(name):
        top = template.replace("{import}", str(import_name))
        if under(path, top) or path == root:
            return path if under(path, top) else top
        return f"{top}/{path[len(root) + 1:] if root else path}"
    if under(path, template):  # already inside its class's place
        return path
    return f"{template}/{CHOICE}/{last}" if template in _CHOSEN else f"{template}/{last}"


def fits(expected: str, actual: str) -> bool:
    """Whether ``actual`` is the destination ``expected``."""
    if CHOICE not in expected:
        return expected == actual
    return re.fullmatch("[^/]+".join(map(re.escape, expected.split(CHOICE))), actual) is not None
