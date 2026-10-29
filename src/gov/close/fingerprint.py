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

Everything is read from git objects of the commit, through ``gov.close.repo.git``; nothing from the working tree.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from gov.cli.errors import GovError
from gov.close import select as _select
from gov.close.repo import git as _git

PATH_MAP_REL = "governance/project/path-map.yaml"
SCHEMA_RELS = tuple(f"{folder}/{_select.SCHEMA_NAME}" for folder in _select.SCHEMA_DIRS)
ALWAYS_CODE = frozenset((PATH_MAP_REL, _select.MAP_REL, *SCHEMA_RELS))
PREFIX = "sha256:"


def _tree(root: Path, commit: str) -> dict[str, str]:
    """``path -> line`` of every entry of the commit, as ``git ls-tree -r -z --full-tree`` gives it."""
    entries = {}
    for line in _git(root, "-c", "core.quotePath=false", "ls-tree", "-r", "-z", "--full-tree",
                     commit + "^{commit}").split("\0"):
        if line:
            entries[line.partition("\t")[2]] = line
    return entries


def _blob(root: Path, line: str | None) -> str | None:
    """The text of the blob the entry names; None where the entry is not a blob or names none."""
    if line is None:
        return None
    mode, kind, sha = line.partition("\t")[0].split()
    if kind != "blob" or mode == "120000":
        return None
    return _git(root, "cat-file", "blob", sha)


def _schema(root: Path, tree: dict[str, str]) -> dict | None:
    """The schema that judges the commit's test map: the commit's own kernel's, else the running package's."""
    for rel in SCHEMA_RELS:
        try:
            return json.loads(_blob(root, tree.get(rel)) or "")
        except ValueError:
            continue
    try:
        return json.loads((Path(_select.__file__).resolve().parents[3] / SCHEMA_RELS[0]).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _record_only(root: Path, tree: dict[str, str]) -> list[str] | None:
    """The commit's ``record_only`` patterns; None where its test map cannot be read as a valid map."""
    import jsonschema
    import yaml

    try:
        data = yaml.safe_load(_blob(root, tree.get(_select.MAP_REL)) or "")
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):  # no map, an empty one, or one that is not a mapping
        return None
    schema = _schema(root, tree)
    if schema is None:  # nothing to judge it by is not a valid map
        return None
    try:
        jsonschema.Draft202012Validator(schema).validate(data)
    except Exception:  # noqa: BLE001 - an invalid map, or a schema that cannot judge it: cannot be computed
        return None
    return list(data.get("record_only") or [])


def _digest(lines) -> str:
    return PREFIX + hashlib.sha256("".join(line + "\n" for line in sorted(lines)).encode("utf-8")).hexdigest()


def of_commit(root: Path, commit: str = "HEAD") -> dict | None:
    """``{"code": ..., "records": ...}``, the two fingerprints of ``commit``; None where they cannot be computed."""
    try:
        tree = _tree(root, commit)
        patterns = _record_only(root, tree)
    except (GovError, UnicodeDecodeError):  # a commit git cannot read, or a blob that is not text
        return None
    if patterns is None:
        return None
    records = {path for path in tree if path not in ALWAYS_CODE and any(_select.match(path, p) for p in patterns)}
    return {"code": _digest(line for path, line in tree.items() if path not in records),
            "records": _digest(tree[path] for path in records)}
