"""The landing proves the path map's coverage (W2-206 fix, PM-1 to PM-3): the cases the acceptance suite leaves
to the builder."""
from __future__ import annotations

from gov.cli.errors import GovError
from gov.queue import command, coverage

import pytest

from queue_support import OTHER, TICKET, path_map_text

NARROW = ("src/**", "tests/**", "governance/**", ".tickets/**", ".gitignore")
MAP = "governance/project/path-map.yaml"
CHANGE = {"src/pkg/gadget.py": "def gadget():\n    return 1  # b\n"}


def _narrow(project, **files):
    project.commit("narrow map", files={MAP: path_map_text(*NARROW), **files})


def test_the_line_to_add_is_the_folder_or_the_path_where_the_folder_holds_placed_files(tmp_path, project):
    _narrow(project)
    project.commit("planted", files={"new/a.md": "a\n", "src/pkg/x.md": "x\n", "root.md": "r\n"})
    project.commit("map", files={MAP: path_map_text("src/pkg/*.py", "tests/**", "governance/**", ".tickets/**",
                                                    ".gitignore")})
    entries, line = coverage.judge(project.root, [(TICKET, ["new/a.md", "src/pkg/x.md", "root.md"], False)])
    [entry] = entries
    assert entry["code"] == "PATH_NO_NAMESPACE" and entry["paths"] == ["new/a.md", "root.md", "src/pkg/x.md"]
    for said in ('- "new/**"', '- "root.md"', '- "src/pkg/x.md"'):
        assert said in entry["reason"]
    assert line.endswith("3 in none, 0 in two")


def test_a_culprit_that_carried_the_map_line_another_relies_on_lands_nothing(project):
    _narrow(project)
    base = project.sha("main")
    project.branch("topic/a", {MAP: path_map_text(*NARROW, "docs/new/**"),
                               "src/pkg/feature.py": "def twice(x):\n    return x\n"},
                   f"Task: {TICKET}", "Role: engineer")
    project.branch("topic/b", {**CHANGE, "docs/new/x.md": "x\n"}, f"Task: {OTHER}", "Role: engineer")
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a", f"{OTHER}=topic/b"])
    assert raised.value.code == "PATH_NO_NAMESPACE" and raised.value.exit_code == 3
    assert project.sha("main") == base
