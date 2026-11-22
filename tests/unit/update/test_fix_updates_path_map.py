"""W2-17 fix F6 (G3 run of 2026-11-22): the update merges ``governance/updates/**`` into the path map. Builder evidence.

``pathmap.merge`` edits the text, never reserialises it: the project's other lines, comments and blank lines stay in
their order; the line goes beside ``governance/project/**`` where that is listed, else into a namespace of its own;
a path map that classifies the update records already, or is not one, is left as it is (``None``).
"""

from __future__ import annotations

import yaml

from gov.update import core, pathmap

KIT = """# The project's path map.
namespaces:
  kernel:
    paths:
      - governance/kernel/**
  project:
    paths:
      - governance/project/**   # the project's own
  adapters:
    paths:
      - .rulesync/**
"""


def _patterns(text):
    return [p for ns in yaml.safe_load(text)["namespaces"].values() for p in ns["paths"]]


def test_the_line_goes_beside_the_project_line_and_every_other_line_stays():
    merged = pathmap.merge(KIT)
    lines = merged.splitlines()
    index = lines.index("      - governance/project/**   # the project's own")
    assert lines[index + 1] == "      - governance/updates/**"
    assert [line for line in lines if line != "      - governance/updates/**"] == KIT.splitlines()
    assert _patterns(merged).count("governance/updates/**") == 1


def test_a_quoted_anchor_gives_a_quoted_line():
    text = KIT.replace("- governance/project/**   # the project's own", '- "governance/project/**"')
    assert '      - "governance/updates/**"\n' in pathmap.merge(text)


def test_without_the_project_line_a_namespace_of_its_own_ends_the_namespaces_map():
    text = "# c\nnamespaces:\n  own:\n    paths:\n      - src/**\n\ncapabilities:\n  x: 1\n"
    merged = pathmap.merge(text)
    assert merged == ("# c\nnamespaces:\n  own:\n    paths:\n      - src/**\n  updates:\n    paths:\n"
                      "      - governance/updates/**\n\ncapabilities:\n  x: 1\n")
    assert yaml.safe_load(merged)["capabilities"] == {"x": 1}


def test_a_file_without_a_final_newline_and_a_crlf_file_are_merged():
    assert pathmap.merge(KIT.rstrip("\n")) is not None
    crlf = KIT.replace("\n", "\r\n")
    merged = pathmap.merge(crlf)
    assert merged.count("\r\n") == merged.count("\n") and "governance/updates/**" in merged


def test_a_path_map_that_classifies_the_records_is_left_alone():
    own = KIT + "  own-records:\n    paths:\n      - governance/updates/**\n"
    assert pathmap.merge(own) is None
    assert pathmap.merge(KIT.replace("governance/project/**", "governance/**")) is None


def test_a_text_that_is_no_path_map_is_left_alone():
    for text in ("", "- a\n- b\n", "namespaces: []\n", "namespaces: [\n", "other: 1\n"):
        assert pathmap.merge(text) is None


def test_plan_lists_the_path_map_as_merged_with_one_write(tmp_path):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / pathmap.REL).write_text(KIT, encoding="utf-8")
    files, actions = {o: [] for o in core.OUTCOMES}, {}
    core._merge_path_map(tmp_path, files, actions)
    assert files["merged"] == [pathmap.REL]
    assert actions[pathmap.REL][0] == "write" and b"governance/updates/**" in actions[pathmap.REL][1]
    again_files, again = {o: [] for o in core.OUTCOMES}, {}
    (tmp_path / pathmap.REL).write_bytes(actions[pathmap.REL][1])
    core._merge_path_map(tmp_path, again_files, again)
    assert again_files["merged"] == [] and again == {}
