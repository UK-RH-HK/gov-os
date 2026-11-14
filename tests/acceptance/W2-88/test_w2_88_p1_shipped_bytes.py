"""Run 8, S24 (DEC-1183, the owner's package 1 (a); run 8 interface items 3 and 5): the three things A9 needs ship inside the wheel.

Copies, byte for byte, under ``src/gov/_shipped/``, each at its path in the Gov OS repository: ``governance/project/retrieval.yaml``, every file
of ``governance/project/indep-walls/`` and of ``governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/``. Each copy equals its source
(the file at its path from the root of the checkout this test runs in): a drifted byte, a file missing from the copy, or an extra file in the
copy fails, naming the file. A string check of the tree (no gov run): ``__pycache__`` folders and ``*.pyc`` files are not files of a copy; an
``__init__.py`` directly under ``_shipped/`` or ``_shipped/governance/...`` above the copied folders is let through (packaging may want one),
any other file under ``_shipped/`` that is not a copy is an extra.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_88_support as W

SHIPPED = W.SRC / "gov" / "_shipped"
ITEMS = {
    "the-pool": "governance/project/retrieval.yaml",
    "the-walls-template": "governance/project/indep-walls",
    "the-audit-briefs": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs",
}


def files_of(path: Path) -> dict:
    """``{relative path: bytes}`` of a file (key ``""``) or of every file under a folder, caches left out."""
    if path.is_file():
        return {"": path.read_bytes()}
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in sorted(path.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


@pytest.mark.parametrize("rel", list(ITEMS.values()), ids=list(ITEMS))
def test_s24_each_shipped_copy_equals_its_source_byte_for_byte(rel):
    """success-S24 (run 8 items 3 and 5): ``src/gov/_shipped/<rel>`` exists and equals ``<checkout>/<rel>``: for a folder, every file of the source
    has its copy at the same relative path with the same bytes, and the copy holds no file the source does not. A missing copy, a missing file,
    an extra file or a drifted byte fails, naming it."""
    source, copy = W.REPO_ROOT / rel, SHIPPED / rel
    assert source.exists(), f"the source {rel} is not in this checkout ({W.REPO_ROOT})"
    assert SHIPPED.is_dir(), f"src/gov/_shipped/ does not exist: {rel} is not shipped inside the gov package"
    assert copy.exists(), f"src/gov/_shipped/{rel} does not exist: {rel} is not shipped inside the gov package"
    assert copy.is_file() == source.is_file(), f"src/gov/_shipped/{rel} is a {'file' if copy.is_file() else 'folder'}, its source is not"
    want, have = files_of(source), files_of(copy)
    assert want, f"the plant: the source {rel} holds no file"
    missing = sorted(set(want) - set(have))
    extra = sorted(set(have) - set(want))
    drifted = sorted(name for name in set(want) & set(have) if want[name] != have[name])
    name = lambda part: f"{rel}/{part}" if part else rel  # noqa: E731
    assert not missing, f"files of {rel} with no copy under src/gov/_shipped/: {[name(p) for p in missing]}"
    assert not extra, f"files under src/gov/_shipped/{rel} that the source does not hold: {[name(p) for p in extra]}"
    assert not drifted, f"copies under src/gov/_shipped/ whose bytes differ from the source: {[name(p) for p in drifted]}"


def test_s24_the_shipped_folder_holds_only_the_copies():
    """success-S24 (run 8 item 5, an extra file in the copy): every file under ``src/gov/_shipped/`` is one of the three items' copies (or an
    ``__init__.py`` above them, or a cache): a file shipped that is no copy of a source fails, naming it."""
    assert SHIPPED.is_dir(), "src/gov/_shipped/ does not exist: the pool, the walls template and the audit briefs are not shipped inside the gov package"
    copies = set()
    for rel in ITEMS.values():
        source = W.REPO_ROOT / rel
        copies |= {rel} if source.is_file() else {f"{rel}/{part}" for part in files_of(source)}
    extra = []
    for path in sorted(SHIPPED.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel = path.relative_to(SHIPPED).as_posix()
        inside = any(rel.startswith(item + "/") for item in ITEMS.values())
        if rel in copies or (path.name == "__init__.py" and not inside):
            continue
        extra.append(rel)
    assert not extra, f"files under src/gov/_shipped/ that are no copy of a shipped source: {extra}"
