"""KPI S1: the old register archived whole, named by the path map, out of both indexes (EMERGENCY-2 11.3, DEC-1214 G4).

Repository-state cases: they read this tree's own archive, path map and kernel schema, and the base's register by
``git show``. Nothing is written.
"""

from __future__ import annotations

import json
import re

import yaml

import w2_203_support as s

MODEL_NAMESPACE = "evaluation-sources"  # out of both indexes already: the archive's namespace has its other fields
SAME_AS_MODEL = ("memory_class", "sensitivity", "permitted_roles", "export_policy")


def _archive() -> str:
    path = s.REPO / s.ARCHIVE_REL
    assert path.is_file(), f"{s.ARCHIVE_REL} is not a file of this tree: the old register is not archived"
    return path.read_text(encoding="utf-8")


def _path_map() -> dict:
    return yaml.safe_load((s.REPO / s.PATH_MAP_REL).read_text(encoding="utf-8"))


def test_s1_the_archive_opens_with_a_line_saying_archived_and_read_only():
    first = _archive().split("\n", 1)[0]
    low = first.lower()
    assert "archived" in low and ("read-only" in low or "read only" in low), \
        f"the archive's first line does not say archived and read-only: {first!r}"
    for what, pattern in (("EMERGENCY-2 section 11.3", r"EMERGENCY-2.*11\.3"), ("DEC-1214 G4", r"DEC-1214.*G4"),
                          ("audit 8", r"audit 8|08-register")):
        assert re.search(pattern, first, re.IGNORECASE), f"the archive's first line does not name {what}: {first!r}"


def test_s1_every_entry_of_the_base_register_is_in_the_archive_text_for_text():
    old = s.entries(s.base_text(s.REGISTER_REL))
    assert len(old) > 1200, f"premise: the base register holds {len(old)} entries"
    new = s.entries(_archive())
    text_of = dict(new)
    missing = [record_id for record_id, _ in old if record_id not in text_of]
    assert not missing, f"{len(missing)} entries of the base register are not in the archive: {missing[:10]}"
    differing = [record_id for record_id, text in old if text_of[record_id] != text]
    assert not differing, f"{len(differing)} entries differ from the base register's: {differing[:10]}"
    order = [record_id for record_id, _ in new if record_id in dict(old)]
    assert order == [record_id for record_id, _ in old], "the archive holds the base's entries in another order"


def test_s1_the_rest_of_the_archive_is_the_base_register_whole():
    """Under its first line the archive is the base's file: no line of it is lost or reordered."""
    rest = iter(_archive().split("\n")[1:])
    lost = [number for number, line in enumerate(s.base_text(s.REGISTER_REL).split("\n"), 1)
            if not any(line == other for other in rest)]
    assert not lost, f"line {lost[0]} of the base register (and what follows it) is not in the archive in its place"


def test_s1_the_path_map_names_the_archive_beside_the_register():
    path_map = _path_map()
    assert path_map.get(s.ARCHIVE_KEY) == s.ARCHIVE_REL, \
        f"the path map's {s.ARCHIVE_KEY} is {path_map.get(s.ARCHIVE_KEY)!r}, not {s.ARCHIVE_REL}"
    assert path_map.get("decision_register") == s.REGISTER_REL


def test_s1_the_archive_namespace_is_out_of_both_indexes():
    from gov.retrieval import lexical

    namespaces = _path_map()["namespaces"]
    assert "archive" in namespaces, f"the path map has no namespace archive: {sorted(namespaces)}"
    archive, model = namespaces["archive"], namespaces[MODEL_NAMESPACE]
    assert archive.get("paths") == ["docs/archive/**"]
    assert archive.get("embedding_policy") == "not embedded" and archive.get("lexical_policy") == "not indexed"
    assert set(archive) == set(model), f"the namespace's fields are not {MODEL_NAMESPACE}'s: {sorted(archive)}"
    for name in SAME_AS_MODEL:
        assert archive[name] == model[name], f"archive.{name} is {archive[name]!r}, {MODEL_NAMESPACE} has {model[name]!r}"
    assert lexical.kept_out(s.REPO, [s.ARCHIVE_REL, s.REGISTER_REL]) == {s.ARCHIVE_REL: "archive"}, \
        "the keyword index does not keep the archive (and only the archive) out"


def test_s1_every_tracked_path_matches_exactly_one_namespace():
    from gov.check import pathmap

    assert s.git(s.REPO, "ls-files", "--", s.ARCHIVE_REL).strip() == s.ARCHIVE_REL, \
        f"{s.ARCHIVE_REL} is not a tracked file of this tree"
    findings = pathmap.check(s.REPO)
    assert findings == [], f"core-pathmap is not green on this tree: {findings[:5]}"


def test_s1_the_kernel_schema_accepts_the_key_as_text():
    import jsonschema

    place = s.REPO / s.SCHEMA_REL
    schema = json.loads(place.read_text(encoding="utf-8"))
    assert s.ARCHIVE_KEY in schema.get("properties", {}), f"{s.SCHEMA_REL} does not state the key {s.ARCHIVE_KEY}"
    assert s.ARCHIVE_KEY not in schema.get("required", []), "the key is optional"
    resolver = jsonschema.RefResolver(base_uri=place.parent.as_uri() + "/", referrer=schema)
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    path_map = _path_map()
    assert s.ARCHIVE_KEY in path_map, f"the path map does not name the archive under {s.ARCHIVE_KEY}"
    errors = [f"{list(error.path)}: {error.message[:120]}" for error in validator.iter_errors(path_map)]
    assert not errors, f"the kernel's schema refuses this tree's path map: {errors[:5]}"
    refused = [list(error.path) for error in validator.iter_errors({**path_map, s.ARCHIVE_KEY: 7})]
    assert [s.ARCHIVE_KEY] in refused, "the schema accepts a number under the key: it is text"
    without = {key: value for key, value in path_map.items() if key != s.ARCHIVE_KEY}
    assert not list(validator.iter_errors(without)), "the schema refuses a path map that names no archive"
