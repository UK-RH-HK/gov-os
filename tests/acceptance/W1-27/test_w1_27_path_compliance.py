"""KPI success 3: path-map compliance is checked by doctor.

Every tracked path matches a path-map entry, and a recorded reference to a
moved path is reported [CAP-06.d].
"""

from __future__ import annotations

import pytest

import w1_27_support as support
import w2_67_doctor
import w2_67b_support


def _path_map_with_namespace(name, paths):
    """Build a valid path map with one namespace covering only ``paths``."""
    ns = support.minimal_namespace_yaml(name=name, paths=paths)
    return (
        "state_class: AUTHORITATIVE\n"
        f"namespaces:\n{ns}"
        "capabilities:\n"
        "  code_intelligence:\n    enabled: false\n"
        "  research_corpus:\n    enabled: false\n"
        f"policies:\n{support.minimal_policies_yaml()}"
        f"systems:\n{support.minimal_systems_yaml()}"
    )


# --------------------------------------------------------------------------
# Every tracked path matches
# --------------------------------------------------------------------------

def test_full_coverage_is_healthy(sandbox, tmp_path):
    """When every tracked path matches a namespace pattern, doctor is ok for path-map coverage.

    Revised (W2-67, I4 F1; Rewrite-Reason: the case reads result, which is empty when doctor is unhealthy): it read
    only top-level values of ``result`` while the count is nested in ``path_map``. It now reads ``path_map``
    wherever doctor put it, on a small committed project of its own with tracked paths in several folders.
    """
    project = w2_67_doctor.small_project(tmp_path / "repo")
    for relative in ("src/pkg/module.py", "docs/guide.md", "tests/test_module.py", "README.md"):
        w2_67b_support.write_committed(project, relative, "content\n")
    run = w2_67_doctor.doctor(project, sandbox)
    path_map = w2_67_doctor.section(run, "path_map")
    assert path_map.get("unclassified_count") == 0 and path_map.get("unclassified") == [], (
        f"doctor reports unclassified paths on a project whose path map covers every tracked path (`**`): "
        f"{path_map}\n{run.describe()}"
    )
    assert path_map.get("status") == "pass", f"path_map is not pass with full coverage: {path_map}\n{run.describe()}"


def test_unclassified_path_is_reported(sandbox, tmp_path):
    """A tracked path that matches no namespace pattern is reported by doctor.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name that doctor always emits): it found
    ``path`` anywhere, and ``ok`` is false on every machine for other sections. It now reads ``path_map``: the
    unclassified path is named and counted, and a covered path (a control) is not.
    """
    project = w2_67_doctor.small_project(tmp_path / "repo")
    w2_67b_support.write_committed(project, "src/covered.py", "# covered by src/**\n")
    w2_67b_support.write_committed(project, "docs/outside.md", "outside every namespace\n")
    support.write_path_map(project, _path_map_with_namespace("only-src", '["src/**"]'))
    run = w2_67_doctor.doctor(project, sandbox)
    envelope = run.envelope()
    if envelope["ok"] is True:
        pytest.fail(f"doctor is ok despite unclassified paths\n{run.describe()}")
    path_map = w2_67_doctor.section(run, "path_map")
    unclassified = path_map.get("unclassified")
    assert isinstance(unclassified, list) and "docs/outside.md" in unclassified, (
        f"doctor does not name docs/outside.md, which matches no namespace pattern, as unclassified: "
        f"{path_map}\n{run.describe()}"
    )
    assert "src/covered.py" not in unclassified, (
        f"doctor names src/covered.py as unclassified although src/** covers it: {path_map}\n{run.describe()}"
    )
    assert path_map.get("unclassified_count") == len(unclassified), (
        f"unclassified_count does not count the unclassified paths: {path_map}\n{run.describe()}"
    )
    assert path_map.get("status") != "pass", f"path_map is pass with an unclassified path: {path_map}\n{run.describe()}"


def test_moved_path_reference_is_reported(sandbox, tmp_path):
    """A recorded reference to a path that has been moved is reported by doctor (CAP-06.d).

    The test creates a file, commits it, moves it, commits the move, then asserts that doctor reports
    the reference to the old path.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name that doctor always emits): no file
    named the old path, and ``moved`` is the key ``moved_references``. A live document now names the old path,
    and the case reads that reference in ``path_compliance.moved_references``, on a small committed project.
    """
    project = w2_67_doctor.small_project(tmp_path / "repo")
    old, new = "src/gov/doctor/old_module.py", "src/gov/doctor/new_module.py"
    w2_67b_support.move_committed(project, old, new)
    w2_67b_support.write_committed(project, "docs/notes.md", f"The check lives in {old}.\n")
    run = w2_67_doctor.doctor(project, sandbox)
    references = w2_67b_support.moved_references(run)
    found = w2_67b_support.references_to(references, old, "docs/notes.md")
    assert found, f"doctor does not report docs/notes.md's reference to the moved path {old}\n{run.describe()}"
    assert all(ref.get("new_path") == new for ref in found), (
        f"the reference does not name the moved path's new path {new}: {found}\n{run.describe()}"
    )
